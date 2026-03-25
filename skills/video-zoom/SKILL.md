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

## Principles

### The best zooms are functional and expressive at the same time

A zoom should make something visible AND carry editorial weight. If it's only practical (guiding the eye to text), it feels clinical. If it's only expressive (punching in for emphasis on already-visible content), it feels like a gimmick. Both together feels like good editing.

### Scale is proportional to the visibility problem

Each tier up isn't just more emphasis — it solves a harder visibility problem while carrying more editorial weight:
- **Guide tier (1.25-1.35)**: terminal text is readable at full scale, but the zoom says "this part matters"
- **Emphasis tier (1.4-1.5)**: content is visible, but the zoom says "this is important"
- **Extreme tier (1.9-4.0)**: content is NOT visible without the zoom, and it's worth seeing (e.g., a Dock icon bounce, a small UI element)

### Zooms are phrases, not punctuation marks

A zoom should span a *thought*, not a clip. Use overhang to extend a zoom across multiple edit points, creating visual continuity across jump cuts. This makes jump cuts feel intentional — the zoom provides a through-line that tells the viewer "this is still one thought."

### Scale follows section, anchor follows content

Hold the same scale within a topical section. Change only the anchor y-position to follow content as it scrolls or shifts. This creates visual rhythm — the viewer's brain registers "we're in the same topic" because the zoom level is constant. Change scale when the *section* changes, not when the *clip* changes.

### Webcam zooms frame the video

The webcam tier appears at the start (personal introduction), punctuates the middle (reflective moments), and closes the video (sign-off). The tool is the subject; the person is the frame.

## Process

### Step 1: Read the polished preview transcript

Read the polished preview utterances. These are the viewer's experience — a continuous flow where zoom-worthy moments become obvious.

### Step 2: Segment into topical sections

Before selecting individual zoom points, segment the transcript into topical sections. Each section gets a consistent zoom treatment.

For each section, classify the visual content:
- **terminal_focused**: speaker discusses or interacts with visible terminal/screen content
- **camera_moment**: personal statement, reaction, emotional beat (full camera or PiP emphasis)
- **mixed**: alternating between screen and camera within the section

### Step 3: Assign zoom tiers per section

Each section gets a base tier. Individual moments within a section can override up (never down).

**Zoom tiers:**

| Tier | Scale (DesignStudio Content Scale) | Animation | When used |
|---|---|---|---|
| **Webcam** | 0.65–0.80 (into face from PiP or full camera) | eased in+out | Personal/emotional moments, reflections, opening/closing |
| **Guide** | 1.25–1.35 | instant in, ease out (short) or eased in+out (sustained reads) | Working, reading, exploring terminal content |
| **Emphasis** | 1.4–1.5 | instant in, ease out or instant hold | Key reveals, important reactions, first encounters |
| **Extreme** | 1.9–4.0 | instant hold | Small/fleeting UI targets that carry editorial weight. Rare (1–2 per video). |

**Tier selection rules:**
- `terminal_focused` sections → **Guide** tier baseline
- `camera_moment` sections → **Webcam** tier
- Key reveals within any section → override to **Emphasis**
- Tiny, fleeting visual details the viewer would miss → **Extreme**

**Scale note:** DesignStudio Content Scale reads directly as magnification (1.25 = 1.25x zoom in). Values < 1.0 zoom in on camera/PiP content. This is NOT the same as FCP's transform scale.

### Step 4: Select zoom points and anchors

**Target density: 3–4 zooms per minute.** Prefer more frequent, gentler zooms over sparse, aggressive ones.

For each zoom point:

1. **Extract a frame** from the preview at the zoom's start time:
   ```bash
   ffmpeg -y -ss <seconds> -i <preview.mp4> -frames:v 1 -vf "scale=960:-1" -q:v 10 zoom/frames/<id>.jpg
   ```

2. **Analyze the frame** to determine anchor position:

   **Terminal/screen content (guide and emphasis tiers):**
   - Anchor x: position of the relevant panel (left terminal ≈ 0.0, right browser ≈ 0.99)
   - Anchor y: position of the relevant content within the panel (top of output ≈ 0.1-0.2, middle ≈ 0.3-0.5, bottom/status bar ≈ 0.7-0.9)
   - As content scrolls within a section, shift y to follow it. Keep scale constant.

   **Webcam/camera (webcam tier):**
   - Full camera shots: anchor center-x (0.5), y high enough to preserve head room (typically 0.73-0.91)
   - PiP camera: anchor to PiP position (typically top-right ≈ 0.97-0.99 x, 0.83-0.92 y)
   - **Head room rule**: the zoom must not crop below mid-forehead. Anchor y high enough that the top of the head stays near the frame edge at the target scale. A little forehead crop is fine; half-forehead looks wrong.

   **Small UI targets (extreme tier):**
   - Anchor precisely on the target element (button, icon, notification)
   - Scale inversely proportional to target size on screen

