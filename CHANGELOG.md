# Changelog

## Unreleased
- Fixed stuck held-key feedback that could continue playing after a key release was missed.
- Added a held-key watchdog: it safely stops a repeat if macOS stops sending both repeat and release events.
- Added callback error logging for scroll and keyboard input.
- Preserved normal held-key feedback using macOS native auto-repeat signals.
