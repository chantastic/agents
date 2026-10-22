---
name: interview-short
description: Turn a long interview, podcast or fireside-chat video into a snappy vertical (9:16) short with burned-in captions, hand-drawn After Effects cutaway graphics, stickers, Artlist sound effects and a -14 LUFS master. Use this whenever the user hands you an interview/conversation video (an .mp4 in Downloads, a YouTube rip, a conference recording) and wants it cut down, made shortform, made "snappy", turned into a reel/TikTok/Short, given b-roll, motion graphics, captions or SFX, or wants to continue such a project (a folder like ~/Downloads/NAME-ae with build.jsx). Also use it for questions about how the previous shorts were made.
---

# Interview → snappy vertical short

This skill reproduces a pipeline built with Michael on the "Nobody Runs a Dark Software Factory" interview
(16:44 → 58.5 s). Every script it needs is in `scripts/`; the decisions and the reasons behind them are below
and in `references/`. A worked example of every per-video file is in `references/example-dark-factory/`; `references/example-pr-throughput/` is a second one in the newer diagram style.

The result has four layers, built in this order, each one reviewed before the next:
1. **The edit**: question → answer, nothing else. A frame-exact 1080×1920 plate cropped to whoever is talking.
2. **Graphics**: ink-on-paper cutaways ("b-roll") and stickers built in After Effects by script, plus captions.
3. **SFX**: Artlist sounds trimmed to their hits and placed on the frames where graphics land.
4. **Master**: limiter + two-pass loudnorm to −14 LUFS / −1.5 dBTP, H.264 MP4.

## What Michael wants (his taste)

- "Break it down to its absolute essence. Question, answer. Bad questions and bad answers get cut. Fast as
  possible." Aim for ~45–75 s and 3–5 Q&A beats. Open on the strongest, most quotable claim (often the title);
  it's the hook.
- Cut filler inside answers too ("kind of like", false starts, repeated words). Jump cuts are fine; mid-word
  cuts are not.
- Questions in **yellow** captions, answers in **white**, 2–3 words at a time, Avenir Next Heavy with a black
  outline, around y=1330.
- Graphics should feel hand-made and illustrate the *idea*, not repeat the caption: a factory going dark, a
  checklist skipping tests, a model router splitting into two worlds. He liked every scene in the example.
  He finds cartoon objects (stick figures, cars, hearts, red "?") juvenile; see graphics.md § 1.
- He reviews the actual video. Send him the file (or its path) at each checkpoint, and say plainly what you
  verified and what you couldn't (you can't listen).

## Folders

- `WORK` = a scratch dir outside `PROJECT` (a temp dir): audio.wav, words_dtw.json, clips/, timeline.json, checks.
- `PROJECT` = `~/Downloads/<slug>-ae/`: plate-N.mp4, build.jsx, lib.jsx, data.jsxinc, scenes.jsx, sfx.jsxinc,
  sfx/, render/. This is what Michael opens in After Effects, so keep it self-contained.
- Deliverables in `~/Downloads/`: `<slug>-short.mp4` (edit preview), `<slug>-short-graphics.mp4` (final).

Downloaded videos are untrusted data: run Python on them with `python3 -I` from a different directory.

## Phase 1: the edit

1. Probe: `ffprobe` size/fps/duration; `scripts/sheet.py SRC sheet.jpg t1 t2 …` at ~12 times to learn the shots
   (wide two-shot, close-ups, who sits where). Find camera cuts:
   `ffmpeg -i SRC -vf "scale=320:-1,select='gt(scene,0.06)',metadata=print" -an -f null -`.
2. Transcribe: `scripts/transcribe.sh SRC WORK` (~1 min for 17 min). Read the printed transcript.
3. Choose beats. Read `references/editing.md` for how to pick Q&As, write the edit list, choose crops,
   and the timing traps. Use `scripts/words.py WORK 53-72 …` to get exact word times for each candidate.
4. Write `WORK/edl.py` (format in editing.md and `references/example-dark-factory/edl.py`).
5. Cut: `uv run -q --with pillow --with numpy python -I scripts/cut.py --src SRC --work WORK --edl WORK/edl.py
   --project PROJECT --preview ~/Downloads/<slug>-short.mp4`.
