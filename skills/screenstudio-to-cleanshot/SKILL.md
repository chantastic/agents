---
name: screenstudio-to-cleanshot
description: Convert a Screen Studio project (.screenstudio) into an editable CleanShot X project (.cleanshotvideo) with the recorded cursor, clicks, cuts and zooms, so it can be edited and exported in CleanShot instead of Screen Studio. Use when Michael has a .screenstudio file but no Screen Studio license, or asks to open, export or convert a Screen Studio recording in CleanShot.
role: transformation
---

# Screen Studio → CleanShot X

Input: a `.screenstudio` package. Output: a `.cleanshotvideo` package next to it, opened in CleanShot X.

## Steps

1. Convert:
   ```sh
   python3 ~/.agents/skills/screenstudio-to-cleanshot/ss2cleanshot.py "X.screenstudio" ["OUT.cleanshotvideo"]
   ```
   If no output path is given, the output goes next to the source, with `:` in the name replaced by `.`. Requires `ffmpeg`.
2. Run `open -a "CleanShot X" OUT.cleanshotvideo`. Scrub to a click and check that the drawn cursor sits on the clicked control and that the zooms follow it.

## What carries over

- The screen video, remuxed without re-encoding from Screen Studio's HLS segments into `files/video.mov`.
- Mouse moves, drags and left clicks, with cursor shapes mapped to CleanShot's enum. Custom cursors become 255 ("other").
- Cuts, from Screen Studio's `slices` to CleanShot's `clips`.
- Zooms, set to follow the cursor (mode 0) at the same zoom level.
- Style settings (cursor size and style, motion blur, padding) come from `template/document.json`. To change them, use `--template` with any CleanShot project that's set up the way you want.

These don't carry over: camera, audio (none has come up yet), keystroke overlays, Screen Studio backgrounds, and speed changes.

## Format notes

- Screen Studio stores mouse x/y in global screen points. The converter subtracts `recording/metadata.json` → display `sessions[0].bounds` and multiplies by `1/recordingScale` to get video pixels. Event time is `processTimeMs - processTimeStartMs`.
- CleanShot's `mouse_events.bin` y-axis starts at the **bottom** of the frame. Forgetting this puts the cursor and zooms in the wrong place. The full binary layout is in the script's docstring.
- The format was reverse-engineered from CleanShot X 5.0.2 (`documentFormatVersion` 1). If a newer CleanShot rejects the output, have Michael record a 3-second CleanShot project with some clicks, then diff it against the template.
