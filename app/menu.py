"""Stable single-instance rumps menu bar controller."""
import time
try:import rumps
except ImportError:rumps=None
try:
 from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
except ImportError:
 NSApplication=None
from . import db,hooks,feedback,onboarding
import settings_server
class HapticMenuBar:
 def __init__(self):
  if rumps is None:raise ImportError('rumps is required on macOS')
  # Source-mode Python normally appears in the Dock; make it a menu-bar agent too.
  if NSApplication:
   try:NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)
   except Exception:pass
  self.app=rumps.App('HapticScroll',quit_button=None)
  # Build once. refresh() only changes existing MenuItem titles; it never recreates the menu.
  self.header=rumps.MenuItem('HapticScroll',callback=None);self.master=rumps.MenuItem('',callback=self.toggle_master)
  self.scroll=rumps.MenuItem('',callback=lambda _:self.toggle('scroll_sound_enabled'));self.typing=rumps.MenuItem('',callback=lambda _:self.toggle('type_sound_enabled'))
  self.haptic=rumps.MenuItem('',callback=lambda _:self.toggle('scroll_haptic_enabled'))
  self.settings=rumps.MenuItem('Open premium settings…',callback=self.open_settings);self.permissions=rumps.MenuItem('Permissions & setup…',callback=onboarding.open_setup);self.restart_item=rumps.MenuItem('Restart input listeners',callback=self.restart)
  self.app.menu=[self.header,None,self.master,self.scroll,self.typing,self.haptic,None,self.settings,self.permissions,self.restart_item,None,rumps.MenuItem('Quit HapticScroll',callback=self.quit)]
  self.health_timer=rumps.Timer(self.health,5);self.refresh()
 def refresh(self):
  s=db.get_settings();mark=lambda key:'✓' if s[key] else '—'
  self.app.title='◉' if s['master_enabled'] else '○';self.header.title='HapticScroll  '+('ACTIVE' if s['master_enabled'] else 'PAUSED')
  self.master.title=f"{mark('master_enabled')}  Feedback engine";self.scroll.title=f"{mark('scroll_sound_enabled')}  Scroll sound";self.typing.title=f"{mark('type_sound_enabled')}  Keyboard sound";self.haptic.title=f"{mark('scroll_haptic_enabled')}  Scroll haptics"
 def toggle(self,key):
  value=not bool(db.get_settings()[key]);db.update_setting(key,value)
  if not value and key in ('scroll_sound_enabled','type_sound_enabled'):feedback.stop()
  self.refresh()
 def toggle_master(self,_):
  enabled=not bool(db.get_settings()['master_enabled']);db.update_setting('master_enabled',enabled)
  if enabled:hooks.manager.start()
  else:hooks.manager.stop();feedback.stop()
  self.refresh()
 def open_settings(self,_):
  # Same process server: works from source and from the packaged .app.
  settings_server.ensure(open_browser=True)
 def restart(self,_):hooks.manager.stop();time.sleep(.12);hooks.manager.start();self.refresh()
 def health(self,_):hooks.manager.ensure_running();self.refresh()
 def _onboard_once(self,timer):timer.stop();onboarding.first_launch_help()
 def quit(self,_):hooks.manager.stop();feedback.stop();settings_server.stop();rumps.quit_application()
 def run(self):
  if db.get_settings()['master_enabled']:hooks.manager.start()
  self.health_timer.start();self.onboarding_timer=rumps.Timer(self._onboard_once,1);self.onboarding_timer.start();self.app.run()
