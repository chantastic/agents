---
name: make-it-personal
description: Interview Chan to extract the personal layer beneath technical or professional content. Use when a draft exists but reads like a product review, recap, or tutorial — and needs the "you" underneath.
---

# Make It Personal

Interview Chan to extract the personal layer beneath technical or professional content. Use when a draft exists but reads like a product review, recap, or tutorial — and needs the "you" underneath.

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

Load `~/.agents/skills/chan-dev-writing/SKILL.md` and assess:
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

## Reference

- Writing style guide: `~/.agents/skills/chan-dev-writing/SKILL.md`
- Reference graph: `~/.agents/skills/chan-dev-writing/REFERENCE.md`
- Past interviews: `~/.agents/skills/make-it-personal/interviews/`
