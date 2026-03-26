---
name: video-cut
description: Create a rough cut from a video recording. Transcribes with Deepgram, uses the LLM to remove duplicate takes, false starts, and fragments, infers a thesis, and outputs FCPXML for Final Cut Pro. Use when editing video recordings or removing retakes before polish.
---

# Video Cut

Create a publication-ready rough cut from a raw recording.

## Epistemic Status

This skill intentionally separates **principle**, **heuristic**, **preference**, and **temporary calibration**.

- **Principles** belong here in `SKILL.md` — rough cut first, editorial later; decisions are source; cut contiguous thoughts, not sentence confetti
- **Heuristics** belong here too — duplicate takes, false starts, fragments, and mistake reactions are common removal categories
- **Preferences** should be stated as taste, not law — some creators want more personality left in the rough cut than others
- **Temporary calibration** (what counts as too fragmentary, when a reaction adds charm, when a short utterance is really a list item, how conservative to be) belongs in `evals/`

When in doubt: keep the rough-cut method here, and let edge-case aggressiveness be calibrated from real reviews.

## Required Environment

- `DEEPGRAM_API_KEY` — set in environment
- `ffmpeg` and `ffprobe` — installed
- Python packages: `opentimelineio`, `otio-fcpx-xml-adapter`

## Inputs

This skill can be invoked standalone or as part of `video-pipeline`.

**Standalone**: Ask the user for video path, keyterms, and target duration.

**Via pipeline**: Read from `manifest.json` in the working directory:
- `source` — video file path
- `keyterms` — domain terms for speech-to-text
- `target_duration` — target length (optional)

The thesis is **not** an input. It is inferred from the content after edit decisions are made (see Step 5b).

## Outputs

Shared sources of truth go to the **project root**. Build artifacts go to `cut/`.

| File | Type | Description |
|---|---|---|
| `transcript.json` | **source** | Deepgram transcript with word-level timestamps |
| `utterances.txt` | **source** | Formatted utterances for review |
| `decisions/cut.json` | **source** | LLM edit decisions with reasoning |
| `cut/edit_list.json` | artifact | Compiled segment list |
| `cut/preview.mp4` | artifact | Rendered preview |
| `cut/timeline.fcpxml` | artifact | Final Cut Pro timeline |
| `cut/timeline.otio` | artifact | OpenTimelineIO timeline |

After completion, update `manifest.json` with stage status, file paths, and stats. Add `decisions/cut.json` to the manifest's top-level `decisions` array.

## Process

### Step 1: Gather Inputs

If `manifest.json` exists, read inputs from it. Otherwise, ask the user for:
1. **Video file path** (required)
2. **Domain terms** that may be misrecognized by speech-to-text (product names, people, technical terms). Suggest terms based on context.
3. **Target duration** (optional — default: aim for 10-15 min for YouTube)

Do **not** ask for a thesis. The thesis is inferred after edit decisions (Step 5b).

Create directories `cut/` and `decisions/` if they don't exist.

### Step 2: Transcribe

Transcribe to the **project root** — the transcript is a shared source of truth, not a cut-stage artifact.

```bash
DEEPGRAM_API_KEY=<key> python3 ~/.agents/services/transcribe.py "<video_path>" \
  --keyterms "<comma,separated,terms>" \
  --output transcript.json
```

### Step 3: Format Utterances for Review

```bash
python3 ~/.agents/services/edit.py format transcript.json --output utterances.txt
```

Read `utterances.txt`. Each line is one utterance with index, timestamps, duration, and text.

### Step 4: Make Edit Decisions

Read every utterance. For each, decide **keep** or **remove**.

**Removal rules (rough cut only — no editorial decisions at this stage):**
- **Duplicate takes**: Multiple attempts at the same sentence. Usually keep the LAST complete version. This includes semantically equivalent phrasings — "wanted to dive into" and "had a desire to dive into" are the same take.
- **False starts**: Speaker begins a sentence but abandons it. The next utterance restarts the same thought more completely. But do not remove a short utterance just because the next one is fuller — labels, names, and list items can add distinct information.
- **Fragments**: Isolated single words or sub-second utterances that aren't meaningful are usually removable. But short utterances can still carry tone, rhythm, or useful emphasis.
- **Reactions to mistakes**: "Oh my gosh" after stumbling, nervous laughter between takes — usually remove unless it adds personality, rhythm, or a sense of real-time process the viewer would enjoy.

Editorial decisions (tangential sections, pacing, repeated observations) are **not** made here. They happen in the polish stage, after the thesis has been inferred from the content.

**Critical rule**: The unit of selection is CONTIGUOUS TIME RANGES. Do not assemble fragments from different parts of a paragraph. If a section flows naturally, keep the whole flow. Cuts should feel like jump cuts between complete thoughts, not spliced-together sentence fragments.

