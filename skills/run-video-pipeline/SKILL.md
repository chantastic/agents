---
name: run-video-pipeline
description: Orchestrate the video editing pipeline from raw recording through cut, polish, and zoom. Coordinates stage skills, manages the manifest, and structures project files. Use when producing an edit from a raw recording.
role: coordinator
---

# Video Pipeline

Orchestrate a raw recording through cut → polish → zoom.

This is the **coordinator**. It owns the manifest, the sequencing, and the wiring between stages. Individual stage skills (cut-video, polish-video, zoom-video) are context-independent transformation skills — they receive inputs, use services as needed, and produce outputs. This skill provides the inputs, captures the outputs, and updates shared state.

## Required Environment

- `DEEPGRAM_API_KEY` — set in environment
- `ffmpeg` and `ffprobe` — installed
- Python packages: `opentimelineio`, `otio-fcpx-xml-adapter`

## Project Structure

```
project/
├── manifest.json              ← coordinator state (only this skill reads/writes it)
├── transcript.json            ← source of truth: original transcript
├── utterances.txt             ← formatted view of transcript
├── decisions/                 ← source: all decision layers
│   ├── cut.json               ← layer 1: rough cut
│   └── polish.json            ← layer 2: editorial
├── cut/                       ← outputs from cut stage
│   ├── edit_list.json
│   ├── preview.mp4
│   ├── timeline.fcpxml
│   └── timeline.otio
├── polish/                    ← outputs from polish stage
│   ├── pass_1/ ... pass_N/
│   └── final/
│       ├── edit_list.json
│       ├── preview.mp4
│       ├── timeline.fcpxml
│       └── timeline.otio
├── zoom/                      ← outputs from zoom stage
│   ├── frames/
│   ├── zooms.json
│   └── timeline_zoomed.fcpxml
└── publish/                   ← created later by run-video-publish (not part of this pipeline)
```

### Decisions as Contract

The **original transcript** is the shared source of truth. Each stage produces a **decisions layer** in `decisions/`. Edit lists are compiled by merging all decision layers:

```bash
python3 ~/.agents/services/edit.py apply transcript.json \
  decisions/cut.json decisions/polish.json \
  --padding 0.05 --output polish/final/edit_list.json
```

Stages never read or modify each other's edit lists. They only read the transcript and write decisions.

## Manifest

The manifest is the coordinator's state file. **No other skill reads or writes it.**

```json
{
  "source": "/absolute/path/to/video.mp4",
  "keyterms": ["term1", "term2"],
  "thesis": null,
  "target_duration": null,
  "transcript": "transcript.json",
  "utterances": "utterances.txt",
  "decisions": ["decisions/cut.json"],
  "stages": {
    "cut": {
      "status": "complete|in_progress|failed",
      "edit_list": "cut/edit_list.json",
      "preview": "cut/preview.mp4",
      "timeline": "cut/timeline.fcpxml",
      "stats": { ... }
    },
    "polish": { ... },
    "zoom": { ... }
  }
}
```

All file paths are relative to the project directory. Source video path is absolute.

## Process

### Step 1: Initialize project

If no `manifest.json` exists, ask the user for:
1. **Video file path** (required)
2. **Domain keyterms** for speech-to-text (suggest terms based on context)
3. **Target duration** (optional)

Do **not** ask for a thesis. It's inferred after cut.

Create directories: `decisions/`, `cut/`, `polish/`, `zoom/`.

Write the initial manifest:
```json
{
  "source": "<absolute path>",
  "keyterms": [...],
  "thesis": null,
  "target_duration": null,
  "transcript": null,
  "utterances": null,
  "decisions": [],
  "stages": {}
}
```

If `manifest.json` already exists, read it and resume from the last incomplete stage.

### Step 2: Run cut

**Extract inputs for cut-video:**
- `source` → `manifest.source`
- `keyterms` → `manifest.keyterms`
- `target_duration` → `manifest.target_duration`
- `output_dir` → project directory

**Invoke cut-video** with these inputs.

