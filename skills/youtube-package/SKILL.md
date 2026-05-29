---
name: youtube-package
description: Generate a complete YouTube publishing package from a Deepgram transcript — viral-but-specific titles, an SEO-friendly description with accurate chapter markers, a pinned comment, a long social caption, a LinkedIn post that affirms the reader, and an X post that challenges them. Use this skill whenever Michael mentions a "YouTube package", "video package", "publish a video", "title and description for [video]", "chapters for [video]", "pinned comment", "social copy for the video", or hands over a Deepgram JSON transcript and asks what to post. Also use whenever a `.deepgram.corrected.json` file appears in the conversation and the goal is publishing copy.
---

# YouTube Package

You are writing the publishing kit for one of Michael's videos. Output goes back in chat — no files. The deliverable is a single chat message Michael can copy-paste from, section by section.

## Inputs you need

**Required**: a transcript file. Two formats are supported, each with its own parser script — pick the one that matches the input:

- **Deepgram-normalized JSON** (usually `.deepgram.corrected.json`) → `scripts/parse_deepgram.py`. This is Michael's default. It carries diarization when available.
- **SRT subtitle file** (`.srt`) → `scripts/parse_srt.py`. Use this when the only thing on hand is the standard subtitle export from YouTube, Descript, etc. No diarization, but the timestamp discipline still holds — chapter markers must come from the emitted `PARAGRAPH_TIMESTAMPS` list either way.

The two scripts share the same output shape (`DURATION`, timestamped paragraphs, `PARAGRAPH_TIMESTAMPS`), so the rest of the workflow doesn't need to know which format produced it.

**Optional but commonly needed** — surface these gaps to Michael in one short clarification message before writing the package, only if you can't infer them from the transcript:
- Announcement / blog post URLs to link in the pinned comment + description
- Guest social handles (LinkedIn, X) if it's an interview
- Anything Michael wants emphasized (a feature launch, a specific quote, a CTA)

If Michael provided this context in the prompt, don't ask again. If the transcript is a solo demo with no obvious external links and Michael didn't mention any, you can proceed without — call it out at the end ("no announcement links surfaced — add one if you have one").

## Workflow

1. Run the parser: `python3 scripts/parse_deepgram.py <path-to-json>`. It emits the duration, a timestamped paragraph-level transcript, and a `PARAGRAPH_TIMESTAMPS:` line — the authoritative list of timestamps you're allowed to use for chapters.
2. Read the full transcript. Identify the core thesis, the speaker, the product/topic, any quotable moments, the structural beats.
3. If anything critical is missing (see "Inputs you need"), ask Michael one tight question before drafting.
4. Write the package. Stream every section in one chat message using the layout in "Output format" below.

## Chapter markers — the rule that matters most

Chapters are sections of the video, not paragraph-by-paragraph signposts. Think acts of a play. The goal is letting viewers jump to the part they care about.

**Hard rules**:
- The first chapter is always `0:00`. YouTube requires it. The label should describe the opening (e.g., "Intro — what is AgentMail" not just "Intro").
- Every other timestamp must come from the `PARAGRAPH_TIMESTAMPS:` line emitted by the parser. Do not invent timestamps. Do not interpolate between paragraphs. If the topic shifts mid-paragraph, snap to the nearest paragraph start in the list (usually the one starting that topic).
- Chapter labels are **literal first, verb-led second**. The goal is that a viewer reading the label knows exactly which part of the video they're about to jump into. Specificity beats style.
  - **Be literal**: name the actual subject. "Read the AgentMail criticism tweet" beats "Read the tweet that broke us" — `us` and `it` and `the thing` are too vague to help a viewer scan.
  - **Verbs are good when they fit cleanly**: "Sign up an agent with one prompt" works because the action and the object are both specific. If the only way to lead with a verb is to swap in a vague pronoun, drop the verb and use a noun phrase that names the moment ("AgentMail's one-prompt signup demo"). Don't force directives onto chapters where the literal version is clearer.
  - **3–8 words.** Specific proper nouns earn their place (product names, named features, named people).
- One chapter per major beat. **Hard caps**:
  - Videos under 10 min: max 6 chapters. If you find yourself going past 6 on a short demo, you're picking sub-beats instead of acts. Merge them.
  - 10–30 min: 4–8 chapters.
  - 30–60 min: 6–10 chapters.
  - 60 min+: 8–14 chapters.
  Don't pad to hit a number. If there are only three real sections, ship three.
- Chapters appear in ascending time order, on consecutive lines, formatted `M:SS Label` (or `H:MM:SS Label` if the video is over an hour).

**How to find the beats**: read the transcript front-to-back and notice where the speaker pivots — new topic, new demo, Q&A starts, the "so what" moment, the close. Those are the chapter boundaries. Single-topic stretches of 30–90 seconds don't need their own chapter.

**Chapter label examples** (literal over stylish; verb if it fits cleanly):

