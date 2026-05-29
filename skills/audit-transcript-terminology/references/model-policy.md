# Model Policy

Terminology auditing benefits from a modern reasoning model because the task requires distinguishing likely ASR errors from valid spoken wording.

## Preferred capabilities

Required for full audit mode:

- strong reasoning
- reliable structured JSON output
- long-context handling, or safe chunking
- low-temperature, conservative behavior
- ability to cite local evidence

Recommended settings:

- temperature: `0–0.2`
- reasoning: `medium` or higher when available
- output: strict JSON conforming to schema

## Model preference ladder

Use this resolution order:

1. explicit user override
2. skill preferred model
3. skill fallback list
4. harness/user default model
5. fail or run review-only if requirements are not met

Current preferred class:

- `openai:gpt-5.1` or successor strong reasoning model
- `anthropic:claude-sonnet-4.5` or successor
- `google:gemini-2.5-pro` or successor

The exact provider is less important than meeting the capabilities above.

## When to degrade

If the available model cannot reliably emit schema-valid JSON:

- do not apply corrections automatically
- produce a human-readable review list instead, or ask to switch models

If the context window is too small:

- chunk by utterance/cue boundaries
- preserve global glossary and topic in every chunk
- merge corrections deterministically

If confidence is low:

- put item in `needs_review`
- do not inflate confidence to satisfy the schema

## Harness portability

The skill may declare preferred models, but the harness owns actual model availability and user preference.

Do not hardcode a provider-specific call inside the skill. Provider-specific logic belongs in a service, extension, or harness adapter.
