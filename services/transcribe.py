#!/usr/bin/env python3
"""Transcribe audio/video via Deepgram Nova-3. Outputs unified JSON."""

import argparse, json, os, subprocess, sys, tempfile, time, urllib.request
from urllib.parse import urlencode

def extract_audio(video_path, output_path):
    """Extract audio as Opus for minimal upload size."""
    cmd = ['ffmpeg', '-y', '-i', video_path, '-vn', '-c:a', 'libopus', '-b:a', '48k', output_path]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(f"ffmpeg error: {r.stderr[-500:]}", file=sys.stderr)
        sys.exit(1)

def transcribe(audio_path, keyterms=None):
    api_key = os.environ.get('DEEPGRAM_API_KEY')
    if not api_key:
        print("Error: DEEPGRAM_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    params = [
        ('model', 'nova-3'),
        ('smart_format', 'true'),
        ('utterances', 'true'),
        ('paragraphs', 'true'),
        ('punctuate', 'true'),
        ('filler_words', 'true'),
        ('language', 'en'),
    ]
    for kt in (keyterms or []):
        params.append(('keyterm', kt))

    url = f"https://api.deepgram.com/v1/listen?{urlencode(params)}"

    with open(audio_path, 'rb') as f:
        audio_data = f.read()

    # Determine content type
    ext = os.path.splitext(audio_path)[1].lower()
    content_types = {'.ogg': 'audio/ogg', '.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.m4a': 'audio/mp4', '.mp4': 'video/mp4'}
    content_type = content_types.get(ext, 'audio/ogg')

    req = urllib.request.Request(url, data=audio_data,
        headers={'Authorization': f'Token {api_key}', 'Content-Type': content_type}, method='POST')

    start = time.time()
    with urllib.request.urlopen(req, timeout=600) as resp:
        result = json.loads(resp.read().decode())
    elapsed = time.time() - start

    ch = result['results']['channels'][0]
    alt = ch['alternatives'][0]

    output = {
        'metadata': {
            'backend': 'deepgram',
            'model': 'nova-3',
            'duration': result['metadata'].get('duration', 0),
            'transcription_time': round(elapsed, 1),
            'keyterms': keyterms or [],
        },
        'words': alt.get('words', []),
        'utterances': result['results'].get('utterances', []),
        'paragraphs': alt.get('paragraphs', {}).get('paragraphs', []),
        'full_response': result,
    }
    return output

def main():
    parser = argparse.ArgumentParser(description='Transcribe via Deepgram Nova-3')
    parser.add_argument('input', help='Audio or video file')
    parser.add_argument('--keyterms', help='Comma-separated keyterms to boost', default='')
    parser.add_argument('--output', '-o', help='Output JSON path', default='transcript.json')
    args = parser.parse_args()

    keyterms = [k.strip() for k in args.keyterms.split(',') if k.strip()] if args.keyterms else []

    # Extract audio if video
    input_path = args.input
    video_exts = {'.mp4', '.mov', '.mkv', '.avi', '.webm'}
    tmp_audio = None
    if os.path.splitext(input_path)[1].lower() in video_exts:
        tmp_audio = tempfile.NamedTemporaryFile(suffix='.ogg', delete=False)
        tmp_audio.close()
        print(f"Extracting audio from {input_path}...", file=sys.stderr)
        extract_audio(input_path, tmp_audio.name)
        input_path = tmp_audio.name
        print(f"Audio extracted: {os.path.getsize(input_path) / 1e6:.1f}MB", file=sys.stderr)

    print(f"Transcribing with Deepgram Nova-3 ({len(keyterms)} keyterms)...", file=sys.stderr)
    result = transcribe(input_path, keyterms)
    print(f"Done in {result['metadata']['transcription_time']}s: "
          f"{len(result['utterances'])} utterances, {len(result['words'])} words",
          file=sys.stderr)

    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Wrote: {args.output}", file=sys.stderr)

    if tmp_audio:
        os.unlink(tmp_audio.name)

if __name__ == '__main__':
    main()
