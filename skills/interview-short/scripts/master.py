#!/usr/bin/env python3
"""Master the render to -14 LUFS / -1.5 dBTP and encode the shareable MP4.
usage: python3 -I master.py RENDER OUT.mp4
A mix with SFX usually peaks above 0 dBFS, so a straight two-pass loudnorm can't stay linear: catch the peaks
with an oversampled limiter at about -4.4 dBFS (limit=0.6) first, then two-pass loudnorm. At limit=0.66 (-3.6 dBFS)
a mix needing more than ~2 dB of gain pushes loudnorm into dynamic mode and the AAC peaks land near -0.9 dBFS;
0.6 kept it linear (PR-throughput short: -14.0 LUFS / -1.5 dBFS). Check the "loudnorm: linear" line. Verify with:
ffmpeg -i OUT.mp4 -af ebur128=peak=true -f null -   (expect I ≈ -14.0, Peak ≤ -1.0)"""
import json, subprocess, sys
IN, OUT = sys.argv[1], sys.argv[2]
LIM = "aresample=192000,alimiter=limit=0.6:attack=1:release=60:level=disabled,aresample=48000"
def measure(af):
    r = subprocess.run(["ffmpeg", "-nostdin", "-i", IN, "-af", af + ",loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    return json.loads(r[r.rindex("{"):r.rindex("}") + 1])
m = measure(LIM)
print("after limiter:", {k: m[k] for k in ("input_i", "input_tp", "input_lra")})
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true:print_format=json")
r = subprocess.run(["ffmpeg", "-nostdin", "-y", "-i", IN, "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p",
    "-af", LIM + "," + ln + ",aresample=48000", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], capture_output=True, text=True)
if r.returncode: print(r.stderr[-1500:]); sys.exit(1)
o = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
print("loudnorm:", o["normalization_type"], "out I", o["output_i"], "TP", o["output_tp"], "->", OUT)
