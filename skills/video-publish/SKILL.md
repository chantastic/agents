---
name: video-publish
description: Generate publish-ready assets from a final video export. Transcribes the final edit, generates chapters, captions (SRT), title options, thumbnails, and a content brief for downstream platform skills. Use standalone after exporting from your NLE.
---

# Video Publish

Generate publish-ready assets from a final video export.

This skill runs **standalone** — not as part of the video-pipeline. There is a human step between zoom and publish (reviewing in FCP, exporting), so publish is invoked separately. It reads context from the manifest but does not write to it. Its outputs are just files.

## Required Environment

- `DEEPGRAM_API_KEY` — set in environment
- `ffmpeg` and `ffprobe` — installed
- `GOOGLE_API_KEY` — optional (for thumbnail generation via Imagen)
- Python package: `google-genai` — optional (for thumbnails)

## Inputs

Publish needs two things:

1. **A final export** — the `.mp4`/`.mov` the user exported from their NLE
2. **Context** — thesis and keyterms (read from `manifest.json` if available, otherwise ask). Speaker attribution is inferred during this skill from export/context clues, defaulting to `chantastic`, and asking the operator if uncertain.

## Outputs

All outputs go to `publish/`. No manifest update — the files speak for themselves.

```
publish/
├── transcript.json            ← Deepgram JSON (kept for querying: chapters, sentiment, thumbnails)
├── captions.srt               ← subtitles
├── captions.vtt               ← WebVTT version
├── chapters.json              ← chapter data (timestamps, titles, summaries)
├── chapters.txt               ← YouTube-formatted (00:00 Title)
├── titles.json                ← viral title options with reasoning
├── description.md             ← SEO description with chapter markers
├── brief.json                 ← content brief for downstream platform skills
└── thumbnails/
    ├── concepts.json          ← thumbnail concepts with prompts
    ├── moments.json           ← high-energy moments identified from transcript
    ├── frames/                ← extracted frames at emotional peaks
    └── T001.png ... T00N.png  ← generated images (if GOOGLE_API_KEY set)
```

## Process

### Step 1: Locate the final export

Look for the export file. If the user provided a path, use it. Otherwise search:
1. `publish/export.mp4` or `publish/export.mov`
2. `export.mp4` or `export.mov` at project root
3. Any `.mp4`/`.mov` at project root that is NOT the source video

If ambiguous, ask the user.

### Step 2: Read context

If `manifest.json` exists, read:
- `thesis` — guides everything downstream
- `keyterms` — passed to Deepgram for accuracy

Determine `speakers` using this precedence:
1. Infer from the export filename / project title if guest names are obvious
2. Check stream metadata or naming conventions from Restream exports if available
3. Default to `chantastic`
4. If still uncertain, ask the operator

If no manifest, ask the user for a brief description. Only ask for speaker names if they cannot be inferred confidently using the precedence above.

### Step 3: Transcribe

Transcribe the export. The JSON is **kept** — it's queried for chapters (utterance flow), thumbnail moments (sentiment/energy), and the content brief (key quotes).

```bash
DEEPGRAM_API_KEY=<key> python3 ~/.agents/services/transcribe.py "<export_path>" \
  --keyterms "<terms>" \
  --output publish/transcript.json
```

### Step 4: Generate captions (SRT + VTT)

Build captions from the transcript utterances. Split long utterances at ~80 chars on word boundaries.

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

Read the transcript utterances. Identify natural topic boundaries — moments where the conversation shifts subject, demo, or segment.

**Chapter guidelines:**
- First chapter at `00:00` (YouTube requirement)
- Target 5-10 chapters (flexible — fewer for tighter content, more for sprawling conversations)
- Minimum ~2 minutes between chapters
- **Titles are learner outcomes, not topic labels.** Chapters help viewers find answers. Frame titles around what the viewer will learn or be able to do:
  - ✅ "How to Use Claude and GPT in the Same Session"
  - ✅ "Your Claude Code Skills Already Work in Pi"
  - ❌ "Multi-Model Setup and Vendor Lock-In"
  - ❌ "Cross-Agent Skills Discussion"
- Use the thesis to weight titles toward the video's narrative
- For multi-speaker content, topic shifts often align with who's driving

Write `publish/chapters.json`:

```json
{
  "chapters": [
    {
      "time": 0.0,
      "timestamp": "00:00",
      "title": "The AI Burnout Horizon",
      "summary": "The paradox of everything being automatable but feeling like more work.",
      "utterance_range": [0, 14]
    }
  ]
}
```

Write `publish/chapters.txt` — YouTube-ready, paste directly:

```
00:00 The AI Burnout Horizon
01:46 What Is Pi? The NeoVim of Coding Agents
...
```

### Step 6: Generate title options

Generate 5-8 title options. Mix styles:

| Style | Example | Notes |
|---|---|---|
| **Curiosity gap** | "I Switched from Claude Code to This" | Withholds the answer |
| **Confrontational** | "Claude Code Has a Vendor Lock-In Problem" | Takes a stance |
| **How-to** | "How to Use Any AI Model in One Terminal" | Promise of value |
| **Listicle** | "5 Things Pi Does That Claude Code Can't" | Scannable |
| **Emotional** | "Why I'm Worried About Claude Going Public" | Vulnerability |

Write `publish/titles.json`:

```json
{
  "titles": [
    {
      "title": "I Switched from Claude Code to This",
      "style": "curiosity_gap",
      "reasoning": "Pi is unnamed — creates a click incentive. 'Switched' implies conviction."
    }
  ]
}
```

