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

import argparse, json, subprocess, sys, os, urllib.parse, glob
from fractions import Fraction


# DesignStudio title template paths and parameter keys.
# Templates are NOT bundled — requires MotionVFX license.
# See ~/.agents/services/motion-templates/README.md for details.

TEMPLATE_SEARCH_PATHS = [
    os.path.expanduser("~/Movies/Motion Templates.localized/Titles.localized/DesignStudio"),
    os.path.expanduser("~/Library/Containers/com.apple.FinalCut/Data/Movies/Motion Templates.localized/Titles.localized/DesignStudio"),
]

TEMPLATES = {
    'constant_zoom': {
        'name': 'Constant Zoom GG18',
        'dir': 'Constant Zoom GG18',
        'moti': 'Constant Zoom GG18.moti',
        'params': {
            'strength': '9999/10003/4/3189716296/203',
            'end_point': '9999/3189715466/3293474482/2/1/13',
        },
    },
    'zoom_in': {
        'name': 'Zoom In 0ZZM',
        'dir': 'Zoom In 0ZZM',
        'moti': 'Zoom In 0ZZM.moti',
        'params': {
            'content_position': '9999/3144439439/3330899423/2/1/13',
            'content_scale': '9999/3144439439/3330899423/2/1/15',
            'animation_in': '9999/3144439361/2/101',
            'animation_out': '9999/3144439361/2/102',
        },
    },
}


def find_template(template_key):
    """Find a DesignStudio template on disk. Returns (moti_path, uid) or (None, None)."""
    info = TEMPLATES[template_key]
    for base in TEMPLATE_SEARCH_PATHS:
        moti = os.path.join(base, info['dir'], info['moti'])
        if os.path.exists(moti):
            # uid uses ~/Titles.localized/ relative path (FCP convention)
            uid = f"~/Titles.localized/DesignStudio/{info['dir']}/{info['moti']}"
            return moti, uid
    return None, None


def resolve_anchor_normalized(anchor_val):
    """Resolve anchor preset to normalized 0–1 coordinates for title templates.

    Returns (x, y) where (0,0)=top-left, (1,1)=bottom-right, (0.5,0.5)=center.
    Values inset from edges to avoid cropping at high zoom.
    """
    presets = {
        'top-left':      (0.15, 0.15),
        'top-center':    (0.50, 0.15),
        'top-right':     (0.85, 0.15),
        'middle-left':   (0.15, 0.50),
        'middle-center': (0.50, 0.50),
        'middle-right':  (0.85, 0.50),
        'bottom-left':   (0.15, 0.85),
        'bottom-center': (0.50, 0.85),
        'bottom-right':  (0.85, 0.85),
    }
    key = anchor_val.strip().lower() if anchor_val else 'middle-center'
    if key in presets:
        return presets[key]
    # Raw "x y" values — assume already normalized
    parts = anchor_val.split()
    return float(parts[0]), float(parts[1])


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


