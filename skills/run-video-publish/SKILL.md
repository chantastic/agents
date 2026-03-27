---
name: run-video-publish
description: Coordinate publish preparation from a final video export. Transcribes the final edit, generates chapters, captions (SRT), title options, thumbnails, and a content brief for downstream marketing work. Use after exporting from your NLE.
---

# Run Video Publish

Coordinate publish preparation from a final video export.

This is a coordinator skill. It sequences the publish-prep workflow for a final export: transcript, captions, chapters, titles, description, thumbnails, and the content brief handoff artifact.

There is a human step between zoom and publish (reviewing in FCP, exporting), so this skill is invoked separately after export.

## Required Environment

- `DEEPGRAM_API_KEY` — set in environment
- `ffmpeg` and `ffprobe` — installed
- `GOOGLE_API_KEY` — optional (for thumbnail generation via Imagen)
- Python package: `google-genai` — optional (for thumbnails)

## Inputs

| Input | Required | Discovery | Description |
|-------|----------|-----------|-------------|
| export | yes | discover: largest .mp4 in cwd, or publish/export.mp4 | The final exported video |
| thesis | no | ask if not discoverable | What the video is about (guides titles, chapters, description) |
| keyterms | no | suggest from context | Domain terms for Deepgram accuracy |
| speakers | no | default: chantastic; infer from filename; ask if uncertain | Speaker attribution |
| output_dir | no | default: publish/ | Where to write all outputs |

When run standalone (the normal case), discover or ask for each input.

Speaker attribution inference precedence:
1. Infer from the export filename / project title if guest names are obvious
2. Check stream metadata or naming conventions from Restream exports
3. Default to `chantastic`
4. If still uncertain, ask the operator

## Outputs

All outputs go to `publish/` (or the specified output_dir):

```
publish/
├── transcript.json            ← Deepgram JSON (kept for querying)
├── captions.srt               ← subtitles
├── captions.vtt               ← WebVTT version
├── chapters.json              ← chapter data (timestamps, titles, summaries)
├── chapters.txt               ← YouTube-formatted (00:00 Title)
├── titles.json                ← viral title options with reasoning
├── description.md             ← SEO description with chapter markers
├── brief.json                 ← content brief for downstream platform skills
└── thumbnails/
    ├── concepts.json          ← thumbnail concepts with prompts
    ├── moments.json           ← high-energy moments from transcript
    ├── frames/                ← extracted frames at emotional peaks
    └── T001.png ... T00N.png  ← generated images (if GOOGLE_API_KEY set)
```

## Process

### Step 1: Locate the export

Resolve the `export` input using discovery:
1. If the operator provided a path, use it
2. `publish/export.mp4` or `publish/export.mov`
3. `export.mp4` or `export.mov` at project root
4. Largest `.mp4`/`.mov` at project root
5. If ambiguous, ask

### Step 2: Gather context

Resolve `thesis`, `keyterms`, and `speakers` using the discovery rules in the Inputs table. If thesis isn't provided or discoverable, ask for a brief description.

### Step 3: Transcribe

```bash
DEEPGRAM_API_KEY=<key> python3 ~/.agents/services/transcribe.py "<export>" \
  --keyterms "<terms>" \
  --output publish/transcript.json
```

### Step 4: Generate captions (SRT + VTT)

Build captions from transcript utterances. Split long utterances at ~80 chars on word boundaries.

```python
import json

with open('publish/transcript.json') as f:
    data = json.load(f)

utterances = data.get('utterances', [])

def format_srt_time(seconds):
    h, rem = divmod(seconds, 3600)
    m, rem = divmod(rem, 60)
    s, ms = divmod(rem, 1)
    return f'{int(h):02d}:{int(m):02d}:{int(s):02d},{int(ms*1000):03d}'

def format_vtt_time(seconds):
    h, rem = divmod(seconds, 3600)
    m, rem = divmod(rem, 60)
    s, ms = divmod(rem, 1)
    return f'{int(h):02d}:{int(m):02d}:{int(s):02d}.{int(ms*1000):03d}'

captions = []
for u in utterances:
    text = u['transcript'].strip()
    start, end = u['start'], u['end']
    duration = end - start
    if len(text) <= 80 or duration < 3:
        captions.append((start, end, text))
    else:
        mid = len(text) // 2
        space = text.find(' ', mid)
        if space == -1: space = mid
        mid_time = start + (duration * space / len(text))
        captions.append((start, mid_time, text[:space].strip()))
        captions.append((mid_time, end, text[space:].strip()))

with open('publish/captions.srt', 'w') as f:
    for i, (s, e, t) in enumerate(captions, 1):
        f.write(f'{i}\n{format_srt_time(s)} --> {format_srt_time(e)}\n{t}\n\n')

with open('publish/captions.vtt', 'w') as f:
    f.write('WEBVTT\n\n')
    for i, (s, e, t) in enumerate(captions, 1):
        f.write(f'{format_vtt_time(s)} --> {format_vtt_time(e)}\n{t}\n\n')
```

