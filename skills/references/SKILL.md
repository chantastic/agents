---
name: references
description: Use at the start of any task in Michael's work to check for authoritative references (specs, official docs, API references) for that area, and whenever we lean on an outside source to get something right (file formats, APIs, platform rules). Keeps a lean shared list of trusted links in ~/.agents/references and adds one when it proves useful. Companion to the vocabulary skill.
---

# References

Keep one shared list of the sources we trust for Michael's work, so neither of us has to hunt for the right spec twice. `~/.agents` is the source of truth.

## Read first
- Before working, read `~/.agents/references/INDEX.md` and the file for the area you're in (e.g. `~/.agents/references/video.md`).
- When a reference covers what you're about to do, follow it over memory, blog posts, or guesses. If it disagrees with the code or a tool's behavior, say so before changing either.
- If a file doesn't exist, carry on silently. Don't create files in advance.

## Add a reference when it earns it
- Add one when Michael points to it, or when it settled a real question while we worked. Write it right away.
- Entry format, one line on what it's authoritative for, plus any tip for reading it:

  ```
  - [Title](https://url): what it's the authority on. _Tip_: how to read it, if not obvious.
  ```

- Prefer the primary source (the vendor's own spec or docs) over summaries. One best link per question; drop links that turned out less useful.
- References only: no notes, how-tos, or copied spec text. Those belong in skills or repos.
- New area of work? Add a file under `~/.agents/references/` and a line in `INDEX.md`, using the same area names as the vocabulary.

## Report
When the references change, say so in one line ("Added the FCPXML reference to video references").
