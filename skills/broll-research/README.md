# B-Roll Research Skill

Autonomous research skill that analyzes video transcripts and collects b-roll assets (logos, screenshots, social media posts, videos) for video editing.

## Quick Start

1. **Enter the nix-shell** (one-time per session):
   ```bash
   cd ~/skills/broll-research
   nix-shell
   ```

2. **One-time setup**: Download spaCy model:
   ```bash
   cd ~/.spacy/data
   wget https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0.tar.gz
   tar -xzf en_core_web_sm-3.8.0.tar.gz
   ```

3. **Use the skill**:
   ```bash
   # From within nix-shell
   claude-code /broll-research --transcript /path/to/transcript.json
   ```

## Architecture

- **Main Skill**: `SKILL.md` - Orchestrates parallel agents
- **Sub-Agents**: `agents/*.md` - Specialized collectors
  - `entity-extractor` - Extract proper nouns with spaCy NER
  - `logo-collector` - Download company/product logos
  - `screenshot-collector` - Capture website screenshots (Playwright)
  - `social-collector` - Screenshot social media posts
  - `video-collector` - Download YouTube clips (yt-dlp)
  - `marker-generator` - Generate FCPXML chapter markers
- **Scripts**: `scripts/*.py` - Python utilities
- **Environment**: `shell.nix` - Nix development environment

## Dependencies (via nix-shell)

All dependencies are managed via Nix:
- Python 3.12 with spaCy
- yt-dlp (YouTube downloads)
- ffmpeg (video processing)
- Bun + Playwright (browser automation)
- wget, jq, xmllint (utilities)

## Output

Creates a `broll-research/` directory with:
```
broll-research/
├── entities.json          # Extracted entities with timestamps
├── assets/
│   ├── logos/            # Company/product logos
│   ├── screenshots/      # Website screenshots
│   ├── social/           # Social media post screenshots
│   └── videos/           # YouTube video clips
├── markers.fcpxml        # FCPXML chapter markers
└── research_log.md       # Human-readable report
```

## Testing

Test entity extraction:
```bash
nix-shell ~/skills/broll-research/shell.nix --run \
  "python3 ~/skills/broll-research/scripts/extract-entities.py /tmp/audio_for_whisper.wav.json /tmp/entities.json"
```

## Notes

- Model path: `~/.spacy/data/en_core_web_sm-3.8.0/`
- All commands must run within nix-shell
- Agents spawn in parallel for performance
- Graceful fallbacks if tools unavailable
