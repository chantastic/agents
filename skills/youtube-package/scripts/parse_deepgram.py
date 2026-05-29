#!/usr/bin/env python3
"""
Parse a Deepgram-normalized JSON transcript into a compact, timestamped text
representation suitable for feeding to an LLM that needs to choose chapter
markers and synthesize copy.

Output layout (plain text to stdout):

  DURATION: M:SS  (or H:MM:SS for longer videos)
  PARAGRAPHS: <count>
  DIARIZED: yes|no
  --
  [M:SS] <Speaker N:> Paragraph text...
  [M:SS] <Speaker N:> Paragraph text...
  ...
  --
  PARAGRAPH_TIMESTAMPS: 0:01, 0:29, 1:16, 1:45, ...

The PARAGRAPH_TIMESTAMPS line is the authoritative list of valid timestamps
the model is allowed to use for chapter markers. It must pick from these.

Usage:
  python parse_deepgram.py <path_to_deepgram.json>
"""
import json
import sys
from pathlib import Path


def fmt_ts(seconds: float, force_hours: bool = False) -> str:
    """Format seconds as M:SS (or H:MM:SS for >1hr)."""
    total = int(round(seconds))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h or force_hours:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def detect_diarization(words: list) -> bool:
    return bool(words) and "speaker" in words[0]


def speaker_for_paragraph(para: dict, words: list, diarized: bool) -> int | None:
    """Pick the modal speaker for words inside this paragraph's time range."""
    if not diarized:
        return None
    start, end = para["start"], para["end"]
    counts: dict[int, int] = {}
    for w in words:
        if w["start"] >= start and w["end"] <= end:
            sp = w.get("speaker")
            if sp is not None:
                counts[sp] = counts.get(sp, 0) + 1
    if not counts:
        return None
    return max(counts.items(), key=lambda kv: kv[1])[0]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: parse_deepgram.py <path>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    with path.open() as f:
        d = json.load(f)

    duration = float(d["metadata"]["duration"])
    paragraphs = d.get("paragraphs", [])
    words = d.get("words", [])
    diarized = detect_diarization(words)
    force_hours = duration >= 3600

    out = []
    out.append(f"DURATION: {fmt_ts(duration, force_hours)}")
    out.append(f"PARAGRAPHS: {len(paragraphs)}")
    out.append(f"DIARIZED: {'yes' if diarized else 'no'}")
    out.append("--")

    para_starts = []
    for p in paragraphs:
        text = " ".join(s["text"] for s in p["sentences"]).strip()
        ts = fmt_ts(p["start"], force_hours)
        para_starts.append(ts)
        prefix = f"[{ts}] "
        if diarized:
            sp = speaker_for_paragraph(p, words, diarized)
            if sp is not None:
                prefix += f"<Speaker {sp}> "
        out.append(prefix + text)

    out.append("--")
    out.append("PARAGRAPH_TIMESTAMPS: " + ", ".join(para_starts))

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
