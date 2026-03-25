# Video Pipeline Contract

Canonical contract for the active video workflow.

This document exists to keep the skills aligned on:
- project layout
- manifest shape
- field ownership
- source vs artifact boundaries
- stage boundaries
- operator handoff points

If the workflow changes, update this file first, then update the dependent skills.

---

## Scope

The active pipeline is:

```text
video-cut → video-polish → video-zoom
```

This contract does **not** include `video-publish` as a pipeline stage. Publish happens **after** manual operator review and export in Final Cut Pro.

Older b-roll experiments are **not** part of the canonical contract.

---

## Lifecycle

### Automated pipeline stages

1. **cut** — transcribe source, make rough-cut decisions, infer thesis
2. **polish** — evaluate the cut preview, add editorial removals and word edits
3. **zoom** — generate FCPXML zoom/title clips against the polished edit

### Operator handoff

After `zoom`, the operator:
1. opens the zoomed timeline in Final Cut Pro
2. reviews and adjusts the edit manually
3. exports the final video

### Post-handoff standalone stage

4. **publish** — reads the exported final video and generates captions, chapters, titles, description, thumbnails, and a content brief

`publish` is part of the broader project lifecycle, but **not** part of the automated `video-pipeline` stage chain.

---

## Canonical Project Layout

```text
project/
├── manifest.json
├── transcript.json
├── utterances.txt
├── decisions/
│   ├── cut.json
│   └── polish.json
├── cut/
│   ├── edit_list.json
│   ├── preview.mp4
│   ├── timeline.fcpxml
│   └── timeline.otio
├── polish/
│   ├── pass_1/
│   ├── pass_N/
│   └── final/
│       ├── edit_list.json
│       ├── preview.mp4
│       ├── timeline.fcpxml
│       └── timeline.otio
├── zoom/
│   ├── frames/
│   ├── zooms.json
│   └── timeline_zoomed.fcpxml
└── publish/
    ├── transcript.json
    ├── utterances.txt
    ├── chapters.json
    ├── chapters.txt
    ├── titles.json
    ├── description.md
    ├── brief.json
    ├── captions.srt
    ├── captions.vtt
    └── thumbnails/
```

### Notes on layout

- `publish/` appears in the canonical project layout because it is part of the overall project lifecycle.
- `publish/` is created later by the standalone `video-publish` skill, after operator intervention.
- `broll/` and `broll-research/` are intentionally omitted from the canonical layout. They belong to older experiments and can be recovered from git history if needed.

---

## Source vs Artifact Rules

### Shared sources of truth

These are the durable inputs and decision layers that downstream stages reason against:

- `transcript.json` — original transcript
- `utterances.txt` — formatted view of the original transcript
- `decisions/cut.json` — rough-cut decision layer
- `decisions/polish.json` — polish decision layer
- `manifest.json` — pipeline state and stage outputs

### Compiled / build artifacts

These are generated from source files and can be re-built:

- `cut/edit_list.json`
- `polish/final/edit_list.json`
- previews (`cut/preview.mp4`, `polish/pass_*/preview.mp4`, `polish/final/preview.mp4`)
- timelines (`*.fcpxml`, `*.otio`)
- `zoom/zooms.json` is a stage output, but it is not a shared upstream source like the transcript/decisions layers; it belongs to the zoom stage's output contract
- everything under `publish/`

### Core principle

**Decisions are source. Edit lists are compiled artifacts.**

Stages should not mutate each other's edit lists. They should read shared sources and write their own outputs.

---

## Manifest Contract

All manifest paths are relative to the project directory except the source media path.

### Canonical shape

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
      "stats": {}
    },
    "polish": {
      "status": "complete|in_progress|failed",
      "passes": 2,
      "edit_list": "polish/final/edit_list.json",
      "preview": "polish/final/preview.mp4",
      "timeline": "polish/final/timeline.fcpxml",
      "stats": {}
    },
    "zoom": {
      "status": "complete|in_progress|failed",
      "zooms": "zoom/zooms.json",
      "timeline": "zoom/timeline_zoomed.fcpxml",
      "stats": {}
    }
  }
}
```

### Field ownership

- `source` — pipeline initialization
- `keyterms` — pipeline initialization / operator input
- `target_duration` — pipeline initialization / operator input
- `transcript` — `video-cut`
- `utterances` — `video-cut`
- `thesis` — `video-cut` after reviewing kept content
- `decisions[]` — appended by stages that produce decision layers
- `stages.cut.*` — `video-cut`
- `stages.polish.*` — `video-polish`
- `stages.zoom.*` — `video-zoom`

### Not owned by manifest as a required upstream field

`speakers` is **not** a required manifest field in the active contract.

Reason: the strongest evidence for speaker attribution usually appears later, during publish, when the system can inspect the final export filename or stream naming.

---

## Speaker Attribution Contract

Speaker attribution is resolved by `video-publish` using this precedence:

1. infer from export filename / project title if guest names are obvious
2. inspect stream metadata or naming conventions from Restream exports if available
3. default to `chantastic`
4. ask the operator if uncertain

This avoids forcing earlier stages to invent speaker metadata before the best evidence exists.

---

## Reporting Contract

### Pipeline reports must describe present-tense truth

`video-pipeline` should report:
- what was produced now
- what the operator should do next
- what later standalone step can be run after that

It should **not** present `publish/*` outputs as if they already exist when `video-publish` has not been run.

### Recommended report shape

#### Produced now
- `zoom/timeline_zoomed.fcpxml`
- `polish/final/timeline.otio`
- `polish/final/preview.mp4`
- `manifest.json`

#### Operator handoff
1. open the zoomed timeline in FCP
2. review and adjust manually
3. export final video
4. run `video-publish`

---

## Experimental Branches

Experimental workflows should remain outside the canonical contract until they are revived and standardized.

For now this includes:
- older b-roll workflows (`broll/`, `broll-research/`)

If one is revived later, decide:
1. whether it is a standalone skill or pipeline stage
2. what directory layout it owns
3. whether it writes decisions, artifacts, or both
4. how it appears in the manifest

Only then should it be reintroduced into this contract.

---

## Change Management Rule

When the architecture changes:

1. update this contract first
2. update every dependent skill that consumes the changed assumption
3. only then treat the new behavior as canonical

This is how contract drift stays small.
