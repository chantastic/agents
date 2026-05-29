#!/usr/bin/env python3
"""
Parse an SRT subtitle file into the same compact, timestamped text
representation that `parse_deepgram.py` emits. Keeping the two parsers
isolated avoids a tangled dispatcher — call whichever script matches
your input format.

Output layout (plain text to stdout):

  DURATION: M:SS  (or H:MM:SS for longer videos)
  PARAGRAPHS: <count>
  DIARIZED: no
  --
  [M:SS] Paragraph text...
  [M:SS] Paragraph text...
  ...
  --
  PARAGRAPH_TIMESTAMPS: 0:00, 0:29, 1:16, ...

The PARAGRAPH_TIMESTAMPS line is the authoritative list of valid
timestamps the model is allowed to use for chapter markers.

Paragraph coalescence: adjacent cues are joined into one paragraph
when the gap between them is small AND the previous cue doesn't end
with terminal punctuation. This produces chapter-friendly chunks
instead of one-line-per-cue noise.

Usage:
  python parse_srt.py <path_to_file.srt>
"""
import re
import sys
from pathlib import Path

# Tunables: change if a particular workflow needs finer or coarser paragraphs.
PARAGRAPH_GAP_SECONDS = 2.0          # gap larger than this always starts a new paragraph
PARAGRAPH_MAX_SECONDS = 45.0         # cap on paragraph length; force a break above this
TERMINAL_PUNCT = ".!?…"              # cue ends here → safe to break paragraph


def fmt_ts(seconds: float, force_hours: bool = False) -> str:
    total = int(round(seconds))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h or force_hours:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def srt_time_to_seconds(ts: str) -> float:
    """Convert 'HH:MM:SS,mmm' (SRT) or 'HH:MM:SS.mmm' (VTT-ish) to seconds."""
    ts = ts.strip().replace(",", ".")
    h, m, rest = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(rest)


CUE_HEADER_RE = re.compile(
    r"^\s*(\d+)\s*\n"
    r"(\d{1,2}:\d{2}:\d{2}[,.]\d{1,3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[,.]\d{1,3})[^\n]*\n"
    r"(.*?)(?=\n\s*\n|\Z)",
    re.DOTALL | re.MULTILINE,
)


def parse_cues(text: str) -> list[dict]:
    """Return a list of {start, end, text} dicts, in file order."""
    # Strip BOM and normalize newlines so the regex above behaves consistently.
    text = text.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    cues = []
    for m in CUE_HEADER_RE.finditer(text):
        start = srt_time_to_seconds(m.group(2))
        end = srt_time_to_seconds(m.group(3))
        # Cue body: collapse internal newlines into spaces; strip basic SRT tags.
        body = m.group(4).strip()
        body = re.sub(r"<[^>]+>", "", body)        # remove HTML-style tags
        body = re.sub(r"\{[^}]+\}", "", body)      # remove ASS-style tags
        body = re.sub(r"\s+", " ", body).strip()
        if body:
            cues.append({"start": start, "end": end, "text": body})
    return cues


def coalesce_into_paragraphs(cues: list[dict]) -> list[dict]:
    """Group adjacent cues into paragraphs. Same output shape as Deepgram parser:
    a list of {start, end, text}.
    """
    paragraphs: list[dict] = []
    current: dict | None = None

    for cue in cues:
        if current is None:
            current = {"start": cue["start"], "end": cue["end"], "text": cue["text"]}
            continue

        gap = cue["start"] - current["end"]
        too_long = (cue["end"] - current["start"]) > PARAGRAPH_MAX_SECONDS
        prev_ends_clean = current["text"].rstrip().endswith(tuple(TERMINAL_PUNCT))

        # Start a new paragraph when:
        #   - the gap is large, OR
        #   - the prev cue ended on a sentence terminator AND there's any real gap, OR
        #   - the running paragraph is already too long.
        if gap > PARAGRAPH_GAP_SECONDS or too_long or (prev_ends_clean and gap > 0.3):
            paragraphs.append(current)
            current = {"start": cue["start"], "end": cue["end"], "text": cue["text"]}
        else:
            current["end"] = cue["end"]
            current["text"] = (current["text"].rstrip() + " " + cue["text"].lstrip()).strip()

    if current is not None:
        paragraphs.append(current)

    return paragraphs


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: parse_srt.py <path>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    raw = path.read_text(encoding="utf-8", errors="replace")
    cues = parse_cues(raw)
    if not cues:
        print("error: no SRT cues parsed from " + str(path), file=sys.stderr)
        return 1

    paragraphs = coalesce_into_paragraphs(cues)
    duration = cues[-1]["end"]
    force_hours = duration >= 3600

    out = []
    out.append(f"DURATION: {fmt_ts(duration, force_hours)}")
    out.append(f"PARAGRAPHS: {len(paragraphs)}")
    out.append("DIARIZED: no")
    out.append("--")

    para_starts = []
    for p in paragraphs:
        ts = fmt_ts(p["start"], force_hours)
        para_starts.append(ts)
        out.append(f"[{ts}] {p['text']}")

    out.append("--")
    out.append("PARAGRAPH_TIMESTAMPS: " + ", ".join(para_starts))

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
