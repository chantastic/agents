---
name: run-youtube-upload
description: Coordinate a YouTube upload from run-video-publish outputs. Reads publish/ assets (titles, description, captions, thumbnails), walks through selection with the user, and uploads via YouTube Data API v3. Use after run-video-publish when ready to upload.
---

# Run YouTube Upload

This is a coordinator skill. It coordinates the final YouTube upload using the assets produced by `run-video-publish`.

It reads the `publish/` directory, presents choices to the user (title, thumbnail, privacy), and calls the YouTube upload service.

## Required Environment

- `YOUTUBE_CLIENT_SECRET_PATH` — path to OAuth `client_secret.json` from Google Cloud Console
- `uv` — installed (manages Python dependencies automatically via inline script metadata)
- One-time auth: run `uv run ~/.agents/services/youtube.py auth` to authorize

### First-Time Setup

If the user hasn't set up YouTube API access yet, walk them through it:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project (or use existing)
3. Enable **YouTube Data API v3** under APIs & Services
4. Go to **Credentials** → Create **OAuth 2.0 Client ID** (type: Desktop app)
5. Download the JSON → save somewhere stable (e.g., `~/.config/youtube/client_secret.json`)
6. Set `YOUTUBE_CLIENT_SECRET_PATH` in their shell config
7. Run auth:

```bash
YOUTUBE_CLIENT_SECRET_PATH=~/.config/youtube/client_secret.json \
  uv run ~/.agents/services/youtube.py auth
```

This opens a browser, user authorizes, tokens are saved next to the client secret.

## Inputs

| Input | Required | Discovery | Description |
|---|---|---|---|
| `publish_dir` | yes | discover: `publish/` in cwd | Directory of assets produced by `run-video-publish` |
| `video_file` | yes | ask or discover alongside publish assets | Final export video to upload |

This skill expects a `publish/` directory from `run-video-publish`:

```
publish/
├── titles.json         ← title options with reasoning
├── description.md      ← SEO description with chapters
├── captions.srt        ← subtitles
├── brief.json          ← topics (used as tags)
└── thumbnails/
    ├── concepts.json   ← thumbnail concepts
    ├── frames/         ← extracted frames
    └── T001.png ...    ← generated thumbnails (if available)
```

Also needs the **export video file** (the same `.mp4/.mov` used by `run-video-publish`).

## Outputs

| Output | Type | Description |
|---|---|---|
| uploaded video | artifact | The completed YouTube upload configured with chosen assets |
| selection record | artifact | The chosen title, thumbnail, privacy, and metadata confirmed during the run |

## Process

### Step 1: Verify auth

Check that credentials are working:

```bash
uv run ~/.agents/services/youtube.py auth
```

If this fails, guide the user through setup (see First-Time Setup above).

### Step 2: Locate assets

Find the `publish/` directory and the export file. Read:

1. `publish/titles.json` — title options
2. `publish/description.md` — description text
3. `publish/brief.json` — topics for tags
4. `publish/captions.srt` — subtitle file
5. `publish/thumbnails/` — available thumbnails

If any are missing, note what's missing but don't block — only the video file and a title are truly required.

### Step 3: Select title ⛔ STOP — wait for user response before continuing

Present the title options from `publish/titles.json` to the user. Show each title with its style and reasoning. Ask the user to pick one, or provide their own.

Example presentation:

```
Title options from video-publish:

1. "I Switched from Claude Code to This" (curiosity_gap)
   → Pi is unnamed — creates a click incentive.

2. "Claude Code Has a Vendor Lock-In Problem" (confrontational)
   → Takes a stance, provokes engagement.

3. "How to Use Any AI Model in One Terminal" (how-to)
   → Clear value proposition for search.

Which title? (or type your own)
```

### Step 4: Review description ⛔ STOP — wait for user response before continuing

Show the contents of `publish/description.md`. Ask the user if it looks good or if they want to edit anything. If they want changes, make them to a copy — don't modify the publish output.

If editing is needed, write the modified version to a temp file for the upload.

### Step 5: Select thumbnail ⛔ STOP — wait for user response before continuing

List available thumbnails in `publish/thumbnails/`. If generated images exist (T001.png, etc.), present them. If only frames exist, present those. If `concepts.json` exists, show the concept descriptions alongside.

Ask the user to pick one, or skip (YouTube will auto-generate).

### Step 6: Confirm upload settings ⛔ STOP — wait for user response before continuing

Before uploading, summarize the plan:

```
Upload summary:
  Video:       export.mp4 (245 MB)
  Title:       "How to Use Any AI Model in One Terminal"
  Description: publish/description.md (reviewed ✓)
  Tags:        Pi, Claude Code, vendor lock-in, multi-model
  Thumbnail:   publish/thumbnails/T002.png
  Captions:    publish/captions.srt
  Privacy:     unlisted
  Category:    Science & Technology (28)

Proceed?
```

Privacy is always **unlisted**. User reviews on YouTube Studio before manually publishing.

### Step 7: Normalize audio

