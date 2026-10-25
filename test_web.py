import http.client, json, os, threading, unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch
import web

class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),web.Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.port=cls.server.server_port
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def req(self,method,path,body=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.port,timeout=5)
        h={'Host':'127.0.0.1:'+str(self.port),**(headers or {})}
        if body is not None:body=json.dumps(body);h.setdefault('Content-Type','application/json')
        c.request(method,path,body=body,headers=h);r=c.getresponse();data=r.read();code=r.status;c.close();return code,data
    def post_headers(self):return {'Origin':'http://127.0.0.1:'+str(self.port),'X-CARLI-Token':web.TOKEN}
    def test_ui(self):
        code,body=self.req('GET','/');self.assertEqual(code,200);self.assertIn(b'CARLi',body)
    def test_status(self):
        code,body=self.req('GET','/api/status');self.assertEqual(code,200);self.assertIn(b'events',body)
    def test_session(self):
        code,body=self.req('GET','/api/session');self.assertEqual(json.loads(body)['token'],web.TOKEN)
    def test_no_csrf(self):
        code,_=self.req('POST','/api/decide',{}, {'Origin':'http://127.0.0.1:'+str(self.port)});self.assertEqual(code,403)
    def test_bad_origin(self):
        code,_=self.req('POST','/api/decide',{}, {'Origin':'https://evil.example','X-CARLI-Token':web.TOKEN});self.assertEqual(code,403)
    def test_wrong_host(self):
        code,_=self.req('GET','/api/status',headers={'Host':'evil.example'});self.assertEqual(code,403)
    def test_invalid_decision(self):
        code,body=self.req('POST','/api/decide',{'proposal_id':'x','digest':'x','decision':'APPROVE'},self.post_headers());self.assertEqual(code,422);self.assertIn(b'NO_PENDING_PROPOSAL',body)
    def test_no_infer_arguments(self):
        code,_=self.req('POST','/api/infer',{'fake':True},self.post_headers());self.assertEqual(code,422)
    def test_live_infer_not_mocked(self):
        with patch.object(web.carli,'infer',side_effect=RuntimeError('LIVE_INFERENCE_BLOCKED')):
            code,body=self.req('POST','/api/infer',{},self.post_headers())
        self.assertEqual(code,422);self.assertIn(b'LIVE_INFERENCE_BLOCKED',body)
    def test_no_json(self):
        code,_=self.req('POST','/api/infer',{}, {**self.post_headers(),'Content-Type':'text/plain'});self.assertEqual(code,415)

if __name__=='__main__':unittest.main()
