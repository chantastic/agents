#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Render preview video from edit list via ffmpeg."""

import argparse, json, os, shutil, subprocess, sys

def render(source_path, edits_path, output_path, batch_size=50):
    with open(edits_path) as f:
        edits = json.load(f)

    print(f"Rendering {len(edits)} segments...", file=sys.stderr)
    os.makedirs('.render_tmp', exist_ok=True)

    batch_files = []
    for bs in range(0, len(edits), batch_size):
        batch = edits[bs:bs + batch_size]
        bi = bs // batch_size
        bo = f'.render_tmp/b_{bi:03d}.mp4'
        batch_files.append(bo)

        inputs = []
        for seg in batch:
            inputs.extend(['-ss', str(seg['start']), '-to', str(seg['end']), '-i', source_path])

        fp = [f'[{i}:v:0][{i}:a:0]' for i in range(len(batch))]
        fs = ''.join(fp) + f'concat=n={len(batch)}:v=1:a=1[outv][outa]'

        cmd = ['ffmpeg', '-y'] + inputs + [
            '-filter_complex', fs, '-map', '[outv]', '-map', '[outa]',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',
            '-c:a', 'aac', '-b:a', '128k', bo
        ]
        print(f"  Batch {bi+1}/{(len(edits)+batch_size-1)//batch_size}...", file=sys.stderr)
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            print(f"  ffmpeg error: {r.stderr[-300:]}", file=sys.stderr)

    # Concatenate batches
    if len(batch_files) == 1 and os.path.exists(batch_files[0]):
        shutil.move(batch_files[0], output_path)
    else:
        fl = '.render_tmp/fl.txt'
        with open(fl, 'w') as f:
            for bf in batch_files:
                if os.path.exists(bf):
                    f.write(f"file '{os.path.abspath(bf)}'\n")
        subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', fl, '-c', 'copy', output_path],
                      capture_output=True, text=True, timeout=300)

    shutil.rmtree('.render_tmp', ignore_errors=True)

    if os.path.exists(output_path):
        r = subprocess.run(['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', output_path],
                          capture_output=True, text=True)
        dur = float(r.stdout.strip())
        size = os.path.getsize(output_path) / 1e6
        print(f"Done: {output_path} ({dur:.1f}s / {dur/60:.1f}min, {size:.0f}MB)", file=sys.stderr)
    else:
        print("ERROR: render failed", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Render preview from edit list')
    parser.add_argument('source', help='Source video')
    parser.add_argument('--edits', required=True, help='Edit list JSON')
    parser.add_argument('--output', '-o', default='preview.mp4', help='Output video')
    args = parser.parse_args()
    render(args.source, args.edits, args.output)

if __name__ == '__main__':
    main()