Normalize the export to -14 LUFS (YouTube's recommended loudness target, EBU R128) using a two-pass ffmpeg loudnorm filter. This does **not** modify the original export — it writes a normalized copy.

**Pass 1 — measure:**

```bash
ffmpeg -i "<export_path>" -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 | grep -A 15 '"input_i"'
```

This prints measured loudness values as JSON. Extract `input_i`, `input_tp`, `input_lra`, and `input_thresh`. Note: `tail -12` is unreliable here — ffmpeg's output length varies by file and version. `grep` for `input_i` is more robust.

**Pass 2 — normalize:**

```bash
ffmpeg -i "<export_path>" \
  -af loudnorm=I=-14:TP=-1:LRA=11:measured_I=<input_i>:measured_TP=<input_tp>:measured_LRA=<input_lra>:measured_thresh=<input_thresh>:linear=true \
  -c:v copy \
  -c:a aac -b:a 192k \
  "<export_dir>/<selected_title>.mp4"
```

The output filename is the selected title, sanitized for filesystem safety (replace `/`, `\`, `:`, `"`, `?`, `*`, `<`, `>`, `|` with `-`). For example, if the title is "I Found the NeoVim of AI Coding Agents", the file is `I Found the NeoVim of AI Coding Agents.mp4`. This is the file that gets uploaded — YouTube uses the filename as a signal for small channels.

Key flags:
- `-c:v copy` — video stream is untouched (fast, no re-encode)
- `linear=true` — uses linear normalization (no dynamic compression)
- `-b:a 192k` — YouTube-appropriate AAC bitrate

Report the before/after LUFS to the user:

```
Audio normalized: -22.3 LUFS → -14.0 LUFS (target)
Output: I Found the NeoVim of AI Coding Agents.mp4
```

If the measured loudness is already within 1 LUFS of -14 (i.e., between -15 and -13), skip normalization but still copy the file to the title-named version (so the filename signal is preserved). Tell the user:

```
Audio already at -14.2 LUFS — normalization not needed.
Copied to: I Found the NeoVim of AI Coding Agents.mp4
```

### Step 8: Upload video

```bash
uv run ~/.agents/services/youtube.py upload \
  --file "<normalized_or_original_export_path>" \
  --title "<selected_title>" \
  --description-file "<description_path>" \
  --tags "<comma,separated,tags>" \
  --privacy unlisted \
  --category 28
```

Parse the JSON output to get the `video_id` and `url`.

### Step 9: Upload captions

If `publish/captions.srt` exists:

```bash
uv run ~/.agents/services/youtube.py caption \
  --video-id "<video_id>" \
  --file "publish/captions.srt" \
  --language en \
  --name "English"
```

### Step 10: Set thumbnail

If a thumbnail was selected:

```bash
uv run ~/.agents/services/youtube.py thumbnail \
  --video-id "<video_id>" \
  --file "<selected_thumbnail_path>"
```

**Note:** Custom thumbnails require the YouTube account to be verified. If this fails with a permission error, let the user know they need to verify their account at https://www.youtube.com/verify.

### Step 11: Report

Present the final result:

```
✅ Upload complete!

  URL:     https://youtu.be/ABC123
  Studio:  https://studio.youtube.com/video/ABC123/edit
  Status:  unlisted (processing)

Next steps:
  • Video is processing — check status in YouTube Studio
  • Review in Studio, then set to public when ready
  • Run content-twitter / content-linkedin / content-recap for promotion
```

Optionally check processing status:

```bash
uv run ~/.agents/services/youtube.py status --video-id "<video_id>"
```

## Making Public

This skill **cannot** set videos to public. The service enforces this — `public` is not an accepted privacy value.

To make a video public, the user must do it manually in **YouTube Studio** → video → Visibility → Public.

This is intentional. Publishing is a human decision.

## Hard Rules

1. **NEVER delete a video.** The service has no delete command. Do not attempt to delete videos through any API call, workaround, or external tool. Deletion is a manual-only operation in YouTube Studio. There are no exceptions to this rule.

2. **All uploads are unlisted.** Every video uploaded through this skill must use `--privacy unlisted`. Do not pass `public` — the service will reject it. The user reviews in YouTube Studio and publishes manually when ready.

## Notes

- **Don't modify publish outputs.** If the user wants description edits, write a modified copy to a temp file.
- **Tags come from brief.json topics.** The `topics` array in the content brief maps directly to YouTube tags.
- **Category 28 = Science & Technology.** This is the default. Ask if the user wants a different category only if the content clearly doesn't fit.
- **Resumable uploads.** The service handles large files with 50MB chunk resumable uploads. No special handling needed in the skill.
- **Scheduling.** If the user wants to schedule, use `--publish-at` with an ISO 8601 timestamp. The service sets privacy to private (required for scheduling). The video becomes public at the scheduled time — confirm the user understands this before using it.

## TODO

- **Channel selection.** The service currently uploads to the default channel for the authenticated account (`mine=True`). Accounts with multiple channels (brand accounts) can't pick a destination. Add `--channel-id` support to the service and a channel picker to the skill. The YouTube API supports this via the upload `insert` call or `onBehalfOfContentOwner` for CMS accounts.

- **Test & Compare (watch for API support).** YouTube Studio's Test & Compare feature lets creators upload up to 3 title/thumbnail combinations and A/B test them. Currently Studio-only — no YouTube Data API v3 endpoint. If this gets API support, skip the title/thumbnail selection steps entirely: upload the top 3 combinations from `titles.json` and `thumbnails/` and let YouTube's data pick the winner.
