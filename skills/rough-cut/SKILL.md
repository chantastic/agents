---
name: rough-cut
description: "ARCHIVED — use video-cut instead. This skill used whisper-cli and ffmpeg silencedetect. It has been replaced by video-cut which uses Deepgram and LLM-driven edit decisions for significantly better results."
disable-model-invocation: true
---

# ⚠️ Archived

This skill has been superseded by `video-cut`.

See `video-cut/SKILL.md` for the current video editing pipeline.

## Why

The rough-cut skill used whisper-cli (hallucinations, poor word timestamps) and ffmpeg silencedetect (no semantic understanding). The video-cut skill uses Deepgram (utterance detection, zero hallucinations, keyterms) and LLM edit decisions (semantic duplicate detection). Quality is dramatically better.
