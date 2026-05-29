#!/usr/bin/env python3
"""Transcribe media to captioner's Deepgram JSON contract."""

import argparse, json, os, subprocess, sys, tempfile, time, urllib.request
from urllib.parse import urlencode
from credentials import deepgram_key

VIDEO_EXTS = {'.mp4', '.m4v', '.mov', '.mkv', '.avi', '.webm'}


def extract_audio(input_path, output_path):
    cmd = ['ffmpeg', '-y', '-i', input_path, '-vn', '-c:a', 'libopus', '-b:a', '48k', output_path]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise SystemExit(f"ffmpeg failed: {r.stderr[-1000:]}")


def transcribe(audio_path, keyterms=None):
    params = [
        ('model', 'nova-3'),
        ('smart_format', 'true'),
        ('utterances', 'true'),
        ('paragraphs', 'true'),
        ('punctuate', 'true'),
        ('filler_words', 'true'),
        ('language', 'en'),
    ]
    for kt in keyterms or []:
        params.append(('keyterm', kt))
    url = f"https://api.deepgram.com/v1/listen?{urlencode(params)}"
    with open(audio_path, 'rb') as f:
        data = f.read()
    ext = os.path.splitext(audio_path)[1].lower()
    content_type = {'.ogg':'audio/ogg','.wav':'audio/wav','.mp3':'audio/mpeg','.m4a':'audio/mp4','.mp4':'video/mp4','.m4v':'video/mp4'}.get(ext, 'audio/ogg')
    req = urllib.request.Request(url, data=data, method='POST', headers={
        'Authorization': f'Token {deepgram_key()}',
        'Content-Type': content_type,
    })
    start = time.time()
    with urllib.request.urlopen(req, timeout=900) as resp:
        result = json.loads(resp.read().decode())
    elapsed = time.time() - start
    ch = result['results']['channels'][0]
    alt = ch['alternatives'][0]
    return {
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


def main():
    ap = argparse.ArgumentParser(description='Transcribe media with Deepgram Nova-3 using 1Password key')
    ap.add_argument('input')
    ap.add_argument('-o', '--output', required=True)
    ap.add_argument('--keyterms', default='', help='Comma-separated Deepgram keyterms')
    args = ap.parse_args()
    keyterms = [x.strip() for x in args.keyterms.split(',') if x.strip()]
    input_path = args.input
    tmp = None
    try:
        if os.path.splitext(input_path)[1].lower() in VIDEO_EXTS:
            tmp = tempfile.NamedTemporaryFile(suffix='.ogg', delete=False)
            tmp.close()
            print(f"extracting audio: {input_path}", file=sys.stderr)
            extract_audio(input_path, tmp.name)
            input_path = tmp.name
        print(f"transcribing with Deepgram Nova-3 ({len(keyterms)} keyterms)", file=sys.stderr)
        out = transcribe(input_path, keyterms)
        with open(args.output, 'w') as f:
            json.dump(out, f, indent=2)
            f.write('\n')
        print(f"wrote: {args.output}", file=sys.stderr)
    finally:
        if tmp:
            os.unlink(tmp.name)

if __name__ == '__main__':
    main()
