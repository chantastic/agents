# Captioner

V1 pipeline:

```txt
audio/video -> Deepgram JSON -> Anthropic terminology audit -> corrected Deepgram JSON -> YouTube-ready SRT
```

Credentials are read only from 1Password:

- `thechans.1password.com: op://Private/Deepgram API Key/credential`
- `workos.1password.com: op://Employee/Anthropic API Key/credential`

## Run

```bash
~/.agents/agents/captioner/services/captioner.py run input.mp4 \
  --topic "MCP Night" \
  --glossary "MCP,AAIF,Cloudflare,Claude Code"
```

Outputs are written beside the input by default:

```txt
input.deepgram.json
input.term-audit.json
input.deepgram.corrected.json
input.srt
```

Use existing transcript/audit:

```bash
captioner.py run input.mp4 --skip-transcribe --skip-audit
```
