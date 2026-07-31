#!/bin/zsh
# Production-style menu-bar bundle. Re-run after source updates.
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pip install -r requirements.txt pyinstaller
rm -rf build dist
python3 -m PyInstaller --noconfirm --clean --windowed \
  --name HapticScroll \
  --osx-bundle-identifier com.aayushdangal.hapticscroll \
  --add-data "sounds:sounds" \
  --add-data "app/web:web" \
  --collect-all pygame --collect-all rumps --collect-all pynput \
  --collect-submodules pynput --collect-submodules app \
  --hidden-import settings_server --hidden-import app.onboarding --hidden-import app.runtime_log \
  --hidden-import pynput.keyboard._darwin --hidden-import pynput.mouse._darwin \
  --hidden-import pynput._util.darwin \
  main.py
PLIST="dist/HapticScroll.app/Contents/Info.plist"
/usr/libexec/PlistBuddy -c 'Delete :LSUIElement' "$PLIST" 2>/dev/null || true
/usr/libexec/PlistBuddy -c 'Add :LSUIElement bool true' "$PLIST"
codesign --force --deep --sign - "dist/HapticScroll.app"
echo "Built: $(pwd)/dist/HapticScroll.app"
echo "Diagnostics log: ~/Library/Logs/HapticScroll/HapticScroll.log"
