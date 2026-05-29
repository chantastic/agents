# Transcript Terminology Correction Contract

This contract defines what counts as a valid terminology correction.

## Goal

Identify likely ASR terminology errors in a transcript while preserving timing, meaning, and evidentiary integrity.

The output is a reviewable patch set, not a rewritten transcript.

## Valid corrections

A correction is valid when it fixes a domain-relevant term and is supported by context.

Common categories:

- `company_name` — Anthropic, Cloudflare, Datadog, Linux Foundation, WorkOS
- `product_name` — Chrome DevTools, Convex, Clerk
- `project_name` — MCP, Kubernetes, React
- `person_name` — a named speaker or referenced person
- `technical_term` — Model Context Protocol, source maps, edge runtime
- `acronym` — MCP, API, SDK, CLI
- `capitalization` — `devtools` → `DevTools`, `javascript` → `JavaScript`
- `spacing_punctuation` — `work OS` → `WorkOS`, `next.js`/`Next JS` → `Next.js`

## Invalid corrections

Do not change text merely to improve readability.

Invalid changes include:

- grammar correction
- style editing
- filler-word removal
- trimming repetitions
- making captions shorter
- changing casual wording into formal wording
- adding words not implied by the transcript
- replacing a generic phrase with a branded term without evidence
- changing meaning to match what the reviewer expected the speaker to say

## Evidence standard

Each correction needs at least one evidence source:

1. explicit glossary entry
2. filename/title/topic
3. context file
4. repeated usage elsewhere in the same transcript
5. strong local semantic evidence
6. known public identity of the speaker/interview/topic

When evidence is weak, place the item in `needs_review`, not `accepted`.

## Confidence guide

- `0.95–1.00`: nearly certain; exact term is in glossary/title/context and original is implausible.
- `0.85–0.94`: strong; local/context evidence supports correction.
- `0.70–0.84`: plausible but needs review.
- `<0.70`: usually omit unless useful as a note.

Default auto-accepted threshold: `0.85`.

## Span rules

Prefer exact local spans.

For timestamped formats:

- include `start` and `end` if available
- include cue/utterance/word index when available
- quote the exact original string
- keep replacement as short as practical

Avoid global replacement unless every occurrence is independently safe. If suggesting a recurring correction, still list occurrences or include a clearly marked `global_candidate` requiring review.

## Preservation rules

Corrections must preserve:

- timing
- speaker intent
- word order, unless correcting a multi-token term
- surrounding punctuation where possible
- raw transcript as a separate artifact

## Examples

Good:

```json
{
  "original": "Anthropocene",
  "corrected": "Anthropic",
  "category": "company_name",
  "confidence": 0.98,
  "reason": "Filename says Anthropic; speaker is co-creator of MCP at Anthropic."
}
```

Good:

```json
{
  "original": "chrome dev tools",
  "corrected": "Chrome DevTools",
  "category": "product_name",
  "confidence": 0.96,
  "reason": "Filename and topic identify Chrome DevTools."
}
```

Bad:

```json
{
  "original": "it's been a quite a wild ride",
  "corrected": "it's been quite a wild ride",
  "reason": "Cleaner grammar"
}
```

Bad because it is grammar cleanup, not terminology correction.
