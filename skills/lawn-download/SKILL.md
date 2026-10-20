---
name: lawn-download
description: Download a video (or a specific version) from lawn.video in Michael's signed-in Chrome via the chrome-devtools MCP, then move it to a requested folder. Use when asked to fetch, export, or download an edit, cut, or version from Lawn.
role: transformation
---

# Lawn download

This is a transformation skill. Input: a video title (optionally team, project, version, or "square"/"multicam") and a destination folder. Output: the original file at the destination.

## Rules

- Use the `chrome-devtools` MCP (`mcp__chrome_devtools__*`). Work only in `https://lawn.video` tabs. Never touch, read, or run scripts in other tabs.
- Read-only in Lawn: never delete, move, rename, upload, comment, or change visibility/sharing.
- If a page redirects to `/sign-in`, stop and ask Michael to sign in. Never type credentials.
- If Chrome shows "Allow multiple downloads?", stop and ask Michael. Don't click it yourself.
- Download one file at a time. Never log or share download URLs.

## Steps

1. `list_pages`; `select_page` an existing lawn.video tab, or `new_page` `https://lawn.video/dashboard`.
2. Locate the video:
   - **Search:** press Cmd+K ("Search folders, videos, and commands"), type the title, pick the match under "Folders and videos". Search covers the current team and latest versions only; switch teams via the "Teams" group.
   - **Browse:** `/dashboard/<team>/<project>`; click **Load more videos** until the title appears (40 per page). A **Version N** badge means older versions exist.
3. Pick the version: on the video page open the `vN` dropdown ("Video versions") and choose the row; each version has its own URL.
4. Lawn doesn't label square vs multicam. Match by title and version number. If more than one candidate fits, list them (title, vN, upload date) and ask.
5. Confirm it's ready: duration shown, no "Uploading..."/"Processing..."/"Failed". The Download button only appears when ready.
6. `take_snapshot`, then `click` the **Download video** button (`aria-label="Download video"`). It shows "Preparing..." briefly.
7. In bash, confirm a new file appeared and wait until it finishes:
   ```bash
   while ls ~/Downloads/*.crdownload >/dev/null 2>&1; do sleep 5; done
   ls -t ~/Downloads | head -3
   ```
   If nothing new shows up within ~1 minute, check `list_console_messages` on the lawn tab and report.
8. Move the newest file (named `<title>.<ext>`, non-`[A-Za-z0-9._-]` chars become `_`) to the destination: `mkdir -p "<dest>" && mv -n ~/Downloads/<file> "<dest>/"`. Report the final path and size.
