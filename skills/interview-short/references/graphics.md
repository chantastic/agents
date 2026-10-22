# Graphics: hand-drawn cutaways and stickers in After Effects

## Contents
1. Style · 2. Layout · 3. Cutaway or sticker · 4. Timing rules · 5. lib.jsx API · 6. Scene ideas · 7. AE scripting traps

## 1. Style: ink on paper

- Paper `#F4EFE4` with 5 % mono noise; ink `#1B1B1F`; accents yellow `#FFD400`, red `#E5484D`, green `#30A46C`,
  blue `#6E7BFF`, navy `#161A2B` (also the "lights off" multiply overlay), purple/pink for "AI slop" gradients.
- Fonts (PostScript names): `Caveat-Bold` (handwritten labels), `CoveredByYourGrace` (big marker titles),
  `Bangers-Regular` (stamps, numbers, ½, ×), `IBMPlexMono-Bold`/`-Medium` (code, counters, PR cards),
  `Inter-Bold` (UI buttons), `AvenirNext-Heavy` (captions). Caveat has × but no → or ✓; draw checks/arrows.
- Lines 7–13 px with round caps; lines draw on with trim paths; objects pop in (scale 0/60/85 → 112 → 100 in
  0.2 s). Every scene gets the "boil" (Turbulent Displace re-seeded 8×/s) so lines wobble like hand drawing;
  stamps also get Roughen Edges. Keep the boil subtle: the default amount is 1.5 (it was 3.5, which made shapes
  look rough).
- Illustrate the idea, not the words. The caption already says the words.
- **Grown-up, not juvenile.** Michael called stick figures, cartoon cars, hearts and big red "?" marks juvenile.
  Use product and diagram language instead: dashboard tiles with sparklines, settings screens with toggles, a
  pipeline with stages and gates, a chart with an annotated gap. Hand-drawn line quality, adult subject matter.
- **One outline per object.** Draw a building (factory, house, office) as a single continuous outline with the
  chimney, roof and walls in one path, never a separate box pasted on top. On the PR-throughput short the chimney
  was its own rectangle and read as a block floating above the roof.
- **Smooth organic lines.** Hand-drawn circles, blobs, contours and any curved line go through `curve(pts)` (or
  `wobble()`/`arc()`, which already return curves). Straight polylines with many points look rough and faceted;
  Michael called the old wobble circles rough.

## 2. Layout (1080×1920)

| Zone | y | Use |
|---|---|---|
| Top platform UI | 0–250 | keep empty |
| Scene title | ~300–440 | Caveat 96–110 or marker 92–104, one line, optional yellow marker underline |
| Illustration | ~480–1200 | the drawing; keep labels above 1220 |
| Captions | ~1270–1400 | never cover (two-line captions start ~1270) |
| Bottom platform UI | 1520–1920 | keep empty |

Stickers over a talking head go in a corner of the wall area (≈ x 250–300, y 420–480) and may overlap hair, not
the face.

## 3. Cutaway or sticker

- **Cutaway** (paper precomp, full frame, audio continues): when the line has a concrete picture (a factory going
  dark, PRs jamming a funnel, a checklist that skips tests). Hard cut in and out on clip boundaries where possible.
- **Sticker** (transparent precomp over the camera): punctuation for a punchy word: a MEME stamp, an "Astra-level"
  tag. 0.8–1.2 s.
- Show the speaker at the start of each answer and for reactions ("Not in a good way", "That's awesome"). In the
  example ~70 % of the runtime was graphics; a 13 s run of back-to-back cutaways was broken up with a 1.7 s shot
  of the guest. Don't leave a 1–6 frame sliver of camera between two cutaways; make them contiguous instead.

## 4. Timing rules

- Scene and SFX times are written on the **graphics timeline** `OLD_T` (initially identical to the plate's clip
  starts). `scene(name, t0, t1)` and `s.T(t)` remap and snap to frames for you. Use `OLD_T[i]` (exact clip start)
  for scene boundaries at cuts, never a typed number.
- Key elements to words from `timeline.json` → `words` (output times). DTW times are a touch late, so land things
  ~0.05–0.1 s before the word.
- Anything a scene shows in its first 0.15 s is landed on frame 0 by `pop`/`popText`/`addTrim` (starting at 85 %
  or part-drawn). Otherwise the first frames after the cut are blank paper, which reads as a flash.
