"""Native Force Touch feedback at one tuned cadence matching audio."""
import threading,time
from . import db
try:from AppKit import NSHapticFeedbackManager,NSHapticFeedbackPatternGeneric,NSHapticFeedbackPatternAlignment,NSHapticFeedbackPerformanceTimeNow
except ImportError:NSHapticFeedbackManager=None
class HapticEngine:
 def __init__(self):self.last={'scroll':0.,'type':0.};self.scroll_gap=.140;self.lock=threading.Lock()
 def set_scroll_gap(self,gap):
  with self.lock:self.scroll_gap=max(.095,min(.190,float(gap)))
 def pulse(self,kind,settings=None):
  s=settings or db.get_settings();intensity=int(s.get(f'{kind}_haptic_intensity',50))
  if not NSHapticFeedbackManager or intensity<=0:return
  now=time.monotonic();gap=self.scroll_gap if kind=='scroll' else .004
  with self.lock:
   if now-self.last[kind]<gap:return
   self.last[kind]=now
  try:NSHapticFeedbackManager.defaultPerformer().performFeedbackPattern_performanceTime_(NSHapticFeedbackPatternAlignment if intensity>=65 else NSHapticFeedbackPatternGeneric,NSHapticFeedbackPerformanceTimeNow)
  except Exception:pass
engine=HapticEngine()
def available():return NSHapticFeedbackManager is not None