| Topic | Avoid | Better |
| --- | --- | --- |
| Speaker introducing themselves | Intro | Meet Adi from AgentMail |
| The tweet that prompted the rebuild | Read the tweet that broke us | Read the AgentMail criticism tweet |
| Live demo of one-prompt signup | Live demo of the new flow | Sign up an agent with one prompt |
| Allow-list rate-limiting | Lock it down with allow-lists | Cap new inboxes to 10 emails per day |
| Closing argument about email | Use it as the identity layer | Why email is already the identity layer |

The first-column versions all rely on vague pronouns (`it`, `us`, `the new flow`). Replace them with the actual nouns the viewer will see. If naming the thing makes the chapter too long, you don't need the verb — a literal noun phrase is fine.

## Output format

Produce exactly this structure, in this order, in one chat message. Use the headers verbatim so Michael can scan it fast.

```
## Titles (5 options)

1. <title>
2. <title>
3. <title>
4. <title>
5. <title>

## YouTube description

<hook paragraph>

<chapter markers, one per line>

<body paragraph(s), ~150–250 words>

<links section>

## Pinned comment

<pinned comment>

## Social caption (<200 chars)

<caption>

## LinkedIn post

<post>

## X post

<post>
```

## Per-section rules

### Titles

Goal: viral *and* specific. Curiosity gap with a payoff, not a tease.

Good patterns:
- Specific numbers or names: `Why I bet on email inboxes for AI agents (and what broke first)`
- Contrarian: `Stop building new auth standards. Just use email.`
- Problem → answer: `Our agent signup was the biggest epic fail I've ever seen. Here's the fix.`
- Concrete result: `One prompt, one inbox: how AgentMail signs up agents in 30 seconds`

Bad patterns (avoid):
- Vague clickbait: `You won't believe what this AI does`
- Generic: `Building AI agents with email`
- All caps / excessive punctuation
- Anything that sounds like every other YouTube title

Constraints:
- 60 characters or fewer (otherwise YouTube truncates in search)
- Use proper nouns when they earn the click (AgentMail, Claude, OpenAI). The transcript is `.corrected.json` precisely because Michael's pipeline has normalized those names — trust the spelling.
- Five options total. Vary the angles (don't give five contrarian titles or five problem-answer titles).

### YouTube description

**Structure**:

1. **Hook** (1–3 sentences). Open with something concrete pulled from the actual video content — a stat, a quote, a tension, the core question the video answers. Do not start with "In this video..." or "Today, [Speaker] talks about...". A good hook makes someone reading the search snippet want to click.

2. **Chapter markers**. One per line, immediately after the hook with a blank line above. Follow the chapter rules above.

3. **Body** (~150–250 words). Expand on the hook. Cover what the viewer will learn, what's surprising, why it matters. Use plain prose, not bullet points. Mention proper nouns once or twice so they get indexed. If the video is part of a series, name the series. No emojis unless Michael's prior videos used them.

4. **Links section** — only include lines for links you actually have. Drop the whole line if a URL or handle wasn't provided and can't be quoted from the transcript. Never use `[add]`, `[TBD]`, or any placeholder token in the published copy. If you have zero links to share, omit the section entirely.

   Format (only including lines that have real values):
   ```
   🔗 Links
   — Announcement: <url>
   — <Speaker name> on X: <handle>
   — <Speaker name> on LinkedIn: <url>
   ```

### Pinned comment

Short — 1 to 3 sentences, roughly 20–60 words. The comment is a doorway, not a recap. Two jobs:

1. **Start the conversation** — ask one specific question tied to a moment in the video (referencing the timestamp helps). Don't ask generic "what did you think?" — ask "Would you have built signup this way at 1:51, or differently?"
2. **Surface critical links** — the announcement URL, anything the speaker said is "linked below". If there are no links to share, drop this part entirely — don't write `[add]` or "more links to come". Just leave it out.

If both jobs fit cleanly in 2 sentences, stop there. Don't restate the video.

Tone: matches the video's energy. Friendly, specific, like Michael talking, not a corporate caption.

### Social caption (under 200 characters)

A short caption for social platforms — Instagram, Threads, repost descriptions, the field on a video share. **Character count is a hard cap: ≤ 200 chars.** Aim for 140–190. Don't pad to hit the ceiling; under is fine.

Structure: a tight hook (often a vivid line or a concrete claim from the video) → one sentence on what's actually in it. That's usually all the room you have. No chapter markers, no links section — those belong on YouTube. No hashtags unless the platform you're targeting genuinely benefits. No CTA padding ("Watch now!") — the caption itself is the pitch.

### LinkedIn post

The goal is for a reader in the target audience (developers, founders, infra people, marketers — adjust based on the video topic) to read the first line and start nodding. Affirm a frustration or observation they already have, then connect it to what the video covers.

Patterns that work:
- "If you've ever [common frustration], you already know [implicit answer]."
- "Most [role] teams I talk to are stuck on [common problem]. It's almost always because of [non-obvious cause]."
- "[Speaker] said something on our latest video that I haven't been able to stop thinking about: [quote]. Here's why it matters."

Length: 120–250 words. Short paragraphs (1–2 lines each). Link at the bottom with a clean lead-in, not "Click here". Don't use hashtags unless the topic specifically benefits (most don't). No emojis at the start of every paragraph.

