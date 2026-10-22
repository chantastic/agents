#!/usr/bin/env python3
"""Contact sheet of frames at given times.  usage: sheet.py VIDEO OUT.jpg [--cols 6] [--w 360] t1 t2 ...
Use on the source (pick crops: where each speaker's face is in each shot), on the plate, and on renders."""
import os, subprocess, sys, tempfile
a = sys.argv[1:]; video, out = a[0], a[1]; a = a[2:]
cols, w = 6, 360
while a and a[0].startswith("--"):
    if a[0] == "--cols": cols = int(a[1])
    if a[0] == "--w": w = int(a[1])
    a = a[2:]
d = tempfile.mkdtemp()
for i, t in enumerate(a):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", t, "-i", video, "-frames:v", "1", "-vf", f"scale={w}:-1", f"{d}/{i:03d}.jpg"], check=True)
rows = -(-len(a) // cols)
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-pattern_type", "glob", "-i", f"{d}/*.jpg", "-vf", f"tile={cols}x{rows}", out], check=True)
print(out, "<- in order:", " ".join(a))
