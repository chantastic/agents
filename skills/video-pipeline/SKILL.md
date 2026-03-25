---
name: video-pipeline
description: Orchestrate a full video production pipeline from raw recording to polished edit. Coordinates video-cut and video-polish stages, manages the manifest, and structures project files. Use when producing a video from a raw recording.
---

# Video Pipeline

Orchestrate a raw recording through cut → polish → final output.

## Required Environment

- `DEEPGRAM_API_KEY` — set in environment
- `ffmpeg` and `ffprobe` — installed
- Python packages: `opentimelineio`, `otio-fcpx-xml-adapter`

## Project Structure

Every video project uses this directory layout:

```
project/
├── manifest.json              ← shared state across stages
├── cut/                       ← video-cut outputs
│   ├── transcript.json
│   ├── utterances.txt
│   ├── decisions.json
│   ├── edit_list.json
│   ├── preview.mp4
│   ├── timeline.fcpxml
│   └── timeline.otio
├── polish/                    ← video-polish outputs
│   ├── pass_1/
│   │   ├── word_map.json
│   │   ├── preview_transcript.json
│   │   ├── preview_utterances.txt
│   │   └── eval.json
│   ├── pass_N/
│   │   ├── edit_list.json
│   │   ├── preview.mp4
│   │   ├── preview_transcript.json
│   │   ├── preview_utterances.txt
│   │   └── eval.json
│   └── final/
│       ├── edit_list.json
│       ├── preview.mp4
│       ├── timeline.fcpxml
│       └── timeline.otio
├── zoom/                      ← video-zoom outputs (FCPXML-only, no OTIO)
│   ├── frames/                ← extracted frames for anchor analysis
│   ├── zooms.json             ← zoom decisions
│   └── timeline_zoomed.fcpxml ← final FCPXML with adjustment clips
└── broll/                     ← future: broll-research outputs
```

## Manifest

The manifest (`manifest.json`) is the single source of truth. Every stage reads it first and writes it last.

```json
{
  "source": "/absolute/path/to/video.mp4",
  "keyterms": ["term1", "term2"],
  "thesis": "Inferred after cut stage — null until then",
  "target_duration": null,
  "stages": {
    "cut": {
      "status": "complete|in_progress|failed",
      "transcript": "cut/transcript.json",
      "decisions": "cut/decisions.json",
      "edit_list": "cut/edit_list.json",
      "preview": "cut/preview.mp4",
      "timeline": "cut/timeline.fcpxml",
      "stats": { ... }
    },
    "polish": {
      "status": "complete|in_progress|failed",
      "passes": 2,
      "edit_list": "polish/final/edit_list.json",
      "preview": "polish/final/preview.mp4",
      "timeline": "polish/final/timeline.fcpxml",
      "stats": { ... }
    },
    "zoom": {
      "status": "complete|in_progress|failed",
      "zooms": "zoom/zooms.json",
      "timeline": "zoom/timeline_zoomed.fcpxml",
      "stats": { ... }
    }
  }
}
```

All file paths in the manifest are **relative to the project directory**.

## Process

### Step 1: Initialize project

If no `manifest.json` exists, ask the user for:
1. **Video file path** (required)
2. **Domain keyterms** for speech-to-text (suggest terms based on context)
3. **Target duration** (optional)

Do **not** ask for a thesis. The thesis is inferred from the content after the cut stage.

Create the directory structure and write the initial manifest:

```json
{
  "source": "<absolute path>",
  "keyterms": [...],
  "thesis": null,
  "target_duration": null,
  "stages": {}
}
```

If `manifest.json` already exists, read it and resume from the last incomplete stage.

### Step 2: Run stages

Execute stages in order: **cut → polish → zoom**. For each stage:

1. Check `manifest.stages.<stage>.status`
2. If `"complete"` — skip (or ask user if they want to re-run)
3. If missing or `"in_progress"` — invoke the stage skill
4. After completion, update the manifest with status, file paths, and stats

#### Stage: cut

Invoke the `video-cut` skill. It reads inputs from the manifest and writes outputs to `cut/`. The cut stage performs a **rough cut only** — removing duplicate takes, false starts, and fragments. No editorial decisions yet.

After the cut stage completes, the cut skill infers a **thesis** from the kept utterances and writes it to the manifest. This thesis describes what the video is actually about, grounded in the content the speaker chose to say. The user can review and adjust it before polish runs.

#### Stage: polish

Invoke the `video-polish` skill. It reads the cut stage outputs **and the inferred thesis** from the manifest. With the thesis now available, polish can make editorial pacing decisions — removing tangential sections, compressing debugging loops, cutting screen-reading. This is where the bulk of editorial improvement happens.

#### Stage: zoom

Invoke the `video-zoom` skill. It reads the polished edit list and preview from the manifest, analyzes the transcript and frames for zoom opportunities, and generates an FCPXML with adjustment clips. This stage is FCPXML-only — no OTIO equivalent exists for adjustment clips. The OTIO timeline from polish remains the portable format.

### Step 3: Report

After all stages complete, report:

| Metric | Value |
|---|---|
| Original duration | from manifest |
| Cut duration | from cut stats |
| Polished duration | from polish stats |
| Total removed | original − polished (% of original) |

**Final outputs** (from manifest paths):
- `zoom/timeline_zoomed.fcpxml` — open in Final Cut Pro (includes zoom adjustment clips)
- `polish/final/timeline.otio` — portable timeline (no zooms)
- `polish/final/preview.mp4` — rendered preview
- `manifest.json` — full audit trail

## Resuming

If invoked on a project with an existing manifest:
- Read the manifest
- Check each stage's status
- Resume from the first incomplete stage
- Do not re-run completed stages unless the user explicitly asks

## Re-running a stage

If the user asks to re-run a stage (e.g., "re-cut with different editorial decisions"):
1. Archive the existing stage directory (rename to `cut_prev/` or similar)
2. Clear that stage's manifest entry
3. Also clear all downstream stages (re-cutting invalidates polish)
4. Re-run from that stage forward

## Notes

- The manifest is the contract between skills. A stage skill should never need to ask the user for information that's already in the manifest.
- All paths in the manifest are relative to the project directory. The source video path is absolute (it may live outside the project).
- Future stages (broll, publish) can be added to the pipeline by extending the manifest schema and adding stage directories.
