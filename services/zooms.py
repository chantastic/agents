#!/usr/bin/env python3
"""Generate FCPXML with zoom adjustment clips.

Builds a clean FCPXML from an edit list and zooms.json,
using FCP 1.14 structure with adjustment clips on lane 1.

Anchor presets (3x3 grid):
    top-left,    top-center,    top-right
    middle-left, middle-center, middle-right
    bottom-left, bottom-center, bottom-right

FCP coordinate system: frame height = 100 units, origin at center.
Half-width = (width/height) * 50 (88.8889 for 16:9). Half-height = 50.
Values confirmed by FCP round-trip export.

Usage:
    python3 zooms.py --source video.mp4 --edits edit_list.json --zooms zooms.json \\
        --name "My Timeline" --output zoomed.fcpxml
"""

import argparse, json, subprocess, sys, os, urllib.parse
from fractions import Fraction


def get_video_info(video_path):
    """Get video duration, frame rate, and resolution."""
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json',
           '-show_format', '-show_streams', video_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    info = json.loads(r.stdout)
    duration = float(info['format'].get('duration', 0))
    fps_num, fps_den = 30, 1
    width, height = 1920, 1080
    for s in info.get('streams', []):
        if s['codec_type'] == 'video':
            rfr = s.get('r_frame_rate', '30/1')
            n, d = rfr.split('/')
            fps_num, fps_den = int(n), int(d)
            width = int(s.get('width', 1920))
            height = int(s.get('height', 1080))
            break
    return duration, fps_num, fps_den, width, height


def to_time(seconds: float, fps_num: int, fps_den: int) -> str:
    """Convert seconds to FCPXML rational time, frame-aligned."""
    frames = round(seconds * fps_num / fps_den)
    t = Fraction(frames * fps_den, fps_num)
    if t.denominator == 1:
        return f"{t.numerator}s"
    return f"{t.numerator}/{t.denominator}s"


def escape_xml(s: str) -> str:
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def file_url(path: str) -> str:
    """Convert absolute path to file:// URL."""
    return 'file://' + urllib.parse.quote(os.path.abspath(path), safe='/:@')


def resolve_anchor(anchor_val: str, width: int, height: int):
    """Resolve anchor to FCP unit coordinates.

    anchor_val: named preset (e.g. "middle-left") or raw FCP units "x y".
    Returns (fcp_x, fcp_y) or None for middle-center.

    Both position and anchor are set to the returned values.
    This pins the named point in place while scaling around it.
    """
    hw = (width / height) * 50.0  # half-width in FCP units (88.8889 for 16:9)

    presets = {
        'top-left':      (-hw,  50),
        'top-center':    (  0,  50),
        'top-right':     ( hw,  50),
        'middle-left':   (-hw,   0),
        'middle-center': None,
        'middle-right':  ( hw,   0),
        'bottom-left':   (-hw, -50),
        'bottom-center': (  0, -50),
        'bottom-right':  ( hw, -50),
    }

    key = anchor_val.strip().lower()
    if key in presets:
        return presets[key]
    else:
        parts = anchor_val.split()
        return float(parts[0]), float(parts[1])


