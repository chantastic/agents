---
name: consult-skill-authoring
description: Guide for writing and refactoring skills. Covers input/output contracts, coordinator vs. standalone design, discovery heuristics, and the promotion path from calibration to principle. Use when creating a new skill, refactoring an existing one, or extracting a skill from a repeated workflow.
---

# Skill Authoring

This is a reference skill. It provides a stable lens for writing and refactoring other skills in this workspace.

A guide for writing skills that work both standalone and as part of a coordinated pipeline.

## When to use this skill

- Creating a new skill from scratch
- Refactoring an existing skill (e.g., removing manifest coupling)
- Extracting a skill from a repeated workflow
- Reviewing whether a skill follows workspace conventions

## Core architecture

### Skills depend on capabilities, not coordination state

A skill may depend on the harness and services. It may not depend on hidden workflow state owned by a coordinator.

This means a skill does NOT:
- Read manifests or pipeline state files
- Check if a previous stage ran by inspecting coordinator state
- Know what runs after it
- Write to shared state files owned by a coordinator

This means a skill DOES:
- Declare its inputs explicitly in an `## Inputs` section
- Declare its outputs explicitly in an `## Outputs` section
- Ask the operator for anything not provided (when run standalone)
- Use convention-based discovery as a convenience (not as coupling)
- Call services to derive local artifacts it needs (transcripts, frames, renders, etc.)

### The coordinator pattern

When skills form a pipeline, a coordinator skill handles the wiring:

```
Coordinator responsibilities:
- Read/write the manifest (shared state)
- Extract inputs for each skill from previous outputs
- Pass inputs explicitly to each skill
- Capture outputs and record them
- Decide sequencing, retries, skips, resumption

Skill responsibilities:
- Do the work
- That's it
```

A skill should be invocable by a coordinator OR by a human with the same interface. The only difference is who provides the inputs.

## Naming and role signaling

A skill name should tell the operator what kind of thing it is.

### Reference skills

Use the `consult-*` prefix.

Examples:
- `consult-chan-writing-style`
- `consult-xstate-naming`
- `consult-workos-voice`

These imply a stable reference lens: a skill you consult for style, conventions, naming, vocabulary, or judgment.

### Transformation skills

Use the sharpest honest action verb for the bounded transformation.

Useful transformation families:
- `create-*`
- `make-*`
- `prepare-*`
- `evaluate-*`

Domain-specific verbs are also valid when they are sharper:
- `get-*`
- `write-*`
- `cut-*`
- `polish-*`
- `zoom-*`
- `publish-*`
- `audit-*`

Examples:
- `create-marketing-brief`
- `make-it-personal`
- `prepare-post`
- `evaluate-skill-output`
- `cut-video`
- `get-broll-assets`

These imply a local transformation: take inputs, do work, produce outputs.

Useful subtype signals:
- `create-*` usually means creating a new artifact
- `make-*` usually means interactive refinement or alignment of existing material toward a target quality
- `prepare-*` usually means making something ready for downstream use
- `evaluate-*` usually means diagnosis, scoring, or assessment of an existing result

Rule: **specific beats generic.** Use a family prefix when it clarifies the type of transformation. Keep a domain-specific verb when it is more precise.

### Coordinator skills

Use the `run-*` prefix.

Examples:
- `run-video-pipeline`
- `run-shutdown-ritual`
- `run-content-distribution`

`run-*` signals that the skill owns sequencing, handoffs, retries, or shared state.

Avoid using `prepare-*`, `create-*`, or `make-*` for coordinator skills — those sound like transformations, not workflow owners. Avoid using `consult-*` for a skill that actually mutates files or coordinates a workflow — that would blur role boundaries. Prefer `run-*` as the default coordinator signal.

### Role declaration

A prefix is helpful, but a skill should also identify its role explicitly in the opening section when the role affects how it should be evaluated.

Example:

```markdown
# Run Video Pipeline

This is a coordinator skill. It owns sequencing, retries, shared state, and handoffs.
Stage skills do not read the manifest; this skill does.
```

Reference, transformation, and coordinator skills are evaluated against different standards. Make the role legible.

## Skill structure

Every skill is a directory containing `SKILL.md`:

```
skills/
└── my-skill/
    ├── SKILL.md          ← the skill prompt
    └── evals/            ← learning artifacts (optional)
```

### SKILL.md anatomy

```markdown
---
name: my-skill
description: One-line description. Use when [trigger].
---

# Skill Name

One paragraph: what this skill does and why.

## Inputs

Declare every input the skill needs. For each:
- Name and type
- Whether it's required or optional
- What the skill does if it's not provided (ask? discover? default?)

Format:

| Input | Required | Discovery | Description |
|-------|----------|-----------|-------------|
| source | yes | ask | Path to video file |
| keyterms | no | suggest from context | Domain terms for STT |
| thesis | yes | ask | One-sentence video description |

"Discovery" is what happens when the input isn't provided:
- **ask** — prompt the operator
- **suggest** — propose a value, confirm with operator  
- **discover** — use convention-based heuristic (e.g., find largest .mp4)
- **default** — use a fixed default value
- **infer** — derive from other inputs (e.g., infer thesis from transcript)

## Outputs

Declare every output the skill produces. For each:
- File path (relative to output_dir or working directory)
- Whether it's a source artifact or compiled artifact
- Brief description

## Process

Step-by-step instructions. This is the prompt the LLM follows.

## Notes

Durable knowledge. Edge cases. Hard-won lessons.
```

