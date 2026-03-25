# Zoom Analysis: Pi First Look

**Date**: 2026-03-25
**Source**: `2026-03-23 11-57-49.mp4`
**Agent zooms**: 27 (1.6/min)
**Chan's zooms**: 56 (4.0/min)

This analysis was conducted by reviewing Chan's final FCPXML export, extracting frames at each zoom point, and reading the DesignStudio title parameters to understand the editorial intent. 16 of 56 zooms were examined frame-by-frame.

---

## Tier System (derived from 56 zooms)

| Tier | Scale | Count | Animation | Purpose |
|---|---|---|---|---|
| Webcam | 0.65–0.80 | 6 | eased in+out | Personal moments, opening/closing, reflective beats |
| Guide | 1.20–1.35 | 35 | instant in, variable out | Terminal reading, exploration, working |
| Emphasis | 1.4–1.5 | 12 | instant in, ease/instant out | Key reveals, reactions, first encounters |
| Extreme | 1.9–4.0 | 3 | instant hold | Small fleeting targets with editorial weight |

### Scale clusters (exact values)

| Scale | Count | Typical use |
|---|---|---|
| 0.65-0.78 | 6 | Webcam/camera |
| 0.94 | 1 | Gentle webcam (tree navigation section) |
| 1.03 | 3 | Subtle shift (status bar, lower content) |
| 1.20 | 3 | Gentle guide (documentation reading) |
| 1.23 | 4 | Guide (questionnaire/extension section) |
| 1.25 | 12 | Core guide (features, first interactions) |
| 1.30 | 4 | Guide (Claude output section) |
| 1.32 | 8 | Guide (model config, tree, sharing sections) |
| 1.35 | 4 | Guide (skills cross-agent section) |
| 1.36 | 1 | Guide/emphasis border |
| 1.40 | 4 | Emphasis (first interactions) |
| 1.42 | 2 | Emphasis (terminal scanning) |
| 1.45 | 2 | Emphasis (sharing, extension) |
| 1.50 | 3 | Strong emphasis (Claude reaction, Anthropic take, cross-agent answer) |
| 1.89 | 1 | Extreme (auto discovery folder) |
| 4.00 | 1 | Extreme (Dock bounce after download) |

**Observation**: Scale increases in ~0.05 increments across sections. Each topical section gets its own consistent scale. The scale drifts upward as the video progresses and the content gets more interesting (1.25 for features → 1.30 for Claude → 1.32 for config → 1.35 for skills).

## Animation Patterns

| Pattern | Count | Editorial meaning |
|---|---|---|
| instant in, instant out | 28 | "Look here, stay here." Sustained attention. |
| instant in, ease out | 14 | "Snap to this, gently release." Most emphasis moments. |
| eased in+out | 13 | "Breathe with this moment." Webcam, sustained reads. |
| ease in, instant out | 1 | Rare. Used once for camera → screen hard transition. |

**Rule**: Animation follows the moment's energy, not the content type. Same content can get instant or eased depending on how the speaker is engaging with it.

## Overhang Analysis

33 of 56 zooms (59%) extend past their parent clip into adjacent clips. Overhang is the primary technique for visual continuity across jump cuts.

**Overhang duration distribution:**
- 1-3s: 14 zooms (bridging one cut)
- 3-7s: 12 zooms (bridging 2-3 cuts)
- 7-14s: 7 zooms (spanning a full phrase across many cuts)

## Frame-by-Frame Analysis

### Opening sequence (Clips 001-012)

**Clip_001** (29.1s) — The only Constant Zoom GG18 in the video. Slow push toward Pi tagline. Strength 0.54, endpoint at center-above-middle (0.5, 0.44). Everything else uses Zoom In 0ZZM.

**Clips 007/009/012** — Webcam tier decreasing in intensity: 0.65 → 0.71 → 0.78. Eases the viewer from "who is this person" into the screen layout. Clip_012 anchors to the PiP corner to bridge from full camera to split-screen.

