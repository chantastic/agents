# FCPXML References

## adjustment-clip-zooms-reference.fcpxml

FCP 1.14 round-trip export showing adjustment clips with zoom transforms.
Source: user-corrected export from FCP (March 2026).

### Key patterns

**Adjustment clip on lane 1** (connected to asset-clip):
```xml
<video ref="r5" lane="1" offset="..." name="..." start="3600s" duration="..." role="adjustments">
    <adjust-transform position="X Y" anchor="X Y" scale="S S"/>
</video>
```

**position = anchor** — pins that point in place while scaling around it.

**middle-center (no offset)** — omit position/anchor, just scale:
```xml
<adjust-transform scale="S S"/>
```

**Keyframed zoom — push** (continuous slow zoom, no return):
```xml
<adjust-transform>
    <param name="scale">
        <keyframeAnimation>
            <keyframe time="3600s" value="1 1" curve="smooth"/>
            <keyframe time="3610s" value="1.5 1.5"/>
        </keyframeAnimation>
    </param>
</adjust-transform>
```

**Keyframed zoom — smooth** (ease in, hold, ease out):
```xml
<adjust-transform>
    <param name="scale">
        <keyframeAnimation>
            <keyframe time="3600s" value="1 1" curve="smooth"/>
            <keyframe time="3600.5s" value="1.5 1.5" curve="smooth"/>
            <keyframe time="3609.7s" value="1.5 1.5" curve="smooth"/>
            <keyframe time="3610s" value="1 1"/>
        </keyframeAnimation>
    </param>
</adjust-transform>
```

When using an anchor with animated styles, keyframe `position` and `anchor` params
alongside `scale` — animate from `"0 0"` (centered) to the anchor coordinates so the
zoom eases toward the focal point rather than jumping to it.

`curve="smooth"` on a keyframe tells FCP to use eased (Catmull-Rom) interpolation
from that keyframe to the next. Omit for linear. Apply to the leading keyframe of
each transition for speed-ramped feel.

### FCP coordinate system

- Frame height = 100 FCP units, origin at center
- Y: up = positive. X: right = positive
- Half-height = 50. Half-width = (width/height) × 50 (88.8889 for 16:9)
- FCP inspector displays values in pixels (FCP units × height/100)

### 3×3 anchor presets (FCP units)

```
top-left:    (-88.89,  50)    top-center:    (0,  50)    top-right:    (88.89,  50)
middle-left: (-88.89,   0)    middle-center: (omit)      middle-right: (88.89,   0)
bottom-left: (-88.89, -50)    bottom-center: (0, -50)    bottom-right: (88.89, -50)
```

### Required FCPXML 1.14 structure

```
<fcpxml version="1.14">
  <resources>
    <format id="r1" frameDuration="100/3000s" width="W" height="H" colorSpace="1-1-1 (Rec. 709)"/>
    <asset id="r2" ...>
      <media-rep kind="original-media" src="file:///..."/>
    </asset>
    <effect id="r3" name="Adjustment Clip" uid="FFAdjustmentEffect"/>
  </resources>
  <library>
    <event name="...">
      <project name="...">
        <sequence format="r1" ...>
          <spine>
            <asset-clip ref="r2" ...>
              <video ref="r3" lane="1" ... role="adjustments">
                <adjust-transform .../>
              </video>
            </asset-clip>
          </spine>
        </sequence>
      </project>
    </event>
  </library>
</fcpxml>
```

### Connected clip offset

Connected clips (lane 1) use the **parent clip's source timebase** for offset, not the timeline. A connected clip CAN overhang past its parent — FCP extends it across adjacent clips.

### FCPXML generation pitfalls

These were learned through trial and error. Do not re-learn them.

**Generate from scratch, don't inject into OTIO output.** The OTIO FCPXML adapter produces `<clip><video ref>` wrappers instead of `<asset-clip ref>`. Adding `<video>` adjustment clips to these `<clip>` elements crashes FCP (conflicting `<video>` children). Always generate FCPXML from the edit list using `<asset-clip>` elements directly.

**Version 1.14 requires `<media-rep>`.** FCPXML 1.8 allowed `src` directly on `<asset>`. Version 1.14 requires `<media-rep kind="original-media" src="file:///..."/>` as a child of `<asset>`. Using the 1.8 pattern with version 1.14 produces a DTD validation error.

**Format element must match FCP's database.** Use `frameDuration="100/3000s"` (not `1/30s`). Include `width`, `height`, and `colorSpace="1-1-1 (Rec. 709)"` on the format element. Omitting `colorSpace` or using non-canonical `frameDuration` causes "unexpected value" errors on the `<sequence>` format reference.

**`library > event > project` hierarchy is required.** A bare `<project>` under `<fcpxml>` may work for OTIO round-trips but is fragile. The full hierarchy matches what FCP exports.

**`start="3600s"` for generators.** FCP uses this as the conventional start time for adjustment clips and generators. Copy this value exactly.

**`role="adjustments"` on adjustment clip `<video>` elements.** FCP normalizes this to `"adjustments.adjustments-1"` on re-export, but `"adjustments"` works for import.

**FCP inspector shows pixels, FCPXML uses FCP units.** The `position` and `anchor` values in FCPXML are in FCP's unit system (frame height = 100 units). The inspector displays the equivalent pixel values (FCP units × height/100). For a 1440p project, 50 FCP units = 720 pixels in the inspector.
