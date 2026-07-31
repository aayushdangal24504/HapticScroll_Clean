"""Low-latency shared sound engine. pygame mixer is used when installed; afplay is fallback."""
import os,subprocess,threading,time
from . import db
SOUND_DIR=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','sounds'))
PACKS={'Nok':{'scroll':'scroll_nok.wav','type':'type_nok.wav'},'Crisp':{'scroll':'scroll_crisp.wav','type':'click_1.wav'},'Velvet':{'scroll':'scroll_soft.wav','type':'type_velvet.wav'},'Deep':{'scroll':'scroll_deep.wav','type':'ambient_low.wav'},'Vinyl':{'scroll':'scroll_vinyl.wav','type':'type_vinyl.wav'},'Pop':{'scroll':'scroll_pop.wav','type':'type_pop.wav'},'Wood':{'scroll':'scroll_wood.wav','type':'type_wood.wav'}}
try:
 import pygame
except ImportError:pygame=None
class AudioEngine:
 def __init__(self):
  self.last={'scroll':0.,'type':0.};self.scroll_gap=.140;self.lock=threading.RLock();self.cache={};self.process={'scroll':None,'type':None};self.scroll_channel=None;self.ready=False
  if pygame:
   try:
    pygame.mixer.pre_init(44100,-16,2,256);pygame.mixer.init();pygame.mixer.set_num_channels(48);self.ready=True
   except Exception: self.ready=False
 def _allowed(self,kind):
  # Tuned for precision: scroll responds within 18ms; type never drops normal fast keystrokes.
  gap=self.scroll_gap if kind=='scroll' else .004;now=time.monotonic()
  with self.lock:
   if now-self.last[kind]<gap:return False
   self.last[kind]=now;return True
 def set_scroll_gap(self,gap):
  with self.lock:self.scroll_gap=max(.095,min(.190,float(gap)))
 def _file(self,kind,voice):return os.path.join(SOUND_DIR,PACKS.get(voice,PACKS['Crisp'])[kind])
 def _sound(self,path):
  if path not in self.cache:self.cache[path]=pygame.mixer.Sound(path)
  return self.cache[path]
 def play(self,kind,volume,voice,force=False):
  if not force and not self._allowed(kind):return False
  path=self._file(kind,voice)
  if not os.path.isfile(path):return False
  volume=max(0,min(100,int(volume)))/100
  with self.lock:
   if self.ready:
    try:
     sound=self._sound(path);sound.set_volume(volume)
     # Never cut an in-flight scroll waveform: abruptly terminating it is what creates radio/static artifacts.
     # Scroll files are deliberately very short, so this remains a clean even detent train at high speed.
     channel=sound.play()
     if kind=='scroll':self.scroll_channel=channel
     return channel is not None
    except Exception:self.ready=False
   try:
    # Fallback only for installations where pygame could not initialise.
    if kind=='scroll' and self.process[kind] and self.process[kind].poll() is None:self.process[kind].terminate()
    self.process[kind]=subprocess.Popen(['afplay','-v',f'{volume:.2f}',path],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return True
   except OSError:return False
 def play_scroll(self,preview=False,voice=None,volume=None):
  s=db.get_settings()
  if not preview and(not s['master_enabled'] or not s['scroll_sound_enabled']):return False
  return self.play('scroll',s['scroll_sound_volume'] if volume is None else volume,voice or s['scroll_sound_pack'],preview)
 def play_type(self,preview=False,voice=None,volume=None):
  s=db.get_settings()
  if not preview and(not s['master_enabled'] or not s['type_sound_enabled']):return False
  return self.play('type',s['type_sound_volume'] if volume is None else volume,voice or s['type_sound_pack'],preview)
 def stop_all(self):
  with self.lock:
   if self.ready:
    pygame.mixer.stop();return
   for p in self.process.values():
    try:
     if p and p.poll() is None:p.terminate()
    except OSError:pass
engine=AudioEngine()
