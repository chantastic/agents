# Rough Cut Skill - Session Context

## Dependencies (in nix config)
- `whisper-cpp` (binary: `whisper-cli`)
- `ffmpeg`
- Model at `~/.whisper/models/ggml-large-v3-turbo.bin`

## FCPXML Critical Learnings
- Use FCPXML 1.13 for FCP 11.x
- No `/` in names
- Times as fractions: `frames/30s`
- Asset must have `<media-rep>` child
- Chapter markers REQUIRE `posterOffset` to avoid crash

## Remaining Issues
- Some duplicate sentences still getting through take detection
- Low volume areas not being cut (may need content-based detection)
