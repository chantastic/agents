---
name: video-pipeline
description: Orchestrate the video editing pipeline from raw recording through cut, polish, and zoom. Coordinates stage skills, manages the manifest, and structures project files. Use when producing an edit from a raw recording.
---

# Video Pipeline

Orchestrate a raw recording through cut → polish → zoom.

## Required Environment

- `DEEPGRAM_API_KEY` — set in environment
- `ffmpeg` and `ffprobe` — installed
- Python packages: `opentimelineio`, `otio-fcpx-xml-adapter`

## Project Structure

Every video project uses this directory layout. **Sources of truth live at the root. Build artifacts live in stage directories.**

```
project/
├── manifest.json              ← shared state across stages
├── transcript.json            ← source of truth: original transcript
├── utterances.txt             ← formatted view of transcript
├── decisions/                 ← source: all decision layers
│   ├── cut.json               ← layer 1: rough cut (fragments, false starts)
│   └── polish.json            ← layer 2: editorial (tangents, pacing, filler)
├── cut/                       ← build artifacts from cut stage
│   ├── edit_list.json
│   ├── preview.mp4
│   ├── timeline.fcpxml
│   └── timeline.otio
├── polish/                    ← build artifacts + working files from polish
│   ├── pass_1/
│   │   ├── preview_transcript.json
│   │   ├── preview_utterances.txt
│   │   └── eval.json
│   ├── pass_N/
│   │   ├── preview.mp4
│   │   ├── preview_transcript.json
│   │   ├── preview_utterances.txt
│   │   └── eval.json
│   └── final/
│       ├── edit_list.json
│       ├── preview.mp4
│       ├── timeline.fcpxml
│       └── timeline.otio
├── zoom/                      ← zoom stage outputs (FCPXML-only, no OTIO)
│   ├── frames/
│   ├── zooms.json
│   └── timeline_zoomed.fcpxml
└── publish/                   ← created later by `video-publish`, after manual FCP review/export
    ├── transcript.json        ← derived: transcript of the final edit
    ├── utterances.txt
    ├── chapters.json
    ├── chapters.txt           ← YouTube-formatted chapter list
    ├── description.md
    ├── captions.srt
    ├── captions.vtt
    └── thumbnails/
        ├── concepts.json
        └── T001.png ...
```

### Decisions as Contract

The **original transcript** (`transcript.json`) is the shared source of truth for all stages. Each stage produces a **decisions layer** in `decisions/` — a set of keep/remove decisions against the original utterance indices:

```
decisions/cut.json      → layer 1: fragments, false starts, duplicate takes
decisions/polish.json   → layer 2: tangents, pacing drag, filler, editorial
```

Edit lists are **compiled artifacts** — produced by merging all decision layers in a single build step:

```bash
python3 ~/.agents/services/edit.py apply transcript.json \
  decisions/cut.json decisions/polish.json \
  --padding 0.05 --output polish/final/edit_list.json
```

Stages never read or modify each other's edit lists. They only read the transcript and write decisions.

## Manifest

The manifest (`manifest.json`) is the single source of truth for pipeline state. Every stage reads it first and writes it last.

```json
{
  "source": "/absolute/path/to/video.mp4",
  "keyterms": ["term1", "term2"],
  "thesis": "Inferred after cut stage — null until then",
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

The top-level `decisions` array lists all decision layers in order. Each stage appends its decisions path when complete. The compile step always uses this array.

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
  "transcript": null,
  "utterances": null,
  "decisions": [],
  "stages": {}
}
```

Create directories: `decisions/`, `cut/`, `polish/`, `zoom/`.

If `manifest.json` already exists, read it and resume from the last incomplete stage.

### Step 2: Run stages

Execute stages in order: **cut → polish → zoom**. For each stage:

1. Check `manifest.stages.<stage>.status`
2. If `"complete"` — skip (or ask user if they want to re-run)
3. If missing or `"in_progress"` — invoke the stage skill
4. After completion, update the manifest with status, file paths, and stats

#### Stage: cut

Invoke the `video-cut` skill. It transcribes the video (writing `transcript.json` and `utterances.txt` at the project root), makes rough cut decisions (writing `decisions/cut.json`), and compiles them into `cut/edit_list.json` and a preview.

