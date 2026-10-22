#!/usr/bin/env python3
"""Write PROJECT/sfx.jsxinc from sfx/cut/hits.json + sfx/cues.json.
cues.json: [["stamp", 8.96, -10], ...] = [sound, time the hit lands (graphics timeline, same as scenes.jsx), level dB].
usage: make_sfx_data.py PROJECT"""
import json, os, sys
P = sys.argv[1]
hits = json.load(open(os.path.join(P, "sfx", "cut", "hits.json"))); cues = json.load(open(os.path.join(P, "sfx", "cues.json")))
bad = [c for c in cues if c[0] not in hits]; assert not bad, f"cues for sounds with no cut: {bad}"
open(os.path.join(P, "sfx.jsxinc"), "w").write("var SFX_HITS = %s;\nvar SFX_CUES = %s;\n" % (json.dumps(hits), json.dumps(cues)))
print(len(cues), "cues,", len(hits), "sounds")
