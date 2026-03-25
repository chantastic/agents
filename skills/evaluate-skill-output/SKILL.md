---
name: evaluate-skill-output
description: Evaluate the quality of a skill's output after a run. Reads the project manifest and all intermediate artifacts, self-assesses across categories, and saves a structured analysis alongside the skill for future learning. Use after completing a skill-driven pipeline (e.g., video-pipeline) to capture what worked, what didn't, and what to learn from the user's edits.
---

# Evaluate Skill Output

Generate a structured self-evaluation of a skill run. The eval is saved alongside the skill — not in the project directory — so it persists as a learning artifact.

## Inputs

1. **Project directory** — path to the project with a `manifest.json` (or equivalent output)
2. **Skill name** — which skill to evaluate (determines where the eval is saved)

If not provided, infer from context: check the current directory for a manifest, or ask.

## Process

### Step 1: Read the skill definition

Read the skill's `SKILL.md` to understand what the skill was supposed to do — its process, outputs, and quality criteria.

```
~/.agents/skills/<skill-name>/SKILL.md
```

### Step 2: Read all project artifacts

Read the manifest and every intermediate file it references. For a video pipeline, this means:

- `manifest.json` — stage status, stats, file paths
- `cut/decisions.json` — every keep/remove decision with reasoning
- `cut/utterances.txt` — the raw utterances that were evaluated
- `polish/pass_*/eval.json` — issues found per pass
- `polish/pass_*/preview_utterances.txt` — what the viewer experiences
- `zoom/zooms.json` — zoom decisions with reasoning

For other skills, read whatever artifacts the skill produces. The manifest (or equivalent) is the guide.

### Step 3: Evaluate each stage

For each stage the skill ran, assess:

#### Accuracy

- **What decisions were made?** Count keeps, removes, fixes, additions.
- **What categories of decisions?** Group by type (duplicates, false starts, pacing drag, etc.)
- **Which decisions are you least confident about?** Flag specific items with reasoning.
- **Were there cascading errors?** Did a mistake in one stage cause problems in a later stage? (e.g., botched segment removal requiring an extra polish pass)

#### Process adherence

- **Did you follow the skill's documented process?** Step by step.
- **What steps were skipped or modified?** And why.
- **Were there methodology violations?** (e.g., skipping re-transcription verification, not asking the user to confirm before proceeding)

#### Efficiency

- **How many passes/retries were needed?** Were extra passes caused by avoidable errors?
- **What was the biggest time sink?** (e.g., environment issues, 1Password auth, large file processing)
- **What could be automated or cached?** (e.g., API key retrieval, intermediate results)

### Step 4: Identify patterns

Look across the evaluation for systematic issues:

- **Recurring error types** — Do you keep making the same kind of mistake? (e.g., forgetting that utterance boundaries don't match segment boundaries)
- **Blind spots** — What categories of issues do you consistently miss on the first pass?
- **Over/under-aggressiveness** — Are you cutting too much or too little? In which categories?
- **Subjective calibration** — For taste-based decisions (zoom scale, pacing cuts), note what you chose and flag for user feedback.

### Step 5: Define learning hooks

For each area where user feedback would improve future runs, define what data to capture:

```json
{
  "feedback_hooks": [
    {
      "category": "pacing_drag",
      "question": "Did I over-cut the model config section?",
      "artifacts": ["polish/pass_1/eval.json", "entries with type pacing_drag"],
      "how_to_compare": "Diff my edit list against reviewer's FCPXML export"
    },
    {
      "category": "zoom_scale",
      "question": "Were 1.50-1.65 scales appropriate or too aggressive?",
      "artifacts": ["zoom/zooms.json"],
      "how_to_compare": "Check which zooms survived and what scales were adjusted"
    }
  ]
}
```

### Step 6: Write the eval

Save to the skill's evals directory:

```
~/.agents/skills/<skill-name>/evals/<date>-<project-slug>.md
```

The filename uses the date and a slug derived from the project (e.g., `2026-03-25-pi-first-look.md`).

#### Eval format

```markdown
# Eval: <Project Name>

**Date**: YYYY-MM-DD
**Source**: <source file path>
**Skill**: <skill-name>
**Duration/Scope**: <key metric — e.g., "64m → 17m (73% removed)">

---

## Summary

<2-3 sentence overall assessment>

## What went well

<Bulleted list with specifics — not generic praise>

## What went poorly

<Numbered list, each with:>
### N. <Issue title>
<What happened, root cause, what should have been done instead>

## Stage-by-stage assessment

### <Stage name>
| Metric | Value |
|---|---|
| ... | ... |

**Decisions**: <count by category>
**Confidence**: <high/medium/low areas>
**Process adherence**: <skipped steps, methodology violations>

## Patterns

<Systematic issues observed across stages>

## Learning hooks

<What to capture from user feedback, in the JSON format above>

## Recommendations

<Specific changes to the skill, services, or process>
```

### Step 7: Check for prior evals

Read any existing evals in the skill's evals directory:

```bash
ls ~/.agents/skills/<skill-name>/evals/
```

If prior evals exist, compare:
- Are the same issues recurring? Note patterns across runs.
- Have previous recommendations been implemented? Check if the skill was updated.
- Is performance improving, stable, or degrading?

Add a **"Cross-run patterns"** section if there are prior evals to compare against.

### Step 8: Report

Tell the user:
- Where the eval was saved
- Top 3 issues to address
- What feedback would be most valuable (from the learning hooks)
- Whether recurring patterns were found across evals

## Notes

- Evals are **skill development artifacts**, not project artifacts. They live in `~/.agents/skills/<skill-name>/evals/`, not in the project directory. This is a core principle — see AGENTS.md.
- The eval should be honest and specific. "Could be better" is useless. "I removed 15 segments for pacing drag but suspect 5 of them contained authentic exploration the viewer would enjoy" is useful.
- When the user provides their edited FCPXML back, a follow-up eval can diff against the original to fill in the learning hooks with ground truth data.
- This skill works for any skill that produces artifacts — not just video-pipeline. The stage-by-stage assessment adapts to whatever the skill's process defines.