- **Never put two keyframes less than a frame apart.** Frame snapping merges them and the later value wins from
  the start (the FIRED stamp sat at 260 % for the whole scene). For a "hidden, then slam in" use a held key one
  frame before the hit, as the example's FIRED stamp does.
- Pops that should land on a word: `pop(L, x, y, T(wordTime - 0.05))`. A stamp "lands" at its smallest scale
  (hit + 0.1 s); cue its SFX there.

## 5. lib.jsx API (all coordinates absolute comp pixels)

| Function | Does |
|---|---|
| `scene(name, t0, t1, paper)` → `s` | new 1080×1920 precomp (paper bg unless `paper === false`); `s.comp`, `s.t0`, `s.t1`, `s.T(t)` |
| `place(s, {boil})` | adds boil, places precomp in MAIN at `s.t0`, logs it for handoffs.py; returns the layer |
| `ink(c, name, [pts…], col, w, t0, t1, closed)` | stroked path(s), drawn on t0→t1 (`null` = no draw-on) |
| `box(c, name, x, y, w, h, r, fill, stroke, sw)` / `ell(...)` / `blob(c, name, pts, fill, stroke, sw)` | filled/outlined shapes |
| `arc(cx, cy, r, a0, a1, n)`, `star(cx, cy, r)`, `wobble(cx, cy, R, seed, n, sy)` | point generators (gauges, sparkles, hand-drawn circles/contours; `sy` squashes). `arc` and `wobble` return smooth curves |
| `curve([pts…])` | marks a point list smooth: `ink`/`blob` then draw a Catmull-Rom Bezier through the points instead of straight segments |
| `arrow(c, name, x0, y0, x1, y1, col, w, t0, t1)`, `check(c, name, x, y, s, col, t0)`, `cross(c, name, x, y, s, col, w, t0)` | drawn-on marks |
| `txt(c, s, font, size, col, x, y, {left, box, stroke, sw, rot, tracking})` | text centred on (x, y) (or baseline-left with `left`) |
| `pop(L, x, y, t, from)`, `popText(L, t, from)` | pop-in around (x, y) / the text's centre |
| `keys(prop, [[t, v], …], hold)`, `between(L, a, b)`, `center(L, x, y)`, `xf(L, matchName)` | keyframes, in/out points, anchors, transform props |
| `dim(c, t0, t1, amount)` | navy multiply overlay ("lights off") |

Patterns: group pieces under `c.layers.addNull()` (set parent after positioning) to move/rotate/scale them as
one (the pink slip, PR cards); expressions for counters (`sourceText`), typing, `wiggle()`, falling coins
(position expression with a modulo). Keep `var SCENES = [ … ]` at the end of scenes.jsx.

## 6. Scene ideas that worked (all in the example's scenes.jsx)

Hook title card + illustration that changes state (factory windows go dark) · a physical switch + room going
dark · rubber stamp sticker · a deliberately sloppy UI then a big red X · a runaway counter + money on fire + a
pink slip + FIRED stamp · a gauge needle swinging · items piling into a funnel ("bottleneck") · a big title card
for a named concept · a checklist where a scanner passes/skips rows and the time drops · a mystery box + a
jittering easy/hard meter · one prompt branching into two worlds with ✓/✗ outcomes · a contour map revealed as an
agent dot explores · a tag sticker · before/after bars (½ cost, 2× speed).

## 7. After Effects scripting traps

- ExtendScript is ES3: `var`, no arrow functions/let/const. Non-ASCII must be `½`-style escapes.
- Effects by matchName, not index or display name: Turbulent Displace Amount `ADBE Turbulent Displace-0002`,
  Size `-0003`, Evolution `-0006`; Noise amount `ADBE Noise-0001`, colour noise `ADBE Noise-0002`.
- Shape contents order matters: path(s), then trim, then stroke, then fill (renderers draw paths above them).
- Set each property right after `addProperty`; earlier references to siblings can go invalid.
- `build.jsx` calls `app.newProject()`: a rebuild replaces the open project, and hand edits Michael made in AE are
  lost unless they're also in the scripts. Ask before rebuilding over his edits.
- `build.log` is written with CR line endings: read it with `tr '\r' '\n'`. `DoScript` returns nothing useful.
- Replacing a footage file in place makes AE render it black from its cache: `cut.py` writes a new `plate-N.mp4`.
