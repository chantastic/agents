---
name: video-polish
description: Iteratively refine a video edit by re-transcribing the preview, evaluating quality as a viewer would experience it, and fixing issues like missed duplicates, mid-utterance stumbles, filler clips, and pacing drag. Use after video-cut to tighten an edit.
---

# Video Polish

Evaluate and refine a video edit by listening to what actually came out.

The core insight: the first pass (video-cut) reads utterances as isolated keep/remove decisions. This skill reads the *output as a viewer experiences it* — a continuous flow where duplicates, stumbles, and pacing problems become obvious.

## Epistemic Status

This skill intentionally separates **principle**, **heuristic**, **preference**, and **temporary calibration**.

- **Principles** belong here in `SKILL.md` — re-transcribe the actual output, evaluate flow continuously, write decisions against the original transcript
- **Heuristics** belong here too — screen narration, LLM output narration, exploration loops, and transitional bridges are common pacing-drag candidates
- **Preferences** should be stated as taste, not law — some formats benefit from more authenticity and more visible fumbling than others
- **Temporary calibration** (how aggressively to cut a given format, what kinds of exploration to preserve, current operator taste) belongs in `evals/`

When in doubt: preserve the evaluation method here, and treat aggressiveness as calibratable.

## Architecture: Decisions, Not Segment Mutation

Polish produces its own **decisions file** (`decisions/polish.json`) in the same format as `decisions/cut.json`. Both are layers of keep/remove decisions against the **original transcript** (`transcript.json`) at the project root.

The edit list is a compiled artifact — it merges contiguous kept utterances into segments, losing utterance provenance. Polish never reads or modifies the cut edit list. Instead:

1. Polish identifies issues by reading the preview as a viewer.
2. For each issue, it records the **original utterance indices** to remove.
3. It writes `decisions/polish.json` with those removals.
4. A single compile step merges all decision layers into the final edit list:

```bash
python3 ~/.agents/services/edit.py apply transcript.json \
  decisions/cut.json decisions/polish.json \
  --padding 0.05 --output polish/final/edit_list.json
```

This eliminates the need to map between utterances and segments. No overlap math, no segment splitting, no reverse-engineering merged segments.

## Required Environment

- `DEEPGRAM_API_KEY` — set in environment
- `ffmpeg` and `ffprobe` — installed
- Python packages: `opentimelineio`, `otio-fcpx-xml-adapter`

## Inputs

Read from `manifest.json` in the project directory:
- `source` — original video path
- `keyterms` — domain terms for re-transcription
- `thesis` — inferred by the cut stage from the video content (used for editorial pacing decisions)
- `transcript` — path to shared transcript (`transcript.json`)
- `decisions` — array of existing decision layer paths
- `stages.cut.preview` — path to the cut preview for re-transcription

The thesis is always available when running after the cut stage — it is inferred from the kept utterances, not provided by the user. This means editorial pacing evaluation (category E) is available on every normal run, even though the exact aggressiveness remains format- and taste-dependent.

If no manifest exists, ask the user for the source video path and look for `cut/` outputs in the working directory.

## Outputs

All outputs go to `polish/` within the project directory:

```
decisions/
└── polish.json                    ← polish decisions (same format as cut)

polish/
├── pass_1/
│   ├── preview_transcript.json    ← re-transcription of cut preview
│   ├── preview_utterances.txt     ← formatted for review
│   └── eval.json                  ← issues found (with original_utterances)
├── pass_2/
│   ├── preview.mp4                ← re-rendered with all decisions compiled
│   ├── preview_transcript.json    ← re-transcription for verification
│   ├── preview_utterances.txt
│   └── eval.json                  ← convergence check
└── final/
    ├── edit_list.json             ← compiled from ALL decision layers
    ├── preview.mp4
    ├── timeline.fcpxml
    └── timeline.otio
```

After completion, update `manifest.json` with polish stage status and stats.

## Process

### Pass 1: Evaluate

This is where the value is. Transcribe the cut preview → read as a viewer → find everything the first pass missed.

#### Step 1.1: Transcribe the cut preview

Use the preview from the cut stage (read path from manifest):

```bash
DEEPGRAM_API_KEY=<key> python3 ~/.agents/services/transcribe.py "<cut_preview_path>" \
  --keyterms "<terms from manifest>" \
  --output polish/pass_1/preview_transcript.json
```

```bash
python3 ~/.agents/services/edit.py format polish/pass_1/preview_transcript.json \
  --output polish/pass_1/preview_utterances.txt
```

