#!/bin/bash
# Transcribe every rendered clip on its own (padded). Whole-file transcription of a jump-cut edit is
# unreliable (it skips and hallucinates), so this is the real check that no clip starts or ends mid-word.
# Doubled lines are a whisper repeat artifact on short clips, not doubled audio.   usage: check_clips.sh WORK
set -uo pipefail
W="$1"; MODEL="${WHISPER_MODEL:-$HOME/.bot-device/models/ggml-large-v3-turbo-q5_0.bin}"; T="$(mktemp -d)"
for f in "$W"/clips/*.mov; do
  ffmpeg -nostdin -v error -y -i "$f" -af "adelay=700,apad=pad_dur=0.7" -ar 16000 -ac 1 "$T/c.wav"
  printf "%s " "$(basename "$f" .mov)"; whisper-cli -m "$MODEL" -f "$T/c.wav" -l en -nt -np -t 8 2>/dev/null | tr -d '\n'; echo
done
rm -rf "$T"
