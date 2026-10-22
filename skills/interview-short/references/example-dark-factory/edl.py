# Worked example: edit list for "Nobody Runs a Dark Software Factory" (Andrew Churchill, Weave x Michael Grinich, ELC 2026).
# 16:44 source -> 58.5s, 4 Q&A beats. Word times are DTW times from words_dtw.json.
# Each clip is a run of words: (first word, its time, last word, its time, speaker, shot[, lo, hi]).
# Times are DTW word times; cut points snap to the quietest moment around them.
# Q = Michael asking (yellow captions), A = Andrew answering (white).
# shot: ("close", cx) Andrew close-up; ("wide", cx) wide shot with a 1.2x punch-in.
# lo/hi clamp the cut so it never crosses a camera cut.
C = ("close", 540)
CLIPS = [
  # 1. dark factory
  ("Is", 269.72, "factory?", 270.74, "Q", ("wide", 1480)),
  ("I", 277.44, "that", 278.44, "A", C),
  ("there's", 279.08, "any", 279.42, "A", C),
  ("very", 280.96, "factory.", 285.04, "A", C),
  ("it's", 286.54, "industry.", 287.74, "A", C),
  ("there", 476.78, "tell.", 478.26, "A", C),
  ("Not", 479.78, "way,", 480.24, "Q", ("wide", 1440)),
  # 2. token era
  ("Earlier", 55.26, "era.", 57.44, "Q", ("wide", 1470)),
  ("If", 61.88, "fired.", 63.70, "Q", ("wide", 1480)),
  ("what", 71.06, "now?", 71.20, "Q", ("wide", 1500)),
  ("I'd", 132.18, "spend", 134.16, "A", C, None, 134.36),
  ("token", 134.80, "efficiency.", 135.34, "Q", ("wide", 1420), 134.40, None),
  # 3. CI
  ("I", 483.76, "bottlenecks", 485.60, "Q", ("wide", 1520)),
  ("What", 504.08, "is?", 505.20, "Q", ("wide", 1520)),
  ("dynamic", 544.66, "validation.", 545.12, "A", C),
  ("before", 547.58, "PR,", 550.06, "A", C),
  ("decide", 551.26, "run.", 552.82, "A", C),
  ("you", 555.96, "tests.", 557.90, "A", C, 555.90, None),
  # 4. model routing
  ("how", 634.16, "task", 636.62, "Q", ("wide", 1500)),
  ("without", 638.68, "it?", 639.32, "Q", ("wide", 1480)),
  ("it's", 746.20, "prompt.", 748.60, "A", C),
  ("refactor", 724.94, "Rust.", 725.70, "A", C),
  ("In", 726.70, "weekend,", 729.56, "A", C),
  ("a", 733.18, "handle.", 734.18, "A", C),
  ("If", 735.32, "kernel,", 736.72, "A", C),
  ("you", 737.90, "DeepSeq,", 738.52, "A", C),
  ("as", 756.26, "works,", 757.60, "A", ("wide", 300), None, 757.80),
  ("it", 758.42, "problem.", 761.00, "A", C, 757.86, None),
  ("it's", 991.76, "performance", 992.98, "A", C),
  ("at", 993.84, "speed.", 995.38, "A", C),
  ("That's", 997.40, "awesome.", 997.74, "Q", ("wide", 1480)),
]
FIX = {"DeepSeq": "DeepSeek", "Astro": "Astra", "had coded": "vibe-coded"}
# cut points checked by transcribing padded snippets: (first, time) -> (start, end), None keeps the snap
FORCE = {
  ("Is", 269.72): (269.45, None),
  ("what", 71.06): (None, 72.22),
  ("dynamic", 544.66): (544.35, None),
  ("before", 547.58): (547.25, None),
  ("it", 758.42): (758.10, None),
  ("you", 555.96): (555.90, None),
  ("at", 993.84): (993.55, None),
}
