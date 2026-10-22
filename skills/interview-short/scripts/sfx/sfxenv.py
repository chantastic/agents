#!/usr/bin/env python3
"""Loudness envelope + hit onsets for each SFX file, to choose trims without listening.
usage: uv run --with numpy python -I sfxenv.py sfx/*.wav   (one row per file: dB envelope, then onset times)"""
import sys, subprocess, numpy as np, os
def load(p):
    raw = subprocess.check_output(["ffmpeg","-v","error","-i",p,"-ac","1","-ar","48000","-f","f32le","-"])
    return np.frombuffer(raw, dtype=np.float32)
for p in sys.argv[1:]:
    x = load(p); sr = 48000; hop = 480
    n = len(x)//hop
    e = 20*np.log10(np.sqrt((x[:n*hop].reshape(n,hop)**2).mean(1))+1e-9)
    pk = 20*np.log10(np.abs(x).max()+1e-9)
    dur = len(x)/sr
    # compress long envelopes to <=120 chars
    step = max(1, int(np.ceil(n/120)))
    m = e[:n//step*step].reshape(-1,step).max(1) if step>1 else e
    s = ''.join(' .:-=+*#%@'[min(9,max(0,int((v+60)/6)))] for v in m)
    # onsets: rises of >12 dB over 30 ms above -40 dB
    on = [i*0.01 for i in range(3,n) if e[i]>-40 and e[i]-e[i-3]>12 and (i<6 or e[i-3]<e[i]-12)]
    ons=[]
    for t in on:
        if not ons or t-ons[-1]>0.08: ons.append(t)
    print(f"{os.path.basename(p):15s} {dur:6.2f}s pk {pk:6.1f}dB  {step*10}ms/char |{s}|")
    print(f"{'':15s} onsets: {' '.join(f'{t:.2f}' for t in ons[:24])}")
