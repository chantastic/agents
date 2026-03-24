#!/usr/bin/env python3
"""Generate OTIO and FCPXML timelines from edit lists."""

import argparse, json, os, subprocess, sys
import opentimelineio as otio

def get_video_info(video_path):
    """Get video duration and frame rate."""
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', video_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    info = json.loads(r.stdout)
    duration = float(info['format'].get('duration', 0))
    fps = 30.0
    for s in info.get('streams', []):
        if s['codec_type'] == 'video':
            rfr = s.get('r_frame_rate', '30/1')
            num, den = rfr.split('/')
            fps = float(num) / float(den)
            break
    return duration, fps

def generate(source_path, edits_path, output_path, timeline_name="Video Edit"):
    with open(edits_path) as f:
        edits = json.load(f)

    duration, fps = get_video_info(source_path)
    source_abs = os.path.abspath(source_path)

    timeline = otio.schema.Timeline(name=timeline_name)
    video_track = otio.schema.Track(name='Video', kind=otio.schema.TrackKind.Video)
    audio_track = otio.schema.Track(name='Audio', kind=otio.schema.TrackKind.Audio)

    avail = otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(0, fps),
        duration=otio.opentime.RationalTime.from_seconds(duration, fps)
    )

    for i, edit in enumerate(edits):
        start = otio.opentime.RationalTime.from_seconds(edit['start'], fps)
        end = otio.opentime.RationalTime.from_seconds(edit['end'], fps)
        source_range = otio.opentime.TimeRange(start_time=start, duration=end - start)

        for track in [video_track, audio_track]:
            ref = otio.schema.ExternalReference(target_url=source_abs, available_range=avail)
            clip = otio.schema.Clip(
                name=f'Clip_{i+1:03d}',
                media_reference=ref,
                source_range=source_range,
                metadata={'transcript': edit.get('text', '')[:200]}
            )
            track.append(clip)

    timeline.tracks.append(video_track)
    timeline.tracks.append(audio_track)

    # Write OTIO
    otio_path = output_path if output_path.endswith('.otio') else output_path.rsplit('.', 1)[0] + '.otio'
    otio.adapters.write_to_file(timeline, otio_path)
    print(f"Wrote: {otio_path} ({len(edits)} clips)", file=sys.stderr)

    # Write FCPXML
    fcpxml_path = otio_path.rsplit('.', 1)[0] + '.fcpxml'
    try:
        otio.adapters.write_to_file(timeline, fcpxml_path)
        print(f"Wrote: {fcpxml_path}", file=sys.stderr)
    except Exception as e:
        print(f"FCPXML export failed: {e}", file=sys.stderr)
        print("Try: pip install otio-fcpx-xml-adapter", file=sys.stderr)

    total = sum(e['end'] - e['start'] for e in edits)
    print(f"Timeline: {len(edits)} clips, {total:.1f}s ({total/60:.1f}min)", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description='Generate OTIO + FCPXML timelines')
    parser.add_argument('--source', required=True, help='Source video path')
    parser.add_argument('--edits', required=True, help='Edit list JSON')
    parser.add_argument('--name', default='Video Edit', help='Timeline name')
    parser.add_argument('--output', '-o', default='timeline.otio', help='Output path')
    args = parser.parse_args()

    generate(args.source, args.edits, args.output, args.name)

if __name__ == '__main__':
    main()
