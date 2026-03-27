---
name: make-it-personal
description: Interview Chan to extract the personal layer beneath technical or professional content. Use when a draft exists but reads like a product review, recap, or tutorial — and needs the "you" underneath.
---

# Make It Personal

This is a transformation skill. It interviews Chan to extract the personal layer beneath technical or professional content, then produces a clearer story and a concrete revision plan. It does not read coordinator-owned state.

## Inputs

| Input | Required | Discovery | Description |
|---|---|---|---|
| `draft` | yes | ask | The current draft that feels too generic, technical, or sanitized |
| `source` | no | ask | Raw transcript, notes, or source material behind the draft |
| `reference` | no | default: `~/.agents/skills/consult-chan-writing-style/SKILL.md` | Reference skill for voice evaluation |
| `output_path` | no | ask only when writing is approved | Path for a new rewritten draft |

## Outputs

| Output | Type | Description |
|---|---|---|
| interview synthesis | artifact | The real story, specific changes, and seed-post ideas presented in-session |
| optional new draft | artifact | A newly written draft saved to a new file only when explicitly requested |
| interview log | capability artifact | A dated Q&A file saved in `~/.agents/skills/make-it-personal/interviews/` |

## When to use

- A generated recap or summary exists but feels generic
- A technical post needs a personal frame
- Content has good information but no confession, resistance, or story
- You need to identify seed posts that break off from a main piece

## Process

### 1. Read the source material

Read both the draft AND the raw transcript/source (video transcript, notes, etc). The transcript often contains off-the-cuff moments the draft sanitized away. Look for:
- Moments of hesitation or resistance
- Opinions stated then walked back
- Personal asides that got cut
- Emotional reactions to technical discoveries

### 2. Evaluate against the writing style

Consult `~/.agents/skills/consult-chan-writing-style/SKILL.md` and assess:
- Is the voice right? (conversational, confessional, direct)
- Are the sentences varied? (fragments + momentum)
- Is there a personal frame or just feature descriptions?
- Does it open with a story/confession or a product pitch?
- Does it close with a question + emoji sign-off?

Present the delta clearly: what's working, what's not, organized by specific style patterns.

### 3. Interview for the personal layer

Use the questionnaire tool to ask 4-6 questions. Structure them as:

**Round 1 (3-5 questions):** The big ones.
- What's the REAL resistance? Not the surface reason.
- What pattern from your life does this connect to?
- What are you afraid of underneath the technical decision?
- Is there a family/life parallel?
- What's the honest version of the polished thing you said?

**Round 2 (2-4 questions):** Follow-ups that sharpen.
- Take the best answer from round 1 and push deeper.
- Ask for a specific story or concrete example.
- Ask about the thing they almost said but held back.

### 4. Synthesize and propose

After the interview, present:
1. **The real story** — what the post is actually about underneath
2. **Specific changes** — how the draft should shift (not a rewrite yet)
3. **Seed posts** — other posts that want to exist but shouldn't be crammed into this one

### 5. Write (only when asked)

Don't rewrite automatically. Present the plan, get approval, then write to a NEW file (never overwrite the original). Follow the chan.dev writing style guide throughout.

### 6. Store the interview

After the session, append the interview Q&A to `~/.agents/skills/make-it-personal/interviews/` as a dated file. This material is reusable for future posts.

## Interview principles

- **Ask about feelings, not facts.** The facts are in the transcript. The feelings are what make it a chan.dev post.
- **Offer options but always allow freeform.** Chan's best answers come when he goes off-script.
- **Name the pattern you see.** "It sounds like this connects to X" — let him confirm or correct.
- **Don't be precious.** Chan's life is an open book. Ask the hard question.
- **The best material is what almost didn't get said.** Push past the first answer.

## Notes

- Consulting `consult-chan-writing-style` is a reference dependency, not workflow coupling. It is a stable lens for judgment.
- Do not overwrite the original draft. Always write to a new file when writing is approved.
- The interview log lives with the skill because it is capability memory, not project state.

## Reference

- Writing style guide: `~/.agents/skills/consult-chan-writing-style/SKILL.md`
- Reference graph: `~/.agents/skills/consult-chan-writing-style/REFERENCE.md`
- Past interviews: `~/.agents/skills/make-it-personal/interviews/`
