#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Transcribe audio/video via Deepgram Nova-3. Outputs unified JSON."""

import argparse, json, math, os, subprocess, sys, tempfile, time, urllib.request
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
    content_types = {'.ogg': 'audio/ogg', '.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.m4a': 'audio/mp4', '.mp4': 'video/mp4', '.m4v': 'video/mp4'}
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

def format_srt_time(seconds):
    seconds = max(0, float(seconds))
    ms_total = int(round(seconds * 1000))
    h, rem = divmod(ms_total, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'


def split_caption_words(words, max_chars=80, max_duration=6.0):
    captions = []
    chunk = []

    def flush():
        if not chunk:
            return
        text = ' '.join(w.get('punctuated_word') or w.get('word', '') for w in chunk).strip()
        if text:
            captions.append((chunk[0]['start'], chunk[-1]['end'], text))
        chunk.clear()

    for word in words:
        token = word.get('punctuated_word') or word.get('word', '')
        if not token:
            continue
        next_text = ' '.join([(w.get('punctuated_word') or w.get('word', '')) for w in chunk] + [token]).strip()
        duration = word.get('end', word.get('start', 0)) - (chunk[0]['start'] if chunk else word.get('start', 0))
        if chunk and (len(next_text) > max_chars or duration > max_duration):
            flush()
        chunk.append(word)
        if token.endswith(('.', '?', '!')) and len(next_text) >= max_chars * 0.55:
            flush()
    flush()
    return captions


def write_srt(transcript, path):
    captions = []
    for u in transcript.get('utterances', []):
        words = u.get('words') or []
        if words:
            captions.extend(split_caption_words(words))
        else:
            text = u.get('transcript', '').strip()
            if text:
                captions.append((u['start'], u['end'], text))

    with open(path, 'w') as f:
        for i, (start, end, text) in enumerate(captions, 1):
            f.write(f'{i}\n{format_srt_time(start)} --> {format_srt_time(end)}\n{text}\n\n')


def main():
    parser = argparse.ArgumentParser(description='Transcribe via Deepgram Nova-3')
    parser.add_argument('input', help='Audio or video file')
    parser.add_argument('--keyterms', help='Comma-separated keyterms to boost', default='')
    parser.add_argument('--output', '-o', help='Output JSON path', default='transcript.json')
    parser.add_argument('--srt', help='Also write SRT captions to this path')
    args = parser.parse_args()

    keyterms = [k.strip() for k in args.keyterms.split(',') if k.strip()] if args.keyterms else []

    # Extract audio if video
    input_path = args.input
    video_exts = {'.mp4', '.m4v', '.mov', '.mkv', '.avi', '.webm'}
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

    if args.srt:
        write_srt(result, args.srt)
        print(f"Wrote: {args.srt}", file=sys.stderr)

    if tmp_audio:
        os.unlink(tmp_audio.name)

if __name__ == '__main__':
    main()
