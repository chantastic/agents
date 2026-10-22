# Worked example: "Nobody Runs a Dark Software Factory"

Andrew Churchill (Weave) with Michael Grinich (WorkOS), ELC 2026. 16:44 source → 58.5 s, 31 clips, 14 graphics
scenes, 76 SFX cues. Use these files as templates for a new video:

- `edl.py`: the edit list (4 beats: dark factory, token era, CI, model routing), with `FIX` and `FORCE`.
- `scenes.jsx`: all 14 scenes. Its hard-coded times are on this video's original timeline, `old_t.json`
  (build with `make_ae_data.py WORK PROJECT NAME --old-t old_t.json` to reproduce it exactly).
- `sfx_cuts.json`, `sfx_cues.json`, `sfx_manifest.csv`: how the 21 Artlist files were trimmed and cued, and where
  they came from.

The original project (with renders) is in `~/Downloads/dark-factory-ae/`.
