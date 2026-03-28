# Services

Services are thin, standalone CLIs used by skills for I/O, rendering, external APIs, and deterministic transformations.

## Doctrine

Services should be:
- **thin** — wrap one tool, API, or transformation
- **CLI-first** — invokable directly from the shell
- **JSON-friendly** — structured data should go to stdout or explicit files
- **boring** — no editorial judgment, no workflow ownership, no hidden state
- **self-describing** — Python dependencies declared inline via `uv` script metadata

Services are not:
- coordinators
- prompt containers
- business-logic engines
- abstraction layers over multiple backends

## Execution model

Python services use `uv` inline script metadata:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "opentimelineio>=0.18",
# ]
# ///
```

This keeps each service self-contained:
- no global pip install story
- no unclear workspace-wide Python dependency bucket
- no guessing which service needs which package

## Dependency split

### Python dependencies
Declared per service via inline `uv` metadata.

### System dependencies
Provided at the workspace level.

Current shared system dependencies:
- `uv`
- `python3`
- `ffmpeg`
- `ffprobe`
- `yt-dlp`
- `jq`

See `../shell.nix` for the workspace dev shell.

## I/O conventions

- **Structured results** → stdout JSON or explicit output file
- **Human/log output** → stderr
- **Failure** → non-zero exit code
- **Writes** → only when requested by arguments / explicit output paths

## Shared code

Shared helpers are allowed when duplication becomes obvious.

Good:
- tiny helpers for subprocess handling
- common ffprobe wrappers
- JSON read/write helpers
- logging setup

Bad:
- service frameworks
- provider abstraction towers
- generic orchestration layers

Rule: **shared helpers, not shared abstractions**.

## Current migration direction

The workspace is standardizing on:
- Python services
- `uv` inline dependency metadata
- one workspace-level dev shell for system tools

`requirements.txt` is being retired in favor of script-local dependency declarations.
