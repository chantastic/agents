#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "google-api-python-client>=2.0",
#   "google-auth-oauthlib>=1.0",
#   "google-auth-httplib2>=0.2",
# ]
# ///
"""YouTube Data API v3 upload service.

Handles OAuth 2.0 auth, video upload (resumable), caption upload,
thumbnail upload, and metadata setting.

Environment:
  YOUTUBE_CLIENT_SECRET_PATH — path to OAuth client_secret.json
  (tokens stored alongside as youtube_tokens.json)

Usage:
  uv run youtube.py auth                         # One-time OAuth setup
  uv run youtube.py upload [options]             # Upload video + metadata
  uv run youtube.py caption --video-id ID --file FILE  # Upload captions
  uv run youtube.py thumbnail --video-id ID --file FILE  # Set thumbnail
  uv run youtube.py status --video-id ID         # Check processing status

All commands output JSON to stdout. Logs go to stderr.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Credentials / token paths
# ---------------------------------------------------------------------------

def get_credentials_dir() -> Path:
    secret_path = os.environ.get("YOUTUBE_CLIENT_SECRET_PATH")
    if not secret_path:
        log.error("YOUTUBE_CLIENT_SECRET_PATH not set")
        sys.exit(1)
    p = Path(secret_path)
    if not p.exists():
        log.error(f"Client secret not found: {p}")
        sys.exit(1)
    return p.parent


def get_client_secret_path() -> Path:
    secret_path = os.environ.get("YOUTUBE_CLIENT_SECRET_PATH")
    if not secret_path:
        log.error("YOUTUBE_CLIENT_SECRET_PATH not set")
        sys.exit(1)
    p = Path(secret_path)
    if not p.exists():
        log.error(f"Client secret not found: {p}")
        sys.exit(1)
    return p


def get_token_path() -> Path:
    return get_credentials_dir() / "youtube_tokens.json"


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",  # captions
    "https://www.googleapis.com/auth/youtube",  # thumbnails, metadata
]


def get_authenticated_service():
    """Return an authenticated YouTube Data API v3 service."""
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    token_path = get_token_path()
    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            log.info("Refreshing expired token...")
            creds.refresh(Request())
        else:
            log.info("Starting OAuth flow — browser will open...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(get_client_secret_path()), SCOPES
            )
            # Google may return fewer scopes than requested (e.g., youtube
            # subsumes youtube.force-ssl). Tell oauthlib that's OK.
            os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
            creds = flow.run_local_server(port=0)

        # Save tokens
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, "w") as f:
            f.write(creds.to_json())
        log.info(f"Tokens saved to {token_path}")

    return build("youtube", "v3", credentials=creds)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_auth(_args):
    """Authenticate and save tokens."""
    service = get_authenticated_service()
    # Verify by fetching channel info
    resp = service.channels().list(part="snippet", mine=True).execute()
    items = resp.get("items", [])
    if items:
        channel = items[0]["snippet"]
        result = {
            "status": "authenticated",
            "channel": channel.get("title", "unknown"),
            "channel_id": items[0]["id"],
        }
    else:
        result = {"status": "authenticated", "channel": "unknown"}
    print(json.dumps(result, indent=2))


def cmd_upload(args):
    """Upload a video with metadata."""
    from googleapiclient.http import MediaFileUpload

    service = get_authenticated_service()

    # Read description from file or string
    description = args.description or ""
    if args.description_file:
        description = Path(args.description_file).read_text()

    # Parse tags
    tags = []
    if args.tags:
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    body = {
        "snippet": {
            "title": args.title,
            "description": description,
            "tags": tags,
            "categoryId": str(args.category),
            "defaultLanguage": args.language or "en",
            "defaultAudioLanguage": args.language or "en",
        },
        "status": {
            "privacyStatus": args.privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    # Add scheduled publish time if provided
    if args.publish_at:
        body["status"]["publishAt"] = args.publish_at
        body["status"]["privacyStatus"] = "private"  # Required for scheduling

    file_path = Path(args.file)
    if not file_path.exists():
        log.error(f"Video file not found: {file_path}")
        sys.exit(1)

    file_size = file_path.stat().st_size
    log.info(f"Uploading {file_path.name} ({file_size / 1024 / 1024:.1f} MB)...")

    media = MediaFileUpload(
        str(file_path),
        mimetype="video/*",
        resumable=True,
        chunksize=50 * 1024 * 1024,  # 50MB chunks
    )

    request = service.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            log.info(f"Upload progress: {pct}%")

    video_id = response["id"]
    result = {
        "status": "uploaded",
        "video_id": video_id,
        "url": f"https://youtu.be/{video_id}",
        "studio_url": f"https://studio.youtube.com/video/{video_id}/edit",
        "privacy": body["status"]["privacyStatus"],
        "title": args.title,
    }

    if args.publish_at:
        result["scheduled_publish"] = args.publish_at

    log.info(f"Upload complete: {result['url']}")
    print(json.dumps(result, indent=2))


def cmd_caption(args):
    """Upload captions/subtitles for a video."""
    from googleapiclient.http import MediaFileUpload

    service = get_authenticated_service()

    caption_path = Path(args.file)
    if not caption_path.exists():
        log.error(f"Caption file not found: {caption_path}")
        sys.exit(1)

    # Determine format from extension
    ext = caption_path.suffix.lower()
    mime_map = {".srt": "application/x-subrip", ".vtt": "text/vtt"}
    mime = mime_map.get(ext, "application/octet-stream")

    body = {
        "snippet": {
            "videoId": args.video_id,
            "language": args.language or "en",
            "name": args.name or "English",
            "isDraft": False,
        },
    }

    media = MediaFileUpload(str(caption_path), mimetype=mime)

    log.info(f"Uploading captions: {caption_path.name} for video {args.video_id}...")
    response = (
        service.captions()
        .insert(part="snippet", body=body, media_body=media)
        .execute()
    )

    result = {
        "status": "uploaded",
        "caption_id": response["id"],
        "video_id": args.video_id,
        "language": body["snippet"]["language"],
    }

    log.info("Captions uploaded")
    print(json.dumps(result, indent=2))


def cmd_thumbnail(args):
    """Set a custom thumbnail for a video."""
    from googleapiclient.http import MediaFileUpload

    service = get_authenticated_service()

    thumb_path = Path(args.file)
    if not thumb_path.exists():
        log.error(f"Thumbnail file not found: {thumb_path}")
        sys.exit(1)

    # Determine mime type
    ext = thumb_path.suffix.lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
    mime = mime_map.get(ext, "image/png")

    media = MediaFileUpload(str(thumb_path), mimetype=mime)

    log.info(f"Setting thumbnail: {thumb_path.name} for video {args.video_id}...")
    response = (
        service.thumbnails()
        .set(videoId=args.video_id, media_body=media)
        .execute()
    )

    items = response.get("items", [{}])
    result = {
        "status": "uploaded",
        "video_id": args.video_id,
        "thumbnails": items[0] if items else {},
    }

    log.info("Thumbnail set")
    print(json.dumps(result, indent=2))


def cmd_status(args):
    """Check video processing status."""
    service = get_authenticated_service()

    response = (
        service.videos()
        .list(part="status,processingDetails,snippet", id=args.video_id)
        .execute()
    )

    items = response.get("items", [])
    if not items:
        result = {"status": "not_found", "video_id": args.video_id}
    else:
        video = items[0]
        status = video.get("status", {})
        processing = video.get("processingDetails", {})
        result = {
            "status": "found",
            "video_id": args.video_id,
            "url": f"https://youtu.be/{args.video_id}",
            "upload_status": status.get("uploadStatus"),
            "privacy_status": status.get("privacyStatus"),
            "processing_status": processing.get("processingStatus"),
            "processing_progress": processing.get("processingProgress", {}),
            "title": video.get("snippet", {}).get("title"),
        }

    print(json.dumps(result, indent=2))


def cmd_update(args):
    """Update video metadata (title, description, tags, privacy)."""
    service = get_authenticated_service()

    # Fetch current video data
    response = (
        service.videos()
        .list(part="snippet,status", id=args.video_id)
        .execute()
    )

    items = response.get("items", [])
    if not items:
        log.error(f"Video not found: {args.video_id}")
        sys.exit(1)

    video = items[0]
    snippet = video["snippet"]
    status = video["status"]

    # Apply updates
    if args.title:
        snippet["title"] = args.title
    if args.description:
        snippet["description"] = args.description
    if args.description_file:
        snippet["description"] = Path(args.description_file).read_text()
    if args.tags:
        snippet["tags"] = [t.strip() for t in args.tags.split(",") if t.strip()]
    if args.privacy:
        status["privacyStatus"] = args.privacy

    body = {
        "id": args.video_id,
        "snippet": snippet,
        "status": status,
    }

    log.info(f"Updating video {args.video_id}...")
    response = service.videos().update(part="snippet,status", body=body).execute()

    result = {
        "status": "updated",
        "video_id": args.video_id,
        "url": f"https://youtu.be/{args.video_id}",
        "title": response["snippet"]["title"],
        "privacy": response["status"]["privacyStatus"],
    }

    log.info("Video updated")
    print(json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="YouTube upload service")
    sub = parser.add_subparsers(dest="command", required=True)

    # auth
    sub.add_parser("auth", help="Authenticate with YouTube")

    # upload
    p_upload = sub.add_parser("upload", help="Upload a video")
    p_upload.add_argument("--file", required=True, help="Video file path")
    p_upload.add_argument("--title", required=True, help="Video title")
    p_upload.add_argument("--description", help="Description text")
    p_upload.add_argument("--description-file", help="Description file path")
    p_upload.add_argument("--tags", help="Comma-separated tags")
    p_upload.add_argument(
        "--privacy",
        default="unlisted",
        choices=["unlisted", "private"],
        help="Privacy status (default: unlisted). Public must be set manually in YouTube Studio.",
    )
    p_upload.add_argument("--category", type=int, default=28, help="Category ID (28=Science & Tech)")
    p_upload.add_argument("--language", default="en", help="Language code")
    p_upload.add_argument("--publish-at", help="ISO 8601 scheduled publish time")

    # caption
    p_caption = sub.add_parser("caption", help="Upload captions")
    p_caption.add_argument("--video-id", required=True)
    p_caption.add_argument("--file", required=True, help="SRT or VTT file")
    p_caption.add_argument("--language", default="en")
    p_caption.add_argument("--name", default="English", help="Caption track name")

    # thumbnail
    p_thumb = sub.add_parser("thumbnail", help="Set custom thumbnail")
    p_thumb.add_argument("--video-id", required=True)
    p_thumb.add_argument("--file", required=True, help="Image file (PNG/JPG)")

    # status
    p_status = sub.add_parser("status", help="Check processing status")
    p_status.add_argument("--video-id", required=True)

    # update
    p_update = sub.add_parser("update", help="Update video metadata")
    p_update.add_argument("--video-id", required=True)
    p_update.add_argument("--title")
    p_update.add_argument("--description")
    p_update.add_argument("--description-file")
    p_update.add_argument("--tags")
    p_update.add_argument(
        "--privacy",
        choices=["unlisted", "private"],
        help="Privacy status. Public must be set manually in YouTube Studio.",
    )

    args = parser.parse_args()

    commands = {
        "auth": cmd_auth,
        "upload": cmd_upload,
        "caption": cmd_caption,
        "thumbnail": cmd_thumbnail,
        "status": cmd_status,
        "update": cmd_update,
    }

    # SAFETY: This service intentionally has no delete command.
    # Videos must never be deleted programmatically. Deletion is
    # a manual-only operation performed in YouTube Studio.

    commands[args.command](args)


if __name__ == "__main__":
    main()
