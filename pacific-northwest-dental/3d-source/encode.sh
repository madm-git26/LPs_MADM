#!/usr/bin/env bash
# Encode a rendered frame folder into the seamless-loop hero video (MP4 + WebM).
# Usage: ./encode.sh frames_dir out_basename   (frames rendered by seq.js at 30 fps, 14 s)
# The last 0.8 s cross-fades into the first 0.8 s, so the 13.2 s output loops without a jump.
set -euo pipefail
IN=$1; OUT=$2
FC="[0]split[a][b];[a]trim=start=0.8,setpts=PTS-STARTPTS[main];[b]trim=end=0.8,setpts=PTS-STARTPTS[head];[main][head]xfade=transition=fade:duration=0.8:offset=12.4,format=yuv420p"
ffmpeg -v error -y -framerate 30 -i "$IN/f%04d.jpg" -filter_complex "$FC" -c:v libx264 -preset slow -crf 22 -profile:v high -movflags +faststart -an "$OUT.mp4"
ffmpeg -v error -y -framerate 30 -i "$IN/f%04d.jpg" -filter_complex "$FC" -c:v libvpx-vp9 -b:v 0 -crf 34 -row-mt 1 -an "$OUT.webm"
ffmpeg -v error -y -i "$OUT.mp4" -frames:v 1 -q:v 4 "$OUT-poster.jpg"
