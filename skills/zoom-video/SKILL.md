---
name: zoom-video
description: Add zoom and punch-in effects to a video edit via FCPXML adjustment clips. Analyzes transcript and frames to identify zoom opportunities, determines focal points, and generates FCPXML with adjustment clips on lane 1. Use after polish-video to add visual emphasis.
role: transformation
---

# Video Zoom

This is a transformation skill. It adds a visual emphasis layer to an existing edit without owning workflow state.

Add zoom/punch-in effects to a polished video edit using FCPXML adjustment clips.

## Epistemic Status

- **Principles** — durable ideas that should survive across projects
- **Heuristics** — useful defaults that may vary by format
- **Preferences** — stated as taste, not law
- **Calibration** — exact scale ranges, density, anchor clusters, plugin quirks. Belongs in `evals/`

## Required Environment

- `ffmpeg` and `ffprobe` — installed

## Inputs

| Input | Required | Discovery | Description |
|-------|----------|-----------|-------------|
| source | yes | discover: largest .mov in cwd | Original video file |
| edit_list | yes | discover: polish/final/edit_list.json or cut/edit_list.json | Edit list from the latest stage |
| preview | yes | discover: polish/final/preview.mp4 or cut/preview.mp4 | Preview video from the latest stage |
| thesis | no | ask | Video goal (guides zoom selection) |
| output_dir | no | default: working directory | Where to write outputs |

When run standalone, discover or ask for each input. When run via a coordinator, these are provided explicitly.

## Outputs

| File | Description |
|---|---|
| `zoom/frames/Z001.jpg` ... | Extracted frames at each zoom point |
| `zoom/zooms.json` | Zoom decisions with timing, scale, and anchor |
| `zoom/timeline_zoomed.fcpxml` | FCPXML with adjustment clips (FCP-only, no OTIO) |

## Principles

### The best zooms are functional and expressive at the same time

A zoom should make something visible AND carry editorial weight. If it's only practical (guiding the eye to text), it feels clinical. If it's only expressive (punching in for emphasis on already-visible content), it feels like a gimmick. Both together feels like good editing.

### Scale solves a visibility problem

Each zoom tier solves a progressively harder visibility problem:
- **Guide**: content is readable but the viewer doesn't know where to look. The zoom says "this part matters."
- **Emphasis**: content is visible but the moment is important. The zoom says "pay attention."
- **Extreme**: content is genuinely not visible at full scale (a small icon, a fleeting animation). The zoom makes it possible to see.

### Zooms are phrases, not punctuation marks

A zoom should span a *thought*, not a clip. Use overhang to extend a zoom across multiple edit points, creating visual continuity across jump cuts.

### Scale follows section, anchor follows content

Hold the same scale within a topical section. Change only the anchor position to follow content. Change scale when the *section* changes, not when the *clip* changes.

### Webcam zooms frame the video

The webcam tier bookends the video: opening, occasional mid-video punctuation, and closing.

## Process

### Step 1: Read the preview transcript

Read the preview utterances (from the preview video or a co-located transcript). These are the viewer's experience.

If no transcript exists alongside the preview, transcribe it:

```bash
python3 ~/.agents/services/edit.py format <transcript> --output zoom/preview_utterances.txt
```

### Step 2: Segment into topical sections

Segment the transcript into topical sections. Classify each:
- **screen_focused**: speaker discusses visible screen content
- **camera_moment**: personal statement, reaction, emotional beat
- **mixed**: alternating

### Step 3: Assign zoom tiers per section

| Tier | Intent | Animation |
|---|---|---|
| **Webcam** | Zoom into camera/face. Personal moments. | eased in+out |
| **Guide** | Direct attention to screen content. | instant in; ease out |
| **Emphasis** | Highlight an important moment. Key reveals. | instant in, ease out |
| **Extreme** | Make small/fleeting target visible. Rare (1–2 per video). | instant in, instant out |

### Step 4: Select zoom points and anchors

**Starting heuristic: ~3–4 zooms per minute.**

For each zoom point:

1. **Extract a frame**:
   ```bash
   ffmpeg -y -ss <seconds> -i <preview> -frames:v 1 -vf "scale=960:-1" -q:v 10 zoom/frames/<id>.jpg
   ```

2. **Read the frame** to determine anchor position.

3. **Set animation** based on moment energy:
   | Moment | Animation |
   |---|---|
   | Reaction, reveal | instant in, ease out |
   | Sustained reading | eased in+out |
   | Quick flash (<2s) | instant in, instant out |
   | Personal reflection | eased in+out |

4. **Set duration with overhang.** Extend past clip boundaries to bridge jump cuts.

5. **Use matched pairs** for repeated action types.

### Step 5: Write zoom decisions

Write `zoom/zooms.json`:

```json
{
  "zooms": [
    {
      "id": "Z001",
      "tier": "webcam",
      "timeline_start": 0.0,
      "timeline_end": 6.5,
      "scale": 0.72,
      "anchor": "0.5 0.80",
      "anim_in": "default",
      "anim_out": "default",
      "reason": "Opening — personal introduction."
    }
  ]
}
```

`timeline_start`/`timeline_end` are positions in the edited timeline, not source timestamps.

### Step 6: Generate FCPXML

```bash
python3 ~/.agents/services/zooms.py \
  --source "<source>" \
  --edits <edit_list> \
  --zooms zoom/zooms.json \
  --name "<timeline name> - Zoomed" \
  --titles \
  --output zoom/timeline_zoomed.fcpxml
```

The `--titles` flag generates DesignStudio title clips (resizable in FCP). Omit for keyframed adjustment clips (no dependencies).

### Step 7: Report

- Number of zooms by tier
- Density per minute
- Path to FCPXML output
- Remind user to open in Final Cut Pro

## FCPXML Generation Notes

- **FCPXML 1.14** — requires `<media-rep>` inside `<asset>`
- **`library > event > project > sequence > spine`** — full hierarchy required
- **`<asset-clip>`** in spine
- **Adjustment clips** on lane 1
- **`start="3600s"`** — FCP convention
- **`colorSpace="1-1-1 (Rec. 709)"`** — required on format element

Reference: `~/.agents/services/references/fcpxml/README.md`

## Notes

- This stage produces FCPXML only — no OTIO equivalent for adjustment clips
- Zoom decisions are subjective — the user will adjust in FCP
- Frame extraction uses the preview video, not the source
- The zoom stage does not modify the edit list or re-render preview — it only adds a visual layer
- Calibration data (scale values, density, position clusters) belongs in `evals/`
