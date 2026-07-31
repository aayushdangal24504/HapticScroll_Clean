#!/bin/zsh
# Creates the one-file download you share with other Mac users.
set -euo pipefail
cd "$(dirname "$0")"
[[ -d "dist/HapticScroll.app" ]] || { echo "Build the app first: zsh build_macos.sh"; exit 1; }
rm -rf release HapticScroll.zip
mkdir -p release
ditto "dist/HapticScroll.app" "release/HapticScroll.app"
(
  cd release
  /usr/bin/zip -qry ../HapticScroll.zip HapticScroll.app
)
echo "Share this one file: $(pwd)/HapticScroll.zip"
