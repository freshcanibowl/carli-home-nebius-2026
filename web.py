"""Local-only CARLi demonstration HTTP server. Never expose to a public network."""
import json, os, secrets, threading, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import carli

ROOT = Path(__file__).resolve().parent
TOKEN = secrets.token_urlsafe(32)
MAX_BODY = 8192

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Do not log authorization tokens or request bodies.
        print('CARLi Web:', self.address_string(), fmt % args)

    def send_json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=True).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'none'; frame-ancestors 'none'")
        self.send_header('Content-Length',str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def allowed_host(self):
        host = self.headers.get('Host','')
        return host in ('127.0.0.1:'+str(self.server.server_port), 'localhost:'+str(self.server.server_port))

    def valid_origin(self):
        origin = self.headers.get('Origin','')
        return origin in ('http://127.0.0.1:'+str(self.server.server_port), 'http://localhost:'+str(self.server.server_port))

    def do_GET(self):
        if not self.allowed_host(): return self.send_json({'error':'HOST_REJECTED'},403)
        if self.path == '/':
            content=(ROOT/'index.html').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Frame-Options','DENY')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
            self.send_header('Content-Length',str(len(content)))
            self.end_headers(); self.wfile.write(content)
        elif self.path == '/app.js':
            content=(ROOT/'app.js').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type','application/javascript; charset=utf-8')
            self.send_header('Cache-Control','no-store')
            self.send_header('Content-Length',str(len(content)))
            self.end_headers(); self.wfile.write(content)
        elif self.path == '/api/status': self.send_json(carli.status())
        elif self.path == '/api/session': self.send_json({'token':TOKEN,'synthetic':True})
        else: self.send_json({'error':'NOT_FOUND'},404)

    def do_POST(self):
        if not self.allowed_host() or not self.valid_origin():
            return self.send_json({'error':'ORIGIN_REJECTED'},403)
        if not secrets.compare_digest(self.headers.get('X-CARLI-Token',''),TOKEN):
            return self.send_json({'error':'CSRF_REJECTED'},403)
        try: length=int(self.headers.get('Content-Length','-1'))
        except ValueError: return self.send_json({'error':'BAD_LENGTH'},400)
        if length<0 or length>MAX_BODY:return self.send_json({'error':'BAD_LENGTH'},413)
        if self.headers.get('Content-Type','').split(';')[0].strip()!='application/json':
            return self.send_json({'error':'JSON_REQUIRED'},415)
        try:
            payload=json.loads(self.rfile.read(length))
            if not isinstance(payload,dict):raise ValueError('OBJECT_REQUIRED')
            if self.path=='/api/infer':
                if payload:raise ValueError('NO_INFERENCE_ARGS_ALLOWED')
                result=carli.infer()
            elif self.path=='/api/decide':
                if set(payload)!={'proposal_id','digest','decision'}:raise ValueError('INVALID_DECISION_FIELDS')
                if not all(isinstance(payload[k],str) for k in payload):raise ValueError('INVALID_DECISION_TYPES')
                result=carli.decide(payload['proposal_id'],payload['digest'],payload['decision'])
            else:return self.send_json({'error':'NOT_FOUND'},404)
            self.send_json(result)
        except (ValueError,RuntimeError,KeyError) as e:
            self.send_json({'error':'GATE_FAIL','detail':str(e)},422)
        except Exception as e:
            # No secrets, stack traces or raw provider responses to browser.
            print('CARLi request failed:',type(e).__name__)
            self.send_json({'error':'INFERENCE_OR_SERVER_FAILURE','detail':type(e).__name__},502)

def serve(port=8765):
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    print('CARLi local demo: http://127.0.0.1:'+str(server.server_port),flush=True)
    print('Synthetic-only; no real reminder scheduling. Ctrl+C to stop.',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765)
    serve(parser.parse_args().port)
