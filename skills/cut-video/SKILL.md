---
name: cut-video
description: Create a rough cut from a video recording. Transcribes with Deepgram, uses the LLM to remove duplicate takes, false starts, and fragments, infers a thesis, and outputs FCPXML for Final Cut Pro. Use when editing video recordings or removing retakes before polish.
role: transformation
---

# Video Cut

This is a transformation skill. It takes a source recording and produces the first durable cut artifacts.

Create a publication-ready rough cut from a raw recording.

## Epistemic Status

This skill intentionally separates **principle**, **heuristic**, **preference**, and **temporary calibration**.

- **Principles** belong here in `SKILL.md` — rough cut first, editorial later; decisions are source; cut contiguous thoughts, not sentence confetti
- **Heuristics** belong here too — duplicate takes, false starts, fragments, and mistake reactions are common removal categories
- **Preferences** should be stated as taste, not law — some creators want more personality left in the rough cut than others
- **Temporary calibration** (what counts as too fragmentary, when a reaction adds charm, when a short utterance is really a list item, how conservative to be) belongs in `evals/`

When in doubt: keep the rough-cut method here, and let edge-case aggressiveness be calibrated from real reviews.

## Required Environment

- `DEEPGRAM_API_KEY` — set in environment
- `ffmpeg` and `ffprobe` — installed
- Python packages: `opentimelineio`, `otio-fcpx-xml-adapter`

## Inputs

| Input | Required | Discovery | Description |
|-------|----------|-----------|-------------|
| source | yes | discover: largest .mp4/.mov in cwd | Path to the raw video recording |
| keyterms | no | suggest from context | Domain terms for Deepgram speech-to-text accuracy |
| target_duration | no | default: aim for 10-15 min | Target length for the cut |
| output_dir | no | default: working directory | Where to write all outputs |

When run standalone, discover or ask for each input. When run via a coordinator (e.g., run-video-pipeline), these are provided explicitly.

Do not ask for a thesis. The thesis is inferred from the content after edit decisions are made (see Step 5b).

## Outputs

| File | Type | Description |
|---|---|---|
| `transcript.json` | **source** | Deepgram transcript with word-level timestamps |
| `utterances.txt` | **source** | Formatted utterances for review |
| `decisions/cut.json` | **source** | LLM edit decisions with reasoning + inferred thesis |
| `cut/edit_list.json` | artifact | Compiled segment list |
| `cut/preview.mp4` | artifact | Rendered preview |
| `cut/timeline.fcpxml` | artifact | Final Cut Pro timeline |
| `cut/timeline.otio` | artifact | OpenTimelineIO timeline |

The inferred thesis is written into `decisions/cut.json` and reported to the operator.

## Process

### Step 1: Gather Inputs

Resolve each input using the discovery rules above. Create directories `cut/` and `decisions/` if they don't exist.

### Step 2: Transcribe

Transcribe to the **output root** — the transcript is a shared source of truth, not a cut-stage artifact.

```bash
DEEPGRAM_API_KEY=<key> python3 ~/.agents/services/transcribe.py "<source>" \
  --keyterms "<comma,separated,terms>" \
  --output transcript.json
```

### Step 3: Format Utterances for Review

```bash
python3 ~/.agents/services/edit.py format transcript.json --output utterances.txt
```

Read `utterances.txt`. Each line is one utterance with index, timestamps, duration, and text.

### Step 4: Make Edit Decisions

Read every utterance. For each, decide **keep** or **remove**.

**Removal rules (rough cut only — no editorial decisions at this stage):**
- **Duplicate takes**: Multiple attempts at the same sentence. Usually keep the LAST complete version. This includes semantically equivalent phrasings — "wanted to dive into" and "had a desire to dive into" are the same take.
- **False starts**: Speaker begins a sentence but abandons it. The next utterance restarts the same thought more completely. But do not remove a short utterance just because the next one is fuller — labels, names, and list items can add distinct information.
- **Fragments**: Isolated single words or sub-second utterances that aren't meaningful are usually removable. But short utterances can still carry tone, rhythm, or useful emphasis.
- **Reactions to mistakes**: "Oh my gosh" after stumbling, nervous laughter between takes — usually remove unless it adds personality, rhythm, or a sense of real-time process the viewer would enjoy.

Editorial decisions (tangential sections, pacing, repeated observations) are **not** made here. They happen in the polish stage, after the thesis has been inferred from the content.

**Critical rule**: The unit of selection is CONTIGUOUS TIME RANGES. Do not assemble fragments from different parts of a paragraph. If a section flows naturally, keep the whole flow. Cuts should feel like jump cuts between complete thoughts, not spliced-together sentence fragments.

For each removal, write a brief reason.

### Step 5: Write Decisions

Write a JSON file with decisions:

```json
{
  "decisions": {
    "000": "keep",
    "001": "remove: false start of 002 ('Pi is a minimal term' vs complete 'Pi is a minimal terminal coding harness')",
    "020": "remove: semantically duplicate of 027 — same intro sentence, different phrasing"
  }
}
```

Save as `decisions/cut.json`.

### Step 5b: Infer Thesis

After making edit decisions, you have read every utterance and know what the speaker actually said. Now synthesize a **thesis** — a one or two sentence description of what this video is about.

Guidelines:
- Ground the thesis in the kept utterances, not the removed ones.
- Focus on what the speaker **does and discovers**, not just the topic. "First look at Pi, exploring extensions, model switching, skills, and cross-agent compatibility" is better than "A video about Pi."
- Include the speaker's perspective or arc if one emerges. "Evaluating Pi as a VIM replacement for AI-assisted coding" captures intent.
- Keep it concrete enough to make editorial decisions against. The polish stage will use this thesis to decide what's tangential and what's essential.

Write the thesis into the decisions file for auditability:

```json
{
  "decisions": { ... },
  "thesis": "First look at Pi as a coding harness — installing, configuring models, exploring tree-based sessions, sharing, and testing extensions."
}
```

Report the inferred thesis to the operator. They can adjust it before moving on.

### Step 6: Compile Edit List

```bash
python3 ~/.agents/services/edit.py apply transcript.json decisions/cut.json \
  --padding 0.05 --output cut/edit_list.json
```

### Step 7: Generate Timeline

```bash
python3 ~/.agents/services/timeline.py \
  --source "<source>" \
  --edits cut/edit_list.json \
  --name "<descriptive timeline name>" \
  --output cut/timeline.otio
```

This generates both `cut/timeline.otio` and `cut/timeline.fcpxml`.

### Step 8: Render Preview

```bash
python3 ~/.agents/services/render.py "<source>" \
  --edits cut/edit_list.json \
  --output cut/preview.mp4
```

### Step 9: Report

Report to the operator:
- Original duration → edited duration (% removed)
- Number of utterances kept vs removed
- Summary of what was cut and why (grouped by category: duplicates, false starts)
- **Inferred thesis** — ask operator to confirm or adjust
- Paths to all outputs
- Remind user to open `.fcpxml` in Final Cut Pro for review

## Notes

- The FCPXML references the source video by absolute path. The source video must be accessible at that path when opening in FCP.
- The cut stage always does a rough cut. Editorial decisions happen in the polish stage, informed by the inferred thesis.
- **Decisions are the contract.** The edit list is a compiled artifact that merges contiguous utterances into segments. Downstream stages (polish) produce their own decisions against the original transcript, and a single compile step merges all layers.
- Edge-case judgment is calibration, not doctrine. Use `evals/` to capture where the operator restored a short utterance, kept a reaction, or treated a would-be false start as a meaningful label.
