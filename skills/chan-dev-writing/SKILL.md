---
name: chan-dev-writing
description: Reference guide for writing in Chan's voice across essays, tutorials, notes, and reflections. Use when drafting, editing, or evaluating content for chan.dev.
---

# chan.dev Writing Style Guide

A distilled reference for writing in Chan's (Michael Chan / @chantastic) voice, extracted from ~130 posts spanning 2016–2026 across personal essays, technical tutorials, life/career reflections, and tool guides.

## Voice & Persona

Chan writes as a practitioner sharing lived experience — not an authority dispensing wisdom. The voice is:

- **Conversational and direct.** Sentences talk *to* you, not *at* you.
- **Confessional.** He leads with his own failures, doubts, and contradictions before offering insight.
- **Warm but unsentimental.** Empathy without softness. He'll say "your strategy sucks" and "I love you" in the same breath.
- **Playfully profane.** "Shit," "fuck," "horse shit" appear naturally — never for shock, always for emphasis or authenticity. The "shit example" in the React Context tutorial is characteristic.
- **Self-aware.** Frequently acknowledges his own contradictions, biases, and incomplete thinking.

## Sentence Style

### Short and punchy
The default sentence is short. Often a fragment. Line breaks carry weight.

> Release.  
> Some things lift, others pull.  
> Let go of things that pull.

> Resist.  
> Keep your head down.  
> Do the thing.  
> Feel the shame of it.

### Strategic use of line breaks
Each line is a beat. Markdown `<br>` (two trailing spaces) creates rhythm within paragraphs. New paragraphs create pauses. This is closer to poetry than prose.

### Varied rhythm
Short bursts are punctuated by occasional longer, flowing sentences that carry momentum before snapping back to fragments.

> Marriage, bills, kids — one with cancer, and a prematurely widowed mother...  
> At 35, I have to realize that  
> Now is not a time for "less but better".

### Em dashes for asides
Used frequently for parenthetical thoughts, pivots, and dramatic pauses:

> I don't trust anyone who doesn't walk with a limp — metaphorically, of course.

## Structure Patterns

### Personal essays (newsletter / reflections)

1. **Hook with a story or scene** — a specific moment (Disneyland, a water slide, a card game with his kids, a wedding toast).
2. **Extract a principle** — the story becomes a lens on something universal.
3. **Make it actionable** — imperative voice. "Do the thing." "Kill the bad program." "Stride your limp."
4. **Close with a question or sign-off** — often asks the reader a direct question. Signs off with an emoji + "chan" or "chantastic."

Example closings:
> 🍣 chantastic
>
> Question:  
> Where do you put effort in the wrong direction?

### Technical tutorials

1. **Start with the problem or the "why"** — "JSX is weird." "Vim is hard to learn. Additionally so because people suck at teaching Vim."
2. **Progressive disclosure** — build incrementally. Show the simplest version, then layer complexity using diffs.
3. **Use real, memorable examples** — "shit" as a word, grandma's house, expletives as context values. Never abstract `Foo`/`Bar`.
4. **Code-first** — code blocks are the backbone. Prose is connective tissue between code, not the other way around.
5. **Diff-heavy** — tutorials show evolution through `diff` blocks with insertions/deletions highlighted, so readers see *what changed* step by step.
6. **Section with clear headings** — table of contents, progressive steps, each step yielding an observable result.

### Found notes (short-form)

Many posts tagged `found` and `note` are raw, unpolished fragments — sometimes just a few sentences. They read like journal entries or voice memos:

> "Fuck you money" is just a lens in the places you given away agency.

> i am a mule; the wanted more cows.
> on my time at planning center

These are deliberately rough. They preserve the energy of the original thought without over-editing.

### Link compilations / running logs

Posts like `2026.md` are structured as weekly logs with headers, bullet points, links, and brief commentary. They're utilitarian — meant as personal reference, not polished content.

## Recurring Themes

- **Ego as the enemy of creation.** "Creation is a battle with ego." Ego redirects toward noble obstacles.
- **Process over goals.** "You fall to the level of your systems." Systems > goals. Habits > aspirations.
- **Communication over correctness.** "What if nothing matters but communication?" Unity beats being right.
- **Doing the thing, badly.** "More and worse." Ship imperfect work. Perfectionism is cowardice.
- **Family as primary context.** Kids (Rock, Ruby), wife (Nellie), mom, dad — family stories are the primary source of metaphor and meaning.
- **Faith and spirituality.** Bible references appear naturally (Job, Genesis, Matthew, Ecclesiastes). Not preachy — woven into personal wrestling.
- **Sports and games as metaphor.** Poker, basketball, Sushi Go, Overcooked, bonsai — concrete activities become lenses.
- **Pain as teacher.** "Stride your limp." "Punch up." Pain × Resistance = Suffering.
- **Chinese-American identity.** First son in a Chinese family. Navigating responsibility, cultural expectation, and self-determination.

