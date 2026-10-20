# Video references

## Final Cut Pro / FCPXML
- [FCPXML Reference](https://developer.apple.com/documentation/professional-video-applications/fcpxml-reference): Apple's authority on FCPXML elements and attributes (assets and media-reps, clips, effects and filters, keyframes, timing). _Tip_: the page renders with JavaScript; if a fetch comes back empty, use the JSON form at `https://developer.apple.com/tutorials/data/documentation/professional-video-applications/fcpxml-reference.json`.
- [FCPXML Document Type Definition](https://developer.apple.com/documentation/professional-video-applications/document-type-definition): the DTD versions to validate against. _Tip_: the page lags (it showed 1.10 in Oct 2026); FCP 12.x writes FCPXML 1.14, and the current DTD ships inside the Final Cut Pro app bundle. Passing the DTD isn't enough on its own; Final Cut also checks frame boundaries, effect IDs, and that media resolves on import.

## Rip / public video extraction
- [YouTube.js configuration](https://ytjs.dev/guide/getting-started): anonymous session, visitor data and cache options. Check the installed version's `Session` types before using option names: 18.2.0 uses `fail_fast`, although the guide spells it `fast_fail`. Fetching a real session requires `generate_session_locally: false`; use `fail_fast: true` to prevent silent synthetic fallback.
- [yt-dlp PO Token Guide](https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide): client-specific token requirements and why public/playable metadata alone does not establish a successful media download.
- [Final Cut Pro release notes](https://support.apple.com/en-us/102825): which FCPXML version each Final Cut release reads and writes.
