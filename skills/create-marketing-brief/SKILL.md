---
name: create-marketing-brief
description: Create a single marketing brief document from a content brief. Produces platform-specific sections for LinkedIn, Twitter/X, and recap/blog so each section embodies the goals of that platform. Use after run-video-publish or with any compatible content brief.
---

# Create Marketing Brief

Create a single marketing brief document from a content brief.

This is a transformation skill. It takes a publish/content brief and produces one document with multiple sections. Each section should embody the goals of that platform, not just restate the same idea three ways.

## Inputs

| Input | Required | Discovery | Description |
|---|---|---|---|
| `brief` | yes | discover: `publish/brief.json` in cwd | Content brief JSON with thesis, chapters, quotes, moments, topics, links |
| `transcript` | no | discover: `transcript_path` inside brief, else `publish/transcript.json` | Full transcript for deeper quotes and context |
| `output_path` | no | default: `publish/marketing-brief.md` | Where to write the final marketing brief |

When run standalone, discover or ask for the brief path. The transcript is optional and should only be read when the brief alone is too thin.

## Outputs

| File | Type | Description |
|---|---|---|
| `publish/marketing-brief.md` | artifact | One markdown brief with platform-specific sections |

## Required brief contract

The brief should provide:
- `thesis`
- `speakers`
- `chapters`
- `key_quotes`
- `key_moments`
- `topics`
- `links`
- `titles`
- `transcript_path` (optional but preferred)

## Process

### Step 1: Read the brief

Read the full brief. Understand:
- what the content is actually about
- what the strongest emotional or practical hooks are
- what the viewer/reader walks away with
- which quotes are sharp enough to travel across formats

If the brief is too thin to support multiple sections, say so explicitly.

### Step 2: Identify the core angles

Pull out 2-4 reusable angles from the brief. These are not yet platform-specific copy. They are the raw material each section will adapt.

Examples:
- the emotional tension
- the practical takeaway
- the surprising reveal
- the most quotable line
- the strongest identity or belief signal

### Step 3: Write a single document with sections

Write one markdown document with these sections.

## 1. Overview

A short summary of:
- the thesis
- who this is for
- the 2-4 strongest angles
- the best quote to anchor the campaign

## 2. LinkedIn

Goal: relief, agreement, and professional resonance.

Write:
- 2-3 LinkedIn post variants
- a short note on what emotional angle each variant is leaning on

Constraints:
- do not summarize the whole video
- distill the shared feeling
- no launch-announcement energy
- no empty thought-leadership tone

## 3. Twitter/X

Goal: provoke curiosity, reaction, or identification through compression.

Write:
- 3-5 tweet variants
- each should be standalone
- each should preserve the gap instead of explaining the thought

Constraints:
- no thread framing
- no second-sentence clarity if it kills the tension
- no padding to hit a count; fewer stronger variants is better

## 4. Recap / Blog

Goal: crystallize the learnings into a standalone written piece.

Write:
- working title ideas
- 3-5 takeaway headings
- opening hook options
- the core arc of the recap post
- recommended quotes to include

This section is not the full post. It is the brief for writing the post well.

## 5. Reusable assets

Include:
- best quotes
- best moments
- possible hooks
- words/phrases worth reusing
- links/resources to mention

### Step 4: Keep sections true to platform goals

Do not flatten all sections into the same voice.

Use the same source material, but adapt it:
- LinkedIn = shared professional tension
- Twitter/X = sharp, withholding, identity-signaling
- Recap/Blog = reflective, structured, takeaway-oriented

### Step 5: Write the file

Write the final brief to `output_path`.

## Notes

- This skill depends on the brief as its primary handoff artifact. It does not assume `run-video-publish` ran — it only needs a compatible brief.
- The brief is the contract. The transcript is optional deep context.
- This skill creates one document with multiple sections. It does not scatter outputs across multiple files.
- Each section should embody the goals of the target platform, not just rephrase the same paragraph.
