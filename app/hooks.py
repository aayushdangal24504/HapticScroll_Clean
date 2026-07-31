"""Exactly one global listener pair, with a held-key repeater for natural trrrr feedback."""
import threading,time
from pynput import keyboard,mouse
from . import db,feedback
from .runtime_log import write as log
class HookManager:
 def __init__(self):
  self.mouse_listener=self.keyboard_listener=None;self.running=False;self.last_error='';self.seen_scroll=False;self.seen_key=False;self.lock=threading.RLock();self.lab_suppressed=set();self.held={}
 def set_lab_mode(self,kind,enabled):
  with self.lock:
   if enabled:self.lab_suppressed.add(kind)
   else:self.lab_suppressed.discard(kind)
 def _scroll(self,x,y,dx,dy):
  try:
   with self.lock:
    if 'scroll' in self.lab_suppressed:return
   if dy:
    if not self.seen_scroll:log('First global scroll event received');self.seen_scroll=True
    feedback.scroll(units=abs(dy))
  except Exception as e:self.last_error=str(e)
 def _valid(self,key):return getattr(key,'char',None) is not None or key in(keyboard.Key.space,keyboard.Key.enter,keyboard.Key.tab,keyboard.Key.backspace)
 def _key_id(self,key):return str(key)
 def _repeat(self,key_id,stop):
  # Wait for the normal key-repeat feeling, then create a clean continuous trrrr.
  if stop.wait(.22):return
  while not stop.wait(.028):
   with self.lock:
    if 'type' in self.lab_suppressed or key_id not in self.held:return
   feedback.typing()
 def _press(self,key):
  try:
   if not self._valid(key):return
   with self.lock:
    if 'type' in self.lab_suppressed:return
    ident=self._key_id(key)
    if ident in self.held:return
    stop=threading.Event();self.held[ident]=stop
   if not self.seen_key:log('First global keyboard event received');self.seen_key=True
   feedback.typing();threading.Thread(target=self._repeat,args=(ident,stop),daemon=True,name='hapticscroll-keyrepeat').start()
  except Exception as e:self.last_error=str(e)
 def _release(self,key):
  with self.lock:
   stop=self.held.pop(self._key_id(key),None)
   if stop:stop.set()
 def start(self):
  with self.lock:
   if self.running and self.is_healthy():return
   self.stop()
   try:
    self.mouse_listener=mouse.Listener(on_scroll=self._scroll);self.keyboard_listener=keyboard.Listener(on_press=self._press,on_release=self._release)
    self.mouse_listener.start();self.keyboard_listener.start();self.running=True;self.last_error='';log('Global mouse + keyboard listeners started')
   except Exception as e:
    self.running=False;self.last_error=str(e);log(f'LISTENER START ERROR: {e!r}')
 def stop(self):
  with self.lock:
   for event in self.held.values():event.set()
   self.held.clear()
   for listener in(self.mouse_listener,self.keyboard_listener):
    try:
     if listener:listener.stop()
    except Exception:pass
   self.mouse_listener=self.keyboard_listener=None;self.running=False;self.lab_suppressed.clear();log('Global listeners stopped')
 def is_healthy(self):return bool(self.running and self.mouse_listener and self.keyboard_listener and self.mouse_listener.is_alive() and self.keyboard_listener.is_alive())
 def ensure_running(self):
  if db.get_settings()['master_enabled'] and not self.is_healthy():self.start()
manager=HookManager()
