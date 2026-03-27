# Eval: Pi First Look

**Date**: 2026-03-25
**Source**: `~/Downloads/2026-03-24 2026 test/2026-05-22 Pi First Look.mp4`
**Skill**: youtube-upload
**Duration/Scope**: 14:04 video, 1.04 GB, full upload pipeline

---

## Summary

The upload completed successfully — video, captions, and thumbnail all landed. Process adherence was mostly good, but the title/description/thumbnail selection was batched into a single questionnaire instead of the sequential review the skill prescribes. The audio normalization pass caught a severely quiet export (-39.2 LUFS) and corrected it. One concern: the `tail -12` approach for extracting loudnorm JSON nearly missed `input_i` — required a second pass with `grep`.

## What went well

- **Auth verified first.** Confirmed channel identity ("chantastic") before touching anything else.
- **All assets located in parallel.** Read titles, description, brief, and thumbnails simultaneously — no wasted round trips.
- **Audio normalization caught a real problem.** Export was at -39.2 LUFS, 25 dB below target. Without normalization, the video would have been nearly inaudible on YouTube.
- **Captions and thumbnail uploaded in parallel** after getting the video_id.
- **Upload confirmation step was clear.** Table format summarized all settings before proceeding.
- **Hard rules followed.** Privacy was unlisted. No deletion attempted.
- **Original export was not modified.** Normalized copy written to a new title-named file.

## What went poorly

### 1. Batched title + description + thumbnail selection

The skill prescribes three sequential steps: (3) select title, (4) review description, (5) select thumbnail. I combined description review and thumbnail selection into a single questionnaire. This is more efficient but violates the skill's intent — the description review should be a focused moment where the user reads the full text, not a checkbox alongside thumbnail picking. The user might skim past description issues when it's one of multiple choices.

**Should have done:** Presented title first (did this correctly), then showed description with a dedicated "looks good / edit" prompt, then thumbnail separately.

### 2. Loudnorm JSON extraction was fragile

Used `tail -12` per the skill, which cut off `input_i` from the output. Required a second `grep` call to get the full measurement JSON. This is a known fragility — ffmpeg's output length varies depending on the stream info and warnings above the JSON block.

**Should have done:** Used `grep -A 15 "input_i"` from the start, or parsed with a more robust approach. The skill's `tail -12` example is a rough guide, not a guarantee.

### 3. Thumbnail presented without images

The skill says to present thumbnail options. I listed the concepts from `concepts.json` with text descriptions, but the reference frames (M01-M08.jpg) were available and could have been shown as images using the read tool. The user picked M07 (Doom) based on text alone — showing the actual frame would have been a better experience.

**Should have done:** Displayed the selected reference frames as images so the user could make a visual choice.

### 4. No processing status check

Step 11 says to "optionally check processing status." I didn't offer this. For a 1 GB upload, processing takes time — confirming it's in progress would have been a nice closer.

## Stage-by-stage assessment

### Step 1: Verify auth
| Metric | Value |
|---|---|
| Status | ✅ Passed |
| Channel | chantastic (UCXpmUxvG37qpckRHdkstf5w) |

**Process adherence**: Followed exactly.

### Step 2: Locate assets
| Metric | Value |
|---|---|
| Assets found | 5/5 (titles, description, brief, captions, thumbnails) |
| Missing | None |
| Generated thumbnails | None (frames only) |

**Process adherence**: Followed exactly. All reads done in parallel.

### Step 3: Select title
| Metric | Value |
|---|---|
| Options presented | 7 |
| User selected | #1 "I Found the NeoVim of AI Coding Agents" |
| Custom title | No |

**Process adherence**: Followed. Showed style and reasoning for each. Allowed custom input.

### Step 4: Review description
| Metric | Value |
|---|---|
| Presented | Yes |
| User approved | Yes (no edits) |

**Process adherence**: Partially followed — batched with thumbnail instead of dedicated review step.

### Step 5: Select thumbnail
| Metric | Value |
|---|---|
| Options presented | 4 concepts + skip |
| Frames shown as images | No (text only) |
| User selected | M07.jpg (Doom in Pi) |

**Process adherence**: Partially followed — concepts described, but reference frames not displayed visually.

### Step 6: Confirm upload
| Metric | Value |
|---|---|
| Summary shown | Yes (table format) |
| User confirmed | Yes |

