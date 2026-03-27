---
name: audit-youtube-channel
description: "Comprehensive YouTube channel analysis using yt-dlp. Use when auditing a YouTube channel's content catalog, analyzing video formats, assessing performance, or developing content strategy. Accepts a channel URL or @handle."
role: transformation
---

# YouTube Audit Skill

This is a transformation skill. It analyzes a YouTube channel and produces a structured audit report.

Analyze any YouTube channel's full video catalog. Extracts metadata via `yt-dlp`, categorizes content formats, assesses performance, and generates a structured report.

## Prerequisites

- `yt-dlp` must be installed

## Input

Channel URL or @handle: `@WorkOS`, `https://www.youtube.com/@WorkOS`

## Directory Structure

```
~/analysis/youtube/{channel}/
  context.md              # Persists across runs
  catalog.json            # Raw yt-dlp dump
  videos.json             # Structured data
  enriched.jsonl          # Individual video metadata
  thumbnails/             # Downloaded images
  transcripts/            # Subtitle text
  {YYYY-MM-DD} {channel} {summary}.md  # Dated reports
```

## Workflow

### Phase 0: Context
Check for `context.md`. If missing, ask about goals, audience, team, funnel, constraints, history. If exists, read it first.

### Phase 1: Catalog Pull
```bash
yt-dlp --dump-single-json --flat-playlist "{URL}/videos" > catalog.json
```
Extract into `videos.json`.

### Phase 2: Enrichment (Optional)
Individual metadata (~3s/video): `upload_date`, `like_count`, `comment_count`, `chapters`, `tags`. Enrich selectively.

### Phase 3: Transcripts (Optional)
`yt-dlp --write-sub --write-auto-sub --sub-lang en`

### Phase 4: Thumbnails (Optional)
Download for visual format analysis.

### Phase 5: Analysis
- **Format categorization**: Duration clusters, title patterns, thumbnail styles
- **Performance**: Views, engagement, duration sweet spots
- **Strategic**: Goal alignment, capacity fit, evidence-based recommendations

Always read `context.md` first. Distinguish data-backed claims from best-practice suggestions.

### Phase 6: Report
Save as `{YYYY-MM-DD} {channel} {summary}.md`.

## Returning Users
- Don't re-ask context questions
- Refresh catalog data
- Reference previous reports
- Create new dated report

## Notes
- Flat-playlist lacks `upload_date` — enrich for chronological analysis
- View counts are point-in-time snapshots
- Add `sleep 1` between requests to avoid rate limiting
