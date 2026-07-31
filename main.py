#!/usr/bin/env python3
"""HapticScroll macOS menu-bar app."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from app import db
# Explicit import keeps this module in the PyInstaller bundle.
import settings_server
from app.runtime_log import write as log

def main():
    db.init_db()
    log("HapticScroll launch")
    try:
        from app.menu import HapticMenuBar
        HapticMenuBar().run()
    except Exception as exc:
        log(f"FATAL START ERROR: {exc!r}")
        print(f"HapticScroll could not start: {exc}")
        print("Run `python3 diagnose.py` and grant Accessibility + Input Monitoring to your terminal/Python.")
        raise
if __name__ == "__main__": main()
