---
name: rough-cut
description: Generate a Final Cut Pro timeline from a video file with automatic silence removal and duplicate take detection. Use when creating rough cuts, removing silences from recordings, or generating FCPXML timelines from video files.
---

# Rough Cut Skill

Generate a Final Cut Pro timeline from a video file with automatic silence removal.

## When to Use

Use this skill when the user asks to:
- Create a rough cut from a video
- Remove silences from a recording
- Generate an FCP timeline from a video file
- Edit a livestream or recording session

## Required Inputs

Ask the user for:
1. **Video file path** (required)
2. **Output location** (optional - defaults to same directory as video)

## Step 1: Get Video Properties

```bash
mdls -name kMDItemDurationSeconds -name kMDItemPixelWidth -name kMDItemPixelHeight "<video_path>"
```

## Step 2: Analyze Audio + Transcribe

### 2a. Detect Noise Floor (Adaptive Threshold)

```bash
ffmpeg -i "<video_path>" -af "volumedetect" -f null - 2>&1 | grep mean_volume
```

Calculate adaptive silence threshold: `silence_threshold = mean_volume - 10dB`

### 2b. Transcribe + Detect Silence

```bash
ffmpeg -i "<video_path>" -vn -acodec pcm_s16le -ar 16000 -ac 1 /tmp/audio_for_whisper.wav -y
whisper-cli -m ~/.whisper/models/ggml-large-v3-turbo.bin -f /tmp/audio_for_whisper.wav --output-json
ffmpeg -i "<video_path>" -af silencedetect=n=-30dB:d=1 -f null - 2>&1 | grep -E "silence_start|silence_end"
```

## Step 3: Analyze for Cuts

### 3a. Detect Silences
Gap > 1000ms between segments = cuttable silence.

### 3b. Detect Repeated Takes
Compare first 3-5 words of consecutive segments. Keep only the LAST take.

### 3c. Build Kept Segments
Skip earlier takes, split at silence gaps, merge consecutive kept segments.

## Step 4: Generate FCPXML

FCPXML 1.13 for FCP 11.x. Key rules:
- No `/` in name attributes
- Times as fractions: `frames/30s`
- Asset must have `<media-rep>` child
- Padding: 0.25s pre-roll, 0.15s post-roll
- Chapter markers REQUIRE `posterOffset` to avoid FCP crash

See `config.json` for configurable parameters and `SESSION_CONTEXT.md` for FCPXML format details.

## Step 5: Generate YouTube Chapters

Create `chapters.txt` with `M:SS` timestamps. First chapter at `0:00`, minimum 3 chapters, 10s minimum per chapter.

## Step 6: Save and Report

Report: original duration, new duration, time saved, cuts made, silences removed, chapter count.

## Marker Protocol

| Marker Type | Use For |
|-------------|---------|
| `<marker>` | Edit points, kept reasons |
| `<chapter-marker>` | Section boundaries (requires posterOffset) |
| `<marker completed="0">` | Review suggestions |

Notes field for metadata: `agent:rough-cut|silence:12.5s|confidence:0.95`