3. **Set animation based on the moment's energy:**

   | Energy | Animation | Use |
   |---|---|---|
   | High (reactions, reveals) | instant in, ease out | Snaps to content, gently releases |
   | Sustained (reading, exploring) | eased in+out | Breathes with the moment |
   | Flash (very short emphasis) | instant in, instant out | Quick hit, hard cut |
   | Comedy/shock | instant in, instant out | Hard cut for impact |

4. **Set duration with overhang:**
   - The zoom should span the topical phrase, not stop at clip boundaries
   - Short moments: 1.5-3s
   - Working moments: 5-10s  
   - Sustained reads: 10-20s
   - Overhang into adjacent clips to bridge jump cuts

### Step 5: Write zoom decisions

Write `zoom/zooms.json`:

```json
{
  "zooms": [
    {
      "id": "Z001",
      "style": "push",
      "tier": "webcam",
      "timeline_start": 0.0,
      "timeline_end": 6.5,
      "scale": 0.72,
      "anchor": "0.5 0.80",
      "anim_in": "default",
      "anim_out": "default",
      "reason": "Opening — personal introduction, full camera."
    },
    {
      "id": "Z002",
      "style": "punch",
      "tier": "guide",
      "timeline_start": 100.0,
      "timeline_end": 112.0,
      "scale": 1.25,
      "anchor": "0.004 0.19",
      "anim_in": "0",
      "anim_out": "default",
      "reason": "Reading Pi features. Terminal upper area."
    },
    {
      "id": "Z003",
      "style": "punch",
      "tier": "emphasis",
      "timeline_start": 200.0,
      "timeline_end": 201.5,
      "scale": 1.5,
      "anchor": "0.97 0.92",
      "anim_in": "0",
      "anim_out": "0",
      "reason": "Key reveal — reaction flash to webcam PiP."
    }
  ]
}
```

**Fields:**
- `id` — unique identifier (Z001, Z002, ...)
- `style` — `"push"` (opening only), `"punch"` (most zooms), or `"smooth"` (sustained reads)
- `tier` — `"webcam"`, `"guide"`, `"emphasis"`, or `"extreme"` (documents intent)
- `timeline_start` / `timeline_end` — position in the POLISHED timeline (seconds). The zoom may overhang past `timeline_end` into subsequent clips.
- `scale` — DesignStudio Content Scale. >1.0 zooms into screen content, <1.0 zooms into camera/PiP.
- `anchor` — DesignStudio Content Position as "x y" (0.0-1.0 range, 0,0 = top-left)
- `anim_in` — `"0"` (instant) or `"default"` (eased). Default: `"0"` for guide/emphasis, `"default"` for webcam.
- `anim_out` — `"0"` (instant) or `"default"` (eased). Default: `"default"`.
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
        "zoom_count": 56,
        "tier_distribution": {"webcam": 6, "guide": 35, "emphasis": 12, "extreme": 3},
        "density_per_min": 4.0
      }
    }
  }
}
```

Report:
- Number of zooms by tier
- Density per minute
- Path to FCPXML output
- Remind user to open in Final Cut Pro

## Editorial Patterns

### Video arc via webcam tier

The webcam tier bookends the video and punctuates the middle:
```
OPEN:   Webcam (strongest) → Webcam → Webcam/transition
BODY:   Guide ↔ Emphasis ↔ occasional Webcam punctuation
CLOSE:  Webcam
```

Opening webcam zooms can decrease in intensity across 2-3 clips (e.g., 0.65 → 0.71 → 0.78) to ease the viewer from "who is this person" into "what are they doing."

### Scroll-follow pairs

When the speaker reads through a long response, use consecutive zooms at the same scale with y-position shifting to follow the content as it scrolls. This creates a "reading together" effect.

### Matched pairs for repeated actions

When the speaker performs the same type of action twice (e.g., typing a greeting into the terminal), use identical zoom parameters. The visual callback says "this is the same gesture."

### Energy tiers within a section

Within a single exploration section, the zoom energy can decelerate:
1. **First encounter** (emphasis 1.4, instant, short) — excitement
2. **Working** (guide 1.25, instant, short) — settling in
3. **Sustained reading** (guide 1.25, eased, long) — absorbing content

### Emphasis tier returns for key reveals

The emphasis tier (1.4-1.5) isn't front-loaded — it reappears throughout the video for important moments: first interactions, Claude's analysis, the cross-agent compatibility answer. It can target either the terminal (content reveal) or the webcam PiP (reaction flash).

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
