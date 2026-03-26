# Evaluate Skill Output — Sidecar Schema

Canonical schema for structured eval sidecars.

The goal is not to eliminate narrative evals. The goal is to pair them with machine-readable summaries so patterns can be counted across runs.

## Pairing rule

Every eval should be saved as two files with the **same basename**:

```text
.../evals/<date>-<slug>.md
.../evals/<date>-<slug>.json
```

- `.md` = narrative analysis for humans / LLMs
- `.json` = structured sidecar for aggregation, comparison, dashboards, and calibration

## Design principles

1. **Generic-first** — the core fields should work for any skill
2. **Best effort** — do not block eval writing just because a field is unknown
3. **Narrate meaning, structure counts** — prose explains why; JSON records what / how often / where
4. **Domain blocks are optional** — use `domain` for video-specific or skill-specific data
5. **Backfills are allowed to be incomplete** — older evals can omit fields that were never captured explicitly

## Core shape

```json
{
  "version": 1,
  "date": "2026-03-25",
  "skill": "video-pipeline",
  "project_slug": "pi-first-look",
  "eval_type": "self",
  "reviewer": {
    "agent": "openai-codex-gpt-5-4-high",
    "settings": {
      "ov": 3
    }
  },
  "source": {
    "path": "~/Downloads/example.mp4",
    "duration_seconds": 3853
  },
  "summary": {
    "outcome": "good",
    "one_line": "Strong cut, conservative polish, under-dense zooms."
  },
  "artifacts_reviewed": [
    "manifest.json",
    "decisions/cut.json"
  ],
  "process_adherence": {
    "followed": [],
    "deviations": []
  },
  "metrics": {},
  "categories": {},
  "issues": [],
  "recommendations": [],
  "feedback_hooks": [],
  "domain": {}
}
```

## Required fields

These should exist on every new sidecar:

- `version` — integer schema version, starts at `1`
- `date` — `YYYY-MM-DD`
- `skill` — skill being evaluated
- `project_slug` — stable slug for the run / project
- `eval_type` — one of:
  - `self`
  - `diff`
  - `review`
- `reviewer.agent` — model or reviewer identifier when known
- `summary.outcome` — one of:
  - `excellent`
  - `good`
  - `mixed`
  - `poor`
- `summary.one_line` — single-sentence summary
- `recommendations` — array (can be empty)
- `domain` — object (can be empty)

## Optional but strongly recommended fields

### `reviewer.settings`
Freeform object for model/operator settings when known.

Example:

```json
{
  "ov": 3,
  "temperature": null
}
```

### `source`
Best for runs tied to a media file or source artifact.

Suggested keys:
- `path`
- `duration_seconds`

### `artifacts_reviewed`
Array of strings naming the files/artifacts read to produce the eval.

### `process_adherence`
Tracks whether the documented method was followed.

```json
{
  "followed": ["re-transcribed preview"],
  "deviations": [
    {
      "step": "thesis confirmation",
      "severity": "medium",
      "description": "Reported thesis but did not explicitly ask for confirmation."
    }
  ]
}
```

Severity values should be one of:
- `low`
- `medium`
- `high`

### `metrics`
Freeform numeric metrics for the run.

Examples:
- `original_duration_seconds`
- `final_duration_seconds`
- `duration_removed_seconds`
- `duration_removed_pct`
- `passes_run`
- `zoom_count`

### `categories`
Category summary map.

Use when you want countable buckets such as:
- `duplicate_detection`
- `false_starts`
- `pacing_drag`
- `zoom_density`
- `ux_flow`

Recommended shape:

```json
{
  "pacing_drag": {
    "count": 12,
    "assessment": "under-aggressive"
  }
}
```

### `issues`
Specific problems or learnings from the run.

Recommended shape:

```json
{
  "id": "issue_001",
  "stage": "polish",
  "category": "pacing_drag",
  "severity": "high",
  "title": "Screen narration under-cut",
  "description": "Kept too much reading of visible screen content.",
  "operator_takeaway": "Cut harder when the viewer can already read the screen."
}
```

### `recommendations`
Actionable follow-ups. This is one of the most important fields.

Recommended shape:

```json
{
  "priority": "P1",
  "scope": "skill",
  "target": "video-polish",
  "action": "Add screen narration as an explicit pacing_drag subtype."
}
```

Suggested `scope` values:
- `skill`
- `service`
- `workflow`
- `operator`
- `documentation`

### `feedback_hooks`
What to ask or compare later to improve future runs.

Recommended shape:

```json
{
  "category": "zoom_calibration",
  "question": "Did the user keep or remove most suggested zooms?",
  "how_to_compare": "Diff zooms.json against the reviewer's FCPXML."
}
```

## Domain-specific extensions

Use `domain` for structured data that is meaningful only for a subset of skills.

### Example: video

```json
{
  "domain": {
    "video": {
      "editing": {
        "utterances_total": 463,
        "utterances_removed": 55,
        "word_edits_applied": 3
      },
      "zoom": {
        "zoom_count": 27,
        "density_per_min": 1.6
      },
      "diff": {
        "extra_time_user_cut_seconds": 190,
        "false_negatives": {
          "screen_narration": 55
        }
      }
    }
  }
}
```

### Example: upload

```json
{
  "domain": {
    "youtube_upload": {
      "audio_normalized": true,
      "input_lufs": -39.2,
      "output_lufs": -14.0,
      "thumbnail_uploaded": true,
      "captions_uploaded": true
    }
  }
}
```

## Backfill policy

When backfilling older evals:
- preserve the `.md` as-is
- add a `.json` sidecar with best-effort extraction
- leave unknown fields out or set them to `null`
- do not invent precision the original eval did not support

## Future evolution

If the schema needs to change incompatibly, increment `version`.

Keep version upgrades small. A lightweight, durable schema is better than a theoretically complete one that nobody maintains.
