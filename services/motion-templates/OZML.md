# OZML Reverse Engineering Notes

Apple Motion project files (`.moti`, `.motn`) use the **OZML** format — plain XML with a scene graph, factory system, and published parameter binding.

## File structure

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE ozxmlscene>
<ozml version="5.13">
    <displayversion>5.6.3</displayversion>
    <factory id="N" uuid="...">...</factory>  <!-- component registry -->
    <scene>
        <scenenode>...</scenenode>             <!-- scene graph tree -->
    </scene>
</ozml>
```

## Factory system

Factories are registered component types. Each has a UUID and description. Standard Apple factories include:

| Description | Purpose |
|---|---|
| Channel | Animation channel / parameter link |
| Generator | Color/shape generator |
| Widget | Published parameter group (what FCP shows in inspector) |
| Image | Image/texture layer |
| Shape | Vector shape |
| Ramp | Value interpolation (ease in/out curves) |
| Clamp | Value range limiter |
| Link | Parameter linking/expression |
| Project | Root project node |

Factory UUIDs are stable across Motion versions. They're Apple-internal identifiers, not template-specific.

## Scene graph

The `<scene>` contains a tree of `<scenenode>` elements. Each node has:
- `name` — display name
- `id` — numeric ID (referenced by targets and parameter bindings)
- `factoryID` — which factory created this node
- `<parameter>` children — the node's configurable values

## Published parameters (Widget system)

This is how FCP title controls work:

1. A `<scenenode>` with `factoryID` pointing to the Widget factory acts as the parameter group
2. `<target>` elements bind published parameter names to scene graph objects:

```xml
<target object="3189716296" channel="3189716296" name="Zoom In On/Off"/>
<target object="3189716296" channel="./203" name="Zoom In Strength"/>
<target object="3293474482" channel="./2/1/13" name="Zoom In End Point"/>
```

- `object` — the scene node ID containing the actual parameter
- `channel` — path to the specific parameter within that node
- `name` — the display name shown in FCP's inspector

3. FCP constructs FCPXML `<param>` keys from: `9999/{object}/{channel}`:

| OZML target | FCPXML param key |
|---|---|
| `object="3189716296" channel="./203"` | `9999/10003/4/3189716296/203` |
| `object="3293474482" channel="./2/1/13"` | `9999/3189715466/3293474482/2/1/13` |

The `9999/10003/4/` prefix and intermediate segments come from the Widget hierarchy.
The exact mapping depends on the nesting depth of widget → target → object.

## Key observations from DesignStudio zoom templates

### Constant Zoom GG18

Published parameters:
```
Zoom In On/Off     → object 3189716296, channel self (toggle)
Zoom In Strength   → object 3189716296, channel ./203
Zoom In End Point  → object 3293474482, channel ./2/1/13
Movement Smoothness → object 3189716296, channel ./204
```

The zoom is implemented as a scale + position transform driven by a Ramp generator.
The Ramp factory handles easing — its parameters control timing curves.

### Zoom In 0ZZM

Published parameters:
```
Animation In       → object 3144439361, channel ./2/101
Animation Out      → object 3144439361, channel ./2/102
Animation In Type  → object 3292644363, channel ./2/100
Content Position   → object 3330899423, channel ./2/1/13
Content Scale      → object 3330899423, channel ./2/1/15
Zoom Sharpen       → object 3146672312, channel self (toggle)
Sharpen Intensity  → object 3146672312, channel ./1
Sharpen Amount     → object 3146672312, channel ./2
```

More complex — includes a sharpen filter (applied during zoom to counteract softness),
animation toggle per direction, and a content position/scale system.

## Building custom templates

To create redistributable zoom templates without MotionVFX dependency:

1. Start from a minimal Motion title project (File → New → FCP Title)
2. Add a single group with scale/position parameters
3. Add a Ramp behavior for animation timing
4. Publish the parameters you want FCP to expose
5. Export as `.moti` to `~/Movies/Motion Templates.localized/Titles.localized/`

The resulting OZML will use only Apple-standard factory UUIDs and can be freely distributed.

Alternatively, construct the OZML XML directly — all factories are Apple-provided,
the format is stable, and Motion will validate on first open. This avoids needing
Motion.app for template creation entirely (though testing still requires it).

## Template file layout

```
MyTemplate/
├── MyTemplate.moti     ← OZML XML file
├── large.png           ← 640×360 thumbnail (shown in FCP browser)
├── small.png           ← 200×113 thumbnail
└── Media/              ← any referenced media (images, etc.)
```

The `.moti` extension is just a renamed `.motn`. FCP uses it to distinguish
title templates from full Motion projects.
