#!/bin/bash
# Transcribe candidate cut points from the source audio, padded with silence so whisper hears the edges.
# usage: probe_cut.sh WORK START-END [START-END ...]     e.g. probe_cut.sh work 269.45-271.08 269.60-271.08
set -uo pipefail
W="$1"; shift; MODEL="${WHISPER_MODEL:-$HOME/.bot-device/models/ggml-large-v3-turbo-q5_0.bin}"
T="$(mktemp -d)"
for r in "$@"; do a="${r%-*}"; b="${r#*-}"
  ffmpeg -nostdin -v error -y -ss "$a" -to "$b" -i "$W/audio.wav" -af "adelay=700,apad=pad_dur=0.7" "$T/p.wav"
  printf "%s: " "$r"; whisper-cli -m "$MODEL" -f "$T/p.wav" -l en -nt -np -t 8 2>/dev/null | tr -d '\n'; echo
done
rm -rf "$T"
