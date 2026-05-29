#!/usr/bin/env python3
"""Validate/apply transcript terminology audit patches."""

import argparse, copy, json, os, re, sys


def load_json(path):
    with open(path) as f:
        return json.load(f)


def write_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def token_text(w):
    return w.get("punctuated_word") or w.get("word") or ""


def plain_word(s):
    return re.sub(r"^\W+|\W+$", "", s).lower()


def preserve_punct(original_token, corrected):
    prefix = re.match(r"^\W*", original_token).group(0)
    suffix = re.search(r"\W*$", original_token).group(0)
    # If corrected already includes terminal punctuation/domain dots, only keep sentence punctuation.
    if suffix and corrected[-1:] not in ".,?!:;":
        return prefix + corrected + suffix
    return prefix + corrected


def correction_words(c):
    return [p for p in re.split(r"\s+", c["corrected"].strip()) if p]


def validate_audit(audit):
    required = ["version", "source", "summary", "accepted", "needs_review", "rejected_or_ignored"]
    missing = [k for k in required if k not in audit]
    if missing:
        raise SystemExit(f"audit missing required keys: {', '.join(missing)}")
    ids = set()
    for section in ("accepted", "needs_review"):
        for c in audit.get(section, []):
            for k in ("id", "original", "corrected", "category", "confidence", "reason"):
                if k not in c:
                    raise SystemExit(f"{section} correction missing {k}: {c}")
            if c["id"] in ids:
                raise SystemExit(f"duplicate correction id: {c['id']}")
            ids.add(c["id"])
    return True


def find_utterance(transcript, c):
    loc = c.get("location") or {}
    idx = loc.get("utterance_index")
    utts = transcript.get("utterances") or []
    if idx is not None and 0 <= idx < len(utts):
        return idx, utts[idx]
    start = c.get("start")
    if start is not None:
        for i, u in enumerate(utts):
            if float(u.get("start", -1)) - 0.05 <= start <= float(u.get("end", -1)) + 0.05:
                return i, u
    return None, None


def patch_word_list(words, c):
    loc = c.get("location") or {}
    start_i = loc.get("word_start_index")
    end_i = loc.get("word_end_index", start_i)
    if start_i is None or end_i is None:
        return False, "no word indexes"
    if start_i < 0 or end_i >= len(words) or start_i > end_i:
        return False, "word indexes out of range"

    span = words[start_i:end_i + 1]
    observed = " ".join(token_text(w) for w in span).strip()
    if c["original"].lower() not in observed.lower() and observed.lower() not in c["original"].lower():
        return False, f"word span mismatch: expected {c['original']!r}, observed {observed!r}"

    repl = correction_words(c)
    if not repl:
        return False, "empty corrected text"

    # Keep timing/word count stable. If replacement token count differs, put full replacement on first
    # word and blank following words. Utterance text/SRT will still be corrected.
    for offset, w in enumerate(span):
        if offset == 0:
            new = repl[0] if len(repl) == len(span) else c["corrected"]
            w["word"] = plain_word(new) or new
            w["punctuated_word"] = preserve_punct(token_text(w), new)
        elif len(repl) == len(span):
            w["word"] = plain_word(repl[offset]) or repl[offset]
            w["punctuated_word"] = preserve_punct(token_text(w), repl[offset])
        else:
            w["word"] = ""
            w["punctuated_word"] = ""
    return True, observed


def replace_text_once(text, original, corrected):
    if not text:
        return text, False
    if original in text:
        return text.replace(original, corrected, 1), True
    pat = re.compile(re.escape(original), re.IGNORECASE)
    new, n = pat.subn(corrected, text, count=1)
    return new, bool(n)


def find_top_word_span(transcript, c):
    words = transcript.get("words") or []
    start = c.get("start")
    end = c.get("end")
    if start is None or end is None or not words:
        return None, None
    matches = []
    for i, w in enumerate(words):
        ws = float(w.get("start", -1))
        we = float(w.get("end", -1))
        center = (ws + we) / 2
        if start - 0.05 <= center <= end + 0.05:
            matches.append(i)
    if not matches:
        return None, None
    return matches[0], matches[-1]