### X post

Bold up front. The "vague" we want is *under-explained*, not *abstract*. There should always be at least one concrete noun in the post — a product name, a specific action, a real number, a named person, a quoted phrase. The reader should feel "wait, what?" not "wait, what are you even talking about?"

Patterns that work:
- A claim about a real thing that sounds wrong until you watch: `email is a better auth standard for agents than anything WorkOS will ship this quarter.`
- A confession about a specific product: `we spent two years on AgentMail's UX and forgot the agent had to sign up first.`
- A specific number with thin context: `9x signup conversion after we let the agent do it itself.`

What "too vague" looks like — avoid this:
- `we forgot to build the thing that mattered most.`  ← what thing?
- `one tweet, one week, one prompt.`  ← prompt for what?

The fix is always to put a real noun back in: name AgentMail, name the agent, name the moment.

Constraints:
- Single tweet. 280 chars max including the link. Aim for under 240 of text so the link fits cleanly.
- All lowercase often works on X; match the energy of the claim.
- No hashtags. No "Watch here:" — just the link at the end on its own line.
- The post should be readable as a thought even before the link is clicked.
- The only placeholder ever allowed in an X post is `[YouTube URL]` on its own line — because the URL doesn't exist until upload. Don't use any other bracketed placeholder.

## Inferring context from a Deepgram transcript

The parser emits a clean timestamped paragraph view. To draft, you usually only need:
- The first 30 seconds (introduces speaker + topic)
- The middle (the substance — demos, arguments, examples)
- The last paragraph or two (the close, often contains the CTA)

Things to extract before writing:
- **Speaker name(s)** — usually in the first paragraph ("My name is X")
- **Product / company** — usually mentioned in the first minute
- **Core thesis** — the one sentence that, if removed, the video falls apart
- **Quotable moments** — vivid phrases, surprising stats, contrarian claims. These feed titles and the X post.
- **The fail / tension** — if there's a "but here's what went wrong" moment, that's almost always the title hook
- **The CTA** — what the speaker tells viewers to do next (try the product, sign up, etc.)

If the transcript is diarized (the parser will say `DIARIZED: yes` and prefix paragraphs with `<Speaker N>`), treat it as an interview and write copy that names both sides. If not diarized, assume single-speaker.

## What not to do

- Don't invent quotes. Every quoted line in the package must appear verbatim in the transcript.
- Don't invent timestamps. Pick from `PARAGRAPH_TIMESTAMPS` only (except `0:00`).
- Don't use em-dashes as decorative punctuation throughout. They're fine occasionally; not as a tic.
- Don't repeat the same opening pattern across the LinkedIn, X, and YouTube hook. Vary.
- Don't end with "And remember to like and subscribe" or any boilerplate. Michael's audience hates that.
- **Don't reach for heavy or academic words *in your own copy*.** "Disproportionately", "subsequently", "ostensibly", "fundamentally", "leverage" — replace them with the plain version every time. "Disproportionately better" → "way better" or "much better". "Subsequently" → "then". "Leverage" → "use". (Exception: if the speaker said the heavy word and you're quoting them verbatim, keep the quote intact. The rule is about your voice, not theirs.)
- **Don't ship `[add]` or any placeholder token in published copy.** If you don't have a URL, handle, or piece of info, drop the line that would have held it. The only exception is `[YouTube URL]` in the X post, since the URL physically doesn't exist until Michael uploads.
- **Don't write a "things I'm missing" note at the bottom of the package.** If something is missing, drop it silently. Michael will notice before publishing; no need to flag it in the deliverable.

## Quick sanity check before sending

Before posting the package in chat, verify:
- Every chapter timestamp (except 0:00) appears in `PARAGRAPH_TIMESTAMPS`.
- Chapters are in ascending time order.
- Chapter count respects the cap for the video length (≤ 6 for under 10 min, etc.).
- No chapter relies on a vague pronoun ("the thing", "it", "us", "the new one"). Each label names a specific noun.
- Five titles, all under 60 chars.
- Social caption is ≤ 200 characters.
- Pinned comment is 1–3 sentences.
- X post is ≤ 280 chars including the link, and contains at least one concrete noun.
- No `[add]` tokens anywhere. No "things missing" note at the bottom. The only allowed placeholder is `[YouTube URL]` in the X post.
- No heavy/academic word tics (disproportionately, subsequently, leverage, etc.) — swap for the plain version.
