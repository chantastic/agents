---
name: video-zoom
description: Add zoom and punch-in effects to a video edit via FCPXML adjustment clips. Analyzes transcript and frames to identify zoom opportunities, determines focal points, and generates FCPXML with adjustment clips on lane 1. Use after video-polish to add visual emphasis.
---

# Video Zoom

Add zoom/punch-in effects to a polished video edit using FCPXML adjustment clips.

## Required Environment

- `ffmpeg` and `ffprobe` — installed

## Inputs

Read from `manifest.json` in the project directory:
- `source` — original video path
- `thesis` — video goal (guides zoom selection)
- `stages.polish.edit_list` — polished edit list
- `stages.polish.preview` — polished preview video

If no manifest exists, ask the user for the source video path, edit list, and preview.

## Outputs

All outputs go to `zoom/` within the project directory:

| File | Description |
|---|---|
| `zoom/frames/Z001.jpg` ... | Extracted frames at each zoom point |
| `zoom/zooms.json` | Zoom decisions with timing, scale, and anchor |
| `zoom/timeline_zoomed.fcpxml` | FCPXML with adjustment clips (FCP-only, no OTIO) |

After completion, update `manifest.json` with stage status and file paths.

## Process

### Step 1: Read the polished preview transcript

Read the polished preview utterances. These are the viewer's experience — a continuous flow where zoom-worthy moments become obvious.

### Step 2: Identify zoom opportunities

Read every utterance and select moments that benefit from visual emphasis.

**Zoom styles:**

| Style | Behavior | Use when |
|---|---|---|
| `punch` | Instant scale change, holds, instant return | Short emphasis: reactions, reveals, key statements |
| `smooth` | Eases from 1.0 → scale (ramp in), holds, eases back to 1.0 (ramp out) | Longer moments: thesis statements, important explanations |
| `push` | Continuous slow zoom from 1.0 → scale over full duration, no return | Building intensity: opening sequences, tension, anticipation |

`punch` is the default. `smooth` adds `ramp_in` (default 0.5s) and `ramp_out` (default 0.3s) fields. `push` zooms continuously for the clip's duration with eased interpolation.

**Zoom-worthy signals:**

| Signal | Scale range | Style | Example |
|---|---|---|---|
| Key statement / thesis | 1.40–1.50 | smooth | "Pi follows a philosophy of aggressive extensibility" |
| Reveal / payoff | 1.50–1.65 | punch | "And it works!" "YOLO. This is a big one." |
| Quick reaction | 1.60–1.75 | punch | "Sick." / "RTFM, bro." |
| Satisfaction / assessment | 1.35–1.50 | smooth | "Pretty painless so far" |
| Opening / closing | 1.40–1.50 | push | Thesis statement, sign-off |
| Emotional emphasis | 1.50–1.65 | punch | "We can even run Doom." |

