---
name: get-broll-assets
description: Research and collect b-roll assets from video transcripts. Extracts entities (companies, products, people) and downloads logos, screenshots, social media posts, and videos. Generates FCPXML markers for video editing. Use when preparing b-roll for a video project.
---

# B-Roll Research

This is a transformation skill. It takes transcript/context inputs and produces a b-roll asset package plus timeline markers.

Research and collect b-roll assets from a video transcript. Extracts entities, collects visual assets, and generates timeline markers.

> **Status:** Experimental / non-canonical. This skill is kept as a standalone workflow and is **not** part of the current canonical `run-video-pipeline` contract. If revived later, its project layout should be standardized before re-integrating it.

## Prerequisites

- `yt-dlp` — for video downloads
- `ffmpeg` — for media processing
- Playwright (via Bun) — for screenshots. If unavailable, skip screenshot/social collection and note it.

For screenshot and social media collection, the nix-shell in this skill directory provides Bun + Playwright:
```bash
nix-shell ~/.agents/skills/get-broll-assets/shell.nix
```

## Process

### Step 1: Locate Transcript

Check for a transcript in the current directory:
1. `transcript.json` (from cut-video skill / Deepgram)
2. Any `.json` file with `utterances` or `words` keys
3. Ask the user for the path

The transcript can be either:
- **Deepgram format** (preferred): has `utterances`, `words`, `paragraphs`
- **Whisper format** (legacy): has `transcription` array with `text` and `offsets`

### Step 2: Extract Entities

Read the transcript and extract entities directly. Do NOT use spaCy or external NER — you are better at this.

From the transcript text, identify:
- **Companies/Products**: OpenAI, WorkOS, AuthKit, Docker, etc.
- **People**: Named individuals mentioned
- **Technologies**: Languages, frameworks, tools (TypeScript, Vim, Kubernetes)
- **Websites**: Domains mentioned (workos.com, agentskills.io)

For each entity, record:
- Name (properly cased)
- Type (ORG, PERSON, PRODUCT, TECH, WEBSITE)
- First mention timestamp (from utterance/word timestamps)
- Mention count
- Context (the sentence where it first appears)

Write to `get-broll-assets/entities.json`:
```json
[{
  "name": "WorkOS",
  "type": "ORG",
  "first_mention_seconds": 1045.3,
  "mention_count": 5,
  "context": "So we'll say what does WorkOS do? workos.com, it's a company that I work at."
}]
```

Rank by mention count × relevance. Focus on the top 10-15 entities.

### Step 3: Create Working Directory

```
get-broll-assets/
├── entities.json
├── assets/
│   ├── logos/
│   ├── screenshots/
│   ├── social/
│   └── videos/
├── markers.fcpxml
└── report.md
```

### Step 4: Collect Assets

For each entity (top 10-15 by relevance), collect:

**Logos** — Search and download:
- Follow `agents/logo-collector.md` for detailed instructions
- Prefer SVG/PNG with transparency from official sources
- Save as `assets/logos/{slug}.png`

**Screenshots** — Capture websites (requires nix-shell for Playwright):
- Follow `agents/screenshot-collector.md`
- Capture official website, product page, or landing page
- Save as `assets/screenshots/{slug}.png`

**Social media** — Capture posts (requires nix-shell for Playwright):
- Follow `agents/social-collector.md`
- Find official Twitter/X or LinkedIn accounts
- Save as `assets/social/{slug}_twitter.png`

**Videos** — Download clips with yt-dlp:
- Follow `agents/video-collector.md`
- Find official YouTube channels, product demos
- Save as `assets/videos/{slug}.mp4`

Run collection tasks in parallel where possible. Skip any that fail and continue.

### Step 5: Generate Timeline Markers

Generate an FCPXML file with chapter markers for each entity's first mention.

Each marker should have:
- Start time at the entity's `first_mention_seconds`
- Label: entity name + asset type
- Note: relative path to the collected asset

Use `~/.agents/services/timeline.py` concepts but for markers specifically, generate FCPXML directly since OTIO marker support varies by adapter.

Save as `get-broll-assets/markers.fcpxml`.

### Step 6: Generate Report

Write `get-broll-assets/report.md`:

```markdown
# B-Roll Research Report
Generated: {date}
Transcript: {transcript_path}

## Summary
- Entities extracted: {count}
- Assets collected: {total}
  - Logos: {n}, Screenshots: {n}, Social: {n}, Videos: {n}

## Entities

### {Entity Name} ({type})
- Mentions: {count}, First at: {timestamp}
- Assets: {list of collected files}

## Missing Assets
- {Entity}: {what couldn't be found}

## Next Steps
1. Review assets in get-broll-assets/assets/
2. Import markers.fcpxml into Final Cut Pro alongside your video timeline
3. Markers show where each entity appears — add b-roll at those points
```

### Step 7: Report to User

Summarize what was collected, what's missing, and the paths to all outputs.

## Notes

- Entity extraction is done by the LLM reading the transcript — no spaCy, no NER library needed.
- The Deepgram transcript (from cut-video) has better text quality (smart formatting, proper nouns) than whisper, making entity extraction more reliable.
- Screenshot and social collection require Playwright via nix-shell. If unavailable, skip those and note it in the report.
- All asset paths in markers are relative to the get-broll-assets directory.
