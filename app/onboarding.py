"""First-launch permission assistance. macOS still requires the user to approve TCC permissions."""
import subprocess

def accessibility_allowed():
    try:
        from Quartz import AXIsProcessTrusted
        return bool(AXIsProcessTrusted())
    except Exception:
        return False

def open_setup(_=None):
    import rumps
    rumps.alert(
        "One-time setup required",
        "HapticScroll needs Accessibility and Input Monitoring to feel global scrolls and keys. "
        "Enable HapticScroll in BOTH pages that open, then quit and reopen the app."
    )
    subprocess.Popen(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"])

def first_launch_help():
    if not accessibility_allowed():
        open_setup()
