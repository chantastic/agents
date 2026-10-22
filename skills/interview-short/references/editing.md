# The edit: choosing beats, the edit list, crops, captions

## Choosing what survives

Read the whole transcript once, then list every question the host asks. For each, ask:

- Does the answer contain one crisp, quotable idea that a stranger would get without context? Keep it.
- Is the question a setup, a ramble, or a sales pitch ("what does your company do")? Cut it, unless a short
  piece of it is needed so the answer makes sense.
- Is the answer a long build-up to a good line? Keep only the line, and maybe one concrete example.

Then order the beats for a short, not for the original conversation:

- **Hook first.** Open on the boldest claim, usually what the title is about. In the example it's the host's
  "Is it like a dark factory?" straight into "I don't think there's any very serious company that has a fully
  autonomous lights-off dark software factory. It's a bit of a meme." followed by its punchline
  ("there are startups that do this… and you can tell" / "not in a good way"), which came 3 minutes later.
- Then 2–4 more beats, each question → answer. A concrete example ("refactor this to Rust: your weekend project vs
  the Linux kernel") earns its seconds; abstract elaboration doesn't.
- End on a result or reaction ("half the cost and twice the speed" / "That's awesome.").
- Shorten questions to their core: "If you're not burning tokens you're going to get fired… what era are we in
  now?" Splice the start and end of a long question together.

Answers can be assembled from non-adjacent pieces of the same answer when the meaning holds. Don't put words in
someone's mouth: never splice so a sentence means something the speaker didn't say.

## The edit list (`edl.py`)

```python
C = ("close", 540)                       # shot spec: ("close"|"wide", crop centre x in SOURCE pixels)
CLIPS = [
  # (first word, its DTW time, last word, its DTW time, speaker, shot[, lo, hi])
  ("Is", 269.72, "factory?", 270.74, "Q", ("wide", 1480)),
  ("I", 277.44, "that", 278.44, "A", C),
  ("I'd", 132.18, "spend", 134.16, "A", C, None, 134.36),   # hi: never run past the camera cut at 134.37
]
FIX = {"DeepSeq": "DeepSeek", "Astro": "Astra", "had coded": "vibe-coded"}   # caption spelling; spaced keys merge words
FORCE = {("Is", 269.72): (269.45, None)}  # cut points you verified with probe_cut.sh
```

- Words are matched by exact text (including punctuation, e.g. `"factory?"`) nearest the given time, so copy
  them from `words.py` output.
- `cut.py` snaps each boundary to the quietest 10 ms near the word edge, caps trailing silence at ~0.55 s, and
  splits nothing for you: if an answer has a pause of 1 s+ in the middle, make it two clips.
- Speaker `Q` is the host (yellow captions), `A` the guest (white).
- A clip must not span a camera cut (the crop is per clip). Find cuts with the scene-detect command in SKILL.md
  and split the clip there, using `lo`/`hi` so neither half crosses it.

## Crops

The output is 1080×1920. A `close` crop takes the full source height (607×1080 from 1080p) centred at `cx`. A
`wide` crop takes 5/6 of the height (≈506×900) for a 1.2× punch-in, top-aligned. Pick `cx` from a contact
sheet of each shot: put the speaker's face in the middle, with the mic allowed to cut in. In a two-shot, crop
to whoever is talking (Q clips → host, A clips → guest). The plate in AE also alternates 100/112 % zoom on
back-to-back close-ups, the "jump zoom" that hides jump cuts.

## Verifying cuts (the traps)

- Whisper's plain token times run 0.3–0.5 s early. Only use the DTW times (`transcribe.sh` does this). Even
  DTW is approximate, so treat every boundary as a hypothesis.
- **Don't verify by transcribing the whole short.** Whisper on a jump-cut edit skips lines and hallucinates. Use
  `check_clips.sh` (each clip alone, padded with silence). A doubled sentence there is a whisper artifact.
- When an edge is wrong (a leaked word like "code?" or a clipped "Is"), test candidates with
  `probe_cut.sh WORK a-b a2-b …` and pin the clean one in `FORCE`.
- Clips are rendered as whole frames with audio trimmed/padded to exactly the video length. Never derive
  timeline positions from container durations: audio runs a few ms long per clip, and that added up to 0.6 s of
  drift in the example, which pushed graphics a frame off at every cut.

## Captions

`cut.py` chunks words into captions of ≤3 words / ~15 characters, breaking at punctuation, and uppercases
them. Each caption shows from its first word until the next caption starts. In AE they are two text layers
(outline under fill) so the outline never eats neighbouring letters; Q yellow `#FFD400`, A white.
