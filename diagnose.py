#!/usr/bin/env python3
"""Run this when feedback does not work; it prints the exact next step."""
import os, platform, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from app import db
print("HapticScroll diagnostics")
print("=" * 28)
print("macOS:", platform.mac_ver()[0] or "NOT macOS")
print("Python:", sys.version.split()[0])
print("afplay:", "OK" if shutil.which("afplay") else "MISSING (macOS required)")
try:
    import pynput; print("pynput: OK")
except Exception as e: print("pynput: ERROR -", e)
try:
    import rumps; print("rumps: OK")
except Exception as e: print("rumps: ERROR -", e)
try:
    from app.haptics import available; print("native trackpad haptics:", "available" if available() else "unavailable (sound remains available)")
except Exception as e: print("native trackpad haptics: ERROR -", e)
db.init_db(); print("settings DB:", db.DB_PATH)
print("\nIf hooks are not detected: System Settings > Privacy & Security >")
print("Accessibility AND Input Monitoring > enable Terminal/iTerm or the Python app, then quit and relaunch.")
try:
    import pygame
    print("pygame low-latency audio: OK")
except Exception as e:
    print("pygame low-latency audio: MISSING - run: python3 -m pip install -r requirements.txt")