### Step 7: Generate SEO description

Write `publish/description.md`:

1. **Hook** (first 2-3 lines, visible before "show more") — what will the viewer learn?
2. **Summary** — grounded in thesis, mentioning speakers by name
3. **Chapter list** — from `chapters.txt`
4. **Links** — tools, speakers, resources mentioned
5. **Tags/keywords** — extracted from content for SEO

Match the voice of the content — conversational for a livestream, tutorial-style for a how-to.

**Clear is greater than clever. But clever is still great.** If a line is both clear and clever, keep it. If you have to choose, choose clear.

### Step 8: Identify thumbnail moments

Query the transcript JSON for high-energy moments — these produce the most expressive frames.

**Signals of high-energy moments:**
- Reactions and exclamations: "Oh my gosh", "That's wild", "I love that"
- Laughter (often transcribed as short utterances with low confidence or filler)
- Rapid back-and-forth exchanges (short utterance durations in quick succession)
- Emphatic statements: "Is AI our curse? Yes." — confident, declarative
- Reveals and surprises: "And it works!" "shittycodingagent.ai"
- Self-deprecating humor: "aliasing node to bun, which is probably the dumbest way"

Scan all utterances. Score each on energy (reaction words, brevity + confidence, exclamation patterns). Select the top 8-12 moments.

Write `publish/thumbnails/moments.json`:

```json
{
  "moments": [
    {
      "time": 93.9,
      "utterance": "Is AI our curse? Yes.",
      "energy": "high",
      "reason": "Emphatic question + instant deadpan answer. Faces will be expressive."
    },
    {
      "time": 392.0,
      "utterance": "shittycodingagent.ai, that's it too.",
      "energy": "high",
      "reason": "Reveal moment — surprise/delight reaction expected."
    }
  ]
}
```

### Step 9: Extract frames and generate thumbnails

Extract frames at each identified moment:

```bash
mkdir -p publish/thumbnails/frames
ffmpeg -y -ss <seconds> -i "<export_path>" -frames:v 1 -q:v 2 publish/thumbnails/frames/<id>.jpg
```

Read the extracted frames. Design 3-4 thumbnail concepts using the most expressive frames.

Thumbnail principles:
- **Readable at 120×68px**
- **Faces drive clicks** — use the frames where reactions are most visible
- **3-5 words max** — large, high-contrast text
- **Visual tension** — contrast, split compositions
- **Honest** — reflects the actual content

Write `publish/thumbnails/concepts.json` with prompts for each concept.

If `GOOGLE_API_KEY` is set, generate with Imagen:

```python
import google.genai as genai
import os, json

client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])

with open('publish/thumbnails/concepts.json') as f:
    concepts = json.load(f)['concepts']

for concept in concepts:
    response = client.models.generate_images(
        model='imagen-3.0-generate-002',
        prompt=concept['prompt'],
        config=genai.types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio='16:9',
            safety_filter_level='BLOCK_ONLY_HIGH',
        )
    )
    for image in response.generated_images:
        path = f'publish/thumbnails/{concept["id"]}.png'
        with open(path, 'wb') as f:
            f.write(image.image.image_bytes)
        print(f'Generated: {path}')
```

If no API key, skip generation — concepts JSON provides prompts for manual creation.

### Step 10: Generate content brief

The content brief is the hand-off to downstream platform skills (`content-linkedin`, `content-twitter`, `content-recap`). It distills the transcript into a queryable summary they can read without processing the full transcript.

Write `publish/brief.json`:

```json
{
  "thesis": "...",
  "speakers": { ... },
  "duration": "48:50",
  "chapters": [ ... ],
  "key_quotes": [
    {
      "quote": "If Claude Code is Visual Studio Code, then Pi is NeoVim.",
      "speaker": "Nick Nisi",
      "time": 141.0,
      "context": "Core analogy explaining Pi's positioning"
    }
  ],
  "key_moments": [
    {
      "moment": "Nick reveals he aliased node to bun",
      "time": 427.0,
      "energy": "comedic",
      "quote": "This is so dumb. Don't be like me."
    }
  ],
  "topics": ["Pi", "Claude Code", "vendor lock-in", "multi-model orchestration", "evals", "Case tool"],
  "links": {
    "Pi": "https://pi.dev",
    "shittycodingagent.ai": "https://shittycodingagent.ai"
  },
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
| Thumbnails | `publish/thumbnails/` | Moments + frames + concepts + generated |
| Content brief | `publish/brief.json` | Hand-off for platform skills |

Remind user:
- Review titles and chapters before uploading
- Run `content-linkedin`, `content-twitter`, `content-recap` skills using `publish/brief.json` for platform posts
- Thumbnail concepts are ready for manual selection/editing

## Notes

- **No manifest write.** Publish is a terminal stage — nothing reads its outputs programmatically. The files are the deliverables.
- **Transcript JSON is kept.** It's queried for chapters (utterance flow), thumbnail moments (sentiment/energy), key quotes (content brief), and is available for any future querying. SRT is generated from it, not instead of it.
- **Standalone invocation.** Not chained in the pipeline. Human step (NLE review + export) between zoom and publish.
- **Content brief is the hand-off.** Downstream platform skills (`content-linkedin`, `content-twitter`, `content-recap`) read `brief.json` — they don't need to process the full transcript.
- **Graceful degradation.** No manifest? Ask for context. No Google API key? Skip thumbnail generation, keep the concepts. No export? Use the polished preview.