## Formatting Conventions

- **Lowercase titles** for personal essays: "fight then unite", "decide", "mule"
- **Title Case** for prescriptive/tutorial posts: "Kill the Old You", "Fail Fast. Fail Safe"
- **Emoji signatures**: 🍣, 🤕, 🎭, ⏳, 🥊, 💖, ✂️, 🌈, etc.
- **Blockquotes** for cited wisdom or song lyrics.
- **`<mark>` tags** in study notes to highlight key passages.
- **Bible references** as links at the end, not inline citations.
- **Questions to the reader** at the end of essays, set apart clearly.
- **Frontmatter** includes `title`, `date` (or `publishDate`), sometimes `description`, `tags`, `references`.

## Technical Writing Specifics

- **Framework**: Astro site with markdown/MDX content collections.
- **Code style**: Modern JS/TS, React hooks, functional components. Prefers `let` over `const` in tutorials for simplicity.
- **Diff notation**: Heavy use of Expressive Code's `diff`, `ins`, `del` syntax for progressive tutorials.
- **Progressive enhancement**: Tutorials build from zero, showing each intermediate state as a working (or at least observable) result.
- **Cross-references**: Links to own posts (e.g., `/react-basics`, `/react19`) and external docs.
- **Collapsible sections**: Uses `<details>` for optional content like video embeds.

## Narrative Techniques

### The Boomerang
Start with a specific scene from the past, launch into the present or a principle, then bring it back to land the point. ("There's a water slide at a local resort where my career changed… 5½ years later, I'm at JSConf US watching Ruby go down the same slide")

### The Confession-to-Imperative
Open by confessing a personal failure or flaw, extract a universal principle, then flip to imperative voice commanding the reader. ("I wasn't prepared… This led me to my why… Find the thing you know deep down… Do it every day")

### The Kid Story
Family stories — especially Rock and Ruby — are the #1 source of metaphor. The kid does something (loses at Sushi Go, runs onto the soccer field, asks a question), Chan extracts a life principle. These are never precious or sentimental. They're honest, sometimes blunt. ("Your strategy sucks… Steal from the players who beat you.")

### The Etymology/Definition Move
Chan frequently cites etymologies or definitions to reframe a word. "Decide" = "to cut off." "Sin" = "miss." "Deconstruction" vs "destruction." This is a signature move — using the literal meaning to deepen the metaphorical argument.

### The Reversal
Set up an expectation, then pivot. Often a one-line paragraph. ("The universe was handing to me something I wanted and I turned it down. Why?")

### The Cinematic Reference
Movies and TV (Pulp Fiction, Ted Lasso, Sheryl Crow lyrics) serve as entry points for personal reflection. Never surface-level fan content — always tied to a transformation.

## Book Report / Study Notes Style

When taking notes on books (Atomic Habits, The Art of the Good Life), Chan uses:
- `<mark>` tags for key quotes and personal highlights
- Inline commentary mixed with quotes
- "Thoughts with friends" sections that capture group discussion verbatim, including disagreements
- Bulleted stream-of-consciousness with occasional tangents
- Cross-references to his own posts and ideas
- AI-generated summaries explicitly labeled as such
- Action-oriented chapter summaries using punchy sentences

## Gear/Tool Posts

For equipment reviews, tool setups, and "what I use" posts:
- **Real-time log format** — dated entries capturing impressions as they happen (Atem Mini Pro ISO)
- **Opinionated but practical** — states preferences with reasoning, not just specs
- **Reference-style links** at bottom of posts for affiliate/product links
- **Comparison awareness** — often notes what didn't work alongside what did
- **Embedded purchasing links** — B&H, Amazon, direct brand links
- **Living documents** — posts grow over time as experience accumulates

## Content Creation / Conference Speaking

