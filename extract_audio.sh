#!/bin/bash
# Usage: ./extract_audio.sh input.mp4 output.wav
IN="$1"
OUT="$2"
ffmpeg -y -i "$IN" -vn -ac 1 -ar 16000 -hide_banner -loglevel error "$OUT"
echo "wrote $OUT"
