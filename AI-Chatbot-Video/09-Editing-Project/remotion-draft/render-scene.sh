#!/bin/bash
# Render ONE scene again after you change it. The full videos are not touched.
# Usage:  ./render-scene.sh SC-022 KH      (language: KH or EN)
# Output: out/SC-022-KH.mp4  -> copy it over 10-Final-Exports/scenes/Khmer/SC-022-KH.mp4 when you are happy.
set -e
cd "$(dirname "$0")"
ID="$1"; L="${2:-KH}"
[ -z "$ID" ] && { echo "Usage: ./render-scene.sh SC-022 KH"; exit 1; }
LANG_LOWER=$(echo "$L" | tr 'A-Z' 'a-z')
FRAMES=$(node -e "const s=require('./src/data/scenes.json').find(x=>x.id==='$ID'); if(!s){console.error('Unknown scene $ID');process.exit(1)} console.log(Math.round(s.dur*25)-1)")
mkdir -p out
npx remotion render src/index.ts "Video$L" "out/$ID-$L.mp4" --props="{\"lang\":\"$LANG_LOWER\",\"only\":\"$ID\"}" \
  --frames="0-$FRAMES" --codec=h264 --crf=20
echo "Saved out/$ID-$L.mp4"
