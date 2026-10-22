# Sound effects: sourcing, trimming, cueing, checking

## Reuse the existing library first

Michael asked to reuse the sounds he already has instead of downloading new ones. The 21 Artlist WAVs from the
dark-factory short are in `~/Downloads/dark-factory-ae/sfx/` (with `manifest.csv`), and their trims are in
`references/example-dark-factory/sfx_cuts.json`; both work as they are. For a new project, copy the WAVs it needs
into `PROJECT/sfx/`, copy their rows from `manifest.csv` into `PROJECT/sfx/manifest.csv`, and copy their entries from
`sfx_cuts.json` into `PROJECT/sfx/cuts.json`, then go straight to `sfxcut.py` and cueing. The PR-throughput short did
exactly this with 19 of the 21 (everything except the coins and fire beds; see
`references/example-pr-throughput/`). Only write an Artlist brief for a sound the library doesn't cover, and ask
Michael first.

## Sourcing from Artlist (Michael's subscription)

What worked: **Michael passes a brief to Codex**, which drives his Chrome, downloads WAVs into
`PROJECT/sfx/` with fixed names, and writes `sfx/manifest.csv` (title, creator, link, duration, notes). Copy
`assets/SFX_BRIEF_TEMPLATE.md` into the project, fill in the title and length, and adjust the sound table to the
scenes you built. The default 19 sounds cover the ink-on-paper style well: scribble, power-down, switch,
stamp, pop (×2), slash, coins, fire, paper-slap, whoosh, card-flick, scan, ding (×2), error, typing, box-thud,
rattle, deflate, riser.

What didn't work, so don't burn time on it: agent-driven browsers couldn't sign in to Artlist, and AppleScript can
open Chrome tabs but Chrome refuses AppleScript JavaScript in Michael's **Work** profile even with View → Developer → Allow JavaScript from Apple Events checked (it is on only in the
Personal profile), and Artlist renders results with JavaScript, so saved pages are empty shells. Downloads are
Michael's to approve in any case.

## Trimming without listening

`uv run -q --with numpy python -I scripts/sfx/sfxenv.py PROJECT/sfx/*.wav` prints each file's loudness envelope
and onset times. Read them like a waveform:

- Impacts (stamp, switch, thud, slap, card snaps): start ~0.03 s before the onset, keep 0.12–0.4 s;
  hit offset = onset − start. A file with several snaps gives several cuts (cardA/B/C) for variety.
- Long recordings (scribble, marker strokes, typing, fire): take a clean, busy section; marker strokes show as
  separate bursts, so take one burst per slash.
- Whooshes, risers, deflates: the "hit" is the peak, not the onset; cue the peak on the motion's key moment.
- Beds (coins, fire): take 4–5 s, long fade-out.

Write `PROJECT/sfx/cuts.json` (`{"name": ["file.wav", start, end, hit, fade_out]}`; the example is
`references/example-dark-factory/sfx_cuts.json`) and run `scripts/sfx/sfxcut.py PROJECT`. Cuts are
peak-normalised to −1 dBFS, so a cue's dB level means the same for every sound.

## Cueing

`PROJECT/sfx/cues.json` is a list of `[sound, hit time on the graphics timeline, dB]`, using the same times as the
scene code (a stamp's hit = when it lands at its smallest scale; a pop = its pop time; a switch = when the lever
moves; one slash per X stroke). Then `scripts/sfx/make_sfx_data.py PROJECT` and `scripts/ae/run_ae.sh PROJECT`.
The example has 76 cues for 58 s: `references/example-dark-factory/sfx_cues.json`.

Starting levels (dialogue at 0 dB) that measured well:

| Sound | dB | Sound | dB |
|---|---|---|---|
| stamp | −9 to −10 | switch | −4 |
| slash | −6 | paper slap | −6 to −10 |
| power-down | −8 to −10 | whoosh | −10 |
| card snaps | −12 | ding | −12 |
| soft chime | −18 | error | −12 to −14 |
| pops | −18 to −24 | scribbles | −10 to −12 |
| coins bed | −15 | fire bed | −21 |
| typing | −14 | box thud / rattle | −8 / −10 |
| riser / deflate | −10 to −15 | scan | −12 |

Avoid stacking three or more hits within ~0.2 s; it smears. Fade beds out before the next talking head.

## Checking

`uv run -q --with numpy python -I scripts/sfx/sfxcheck.py PROJECT` aligns the plate to the render (AAC adds
~21 ms), subtracts it, and reports per-cue sync and level. A speech residual below −40 dB means the subtraction
is trustworthy. Targets: 90 % of hits within ±40 ms (about a frame); effects a median ~10 dB under speech
peaks; anything more than a dB or two over speech is too loud; anything 20 dB+ under is probably inaudible
(fine for beds). Adjust `cues.json`, regenerate, rebuild, recheck.

## Master

`python3 -I scripts/master.py RENDER OUT.mp4`: oversampled limiter at ~−4.4 dBFS (`limit=0.6`), then two-pass
loudnorm to −14 LUFS / −1.5 dBTP. Expect I ≈ −14.0 LUFS and a measured peak around −1.5 dBFS after AAC, and the
script to print `loudnorm: linear`. The limiter used to be `limit=0.66` (−3.6 dBFS): a mix needing more than about
2 dB of gain then pushed loudnorm into dynamic mode, and the AAC peaked near −0.9 dBFS. If it ever prints
`dynamic`, lower the limit a little more rather than accepting it.
