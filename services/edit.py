#!/usr/bin/env python3
"""Format utterances for LLM review, apply LLM decisions to generate edit list."""

import argparse, json, sys

def format_utterances(transcript_path, output_path):
    """Format utterances as numbered list for LLM review."""
    with open(transcript_path) as f:
        data = json.load(f)

    utterances = data.get('utterances', [])
    lines = []
    for i, u in enumerate(utterances):
        lines.append(f"[{i:03d}] [{u['start']:.1f}-{u['end']:.1f}] ({u['end']-u['start']:.1f}s) {u['transcript']}")

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"Formatted {len(utterances)} utterances → {output_path}", file=sys.stderr)

def apply_decisions(transcript_path, decisions_path, output_path, padding=0.05):
    """Apply keep/remove decisions to generate edit list."""
    with open(transcript_path) as f:
        data = json.load(f)
    with open(decisions_path) as f:
        decisions = json.load(f)

    utterances = data.get('utterances', [])
    dec = decisions.get('decisions', decisions)  # support both wrapped and unwrapped

    # Get video duration from metadata or last utterance
    duration = data.get('metadata', {}).get('duration', 0)
    if not duration and utterances:
        duration = utterances[-1]['end'] + 10

    # Build edit list from kept utterances
    edits = []
    for i, u in enumerate(utterances):
        key = f"{i:03d}"
        decision = dec.get(key, 'keep')
        if isinstance(decision, str) and decision.startswith('keep'):
            edits.append({
                'start': max(0, u['start'] - padding),
                'end': min(duration, u['end'] + padding),
                'text': u['transcript'].strip(),
            })

    # Merge overlapping/adjacent
    if edits:
        merged = [edits[0].copy()]
        for t in edits[1:]:
            prev = merged[-1]
            if t['start'] >= prev['start'] and t['start'] <= prev['end'] + 0.1:
                merged[-1]['end'] = max(prev['end'], t['end'])
                merged[-1]['text'] += ' ' + t['text']
            else:
                merged.append(t.copy())
        edits = merged

    total = sum(e['end'] - e['start'] for e in edits)
    kept = sum(1 for k, v in dec.items() if isinstance(v, str) and v.startswith('keep'))
    removed = sum(1 for k, v in dec.items() if isinstance(v, str) and v.startswith('remove'))

    with open(output_path, 'w') as f:
        json.dump(edits, f, indent=2)

    print(f"Applied decisions: {kept} kept, {removed} removed → {len(edits)} segments, {total:.1f}s ({total/60:.1f}min)", file=sys.stderr)
    print(f"Wrote: {output_path}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description='Format/apply edit decisions')
    sub = parser.add_subparsers(dest='command')

    fmt = sub.add_parser('format', help='Format utterances for LLM review')
    fmt.add_argument('transcript', help='Transcript JSON')
    fmt.add_argument('--output', '-o', default='utterances.txt')

    app = sub.add_parser('apply', help='Apply LLM decisions')
    app.add_argument('transcript', help='Transcript JSON')
    app.add_argument('decisions', help='Decisions JSON')
    app.add_argument('--padding', type=float, default=0.05)
    app.add_argument('--output', '-o', default='edit_list.json')

    args = parser.parse_args()
    if args.command == 'format':
        format_utterances(args.transcript, args.output)
    elif args.command == 'apply':
        apply_decisions(args.transcript, args.decisions, args.output, args.padding)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
