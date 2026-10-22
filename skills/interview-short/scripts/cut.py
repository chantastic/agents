#!/usr/bin/env python3
"""Cut an interview into a frame-exact vertical (1080x1920) plate from an edit list.

    uv run --with pillow --with numpy python -I cut.py --src VIDEO --work WORK --edl edl.py \
        --project PROJECT [--preview preview.mp4]

WORK must hold audio.wav + words_dtw.json (from transcribe.sh). The edit list (edl.py) defines:
  CLIPS: (first word, its time, last word, its time, "Q"|"A", ("close"|"wide", crop centre x)[, lo, hi])
  FIX:   caption spelling fixes; a key with a space merges consecutive words ("had coded": "vibe-coded")
  FORCE: {(first word, its time): (start or None, end or None)} cut points verified by probe_cut.sh
Writes WORK/clips/NN.mov, WORK/timeline.json, PROJECT/plate-N.mp4 (new N every run, so After Effects
never reuses a cached copy) and, with --preview, a quick captioned MP4 for reviewing the edit.
"""
import argparse, glob, json, os, re, runpy, subprocess, wave
from fractions import Fraction
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True); ap.add_argument("--work", required=True)
ap.add_argument("--edl", required=True); ap.add_argument("--project", required=True)
ap.add_argument("--preview")
args = ap.parse_args()
E = runpy.run_path(args.edl)
CLIPS, FIX, FORCE = E["CLIPS"], E.get("FIX", {}), E.get("FORCE", {})
W = args.work
CL = os.path.join(W, "clips"); os.makedirs(CL, exist_ok=True)
os.makedirs(args.project, exist_ok=True)
words = json.load(open(os.path.join(W, "words_dtw.json")))

probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
    "stream=width,height,r_frame_rate", "-of", "json", args.src]))["streams"][0]
SW, SH = probe["width"], probe["height"]
RATE = Fraction(probe["r_frame_rate"]); FPS = float(RATE)

# --- snap cut points to the quietest 10 ms near each boundary ---
with wave.open(os.path.join(W, "audio.wav")) as wf:
    sr = wf.getframerate()
    pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32)
