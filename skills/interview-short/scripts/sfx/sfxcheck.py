#!/usr/bin/env python3
"""Measure the SFX in a render without listening: align the plate to the render (AAC adds ~21 ms), subtract it to
get an effects-only stem, then report per-cue sync (hit vs graphic) and level vs nearby speech peaks.
usage: uv run --with numpy python -I sfxcheck.py PROJECT
Targets: hits within about a frame; effects a median ~10 dB under speech peaks; nothing much above 0 dB re speech."""
import glob, json, os, re, subprocess, sys, numpy as np
P = sys.argv[1]
def load(p): return np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", "48000", "-f", "f32le", "-"]), dtype=np.float32).astype(np.float64)
data = open(os.path.join(P, "data.jsxinc")).read()
plate = json.loads(re.search(r"var PLATE = (\".*?\");", data).group(1))
C = json.loads(re.search(r"var CLIPS = (\[.*?\]);", data).group(1)); O = json.loads(re.search(r"var OLD_T = (\[.*?\]);", data).group(1))
num, den = map(int, re.search(r"FPS_NUM = (\d+), FPS_DEN = (\d+)", data).groups()); f = num / den
cues = json.loads(re.search(r"var SFX_CUES = (\[.*?\]);", open(os.path.join(P, "sfx.jsxinc")).read(), re.S).group(1))
render = sorted(glob.glob(os.path.join(P, "render", "*-graphics.*")), key=os.path.getmtime)[-1]
mix, dia = load(render), load(os.path.join(P, plate))
def remap(t):
    i = 0
    while i + 1 < len(O) and O[i + 1] <= t + 1e-6: i += 1
    return round((C[i][0] + t - O[i]) * f) / f
T = sorted(remap(c[1]) for c in cues)
gaps = [(T[i + 1] - T[i], T[i]) for i in range(len(T) - 1)] + [(T[0], 0.0)]
g, s0 = max(gaps); a, b = int((s0 + 0.8) * 48000), int((s0 + min(g - 0.5, 4.5)) * 48000)   # longest cue-free stretch
best = (0, -1)
for lag in range(-2880, 2881, 4):
    c = np.dot(mix[a:b], dia[a + lag:b + lag]); best = max(best, (lag, c), key=lambda x: x[1])
for lag in range(best[0] - 4, best[0] + 5):
    c = np.dot(mix[a:b], dia[a + lag:b + lag]); best = max(best, (lag, c), key=lambda x: x[1])
d = np.roll(dia, -best[0]); n = min(len(mix), len(d))
gain = np.dot(mix[a:b], d[a:b]) / np.dot(d[a:b], d[a:b]); fx = mix[:n] - gain * d[:n]
res = 20 * np.log10(np.sqrt(np.mean(fx[a:b] ** 2)) / np.sqrt(np.mean(mix[a:b] ** 2)))
print(f"plate offset {best[0] / 48:.2f} ms, speech residual {res:.1f} dB (should be below -40)")
hop = 240
def env(x): m = len(x) // hop; return 20 * np.log10(np.sqrt((x[:m * hop].reshape(m, hop) ** 2).mean(1)) + 1e-12)
ef, em = env(fx), env(mix[:n]); off, lv = [], []
for name, t, gdb in cues:
    Tt = remap(t); i0, i1 = max(0, int((Tt - 0.06) / 0.005)), int((Tt + 0.06) / 0.005)
    seg = ef[i0:i1]; k = int(np.argmax(seg[4:] - seg[:-4])) + 4 if len(seg) > 5 else 0
    off.append(((i0 + k) * 0.005 - Tt, name, t))
    j0, j1 = int(Tt / 0.005), int((Tt + 0.15) / 0.005)
    lv.append((float(ef[j0:j1].max() - np.percentile(em[max(0, j0 - 200):j0 + 200], 90)), name, t))
o = np.array([x[0] for x in off]); l = np.array([x[0] for x in lv])
print(f"sync over {len(off)} cues: median {np.median(o) * 1000:+.0f} ms (≈ the plate offset is fine), 90% within ±{np.percentile(np.abs(o), 90) * 1000:.0f} ms")
print("  worst:", [(f"{x[0] * 1000:+.0f}ms", x[1], x[2]) for x in sorted(off, key=lambda x: -abs(x[0]))[:4]])
print(f"level vs nearby speech peaks: median {np.median(l):+.1f} dB")
print("  loudest:", [(round(x[0], 1), x[1], x[2]) for x in sorted(lv, key=lambda x: -x[0])[:5]])
print("  quietest:", [(round(x[0], 1), x[1], x[2]) for x in sorted(lv, key=lambda x: x[0])[:5]])
