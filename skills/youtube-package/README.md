# youtube-package

Generates a complete YouTube publishing kit from a video transcript:

- 5 viral-but-specific title options
- SEO-friendly YouTube description with content-based hook and accurate chapter markers
- Short pinned comment (1–3 sentences)
- Social caption (≤ 200 chars)
- LinkedIn post that affirms the reader
- X post that's bold and concrete

Output is a single chat message structured so it can be copy-pasted section by section into the right field at upload time. No files are produced by the skill itself.

## Layout

```
youtube-package/
├── SKILL.md                 ← rules and workflow (the skill itself)
├── README.md                ← this file
├── scripts/
│   ├── parse_deepgram.py    ← parser for Deepgram-normalized JSON transcripts
│   └── parse_srt.py         ← parser for .srt subtitle files
└── evals/
    ├── evals.json           ← regression test prompts
    └── files/               ← bundled sample transcripts the evals reference
```

## How to use

Drop a transcript path into chat and ask for the package. The skill auto-dispatches by extension:

- `.deepgram.corrected.json` (or any normalized Deepgram JSON) → `scripts/parse_deepgram.py`
- `.srt` → `scripts/parse_srt.py`

Both parsers emit the same shape: a `DURATION` header, paragraph-shaped chunks with timestamps, and a `PARAGRAPH_TIMESTAMPS:` line that's the authoritative list of timestamps the model is allowed to use for chapter markers. That single discipline is what keeps chapters correct.

## Things to consider

The skill is in good shape for short solo demos (the case it was iterated on), but a few things are worth knowing before leaning on it harder.

**Diarized interviews are untested.** The Deepgram parser handles the `DIARIZED: yes` case and labels paragraphs by speaker. The SKILL.md tells the model to "name both sides". But every transcript used to build and test the skill was a single-speaker demo, so the interview path is unproven end-to-end. Worth a dry run with a real two-speaker transcript before trusting it for a podcast workflow.

**Long-form is untested.** All five test transcripts were ~6-minute demos. The skill has chapter caps for 10–30, 30–60, and 60+ minute videos, but those branches were never exercised. A 45-minute interview will produce many more paragraphs than the parser was tuned against, and the chosen chapter beats may feel off-rhythm on the first try. Plan one calibration run when the first long-form video shows up.

**VTT isn't supported.** YouTube's native caption export is `.vtt`, not `.srt`. The two formats overlap 95% — adding a `parse_vtt.py` sibling is a small job (about 30 lines), and it should be done the moment that input shows up rather than retrofitting the SRT parser to handle both.

**No voice priors.** The skill leans on structural rules instead of imitating Michael's voice. That keeps the skill general, but the longer you use it the more you'll notice it has a "house style" that isn't quite yours. The clean fix when that becomes a problem: drop 3–5 packages you loved into `references/voice-samples.md` and add one line to SKILL.md pointing the model at them.

**The `[YouTube URL]` placeholder still needs a human hand.** The X post and (sometimes) the LinkedIn post end with `[YouTube URL]` because the real URL doesn't exist until upload. There's no automation for the find-and-replace step after upload. If this becomes annoying, a small post-upload tool would help — but it's outside the skill's scope.

**Single-shot, no toggles.** The skill always produces all six sections. There's no way to ask for "just titles and description" or to skip the LinkedIn post for a video that doesn't need one. Manual deletion after the fact is the current workaround. Easy to add a section-toggle later if it becomes a real friction point.

## Eval set

`evals/evals.json` contains regression prompts that cover both parser paths and several context shapes (clean prompt, prompt with provided URLs, sparse prompt with no context). The referenced transcript files live in `evals/files/` so the eval set is self-contained.

Run an eval manually by handing the prompt to a fresh Claude session that has access to this skill. To run them as part of a structured benchmark, use the skill-creator workflow with this directory as the skill path.

## Iteration history

The skill went through three iterations before shipping. Each iteration's outputs and benchmarks live outside this directory (in a `youtube-package-workspace/` sibling alongside the eval workspace). What changed across iterations, in order:

1. **iter-1 → iter-2**: chapter labels switched to verb-led directives, pinned comments tightened to 1–3 sentences, social caption rule corrected from "≥ 200 words" to "≤ 200 chars", URL placeholders banned inside fake URLs.
2. **iter-2 → iter-3**: chapter labels switched again to literal-first (no vague pronouns like *it/us/this*), hard caps on chapter count by video duration, all `[add]` placeholder tokens banned from published copy, no more "things missing" note at the bottom of packages, X posts required to lead with a concrete noun, heavy/academic words banned in the writer's voice (verbatim quotes exempt).
3. **iter-3 → ship**: SRT parser added as a sibling to the Deepgram parser. Both isolated, both emit the same shape downstream.