For each removal, write a brief reason.

### Step 5: Write Decisions

Write a JSON file with decisions:

```json
{
  "decisions": {
    "000": "keep",
    "001": "remove: false start of 002 ('Pi is a minimal term' vs complete 'Pi is a minimal terminal coding harness')",
    "020": "remove: semantically duplicate of 027 — same intro sentence, different phrasing"
  }
}
```

Save as `decisions/cut.json`.

### Step 5b: Infer Thesis

After making edit decisions, you have read every utterance and know what the speaker actually said. Now synthesize a **thesis** — a one or two sentence description of what this video is about.

Guidelines:
- Ground the thesis in the kept utterances, not the removed ones.
- Focus on what the speaker **does and discovers**, not just the topic. "First look at Pi, exploring extensions, model switching, skills, and cross-agent compatibility" is better than "A video about Pi."
- Include the speaker's perspective or arc if one emerges. "Evaluating Pi as a VIM replacement for AI-assisted coding" captures intent.
- Keep it concrete enough to make editorial decisions against. The polish stage will use this thesis to decide what's tangential and what's essential.

Write the thesis to `manifest.json` (set the `thesis` field). Also save it in the decisions file for auditability:

```json
{
  "decisions": { ... },
  "thesis": "First look at Pi as a coding harness — installing, configuring models, exploring tree-based sessions, sharing, and testing extensions."
}
```

Report the inferred thesis to the user. They can adjust it before the polish stage runs.

### Step 6: Compile Edit List

Compile the decisions into a segment-based edit list. This is a **build step** — decisions are the source, the edit list is the compiled output.

```bash
python3 ~/.agents/services/edit.py apply transcript.json decisions/cut.json \
  --padding 0.05 --output cut/edit_list.json
```

**Important:** `decisions/cut.json` is the contract between stages, not `cut/edit_list.json`. The polish stage will produce its own decisions file (`decisions/polish.json`), and a final compile step merges all decision layers into the polished edit list. The edit list merges contiguous kept utterances into single segments, losing utterance provenance — this is fine because no downstream stage needs to reverse-engineer the mapping.

### Step 7: Generate Timeline

```bash
python3 ~/.agents/services/timeline.py \
  --source "<video_path>" \
  --edits cut/edit_list.json \
  --name "<descriptive timeline name>" \
  --output cut/timeline.otio
```

This generates both `cut/timeline.otio` and `cut/timeline.fcpxml`.

### Step 8: Render Preview

```bash
python3 ~/.agents/services/render.py "<video_path>" \
  --edits cut/edit_list.json \
  --output cut/preview.mp4
```

### Step 9: Update Manifest and Report

Update `manifest.json` — set the shared sources, the `thesis` field, add decisions to the `decisions` array, and write the cut stage entry:

```json
{
  "transcript": "transcript.json",
  "utterances": "utterances.txt",
  "decisions": ["decisions/cut.json"],
  "thesis": "First look at Pi as a coding harness — installing, configuring models, exploring sessions, sharing, and testing extensions.",
  "stages": {
    "cut": {
      "status": "complete",
      "edit_list": "cut/edit_list.json",
      "preview": "cut/preview.mp4",
      "timeline": "cut/timeline.fcpxml",
      "stats": {
        "original_duration": ...,
        "edited_duration": ...,
        "utterances_total": ...,
        "utterances_kept": ...,
        "utterances_removed": ...
      }
    }
  }
}
```

Report to the user:
- Original duration → edited duration (% removed)
- Number of utterances kept vs removed
- Summary of what was cut and why (grouped by category: duplicates, false starts)
- **Inferred thesis** — ask user to confirm or adjust before polish runs
- Paths to outputs
- If running standalone, remind user to open the `.fcpxml` in Final Cut Pro
- If running as part of pipeline, note that polish stage is next and will use the thesis for editorial decisions

## Notes

- The FCPXML references the source video by absolute path. The source video must be accessible at that path when opening in FCP.
- Shared sources (`transcript.json`, `utterances.txt`, `decisions/cut.json`) live at the project root. Build artifacts (`edit_list.json`, `preview.mp4`, timelines) live in `cut/`. The user can review `decisions/cut.json` to understand every cut.
- The cut stage always does a rough cut. Editorial decisions happen in the polish stage, informed by the inferred thesis.
- **Decisions are the contract.** The edit list is a compiled artifact that merges contiguous utterances into segments. Downstream stages (polish) produce their own decisions against the original transcript, and a single compile step merges all layers.
- Edge-case judgment is calibration, not doctrine. Use `evals/` to capture where the operator restored a short utterance, kept a reaction, or treated a would-be false start as a meaningful label.
