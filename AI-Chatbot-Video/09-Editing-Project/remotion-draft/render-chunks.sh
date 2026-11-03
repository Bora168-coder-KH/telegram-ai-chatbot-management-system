#!/bin/bash
# Render both languages in chunks of 2000 frames; retry a failed chunk up to 3 times; then join the chunks.
cd "$(dirname "$0")"
CH=${CHROME_PATH:-}   # optional: path to a Chrome binary
TOTAL=10150; STEP=1000
mkdir -p out/chunks
for L in KH EN; do
  : > out/chunks/list-$L.txt
  for ((a=0; a<TOTAL; a+=STEP)); do
    b=$((a+STEP-1)); [ $b -ge $TOTAL ] && b=$((TOTAL-1))
    f=out/chunks/$L-$(printf %05d $a).mp4
    for try in 1 2 3 4 5 6; do
      [ -f "$f" ] && break
      echo "$L $a-$b try $try" >> out/status.txt
      npx remotion render src/index.ts Video$L "$f.tmp.mp4" --frames=$a-$b --codec=h264 --crf=20 --concurrency=3 --timeout=30000 \
        ${CH:+--browser-executable=$CH} --log=info > out/render-$L-$a-try$try.log 2>&1 && mv "$f.tmp.mp4" "$f"
    done
    [ -f "$f" ] || { echo "failed $L $a" >> out/status.txt; exit 1; }
    echo "file '$(basename $f)'" >> out/chunks/list-$L.txt
  done
  ffmpeg -y -loglevel error -f concat -safe 0 -i out/chunks/list-$L.txt -c copy out/AI-Chatbot-Video-$L.mp4 && echo "done $L" >> out/status.txt
done
