# Agents Workspace

This is Chan's (chantastic) shared agent workspace. Skills and services here are used across coding agents (Pi, Claude Code, Codex).

## Structure

```
services/     — standalone Python CLI scripts. No agent dependency.
  requirements.txt — pip dependencies (opentimelineio, otio-fcpx-xml-adapter)
skills/       — Agent Skills standard (agentskills.io). Portable across agents.
```

## Setup

```bash
pip3 install -r ~/.agents/services/requirements.txt
```

Also requires: `ffmpeg`, `ffprobe` on PATH, and `DEEPGRAM_API_KEY` in environment.

## Active Skills

| Skill | Purpose |
|-------|---------|
| `video-pipeline` | Orchestrator: coordinates cut → polish → zoom → publish stages, manages manifest |
| `video-cut` | Rough cut: transcribe + LLM decisions → FCPXML |
| `video-polish` | Iterative refinement: re-transcribe, evaluate flow, fix issues |
| `video-zoom` | Zoom/punch-in effects via FCPXML adjustment clips |
| `run-video-publish` | Coordinator for publish-prep assets (captions, chapters, titles, thumbnails, brief) |
| `create-marketing-brief` | Create one multi-section marketing brief for LinkedIn, Twitter/X, and recap/blog |
| `broll-research` | B-roll asset collection from transcripts |
| `chantastic-scripts` | Blog → YouTube script conversion |
| `youtube-audit` | Channel analysis via yt-dlp |
| `xstate-naming` | XState naming conventions |
| `skill-authoring` | Guide for writing and refactoring skills |

The video skills form a pipeline: `video-pipeline` orchestrates `video-cut` → `video-polish` → `video-zoom`. Each skill can also be invoked standalone — the pipeline coordinator passes cross-stage inputs between stages, but each skill only needs its declared inputs and the harness capabilities available to it, not the manifest.

`run-video-publish` runs after the operator exports from their NLE. It is not part of the video editing pipeline, but it does coordinate the publish-prep workflow for that final export.

`create-marketing-brief` consumes the publish/content brief and produces one markdown document with platform-specific sections for downstream marketing use.

## Principles

### Skills depend on capabilities, not coordination state

A skill may depend on the harness, services, explicit inputs, convention-based discovery, and operator interaction. It may not read manifests, inspect pipeline state, or know what stage it's in. When run standalone, it discovers, derives, or asks. When run via a coordinator, cross-stage inputs are provided.

See OPERATING_PRINCIPLES.md §11.

### Only the coordinator knows the graph

Sequencing, state tracking, retries, and inter-skill wiring live in `video-pipeline`. Individual skills don't know what ran before or after them. The manifest is the coordinator's state file — no other skill reads or writes it.

See OPERATING_PRINCIPLES.md §12.

### The operator is never re-asked

Previously this workspace stated "manifests over re-asking" — downstream skills read the manifest directly to avoid redundant questions. The intent is the same: the operator should never be asked for something the system already knows. What changed is the mechanism. In a coordinated pipeline, the coordinator reads the manifest and passes inputs explicitly. In standalone use, the skill discovers or asks. Either way, the operator provides each piece of information once.

The shift from "every skill reads the manifest" to "the coordinator reads the manifest and context-independent skills receive inputs" is an architectural upgrade, not a reversal. It separates the concern of *not re-asking* (still true) from the mechanism of *how context flows* (now cleaner).

### Convention is not coupling

Skills can use sensible discovery defaults ("find the largest .mp4 here") without knowing the system that produced the file. Encoding knowledge of another skill's internal structure (reading manifest fields, checking decision file paths) is coupling and belongs only in the coordinator.

See OPERATING_PRINCIPLES.md §13.

### Project artifacts live with the project, learning artifacts live with the skill

Video project artifacts (previews, transcripts, edit lists, timelines) live in the project directory. Evals, self-analyses, and calibration data live alongside the skill they improve (`~/.agents/skills/<skill>/evals/`).

### Services over abstractions

Services are thin CLI wrappers around a specific external tool (Deepgram, ffmpeg, OTIO). They do one thing. They don't abstract over multiple backends.

### Skills are prompts, not code

A skill's SKILL.md is an LLM prompt with bash commands. The intelligence lives in the instructions (what to look for, how to decide), not in algorithmic code.

### LLMs for decisions, services for I/O

The LLM reads data, makes decisions, writes decisions. Services handle I/O: calling APIs, reading files, rendering video.

### Build for the best case