**Capture outputs:**
- `transcript.json` and `utterances.txt` at project root
- `decisions/cut.json`
- `cut/edit_list.json`, `cut/preview.mp4`, `cut/timeline.fcpxml`, `cut/timeline.otio`
- Inferred thesis (from `decisions/cut.json`)

**Update manifest:**
- Set `transcript`, `utterances`
- Set `thesis` from the cut skill's output
- Append `decisions/cut.json` to `decisions` array
- Write `stages.cut` with status, paths, and stats

**Checkpoint:** Report the inferred thesis. Ask operator to confirm or adjust before polish.

### Step 3: Run polish

**Extract inputs for polish-video:**
- `source` → `manifest.source`
- `preview` → `manifest.stages.cut.preview`
- `transcript` → `manifest.transcript`
- `thesis` → `manifest.thesis`
- `decisions` → `manifest.decisions` (array of paths)
- `keyterms` → `manifest.keyterms`
- `output_dir` → project directory

**Invoke polish-video** with these inputs.

**Capture outputs:**
- `decisions/polish.json`
- `polish/final/edit_list.json`, `polish/final/preview.mp4`, `polish/final/timeline.fcpxml`, `polish/final/timeline.otio`
- Pass count and stats

**Update manifest:**
- Append `decisions/polish.json` to `decisions` array
- Write `stages.polish` with status, paths, and stats

### Step 4: Run zoom

**Extract inputs for zoom-video:**
- `source` → `manifest.source`
- `edit_list` → `manifest.stages.polish.edit_list` (or `stages.cut.edit_list` if no polish)
- `preview` → `manifest.stages.polish.preview` (or `stages.cut.preview`)
- `thesis` → `manifest.thesis`
- `output_dir` → project directory

**Invoke zoom-video** with these inputs.

**Capture outputs:**
- `zoom/zooms.json`, `zoom/timeline_zoomed.fcpxml`
- Zoom count and stats

**Update manifest:**
- Write `stages.zoom` with status, paths, and stats

### Step 5: Report

| Metric | Value |
|---|---|
| Original duration | from manifest |
| Cut duration | from cut stats |
| Polished duration | from polish stats |
| Total removed | original − polished (% of original) |

**Produced:**
- `zoom/timeline_zoomed.fcpxml` — open in Final Cut Pro
- `polish/final/timeline.otio` — portable timeline
- `polish/final/preview.mp4` — rendered preview
- `manifest.json` — full audit trail

**Operator handoff:**
1. Open `zoom/timeline_zoomed.fcpxml` in Final Cut Pro
2. Review and adjust the edit manually
3. Export the final video from FCP
4. Run `run-video-publish` on that export to generate publish assets

## Resuming

If invoked on a project with an existing manifest:
- Read the manifest
- Check each stage's status
- Resume from the first incomplete stage
- Do not re-run completed stages unless the user explicitly asks

## Re-running a stage

If the user asks to re-run a stage:
1. Archive the existing stage directory (rename to `cut_prev/` or similar)
2. Archive the decisions file
3. Remove that stage's decisions from the manifest `decisions` array
4. Clear all downstream stages (re-cutting invalidates polish)
5. Re-run from that stage forward

## Skipping stages

The operator may want to skip stages (e.g., skip polish for a quick cut, skip zoom for audio-only content). When the operator indicates a skip:

1. Mark the stage as `"skipped"` in the manifest
2. Wire the next stage's inputs from the last completed stage's outputs
3. Do not ask "are you sure?" — the operator owns intent

Example: skipping polish means zoom receives cut's edit list and preview instead of polish's.

## Notes

- **The manifest is the coordinator's state, not a shared contract.** Individual skills never read it. This skill extracts inputs from it and passes them explicitly.
- **Decisions are source, edit lists are compiled.** Each stage produces a decisions file against the original transcript. Edit lists are built by compiling all decision layers.
- **Publish is not a pipeline stage.** It runs standalone after the human exports from FCP. It can optionally receive thesis and keyterms from the operator (who may read them from the manifest, but publish doesn't).
- **Human intervention is part of the system.** The thesis checkpoint after cut, the FCP review after zoom, and the export before publish are all modeled as explicit handoffs.
