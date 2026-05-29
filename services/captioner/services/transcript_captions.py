#!/usr/bin/env python3
"""Generate YouTube-friendly SRT from corrected Deepgram JSON words."""

import argparse, json, re


def text(w): return w.get('punctuated_word') or w.get('word') or ''

def srt_time(sec):
    ms = int(round(max(0, float(sec)) * 1000)); h, rem = divmod(ms, 3600000); m, rem = divmod(rem, 60000); s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def sentence_end(tok): return tok.endswith(('.', '?', '!'))
def soft_break(tok): return tok.endswith((',', ';', ':'))


def wrap_balanced(tokens, max_line_chars=42, max_lines=2):
    raw = ' '.join(tokens).strip()
    if len(raw) <= max_line_chars: return raw
    best = None
    for i in range(1, len(tokens)):
        a, b = ' '.join(tokens[:i]), ' '.join(tokens[i:])
        if len(a) <= max_line_chars and len(b) <= max_line_chars:
            score = abs(len(a) - len(b))
            if best is None or score < best[0]: best = (score, a, b)
    if best: return best[1] + '\n' + best[2]
    # fallback greedy two lines
    lines, cur = [], []
    for t in tokens:
        nxt = ' '.join(cur + [t])
        if cur and len(nxt) > max_line_chars and len(lines) < max_lines - 1:
            lines.append(' '.join(cur)); cur = [t]
        else:
            cur.append(t)
    if cur: lines.append(' '.join(cur))
    return '\n'.join(lines[:max_lines])


def make_cues(words, max_line_chars=42, max_lines=2, max_duration=6.0, min_duration=0.8):
    words = [w for w in words if text(w).strip()]
    max_chars = max_line_chars * max_lines
    cues, chunk = [], []

    def flush():
        nonlocal chunk
        if not chunk: return
        toks = [text(w).strip() for w in chunk if text(w).strip()]
        if toks:
            cues.append((chunk[0]['start'], chunk[-1]['end'], wrap_balanced(toks, max_line_chars, max_lines)))
        chunk = []

    for w in words:
        tok = text(w).strip()
        if not tok: continue
        prospective = chunk + [w]
        toks = [text(x).strip() for x in prospective if text(x).strip()]
        chars = len(' '.join(toks))
        dur = w.get('end', w.get('start', 0)) - (chunk[0].get('start', w.get('start', 0)) if chunk else w.get('start', 0))
        if chunk and (chars > max_chars or dur > max_duration):
            # Prefer backing up to last punctuation in current chunk.
            split_at = None
            for idx in range(len(chunk)-1, -1, -1):
                if sentence_end(text(chunk[idx])) or soft_break(text(chunk[idx])):
                    split_at = idx + 1; break
            if split_at and split_at < len(chunk):
                rest = chunk[split_at:]
                chunk = chunk[:split_at]
                flush()
                chunk = rest
            else:
                flush()
        chunk.append(w)
        cur_dur = chunk[-1].get('end', 0) - chunk[0].get('start', 0)
        cur_chars = len(' '.join(text(x).strip() for x in chunk))
        if sentence_end(tok) and cur_dur >= min_duration and cur_chars >= max_line_chars * 0.6:
            flush()
    flush()
    return cues


def write_srt(cues, path):
    with open(path, 'w') as f:
        for i, (start, end, body) in enumerate(cues, 1):
            f.write(f"{i}\n{srt_time(start)} --> {srt_time(end)}\n{body}\n\n")


def main():
    ap = argparse.ArgumentParser(description='Generate YouTube-friendly SRT from Deepgram JSON')
    ap.add_argument('transcript')
    ap.add_argument('-o', '--output', required=True)
    ap.add_argument('--max-line-chars', type=int, default=42)
    ap.add_argument('--max-lines', type=int, default=2)
    ap.add_argument('--max-duration', type=float, default=6.0)
    ap.add_argument('--min-duration', type=float, default=0.8)
    args = ap.parse_args()
    data = json.load(open(args.transcript))
    cues = make_cues(data.get('words') or [], args.max_line_chars, args.max_lines, args.max_duration, args.min_duration)
    write_srt(cues, args.output)
    print(f"wrote: {args.output} ({len(cues)} cues)")

if __name__ == '__main__': main()