**Process adherence**: Followed. All settings visible before proceeding.

### Step 7: Normalize audio
| Metric | Value |
|---|---|
| Input LUFS | -39.2 |
| Output LUFS | -14.0 (target) |
| Delta | +25.2 dB |
| Method | Two-pass loudnorm, linear=true |
| Re-encode | Audio only (AAC 192k), video copy |
| Output file | `I Found the NeoVim of AI Coding Agents.mp4` |

**Process adherence**: Followed. Two-pass method, linear normalization, video stream copied, title-named output file. Required retry on measurement extraction.

### Step 8: Upload video
| Metric | Value |
|---|---|
| File size | 1045.8 MB |
| Upload method | Resumable (50 MB chunks) |
| video_id | XzZgLDL0wZY |
| Privacy | unlisted |
| Category | 28 (Science & Technology) |

**Process adherence**: Followed exactly.

### Step 9: Upload captions
| Metric | Value |
|---|---|
| Format | SRT |
| Language | en |
| Status | ✅ Uploaded |

**Process adherence**: Followed exactly. Run in parallel with thumbnail.

### Step 10: Set thumbnail
| Metric | Value |
|---|---|
| File | M07.jpg (Doom frame) |
| Status | ✅ Uploaded |

**Process adherence**: Followed exactly. Run in parallel with captions.

### Step 11: Report
| Metric | Value |
|---|---|
| URL shown | ✅ |
| Studio link shown | ✅ |
| Next steps listed | ✅ |
| Processing status checked | ❌ Not offered |

**Process adherence**: Mostly followed. Skipped optional status check.

## Patterns

- **Batching user choices for efficiency at the cost of attention.** Combining description review + thumbnail into one prompt is a UX shortcut that could cause the user to miss issues. This is a tension between "don't waste the user's time" and "give each decision its own space." For a skill that's fundamentally a review-and-confirm flow, each decision deserves focus.
- **Fragile ffmpeg output parsing.** The `tail -12` pattern is unreliable. This will break again on different ffmpeg versions or files with different stream counts.

## Learning hooks

```json
{
  "feedback_hooks": [
    {
      "category": "ux_flow",
      "question": "Did batching description + thumbnail feel rushed, or was it efficient?",
      "artifacts": ["questionnaire responses"],
      "how_to_compare": "Ask user if they actually read the full description before approving"
    },
    {
      "category": "thumbnail_selection",
      "question": "Would seeing the actual frame images have changed the thumbnail choice?",
      "artifacts": ["publish/thumbnails/frames/M07.jpg"],
      "how_to_compare": "Show frames in a future run and see if selection differs"
    },
    {
      "category": "audio_normalization",
      "question": "Was -39.2 LUFS an export issue (e.g., FCP export settings) or expected?",
      "artifacts": ["ffmpeg loudnorm output"],
      "how_to_compare": "Check the user's FCP export settings for future projects",
      "resolved": "User forgot to boost in FCPX. One-off, not a settings issue. The normalization step in the skill handles this fine — no upstream fix needed."
    },
    {
      "category": "channel_destination",
      "question": "Did the upload go to the right channel?",
      "artifacts": ["auth response showing 'chantastic'"],
      "how_to_compare": "User confirms in YouTube Studio"
    }
  ]
}
```

## Recommendations

1. **Split description review and thumbnail selection into separate prompts.** Don't batch. The skill prescribes sequential steps for a reason — each is a review moment.

2. **Show thumbnail frames as images.** Use the `read` tool on `.jpg` files to display them inline. Text descriptions of frames are a poor substitute for seeing them.

3. **Fix loudnorm JSON extraction.** Replace `tail -12` with `grep -A 15 '"input_i"'` or pipe through a JSON parser. The current approach is version-dependent and fragile. Consider updating the skill doc.

4. **Offer processing status check.** After a large upload, ask if the user wants to check processing status. It's a 5-second call that provides useful closure.

5. **Investigate the -39.2 LUFS export.** That's abnormally quiet — typical FCP exports land around -16 to -24 LUFS. The user may have an export preset issue that should be caught upstream (in video-publish or video-pipeline) rather than corrected here.

6. **Channel selection (already in TODO).** The user surfaced this during the run — their account has multiple channels. This needs to be addressed in the service before the next multi-channel upload.