Use the best available tool (Deepgram, Claude). Don't add fallback paths for cheaper/offline alternatives inside the same service.

### Re-transcribe the output to evaluate it

Render the preview, transcribe it, read as continuous flow. This catches issues no amount of decision-reviewing will find.

## Video Editing — Hard-Won Knowledge

### Transcription

- **Deepgram Nova-3** is the transcription backend. Utterance detection (`utterances=true`) is the single most important feature — it splits retakes that whisper groups into one segment.
- **Always use keyterms** (`keyterm` parameter). Domain terms (product names, people, technical jargon) are consistently misrecognized without boosting. A two-pass approach (cheap first pass → identify variants → re-transcribe with keyterms) costs ~$0.56 for a 60-min video and dramatically improves quality.
- **Send audio, not video.** Deepgram bills per minute of audio, not file size. But uploading 14MB (Opus) vs 1.7GB (MP4) means the API responds in seconds instead of minutes.
- **48kbps Opus** is sufficient for speech transcription. No quality loss vs WAV for STT purposes.
- **Deepgram does not hallucinate.** Unlike whisper (encoder-decoder), Deepgram returns nothing during silence. No "Thank you" artifacts. No repetition loops.
- **Paragraphs** (`paragraphs=true`) return natural topic boundaries. Use these to understand section structure, not as selection units.

### Editing

- **The LLM is the edit engine.** Feed it the utterance list. It makes keep/remove decisions with semantic understanding. No SequenceMatcher. No prefix matching.
- **Keep the last take.** When the speaker does multiple attempts at a sentence, keep the last complete version.
- **Contiguous time ranges, not sentence fragments.** Never cherry-pick individual sentences from a flowing section. If you keep part of a paragraph, keep a contiguous run. Cuts should feel like jump cuts between complete thoughts.
- **Sentences inform boundaries, not selection.** Use sentence timestamps to snap cut points to clean word boundaries. Don't use sentences as Lego blocks to assemble.
- **Editorial cuts need a thesis.** "Remove duplicates" is mechanical. "What serves a compelling YouTube video?" requires an anchor — the video's main point. Without it, editorial decisions have no basis.
- **Padding of 50ms** on each cut prevents clipped consonants without noticeable dead air.

### Polish / Refinement

- **Re-transcription is the QA step.** Render the preview, transcribe it with Deepgram, read the output as continuous flow. This is how you catch missed duplicates ("Oh, interesting" said twice 10 utterances apart), mid-utterance stumbles ("good to dig and good to go"), and false starts that span two kept utterances.
- **Editorial pacing is ~70% of polish value.** Compressing "tried 5 paths, failed each" into "tried, failed, resolved" saves more time than all mechanical fixes (dead air, filler, stumbles) combined. The skill should treat pacing as the primary concern, not a bullet in a list.
- **Mechanical dead-air removal is nearly worthless.** Deepgram's utterance boundaries are already tight around speech. Internal silence gaps >0.4s totaled 1.6s across 349 segments in a 20-min edit. The perceived "dead air" is a pacing problem, not a silence problem.
- **Word-level timestamps enable mid-utterance surgery.** Deepgram returns start/end for every word. Use these to trim self-corrections ("good to dig and we should be good to go" → "good to go") that live inside a single utterance and are invisible to utterance-level decisions.
- **Convergence is fast.** Usually one fix cycle (evaluate → fix → verify). Issues are systematic (missed duplicates, pacing), not cascading. Allow up to 3 cycles but expect 1.
- **Project structure matters.** Use `cut/`, `polish/pass_N/`, `polish/final/` directories. Flat files in a root directory don't compose, collide across runs, and lose lineage.

### Output

- **OTIO is the interchange format.** Generate OTIO first, then export to FCPXML via `otio-fcpx-xml-adapter`. OTIO is JSON-based, Python-native, and editor-agnostic.
- **Always generate FCPXML alongside OTIO** — it's the format the editor (Final Cut Pro) actually opens.
- **FCPXML references source video by absolute path.** The source must be accessible at that path when opening in FCP.
- **Save all intermediates** (transcript.json, decisions.json, edit_list.json). They're the audit trail. The user can review every cut decision.

### Cost

A full pipeline run (transcription + LLM edit decisions + polish re-transcriptions) costs ~$0.60-$1.20 per 60-min video. This is negligible. Don't optimize for cost at the expense of quality. The polish pass adds ~$0.20-$0.40 for re-transcriptions and is worth every cent.