### First interaction (Clips 014-034)

**Clips 014/016** — Matched pair at scale 1.42. Same animation, same template. Y-position flips from bottom (0.93, cursor area) to top (0.01, warning message). Zoom follows the speaker's attention vertically through the terminal.

**Clips 021/027** — Identical parameters (1.4, position 0.004/0.361). Both are "hello, you there?" moments. Visual callback for repeated action.

**Clip_030** — Scale drops to 1.25. The shift from emphasis (1.4) to guide (1.25) marks the transition from excitement to working.

**Clip_034** — Same 1.25 scale, but animation changes from instant to eased, and duration extends to 11.2s. The zoom decelerates as the speaker settles into reading Pi's output.

### Mid-video webcam punctuation (Clip_038)

Scale 0.72, full camera, eased in+out. "I want some coordinator to be the glue." Partial coverage (50% of clip) — the zoom covers the personal statement but releases for the transition back to screen content.

### Guide section (Clips 041-060)

Sustained guide tier at 1.25. Scroll-follow pairs: Clips 041 and 045 share scale but y-position shifts from 0.19 → 0.27 as the terminal content scrolls down.

### Key reveals (Clips 086, 225)

Both scale 1.5, both instant in/instant out, both ~1.5s duration. Clip_086 targets webcam PiP (reaction to Claude's praise). Clip_225 targets terminal (cross-agent answer). Same treatment regardless of what's on screen — the tier is about importance, the anchor is about content.

### Extreme tier (Clips 267, 271)

**Clip_267** (1.89x) — "auto discovery folder." A specific terminal path being discussed.

**Clip_271** (4.0x) — Dock bounce after downloading questionnaire.ts. Position (0.54, 0.002) targets the Dock at the screen bottom. 0.9s duration matches the bounce animation. Functional (makes the Dock bounce visible) and expressive (comedy punctuation after minutes of extension struggle).

### Closing (Clip_305)

Scale 0.76, full camera, eased in+out. Bookends with the opening webcam shots. Overhang carries through the sign-off.

## Webcam Anchor Constraint

Webcam zooms must anchor y high enough to preserve head room. The speaker's framing puts the top of the head near the frame edge. At zoom scales of 0.65-0.80, anchoring too low crops below mid-forehead, which looks wrong. Observed y values: 0.74-0.92. This is a physical constraint of the camera framing, not an editorial choice — but it becomes a rule.

## Key Learnings for Skill

1. **Frequency was 2x too low** (1.6/min vs 4.0/min target). More frequent, gentler zooms beat sparse, aggressive ones.

2. **Scale consistency within sections** is the most important pattern. Don't make every zoom unique — make sections visually coherent, then vary between sections.

3. **Overhang is the primary continuity technique.** 59% of zooms span multiple clips. The skill should think in phrases, not clips.

4. **Animation follows energy, not content type.** Instant in for high-energy moments, eased for sustained reading. The same content can get either treatment.

5. **The emphasis tier returns for key reveals throughout.** It's not front-loaded. Any moment with high editorial importance gets 1.4-1.5 regardless of position in the video.

6. **Extreme zooms serve visibility and expression simultaneously.** Scale is proportional to how small the target is. The editorial weight comes from the decision to zoom at all, not just the scale.

7. **Matched pairs and scroll-follow pairs** create visual rhythm. Repeated actions get identical parameters. Scrolling content gets same-scale, shifted-anchor.

## What Changed in the Skill

- Replaced the 3×3 anchor grid with continuous position based on frame analysis
- Added tier system (webcam/guide/emphasis/extreme) with scale ranges
- Added animation rules (instant/eased based on energy, not content)
- Added overhang as a first-class concept
- Added section-based zoom planning (segment → assign tier → select points)
- Increased target density from ~2/min to 3-4/min
- Added editorial patterns section (bookending, scroll-follow, matched pairs, energy deceleration)
- Added webcam head-room constraint
- Added principle: "the best zooms are functional and expressive at the same time"
