#!/usr/bin/env python3
"""Print DTW word times for time windows, to pick exact first/last words for the edit list.
usage: words.py WORK 53-72 268-290 ...   (source seconds)"""
import json, os, sys
w = json.load(open(os.path.join(sys.argv[1], "words_dtw.json")))
for r in sys.argv[2:]:
    a, b = map(float, r.split("-"))
    print(f"--- {a}-{b}"); print(" ".join(f"{x[2]}@{x[0]:.2f}" for x in w if a <= x[0] < b))
