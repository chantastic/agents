#!/usr/bin/env python3
"""Set up an After Effects project folder: copies lib.jsx + build.jsx, and starts scenes.jsx / sfx.jsxinc
if they don't exist yet.   usage: init_project.py PROJECT"""
import os, shutil, sys
P = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); os.makedirs(os.path.join(P, "render"), exist_ok=True)
for f in ("lib.jsx", "build.jsx"): shutil.copy(os.path.join(HERE, f), os.path.join(P, f))
if not os.path.exists(os.path.join(P, "scenes.jsx")):
    open(os.path.join(P, "scenes.jsx"), "w").write("// Scene functions for this video (see references/graphics.md and the worked example).\n\nvar SCENES = [];\n")
if not os.path.exists(os.path.join(P, "sfx.jsxinc")):
    open(os.path.join(P, "sfx.jsxinc"), "w").write("var SFX_HITS = {};\nvar SFX_CUES = [];\n")
print("project ready:", P)