#### Step 1.2: Read as a viewer

Read every preview utterance from start to finish. This is the critical step. Evaluate against these criteria:

**A. Missed duplicates**
Scan for semantically repeated observations, reactions, or phrases that appear in different parts of the video. These are invisible when reading utterances in isolation but obvious in continuous flow.

Examples from real edits:
- "Oh, interesting. So there is a path" followed by "Oh, interesting. So there's a universal path" — same reaction twice
- "Let's check out the headline features" → session resume → "Let's look at the headline features" — same transition twice

**B. Mid-utterance stumbles**
Self-corrections within a single utterance: "we should be good to dig and we should be good to go." These were invisible to utterance-level decisions but are audible in the rendered output.

**C. Missed false starts**
False starts that weren't caught because they spanned two kept utterances: "And then we'll cp from our" (kept) → "and we'll move from our downloads folder" (kept). The first is a false start of the second.

**D. Filler clips**
Utterances under ~0.8 seconds that exist only as isolated filler: a lone "Cool." or "K." that doesn't connect to adjacent content. Not all short clips are filler — "YOLO" or "Sick" after a reveal add personality and should stay.

**E. Pacing drag (editorial)**
Evaluate against the thesis (from `manifest.json`). In past runs this has been the highest-value category, but the exact payoff depends on format, operator taste, and how much authentic exploration the video should preserve. See `evals/` for current calibration.

**E1. Screen narration** — when the speaker reads visible screen content aloud, treat it as a **pacing-drag candidate**. If the speaker is only duplicating documentation, feature lists, or command output line-by-line, much of that can usually go because the viewer can already read it. Keep narration that adds interpretation, reaction, framing, or personality.

**E2. LLM output narration** — when the speaker narrates what Claude/GPT wrote back, treat it as a **pacing-drag candidate**. Viewers often care more about the speaker's reaction or judgment than a long summary of model output they never saw in context. Keep the reaction/assessment; compress or remove the low-context recap.

**E3. Exploration loops** — repeated attempts at the same task are often compressible. A common pattern is to keep the first attempt, the meaningful failure, and the resolution, then trim the intermediate retries. But preserve more of the loop when the fumbling itself is entertaining, revealing, or part of the promise of the video.

**E4. Transitional bridges** — empty phrases between sections are often removable when the next section starts with enough context. Treat them as candidates, not an automatic cut rule.

**E5. Other drag:**
- Extended tangents unrelated to the thesis
- Extended confusion that could be compressed to the moment of confusion + the resolution

**F. Audio artifacts**
Jump cuts that land mid-word, segments that start/end abruptly. Note the preview timestamp.

#### Step 1.3: Write evaluation

Save all issues as `polish/pass_1/eval.json`:

```json
{
  "issues": [
    {
      "type": "missed_duplicate|mid_utterance_stumble|missed_false_start|filler_clip|pacing_drag|audio_artifact",
      "preview_utterances": ["136"],
      "preview_timestamp": "822.3-833.6",
      "original_utterances": ["322", "324"],
      "description": "Human-readable description of the issue",
      "fix": "remove utterances 322, 324"
    }
  ]
}
```

The `original_utterances` field is the key output. These are indices into the **original transcript** (`transcript.json`), which is the shared source of truth across all stages.

---

### Pass 2: Write Decisions, Compile, and Verify

#### Step 2.1: Write polish decisions

Convert the eval issues into a decisions file. This is the same format as `decisions/cut.json` — only include utterances that polish is additionally removing.

```json
{
  "decisions": {
    "033": "remove: pacing_drag — Sisyphus tangent, not related to thesis",
    "034": "remove: pacing_drag — Sisyphus tangent",
    "071": "remove: filler_clip — isolated 'Okay.' (0.4s)",
    "322": "remove: missed_duplicate — same observation as 318"
  },
  "word_edits": [
    {
      "utterance": "145",
      "exclude_from_word": 8,
      "exclude_to_word": 14,
      "reason": "mid_utterance_stumble — 'we should be good to dig and we should be good to go' → trim the stumble"
    }
  ]
}
```

Save as `decisions/polish.json`.

**Polish decisions only include utterances to remove.** Utterances not mentioned are left as-is (inheriting their status from the cut layer). You never need to re-specify "keep" for utterances the cut stage already kept.

