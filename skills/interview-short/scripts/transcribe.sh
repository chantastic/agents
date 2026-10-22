#!/bin/bash
# Transcribe an interview with word-level timings.  usage: transcribe.sh VIDEO WORKDIR
# Writes WORKDIR/audio.wav, transcript.srt (to read), dtw.json and words_dtw.json ([start, end, word], seconds).
# DTW alignment (--dtw, needs -nfa: no flash attention) is what makes the word times usable; whisper's plain
# token offsets run 0.3-0.5 s early and clip words at every cut.
set -euo pipefail
SRC="$1"; W="$2"; mkdir -p "$W"
MODEL="${WHISPER_MODEL:-$HOME/.bot-device/models/ggml-large-v3-turbo-q5_0.bin}"
HERE="$(cd "$(dirname "$0")" && pwd)"
ffmpeg -nostdin -v error -y -i "$SRC" -ar 16000 -ac 1 "$W/audio.wav"
whisper-cli -m "$MODEL" -f "$W/audio.wav" -l en -ojf -osrt -of "$W/dtw" --dtw large.v3.turbo -nfa -t 8 > "$W/whisper.log" 2>&1
mv "$W/dtw.srt" "$W/transcript.srt"
python3 -I "$HERE/words_dtw.py" "$W/dtw.json" "$W/words_dtw.json"
python3 -I - "$W/transcript.srt" <<'PY'
import sys
for b in open(sys.argv[1]).read().strip().split("\n\n"):
    l = b.split("\n"); print(l[1][:8], " ".join(l[2:]))
PY
