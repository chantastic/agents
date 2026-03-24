---
name: broll-research
description: Research and collect b-roll assets from video transcripts. Extracts entities (companies, products, people) and downloads logos, screenshots, social media posts, and videos. Generates FCPXML markers for video editing. Use when preparing b-roll for a video project.
---

# B-Roll Research Skill

Research and collect b-roll assets from video transcripts. Extracts entities (companies, products, people) and downloads logos, screenshots, social media posts, and videos. Generates FCPXML markers for video editing.

## IMPORTANT: Development Environment

**This skill requires running all commands within a nix-shell environment.**

All dependencies (Python/spaCy, yt-dlp, ffmpeg, Bun/Playwright, jq, xmllint) are managed via `shell.nix` in the skill directory.

**Before executing ANY command**, enter the nix-shell:
```bash
cd ~/skills/broll-research
nix-shell
```

OR wrap individual commands with:
```bash
nix-shell ~/skills/broll-research/shell.nix --run "COMMAND_HERE"
```

The nix-shell provides an isolated, reproducible environment with all required tools.

## Overview

This skill orchestrates multiple specialized agents to:
1. Extract entities (companies, products, people) from transcripts
2. Collect assets in parallel (logos, screenshots, social media, videos)
3. Generate FCPXML chapter markers linking assets to timeline positions
4. Produce a human-readable research report

## Workflow

### Phase 1: Setup and Validation

1. **Determine transcript location**:
   - If user provides `--transcript` path, use that
   - Otherwise, look for `/tmp/audio_for_whisper.wav.json` (from recent rough-cut run)
   - Validate transcript file exists and is valid JSON

2. **Determine working directory**:
   - If transcript is in `/tmp/`, ask user where to create `broll-research/` directory
   - Otherwise, create `broll-research/` as sibling to transcript file
   - Create directory structure:
     ```
     broll-research/
     ├── entities.json
     ├── assets/
     │   ├── logos/
     │   ├── screenshots/
     │   ├── social/
     │   └── videos/
     ├── markers.fcpxml
     └── research_log.md
     ```

3. **Enter nix-shell environment**:
   ```bash
   cd ~/skills/broll-research
   nix-shell
   ```

   This loads all dependencies (Python/spaCy, yt-dlp, ffmpeg, Bun, jq, xmllint).

   **CRITICAL**: All subsequent commands in this skill MUST be run within the nix-shell.

4. **Validate spaCy model**:
   ```bash
   python3 -c "import spacy; from pathlib import Path; model_path = Path.home() / '.spacy' / 'data' / 'en_core_web_sm-3.8.0' / 'en_core_web_sm' / 'en_core_web_sm-3.8.0'; spacy.load(str(model_path))"
   ```

   If model not found, instruct user to download it (one-time setup):
   ```bash
   cd ~/.spacy/data
   wget https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0.tar.gz
   tar -xzf en_core_web_sm-3.8.0.tar.gz
   ```

### Phase 2: Entity Extraction (Sequential)

**Run entity extraction**:
- Use the Python script `scripts/extract-entities.py` with spaCy NER
- Pass transcript path and output path (`./broll-research/entities.json`)
- **All commands must run via nix-shell**: Wrap with `nix-shell ~/skills/broll-research/shell.nix --run "COMMAND"`
- **Wait for completion** before proceeding (output needed for next phase)

**Expected output**: `entities.json` with format:
```json
[{
  "name": "OpenAI",
  "type": "ORG",
  "first_mention_ms": 8120,
  "mention_count": 5,
  "relevance_score": 10,
  "context": "and then OpenAI released ChatGPT..."
}]
```

**Validation**: Check that at least 3 entities were extracted. If fewer, warn user that transcript may be too generic for b-roll research.

### Phase 3: Asset Collection (Parallel)

**Run 4 asset collection tasks**:

All tasks use the same inputs:
- Path to `entities.json`
- Output directory (e.g., `./broll-research/assets/`)
- Number of entities to process (recommend: top 10 by relevance_score)

