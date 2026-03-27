# Diff Eval: Pi First Look — My Edit vs. Chan's Edit

**Date**: 2026-03-25
**Source**: `2026-03-23 11-57-49.mp4` (64m 13s)
**My edit**: 17.2 min (308 segments)
**Chan's edit**: 14.1 min (260 clips)
**Delta**: Chan cut 190s (3.2 min) more — 18.4% tighter than mine

---

## Summary

I was **too conservative in the polish stage**. Chan cut an additional ~3 minutes, almost entirely editorial pacing cuts. The biggest lesson: **when the speaker reads screen content aloud or narrates Claude's output, that's almost always cuttable** — the viewer can read the screen. My polish stage identified pacing drag as the #1 category but didn't go far enough.

---

## What Chan cut that I kept

### 1. Reading screen content aloud (~55s)

The single biggest category. When the speaker reads Pi's feature list from the terminal:
- Context files, compaction features (13.6s)
- Extension capabilities, skills, packages (12.4s)  
- Prompt templates, themes, Pi packages (7.3s)
- Four modes, standard chat (4.1s)
- Programmatic integrations (2.0s)
- Pi capabilities rundown (5.1s)

**Learning**: The viewer can see the screen. Reading documentation aloud adds nothing. In future polish passes, flag any utterance where the speaker is narrating visible text as a pacing_drag candidate.

### 2. Claude's recommendations/output (~50s)

Chan cut most of the section where Claude analyzes the speaker's existing skills and makes pipeline recommendations:
- "Port your skills to Pi format, highest value, lowest effort..." (12s)
- "Skills colon syntax for Pi" (5.1s)
- "A pipeline skill would chain them. Record, rough cut, silence removal, b roll, one command..." (17.6s)
- "Talks about scripts, publishing, gaps" (11.8s)

**Learning**: Claude's output is interesting to the speaker but not to the viewer. The viewer hasn't seen the speaker's skills — they have no context for recommendations about porting them. Only the *reaction* to Claude's output matters, not the output itself. In future edits, when the speaker narrates LLM output, keep the reaction/assessment, cut the narration.

### 3. Sharing/export exploration (~25s removed in aggregate)

The sharing feature exploration — trying to share, seeing the gist, trying to open HTML, asking about shareable URLs — was compressed significantly. Chan kept the key moments (shared → got URL → looks nice) but cut the fumbling in between.

**Learning**: Exploration loops follow a pattern: *try → fumble → discover → react*. The viewer needs *try → discover → react*. The fumble steps are only interesting if they teach something. "It doesn't seem useful in this state" and "Are we able to view just..." is the fumble — cut it.

### 4. Steering/evaluative test section (~12s)

I had already cut the joke section and WorkOS test in polish, but Chan went further:
- Cut "I didn't really see a difference because this wasn't a huge task" (4.8s)
- Cut "let's give it something more evaluative" (3.5s)
- Cut the alt-enter explanation (3.6s)

**Learning**: I kept the *conclusion* of the steering test but Chan cut even that. If the test was inconclusive and the feature explanation is redundant (already shown earlier), the entire section can go.

### 5. Extension loading attempts (~16.5s more)

Beyond what I already cut in polish, Chan further trimmed:
- "So load an extension with the extension flag" (3.8s)
- Download attempts (6.7s)
- Questionnaire searching + apology for ugliness (7.9s)

**Learning**: I was right to cut the confusion loop but wrong to keep the attempted paths. The viewer doesn't need to see `pi --extension questionnaire.ts` fail — just the resolution.

### 6. Transitions and fragments (~15s)

Small cuts throughout: "Okay. We'll come back to that", "Let's check out headline features", "I think when I kick this off", etc.

**Learning**: Transitional phrases between sections are often empty bridges. If the next section starts with enough context, the transition is unnecessary.

---

## What Chan restored that I cut

### JSON RPC mention (1.7s at 660.0-661.7)

I removed "JSON RPC" as a false start building to "for programmatic integrations." Chan kept it. In the flow, it reads: "...one shot answers, great for piping. Oh, that's interesting. JSON RPC for programmatic integrations." The "JSON RPC" label actually adds information — it names the specific mode.

**Learning**: Not every short utterance before a longer one is a false start. If it adds a distinct piece of information (a name, a label), it's a list item, not a false start.

### End section (~4.4s at 3791.2-3795.6)

Chan restored some content near the end that I had cut. Likely part of the closing flow.

---

## Zoom comparison

