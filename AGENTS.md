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
| `video-pipeline` | Orchestrator: coordinates cut → polish stages, manages manifest |
| `video-cut` | First pass editing: Deepgram + LLM → FCPXML |
| `video-polish` | Iterative refinement: re-transcribe preview, fix what first pass missed |
| `broll-research` | B-roll asset collection from transcripts |
| `chantastic-scripts` | Blog → YouTube script conversion |
| `youtube-audit` | Channel analysis via yt-dlp |
| `xstate-naming` | XState naming conventions |

The video skills form a pipeline: `video-pipeline` → `video-cut` → `video-polish`. Call `video-pipeline` to run the full chain, or invoke individual skills directly.

Previously `rough-cut` existed here (whisper-cli + silencedetect). It was removed — `video-cut` fully replaces it.

For the cross-skill collaboration doctrine and the rationale behind these rules, see `OPERATING_PRINCIPLES.md`.

## Principles

### Project artifacts live with the project, learning artifacts live with the skill

Video project artifacts (manifests, previews, transcripts, edit lists, timelines) live in the project directory — even if that's in `~/Downloads`. They're tied to that specific video and disposable once the video ships.

But evals, self-analyses, and accuracy data are **skill development artifacts**. They teach the skills to be better. If they're stored in the project directory (especially Downloads), they vanish when the project is cleaned up and can never inform future runs. Store them alongside the skill or extension they improve (e.g., `~/.agents/skills/video-pipeline/evals/`).

### Services over abstractions

Services are thin CLI wrappers around a specific external tool (Deepgram, ffmpeg, OTIO). They do one thing. They don't abstract over multiple backends — a Deepgram wrapper is a Deepgram wrapper, not a "transcription service with pluggable backends." If a different backend is needed, write a different script.

This was learned the hard way: a unified transcription schema that papered over whisper and Deepgram differences lost the features (utterance boundaries, keyterms) that made Deepgram better.

### Skills are prompts, not code

A skill's SKILL.md is an LLM prompt with bash commands. The intelligence lives in the instructions (what to look for, how to decide), not in algorithmic code. When an LLM can do the task better than an algorithm, delete the algorithm.

Example: duplicate take detection. SequenceMatcher catches "As a two decade Vim user, I've been" matching "as a two decade Vim user, I've been looking for something." But it misses "I wanted to dive into Pi" matching "I had a desire to dive into Pi." The LLM catches both. The SequenceMatcher code was deleted.

### LLMs for decisions, services for I/O

The LLM reads data, makes decisions, writes decisions. Services handle I/O: calling APIs, reading files, rendering video. Don't put decision logic in Python when the LLM is better at it. Don't put file I/O in the LLM prompt when a script is more reliable.

### Manifests over re-asking

When skills form a pipeline, use a `manifest.json` as the contract between stages. The first skill gathers inputs (video path, keyterms, thesis) and writes them to the manifest. Every downstream skill reads the manifest instead of re-asking the user. The manifest also tracks stage status (complete/in_progress/failed), file paths, and stats — enabling resumption, re-runs, and auditability.

File paths in the manifest are relative to the project directory. Source files that live outside the project use absolute paths.

### Re-transcribe the output to evaluate it

You cannot evaluate an edit by reviewing the edit list on paper. Re-transcribe the rendered preview and read it as a viewer would experience it — a continuous flow. Duplicates, stumbles, and pacing problems that are invisible when reading isolated utterances become obvious in continuous flow. This costs one Deepgram call (~$0.20) and catches issues no amount of careful decision-making will find on the first pass.

### Build for the best case

Use the best available tool (Deepgram, Claude). Don't add fallback paths for cheaper/offline alternatives inside the same service — that creates untested code paths that produce worse results silently. If offline is needed, build a separate skill explicitly labeled as lower quality.

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
- **Project structure matters.** Use `cut/`, `polish/pass_N/`, `polish/final/` directories. Flat files in a root directory don't compose, collide across runs, and lose lineage. A manifest.json tracks which file fed which.

### Output

- **OTIO is the interchange format.** Generate OTIO first, then export to FCPXML via `otio-fcpx-xml-adapter`. OTIO is JSON-based, Python-native, and editor-agnostic.
- **Always generate FCPXML alongside OTIO** — it's the format the editor (Final Cut Pro) actually opens.
- **FCPXML references source video by absolute path.** The source must be accessible at that path when opening in FCP.
- **Save all intermediates** (transcript.json, decisions.json, edit_list.json). They're the audit trail. The user can review every cut decision.

### Cost

A full pipeline run (transcription + LLM edit decisions + polish re-transcriptions) costs ~$0.60-$1.20 per 60-min video. This is negligible. Don't optimize for cost at the expense of quality. The polish pass adds ~$0.20-$0.40 for re-transcriptions and is worth every cent.
