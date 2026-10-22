#!/usr/bin/env python3
"""Trim each sound to its hit, fade, make it stereo 48 kHz and peak-normalise to -1 dBFS (so cue levels mean
the same thing for every sound). usage: uv run --with numpy python -I sfxcut.py PROJECT
Reads PROJECT/sfx/cuts.json: {"stamp": ["stamp.wav", start, end, hit_offset_in_cut, fade_out], ...}
(times in seconds; pick start/end/hit from sfxenv.py). Writes PROJECT/sfx/cut/NAME.wav and cut/hits.json."""
import json, os, subprocess, sys, numpy as np
P = sys.argv[1]; D = os.path.join(P, "sfx"); os.makedirs(os.path.join(D, "cut"), exist_ok=True)
hits = {}
for name, (src, a, b, hit, fo) in json.load(open(os.path.join(D, "cuts.json"))).items():
    d = b - a; dst = os.path.join(D, "cut", name + ".wav"); tmp = dst + ".tmp.wav"
    ch = int(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "stream=channels", "-of", "csv=p=0", os.path.join(D, src)]).split()[0])
    af = f"atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000," + ("" if ch == 2 else "pan=stereo|c0=c0|c1=c0,") + \
         f"afade=t=in:d=0.004,afade=t=out:st={max(d - fo, 0):.3f}:d={fo}"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", os.path.join(D, src), "-af", af, "-c:a", "pcm_s24le", tmp], check=True)
    x = np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-i", tmp, "-f", "f32le", "-"]), dtype=np.float32)
    g = -1 - 20 * np.log10(np.abs(x).max() + 1e-9)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", tmp, "-af", f"volume={g:.2f}dB", "-c:a", "pcm_s24le", dst], check=True)
    os.remove(tmp); hits[name] = round(hit, 3)
    print(f"{name:12s} {d:5.2f}s  hit@{hit:.2f}  normalised {g:+5.1f} dB")
json.dump(hits, open(os.path.join(D, "cut", "hits.json"), "w"))
