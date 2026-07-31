"""Global input listeners with safe held-key feedback and automatic cleanup."""
import threading
import time
from pynput import keyboard, mouse
from . import db, feedback
from .runtime_log import write as log

# macOS normally sends key-repeat press events while a key remains held. If a
# release event is ever lost, this grace period stops a stale repeat safely.
STALE_HELD_KEY_SECONDS = 0.80
INITIAL_REPEAT_DELAY = 0.22
REPEAT_INTERVAL = 0.028

class HookManager:
    def __init__(self):
        self.mouse_listener = self.keyboard_listener = None
        self.running = False
        self.last_error = ""
        self.seen_scroll = self.seen_key = False
        self.lock = threading.RLock()
        self.lab_suppressed = set()
        # key id -> {stop: Event, last_signal: monotonic timestamp}
        self.held = {}

    def set_lab_mode(self, kind, enabled):
        with self.lock:
            (self.lab_suppressed.add if enabled else self.lab_suppressed.discard)(kind)

    def _scroll(self, x, y, dx, dy):
        try:
            with self.lock:
                if "scroll" in self.lab_suppressed:
                    return
            if dy:
                if not self.seen_scroll:
                    log("First global scroll event received")
                    self.seen_scroll = True
                feedback.scroll(units=abs(dy))
        except Exception as exc:
            self.last_error = str(exc)
            log(f"SCROLL CALLBACK ERROR: {exc!r}")

    @staticmethod
    def _valid(key):
        return getattr(key, "char", None) is not None or key in (
            keyboard.Key.space, keyboard.Key.enter, keyboard.Key.tab, keyboard.Key.backspace
        )

    @staticmethod
    def _key_id(key):
        return str(key)

    def _repeat(self, key_id, stop):
        """Create held-key feedback, but never let a missed release repeat forever."""
        if stop.wait(INITIAL_REPEAT_DELAY):
            return
        while not stop.wait(REPEAT_INTERVAL):
            with self.lock:
                state = self.held.get(key_id)
                if state is None or "type" in self.lab_suppressed:
                    return
                # A genuine held key generates native repeated press events.
                # If neither those nor a release arrives, treat it as stale.
                if time.monotonic() - state["last_signal"] > STALE_HELD_KEY_SECONDS:
                    self.held.pop(key_id, None)
                    stop.set()
                    log(f"Stopped stale held-key repeat: {key_id}")
                    return
            feedback.typing()

    def _press(self, key):
        try:
            if not self._valid(key):
                return
            with self.lock:
                if "type" in self.lab_suppressed:
                    return
                key_id = self._key_id(key)
                existing = self.held.get(key_id)
                if existing:
                    # Native macOS auto-repeat confirms that this key remains held.
                    existing["last_signal"] = time.monotonic()
                    return
                stop = threading.Event()
                self.held[key_id] = {"stop": stop, "last_signal": time.monotonic()}
            if not self.seen_key:
                log("First global keyboard event received")
                self.seen_key = True
            feedback.typing()
            threading.Thread(
                target=self._repeat, args=(key_id, stop), daemon=True,
                name="hapticscroll-keyrepeat"
            ).start()
        except Exception as exc:
            self.last_error = str(exc)
            log(f"KEYBOARD CALLBACK ERROR: {exc!r}")

    def _release(self, key):
        with self.lock:
            state = self.held.pop(self._key_id(key), None)
            if state:
                state["stop"].set()

    def start(self):
        with self.lock:
            if self.running and self.is_healthy():
                return
            self.stop()
            try:
                self.mouse_listener = mouse.Listener(on_scroll=self._scroll)
                self.keyboard_listener = keyboard.Listener(on_press=self._press, on_release=self._release)
                self.mouse_listener.start()
                self.keyboard_listener.start()
                self.running = True
                self.last_error = ""
                log("Global mouse + keyboard listeners started")
            except Exception as exc:
                self.running = False
                self.last_error = str(exc)
                log(f"LISTENER START ERROR: {exc!r}")

    def stop(self):
        with self.lock:
            for state in self.held.values():
                state["stop"].set()
            self.held.clear()
            for listener in (self.mouse_listener, self.keyboard_listener):
                try:
                    if listener:
                        listener.stop()
                except Exception:
                    pass
            self.mouse_listener = self.keyboard_listener = None
            self.running = False
            self.lab_suppressed.clear()
            log("Global listeners stopped")

    def is_healthy(self):
        return bool(
            self.running and self.mouse_listener and self.keyboard_listener
            and self.mouse_listener.is_alive() and self.keyboard_listener.is_alive()
        )

    def ensure_running(self):
        if db.get_settings()["master_enabled"] and not self.is_healthy():
            self.start()

manager = HookManager()
