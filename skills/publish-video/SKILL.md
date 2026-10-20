---
name: publish-video
description: Use when taking a finished or near-finished video edit (full YouTube video or Short) to published — confirming tracker status, pre-publish checks, export, upload to video.workos.cloud, YouTube publish, social coordination, and recording URLs/dates back in the project tracker.
---

# Publish Video

Take a finished/near-finished edit to published, for full videos and Shorts. The project tracker is the single source of truth — read it first, write to it last.

## 1. Confirm the item in the tracker
- Find the project folder's tracker (e.g. `tracker.xlsx` / `tracker.csv`). One tracker per project folder.
- Locate the row for this video/Short. Confirm title, format (full / Short), edit status, target publish date, owner.
- If status only exists in chat history or a session, write it into the tracker now.

## 2. Pre-publish checks (block until resolved)
- **Approvals:** speaker, partner, company comms, panel approvals as applicable. Record who approved and when.
- **Factual claims:** product claims, numbers, customer names verified.
- **Rights:** archival footage, music, logos, third-party screenshots cleared.
- **On-screen sensitive data:** scan for keys, emails, customer data, internal URLs. Demo accounts are usually fine — **confirm, don't assume**, before deciding to blur or not.

See `references/checklist.md`.

## 3. Export
- **Full video:** 16:9 (e.g. 1920×1080 or 3840×2160), H.264/H.265, AAC audio.
- **Short:** vertical 9:16 (1080×1920), ≤60s **or per current YouTube limits — verify before export**.
- Export captions (SRT/VTT) where available.

## 4. Upload and publish
- Upload to **video.workos.cloud** (team video app). If its MCP tools are available:
  - `list_videos` — check it isn't already uploaded.
  - `create_video_upload` → upload → `finalize`.
  - `get_video_status` until processed; `get_video_package` for the deliverable package.
  - `delete_video` only for mistaken/duplicate uploads, with confirmation.
- Publish to YouTube with:
  - **Title** (clear, searchable), **description** (summary, links, CTA), **thumbnail**, **chapters** (full videos; first at 0:00), tags, captions, visibility/schedule.
  - Shorts: vertical, short title, link to the related full video.

## 5. Social coordination
- Align with the Head of Growth Marketing's publishing plan — she schedules X and LinkedIn.
- Clarify per post whether it's a **standalone cut** or the **Short**; they're different assets.
- Before scheduling, check what's already live on the YouTube channel and X (@WorkOS).

## 6. After publishing
- Record in the tracker: YouTube URL, X post URL, publish date(s), Short URL(s), status = Published.
- Verify publicly visible: open the URLs logged out / in a private window; check processing, thumbnail, chapters, captions.

## Gotchas
- **Status lived in an agent session, not a shared file.** Always write status to the tracker.
- **Growth's plan and the edit plan drifted on dates.** Reconcile both before scheduling; the tracker gets the agreed date.
- **Shorts got forgotten.** Schedule each Short explicitly as its own tracker row with its own date.
- **An X post of the full demo is not the Short.** Track them separately.
- **Check what's already posted** (YouTube channel + X @WorkOS) before scheduling anything, to avoid duplicates.