| Metric | My edit | Chan's edit |
|---|---|---|
| Zoom count | 27 | 56 |
| Zoom density | 1.6/min | 4.0/min |
| Scale range | 1.40-1.65 (as zoom params) | 0.25x-1.53x magnification (FCP Content Scale) |

### Key zoom learnings

**Note:** The DesignStudio title plugins use their own Content Scale where values >1.0 mean zoomed in (1.25 = 1.25x magnification). This is different from FCP's transform scale where <1.0 means zoomed in. The values below are plugin Content Scale, read directly as magnification.

1. **Chan uses 2x the zooms I suggested.** Even though the user said "more zooms than fewer," I was still conservative at 27. Chan went to 56 — roughly one every 15 seconds.

2. **Chan's zoom scales are similar to mine in actual magnification.** Most screen zooms are 1.25-1.35x (plugin Content Scale). My zooms at 1.40-1.65x were slightly more aggressive. The bigger difference is *frequency* — Chan zooms twice as often.

3. **Chan uses consistent zoom levels per section.** Many adjacent clips share the same scale and similar anchors (e.g., multiple clips at 1.25x/middle-left). This creates a visual rhythm rather than every zoom being a unique event.

4. **Extreme zooms are rare but purposeful.** The 4.0x zoom (Clip_271 at 3301.2s) and 1.89x zoom (Clip_267 at 3219.6s) are outliers — likely used for very specific emphasis moments (e.g., zooming into a small UI element). The 1.5x zooms are used for camera/face-cam shots.

5. **Many zooms have no animation in/out.** Chan set `Animation In = 0` and `Animation Out = 0` on many zooms, making them instant punch-ins rather than smooth transitions. This is more aggressive than my "smooth" style suggestions.

6. **Webcam/camera zooms use ~0.65-0.75 Content Scale** (which in plugin terms means zoomed OUT / less magnified — these are the title clips where the source is already a face-cam crop). Standard screen zooms cluster around 1.25-1.35x.

---

## Calibration data for future runs

### Editorial cuts: my accuracy

| Category | My precision | My recall | Notes |
|---|---|---|---|
| Duplicate takes | High | High | Both edits agree on all duplicate removals |
| False starts | High | Medium | I missed that "JSON RPC" wasn't a false start |
| Screen-reading | Low | Low | I kept ~55s of screen-narration Chan cut |
| Claude output narration | Low | Low | I kept ~50s of LLM output narration Chan cut |
| Exploration fumbling | Medium | Medium | I caught the big loops but kept too many small attempts |
| Transitions | Low | Medium | I kept many empty bridge phrases |

### Zoom calibration

Note: All scales below are DesignStudio plugin Content Scale (>1.0 = zoomed in). Not FCP transform scale.

| Parameter | My default | Chan's actual | Recommended |
|---|---|---|---|
| Frequency | ~1.6/min | ~4.0/min | 3-4/min |
| Base scale (screen) | 1.40-1.50 | 1.25-1.35 | 1.25-1.35 |
| Base scale (camera) | 1.45-1.65 | 1.50 | 1.50 |
| Emphasis scale | 1.60-1.75 | up to 4.0 for extreme | 1.5-2.0, rare |
| Style | mix of smooth/punch | mostly instant (no anim in/out) | default to instant |
| Consistency | unique per zoom | grouped by section | group by section |

---

## Recommendations for skill updates

### video-polish

1. **Add "screen narration" as an explicit pacing_drag subcategory.** When the speaker reads visible terminal/browser content, flag it. This alone would have caught ~55s.
2. **Add "LLM output narration" as a subcategory.** When the speaker narrates Claude/GPT output, keep only reactions and assessments.
3. **Be more aggressive on exploration loops.** Cut the failed attempts, keep try → discover → react.
4. **Cut transitional bridge phrases** unless they introduce genuinely new context.

### video-zoom

1. **Double the zoom frequency** to 3-4 per minute.
2. **Slightly lower default scale** to 1.25-1.35x for screen content, ~1.50x for camera. (DesignStudio plugin Content Scale, not FCP transform.)
3. **Default to instant (no animation in/out)** instead of smooth.
4. **Group zooms by section** — use consistent scale/anchor within a section, vary between sections.
5. **Reserve 1.5x+ for emphasis, 2x+ for extreme moments only.**

### video-cut

1. **"JSON RPC" was not a false start.** When a short utterance adds a distinct label or name before a longer description, it's a list item. Don't remove it just because the next utterance is more complete.
