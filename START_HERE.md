# Create the one-file HapticScroll download

This is the clean source/build folder. It is not what you share with users.

## On your Mac, build once

```zsh
zsh build_macos.sh
zsh make_shareable_zip.sh
```

This creates `HapticScroll.zip` beside this file.

## What you share
Share only `HapticScroll.zip`. It contains only the app bundle—no source code, Python command, DMG, build folder, or settings database.

## Recipient flow
1. Download and unzip HapticScroll.zip.
2. Double-click HapticScroll.app.
3. Since this build is unsigned, on the first run Control-click the app → Open → Open.
4. The app explains that it needs **Accessibility** and **Input Monitoring**. Enable HapticScroll in both macOS Privacy & Security pages and relaunch it.

Apple requires users to approve those two permissions; no app can grant them automatically.
