---
name: video-cut
description: Create a rough cut and editorial cut from a video recording. Transcribes with Deepgram, uses the LLM to remove duplicate takes and make editorial decisions, outputs FCPXML for Final Cut Pro. Use when editing video recordings, removing retakes, or creating YouTube-ready cuts.
---

# Video Cut

Create a publication-ready video edit from a raw recording.

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

All outputs go to `cut/` within the project directory:

| File | Description |
|---|---|
| `cut/transcript.json` | Deepgram transcript with word-level timestamps |
| `cut/utterances.txt` | Formatted utterances for review |
| `cut/decisions.json` | LLM edit decisions with reasoning |
| `cut/edit_list.json` | Applied segment list |
| `cut/preview.mp4` | Rendered preview |
| `cut/timeline.fcpxml` | Final Cut Pro timeline |
| `cut/timeline.otio` | OpenTimelineIO timeline |

After completion, update `manifest.json` with stage status, file paths, and stats.

## Process

### Step 1: Gather Inputs

If `manifest.json` exists, read inputs from it. Otherwise, ask the user for:
1. **Video file path** (required)
2. **Domain terms** that may be misrecognized by speech-to-text (product names, people, technical terms). Suggest terms based on context.
3. **Target duration** (optional — default: aim for 10-15 min for YouTube)

Do **not** ask for a thesis. The thesis is inferred after edit decisions (Step 5b).

Create `cut/` directory if it doesn't exist.

### Step 2: Transcribe

```bash
DEEPGRAM_API_KEY=<key> python3 ~/.agents/services/transcribe.py "<video_path>" \
  --keyterms "<comma,separated,terms>" \
  --output cut/transcript.json
```

### Step 3: Format Utterances for Review

```bash
python3 ~/.agents/services/edit.py format cut/transcript.json --output cut/utterances.txt
```

Read `cut/utterances.txt`. Each line is one utterance with index, timestamps, duration, and text.

### Step 4: Make Edit Decisions

Read every utterance. For each, decide **keep** or **remove**.

**Removal rules (rough cut only — no editorial decisions at this stage):**
- **Duplicate takes**: Multiple attempts at the same sentence. Keep the LAST complete version. This includes semantically equivalent phrasings — "wanted to dive into" and "had a desire to dive into" are the same take.
- **False starts**: Speaker begins a sentence but abandons it. The next utterance restarts the same thought more completely.
- **Fragments**: Isolated single words or sub-second utterances that aren't meaningful (not interjections like "okay", "nice", "wow").
- **Reactions to mistakes**: "Oh my gosh" after stumbling, nervous laughter between takes — remove unless it adds personality.

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

Save as `cut/decisions.json`.

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

### Step 6: Apply Decisions

```bash
python3 ~/.agents/services/edit.py apply cut/transcript.json cut/decisions.json \
  --padding 0.05 --output cut/edit_list.json
```

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

Update `manifest.json` — both the `thesis` field (top-level) and the cut stage entry:

```json
{
  "thesis": "First look at Pi as a coding harness — installing, configuring models, exploring sessions, sharing, and testing extensions.",
  "stages": {
    "cut": {
      "status": "complete",
      "transcript": "cut/transcript.json",
      "utterances": "cut/utterances.txt",
      "decisions": "cut/decisions.json",
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
- All intermediate files are saved in `cut/` for auditability. The user can review `cut/decisions.json` to understand every cut.
- The cut stage always does a rough cut. Editorial decisions happen in the polish stage, informed by the inferred thesis.
