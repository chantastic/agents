# System-Level Eval: Operator Uplift Session

**Date**: 2026-03-25  
**Reviewer / Collaborator**: `openai-codex-gpt-5-4-high`  
**Settings**: `OV=3`  
**Scope**: Workspace-level operator review and follow-through across contracts, evals, calibration hygiene, and cross-skill doctrine

---

## Summary

This session was not a skill run review. It was a **system review**.

The main shift was from improving individual prompts to improving the **operating system around the prompts**:
- define contracts
- align docs to contracts
- make evals compound
- separate durable rules from calibration
- articulate the collaboration model between operator and agent

The outcome of the session was a meaningful operator uplift. The workspace now has clearer truth boundaries, a stronger eval loop, a first tiny aggregator over eval sidecars, and a new `OPERATING_PRINCIPLES.md` file for cross-skill philosophy.

---

## What changed during the session

### P0 — Canonical contract for the active video workflow

Created a single source of truth in:
- `skills/video-pipeline/SCHEMA.md`

Key decisions:
- active automated pipeline is `video-cut -> video-polish -> video-zoom`
- `video-publish` is post-handoff and standalone
- `speakers` should not be required upstream; infer later near publish
- b-roll is removed from the canonical active contract for now
- operator handoff between zoom and publish is explicit

### P1 — Truth alignment across skills

Patched skill docs so the prompts match the current architecture:
- `skills/evaluate-skill-output/SKILL.md`
- `skills/video-pipeline/SKILL.md`
- `skills/video-cut/SKILL.md`
- `skills/video-publish/SKILL.md`
- `skills/broll-research/SKILL.md`

Main effect:
- reduced contract drift
- removed misleading stage/output language
- clarified metadata ownership and experimental status

### P2 — Structured eval sidecars

Added paired eval artifacts:
- `.md` = narrative memory
- `.json` = operational memory

Created:
- `skills/evaluate-skill-output/SCHEMA.md`
- JSON sidecars for all current evals
- `services/evals.py` as a tiny aggregator

Main effect:
- evals became queryable, not just readable
- recurring issue categories and recommendation targets can now be summarized across runs

### P3 — Separate durable rules from calibration

Patched:
- `skills/video-cut/SKILL.md`
- `skills/video-polish/SKILL.md`
- `skills/video-zoom/SKILL.md`

Main effect:
- core skills now distinguish:
  - principle
  - heuristic
  - preference
  - temporary calibration
- exact numbers and current operator taste are now more clearly framed as belonging in `evals/`

### System-level doctrine

Created:
- `OPERATING_PRINCIPLES.md`

Linked from:
- `AGENTS.md`

Main effect:
- the workspace now has a philosophy layer, distinct from runtime instructions and domain contracts

---

## Most important conceptual takeaways

### 1. The operator owns intent. The agent owns execution.

This became the clearest articulation of the collaboration model.

The operator owns:
- direction
- taste
- publication decisions
- acceptable risk

The agent owns:
- execution within scope
- synthesis across artifacts
- structure, auditability, and memory
- surfacing uncertainty when it matters

This is the center of gravity for the workspace.

### 2. Human intervention is part of the system, not a failure of the system.

The session sharpened the idea that handoffs should be modeled explicitly.

Editing in FCP, final review, and publication are not awkward automation gaps. They are meaningful operator boundaries.

### 3. Contracts matter more than local cleverness once the workflow is real.

The workspace has crossed the threshold where the main risk is no longer one bad prompt decision. The bigger risk is cross-skill confusion caused by drift in:
- paths
- stage boundaries
- metadata ownership
- reports that imply outputs that do not yet exist

### 4. Narrative memory and operational memory are both required.

This became the guiding principle for evals:
- markdown explains meaning
- json sidecars make meaning countable

### 5. Not every successful lesson deserves promotion to doctrine.

This was the philosophical heart of the later part of the session.

The operator wanted language to distinguish:
- principle
- heuristic
- preference
- temporary calibration

That distinction became the backbone of P3 and the new principles doc.

---

## Patterns surfaced by the session

### Pattern: the workspace is maturing from prompts into an operating system

The conversation repeatedly returned to:
- contracts
- doctrine
- calibration boundaries
- memory systems
- handoffs

That indicates a healthy maturity shift. The workspace is no longer proving that skills can work. It is now deciding how those skills should coexist and learn.

### Pattern: the video workflow is the proving ground for general workspace ideas

Many of the strongest lessons came from the video skills, but the resulting concepts were broader:
- source vs compiled artifacts
- eval colocation
- handoff modeling
- doctrine vs calibration
- operator-visible uncertainty

### Pattern: explicit philosophy reduces accidental overfitting

Before this session, some strong and useful heuristics were starting to sound like universal law. The session corrected that by giving the system a language for levels of certainty.

---

## Highest-value phrases / formulations from the session

These feel worth preserving because they capture the workspace philosophy succinctly:

- **The operator owns intent. The agent owns execution.**
- **Human intervention is part of the system, not a failure of the system.**
- **Truth should live where the best evidence exists.**
- **Contracts matter more than local cleverness.**
- **Structure the counts. Narrate the meaning.**
- **The system should encode the kind of certainty it has.**
- **Not every successful lesson deserves promotion to doctrine.**
- **Learn at the right level.**

---

## What feels most important to revisit later

### 1. Promotion path: when does a lesson graduate?

This is probably the next big philosophical question.

A future version of `OPERATING_PRINCIPLES.md` may want an explicit section on how lessons move from:
- eval
- to skill heuristic
- to cross-skill doctrine
- to `AGENTS.md`

### 2. Ask / infer / default as a first-class rubric

This emerged strongly but is not yet fully promoted into the top-level runtime constitution. It may deserve to become one of the main cross-skill collaboration rules.

### 3. Operator handoff as a reusable pattern

This currently exists strongly in the video workflow, but it may become a broader workspace pattern. If so, it should eventually be named more explicitly and reused outside video.

### 4. Which principles belong in `AGENTS.md` vs `OPERATING_PRINCIPLES.md`

This split now exists, but the long-term boundary still needs lived experience.

---

## Recommendations

1. **Live with `OPERATING_PRINCIPLES.md` before promoting more into `AGENTS.md`.**
   Let the doctrine be pressure-tested by real use.

2. **Watch for recurring promotion candidates in future evals.**
   Especially around:
   - ask / infer / default
   - operator handoff
   - doctrine vs calibration

3. **Keep sidecar summaries honest and lightweight.**
   The eval system got stronger in this session because it stayed useful without becoming bureaucratic.

4. **Preserve the distinction between runtime constitution, philosophy, domain contract, and local skill method.**
   That layering is one of the most important architecture decisions made in this session.

---

## Closing assessment

This session improved the workspace at the system level.

Not by making one skill smarter.
By making the workspace more legible to itself.

That is the real operator uplift.