### The Inputs section is the contract

This is the most important section. It replaces manifest-reading with explicit declaration.

**Before (coupled):**
```markdown
## Inputs
Read from manifest.json in the working directory:
- source — original video path
- stages.cut.preview — path to cut preview
- thesis — inferred by cut stage
```

**After (pure):**
```markdown
## Inputs
| Input | Required | Discovery | Description |
|-------|----------|-----------|-------------|
| source | yes | discover: largest .mp4/.mov in cwd | Original video |
| preview | yes | discover: cut/preview.mp4 | Preview from previous edit |
| thesis | yes | ask | What the video is about |
| transcript | yes | discover: transcript.json in cwd | Deepgram transcript JSON |
| decisions | no | discover: decisions/*.json | Existing decision layers |
| keyterms | no | ask | Domain terms for re-transcription |
```

The skill doesn't know where these came from. A coordinator might extract them from a manifest. A human might type them in. The skill doesn't care.

## Convention-based discovery

When an input isn't provided, a skill can look in conventional locations before asking.

**Good conventions:**
- Look for the largest `.mp4`/`.mov` in the working directory
- Look for `transcript.json` in the working directory
- Look for `decisions/*.json` for decision layers
- Look for `cut/preview.mp4` or `polish/final/preview.mp4`

**These are NOT coupling** because they don't encode knowledge of another skill's internal state. They're just reasonable guesses about file layout.

**Bad coupling:**
- Reading `manifest.json` and parsing `stages.cut.preview`
- Checking `stages.polish.status === "complete"`
- Reading another skill's eval files to adjust behavior

The test: "Would this discovery logic work if the files were placed here manually, without any skill having run?" If yes, it's convention. If no, it's coupling.

## Writing for both standalone and coordinated use

A well-written skill works in two modes without any conditional logic:

**Standalone mode:**
1. Skill is invoked directly by the operator
2. Inputs are discovered via conventions or asked for
3. Outputs are written to the working directory
4. No manifest is read or written

**Coordinated mode:**
1. Coordinator reads the manifest
2. Coordinator extracts inputs and provides them to the skill
3. Skill runs identically — it received inputs, it doesn't care how
4. Coordinator captures outputs and updates the manifest

The skill's process section should NOT have "if manifest exists... else..." branching. It should use whatever inputs it received, derive what it reasonably can via services, and ask only when needed.

## Epistemic status markers

Skills should signal how rigid each instruction is:

| Level | Where it lives | Example |
|-------|---------------|---------|
| **Principle** | SKILL.md, OPERATING_PRINCIPLES.md | "Skills are pure functions" |
| **Heuristic** | SKILL.md process steps | "Keep the last take in duplicate runs" |
| **Preference** | SKILL.md, stated as taste | "Prefer more frequent gentle zooms" |
| **Calibration** | evals/ | "Scale 1.25 for guide tier on 2560x1440" |

Mark sections explicitly when the distinction matters:
- "**Principle:** Contiguous time ranges, not sentence fragments."
- "**Heuristic:** Target 5-10 chapters. Fewer for tight content."
- "**Starting heuristic:** 3-4 zooms per minute. Adjust per format."

## Coordinator skills

A coordinator skill has a different structure. It owns the graph:

```markdown
## Process

### Step 1: Initialize
- Create/read manifest
- Gather project-level inputs (source, keyterms)

### Step 2: Run cut
- Extract inputs: source, keyterms, target_duration
- Invoke cut-video with those inputs
- Capture outputs: transcript, decisions, thesis, preview
- Update manifest

### Step 3: Run polish
- Extract inputs: source, transcript, thesis, decisions[], preview, keyterms
- Invoke polish-video with those inputs
- Capture outputs: new decisions, final edit_list, final preview
- Update manifest

### Step 4: Handoff
- Report what was produced
- Tell operator what to do next (open in FCP, export, run publish)
```

The coordinator's job is mapping between the manifest's shape and each skill's input contract. That mapping logic lives in one place.

## Checklist for new skills

- [ ] Name matches role (`consult-*` for reference skills, `run-*` for coordinators, sharp action verb for transformations such as `create-*`, `make-*`, `prepare-*`, `evaluate-*`, or a more precise domain verb)
- [ ] Role is explicit in the opening section when role affects evaluation
- [ ] `## Inputs` table with Required/Discovery columns (for transformation/coordinator skills)
- [ ] `## Outputs` table with source-vs-artifact distinction (for transformation/coordinator skills)
- [ ] No manifest reads or writes in transformation or reference skills
- [ ] No references to coordinator-owned state in transformation or reference skills
- [ ] Reference dependencies are stable lenses, not workflow-state dependencies
- [ ] Discovery heuristics that work with manually-placed files
- [ ] Discovery falls back to asking
- [ ] Local missing artifacts are derived via services when reasonable
- [ ] Process steps that work identically standalone or coordinated
- [ ] Epistemic status markers on non-obvious instructions
- [ ] `evals/` directory for calibration data (if applicable)

## Checklist for refactoring existing skills

- [ ] Move all manifest reads/writes to the coordinator
- [ ] Replace "read from manifest" with input declarations
- [ ] Replace "if manifest exists... else ask" with just the input contract
- [ ] Verify discovery heuristics don't encode knowledge of other skills
- [ ] Test mentally: "does this skill work if I just hand it files in an empty directory?"
