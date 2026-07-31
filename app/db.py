"""Small, migration-safe SQLite store for HapticScroll preferences."""
import os
import sqlite3

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "db", "haptic_settings.db"))

DEFAULTS = {
    "master_enabled": 1, "scroll_sound_enabled": 1, "scroll_sound_volume": 62,
    "scroll_haptic_enabled": 1, "scroll_haptic_intensity": 55, "scroll_density": 55,
    "type_sound_enabled": 1, "type_sound_volume": 48,
    "type_haptic_enabled": 1, "type_haptic_intensity": 45, "type_density": 55,
    "sound_pack": "Crisp", "scroll_sound_pack": "Crisp", "type_sound_pack": "Crisp", "dark_mode": 1,
}
VALID_KEYS = set(DEFAULTS)

def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH, timeout=3)

def init_db():
    with _connect() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY CHECK(id=1))")
        columns = {row[1] for row in conn.execute("PRAGMA table_info(settings)")}
        for key, value in DEFAULTS.items():
            if key not in columns:
                sql_type = "TEXT" if isinstance(value, str) else "INTEGER"
                default = repr(value) if isinstance(value, str) else str(value)
                conn.execute(f"ALTER TABLE settings ADD COLUMN {key} {sql_type} DEFAULT {default}")
        conn.execute("CREATE TABLE IF NOT EXISTS profiles (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, settings_json TEXT)")
        conn.execute("INSERT OR IGNORE INTO settings (id) VALUES (1)")
        for key, value in DEFAULTS.items():
            conn.execute(f"UPDATE settings SET {key}=COALESCE({key}, ?) WHERE id=1", (value,))
        # Map the original prototype's unused pack name to the new voice catalog.
        conn.execute("UPDATE settings SET sound_pack='Crisp' WHERE sound_pack='mechanical'")
        # New independent voices inherit the old single voice on upgrade.
        conn.execute("UPDATE settings SET scroll_sound_pack=sound_pack WHERE scroll_sound_pack IS NULL OR scroll_sound_pack=''")
        conn.execute("UPDATE settings SET type_sound_pack=sound_pack WHERE type_sound_pack IS NULL OR type_sound_pack=''")
        # Repair values written by the early prototype, which incorrectly cast
        # the independent pack names to booleans.
        conn.execute("UPDATE settings SET scroll_sound_pack='Crisp' WHERE scroll_sound_pack NOT IN ('Nok','Crisp','Velvet','Deep','Vinyl','Pop','Wood')")
        conn.execute("UPDATE settings SET type_sound_pack='Crisp' WHERE type_sound_pack NOT IN ('Nok','Crisp','Velvet','Deep','Vinyl','Pop','Wood')")

def get_settings():
    init_db()
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
    values = dict(DEFAULTS)
    if row:
        values.update({key: row[key] for key in row.keys() if key in DEFAULTS and row[key] is not None})
    return values

def update_setting(key, value):
    if key not in VALID_KEYS:
        raise ValueError(f"Unknown setting: {key}")
    if key not in ("sound_pack", "scroll_sound_pack", "type_sound_pack"):
        value = max(0, min(100, int(float(value)))) if "density" in key or "volume" in key or "intensity" in key else int(bool(value))
    init_db()
    with _connect() as conn:
        conn.execute(f"UPDATE settings SET {key}=? WHERE id=1", (value,))

def update_settings(values):
    for key, value in values.items():
        update_setting(key, value)
