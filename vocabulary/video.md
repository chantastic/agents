# Video vocabulary

Video post-production and publishing for WorkOS, including the video app (video.workos.cloud, repo workos/youtube).

**Video**: the parent record for one piece of content (a talk, panel, demo). Uploading the first cut creates it. One video has many cuts, presenters and assets.
_Avoid_: content (too generic, collides with content license), upload (uploads are cuts)

**Cut**: one rendered video file belonging to a video. Each has a format, a kind (primary, clip or edit) and its own targets. One video, many cuts.
_Avoid_: upload, artifact

**Primary cut**: the full-length master cut, usually 16:9, typically published to YouTube only.

**Format**: a cut's frame shape (16:9, 1:1 square, 9:16 vertical). Only the shape; it says nothing about which part of the video the cut shows.
_Avoid_: format when you mean the kind of cut

**Clip**: a cut that is one section of the video, a contiguous time range of the primary cut. Clip is also the broad word for clipping a section out of a larger piece of content.

**Edit**: a high-potency distillation of the video that can rearrange, compress or remix it, rather than one contiguous section. Borrowed from TikTok. Typically social-only.

**Presenter**: a person on stage for a video. Speaker, panelist, moderator and host are roles. One video, many presenters. Each presenter can get their own share kit.

**Asset**: a non-video file attached to a video or a cut (thumbnail, captions, slides, photos, Drive links).
_Avoid_: artifact (that's files produced by agent runs)

**Target**: a destination a cut is published to (YouTube, X, LinkedIn, TikTok, Instagram and so on). Each cut has its own targets, in any combination.

**Publication**: one instance of publishing a cut to a target. A cut can be published to the same target more than once.

**Share kit**: the public /share page and post kit sent to a presenter (or a general kit) so they can repost a video first-party. Separate from the /videos admin pages.

**Short**: packaging, not a kind of cut. How a vertical cut is presented on a target, like YouTube #Shorts. Closest to an Instagram Reel.
_Avoid_: reel, vertical

## Proposed
Not yet confirmed. Each needs Michael's OK before moving above this line.

**Direction**: a distinct creative approach to the same footage, e.g. the four OOH directions (match-cut, readable, POV hunt, ROX-style).
_Avoid_: concept, variant, version

**Tracker**: the project's spreadsheet that is the source of truth for each video's status, dates and URLs.
