---
name: video-polish
description: Iteratively refine a video edit by re-transcribing the preview, evaluating quality as a viewer would experience it, and fixing issues like missed duplicates, mid-utterance stumbles, filler clips, and pacing drag. Use after video-cut to tighten an edit.
---

# Video Polish

Evaluate and refine a video edit by listening to what actually came out.

The core insight: the first pass (video-cut) reads utterances as isolated keep/remove decisions. This skill reads the *output as a viewer experiences it* — a continuous flow where duplicates, stumbles, and pacing problems become obvious.

## Required Environment

- `DEEPGRAM_API_KEY` — set in environment
- `ffmpeg` and `ffprobe` — installed
- Python packages: `opentimelineio`, `otio-fcpx-xml-adapter`

## Inputs

Read from `manifest.json` in the project directory:
- `source` — original video path
- `keyterms` — domain terms for re-transcription
- `thesis` — inferred by the cut stage from the video content (used for editorial pacing decisions)
- `stages.cut` — paths to transcript, edit list, and preview from the cut stage

The thesis is always available when running after the cut stage — it is inferred from the kept utterances, not provided by the user. This means editorial pacing evaluation (category E) is always active.

If no manifest exists, ask the user for the source video path and look for `cut/` outputs in the working directory.

## Outputs

All outputs go to `polish/` within the project directory:

```
polish/
├── pass_1/
│   ├── preview_transcript.json    ← re-transcription of cut preview
│   ├── preview_utterances.txt     ← formatted for review
│   ├── word_map.json              ← word-level segment data
│   └── eval.json                  ← issues found
├── pass_2/
│   ├── edit_list.json             ← fixed segment list
│   ├── preview.mp4                ← re-rendered preview
│   ├── preview_transcript.json    ← re-transcription for verification
│   ├── preview_utterances.txt
│   └── eval.json                  ← convergence check
└── final/
    ├── edit_list.json
    ├── preview.mp4
    ├── timeline.fcpxml
    └── timeline.otio
```

After completion, update `manifest.json` with polish stage status and stats.

## Process

### Pass 1: Evaluate

This is where the value is. Render → transcribe → read as a viewer → find everything the first pass missed.

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

#### Step 1.2: Build word-level segment map

Read the original transcript (`cut/transcript.json`) and edit list (`cut/edit_list.json`). For each segment, find all words that fall within its time range. Record internal gaps and bookend silence. Save as `polish/pass_1/word_map.json`.

This data is needed later for word-level fixes (trimming mid-utterance stumbles).

#### Step 1.3: Read as a viewer

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
Segments under ~0.8 seconds that exist only as isolated filler: a lone "Cool." or "K." that doesn't connect to adjacent content. Not all short clips are filler — "YOLO" or "Sick" after a reveal add personality and should stay.

**E. Pacing drag (editorial)**
Evaluate against the thesis (from `manifest.json`). Sections where the preview feels slow:
- Long stretches of reading output aloud that viewers could read on screen
- Repeated debugging loops where the narrative is "tried → failed → tried → failed → tried → succeeded" but could be "tried → failed → succeeded"
- Extended confusion that could be compressed to the moment of confusion + the resolution

This is the highest-value category. In real edits, editorial pacing cuts account for ~70% of the time saved in the polish pass.

**F. Audio artifacts**
Jump cuts that land mid-word, segments that start/end abruptly. Note the preview timestamp.

#### Step 1.4: Write evaluation

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
      "fix": "Specific fix: which segments to remove, which words to trim"
    }
  ]
}
```

---

### Pass 2: Fix and Verify

#### Step 2.1: Apply fixes

Read `polish/pass_1/eval.json`. For each issue, map back to original source timestamps and apply:

- **Missed duplicate / missed false start / filler clip**: Remove the segment from the edit list.
- **Mid-utterance stumble**: Use word-level timestamps from `polish/pass_1/word_map.json` to split the segment, removing the stumble words. Preserve ≥0.05s padding around cut points.
- **Pacing drag**: Remove the identified segments. Follow the contiguous time range rule — don't splice fragments from different parts of a section.

Save the fixed edit list as `polish/pass_2/edit_list.json`.

#### Step 2.2: Render and re-transcribe

```bash
python3 ~/.agents/services/render.py "<source_video>" \
  --edits polish/pass_2/edit_list.json \
  --output polish/pass_2/preview.mp4
```

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

- **If new issues found**: Create `polish/pass_3/`, apply fixes, render, re-transcribe, re-evaluate. Increment pass numbers.
- **If no new issues or only marginal improvements**: Converge.
- **Maximum**: 3 fix cycles (passes 2, 3, 4). After that, report remaining issues for manual review.

In practice, convergence usually happens after 1 fix cycle. The issues are systematic (missed duplicates, pacing), not cascading.

---

### Final Output

Copy the last pass's edit list to `polish/final/edit_list.json`. Generate the final timeline and preview:

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

Update `manifest.json`:

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
        "segments_before": ...,
        "segments_after": ...,
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
| Segments | ? | ? | ? removed, ? split |
| Issues fixed | — | ? | by category |
| Passes | — | ? | — |

List final output file paths. If running standalone, remind user to open `.fcpxml` in Final Cut Pro.

## Notes

- Every intermediate file is preserved. The user can trace any cut: `eval.json` → `edit_list.json` → `word_map.json` → `cut/transcript.json`.
- The re-transcription step is essential. It catches things that look fine on paper but are obvious when experienced as continuous flow. Do not skip it to save cost.
- This skill does not make content-level editorial decisions about what topics to cover. It tightens *how the existing content flows*. Major content restructuring belongs in `video-cut`.
- Dead air removal (silence gaps between words) is folded into the fix step when needed. It is not a separate pass — in practice, transcript-based cuts leave very little intra-segment silence.
