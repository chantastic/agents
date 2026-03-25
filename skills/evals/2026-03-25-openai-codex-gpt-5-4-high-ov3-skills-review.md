# Eval: Skills Workspace Review

**Date**: 2026-03-25  
**Reviewer**: OpenAI API coding assistant  
**Model**: `openai-codex-gpt-5-4-high`  
**Settings**: response style `OV=3` (concise), no temperature/top_p exposed  
**Scope**: review of `~/.agents/skills` and existing skill-local `evals/`

---

## Summary

This is a strong skills workspace. The best parts are practical, opinionated, and obviously shaped by real runs rather than imagined use. The video pipeline stack is the center of gravity: strong artifact discipline, clean stage separation, and real learning loops through stored evals.

The main risk is **contract drift** across skills: schemas, paths, expectations, and stage boundaries are mostly clear in your head but not always synchronized in the prompts. The evals are high quality, but some lessons have not fully propagated back into all skill docs. The repo is now limited more by consistency and calibration management than by raw prompt quality.

---

## What looks strong

### 1. Artifact discipline

The strongest architectural pattern in the repo is:
- `manifest.json` as contract
- transcript as source of truth
- decisions as source
- edit lists as compiled artifacts
- evals stored with the skill, not the project

This is unusually good. It gives you resumability, inspectability, and learning over time.

### 2. Prompts reflect real scar tissue

The best skills read like operational doctrine, not framework theater. Especially:
- `video-pipeline/SKILL.md`
- `video-cut/SKILL.md`
- `video-polish/SKILL.md`
- `video-zoom/SKILL.md`
- `youtube-upload/SKILL.md`

### 3. Evals are genuinely useful

The evals contain actual diagnosis and calibration data, not generic self-praise. They changed the prompt design. That is the right loop.

### 4. Good separation of durable logic vs tool I/O

The repo generally follows the right split:
- prompts do judgment
- services do I/O

That is one of the healthiest patterns in the workspace.

---

## Main issues / risks

### 1. Contract drift across skills

This is the biggest risk.

Examples:
- `evaluate-skill-output/SKILL.md` references old paths like `cut/decisions.json` and `cut/utterances.txt`, while the current system uses `decisions/cut.json` and root-level `utterances.txt`.
- `video-pipeline/SKILL.md` says `video-publish` is standalone after manual export, but its report section lists `publish/*` outputs as if the pipeline generated them.
- `broll-research/SKILL.md` writes to `broll-research/`, while the pipeline layout reserves `broll/`.
- `video-publish/SKILL.md` expects `speakers` from manifest, but upstream schema examples do not clearly define who writes that field.
- `video-cut/SKILL.md` description/frontmatter still implies rough + editorial cut, while the body moves editorial to polish.

### 2. Evals are rich but mostly prose

The markdown is excellent for human review and LLM context, but weak for cross-run comparison. Several evals already propose structured outputs (`accuracy.json`, `timeline_diff.json`, manifest `eval` keys), but those structures are not yet the standard artifact.

### 3. Risk of overfitting to a flagship project

A lot of the strongest calibration rules come from the Pi first-look videos. Those lessons are useful, but some are genre-conditional rather than universal:
- screen narration is pacing drag
- LLM output narration should be cut
- 3–4 zooms/min
- default to instant punch-ins

These are probably right for this format. They should not quietly become default truth for every future video type.

### 4. Discoverability / metadata unevenness

These lack frontmatter:
- `chan-dev-writing/SKILL.md`
- `make-it-personal/SKILL.md`

`make-it-personal` especially looks like a real skill and would benefit from normal metadata/discovery conventions.

### 5. Sensitive-memory concern

`make-it-personal` stores interviews in the skill directory. That may be exactly what you want, but it is meaningfully different from normal eval storage. If this repo syncs broadly, treat that as deliberate memory retention, not just a prompt artifact.

---

## Different takeaways from existing evals

### The biggest win is architectural, not just editorial

The most important achievement is not “better cuts.” It is the system:
- decision layers
- compile step
- re-transcription as QA
- evals colocated with skills

That is the compounding advantage.

### The repo’s bottleneck is now synchronization, not intelligence

You are already producing good lessons. The weak point is making sure every relevant skill absorbs those lessons cleanly and consistently.

### The remaining hard problems are mostly taste problems

The mechanics are in decent shape. The remaining frontier is:
- editorial aggression
- pacing taste
- zoom taste
- user review UX

That is a good sign.

---

## Priority punch list

### P0 — Fix shared contracts and drift
Create a single authoritative schema / contract doc for the video stack and align all related skills to it.

Includes:
- canonical manifest shape
- canonical directory layout
- canonical source vs artifact rules
- who writes each field (`thesis`, `speakers`, `decisions`, etc.)
- which stages are standalone vs in-pipeline

### P1 — Update stale skill docs to match reality
Patch obvious mismatches in:
- `evaluate-skill-output/SKILL.md`
- `video-pipeline/SKILL.md`
- `video-cut/SKILL.md`
- `broll-research/SKILL.md`
- `video-publish/SKILL.md`

### P2 — Add structured eval artifacts
Keep markdown evals, but add machine-readable sidecars for category counts, accuracy, diffs, and calibration values.

### P3 — Separate durable rules from local calibration
Keep `SKILL.md` focused on durable process. Move layout-specific or project-specific numbers into `evals/` or a dedicated calibration doc.

### P4 — Normalize skill metadata
Add frontmatter / discovery consistency, especially for `make-it-personal`.

### P5 — Decide privacy stance for personal-memory artifacts
Explicitly decide what belongs in skill-local memory vs private local-only storage.

---

## Operator education notes

### Why P0 matters most

As an operator, your biggest scaling problem is not writing a smart prompt. It is preserving a **stable contract** between smart prompts.

A skill system gets expensive when:
- every skill is individually good
- but the shared assumptions between them drift

That causes subtle failures:
- wrong file looked up
- missing field expected downstream
- stage reports promise outputs that do not exist
- eval skill critiques yesterday’s architecture instead of today’s

Prompt quality gives you local wins. Contract quality gives you compound wins.

### The maturity shift you are in

You are no longer proving that skills can do useful work.
You are now in the stage where the operating system around the skills matters:
- contracts
- eval format
- portability boundaries
- memory boundaries
- calibration hygiene

That is a very healthy shift.

---

## Recommended sequence

1. Fix schema / contract drift first
2. Patch stale docs
3. Add structured eval outputs
4. Split durable guidance from calibration
5. Clean up discoverability and privacy edges

---

## Top 3 recommendations

1. Write one canonical schema/contract doc for the video stack
2. Patch the stale skill docs that still reflect older architecture
3. Start emitting structured eval sidecars alongside markdown evals

---

## Closing assessment

These skills look like real operator tools. The quality ceiling is already high. The fastest path upward is not “be smarter.” It is “make the system more legible to itself.”
