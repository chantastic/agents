#!/usr/bin/env python3
"""Write PROJECT/data.jsxinc (captions, clip starts, plate, frame rate) from WORK/timeline.json.
usage: make_ae_data.py WORK PROJECT NAME [--remap | --old-t FILE.json]
Scene and SFX times are written on the "graphics timeline" OLD_T, which remap() maps onto the plate.
First run: OLD_T = the clip starts, so graphics times are plate times. After re-cutting (new timeline), pass
--remap to keep the previous clip starts as OLD_T, so every hard-coded graphics/SFX time follows its clip.
--old-t FILE uses clip starts from a JSON list (the worked example ships its own as old_t.json)."""
import glob, json, os, re, sys
W, P, NAME = sys.argv[1:4]; remap = "--remap" in sys.argv
t = json.load(open(os.path.join(W, "timeline.json")))
clips = [[c["t"], c["d"], c["shot"]] for c in t["clips"]]
inc = os.path.join(P, "data.jsxinc")
old = [c[0] for c in clips]
if "--old-t" in sys.argv:
    old = json.load(open(sys.argv[sys.argv.index("--old-t") + 1]))
    assert len(old) == len(clips), "old_t has a different clip count"
elif remap and os.path.exists(inc):
    prev = re.search(r"var OLD_T = (\[.*?\]);", open(inc).read())
    if prev: old = json.loads(prev.group(1))
    assert len(old) == len(clips), "clip count changed; remap only works for re-timed clips, so retime scenes by hand"
plates = sorted(glob.glob(os.path.join(P, "plate-*.mp4")), key=lambda p: int(re.search(r"plate-(\d+)", p).group(1)))
assert plates, "no plate-N.mp4 in project; run cut.py first"
num, den = t.get("fps", [30000, 1001])
open(inc, "w").write(
    f"var NAME = {json.dumps(NAME)};\nvar PLATE = {json.dumps(os.path.basename(plates[-1]))};\n"
    f"var FPS_NUM = {num}, FPS_DEN = {den};\n"
    f"var CAPTIONS = {json.dumps(t['events'])};\nvar CLIPS = {json.dumps(clips)};\nvar TOTAL = {t['total']:.4f};\n"
    f"// clip starts on the graphics timeline (scene and SFX times are written against these)\nvar OLD_T = {json.dumps(old)};\n")
print(f"{inc}: {len(clips)} clips, {len(t['events'])} captions, plate {os.path.basename(plates[-1])}, {t['total']:.2f}s")
