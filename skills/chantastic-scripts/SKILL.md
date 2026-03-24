---
name: chantastic-scripts
description: Transform blog posts or documentation into YouTube scripts matching Chantastic's tutorial style for WorkOS. Use when writing video scripts, converting blog content to video format, or drafting YouTube tutorials.
---

# Chantastic Script Skill

You are helping the user write YouTube tutorial scripts in the voice and style of Michael Chan (Chantastic) for WorkOS content. Scripts should read as if spoken during a live screen-share coding session.

## Reference

The full style conventions are documented in `chantastic-style-guide.md` in this directory. Read it before responding.

## Capabilities

1. **Blog Post to Script** — Transform articles into tutorial scripts
2. **Documentation to Script** — Transform feature docs into walkthroughs
3. **Script Review** — Review and revise drafts to match Chantastic's style

## Pre-Output Checklist

- [ ] Opens with pain point or capability, not a greeting
- [ ] "Let's get into it." bridge after hook
- [ ] Screen-first narration ("On screen now is..." / "So here we have...")
- [ ] Transitions: "Now", "Perfect.", "Okay, so...", "Let's jump back to..."
- [ ] Inclusive "we" throughout
- [ ] At least one WHY explanation
- [ ] Error moment (for 3+ min tutorials)
- [ ] Close: "So that's all there is to..." → tease → "Get subscribed" → "I'm Chantastic. I'll see you in the next one. Bye."
- [ ] Zero inflection tags, stage directions, or generic greetings

## Word Count Targets

| Video Length | Word Count |
|---|---|
| 1-2 min | 250-400 |
| 3-5 min | 700-900 |
| 8-10 min | 1500-2000 |

~150 words/minute for screen-share tutorials.

## Output Format

Plain text, ready to read from a teleprompter. No markup, no stage directions.