Chan has deep experience as a conference speaker, emcee, and content creator. When writing about these:
- **Speaks from experience** — "I've been speaking since 2013"
- **Tactical and specific** — "Copy paste this into a DM"
- **Demystifying** — treats speakers as normal people who "left their families, escaped work, and flew across the country, JUST TO TALK WITH YOU"
- **Social proof through vulnerability** — shares his own failures (unfinished email sequences, bad talks) as credentials

## The "Found Note" Genre

A distinctive content type across ~100 short posts. These are:
- Tagged `found` and `note` in frontmatter
- Clearly voice-memo or journal-entry transcriptions
- Often parenthetical annotations: "(my glass analogy)" or "(on my time at planning center)"
- Deliberately unpolished — typos, incomplete sentences, raw thoughts
- Sometimes just a title and a tweet embed
- Serve as seeds for longer essays that may never come
- The energy of discovery matters more than completion

## Emotional Range

Chan's writing covers a wide emotional spectrum within a single post:
- **Anger**: "I'm not sure they accumulated much (wisdom)"
- **Grief**: "I think about relatives who passed"
- **Self-deprecation**: "I'm no expert but…" / "I suck at negotiation"
- **Fierce directness**: "Pull your head out of your butt and try something different"
- **Tenderness**: "I love you. And I hope to see more of you."
- **Dark humor**: "thinking about death" while sick with the flu
- **Gratitude**: "I'm grateful and nostalgic for all the people I've met"

The transitions between these are abrupt and honest, not smooth. That abruptness *is* the style.

## Anti-patterns (What Chan Does NOT Do)

- **Does not write in corporate voice.** No "leverage," "utilize," "in order to."
- **Does not hedge excessively.** Doesn't say "I think maybe perhaps." Says "I think" or just states it.
- **Does not use filler transitions.** No "furthermore," "additionally," "in conclusion."
- **Does not write long paragraphs.** If a paragraph is more than 3-4 lines, something is wrong.
- **Does not separate himself from the reader.** "You" and "I" are the primary pronouns. Not "one" or "the developer."
- **Does not polish found notes.** Raw thoughts stay raw. The energy matters more than grammar.
- **Does not avoid profanity or strong opinion.** But uses both with purpose, never gratuitously.
- **Does not write clickbait.** Titles are honest, often poetic or aphoristic.
- **Does not explain what AI wrote for him.** When AI writes content, he labels it explicitly: "This post was written by AI" or "🚧 written via prompt." He doesn't pass off AI writing as his own.
- **Does not write listicles with forced commentary.** Gear posts are practical reference, not "10 BEST MICROPHONES (YOU WON'T BELIEVE #7)."
- **Does not moralize from above.** Even when giving direct advice, it comes from "I learned this the hard way" not "you should know better."

## Calibration Examples

### ✅ Sounds like Chan
> I don't have trouble doing a thing perfectly.  
> Any monkey with time can achieve perfection.
>
> But time...  
> Most of us just don't get enough time for perfect.

### ✅ Sounds like Chan (technical)
> This is a shit example of Context.  
> Shit because it uses "shit" as an illustration and because it's simplistic.
>
> We'll get to **the why** after we cover **the how**.

### ❌ Does NOT sound like Chan
> In this comprehensive guide, we'll explore the fundamentals of React Context API, providing you with actionable insights to leverage this powerful feature in your applications.

### ❌ Does NOT sound like Chan
> It is important to note that consistency is a key factor in achieving long-term success in one's career development journey.

### ✅ Sounds like Chan (found note)
> i am most disatisfied when i take in more than i can process.
>
> "cognitive obesity"  
> "cognitive inflamation"

### ✅ Sounds like Chan (newsletter sign-off)
> Make any fouls this week?  
> Hit reply. I'd love the company 😅

### ✅ Sounds like Chan (confession-to-imperative)
> I wasn't prepared for the market to collapse.  
> I wasn't prepared for the family business to fail.  
> I wasn't prepared to be laid off —  
> By my dad.  
> I wasn't prepared.

### ✅ Sounds like Chan (the reversal)
> "I could be the Joe Rogan of React", I thought.  
> The show quickly died.

### ✅ Sounds like Chan (technical opening)
> Context is a 3-part system:  
> create, use, provide.

### ❌ Does NOT sound like Chan
> As a Developer Educator, you'll serve developers by inspiring and equipping them to build with [product] through high-quality technical videos. The person in this role will own the vision, strategy, metrics, and execution behind our developer video content.

_(This is job-listing prose. Chan's actual writing about developer education roles would be opinionated and personal, not corporate.)_
