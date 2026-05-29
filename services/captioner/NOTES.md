# Captioner Notes

## Current shape

`captioner` is currently a local service:

```txt
~/.agents/services/captioner/
```

It runs:

```txt
video/audio
  -> Deepgram JSON
  -> Anthropic terminology audit
  -> corrected Deepgram JSON
  -> YouTube-ready SRT
```

Outputs are written beside the input by default:

```txt
input.deepgram.json
input.term-audit.json
input.deepgram.corrected.json
input.srt
```

## Key realization

The service is useful for reliable execution, but the real value of an agent is follow-up interaction.

A CLI can log uncertain terms:

```txt
needs review:
  - NCP -> MCP
  - AIF -> AAIF
```

An agent can ask:

> I found two likely `NCP -> MCP` corrections. Apply both?

Then it can update the audit JSON, rerun apply, and regenerate captions.

## Working distinction

```txt
service = reliable execution
agent = interactive judgment around uncertainty
skill = reusable instructions for the LLM
```

For captioner:

```txt
~/.agents/services/captioner/   # executable deterministic pipeline
~/.agents/skills/captioner/     # future Pi/LLM-facing interactive wrapper
```

The service should stay dumb and safe. The skill/agent layer should handle conversation and judgment.

## Future agent wrapper responsibilities

A future `captioner` skill or Pi extension should:

1. Ask for missing topic/glossary when helpful.
2. Suggest likely glossary terms from filename/transcript.
3. Run the service.
4. Read `input.term-audit.json`.
5. Summarize accepted corrections and `needs_review` items.
6. Ask the user to approve uncertain corrections.
7. Update `term-audit.json` based on answers.
8. Rerun:

```bash
captioner run <input> --skip-transcribe --skip-audit
```

9. Report final artifacts.

## Useful follow-up questions

- "I found `NCP -> MCP` twice. Context strongly suggests MCP. Apply both?"
- "Is `AIF` supposed to be `AAIF` / Agentic AI Foundation?"
- "Should `workers` be capitalized as `Workers` in this Cloudflare context?"
- "I found a likely grammar/transcript issue outside terminology scope. Ignore or review manually?"

## Do not move this into low-level services

Do not make `deepgram_transcribe.py`, `anthropic_audit.py`, `transcript_terms.py`, or `transcript_captions.py` interactive.

Keep them scriptable and deterministic.

Put interactivity in a wrapper skill/agent/extension.

## Possible implementation paths

### Minimal Pi skill wrapper

Create:

```txt
~/.agents/skills/captioner/SKILL.md
```

The skill loads when the user asks to caption/transcribe a video. It runs the `captioner` CLI and performs the review loop by editing the audit JSON.

### Pi extension

Create a Pi extension if we want native commands/tools:

```txt
/captioner <file>
```

or a structured UI for accepting/rejecting corrections.

### Keep service canonical

Even if an agent wrapper is added, keep the service as the canonical executor:

```txt
captioner run input.mp4 --topic "..." --glossary "..."
```
