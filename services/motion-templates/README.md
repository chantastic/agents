# Motion Templates for Video Zoom

Title-based zoom effects using DesignStudio (MotionVFX) templates in FCP.
Templates are **not bundled** — requires a MotionVFX license and install.

## Required templates

Install these from MotionVFX DesignStudio (via mInstaller or manual download):
- **Constant Zoom GG18** — continuous slow zoom (maps to `push`)
- **Zoom In 0ZZM** — animated zoom with in/out control (maps to `smooth` / `punch`)

After install, FCP finds them automatically in:
```
~/Library/Containers/com.apple.FinalCut/Data/Movies/Motion Templates.localized/Titles.localized/DesignStudio/
```

## FCPXML effect references

### Constant Zoom GG18

```xml
<effect id="r_cz" name="Constant Zoom GG18"
    uid="~/Titles.localized/DesignStudio/Constant Zoom GG18/Constant Zoom GG18.moti"/>
```

**Parameters:**

| Name | Key | Description |
|---|---|---|
| Zoom In Strength | `9999/10003/4/3189716296/203` | Zoom intensity (float, 0.0–1.0) |
| Zoom In End Point | `9999/3189715466/3293474482/2/1/13` | Target position (normalized "x y") |

### Zoom In 0ZZM

```xml
<effect id="r_zi" name="Zoom In 0ZZM"
    uid="~/Titles.localized/DesignStudio/Zoom In 0ZZM/Zoom In 0ZZM.moti"/>
```

**Parameters:**

| Name | Key | Description |
|---|---|---|
| Content Position | `9999/3144439439/3330899423/2/1/13` | Zoom target (normalized "x y") |
| Content Scale | `9999/3144439439/3330899423/2/1/15` | Zoom scale factor (float) |
| Animation In | `9999/3144439361/2/101` | Enable zoom-in animation (0/1) |
| Animation Out | `9999/3144439361/2/102` | Enable zoom-out animation (0/1) |

**Style mapping:**
- `punch`: Animation In = 0, Animation Out = 0
- `smooth`: defaults (both animated)
- `smooth` (in only): Animation Out = 0

## Coordinate system

Content Position / Zoom In End Point use **normalized coordinates** (0–1):
- `(0.5, 0.5)` = center
- `(0, 0)` = top-left
- `(1, 1)` = bottom-right

### Mapping from 3×3 anchor grid

| Anchor | Normalized position |
|---|---|
| top-left | `0.15 0.15` |
| top-center | `0.5 0.15` |
| top-right | `0.85 0.15` |
| middle-left | `0.15 0.5` |
| middle-center | `0.5 0.5` |
| middle-right | `0.85 0.5` |
| bottom-left | `0.15 0.85` |
| bottom-center | `0.5 0.85` |
| bottom-right | `0.85 0.85` |

Values inset from edges (0.15/0.85) to avoid cropping past frame at high zoom scales.

## Fallback

If templates aren't installed, `zooms.py` falls back to keyframed adjustment clips.
These work without any dependencies but aren't easily resizable in FCP's timeline.