def generate_fcpxml(source_path, edits_path, zooms_path, output_path, timeline_name, use_titles=False):
    with open(edits_path) as f:
        edits = json.load(f)
    with open(zooms_path) as f:
        zooms = json.load(f).get('zooms', [])

    # Detect title templates
    title_refs = {}  # template_key → (moti_path, uid)
    if use_titles:
        for key in TEMPLATES:
            path, uid = find_template(key)
            if path:
                title_refs[key] = (path, uid)
                print(f"  Title template found: {TEMPLATES[key]['name']}", file=sys.stderr)
            else:
                print(f"  Title template NOT found: {TEMPLATES[key]['name']} — falling back to adjustment clips", file=sys.stderr)
        if not title_refs:
            print("  No title templates found, using adjustment clips for all zooms", file=sys.stderr)
            use_titles = False

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
                    'style': z.get('style', 'punch'),
                    'src_offset': src_offset,
                    'duration': z_dur,
                    'scale': z.get('scale', 1.50),
                    'anchor': z.get('anchor', None),
                    'ramp_in': z.get('ramp_in', 0.5),
                    'ramp_out': z.get('ramp_out', 0.3),
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
    has_zooms = any(clip_zooms[i] for i in clip_zooms)
    if has_zooms:
        W.append(f'        <effect id="r3" name="Adjustment Clip" uid="FFAdjustmentEffect"/>')
    # Title template effect refs
    title_effect_ids = {}
    if use_titles and has_zooms:
        next_id = 4
        if 'constant_zoom' in title_refs:
            rid = f'r{next_id}'
            _, uid = title_refs['constant_zoom']
            W.append(f'        <effect id="{rid}" name="{TEMPLATES["constant_zoom"]["name"]}" uid="{uid}"/>')
            title_effect_ids['constant_zoom'] = rid
            next_id += 1
        if 'zoom_in' in title_refs:
            rid = f'r{next_id}'
            _, uid = title_refs['zoom_in']
            W.append(f'        <effect id="{rid}" name="{TEMPLATES["zoom_in"]["name"]}" uid="{uid}"/>')
            title_effect_ids['zoom_in'] = rid
            next_id += 1
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
                style = z.get('style', 'punch')
                result = resolve_anchor(z['anchor'], width, height) if z.get('anchor') else None
                norm = resolve_anchor_normalized(z.get('anchor'))

                # --- Title-based zoom (preferred when templates available) ---
                if use_titles and style == 'push' and 'constant_zoom' in title_effect_ids:
                    ref = title_effect_ids['constant_zoom']
                    params = TEMPLATES['constant_zoom']['params']
                    nx, ny = norm
                    W.append(f'                            <title ref="{ref}" lane="1" '
                             f'offset="{z_off}" name="{TEMPLATES["constant_zoom"]["name"]}" '
                             f'start="3600s" duration="{z_dur}">')
                    # Strength: map our scale to 0–1 range (1.5 → ~0.33)
                    strength = min(1.0, (scale - 1.0))
                    W.append(f'                                <param name="Zoom In Strength" key="{params["strength"]}" value="{strength:.4f}"/>')
                    if norm != (0.5, 0.5):
                        W.append(f'                                <param name="Zoom In End Point" key="{params["end_point"]}" value="{nx:.6f} {ny:.6f}"/>')
                    W.append(f'                            </title>')
                    continue

                if use_titles and style in ('smooth', 'punch') and 'zoom_in' in title_effect_ids:
                    ref = title_effect_ids['zoom_in']
                    params = TEMPLATES['zoom_in']['params']
                    nx, ny = norm
                    W.append(f'                            <title ref="{ref}" lane="1" '
                             f'offset="{z_off}" name="{TEMPLATES["zoom_in"]["name"]}" '
                             f'start="3600s" duration="{z_dur}">')
                    if norm != (0.5, 0.5):
                        W.append(f'                                <param name="Content Position" key="{params["content_position"]}" value="{nx:.6f} {ny:.6f}"/>')
                    W.append(f'                                <param name="Content Scale" key="{params["content_scale"]}" value="{scale}"/>')
                    if style == 'punch':
                        # Disable both animations for hard cut
                        W.append(f'                                <param name="Animation In" key="{params["animation_in"]}" value="0"/>')
                        W.append(f'                                <param name="Animation Out" key="{params["animation_out"]}" value="0"/>')
                    W.append(f'                            </title>')
                    continue

                # --- Fallback: adjustment clip with keyframed/static transforms ---
                W.append(f'                            <video ref="r3" lane="1" '
                         f'offset="{z_off}" name="Zoom {z["id"]}" '
                         f'start="3600s" duration="{z_dur}" role="adjustments">')

                if style == 'smooth':
                    ramp_in = z.get('ramp_in', 0.5)
                    ramp_out = z.get('ramp_out', 0.3)
                    z_dur_secs = z['duration']
                    t0 = 3600.0
                    t1 = t0 + ramp_in
                    t2 = t0 + z_dur_secs - ramp_out
                    t3 = t0 + z_dur_secs
                    if t1 >= t2:
                        mid = t0 + z_dur_secs / 2
                        t1 = mid
                        t2 = mid
                    kt0 = to_time(t0, fps_num, fps_den)
                    kt1 = to_time(t1, fps_num, fps_den)
                    kt2 = to_time(t2, fps_num, fps_den)
                    kt3 = to_time(t3, fps_num, fps_den)
                    anchor_attr = ''
                    if result:
                        fx, fy = result
                        anchor_attr = f' position="{fx:.4f} {fy:.4f}" anchor="{fx:.4f} {fy:.4f}"'
                    W.append(f'                                <adjust-transform{anchor_attr}>')
                    W.append(f'                                    <param name="scale">')
                    W.append(f'                                        <keyframeAnimation>')
                    W.append(f'                                            <keyframe time="{kt0}" value="1 1" curve="smooth"/>')
                    W.append(f'                                            <keyframe time="{kt1}" value="{scale} {scale}" curve="smooth"/>')
                    W.append(f'                                            <keyframe time="{kt2}" value="{scale} {scale}" curve="smooth"/>')
                    W.append(f'                                            <keyframe time="{kt3}" value="1 1"/>')
                    W.append(f'                                        </keyframeAnimation>')
                    W.append(f'                                    </param>')
                    W.append(f'                                </adjust-transform>')

                elif style == 'push':
                    t0 = 3600.0
                    t1 = t0 + z['duration']
                    kt0 = to_time(t0, fps_num, fps_den)
                    kt1 = to_time(t1, fps_num, fps_den)
                    anchor_attr = ''
                    if result:
                        fx, fy = result
                        anchor_attr = f' position="{fx:.4f} {fy:.4f}" anchor="{fx:.4f} {fy:.4f}"'
                    W.append(f'                                <adjust-transform{anchor_attr}>')
                    W.append(f'                                    <param name="scale">')
                    W.append(f'                                        <keyframeAnimation>')
                    W.append(f'                                            <keyframe time="{kt0}" value="1 1" curve="smooth"/>')
                    W.append(f'                                            <keyframe time="{kt1}" value="{scale} {scale}"/>')
                    W.append(f'                                        </keyframeAnimation>')
                    W.append(f'                                    </param>')
                    W.append(f'                                </adjust-transform>')

                else:
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
    mode = "titles" if use_titles and title_effect_ids else "adjustment clips"
    print(f"Generated: {len(clips)} clips, {zoom_count} zooms ({mode}) for {len(zooms)} zoom entries", file=sys.stderr)
    print(f"Timeline: {total_dur:.1f}s ({total_dur/60:.1f}min)", file=sys.stderr)
    print(f"Wrote: {output_path}", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(description='Generate FCPXML with zoom adjustment clips')
    p.add_argument('--source', required=True, help='Source video path')
    p.add_argument('--edits', required=True, help='Edit list JSON')
    p.add_argument('--zooms', required=True, help='Zooms JSON file')
    p.add_argument('--name', default='Video Edit - Zoomed', help='Timeline name')
    p.add_argument('--output', '-o', required=True, help='Output FCPXML file')
    p.add_argument('--titles', action='store_true',
                   help='Use DesignStudio title templates instead of adjustment clips (requires MotionVFX)')
    args = p.parse_args()
    generate_fcpxml(args.source, args.edits, args.zooms, args.output, args.name,
                    use_titles=args.titles)


if __name__ == '__main__':
    main()