def generate_fcpxml(source_path, edits_path, zooms_path, output_path, timeline_name):
    with open(edits_path) as f:
        edits = json.load(f)
    with open(zooms_path) as f:
        zooms = json.load(f).get('zooms', [])

    duration, fps_num, fps_den, width, height = get_video_info(source_path)
    source_dur = to_time(duration, fps_num, fps_den)

    # FCP canonical frameDuration: 100/3000s for 30fps, etc.
    frame_dur = f"{fps_den * 100}/{fps_num * 100}s"

    # Build cumulative timeline positions using frame-accurate integers
    # to prevent ±1 frame rounding drift between clips
    fps = Fraction(fps_num, fps_den)
    tl_frame = 0  # accumulate in frames (integers)
    clips = []
    for i, edit in enumerate(edits):
        src_start_frame = round(edit['start'] * fps)
        src_end_frame = round(edit['end'] * fps)
        dur_frames = src_end_frame - src_start_frame
        clips.append({
            'i': i, 'name': f'Clip_{i+1:03d}',
            'src_start': edit['start'], 'src_end': edit['end'],
            'src_start_frame': src_start_frame, 'dur_frames': dur_frames,
            'tl_start_frame': tl_frame,
            # Keep float versions for zoom mapping
            'tl_start': float(Fraction(tl_frame * fps_den, fps_num)),
            'tl_end': float(Fraction((tl_frame + dur_frames) * fps_den, fps_num)),
            'dur': float(Fraction(dur_frames * fps_den, fps_num)),
        })
        tl_frame += dur_frames
    total_dur = float(Fraction(tl_frame * fps_den, fps_num))

    # Map zooms to clips.
    # Connected clips use the PARENT CLIP'S SOURCE TIMEBASE for offset.
    # A connected clip CAN overhang past its parent — FCP extends it
    # visually across adjacent clips. So we attach each zoom to the
    # FIRST overlapping clip with its FULL duration (no splitting).
    min_dur = fps_den / fps_num  # one frame
    clip_zooms = {i: [] for i in range(len(clips))}
    for z in zooms:
        z_start = z['timeline_start']
        z_end = z['timeline_end']
        z_dur = z_end - z_start
        if z_dur < min_dur:
            continue
        # Find first overlapping clip
        for c in clips:
            if c['tl_end'] > z_start and c['tl_start'] < z_end:
                # Convert zoom start to source time within this clip
                src_offset = c['src_start'] + (z_start - c['tl_start'])
                clip_zooms[c['i']].append({
                    'id': z['id'],
                    'src_offset': src_offset,
                    'duration': z_dur,
                    'scale': z.get('scale', 1.50),
                    'anchor': z.get('anchor', None),
                })
                break

    # --- Build FCPXML ---
    src_url = file_url(source_path)
    seq_dur = to_time(total_dur, fps_num, fps_den)

    W = []
    W.append('<?xml version="1.0" encoding="UTF-8"?>')
    W.append('<!DOCTYPE fcpxml>')
    W.append('')
    W.append('<fcpxml version="1.14">')
    W.append('    <resources>')
    W.append(f'        <format id="r1" frameDuration="{frame_dur}" '
             f'width="{width}" height="{height}" '
             f'colorSpace="1-1-1 (Rec. 709)"/>')
    W.append(f'        <asset id="r2" name="Source" start="0s" '
             f'duration="{source_dur}" hasVideo="1" format="r1" '
             f'hasAudio="1" audioSources="1" audioChannels="2" audioRate="48000">')
    W.append(f'            <media-rep kind="original-media" src="{escape_xml(src_url)}"/>')
    W.append(f'        </asset>')
    if any(clip_zooms[i] for i in clip_zooms):
        W.append(f'        <effect id="r3" name="Adjustment Clip" uid="FFAdjustmentEffect"/>')
    W.append('    </resources>')

    W.append(f'    <library>')
    W.append(f'        <event name="Imported">')
    W.append(f'            <project name="{escape_xml(timeline_name)}">')
    W.append(f'                <sequence format="r1" duration="{seq_dur}" '
             f'tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">')
    W.append(f'                    <spine>')

    def frames_to_time(frames):
        """Convert integer frame count to FCPXML rational time string."""
        t = Fraction(frames * fps_den, fps_num)
        if t.denominator == 1:
            return f"{t.numerator}s"
        return f"{t.numerator}/{t.denominator}s"

    for c in clips:
        offset = frames_to_time(c['tl_start_frame'])
        dur = frames_to_time(c['dur_frames'])
        start = frames_to_time(c['src_start_frame'])
        zlist = clip_zooms[c['i']]

        if not zlist:
            W.append(f'                        <asset-clip ref="r2" offset="{offset}" '
                     f'name="{c["name"]}" start="{start}" duration="{dur}" '
                     f'format="r1" tcFormat="NDF" audioRole="dialogue"/>')
        else:
            W.append(f'                        <asset-clip ref="r2" offset="{offset}" '
                     f'name="{c["name"]}" start="{start}" duration="{dur}" '
                     f'format="r1" tcFormat="NDF" audioRole="dialogue">')
            for z in zlist:
                z_off = to_time(z['src_offset'], fps_num, fps_den)
                z_dur = to_time(z['duration'], fps_num, fps_den)
                scale = z['scale']
                W.append(f'                            <video ref="r3" lane="1" '
                         f'offset="{z_off}" name="Zoom {z["id"]}" '
                         f'start="3600s" duration="{z_dur}" role="adjustments">')
                result = resolve_anchor(z['anchor'], width, height) if z.get('anchor') else None
                if result:
                    fx, fy = result
                    W.append(f'                                <adjust-transform '
                             f'position="{fx:.4f} {fy:.4f}" '
                             f'anchor="{fx:.4f} {fy:.4f}" '
                             f'scale="{scale} {scale}"/>')
                else:
                    W.append(f'                                <adjust-transform '
                             f'scale="{scale} {scale}"/>')
                W.append(f'                            </video>')
            W.append(f'                        </asset-clip>')

    W.append('                    </spine>')
    W.append('                </sequence>')
    W.append('            </project>')
    W.append('        </event>')
    W.append('    </library>')
    W.append('</fcpxml>')

    with open(output_path, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(W))

    zoom_count = sum(len(v) for v in clip_zooms.values())
    print(f"Generated: {len(clips)} clips, {zoom_count} adjustment clips for {len(zooms)} zooms", file=sys.stderr)
    print(f"Timeline: {total_dur:.1f}s ({total_dur/60:.1f}min)", file=sys.stderr)
    print(f"Wrote: {output_path}", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(description='Generate FCPXML with zoom adjustment clips')
    p.add_argument('--source', required=True, help='Source video path')
    p.add_argument('--edits', required=True, help='Edit list JSON')
    p.add_argument('--zooms', required=True, help='Zooms JSON file')
    p.add_argument('--name', default='Video Edit - Zoomed', help='Timeline name')
    p.add_argument('--output', '-o', required=True, help='Output FCPXML file')
    args = p.parse_args()
    generate_fcpxml(args.source, args.edits, args.zooms, args.output, args.name)


if __name__ == '__main__':
    main()