### Step 5: Generate chapters

Read the transcript utterances. Identify natural topic boundaries.

**Chapter guidelines:**
- First chapter at `00:00` (YouTube requirement)
- Target 5-10 chapters (flexible)
- Minimum ~2 minutes between chapters
- **Titles are learner outcomes, not topic labels:**
  - ✅ "How to Use Claude and GPT in the Same Session"
  - ❌ "Multi-Model Setup and Vendor Lock-In"
- Use the thesis to weight titles toward the video's narrative

Write `publish/chapters.json` and `publish/chapters.txt` (YouTube-ready format).

### Step 6: Generate title options

Generate 5-8 title options. Mix styles:

| Style | Example |
|---|---|
| **Curiosity gap** | "I Switched from Claude Code to This" |
| **Confrontational** | "Claude Code Has a Vendor Lock-In Problem" |
| **How-to** | "How to Use Any AI Model in One Terminal" |
| **Listicle** | "5 Things Pi Does That Claude Code Can't" |
| **Emotional** | "Why I'm Worried About Claude Going Public" |

Write `publish/titles.json` with reasoning for each.

### Step 7: Generate SEO description

Write `publish/description.md`:
1. **Hook** (first 2-3 lines, visible before "show more")
2. **Summary** — grounded in thesis, mentioning speakers by name
3. **Chapter list** — from chapters.txt
4. **Links** — tools, speakers, resources mentioned
5. **Tags/keywords** — for SEO

**Clear is greater than clever. But clever is still great.**

### Step 8: Identify thumbnail moments

Query the transcript for high-energy moments:
- Reactions and exclamations
- Laughter
- Rapid back-and-forth exchanges
- Emphatic statements
- Reveals and surprises
- Self-deprecating humor

Select top 8-12 moments. Write `publish/thumbnails/moments.json`.

### Step 9: Extract frames and generate thumbnails

Extract frames at each moment:

```bash
mkdir -p publish/thumbnails/frames
ffmpeg -y -ss <seconds> -i "<export>" -frames:v 1 -q:v 2 publish/thumbnails/frames/<id>.jpg
```

Design 3-4 thumbnail concepts. Write `publish/thumbnails/concepts.json`.

Thumbnail principles:
- **Readable at 120×68px**
- **Faces drive clicks**
- **3-5 words max**
- **Visual tension**
- **Honest**

If `GOOGLE_API_KEY` is set, generate with Imagen. Otherwise skip — concepts provide prompts for manual creation.

### Step 10: Generate content brief

Write `publish/brief.json` — the hand-off artifact for downstream marketing work.

Downstream brief contract:
- `create-marketing-brief` relies on: `thesis`, `speakers`, `chapters`, `key_quotes`, `key_moments`, `topics`, `links`, `titles`
- include `transcript_path` so downstream work can optionally read the full transcript without guessing

Write `publish/brief.json`:

```json
{
  "thesis": "...",
  "speakers": { ... },
  "duration": "48:50",
  "chapters": [ ... ],
  "key_quotes": [ ... ],
  "key_moments": [ ... ],
  "topics": [ ... ],
  "links": { ... },
  "titles": [ ... ],
  "transcript_path": "publish/transcript.json"
}
```

### Step 11: Report

| Asset | File | Notes |
|---|---|---|
| Transcript | `publish/transcript.json` | Deepgram JSON, queryable |
| Captions | `publish/captions.srt` + `.vtt` | Subtitle files |
| Chapters | `publish/chapters.txt` | YouTube-ready, paste directly |
| Titles | `publish/titles.json` | 5-8 options with reasoning |
| Description | `publish/description.md` | SEO-friendly with chapters |
| Thumbnails | `publish/thumbnails/` | Moments + frames + concepts |
| Content brief | `publish/brief.json` | Hand-off for platform skills |

Remind user:
- Review titles and chapters before uploading
- Run `create-marketing-brief` using `publish/brief.json`
- Thumbnail concepts ready for manual selection/editing

## Notes

- **Standalone by design.** Publish is a terminal stage. Nothing reads its outputs programmatically.
- **Transcript JSON is kept.** Queried for chapters, thumbnail moments, key quotes, and available for future use.
- **Content brief is the hand-off.** Downstream marketing work reads `brief.json` — no one should have to guess from the transcript when the brief already exists.
- **Graceful degradation.** No thesis? Ask. No Google API key? Skip thumbnail generation. No keyterms? Transcribe without them.