def apply_correction(transcript, c):
    if not c.get("apply", True):
        return False, "apply=false"

    patched_any = False
    messages = []

    # Top-level Deepgram words use global indexing; audit word indexes are usually utterance-local.
    loc = c.get("location") or {}
    top_start, top_end = find_top_word_span(transcript, c)
    if top_start is not None:
        top_c = copy.deepcopy(c)
        top_c.setdefault("location", {})["word_start_index"] = top_start
        top_c.setdefault("location", {})["word_end_index"] = top_end
        ok, msg = patch_word_list(transcript["words"], top_c)
        patched_any |= ok
        messages.append(f"top_words: {msg}")

    # Utterance words/text.
    _, utt = find_utterance(transcript, c)
    if utt:
        if utt.get("words") and loc.get("word_start_index") is not None:
            ok, msg = patch_word_list(utt["words"], c)
            patched_any |= ok
            messages.append(f"utterance_words: {msg}")
        new_text, ok = replace_text_once(utt.get("transcript", ""), c["original"], c["corrected"])
        if ok:
            utt["transcript"] = new_text
            patched_any = True
            messages.append("utterance_text: patched")
        elif utt.get("transcript"):
            messages.append("utterance_text: original not found")

    # Paragraph text, if present.
    for p in transcript.get("paragraphs") or []:
        for sent in p.get("sentences") or []:
            new_text, ok = replace_text_once(sent.get("text", ""), c["original"], c["corrected"])
            if ok:
                sent["text"] = new_text
                patched_any = True
                messages.append("paragraph_sentence: patched")
                break
        new_text, ok = replace_text_once(p.get("text", ""), c["original"], c["corrected"])
        if ok:
            p["text"] = new_text
            patched_any = True
            messages.append("paragraph_text: patched")

    return patched_any, "; ".join(messages)


def apply_audit(transcript, audit, min_confidence=0.85):
    out = copy.deepcopy(transcript)
    applied, skipped, failed = [], [], []
    for c in audit.get("accepted", []):
        if float(c.get("confidence", 0)) < min_confidence:
            skipped.append({"id": c["id"], "reason": "below min_confidence"})
            continue
        ok, msg = apply_correction(out, c)
        row = {"id": c["id"], "original": c["original"], "corrected": c["corrected"], "message": msg}
        (applied if ok else failed).append(row)

    meta = out.setdefault("metadata", {})
    meta["term_audit"] = {
        "source_audit": audit.get("source", {}).get("path"),
        "accepted_count": len(audit.get("accepted", [])),
        "applied_count": len(applied),
        "skipped_count": len(skipped),
        "failed_count": len(failed),
        "applied": applied,
        "skipped": skipped,
        "failed": failed,
    }
    return out


def format_srt_time(seconds):
    seconds = max(0, float(seconds))
    ms_total = int(round(seconds * 1000))
    h, rem = divmod(ms_total, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(transcript, path):
    cues = []
    for u in transcript.get("utterances") or []:
        text = (u.get("transcript") or "").strip()
        if text:
            cues.append((u.get("start", 0), u.get("end", 0), text))
    if not cues and transcript.get("words"):
        words = [w for w in transcript["words"] if token_text(w)]
        chunk = []
        for w in words:
            tok = token_text(w)
            next_text = " ".join(token_text(x) for x in chunk + [w]).strip()
            dur = w.get("end", w.get("start", 0)) - (chunk[0].get("start", 0) if chunk else w.get("start", 0))
            if chunk and (len(next_text) > 80 or dur > 6.0):
                cues.append((chunk[0]["start"], chunk[-1]["end"], " ".join(token_text(x) for x in chunk).strip()))
                chunk = []
            chunk.append(w)
        if chunk:
            cues.append((chunk[0]["start"], chunk[-1]["end"], " ".join(token_text(x) for x in chunk).strip()))

    with open(path, "w") as f:
        for i, (start, end, text) in enumerate(cues, 1):
            f.write(f"{i}\n{format_srt_time(start)} --> {format_srt_time(end)}\n{text}\n\n")


def cmd_validate(args):
    audit = load_json(args.audit)
    validate_audit(audit)
    print(f"ok: {args.audit}")


def cmd_apply(args):
    transcript = load_json(args.transcript)
    audit = load_json(args.audit)
    validate_audit(audit)
    out = apply_audit(transcript, audit, args.min_confidence)
    write_json(out, args.output)
    print(f"wrote: {args.output}", file=sys.stderr)
    stats = out.get("metadata", {}).get("term_audit", {})
    print(f"applied={stats.get('applied_count')} failed={stats.get('failed_count')} skipped={stats.get('skipped_count')}", file=sys.stderr)
    if args.srt:
        write_srt(out, args.srt)
        print(f"wrote: {args.srt}", file=sys.stderr)
    if stats.get("failed"):
        print(json.dumps(stats["failed"], indent=2), file=sys.stderr)
        return 1
    return 0


def cmd_srt(args):
    transcript = load_json(args.transcript)
    write_srt(transcript, args.output)
    print(f"wrote: {args.output}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description="Validate/apply transcript terminology audit patches")
    sub = ap.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate")
    v.add_argument("audit")
    v.set_defaults(func=cmd_validate)

    a = sub.add_parser("apply")
    a.add_argument("transcript")
    a.add_argument("audit")
    a.add_argument("-o", "--output", required=True)
    a.add_argument("--srt")
    a.add_argument("--min-confidence", type=float, default=0.85)
    a.set_defaults(func=cmd_apply)

    s = sub.add_parser("srt")
    s.add_argument("transcript")
    s.add_argument("-o", "--output", required=True)
    s.set_defaults(func=cmd_srt)

    args = ap.parse_args()
    rc = args.func(args)
    raise SystemExit(rc or 0)


if __name__ == "__main__":
    main()
