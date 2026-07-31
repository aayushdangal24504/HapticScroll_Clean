"""Shared feedback pipeline with a velocity-aware, Snick-inspired scroll cadence."""
import threading,time
from . import audio_engine,db,haptics
_scroll_units=0;_scroll_lock=threading.Lock();_last_scroll=0.
def _run(kind,preview=False,settings=None):
 s=settings or db.get_settings();sound_on=bool(s[f'{kind}_sound_enabled']);haptic_on=bool(s[f'{kind}_haptic_enabled'])
 if not preview and not s['master_enabled']:return False
 played=False
 if sound_on:played=audio_engine.engine.play(kind,s[f'{kind}_sound_volume'],s[f'{kind}_sound_pack'],force=preview)
 if haptic_on and (played or not sound_on):haptics.engine.pulse(kind,settings=s)
 return played or haptic_on
def scroll(preview=False,settings=None,units=1):
 """One detent per two units; faster gestures receive a slightly quicker, never noisy cadence."""
 global _scroll_units,_last_scroll
 if not preview:
  now=time.monotonic()
  with _scroll_lock:
   delta=now-_last_scroll if _last_scroll else .2;_last_scroll=now
   # Slow precision movement = spacious; a fast flick tightens naturally, like Snick's velocity-aware behavior.
   gap=.100 if delta<.035 else (.125 if delta<.075 else .165)
   audio_engine.engine.set_scroll_gap(gap);haptics.engine.set_scroll_gap(gap)
   _scroll_units+=max(1,abs(int(units)))
   if _scroll_units<2:return False
   _scroll_units%=2
 return _run('scroll',preview,settings)
def typing(preview=False,settings=None):return _run('type',preview,settings)
def stop(kind=None):audio_engine.engine.stop_all()
