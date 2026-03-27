# Operating Principles

These principles describe how this workspace is meant to operate.

`AGENTS.md` is the runtime constitution: concise, directive, and optimized for execution.
This file is different. It is mostly philosophy — the *why* behind the rules, the collaboration model between operator and agent, and the standards for promoting lessons into doctrine.

Start here when the question is not just "what should the skill do?" but "how should this system think?"

---

## 1. The operator owns intent. The agent owns execution.

The operator is the system owner.

That means the operator owns:
- direction
- taste
- publication decisions
- acceptable risk
- what counts as "done"

The agent owns:
- execution within the agreed scope
- synthesis across artifacts
- maintaining structure and audit trails
- surfacing uncertainty when it matters
- turning repeated work into reusable process

This workspace is not built around agent autonomy for its own sake. It is built around operator leverage.

The goal is not to remove the operator.
The goal is to let the operator spend more attention on judgment and less on coordination, bookkeeping, and repetitive analysis.

---

## 2. Human intervention is part of the system, not a failure of the system.

A workflow that includes a human step is not incomplete.
It is honest.

Some boundaries are real:
- editing in Final Cut Pro
- publication decisions
- taste-sensitive review
- identity-sensitive choices

Those boundaries should be modeled explicitly as **handoffs**, not treated as awkward gaps in automation.

A good agent does not pretend the human is unnecessary.
A good agent packages the handoff so the operator can resume cleanly.

This is why operator handoff is a first-class concept in the video workflow.

---

## 3. Truth should live where the best evidence exists.

Do not force early certainty.

If a field is best known later in the workflow, let it be inferred later.
If the operator is the only trustworthy source, ask.
If a reversible default is good enough, default.

This leads to a simple collaboration rule:
- **default** when the choice is low-risk and reversible
- **infer** when the evidence exists in artifacts or context
- **ask** when the decision is identity-sensitive, publication-sensitive, destructive, or taste-critical

Examples:
- `speakers` belongs near publish, where the final export and stream naming provide the strongest evidence
- publication stays manual even when upload is automated
- uncertain stylistic choices should be surfaced, not buried

The system should not invent certainty just because a downstream step would prefer a value.

---

## 4. Contracts matter more than local cleverness.

Once a workflow starts working, the main failure mode changes.

The problem is no longer usually "the model made one bad decision."
It becomes "the system was locally smart but globally confused."

That is why this workspace values:
- manifests
- explicit schemas
- field ownership
- source vs artifact boundaries
- clear stage boundaries
- present-tense reporting

A stale skill doc is worse than a missing one.
Prompts are executable docs. If they drift, the system drifts.

The right response to a maturing workflow is not only better prompts.
It is a more legible contract between prompts.

---

## 5. Decisions are durable. Compiled artifacts are disposable.

The system should preserve the reasoning units, not only the outputs.

In this workspace, that means:
- transcripts are source
- decisions are source
- manifests are source
- edit lists, previews, and timelines are compiled artifacts

Compiled artifacts matter. But they can be regenerated.
The durable value is the record of what was decided, against what source, and why.

This principle keeps the workflows inspectable, resumable, and debuggable.
It also makes later stages safer: they can build from shared truth instead of reverse-engineering downstream artifacts.

---

## 6. Learning artifacts belong with the capability they improve.

Project artifacts live with the project.
Learning artifacts live with the skill.

That distinction exists because projects are temporary, but the lessons are reusable.
If evals live next to a disposable project, they disappear when the project is cleaned up.
If they live next to the skill, they can change future runs.

This is not just storage hygiene.
It is how the workspace compounds.

The unit of learning here is not only the project.
It is the capability.

---

## 7. Narrative memory and operational memory are both required.

A mature operator system needs two kinds of memory:

- **Narrative memory** — what happened, what surprised us, why it mattered
- **Operational memory** — what category recurred, how often, where, and with what severity

That is why evals now come in pairs:
- `.md` for the story
- `.json` for the counts

The markdown explains meaning.
The sidecar makes the meaning queryable.

Neither should replace the other.
Structure without judgment gets sterile.
Narrative without structure does not compound fast enough.

---

## 8. Not every successful lesson deserves promotion to doctrine.

A powerful system needs a promotion path for ideas.

Not everything learned in one run should become a workspace-wide principle.
Some things should remain:
- a local heuristic
- a style preference
- a temporary calibration
- a note in an eval

This workspace uses four levels:

### Principle
Durable across projects. Belongs in `AGENTS.md`, `OPERATING_PRINCIPLES.md`, contracts, or core skills.

### Heuristic
A useful default. Belongs in skills, but should be phrased with judgment.

### Preference
Taste. Belongs as taste, not truth.

### Temporary calibration
Current best-known numbers or tendencies for a format, layout, or operator. Belongs in `evals/` and other calibration artifacts.

The discipline is not just learning quickly.
It is learning at the right level.

---

## 9. The system should encode the kind of certainty it has.

A strong prompt should not only say what to do.
It should signal how rigidly to believe it.

That is the reason for the distinction between:
- principle
- heuristic
- preference
- temporary calibration

When a model cannot distinguish law from lore, it becomes brittle.
When it can, it becomes portable.

This is why the video skills now explicitly separate durable process from taste and calibration.
That pattern should spread only where it adds clarity.

---

## 10. The system is built for leverage, not purity.

This workspace is intentionally pragmatic.

It values:
- thin services over abstraction towers
- good tools over ideological fallback paths
- explicit handoffs over fake end-to-end autonomy
- real eval loops over ornamental architecture
- operator trust over theoretical elegance

The question is not "is this perfectly general?"
The question is "does this make the operator stronger without making the system harder to trust?"

That is the standard.

---

