# Worked example: "Your PR Throughput Is Up 3x. Is Your ARR?"

Pavan Kumar Patibandla (Amplitude) with Greg Sabo (WorkOS), ELC 2026. 12:54 source → 61.8 s, 22 clips,
11 graphics scenes, 67 SFX cues. This is the second short, made after Michael's feedback on the first draft; read it
alongside `../example-dark-factory/`.

- `scenes.jsx`: all 11 scenes, in the v2 "product/diagram" style: a factory drawn as one outline with PR cards
  rolling off the line, dashboard tiles with sparklines, a PRs-vs-ARR chart with the gap annotated, a slow
  pipeline with stages and gates. Smooth lines use `curve()`. Its hard-coded times are on this video's original
  timeline, `old_t.json` (build with `make_ae_data.py WORK PROJECT NAME --old-t old_t.json`).
- `sfx_cues.json`: the 67 cues. There are no new sounds: the project reused 19 of the dark-factory Artlist WAVs
  and their trims (`../example-dark-factory/sfx_cuts.json` without `coins` and `fire`), as described in
  `references/sfx.md`.

What changed after Michael's review of the first draft: he called the circles rough and some scenes juvenile
(stick figures, cartoon cars, hearts, big red "?"), and the factory's chimney was a separate box floating above
the roof. The fixes were smooth Bezier curves in `lib.jsx` (`curve()`, gentler `wobble()`, boil 3.5 → 1.5),
diagram-style scenes, and a one-outline factory. The master used `limit=0.6` and measured −14.0 LUFS / −1.5 dBFS.

The original project (with renders) is in `~/Downloads/pr-throughput-ae/`.
