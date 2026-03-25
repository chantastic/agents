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

**Keyframed zoom** (animated scale over time):
```xml
<adjust-transform>
    <param name="scale">
        <keyframeAnimation>
            <keyframe time="3600s" value="1 1"/>
            <keyframe time="3610s" value="1.87 1.87"/>
        </keyframeAnimation>
    </param>
</adjust-transform>
```

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