## 11. Skills depend on capabilities, not coordination state.

A skill may depend on the harness and services. What it may not do is depend on hidden workflow state owned by a coordinator.

This means:
- A skill may call services to derive local data it needs
- A skill does not read coordinator-owned state files like manifests
- A skill does not know what ran before it or what runs after
- A skill receives its cross-stage context from whoever invokes it — coordinator, operator, or future sub-agent
- A skill's `## Inputs` section is its contract

The benefit is composability. A context-independent skill can be:
- Run standalone by a human ("here's my video, cut it")
- Orchestrated by a coordinator ("here are the outputs from the last stage, polish them")
- Parallelized by a sub-agent system (future optimization, not a requirement)

If a skill needs data that can reasonably be derived from the artifact in front of it, it should prefer a service over pushing that burden onto the operator.

Examples:
- `run-video-publish` may transcribe an export if no transcript exists
- `polish-video` may re-transcribe a preview
- `zoom-video` may extract frames

When a skill needs cross-stage context from a previous stage, **the coordinator provides it, the skill does not fetch it.**

Convention-based discovery ("look for the biggest .mp4 here") is acceptable as a convenience default. Reading coordinator-owned state is coupling and belongs in the coordinator.

---

## 12. Only the coordinator knows the graph.

Sequencing, state tracking, retries, and inter-skill wiring live in exactly one place: the coordinator skill.

Individual skills do not know:
- What stage they are in a pipeline
- What ran before them
- What runs after them
- How to update shared state (manifests)

The coordinator:
- Reads and writes the manifest
- Extracts the right inputs for each skill from previous outputs
- Passes those inputs explicitly
- Captures outputs and records them in shared state
- Decides what to retry, skip, or resume

This separation means skills can be rearranged, skipped, or run in isolation without modification. The pipeline topology lives in the coordinator, not distributed across skills.

A coordinator should be identifiable as such — both in name and in description — because it is evaluated against a different standard than a transformation skill.

---

## 13. Names should signal role.

A skill name should help the operator understand what kind of thing they are invoking.

Use naming to distinguish:
- **reference skills** — stable lenses for style, conventions, naming, vocabulary, and judgment
- **transformation skills** — bounded actions that produce an output
- **coordinator skills** — workflow owners that sequence other steps and manage state

Recommended naming:
- **Reference skills:** `consult-*`
- **Coordinator skills:** `run-*`
- **Transformation skills:** use the sharpest honest action verb

Useful transformation families:
- `create-*` — create a new artifact
- `make-*` — interactively refine or align existing material toward a target quality
- `prepare-*` — make something ready for downstream use
- `evaluate-*` — assess an existing artifact, run, or result

Domain-specific verbs are also valid when they are sharper than a generic family prefix:
- `cut-*`
- `polish-*`
- `zoom-*`
- `get-*`
- `audit-*`
- `publish-*`

Examples:
- `consult-chan-writing-style`
- `create-marketing-brief`
- `make-it-personal`
- `prepare-post`
- `evaluate-skill-output`
- `cut-video`
- `get-broll-assets`
- `run-video-pipeline`

A prefix is a useful operator signal, but it is not sufficient on its own. A skill should also identify its role explicitly when that role affects how it should be evaluated.

Prefer an explicit frontmatter field:
- `role: reference`
- `role: transformation`
- `role: coordinator`

Within transformation skills, prefixes can carry useful subtype signals:
- `create-*` usually implies creating a new artifact
- `make-*` usually implies interactive refinement or alignment of existing material toward a target quality
- `prepare-*` usually implies readiness or packaging for downstream use
- `evaluate-*` usually implies diagnosis, scoring, or assessment of an existing result

Rule: **specific beats generic.**
Use a family prefix when it genuinely clarifies the type of transformation. Keep a domain-specific verb when it is more precise.

This matters because each role is evaluated differently:
- reference skills are judged on clarity, usefulness as a lens, and stability as a reusable source of judgment
- transformation skills are judged on local clarity, harness use, and freedom from coordination-state coupling
- coordinators are judged on sequencing, state ownership, retries, handoffs, and contract mapping

---

## 14. Reference dependencies are composition, not coupling.

A skill may depend on stable reference skills or reference documents for judgment, style, conventions, or vocabulary.

This is not the same as reading coordinator-owned state.

Examples of valid composition:
- `make-it-personal` consulting a writing-style reference skill
- a naming skill consulting a conventions document
- a publishing skill consulting a voice/style reference

Examples of invalid coupling:
- reading `manifest.json` to determine what stage ran before
- inspecting another skill's stage status to decide behavior
- assuming workflow history from coordinator-owned state

The distinction:
- **reference dependency** = using a stable lens to improve judgment
- **coordination dependency** = relying on hidden workflow state to decide execution

Reference dependencies are good composition. Coordination dependencies belong in the coordinator.

---

## 15. Convention is not coupling.

A skill can use sensible defaults without knowing about the system that produced them.

Discovery heuristics are fine:
- "If no source provided, look for the largest .mp4 in the working directory"
- "If no thesis provided, ask the operator"
- "If no keyterms provided, suggest some from context"
- "If no transcript exists, transcribe the provided video"

These are conventions — reasonable assumptions about directory structure, file naming, and locally derivable artifacts.

Coupling is not fine:
- "Read `manifest.json` and extract `stages.cut.preview`"
- "Look at `stages.polish.status` to decide what to do"
- "Assume cut must have run because this directory usually comes from run-video-pipeline"

The distinction: a convention makes a guess based on what's common or derives a local artifact from the file in front of the skill. Coupling encodes knowledge of a specific workflow's internal structure or history. Skills use conventions and services. Coordinators use coupling (to the manifest they own).
