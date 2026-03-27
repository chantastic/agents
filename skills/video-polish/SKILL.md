---
name: video-polish
description: Iteratively refine a video edit by re-transcribing the preview, evaluating quality as a viewer would experience it, and fixing issues like missed duplicates, mid-utterance stumbles, filler clips, and pacing drag. Use after video-cut to tighten an edit.
---

# Video Polish

Evaluate and refine a video edit by listening to what actually came out.

The core insight: the first pass (video-cut) reads utterances as isolated keep/remove decisions. This skill reads the *output as a viewer experiences it* — a continuous flow where duplicates, stumbles, and pacing problems become obvious.

## Epistemic Status

- **Principles** — re-transcribe the actual output, evaluate flow continuously, write decisions against the original transcript
- **Heuristics** — screen narration, LLM output narration, exploration loops, and transitional bridges are common pacing-drag candidates
- **Preferences** — some formats benefit from more authenticity and visible fumbling than others
- **Temporary calibration** — how aggressively to cut a given format, what kinds of exploration to preserve. Belongs in `evals/`

## Architecture: Decisions, Not Segment Mutation

Polish produces its own **decisions file** (`decisions/polish.json`) in the same format as cut decisions. Both are layers of keep/remove decisions against the **original transcript**.

The edit list is a compiled artifact — it merges contiguous kept utterances into segments. Polish never reads or modifies cut's edit list. Instead:

1. Polish identifies issues by reading the preview as a viewer.
2. For each issue, it records the **original utterance indices** to remove.
3. It writes `decisions/polish.json` with those removals.
4. A single compile step merges all decision layers into the final edit list.

## Required Environment

- `DEEPGRAM_API_KEY` — set in environment
- `ffmpeg` and `ffprobe` — installed
- Python packages: `opentimelineio`, `otio-fcpx-xml-adapter`

## Inputs