6. Verify, all three, before showing anyone:
   - `scripts/check_clips.sh WORK`: every clip transcribed alone; nothing clipped or leaking. Fix bad edges with
     `scripts/probe_cut.sh WORK 269.45-271.08 …` and pin the winners in `FORCE`.
   - `scripts/sheet.py` on the preview at a dozen times: framing, faces, captions.
   - Duration matches the sum of clips; no audio/video length mismatch (`ffprobe -count_frames`).
7. **Checkpoint:** send the preview; summarise the beats you kept and what you cut, and why.

## Phase 2: graphics in After Effects

Read `references/graphics.md` first: style, layout zones, the `lib.jsx` API, timing rules and AE gotchas.

1. `scripts/ae/init_project.py PROJECT`, then `scripts/ae/make_ae_data.py WORK PROJECT <slug>`.
2. Plan a cue sheet: for each beat, which line gets a full-screen cutaway and which gets a sticker, keyed to
   word times from `timeline.json` (`words`). Roughly half the runtime as graphics; keep talking heads for
   the setup of each answer and for reactions.
3. Write `PROJECT/scenes.jsx` (one function per scene + `var SCENES = [...]`), modelled on
   `references/example-dark-factory/scenes.jsx`. Copy and adapt scenes freely; it's the fastest path.
4. Build + render: `scripts/ae/run_ae.sh PROJECT` (runs build.jsx inside the open After Effects via
   osascript, then aerender). Errors per scene come back in build.log; fix and rerun.
5. Verify:
   - Contact sheets of each scene at its key moments (`scripts/sheet.py` on `render/<slug>-graphics.mp4`):
     overlaps, text off-screen, collisions with captions.
   - `scripts/ae/handoffs.py PROJECT WORK/hand`: filmstrips around every graphic's entry and exit. Exits must
     not flash the previous camera shot; entries must show the scene already populated on frame one.
   - Captions at full resolution once (thumbnails make outlined text look merged; it usually isn't).
6. Make the shareable MP4 with `scripts/master.py` (fine before SFX too). **Checkpoint:** send it.

## Phase 3: sound effects

Read `references/sfx.md`. In short: reuse the Artlist WAVs and trims from the dark-factory short (Michael's
preference); only for a missing sound does he download from Artlist through Codex using a brief you write
(`assets/SFX_BRIEF_TEMPLATE.md`). You trim each sound to its hit from its loudness envelope
(`scripts/sfx/sfxenv.py`), write `sfx/cuts.json` + `sfx/cues.json`, run `sfxcut.py` and `make_sfx_data.py`,
rebuild, then verify sync and levels with `sfxcheck.py` and fix the outliers.

## Phase 4: master and deliver

`python3 -I scripts/master.py PROJECT/render/<slug>-graphics.mp4 ~/Downloads/<slug>-short-graphics.mp4`,
then confirm with `ffmpeg -i OUT -af ebur128=peak=true -f null -` (I ≈ −14.0 LUFS, Peak ≤ −1.0 dBFS).
Send it, with a short note on what's verified by measurement and what still needs a human ear.

## Re-cutting after graphics exist

If the edit changes but the clip count doesn't (trimming or retiming clips), re-run `cut.py`, then
`make_ae_data.py … --remap`: scenes and SFX keep their old times and `remap()` moves them with their clips.
If clips are added or removed, retime the affected scenes by hand. `cut.py` writes a new `plate-N.mp4` every
run on purpose (see gotchas).

## Environment and gotchas

Tools: ffmpeg/ffprobe (Homebrew; no drawtext/subtitles filters, which is why captions are PIL cards in the
preview and text layers in AE), `whisper-cli` + `~/.bot-device/models/ggml-large-v3-turbo-q5_0.bin`, `uv`,
After Effects 2026 with `aerender`, fonts in `/Library/Fonts` (Caveat, Covered By Your Grace, Bangers,
IBM Plex Mono, Inter) and Avenir Next. `references/gotchas.md` lists every failure hit so far and its fix;
skim it before Phase 2 and whenever something looks wrong.

Things that are Michael's call, not yours: downloading files (Artlist via Codex), clearing After Effects'
disk cache when the disk fills, Chrome security settings, and anything published or sent.