**Anti-patterns (don't zoom):**
- Already zoomed recently (minimum ~15s gap)
- Speaker is reading screen content (screen is the focus, not the speaker)
- Mid-sentence — zooms start on utterance boundaries
- Too many in a row — max ~4 per minute, creates visual fatigue
- Very short clips (<0.5s) — zoom won't register

### Step 3: Extract frames

For each zoom candidate, extract a frame from the preview video at the zoom's timeline start:

```bash
ffmpeg -y -ss <timeline_seconds> -i <preview.mp4> -frames:v 1 -q:v 2 zoom/frames/<id>.jpg
```

### Step 4: Analyze frames for anchor selection

Read each extracted frame. Determine the focal point using the 3×3 anchor grid:

```
top-left      top-center      top-right
middle-left   middle-center   middle-right
bottom-left   bottom-center   bottom-right
```

**Decision guide:**

| Frame content | Anchor |
|---|---|
| Terminal on left, text is the focus | `middle-left` |
| Terminal on left, text in lower area | `bottom-left` |
| Terminal on left, text in upper area | `top-left` |
| Browser/docs on right | `middle-right` |
| Browser on right, upper content | `top-right` |
| Full-screen UI, centered content | `middle-center` |
| Full-screen camera (talking head) | `middle-center` |
| Camera with face in upper portion | `top-center` |
| Split screen, emphasize left panel | `middle-left` |
| Split screen, emphasize right panel | `middle-right` |

### Step 5: Write zoom decisions

Write `zoom/zooms.json`:

```json
{
  "zooms": [
    {
      "id": "Z001",
      "style": "push",
      "timeline_start": 0.0,
      "timeline_end": 6.5,
      "scale": 1.50,
      "anchor": "middle-left",
      "reason": "Opening thesis. Slow push into terminal showing Pi description."
    },
    {
      "id": "Z002",
      "style": "smooth",
      "timeline_start": 19.4,
      "timeline_end": 27.9,
      "scale": 1.50,
      "anchor": "middle-center",
      "ramp_in": 0.5,
      "ramp_out": 0.3,
      "reason": "Personal motivation — smooth in and out for emphasis."
    },
    {
      "id": "Z003",
      "style": "punch",
      "timeline_start": 100.1,
      "timeline_end": 101.0,
      "scale": 1.65,
      "anchor": "middle-left",
      "reason": "Quick reaction: 'RTFM, bro.' Hard cut for impact."
    }
  ]
}
```

**Fields:**
- `id` — unique identifier (Z001, Z002, ...)
- `style` — `"punch"` (default), `"smooth"`, or `"push"`
- `timeline_start` / `timeline_end` — position in the POLISHED timeline (seconds)
- `scale` — zoom factor (1.0 = no zoom, 1.50 = 50% punch-in)
- `anchor` — named preset or raw FCP units "x y"
- `ramp_in` — (smooth only) seconds to ease in, default 0.5
- `ramp_out` — (smooth only) seconds to ease out, default 0.3
- `reason` — why this moment deserves a zoom

**Important:** `timeline_start`/`timeline_end` are positions in the edited timeline, not source timestamps. Use the preview utterance timestamps.

### Step 6: Generate FCPXML

```bash
python3 ~/.agents/services/zooms.py \
  --source "<source_video>" \
  --edits <edit_list.json> \
  --zooms zoom/zooms.json \
  --name "<timeline name> - Zoomed" \
  --titles \
  --output zoom/timeline_zoomed.fcpxml
```

The `--titles` flag generates zooms as **DesignStudio title clips** instead of adjustment clips. Title-based zooms are resizable in FCP's timeline — drag the edge and the animation auto-scales. Requires MotionVFX DesignStudio templates installed (Constant Zoom GG18, Zoom In 0ZZM). Falls back to keyframed adjustment clips if templates are not found.

Omit `--titles` to always use adjustment clips (no dependencies).

### Step 7: Update manifest and report

Update `manifest.json`:

```json
{
  "stages": {
    "zoom": {
      "status": "complete",
      "zooms": "zoom/zooms.json",
      "timeline": "zoom/timeline_zoomed.fcpxml",
      "stats": {
        "zoom_count": 15,
        "presets_used": {"middle-left": 8, "middle-right": 2, ...}
      }
    }
  }
}
```

Report:
- Number of zooms added
- Distribution of anchor presets used
- Path to FCPXML output
- Remind user to open in Final Cut Pro

## Anchor Preset Reference

FCP coordinate system: frame height = 100 units, origin at center. Values confirmed by FCP round-trip export.

```
top-left:    (-88.89,  50)    top-center:    (0,  50)    top-right:    (88.89,  50)
middle-left: (-88.89,   0)    middle-center: (omit)      middle-right: (88.89,   0)
bottom-left: (-88.89, -50)    bottom-center: (0, -50)    bottom-right: (88.89, -50)
```

Half-width = `(width / height) × 50`. For 16:9 = 88.8889. For other aspect ratios, computed at runtime.

Both `position` and `anchor` are set to the same values. This pins the named point to the frame edge while scaling around it. For `middle-center`, omit both — bare `scale` only.

## FCPXML Generation Notes

The `zooms.py` service generates FCPXML from scratch (not by modifying OTIO output). Key decisions:

- **FCPXML 1.14** — requires `<media-rep>` inside `<asset>` (no `src` attribute on asset)
- **`library > event > project > sequence > spine`** — full hierarchy required
- **`<asset-clip>`** in spine — not the `<clip><video>` wrapper that OTIO generates
- **Adjustment clips** — `<video ref="..." lane="1" role="adjustments">` connected to asset-clips
- **Connected clip offset** — uses parent clip's **source timebase**, not timeline position
- **Overhang** — a single zoom attached to one clip can extend across adjacent clips
- **`start="3600s"`** — FCP convention for generator start time
- **`colorSpace="1-1-1 (Rec. 709)"`** — required on format element

Reference file: `~/.agents/services/references/fcpxml/README.md`

## Notes

- This stage produces FCPXML only — no OTIO equivalent exists for adjustment clips
- The OTIO timeline from the polish stage remains the portable interchange format
- Zoom decisions are subjective — the user will likely adjust timing, scale, and anchors in FCP
- Frame extraction uses the preview video (edited timeline), not the source
- The zoom stage does not modify the edit list or re-render preview — it only adds a visual layer
