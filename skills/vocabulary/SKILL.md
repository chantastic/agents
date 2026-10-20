---
name: vocabulary
description: Use at the start of any task in Michael's work to read the vocabulary for that area, and whenever we name, rename, or argue about what something is called (video edits, cuts, publishing, video.workos.cloud, devices, events). Keeps one lean shared vocabulary in ~/.agents/vocabulary and writes a word down the moment it settles. Adapted from Matt Pocock's domain-modeling / grill-with-docs.
---

# Vocabulary

When you understand the language, you understand the process.

Keep one shared vocabulary for Michael's work so neither of us has to work out what a word means twice. `~/.agents` is the source of truth. Call it "vocabulary", never "glossary" or "terms".

## Read first
- Before working, read `~/.agents/vocabulary/INDEX.md` and the file for the area you're in (e.g. `~/.agents/vocabulary/video.md`).
- Inside a repo, also read its own `VOCABULARY.md` (or another team's `GLOSSARY.md`, if that's what the repo has) and `docs/adr/` if they exist. Repo words win inside that repo.
- If a file doesn't exist, carry on silently. Don't create files in advance.

## Use the words
- When naming anything (files, tracker rows, PR titles, messages, UI copy), use the vocabulary word. Never drift to a word listed under _Avoid_.
- If Michael uses a word differently from the vocabulary, stop and ask which he means, in one line. Don't guess and move on.
- If what he says and the code or files disagree, quote the code back and ask which is right before changing either.

## Write a word down the moment it settles
- A word is settled when Michael picks it, confirms it, or corrects one. Write it immediately, not at the end of the session.
- Entry format, one or two sentences on what the thing **is**:

  ```
  **Word**: what it is.
  _Avoid_: words we don't use for it
  ```

- Never write words Michael hasn't agreed to. A vocabulary he hasn't reviewed is worse than none. Proposals go in a `## Proposed` section at the bottom until he confirms.
- Vocabulary only: no implementation details, specs, how-tos, decisions, or scratch notes. Those belong in skills, trackers, or repos.
- Prune as often as you add. Merge duplicates, delete words nobody uses. If an area's file passes ~60 entries, it has absorbed things that aren't vocabulary.
- New area of work (one a reader wouldn't want to hold in mind at the same time)? Add a file under `~/.agents/vocabulary/` and a line in `INDEX.md`.

## Decisions (rare)
Record a decision only if it's **all three**: hard to reverse, surprising without context, and a real trade-off. Offer it, don't assume. One to three sentences (context, choice, reason) in the repo's `docs/adr/NNNN-slug.md`, or `~/.agents/decisions/` if it isn't repo work. If any test fails, say which, and don't write it.

## Report
When the vocabulary changes, say so in one line ("Added **cut** to the video vocabulary").
