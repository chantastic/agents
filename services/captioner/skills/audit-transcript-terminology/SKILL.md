---
name: audit-transcript-terminology
description: Conservative post-transcription audit for domain terminology, product names, people, acronyms, and technical phrases that may have been misrecognized. Use after transcription when JSON/SRT/plain transcripts need terminology review before captions, publishing, or downstream video workflows.
role: transformation
metadata:
  model_policy:
    preferred:
      - openai:gpt-5.1
    fallbacks:
      - anthropic:claude-sonnet-4.5
      - google:gemini-2.5-pro
      - user_default
    requirements:
      reasoning: true
      structured_outputs: true
      context_window_min: 32000
---

# Audit Transcript Terminology

This is a transformation skill. It reviews a machine transcript for likely domain-terminology transcription errors and produces a conservative, reviewable correction audit. It does not rewrite the transcript for style.

Primary output is a patch set. Corrected transcripts are derived artifacts.

## Inputs

| Input | Required | Discovery | Description |
|---|---:|---|---|
| transcript | yes | ask/discover | Path to transcript file. Supports Deepgram JSON, Whisper-like JSON, SRT, or plain text. |
| topic | no | infer/suggest | Subject of the recording, e.g. `MCP at Anthropic`, `Chrome DevTools`, `Datadog`. |
| glossary | no | suggest | Domain terms, products, names, acronyms, APIs, companies, projects. |
| context_files | no | discover | Related notes, title, description, script, README, event page, or brief. |
| output | no | default | Correction audit JSON path. Default: sibling file ending `.term-audit.json`. |
| min_confidence | no | default | Minimum confidence for applying automatically. Default: `0.85`; still report lower-confidence candidates separately. |

If no transcript is provided, look for likely transcripts in the working directory first, then common operator locations such as `~/Downloads`. Prefer files named `*.transcript.json`, `transcript.json`, or `*.srt`. Ignore unrelated JSON files such as OAuth `client_secret*.json`.

## Outputs

Primary:

| Output | Description |
|---|---|
| `*.term-audit.json` | Reviewable correction patch set conforming to `schemas/corrections.schema.json`. |

Optional derived outputs when a tool/service exists:

| Output | Description |
|---|---|
| `*.corrected.json` | Transcript JSON with accepted corrections applied while preserving timing. |
| `*.corrected.srt` | SRT captions regenerated or patched from accepted corrections. |

Do not overwrite the raw transcript. Preserve it as evidence.

## Model policy

Use a strong reasoning model with reliable structured JSON output. Prefer the model configured in frontmatter when available. If unavailable, use the harness/user default only if it can follow the schema and correction contract.

If the available model is weak at structured output or long-context reasoning, run in review-only mode and avoid automatic application.

See `references/model-policy.md`.

## Correction contract

Read `references/correction-contract.md` before auditing.

In short:

- Correct terminology, not prose.
- Preserve timestamps and meaning.
- Prefer false negatives over false positives.
- Emit uncertainty instead of guessing.
- Never silently rewrite full transcript text.

Valid correction types include:

- product/company/project names: `Anthropocene` → `Anthropic`, `work OS` → `WorkOS`
- technical acronyms and capitalization: `m c p` → `MCP`, `next j s` → `Next.js`
- APIs/frameworks/libraries: `model context protocol`, `DevTools`, `Kubernetes`
- people names when context makes them clear
- common domain phrases misheard by ASR

Invalid correction types:

- grammar cleanup
- filler removal
- shortening captions
- changing speaker intent
- replacing casual speech with formal prose
- speculative additions not grounded in transcript/context

## Procedure

1. **Load the transcript**
   - Inspect structure and identify format.
   - For Deepgram JSON, use `utterances`, `words`, and `paragraphs` when available.
   - For SRT, use cue number, start/end, and cue text.

2. **Gather topic context**
   - Use provided topic/glossary/context files.
   - If absent, infer a tentative topic from filename and opening transcript.
   - Ask the operator for topic/glossary only when ambiguity would materially change corrections.

3. **Build candidate glossary**
   - Include provided glossary.
   - Add obvious proper nouns from filename, context, and transcript.
   - Add likely domain terms from context, but do not treat inferred terms as guaranteed.

4. **Audit conservatively**
   - Work in chunks if transcript is long.
   - For each suspected error, capture local context and exact source location.
   - Prefer span-local corrections over global replacements.
   - Flag recurring patterns, but still list concrete affected spans.

5. **Validate corrections**
   - Correction must be supported by topic/glossary/context or strong local evidence.
   - Original text must appear at the cited location or be reconstructable from adjacent words.
   - Corrected text must preserve the spoken meaning.
   - Assign confidence.

6. **Write audit JSON**
   - Follow `schemas/corrections.schema.json`.
   - Include `accepted`, `needs_review`, and `rejected_or_ignored` sections.
   - Include summary counts and model/policy metadata.

7. **Report concisely**
   - Show output path.
   - Summarize high-confidence corrections and review-needed items.
   - Mention if no safe corrections were found.

## Output shape

Write JSON like:

```json
{
  "version": "1.0",
  "source": {
    "path": "/Users/chan/Downloads/example.transcript.json",
    "format": "deepgram-json"
  },
  "context": {
    "topic": "MCP at Anthropic",
    "glossary": ["MCP", "Anthropic", "Model Context Protocol"]
  },
  "summary": {
    "accepted_count": 1,
    "needs_review_count": 1,
    "rejected_or_ignored_count": 0
  },
  "accepted": [
    {
      "id": "corr_001",
      "start": 4.88,
      "end": 5.92,
      "location": { "kind": "srt_cue", "cue": 2 },
      "original": "Anthropocene",
      "corrected": "Anthropic",
      "category": "company_name",
      "confidence": 0.98,
      "reason": "Filename and topic indicate Anthropic; 'Anthropocene' is a likely ASR substitution."
    }
  ],
  "needs_review": [],
  "rejected_or_ignored": []
}
```

## Example transcripts

Known local examples currently exist in `~/Downloads`:

- `David Parra - Co-Creator MCP_Anthropic_v3_trimmed.srt`
- `David Parra - Co-Creator MCP_Anthropic_v3_trimmed.transcript.json`
- `Paul Irish - Chrome Devtools_v3 - edit.srt`
- `Paul Irish - Chrome Devtools_v3 - edit.transcript.json`
- `Rita Kozlov - Vp Product Cloudflare_v3.srt`
- `Jim Zemlin - CEO_Linux Foundation_v3 - edit.transcript.json`

Use these as calibration material, not as hardcoded assumptions.
