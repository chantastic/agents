---
name: run-shutdown-ritual
description: Coordinate a daily shutdown ritual (à la Cal Newport's Deep Work). Two modes — triage incoming links/notes into durable storage, and wrap by scanning recent filesystem activity. Use when closing out the day or clearing browser tabs.
---

# Run Shutdown Ritual

This is a coordinator skill. It coordinates a daily shutdown ritual: gather loose inputs, scan recent activity, draft durable updates, and prepare cleanup actions without deleting anything directly.

Named after Cal Newport's shutdown ritual in *Deep Work* — the practice of reviewing every open loop at the end of a work period so your brain can actually let go. Daily, not weekly — because tabs and downloads don't wait.

## Inputs

| Input | Required | Discovery | Description |
|---|---|---|---|
| `mode` | yes | ask | `triage` or `wrap` |
| `items` | no | ask | Links, notes, and fragments for triage mode |
| `output_targets` | no | discover from file map | Durable destinations used during routing |

## Outputs

| Output | Type | Description |
|---|---|---|
| drafted updates | artifact | Proposed additions to durable files |
| routing decisions | artifact | Categorized links/notes mapped to destinations |
| trash candidates | artifact | Files moved to `~/Downloads/trash_candidates/` for manual review |

## Modes

### 1. Triage

User dumps links, notes, and fragments. The skill:

1. **Categorizes** each item by topic
2. **Routes** to the correct durable file (see File Map below)
3. **Formats** according to that file's conventions (link style, section headers, etc.)
4. **Scaffolds** the current week section in `2026.md` if it doesn't exist yet

If a link is bare (no description), fetch or infer a useful title.

### 2. Wrap

Scan the filesystem for recent activity and surface what happened today. Append to the current week's entry.

**Scan sources:**
- `~/Downloads/` — recent files, video exports, screenshots, archives
- `~/Desktop/` — scratch notes, scripts, planning docs
- `~/sites/chan.dev/` — git log for the day
- Video pipeline manifests — any `manifest.json` in recent project dirs
- Published posts — new `.md` files in `src/content/posts/`

**Draft the update:**
- Summarize today's activity into sections matching the 2026.md style
- Append to existing week section (don't overwrite previous days)
- Flag ephemeral files that should move to durable storage (or be deleted)

Present the draft. User edits, approves, or rejects sections.

### 3. Move to Durable Storage

> 🚧 **Learning mode.** We don't yet know the full scope of what "move to durable storage" means for Chan. This section will grow as we discover what access and actions are needed.

Known patterns:
- **WorkOS videos** → Google Drive: `~/Library/CloudStorage/GoogleDrive-michael.chan@workos.com/Shared drives/Marketing/Youtube Videos/`
- **Personal videos** → NAS (path TBD)
- **Screenshots/CleanShots** → no durable home yet. Leave in place until decided.
- **Scratch notes on Desktop** → merge into 2026.md or posts, then delete?

**Rules:**
- **Never delete files directly.** Move delete candidates to `~/Downloads/trash_candidates/`. User empties manually.
- Future: may support `Move to Trash` via macOS, but not yet.

**Open questions:**
- NAS mount path for personal video archive?
- Durable home for screenshots?
- Are there naming conventions for archived projects?
- Do video project dirs need to be preserved whole, or just the manifests/publish outputs?

As we do this together, update this section with answers.

## File Map

These are the durable destinations for triaged content.

| Topic | File | Notes |
|-------|------|-------|
| Weekly log (default) | `~/sites/chan.dev/src/content/posts/2026.md` | Organized by week number, descending. Current year only. |
| Watches | `~/sites/chan.dev/src/content/posts/watches.md` | Wishlist, straps, repair shops, mods, budget finds |
| TODOs / reminders | `~/Desktop/notes.md` | Short-lived. Migrate to 2026.md when acted on. |
| Blog post seeds | `~/sites/chan.dev/src/content/posts/<slug>.md` | Use `tags: [seed]` in frontmatter for fragments |

> **Expand this map** as new destinations emerge. If the user says "add this to my ___," and there's no row, ask where it lives and add it.

## Week Number & Dates

The 2026.md file uses ISO week numbers. Week sections look like:

```markdown
## 13
Mar 25-31
```

Calculate the current week from today's date. If the section doesn't exist, create it at the top (before the previous week).

## Formatting Conventions

### 2026.md
- H3 (`###`) for topic sections within a week
- Markdown links: `[Title (Source)](url)`
- Clean URLs — strip tracking params (`utm_*`, `srsltid`, `_trkparms`, etc.)
- Carryover items use `- [ ]` checkboxes
- Contextual notes are plain text bullets, no link required

### watches.md
- H2 (`##`) for categories (e.g., "Budget Field Watches")
- Bold (`**Name**`) for each watch, followed by a blank line and description
- Link wraps the watch name or goes in a separate `[link](url)` line
- Keep AliExpress/eBay URLs short (strip query params)

### Blog post seeds
- Frontmatter: `title`, `date`, `tags: [seed, from:<source>]`
- Short — a few paragraphs max
- End with `---` and `(seed from [source](/source))`

## What This Skill Does NOT Do

- It doesn't publish or commit. It edits files locally.
- It **never deletes files**. Trash candidates go to `~/Downloads/trash_candidates/`.
- It doesn't reorganize existing content — only appends.