**Tasks** (run in parallel where possible):
1. **Logo collection** → Follow `agents/logo-collector.md` to search and download company/product logos
2. **Screenshot collection** → Follow `agents/screenshot-collector.md` to capture website screenshots using Playwright
3. **Social media collection** → Follow `agents/social-collector.md` to screenshot social media posts (Twitter, LinkedIn)
4. **Video collection** → Follow `agents/video-collector.md` to download YouTube clips with yt-dlp

**Wait for all collection tasks** to complete before proceeding to marker generation.

### Phase 4: FCPXML Marker Generation (Sequential)

**Generate FCPXML markers** by following `agents/marker-generator.md`:
- Pass paths: `entities.json`, `assets/` directory, output `markers.fcpxml`
- Scan assets directories and generate FCPXML chapter markers
- Each marker contains:
  - Start time (from entity's first_mention_ms)
  - Marker label (entity name + asset type)
  - Note with relative path to asset file

**Wait for completion**.

### Phase 5: Research Report Generation

**Generate `research_log.md`**:

Create a human-readable markdown report summarizing the research:

```markdown
# B-Roll Research Report
Generated: {date}
Transcript: {transcript_path}

## Summary
- Entities extracted: {count}
- Assets collected: {total_count}
  - Logos: {logo_count}
  - Screenshots: {screenshot_count}
  - Social media: {social_count}
  - Videos: {video_count}

## Entity Breakdown

### {Entity Name} ({type})
- Mentions: {mention_count}
- First mention: {timestamp}
- Assets:
  - Logo: `./assets/logos/{slug}.png`
  - Screenshot: `./assets/screenshots/{slug}.png`
  - Social: `./assets/social/{slug}_twitter.png`
  - Video: `./assets/videos/{slug}.mp4`

[Repeat for each entity]

## Assets Not Found
- {Entity}: No logo found
- {Entity}: No social media presence

## Next Steps
1. Review assets in `./broll-research/assets/`
2. Import `markers.fcpxml` into Final Cut Pro
3. Markers will show asset locations on timeline
```

### Phase 6: User Report

**Report completion to user**:

```
✓ B-roll research complete!

Entities extracted: 12
Assets collected: 35
  - Logos: 10
  - Screenshots: 12
  - Social media: 8
  - Videos: 5

Output directory: ./broll-research/

Next steps:
1. Review research_log.md for detailed findings
2. Import markers.fcpxml into Final Cut Pro
3. Assets are organized in ./assets/ subdirectories
```

## Error Handling

- **No transcript found**: Guide user to provide `--transcript` path
- **Invalid transcript**: Explain expected Whisper JSON format
- **No entities extracted**: Suggest transcript may be too generic
- **Dependencies missing**: Agents will fallback gracefully (e.g., regex instead of spaCy)
- **Network failures**: Collectors skip failed downloads and continue
- **All collectors fail**: Still generate report showing what was attempted

## Agent Communication Protocol

Agents communicate via file outputs:
- `entities.json` - Shared input for all collectors
- Asset files - Organized by type in subdirectories
- `markers.fcpxml` - Final output for video editor

No inter-agent communication needed - all run independently.

## Performance Expectations

- Entity extraction: ~5-10 seconds
- Asset collection (parallel): ~30-60 seconds (depends on entity count)
- Marker generation: ~2-5 seconds
- Total time: **~45-90 seconds** for 10 entities

## Usage Examples

**Basic usage** (use existing transcript):
```
/skill:broll-research
```

**Specify transcript**:
```
/skill:broll-research --transcript /path/to/transcript.json
```

**Specify output directory**:
```
/skill:broll-research --transcript /tmp/audio.json --output /Users/chan/Videos/project1/
```

## Future Enhancements

- Cache frequently used assets globally (`~/.broll-cache/`)
- Support custom entity lists (user-provided JSON)
- Integration with stock photo APIs (Pexels, Unsplash)
- Automatic marker insertion into rough-cut timeline
- Multi-language support with multilingual spaCy models
