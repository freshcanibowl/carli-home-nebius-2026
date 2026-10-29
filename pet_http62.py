"""Local-only, synthetic-only, separate pet-scoped test HTTP server.

This NEVER serves legacy /api/status, /api/infer, /api/decide routes.
No account creation or token vending over HTTP. Tokens must be provisioned offline.
No provider inference. No public deployment.
"""
import json
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pet_vault62 import Vault, AccessDenied, InvalidOperation

MAX_BODY = 4096

class PetHandler(BaseHTTPRequestHandler):
    vault = None
    def log_message(self, fmt, *args):
        # No URL query strings or sensitive bodies logged.
        return
    def send_json(self, payload, status=200):
        data=json.dumps(payload, ensure_ascii=True).encode('utf-8')
        self.send_response(status)
        for k,v in [('Content-Type','application/json; charset=utf-8'),('Cache-Control','no-store'),('X-Content-Type-Options','nosniff'),('Content-Security-Policy',"default-src 'none'; frame-ancestors 'none'"),('Content-Length',str(len(data)))]:self.send_header(k,v)
        self.end_headers();self.wfile.write(data)
    def _host_ok(self):
        return self.headers.get('Host','') in ('127.0.0.1:'+str(self.server.server_port),'localhost:'+str(self.server.server_port))
    def _origin_ok(self):
        origin=self.headers.get('Origin')
        # CLI clients without an Origin are accepted; browsers must match localhost.
        return not origin or origin in ('http://127.0.0.1:'+str(self.server.server_port),'http://localhost:'+str(self.server.server_port))
    def _auth(self):
        value=self.headers.get('Authorization','')
        if not value.startswith('Bearer ') or value.count(' ')!=1:raise AccessDenied('UNAUTHORIZED')
        return value[7:]
    def _path(self):
        u=urllib.parse.urlsplit(self.path)
        if u.query or u.fragment or '%' in u.path:return None
        pieces=u.path.strip('/').split('/')
        if len(pieces)==2 and pieces==['api','pets']:return ('pets',None,None)
        if len(pieces)==4 and pieces[:2]==['api','pets'] and pieces[3] in ('state','memories','proposals','decisions') and pieces[2]:return ('pet',pieces[2],pieces[3])
        return None
    def _request(self, method):
        if not self._host_ok():return self.send_json({'error':'HOST_REJECTED'},403)
        if not self._origin_ok():return self.send_json({'error':'ORIGIN_REJECTED'},403)
        if method=='POST' and self.headers.get('Origin') and self.headers.get('X-CARLI-Intent')!='synthetic-demo':
            return self.send_json({'error':'INTENT_HEADER_REQUIRED'},403)
        route=self._path()
        if not route:return self.send_json({'error':'NOT_FOUND'},404)
        try:
            token=self._auth()
            if method=='GET':
                if route[0]=='pets':result=self.vault.list_pets(token)
                elif route[2]=='state':result=self.vault.get_pet_state(token,route[1])
                else:return self.send_json({'error':'NOT_FOUND'},404)
            else:
                raw_length=self.headers.get('Content-Length','')
                if not raw_length.isdecimal() or not 0<int(raw_length)<=MAX_BODY:return self.send_json({'error':'BODY_LIMIT'},413)
                if self.headers.get('Content-Type','').split(';')[0].strip()!='application/json':return self.send_json({'error':'JSON_REQUIRED'},415)
                try: obj=json.loads(self.rfile.read(int(raw_length)))
                except (UnicodeError,ValueError):return self.send_json({'error':'INVALID_JSON'},400)
                if not isinstance(obj,dict):return self.send_json({'error':'OBJECT_REQUIRED'},400)
                if route[0]=='pets' and set(obj)=={'name','species'}:
                    result=self.vault.create_pet(token,obj['name'],obj['species'])
                elif route[0]=='pet' and route[2]=='memories' and set(obj)=={'observation'}:
                    result=self.vault.add_memory(token,route[1],obj['observation'])
                elif route[0]=='pet' and route[2]=='proposals' and set(obj)=={'evidence_ids','text'}:
                    result=self.vault.propose(token,route[1],obj['evidence_ids'],obj['text'])
                elif route[0]=='pet' and route[2]=='decisions' and set(obj)=={'proposal_id','digest','decision'}:
                    result=self.vault.decide(token,route[1],obj['proposal_id'],obj['digest'],obj['decision'])
                else:return self.send_json({'error':'INVALID_FIELDS_OR_ROUTE'},422)
            self.send_json(result)
        except AccessDenied:
            # Do not reveal existence of other owners' pet or proposal.
            self.send_json({'error':'ACCESS_DENIED'},403)
        except (InvalidOperation,ValueError,TypeError,KeyError):
            self.send_json({'error':'VALIDATION_FAILED'},422)
        except Exception:
            # Never return database, tokens, stack traces.
            self.send_json({'error':'SERVER_FAILURE'},500)
    def do_GET(self):self._request('GET')
    def do_POST(self):self._request('POST')

def create_server(path, port=8766):
    vault=Vault(path)
    handler=type('BoundPetHandler',(PetHandler,),{'vault':vault})
    return ThreadingHTTPServer(('127.0.0.1',port),handler)

if __name__=='__main__':
    db=os.environ.get('CARLI_PET_VAULT_DB','carli_pet_vault62.sqlite3')
    server=create_server(db)
    print('Synthetic pet HTTP test API at http://127.0.0.1:8766 (NO production authentication, NO inference)',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
