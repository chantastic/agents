# Chantastic YouTube Script Style Guide

A comprehensive reference for writing YouTube tutorial scripts in Michael Chan's (Chantastic) style, based on analysis of 18 WorkOS tutorial videos.

## Script Architecture

Every tutorial follows a 4-beat structure:
1. **Hook** (1-3 sentences) — Pain point, capability, or timely event. Never a greeting.
2. **Bridge** — "Let's get into it."
3. **Step-by-step walkthrough** — Linear, screen-first narration. Errors included.
4. **Close** — Summary + tease + CTA + sign-off.

## Opening Hooks

Lead with a concrete developer concern or exciting announcement.

**DO:** "Keeping data in sync across systems can be a nightmare." / "AuthKit just added permissions..." / "Laravel Cloud launched today..."

**AVOID:** "Hey everyone, welcome back!" / "In today's video..." / Any `[inflection]` tags

## Transitions

| Phrase | Function |
|--------|----------|
| "Now" | Step advance |
| "Perfect." | Success confirmation |
| "Okay, so..." | Topic shift |
| "Let's jump back to..." | Context switch |
| "And here we go." | Reveal moment |

## Screen-First Narration

Narrate what's visible: "On screen now is..." / "So here we have..." / "If we scroll over..."
Narrate actions: "Let's open up..." / "Navigate to..." / "Scrolling down..."

## Technical Explanations

- Explain WHY, not just WHAT
- Use inclusive "we" — "We need to..." not "You need to..."
- Acknowledge complexity casually — "I know it's a mouthful."

## Error Handling Pattern

1. Encounter → 2. Acknowledge ("Well, that's weird.") → 3. Investigate → 4. Explain → 5. Fix

## Close Formula

"So that's all there is to [topic]. [Tease next video] Get subscribed. I'm Chantastic. I'll see you in the next one. Bye."

## Tone

Like a smart friend showing you something cool at their desk. First-person, present-tense, enthusiastic without hype, confident but humble.

## Anti-Patterns (NEVER use)

- `[pauses]`, `[confident]`, `[VISUAL:]` — inflection/stage direction tags
- `[SCENE N]` markers
- Third-person narration ("the developer", "users should")
- Character/word counts for TTS
- Generic greetings
