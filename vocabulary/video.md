# Video vocabulary

Video post-production and publishing for WorkOS, including the video app (video.workos.cloud, repo workos/youtube).

**Video**: the parent record for one piece of content (a talk, panel, demo). Uploading the first cut creates it. One video has many cuts, presenters and assets.
_Avoid_: content (too generic, collides with content license), upload (uploads are cuts)

**Cut**: one rendered video file belonging to a video. Each has a format, a kind (primary, alt, clip or edit) and its own platforms. One video, many cuts.
_Avoid_: upload, artifact

**Primary cut**: the full-length master cut, usually 16:9, typically published to YouTube only.

**Format**: a cut's frame shape (16:9, 1:1 square, 9:16 vertical). Only the shape; it says nothing about which part of the video the cut shows.
_Avoid_: format when you mean the kind of cut

**Alt**: a cut with the same content as the primary cut in a different format, like a vertical or square version of the full talk.
_Avoid_: edit (an edit changes the content; an alt only changes the format)

**Clip**: a cut that is one section of the video, a contiguous time range of the primary cut. Clip is also the broad word for clipping a section out of a larger piece of content. A clip can be any format; it isn't inherently vertical.

**Edit**: a high-potency distillation of the video that can rearrange, compress or remix it, rather than one contiguous section. Borrowed from TikTok. Typically social-only.

**Presenter**: a person on stage for a video. Speaker, panelist, moderator and host are roles. One video, many presenters. Each presenter can get their own share kit.

**Asset**: a non-video file attached to a video or a cut (thumbnail, captions, slides, photos, Drive links).
_Avoid_: artifact (that's files produced by agent runs)

**Platform**: a destination a cut is published to (YouTube, X, LinkedIn, TikTok, Instagram and so on). Each cut has its own platforms, in any combination.
_Avoid_: target (the app's older name for this)

**Publication**: one instance of publishing a cut to a platform. A cut can be published to the same platform more than once.

**Share kit**: the public /share page and post kit sent to a presenter (or a general kit) so they can repost a video first-party. Separate from the /videos admin pages.

**Short**: packaging, not a kind of cut. How a vertical cut is presented on a platform, like YouTube #Shorts. Implies a vertical (9:16) format. A reel is the Instagram equivalent.
_Avoid_: vertical (that's a format, not a short)

## Next version (settled 2026-10-23)
The restructure of the video app. These replace the terms above once it ships; until then the terms above describe the live app.

**Piece**: the top-level record for one piece of content. Only a title is required. Holds timelines today; articles, posts and threads may join later. Every piece has a speaker kit automatically, never created or deleted by hand.
_Avoid_: video (as the parent record), project

**Timeline**: the primitive. One sequence of content with its own timestamps: transcript, chapters, presenters, title and description live here. The full talk is a timeline; a clip or an edit is another timeline that records the timeline it came from (a clip also records its time range). Defaults cascade only when a timeline is created; nothing stays live-linked.
_Avoid_: cut, video (for the content-level record)

**Export**: an actual video file on a timeline, sharing its timestamps: a 16:9, a 9:16 reframe, a burned-in-captions version. Removing an intro bumper changes the timestamps, so that is a new timeline, not an export. Replaces alt and format.
_Avoid_: rendition, alt, format, variant, version

**Service**: the entity a platform belongs to: YouTube, Instagram, LinkedIn, X. A connection attaches to a service.
_Avoid_: company, platform (for the entity)

**Platform**: a surface within a service: YouTube Upload, YouTube Shorts, Instagram Reels. Holds only best practices: prompts, ideal transcoding, aspect and length rules, what its algorithm needs (e.g. Shorts must be vertical). Never holds account details. Chooses the export it needs, and can make one just in time (e.g. a 9:16 with the widescreen frame on a blurred background).
_Avoid_: target, destination

**Connection**: the account integration with a service (e.g. the WorkOS YouTube channel). Kept separate so account details never live on a platform. A service with one connection is chosen silently.

**Placement**: a first-class, linked record of one export posted to one platform through one connection, with its own copy, status, link, publish time and performance. The same export can have several placements on the same platform. Replaces publication. Durable history: a placement outlives the piece, timeline and export it came from. Deleting those unlinks the placement (its links become empty) and never deletes it or takes the post down; the placement keeps a snapshot of what was published.
_Avoid_: publication, post (for the record)

**Timeline processing / Export processing**: processing splits by what it acts on. Timeline processing works on content (transcription, presenters, chapters, copy drafts) once per timeline; export processing works on the file (encoding, reframing, burned-in captions, thumbnail) once per export.

## Proposed
Not yet confirmed. Each needs Michael's OK before moving above this line.

**Direction**: a distinct creative approach to the same footage, e.g. the four OOH directions (match-cut, readable, POV hunt, ROX-style).
_Avoid_: concept, variant, version

**Tracker**: the project's spreadsheet that is the source of truth for each video's status, dates and URLs.
