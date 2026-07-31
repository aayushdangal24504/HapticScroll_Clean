# HapticScroll

A macOS menu-bar utility that adds local sound and optional Force Touch feedback to global scrolling and typing.

> **Status: experimental pre-release.** Test the packaged app on a clean macOS user account before sharing it broadly.

## Features

- Menu-bar-only experience
- Global keyboard and vertical-scroll event listeners
- Separate Scroll and Keyboard sound voices
- Independent sound volume, toggles, and haptic controls
- Local browser-based Settings page at `127.0.0.1` — no account, tracking, or network service
- Keyboard and scroll test labs
- Optional Force Touch feedback on supported hardware
- First-launch instructions for required macOS privacy permissions

## Requirements

- macOS
- Python 3.9 or newer for source development/building
- A Force Touch trackpad only if you want physical haptic feedback

## Run from source

```zsh
python3 -m pip install -r requirements.txt
python3 main.py
```

The app runs from the menu bar. Open its `◉` icon to reach Settings.

## Permissions

macOS requires users to allow the app in **both** locations:

1. System Settings → Privacy & Security → Accessibility
2. System Settings → Privacy & Security → Input Monitoring

These permissions are required for any app that observes global keyboard and scroll events. Apple does not allow apps to approve them automatically.

## Build a shareable app ZIP

```zsh
zsh build_macos.sh
zsh make_shareable_zip.sh
```

The second command creates `HapticScroll.zip`. Share that file with testers; they should not need Python or Terminal.

Because this project is not currently signed/notarized with an Apple Developer ID, a new user must Control-click the app and choose **Open** on first launch.

## Repository layout

```text
app/                 App logic: hooks, audio, haptics, menu, settings assets
app/web/             Local Settings web UI
sounds/              Bundled generated WAV voices
main.py              Source entry point
settings_server.py   Embedded local Settings server
build_macos.sh       Creates the menu-bar app bundle
make_shareable_zip.sh Creates the end-user app ZIP
```

## Privacy

HapticScroll processes input events locally only to trigger feedback. It does not store typed content, transmit input data, require an account, or call a remote API.

## Development notes

- Build artifacts (`build/`, `dist/`, and generated app ZIPs) are ignored by Git.
- `db/haptic_settings.db` is local runtime state and is intentionally ignored.
- Release binaries should be code-signed and notarized before public distribution.

## License

MIT. See [LICENSE](LICENSE).