Cut performs a **rough cut only** — removing duplicate takes, false starts, and fragments. No editorial decisions yet.

After the cut stage completes, the cut skill infers a **thesis** from the kept utterances and writes it to the manifest. This thesis describes what the video is actually about, grounded in the content the speaker chose to say. The user can review and adjust it before polish runs.

#### Stage: polish

Invoke the `video-polish` skill. It reads the cut preview, transcript, **and the inferred thesis** from the manifest. With the thesis now available, polish can make editorial pacing decisions — removing tangential sections, compressing debugging loops, cutting screen-reading. This is where the bulk of editorial improvement happens.

Polish writes `decisions/polish.json` (decision layer 2) — additional removals against the same original transcript. The final edit list is compiled from all layers:

```bash
python3 ~/.agents/services/edit.py apply transcript.json \
  decisions/cut.json decisions/polish.json \
  --padding 0.05 --output polish/final/edit_list.json
```

Polish never reads or modifies `cut/edit_list.json`. It only adds decisions.

#### Stage: zoom

Invoke the `video-zoom` skill. It reads the polished edit list and preview from the manifest, analyzes the transcript and frames for zoom opportunities, and generates an FCPXML with adjustment clips. This stage is FCPXML-only — no OTIO equivalent exists for adjustment clips. The OTIO timeline from polish remains the portable format.

#### After the pipeline: publish

The `video-publish` skill runs **standalone**, not as part of this pipeline. There is a human step between zoom and publish — the user opens the zoomed FCPXML in Final Cut Pro, reviews/adjusts, and exports the final video. Once the export exists, invoke `video-publish` directly.

Publish reads context from the manifest where available (especially `thesis` and `keyterms`) but does not write to it. Speaker attribution is inferred by `video-publish` from the export context (filename/stream naming), defaulting to `chantastic`, and asking the operator if uncertain. Its outputs are just files — captions, chapters, description, thumbnails.

### Step 3: Report

After all stages complete, report:

| Metric | Value |
|---|---|
| Original duration | from manifest |
| Cut duration | from cut stats |
| Polished duration | from polish stats |
| Total removed | original − polished (% of original) |

**Produced now** (from manifest paths):
- `zoom/timeline_zoomed.fcpxml` — open in Final Cut Pro (includes zoom adjustment clips)
- `polish/final/timeline.otio` — portable timeline (no zooms)
- `polish/final/preview.mp4` — rendered preview
- `manifest.json` — full audit trail

**Operator handoff**:
1. Open `zoom/timeline_zoomed.fcpxml` in Final Cut Pro
2. Review and adjust the edit manually
3. Export the final video from FCP
4. Run `video-publish` on that export to generate publish assets

## Resuming

If invoked on a project with an existing manifest:
- Read the manifest
- Check each stage's status
- Resume from the first incomplete stage
- Do not re-run completed stages unless the user explicitly asks

## Re-running a stage

If the user asks to re-run a stage (e.g., "re-cut with different editorial decisions"):
1. Archive the existing stage directory (rename to `cut_prev/` or similar)
2. Archive the decisions file (rename `decisions/cut.json` → `decisions/cut_prev.json`)
3. Remove that stage's decisions from the manifest `decisions` array
4. Also clear all downstream stages (re-cutting invalidates polish)
5. Re-run from that stage forward

## Notes

- The manifest is the contract between skills. A stage skill should never need to ask the user for information that's already in the manifest.
- All paths in the manifest are relative to the project directory. The source video path is absolute (it may live outside the project).
- **Decisions are source, edit lists are compiled.** Each stage produces a decisions file against the original transcript. Edit lists are built by compiling all decision layers. Stages never modify each other's edit lists.
- `edit.py apply` accepts multiple decision files. Any utterance marked "remove" in any layer is removed. This makes the compile step trivial regardless of how many stages add decisions.
- `publish/` is part of the overall project lifecycle, but it is created later by the standalone `video-publish` skill after operator review/export. It is not a pipeline stage in this skill.
- Experimental branches (like older b-roll workflows) should stay out of the canonical pipeline contract until they are revived and standardized.
