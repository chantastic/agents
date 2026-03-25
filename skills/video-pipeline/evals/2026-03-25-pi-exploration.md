# Pipeline Eval: Pi Exploration

**Date:** 2026-03-25
**Source:** `~/Downloads/test video-pipeline/2026-03-23 11-57-49.mp4`
**Duration:** 64.2 min → 19.6 min (69.5% removed)
**Mode:** Rough cut (no thesis)
**Stages:** cut → polish → zoom

---

## Results

| Metric | Value |
|---|---|
| Original duration | 64.2 min (3853s) |
| After cut | 19.7 min (1182s) — 69.3% removed |
| After polish | 19.6 min (1177s) — 0.14% more removed |
| Utterances | 463 total → 408 kept, 55 removed |
| Polish issues found | 5 (4 applied) |
| Zooms added | 18 (0.9/min) |

### Cut breakdown

| Category | Count |
|---|---|
| False starts | 40 |
| Duplicates | 8 |
| Fragments | 6 |
| Reactions to mistakes | 1 |
| Other | 3 |

### Polish issues

| Type | Description |
|---|---|
| Mid-utterance stumble | "we should be good to dig and we should be good to go" |
| Mid-utterance stumble | "reviewing, reviewing and navigating code bases" |
| Missed false start | "I've been finding that I do a lot. Um, I've been finding..." (within single utterance) |
| Filler clip | Isolated "Cool." (0.6s) |
| Mid-utterance stumble | "Codex Mac. Codex Max" (not applied — single instance in segment) |

### Zoom stats

- 18 zooms, 107s total (9.1% of video)
- Scale range: 1.10–1.30 (pre-update; should have been 1.50 baseline)
- Anchors: 13× middle-left, 4× middle-center, 1× middle-right
- Largest gap between zooms: 229s (needs attention)

---

## What worked

**Cut stage is the star.** Removed 69% of source material with defensible decisions. The "two decade VIM user" intro alone had 8 false starts. This is exactly the tedious work the LLM handles well.

**Infrastructure is solid.** Manifest-driven resumability, clean service separation (transcribe, edit, render, timeline, zooms), frame-accurate FCPXML generation.

**Zoom stage adds real production value** with zero manual effort — frame extraction, anchor analysis from actual screenshots, FCPXML adjustment clips with verified FCP coordinates.

## What underperformed

**Polish stage was near-worthless.** Removed 5.4s from a 20-min video (0.14%). Found 5 issues, ran a full re-transcription cycle, barely changed anything. Without a thesis, pacing drag (the highest-value category) is disabled. The render→transcribe→evaluate loop isn't justified for 4 minor fixes.

**Zoom scales too conservative.** All 18 zooms used 1.10–1.30 (old defaults). Updated to 1.50 baseline after the fact but didn't regenerate. 0.9 zooms/min is sparse, with a 229s dead zone.

**Cut stage too conservative.** 408/463 utterances kept. Long stretches of config debugging, extension troubleshooting, and screen-reading survived. Correct behavior without a thesis — but the video would benefit from editorial cuts.

---

## Bugs found and fixed during this run

| Bug | Location | Fix |
|---|---|---|
| `execute` instead of `handler` | `video-editor.ts` | Renamed to `handler` (pi API) |
| `ctx.agent.queueMessage` doesn't exist | `video-editor.ts` | Changed to `pi.sendUserMessage()` |
| ±1 frame offset drift between clips | `timeline.py`, `zooms.py` | Accumulate timeline position in integer frames, not float seconds |

The extension bugs existed since the first commit — the extension was never tested. The frame drift produced 83/346 one-frame gaps/overlaps in the FCPXML.

---

## Recommended changes

### 1. Make polish conditional on thesis

Skip polish entirely for rough cuts, or reduce to a lightweight stumble-only scan without re-transcription. The full cycle isn't worth it for 4 minor issues.

### 2. Add stage skip flags

Let the user opt out of stages (`--skip-polish`, `--skip-zoom`). Currently all-or-nothing.

### 3. Regenerate zooms after scale changes

The pipeline should either regenerate zooms when defaults change or apply the default scale only as a fallback (not baked into zooms.json).

### 4. Smoke test the extension

`video-editor.ts` was broken from day one. Add a basic test that verifies handler registration and message sending.

---

## Ideas for future improvement

### Highest value

**Silence/dead-air removal as pre-processing.** The 64-min source has large stretches of silence (waiting for LLM responses, reading, thinking). Energy-based silence detection before transcription would cut the raw material dramatically. Single highest-value addition.

**Chapter markers / segment detection.** Natural topic transitions ("Okay. We'll come back to that.") should become FCPXML chapter markers for editing and YouTube chapters.

### Medium value

**Multi-pass zoom with motion tracking.** Static anchors don't work for scrolling terminal content. Keyframed position pans would keep relevant text in frame.

**Audio normalization between segments.** Jump cuts have audible volume differences. Per-segment LUFS matching would smooth the audio.

**Confidence scoring on cut decisions.** Have the LLM rate confidence (high/medium/low) per removal. Flag low-confidence decisions for human review.

### Things to learn from this video

**1. YouTube retention curves.** If published, compare viewer drop-off points against kept utterances. That's ground truth for editorial instincts.

**2. Does thesis matter?** Re-run with thesis like "Pi is a minimal, extensible coding agent that doesn't lock you in." Measure how much more the cut stage removes.

**3. Zoom scale calibration.** A/B test old (1.10–1.30) vs new (1.50+) scales. Right level depends on recording layout (split-screen vs talking head).

**4. Automatic b-roll detection.** When speaker says "let's look at the docs" and screen shows docs — detect and flag for zoom-to-screen or overlay.
