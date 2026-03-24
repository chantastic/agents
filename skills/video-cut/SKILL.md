---
name: video-cut
description: Create a rough cut and editorial cut from a video recording. Transcribes with Deepgram, uses the LLM to remove duplicate takes and make editorial decisions, outputs FCPXML for Final Cut Pro. Use when editing video recordings, removing retakes, or creating YouTube-ready cuts.
---

# Video Cut

Create a publication-ready video edit from a raw recording.

## Required Environment

- `DEEPGRAM_API_KEY` — set in environment
- `ffmpeg` and `ffprobe` — installed
- Python packages: `opentimelineio`, `otio-fcpx-xml-adapter`

## Process

### Step 1: Gather Inputs

Ask the user for:
1. **Video file path** (required)
2. **Domain terms** that may be misrecognized by speech-to-text (product names, people, technical terms). Suggest terms based on context.
3. **Video goal/thesis** (optional — for editorial cut). Example: "Pi is a minimal, extensible coding agent."
4. **Target duration** (optional — default: aim for 10-15 min for YouTube)

### Step 2: Transcribe

```bash
DEEPGRAM_API_KEY=<key> python3 ~/.agents/services/transcribe.py "<video_path>" \
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

**Removal rules (rough cut):**
- **Duplicate takes**: Multiple attempts at the same sentence. Keep the LAST complete version. This includes semantically equivalent phrasings — "wanted to dive into" and "had a desire to dive into" are the same take.
- **False starts**: Speaker begins a sentence but abandons it. The next utterance restarts the same thought more completely.
- **Fragments**: Isolated single words or sub-second utterances that aren't meaningful (not interjections like "okay", "nice", "wow").
- **Reactions to mistakes**: "Oh my gosh" after stumbling, nervous laughter between takes — remove unless it adds personality.

**Additional removal rules (editorial cut — apply if thesis/goal provided):**
- **Tangential sections**: Content that doesn't serve the video's thesis. A joke test in a tool review, for example.
- **Lengthy explorations**: 5 minutes of config debugging can be told in 1 minute — keep the intent, the struggle moment, and the payoff.
- **Reading aloud**: Viewers can read. Keep the speaker's reaction to what they're reading, cut the reading itself.
- **Repeated observations**: "Pretty painless" said three different ways — keep the best one.

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

Save as `decisions.json`.

### Step 6: Apply Decisions

```bash
python3 ~/.agents/services/edit.py apply transcript.json decisions.json \
  --padding 0.05 --output edit_list.json
```

### Step 7: Generate Timeline

```bash
python3 ~/.agents/services/timeline.py \
  --source "<video_path>" \
  --edits edit_list.json \
  --name "<descriptive timeline name>" \
  --output timeline.otio
```

This generates both `timeline.otio` and `timeline.fcpxml`.

### Step 8: Render Preview

```bash
python3 ~/.agents/services/render.py "<video_path>" \
  --edits edit_list.json \
  --output preview.mp4
```

### Step 9: Report

Report to the user:
- Original duration → edited duration (% removed)
- Number of utterances kept vs removed
- Summary of what was cut and why (grouped by category: duplicates, false starts, editorial)
- Paths to outputs: `.fcpxml`, `.otio`, `preview.mp4`, `edit_list.json`, `decisions.json`
- Remind user to open the `.fcpxml` in Final Cut Pro

## Notes

- The FCPXML references the source video by absolute path. The source video must be accessible at that path when opening in FCP.
- All intermediate files (transcript.json, decisions.json, edit_list.json) are saved for auditability. The user can review decisions.json to understand every cut.
- If the user asks for just a rough cut (no editorial), skip the editorial removal rules in step 4.
