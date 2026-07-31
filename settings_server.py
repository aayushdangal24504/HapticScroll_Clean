"""Embedded local settings server. Runs inside the app process, including PyInstaller builds."""
import json, os, sys, threading, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from app import db, feedback, hooks
from app.runtime_log import write as log
PORT=8765
if getattr(sys, 'frozen', False):
    ROOT=os.path.join(sys._MEIPASS, 'web')
else:
    ROOT=os.path.join(os.path.dirname(__file__), 'app', 'web')
_server=None;_thread=None;_lock=threading.Lock()
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=ROOT,**kw)
 def send_json(self,data,status=200):
  raw=json.dumps(data).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def do_GET(self):
  if self.path=='/api/settings':return self.send_json(db.get_settings())
  if self.path=='/api/status':return self.send_json({'listeners':hooks.manager.is_healthy(),'error':hooks.manager.last_error})
  return super().do_GET()
 def do_POST(self):
  try:payload=json.loads(self.rfile.read(int(self.headers.get('Content-Length',0))) or b'{}')
  except json.JSONDecodeError:return self.send_json({'error':'Invalid request'},400)
  if self.path=='/api/settings':
   allowed={k:v for k,v in payload.items() if k in db.VALID_KEYS};db.update_settings(allowed)
   if any(k in allowed and not allowed[k] for k in ('master_enabled','scroll_sound_enabled','type_sound_enabled')):feedback.stop()
   return self.send_json(db.get_settings())
  if self.path=='/api/preview':
   from app import audio_engine
   kind=payload.get('kind','scroll');voice=payload.get('voice');config=payload.get('config') or db.get_settings()
   audio_engine.engine.play(kind,config.get(f'{kind}_sound_volume',60),voice,force=True);return self.send_json({'ok':True})
  if self.path=='/api/lab':
   kind=payload.get('kind');active=bool(payload.get('active'))
   if kind not in ('scroll','type'):return self.send_json({'error':'Unknown lab'},400)
   hooks.manager.set_lab_mode(kind,active);return self.send_json({'ok':True})
  if self.path=='/api/event':
   kind=payload.get('kind');config=payload.get('config') or db.get_settings()
   if kind=='scroll':feedback.scroll(settings=config)
   elif kind=='type':feedback.typing(settings=config)
   else:return self.send_json({'error':'Unknown event'},400)
   return self.send_json({'ok':True})
  return self.send_json({'error':'Not found'},404)
 def log_message(self,*_):pass
def ensure(open_browser=True):
 global _server,_thread
 with _lock:
  if _server is None:
   try:
    log(f"Settings root: {ROOT}; index exists={os.path.isfile(os.path.join(ROOT, 'index.html'))}")
    _server=ThreadingHTTPServer(('127.0.0.1',PORT),Handler)
    _thread=threading.Thread(target=_server.serve_forever,daemon=True,name='hapticscroll-settings-server');_thread.start()
   except OSError as exc:
    log(f'Settings server could not bind: {exc!r}')
    _server=False
 if open_browser:webbrowser.open(f'http://127.0.0.1:{PORT}')
def stop():
 global _server
 with _lock:
  if _server and _server is not False:
   _server.shutdown();_server.server_close()
  _server=None