The optional `word_edits` section handles mid-utterance stumbles — sub-utterance edits that split a kept utterance at word boundaries. These are passed through to `edit.py apply` which handles the splitting.

#### Step 2.2: Compile all decisions and render

Compile both decision layers into a single edit list:

```bash
python3 ~/.agents/services/edit.py apply transcript.json \
  decisions/cut.json decisions/polish.json \
  --padding 0.05 --output polish/pass_2/edit_list.json
```

Render the preview:

```bash
python3 ~/.agents/services/render.py "<source_video>" \
  --edits polish/pass_2/edit_list.json \
  --output polish/pass_2/preview.mp4
```

Re-transcribe for verification:

```bash
DEEPGRAM_API_KEY=<key> python3 ~/.agents/services/transcribe.py polish/pass_2/preview.mp4 \
  --keyterms "<terms>" \
  --output polish/pass_2/preview_transcript.json
```

```bash
python3 ~/.agents/services/edit.py format polish/pass_2/preview_transcript.json \
  --output polish/pass_2/preview_utterances.txt
```

#### Step 2.3: Convergence check

Read the new preview utterances. Evaluate against the same criteria. Save as `polish/pass_2/eval.json`.

- **If new issues found**: Add additional removals to `decisions/polish.json`, re-compile, re-render, re-evaluate. Increment pass directories.
- **If no new issues or only marginal improvements**: Converge.
- **Maximum**: 3 fix cycles. After that, report remaining issues for manual review.

When adding decisions in subsequent passes, **append to the same `decisions/polish.json`** — it accumulates all polish-stage removals. Then re-compile from scratch each time.

In practice, convergence usually happens after 1 fix cycle. The issues are systematic (missed duplicates, pacing), not cascading.

---

### Final Output

Copy the last pass's edit list to `polish/final/edit_list.json`. Generate the final timeline and preview:

```bash
# Final compile (same command, just different output path)
python3 ~/.agents/services/edit.py apply transcript.json \
  decisions/cut.json decisions/polish.json \
  --padding 0.05 --output polish/final/edit_list.json
```

```bash
python3 ~/.agents/services/timeline.py \
  --source "<source_video>" \
  --edits polish/final/edit_list.json \
  --name "<name> - Polished" \
  --output polish/final/timeline.otio
```

```bash
python3 ~/.agents/services/render.py "<source_video>" \
  --edits polish/final/edit_list.json \
  --output polish/final/preview.mp4
```

### Update Manifest and Report

Update `manifest.json`. Add `decisions/polish.json` to the top-level `decisions` array:

```json
{
  "stages": {
    "polish": {
      "status": "complete",
      "passes": 2,
      "pass_dirs": ["polish/pass_1", "polish/pass_2"],
      "edit_list": "polish/final/edit_list.json",
      "preview": "polish/final/preview.mp4",
      "timeline": "polish/final/timeline.fcpxml",
      "stats": {
        "edited_duration": ...,
        "utterances_removed_by_polish": ...,
        "word_edits_applied": ...,
        "issues_fixed": ...,
        "passes_run": ...
      }
    }
  }
}
```

Report:

| Metric | Cut | Polished | Improvement |
|---|---|---|---|
| Duration | ? | ? | ? removed |
| Utterances removed | ? (cut) | ? (polish) | ? additional |
| Issues fixed | — | ? | by category |
| Passes | — | ? | — |

List final output file paths. If running standalone, remind user to open `.fcpxml` in Final Cut Pro.

## Notes

- **Decisions are the contract, not segments.** Polish writes decisions against the original transcript, the same unit as cut. The edit list is a compiled artifact produced at the end. This eliminates segment-mapping bugs.
- Every intermediate file is preserved. The user can trace any cut: `eval.json` → `decisions/polish.json` + `decisions/cut.json` → `transcript.json`.
- The re-transcription step is essential. It catches things that look fine on paper but are obvious when experienced as continuous flow. Do not skip it to save cost.
- This skill does not make content-level editorial decisions about what topics to cover. It tightens *how the existing content flows*. Major content restructuring belongs in `video-cut`.
- Dead air removal (silence gaps between words) is folded into the compile step when needed. It is not a separate pass — in practice, transcript-based cuts leave very little intra-segment silence.
- The `word_map.json` from the previous version of this skill is no longer needed. Word-level edits are handled natively by `edit.py apply` via the `word_edits` section.
- Exact editorial aggressiveness is calibration, not doctrine. Use `evals/` to track what the operator actually kept, restored, or further cut for this format.
