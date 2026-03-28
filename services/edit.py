#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Format utterances for LLM review, apply LLM decisions to generate edit list.

Supports layered decisions: multiple decision files are merged, with later files
taking precedence. Any utterance marked "remove" in ANY layer is removed.
This allows cut and polish stages to each produce their own decisions file,
and a single compile step merges them into the final edit list.

Word-level edits (mid-utterance stumbles) are supported via a "word_edits"
section in any decisions file. These split utterances at word boundaries.
"""

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

def load_and_merge_decisions(decision_paths):
    """Load multiple decision files and merge them.

    Rules:
    - Later files take precedence over earlier files.
    - Any utterance marked "remove" in ANY layer is removed (remove wins over keep).
    - word_edits are collected from all layers.
    """
    merged = {}
    word_edits = []

    for path in decision_paths:
        with open(path) as f:
            data = json.load(f)

        dec = data.get('decisions', data)
        for key, value in dec.items():
            if key in ('thesis', 'word_edits'):
                continue
            # Remove always wins: once removed, stays removed
            if key in merged and isinstance(merged[key], str) and merged[key].startswith('remove'):
                continue
            merged[key] = value

        # Collect word_edits from this layer
        if 'word_edits' in data:
            word_edits.extend(data['word_edits'])

    return merged, word_edits

def apply_decisions(transcript_path, decision_paths, output_path, padding=0.05):
    """Apply keep/remove decisions from one or more decision files to generate edit list.

    When multiple decision files are provided, they are merged as layers:
    - cut/decisions.json  (rough cut: fragments, false starts)
    - polish/decisions.json  (editorial: tangents, pacing, filler)

    Any utterance marked "remove" in any layer is removed from the final edit.
    """
    with open(transcript_path) as f:
        data = json.load(f)

    utterances = data.get('utterances', [])

    # Merge all decision layers
    dec, word_edits = load_and_merge_decisions(decision_paths)

    # Get video duration from metadata or last utterance
    duration = data.get('metadata', {}).get('duration', 0)
    if not duration and utterances:
        duration = utterances[-1]['end'] + 10

    # Build word-level index for word_edits
    words = data.get('words', [])
    word_edit_ranges = []  # list of (utt_index, exclude_start, exclude_end)
    for we in word_edits:
        utt_idx = we.get('utterance')
        if utt_idx is None:
            continue
        # Find word timestamps within this utterance
        utt = utterances[int(utt_idx)]
        utt_words = [w for w in words if w['start'] >= utt['start'] - 0.05 and w['end'] <= utt['end'] + 0.05]

        exclude_from = we.get('exclude_from_word')
        exclude_to = we.get('exclude_to_word')
        if exclude_from is not None and exclude_to is not None and utt_words:
            # Find the start/end of the excluded word range
            ex_start = utt_words[min(exclude_from, len(utt_words)-1)]['start']
            ex_end = utt_words[min(exclude_to, len(utt_words)-1)]['end']
            word_edit_ranges.append((int(utt_idx), ex_start, ex_end))

    # Build edit list from kept utterances
    edits = []
    for i, u in enumerate(utterances):
        key = f"{i:03d}"
        decision = dec.get(key, 'keep')
        if isinstance(decision, str) and decision.startswith('remove'):
            continue

        utt_start = max(0, u['start'] - padding)
        utt_end = min(duration, u['end'] + padding)
        text = u['transcript'].strip()

        # Check for word-level edits on this utterance
        utt_word_edits = [we for we in word_edit_ranges if we[0] == i]
        if utt_word_edits:
            # Split utterance around excluded word ranges
            for _, ex_start, ex_end in sorted(utt_word_edits):
                if ex_start > utt_start + 0.1:
                    edits.append({
                        'start': utt_start,
                        'end': ex_start - padding,
                        'text': text + ' [split]',
                    })
                utt_start = ex_end + padding
            if utt_end > utt_start + 0.1:
                edits.append({
                    'start': utt_start,
                    'end': utt_end,
                    'text': text + ' [split]',
                })
        else:
            edits.append({
                'start': utt_start,
                'end': utt_end,
                'text': text,
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

    n_layers = len(decision_paths)
    layer_label = f" ({n_layers} decision layers)" if n_layers > 1 else ""
    we_label = f", {len(word_edits)} word edits" if word_edits else ""
    print(f"Applied decisions{layer_label}: {kept} kept, {removed} removed{we_label} → {len(edits)} segments, {total:.1f}s ({total/60:.1f}min)", file=sys.stderr)
    print(f"Wrote: {output_path}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description='Format/apply edit decisions')
    sub = parser.add_subparsers(dest='command')

    fmt = sub.add_parser('format', help='Format utterances for LLM review')
    fmt.add_argument('transcript', help='Transcript JSON')
    fmt.add_argument('--output', '-o', default='utterances.txt')

    app = sub.add_parser('apply', help='Apply LLM decisions')
    app.add_argument('transcript', help='Transcript JSON')
    app.add_argument('decisions', nargs='+', help='One or more decisions JSON files (layered, later wins)')
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
