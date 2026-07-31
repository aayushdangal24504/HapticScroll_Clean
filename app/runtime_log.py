"""Small persistent log for packaged menu-bar builds (which have no console)."""
from pathlib import Path
from datetime import datetime
LOG=Path.home()/"Library"/"Logs"/"HapticScroll"/"HapticScroll.log"
def write(message):
 try:
  LOG.parent.mkdir(parents=True,exist_ok=True)
  with LOG.open('a',encoding='utf-8') as f:f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S}  {message}\n")
 except OSError:pass
