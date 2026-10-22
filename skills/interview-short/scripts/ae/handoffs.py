#!/usr/bin/env python3
"""Filmstrips around every graphics in/out point in the render, to catch flashes and blank first frames.
usage: handoffs.py PROJECT OUT_DIR      (reads the "placed" lines build.jsx logs to build.log)
Each row: 2 frames before the boundary, the boundary frame, 2 after. A good exit is graphic, graphic, then one
camera shot; a good entry shows the scene already populated on its first frame."""
import glob, os, re, subprocess, sys
P, O = sys.argv[1], sys.argv[2]; os.makedirs(O, exist_ok=True)
log = open(os.path.join(P, "build.log"), errors="replace").read().replace("\r", "\n")
num, den = map(int, re.search(r"FPS_NUM = (\d+), FPS_DEN = (\d+)", open(os.path.join(P, "data.jsxinc")).read()).groups())
fps = num / den
render = sorted(glob.glob(os.path.join(P, "render", "*-graphics.*")), key=os.path.getmtime)[-1]
rows = {"in": [], "out": []}
for name, t0, t1, kind in re.findall(r"placed\t([^\t]+)\t([\d.]+)\t([\d.]+)\t(\w+)", log):
    for side, t in (("in", float(t0)), ("out", float(t1))):
        f = round(t * fps); a = max(f - 2, 0)
        img = os.path.join(O, f"{side}_{f:05d}.jpg")
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", render, "-vf",
            f"select='between(n,{a},{f+2})',scale=150:-1,tile=5x1", "-fps_mode", "passthrough", "-frames:v", "1", img], check=True)
        rows[side].append(img)
for side, imgs in rows.items():
    if not imgs: continue
    out = os.path.join(O, f"{side}s.jpg")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *sum((["-i", i] for i in imgs), []),
        "-filter_complex", f"vstack={len(imgs)}" if len(imgs) > 1 else "null", out], check=True)
    print(out, f"({len(imgs)} rows)")