| Input | Required | Discovery | Description |
|-------|----------|-----------|-------------|
| source | yes | discover: largest .mov in cwd | Original video file |
| preview | yes | discover: cut/preview.mp4 | Preview video from the previous edit stage |
| transcript | yes | discover: transcript.json in cwd | Original Deepgram transcript JSON |
| thesis | yes | ask | One-sentence description of what the video is about |
| decisions | no | discover: decisions/*.json (alphabetical) | Existing decision layers to build on. If none provided, polish starts fresh. |
| keyterms | no | ask | Domain terms for re-transcription accuracy |
| output_dir | no | default: working directory | Where to write outputs |

When run standalone, discover or ask for each input. When run via a coordinator, these are provided explicitly.

## Outputs

```
decisions/
└── polish.json                    ← polish decisions (same format as cut)

polish/
├── pass_1/
│   ├── preview_transcript.json    ← re-transcription of input preview
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

## Process

### Pass 1: Evaluate

#### Step 1.1: Transcribe the input preview

```bash
DEEPGRAM_API_KEY=<key> python3 ~/.agents/services/transcribe.py "<preview>" \
  --keyterms "<keyterms>" \
  --output polish/pass_1/preview_transcript.json
```

```bash
python3 ~/.agents/services/edit.py format polish/pass_1/preview_transcript.json \
  --output polish/pass_1/preview_utterances.txt
```

#### Step 1.2: Read as a viewer

Read every preview utterance from start to finish. Evaluate against these criteria:

**A. Missed duplicates**
Semantically repeated observations, reactions, or phrases in different parts of the video. Invisible in isolation, obvious in flow.

**B. Mid-utterance stumbles**
Self-corrections within a single utterance: "we should be good to dig and we should be good to go."

**C. Missed false starts**
False starts spanning two kept utterances: "And then we'll cp from our" → "and we'll move from our downloads folder."

**D. Filler clips**
Utterances under ~0.8 seconds that exist only as isolated filler. Not all short clips are filler — "YOLO" or "Sick" after a reveal add personality.

**E. Pacing drag (editorial)**
Evaluate against the thesis. This is typically the highest-value category.

**E1. Screen narration** — speaker reads visible screen content aloud. Keep narration that adds interpretation; remove pure duplication of what's visible.

**E2. LLM output narration** — speaker narrates what a model wrote back. Keep the reaction/assessment; compress the low-context recap.

**E3. Exploration loops** — repeated attempts at the same task. Keep first attempt + meaningful failure + resolution. Trim intermediate retries (unless the fumbling is entertaining).

**E4. Transitional bridges** — empty phrases between sections. Removable when the next section starts with enough context.

**E5. Other drag** — extended tangents unrelated to thesis, extended confusion that could be compressed.

**F. Audio artifacts**
Jump cuts that land mid-word, segments that start/end abruptly.

#### Step 1.3: Write evaluation

Save as `polish/pass_1/eval.json`:

```json
{
  "issues": [
    {
      "type": "missed_duplicate|mid_utterance_stumble|missed_false_start|filler_clip|pacing_drag|audio_artifact",
      "preview_utterances": ["136"],
      "preview_timestamp": "822.3-833.6",
      "original_utterances": ["322", "324"],
      "description": "Human-readable description",
      "fix": "remove utterances 322, 324"
    }
  ]
}
```

The `original_utterances` field maps back to indices in the original transcript.

---

### Pass 2: Write Decisions, Compile, and Verify

#### Step 2.1: Write polish decisions

```json
{
  "decisions": {
    "033": "remove: pacing_drag — tangent, not related to thesis",
    "071": "remove: filler_clip — isolated 'Okay.' (0.4s)",
    "322": "remove: missed_duplicate — same observation as 318"
  },
  "word_edits": [
    {
      "utterance": "145",
      "exclude_from_word": 8,
      "exclude_to_word": 14,
      "reason": "mid_utterance_stumble"
    }
  ]
}
```

Save as `decisions/polish.json`.

#### Step 2.2: Compile all decisions and render

Compile all decision layers (any provided as input, plus the new polish decisions). If no prior decisions were provided, polish's own decisions are the only layer:

```bash
python3 ~/.agents/services/edit.py apply "<transcript>" \
  [prior decision files, if any] decisions/polish.json \
  --padding 0.05 --output polish/pass_2/edit_list.json
```

Render and re-transcribe:

```bash
python3 ~/.agents/services/render.py "<source>" \
  --edits polish/pass_2/edit_list.json \
  --output polish/pass_2/preview.mp4
```

```bash
DEEPGRAM_API_KEY=<key> python3 ~/.agents/services/transcribe.py polish/pass_2/preview.mp4 \
  --keyterms "<keyterms>" \
  --output polish/pass_2/preview_transcript.json
```

#### Step 2.3: Convergence check

Read the new preview utterances. Evaluate against the same criteria. Save as `polish/pass_2/eval.json`.

- **New issues found**: Append to `decisions/polish.json`, re-compile, re-render. Increment pass directories.
- **No new issues**: Converge.
- **Maximum**: 3 fix cycles.

---

### Final Output

Copy the last pass's edit list to `polish/final/edit_list.json`. Generate final timeline and preview:

```bash
python3 ~/.agents/services/edit.py apply "<transcript>" \
  [prior decision files, if any] decisions/polish.json \
  --padding 0.05 --output polish/final/edit_list.json
```

```bash
python3 ~/.agents/services/timeline.py \
  --source "<source>" \
  --edits polish/final/edit_list.json \
  --name "<name> - Polished" \
  --output polish/final/timeline.otio
```

```bash
python3 ~/.agents/services/render.py "<source>" \
  --edits polish/final/edit_list.json \
  --output polish/final/preview.mp4
```

### Report

| Metric | Cut | Polished | Improvement |
|---|---|---|---|
| Duration | ? | ? | ? removed |
| Utterances removed | ? (cut) | ? (polish) | ? additional |
| Issues fixed | — | ? | by category |
| Passes | — | ? | — |

List final output paths. Remind user to open `.fcpxml` in Final Cut Pro for review.

## Notes

- **Decisions are the contract, not segments.** Polish writes decisions against the original transcript, the same unit as cut. The edit list is compiled at the end.
- Every intermediate is preserved. The user can trace any cut: `eval.json` → `decisions/polish.json` + earlier decisions → `transcript.json`.
- The re-transcription step is essential. Do not skip it to save cost.
- This skill tightens *how existing content flows*. Major content restructuring belongs in video-cut.
- Exact editorial aggressiveness is calibration, not doctrine. Use `evals/` for current taste.
