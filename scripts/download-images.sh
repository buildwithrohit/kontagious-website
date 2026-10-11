#!/usr/bin/env bash
# Downloads every photo the site uses from the old Wix site into ./images
# Run once from the project root:  bash scripts/download-images.sh
set -u
cd "$(dirname "$0")/.."
mkdir -p images
ok=0; fail=0
while read -r name url; do
  [ -z "$name" ] && continue
  if [ -s "images/$name" ]; then ok=$((ok+1)); continue; fi
  if curl -fsSL --retry 2 -o "images/$name" "$url"; then ok=$((ok+1)); else echo "FAILED: $name"; rm -f "images/$name"; fail=$((fail+1)); fi
done < scripts/images-manifest.txt
echo "Done. $ok downloaded or already present, $fail failed."
du -sh images
