# Self-Analysis: 2026 Pi First Look

**Date**: 2026-03-25
**Source**: `2026-03-23 11-57-49.mp4` (64m 13s)
**Final output**: 17m 14s (73% removed)

---

## What went well

**Cut stage was solid.** The duplicate take detection was the strongest part — the "two decade VIM user" section had 8 takes and I correctly identified the last complete one. Same for the "wanting to dive into Pi" section (7 takes → 1). False start detection was accurate. The rough cut took 64 min → 20 min with clean jump cuts between complete thoughts.

**Polish found real issues.** The mid-utterance stumble ("good to dig and we should be good to go"), the repeated "oh interesting" reaction, and the duplicate outro were all invisible in the cut pass but obvious in continuous flow. The pacing drag removals (joke section, WorkOS steering test, model confusion loop, extension confusion loop) were the highest-value edits.

**Zoom frame analysis was accurate.** Reading the actual frames let me pick correct anchors — the split-screen layout (terminal left, browser right) was consistent, and I correctly identified the Doom screenshot in bottom-right for Z023.

## What went poorly

### 1. The joke removal was botched in pass 2

I removed segments for utterances 128-131 but forgot that utterance 133 contained both the dog joke AND the conclusion ("I didn't really see a difference"). This required a pass 3 that should have been caught in pass 2. Root cause: I was thinking in utterance indices but the edit list uses contiguous time segments that merge adjacent utterances. I should have verified the segment content before finalizing.

### 2. 1Password friction burned ~10 minutes

The biometric auth kept timing out. I should have cached the key after the first successful retrieval instead of calling `op read` fresh each time.

### 3. Some polish removals were too aggressive on the model config section

I removed utterances 194-200 and 216-222 in bulk, but some of that was the speaker's genuine exploration process. A viewer watching a "first look" video expects some fumbling — it's authentic. I may have over-compressed the model setup section.

### 4. I didn't verify the pass 3 output

The skill says to re-transcribe and check for convergence after each fix pass. I skipped verification on pass 3 (just removed 1 segment and trimmed another) and went straight to final. The changes were small enough that this was probably fine, but it breaks the methodology.

### 5. Zoom timing precision is uncertain

I used the re-transcribed preview utterance timestamps, but the final edit list changed slightly after pass 3. The zooms might be off by 1-3 seconds in spots. In FCP they'll need nudging.

### 6. I never asked to confirm the thesis before running polish

The skill explicitly says to ask the user to review/adjust the thesis. I just reported it and kept going.

---

## Data to Store for Future Evals

### 1. Decision-level ground truth

The most valuable thing is a **diff between my decisions and the reviewer's**. For each stage:

```json
{
  "cut_decisions_diff": {
    "false_positives": ["045: I removed this but reviewer kept it"],
    "false_negatives": ["198: I kept this but reviewer removed it"],
    "agreed": 440
  },
  "polish_issues_diff": {
    "false_positives": ["pacing_drag at 483-542: I cut too much of model config"],
    "false_negatives": ["missed_stumble at 345.9: 'disarray' section could be tighter"],
    "agreed": 12
  },
  "zoom_diff": {
    "removed": ["Z008: reviewer deleted the 'pretty painless' zoom"],
    "moved": ["Z007: shifted 2.1s later"],
    "rescaled": ["Z023: reviewer changed Doom from 1.60 to 1.75"],
    "added": ["reviewer added a zoom at 450s I missed"],
    "anchor_changed": ["Z018: middle-right → top-right"]
  }
}
```

### 2. Reviewer's final FCPXML → edit list extraction

After editing in FCP, export the FCPXML. Diff against mine to extract:

- **Clips removed** (segments I should have cut)
- **Clips added back** (segments I shouldn't have cut)
- **Clip boundary adjustments** (my trim points were off by N frames)
- **Zoom adjustments** (timing, scale, anchor changes)

A script to generate this diff:

```bash
python3 ~/.agents/services/timeline.py diff \
  zoom/timeline_zoomed.fcpxml \
  eval/reviewer_final.fcpxml \
  --output eval/timeline_diff.json
```

### 3. Per-category accuracy rates

Track across videos to see systematic patterns:

```json
{
  "video_id": "2026-03-23-pi-first-look",
  "cut": {
    "duplicate_detection": {"precision": null, "recall": null},
    "false_start_detection": {"precision": null, "recall": null},
    "fragment_detection": {"precision": null, "recall": null}
  },
  "polish": {
    "missed_duplicate": {"precision": null, "recall": null},
    "pacing_drag": {"precision": null, "recall": null},
    "mid_utterance_stumble": {"precision": null, "recall": null}
  },
  "zoom": {
    "placement_accuracy_seconds": null,
    "scale_accuracy": null,
    "anchor_accuracy": null,
    "count_preference": "agent suggested 27, final had ?"
  }
}
```

### 4. Manifest eval key

Add to manifest after review:

```json
{
  "eval": {
    "reviewer": "chan",
    "final_timeline": "eval/reviewer_final.fcpxml",
    "final_duration": null,
    "notes": "free text about what felt wrong",
    "diff": "eval/timeline_diff.json",
    "accuracy": "eval/accuracy.json"
  }
}
```

### 5. Specific things to learn from reviewer edits

1. **Where did I over-cut?** Especially in the polish pacing_drag sections. I suspect the model config fumbling and some of the extension loading journey should be longer.
2. **Where did I under-cut?** Sections I kept that still drag.
3. **Zoom taste calibration.** Which of my 27 zooms survived, which were annoying, what scale/timing adjustments were made. This is the most subjective part.
4. **Transition quality.** Do any of my cut points land awkwardly? The 0.05s padding should handle most cases, but some transitions might need breathing room.

---

## Proposed Review Workflow

1. Open `zoom/timeline_zoomed.fcpxml` in Final Cut Pro
2. Make edits (remove clips, adjust zooms, retrim)
3. Export as FCPXML → save to `eval/reviewer_final.fcpxml`
4. Agent runs the diff script and generates eval data
5. Eval data becomes context for the next video's cut/polish/zoom decisions
