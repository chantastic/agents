#!/usr/bin/env python3
"""Captioner orchestrator: media -> Deepgram JSON -> term audit -> corrected JSON -> SRT."""

import argparse, json, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def eprint(msg=""):
    print(msg, file=sys.stderr)


def rel(p):
    try:
        return str(Path(p).expanduser().resolve())
    except Exception:
        return str(p)


def run(cmd, verbose=False):
    if verbose:
        eprint('+ ' + ' '.join(str(c) for c in cmd))
    subprocess.run([str(c) for c in cmd], check=True)


def stage(n, total, title, details=None):
    eprint(f"\n[{n}/{total}] {title}")
    for k, v in (details or {}).items():
        if v:
            eprint(f"      {k}: {v}")


def timed(fn):
    start = time.time()
    fn()
    return time.time() - start


def load_json(path):
    with open(path) as f:
        return json.load(f)


def count_srt_cues(path):
    if not Path(path).exists():
        return 0
    count = 0
    with open(path) as f:
        for line in f:
            if line.strip().isdigit():
                count += 1
    return count


def print_audit_terms(audit):
    accepted = audit.get('accepted') or []
    review = audit.get('needs_review') or []
    if accepted:
        eprint("      replacements:")
        for c in accepted:
            flag = "apply" if c.get('apply', True) and c.get('original') != c.get('corrected') else "skip"
            eprint(f"        - {c.get('original')} → {c.get('corrected')} ({c.get('confidence')}, {flag})")
    if review:
        eprint("      needs review:")
        for c in review:
            eprint(f"        - {c.get('original')} → {c.get('corrected')} ({c.get('confidence')})")


def print_applied_terms(stats):
    applied = stats.get('applied') or []
    skipped = stats.get('skipped') or []
    failed = stats.get('failed') or []
    if applied:
        eprint("      replaced:")
        for c in applied:
            eprint(f"        - {c.get('original')} → {c.get('corrected')}")
    if skipped:
        eprint("      skipped:")
        for c in skipped:
            eprint(f"        - {c.get('id')}: {c.get('reason')}")
    if failed:
        eprint("      failed:")
        for c in failed:
            eprint(f"        - {c.get('original')} → {c.get('corrected')}: {c.get('message')}")


def paths(input_path, out_dir=None):
    p = Path(input_path).resolve()
    d = Path(out_dir).resolve() if out_dir else p.parent
    stem = p.stem
    return {
        'deepgram': d / f'{stem}.deepgram.json',
        'audit': d / f'{stem}.term-audit.json',
        'corrected': d / f'{stem}.deepgram.corrected.json',
        'srt': d / f'{stem}.srt',
    }


def main():
    ap = argparse.ArgumentParser(description='Generate corrected YouTube-ready captions from audio/video')
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run')
    r.add_argument('input')
    r.add_argument('--topic', default='')
    r.add_argument('--glossary', default='', help='Comma-separated terms for Deepgram keyterms + audit context')
    r.add_argument('--out-dir')
    r.add_argument('--skip-transcribe', action='store_true', help='Use existing input.deepgram.json')
    r.add_argument('--skip-audit', action='store_true', help='Use existing input.term-audit.json')
    r.add_argument('--deepgram-json', help='Override raw Deepgram JSON path')
    r.add_argument('--audit-json', help='Override term audit JSON path')
    r.add_argument('--verbose', action='store_true', help='Print subprocess commands')
    args = ap.parse_args()

    ps = paths(args.input, args.out_dir)
    if args.deepgram_json: ps['deepgram'] = Path(args.deepgram_json).resolve()
    if args.audit_json: ps['audit'] = Path(args.audit_json).resolve()
    if args.out_dir: Path(args.out_dir).mkdir(parents=True, exist_ok=True)

    eprint("Captioner")
    eprint(f"  input: {rel(args.input)}")
    eprint(f"  topic: {args.topic or '(not provided)'}")
    eprint(f"  glossary: {args.glossary or '(not provided)'}")

    total = 4

    if args.skip_transcribe:
        stage(1, total, "Skipping Deepgram transcription", {"using": ps['deepgram']})
    else:
        stage(1, total, "Transcribing with Deepgram", {"output": ps['deepgram']})
        elapsed = timed(lambda: run([HERE/'deepgram_transcribe.py', args.input, '-o', ps['deepgram'], '--keyterms', args.glossary], args.verbose))
        dg = load_json(ps['deepgram'])
        eprint(f"      done: {elapsed:.1f}s, {len(dg.get('utterances') or [])} utterances, {len(dg.get('words') or [])} words")

    if args.skip_audit:
        stage(2, total, "Skipping terminology audit", {"using": ps['audit']})
    else:
        stage(2, total, "Auditing terminology with Anthropic", {"output": ps['audit']})
        elapsed = timed(lambda: run([HERE/'anthropic_audit.py', ps['deepgram'], '-o', ps['audit'], '--topic', args.topic, '--glossary', args.glossary], args.verbose))
        audit = load_json(ps['audit'])
        summary = audit.get('summary', {})
        eprint(f"      done: {elapsed:.1f}s, accepted={summary.get('accepted_count', len(audit.get('accepted', [])))}, review={summary.get('needs_review_count', len(audit.get('needs_review', [])))}, ignored={summary.get('rejected_or_ignored_count', len(audit.get('rejected_or_ignored', [])))}")
        print_audit_terms(audit)

    if args.skip_audit and Path(ps['audit']).exists():
        audit = load_json(ps['audit'])
        print_audit_terms(audit)

    stage(3, total, "Applying terminology corrections", {"output": ps['corrected']})
    elapsed = timed(lambda: run([HERE/'transcript_terms.py', 'apply', ps['deepgram'], ps['audit'], '-o', ps['corrected']], args.verbose))
    corrected = load_json(ps['corrected'])
    stats = corrected.get('metadata', {}).get('term_audit', {})
    eprint(f"      done: {elapsed:.1f}s, applied={stats.get('applied_count')}, skipped={stats.get('skipped_count')}, failed={stats.get('failed_count')}")
    print_applied_terms(stats)

    stage(4, total, "Generating YouTube-ready SRT", {"output": ps['srt']})
    elapsed = timed(lambda: run([HERE/'transcript_captions.py', ps['corrected'], '-o', ps['srt']], args.verbose))
    eprint(f"      done: {elapsed:.1f}s, cues={count_srt_cues(ps['srt'])}")

    eprint("\nDone. Artifacts:")
    eprint(f"  raw:       {ps['deepgram']}")
    eprint(f"  audit:     {ps['audit']}")
    eprint(f"  corrected: {ps['corrected']}")
    eprint(f"  srt:       {ps['srt']}")


if __name__ == '__main__': main()