hop = sr // 100
env = np.sqrt(np.convolve((pcm[: len(pcm) // hop * hop].reshape(-1, hop) ** 2).mean(1), np.ones(3) / 3, "same"))

def quietest(lo, hi):
    a, b = int(lo * 100), int(hi * 100)
    if b <= a: return lo
    return (a + int(np.argmin(env[a:b]))) / 100

def find(txt, t):
    return min((i for i, w in enumerate(words) if w[2] == txt), key=lambda i: abs(words[i][0] - t))

def cut(first, ft, last, lt, lo=None, hi=None):
    i, j = find(first, ft), find(last, lt)
    a = quietest(max(words[i][0] - 0.25, words[i - 1][0] + 0.08), words[i][0] + 0.02)
    b = quietest(words[j][0] + 0.12, min(words[j + 1][0] + 0.03, words[j][0] + 0.55))
    if lo is not None: a = max(a, lo)
    if hi is not None: b = min(b, hi)
    return a, b, words[i:j + 1]

def render(i, a, b, shot):
    kind, cx = shot
    h = SH if kind == "close" else round(SH * 0.8333 / 2) * 2   # wide shots get a 1.2x punch-in
    w = round(h * 9 / 16 / 2) * 2
    x = int(min(max(cx - w / 2, 0), SW - w))
    out = os.path.join(CL, f"{i:02d}.mov")
    # whole frames only, audio trimmed/padded to exactly the video length, so cuts never drift
    n = max(1, round((b - a) * FPS))
    d = n / FPS
    fc = (f"[0:v]crop={w}:{h}:{x}:0,scale=1080:1920:flags=lanczos,setsar=1,fps={RATE},"
          f"trim=end_frame={n},setpts=PTS-STARTPTS[v];"
          f"[0:a]aresample=48000,asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={max(d-0.025,0):.4f}:d=0.025,"
          f"apad=whole_dur={d:.6f},atrim=end={d:.6f}[a]")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{d + 0.5:.3f}", "-i", args.src,
        "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "pcm_s16le", out], check=True)
    return out, d

def chunks(ws):
    out, cur = [], []
    for w in ws:
        cur.append(w)
        txt = " ".join(x[2] for x in cur)
        if len(cur) >= 3 or len(txt) >= 15 or txt[-1] in ".,?!":
            out.append(cur); cur = []
    if cur: out.append(cur)
    return out

def clean(t):
    t = FIX.get(t.strip(".,?!"), t.strip(".,?!")) + ("?" if t.endswith("?") else "")
    return t.upper()

MERGE = [k.split() for k in FIX if " " in k]
def merge(ws):
    for parts in MERGE:
        k = 0
        while k + len(parts) <= len(ws):
            if [w[2].strip(".,?!") for w in ws[k:k + len(parts)]] == parts:
                ws[k][2] = " ".join(parts); del ws[k + 1:k + len(parts)]
            k += 1
    return ws

files, events, t0 = [], [], 0.0
timeline = {"clips": [], "words": [], "fps": [RATE.numerator, RATE.denominator]}
for i, (first, ft, last, lt, spk, shot, *lim) in enumerate(CLIPS):
    a2, b2, ws = cut(first, ft, last, lt, *lim)
    fa, fb = FORCE.get((first, ft), (None, None))
    a2, b2 = fa if fa is not None else a2, fb if fb is not None else b2
    f, d = render(i, a2, b2, shot); files.append(f)
    ws = merge([list(w) for w in ws])
    for ch in chunks(ws):
        events.append([round(t0 + max(ch[0][0] - a2 - 0.05, 0), 4), " ".join(clean(x[2]) for x in ch), spk])
    timeline["clips"].append({"i": i, "t": round(t0, 4), "d": round(d, 4), "spk": spk, "shot": shot[0], "src": [a2, b2]})
    for w in ws:
        timeline["words"].append([round(t0 + max(w[0] - a2 - 0.03, 0), 3), clean(w[2]), spk, i])
    print(f"{i:02d} {a2:8.2f}-{b2:8.2f} {d:5.2f}s  {' '.join(w[2] for w in ws)}")
    t0 += d
timeline["events"] = sorted(events); timeline["total"] = t0
json.dump(timeline, open(os.path.join(W, "timeline.json"), "w"))

# --- caption-free plate for After Effects, under a new name every run ---
used = [int(m.group(1)) for p in glob.glob(os.path.join(args.project, "plate-*.mp4"))
        if (m := re.search(r"plate-(\d+)\.mp4$", p))]
plate = os.path.join(args.project, f"plate-{max(used, default=0) + 1}.mp4")
inputs = sum((["-i", f] for f in files), [])
n = len(files)
fc = "".join(f"[{k}:v][{k}:a]" for k in range(n)) + f"concat=n={n}:v=1:a=1[v][a];[a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[ao]"
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[ao]",
    "-c:v", "libx264", "-crf", "12", "-preset", "slow", "-g", "15", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", plate], check=True)
print(f"total {t0:.2f}s, plate -> {plate}")

# --- optional quick preview with burned-in captions (this ffmpeg has no drawtext/subtitles, so PIL cards) ---
if args.preview:
    from PIL import Image, ImageDraw, ImageFont
    CAP = os.path.join(W, "caps"); os.makedirs(CAP, exist_ok=True)
    FONT = ImageFont.truetype("/System/Library/Fonts/Avenir Next.ttc", 92, index=8)
    COL = {"Q": (255, 214, 0, 255), "A": (255, 255, 255, 255)}
    def card(text, spk, path):
        im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
        lines, cur = [], ""
        for wd in text.split():
            t = (cur + " " + wd).strip()
            if dr.textlength(t, font=FONT) > 960 and cur: lines.append(cur); cur = wd
            else: cur = t
        lines.append(cur)
        y = 1330 - (len(lines) - 1) * 55
        for ln in lines:
            dr.text((540, y), ln, font=FONT, fill=COL[spk], anchor="mm", stroke_width=9, stroke_fill=(0, 0, 0, 255)); y += 110
        im.save(path)
    ev = timeline["events"]
    blank = os.path.join(CAP, "blank.png"); Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)).save(blank)
    lst = ["ffconcat version 1.0"] + ([f"file '{blank}'", f"duration {ev[0][0]:.3f}"] if ev[0][0] > 0 else [])
    for k, (s, txt, spk) in enumerate(ev):
        p = os.path.join(CAP, f"c{k:03d}.png"); card(txt, spk, p)
        e = ev[k + 1][0] if k + 1 < len(ev) else t0
        lst += [f"file '{p}'", f"duration {max(e - s, 0.04):.3f}"]
    lst += [f"file '{blank}'"]
    open(os.path.join(W, "caps.txt"), "w").write("\n".join(lst) + "\n")
    fc = f"[1:v]fps={RATE},format=rgba[c];[0:v][c]overlay=0:0:shortest=0:eof_action=pass,format=yuv420p[vo]"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", plate, "-f", "concat", "-safe", "0", "-i", os.path.join(W, "caps.txt"),
        "-filter_complex", fc, "-map", "[vo]", "-map", "0:a", "-t", f"{t0:.3f}",
        "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", args.preview], check=True)
    print("preview ->", args.preview)
