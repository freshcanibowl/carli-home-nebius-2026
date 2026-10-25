"""Real-loopback HTTP integration tests for Stage 2 synthetic isolation."""
import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from pet_http62 import create_server

class PetHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.server=create_server(str(Path(cls.tmp.name)/'pet.sqlite3'),0)
        cls.t=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.t.start()
        cls.a=cls.server.RequestHandlerClass.vault.bootstrap_synthetic_owner('Owner A')['session_token']
        cls.b=cls.server.RequestHandlerClass.vault.bootstrap_synthetic_owner('Owner B')['session_token']
        cls.momo=cls.api('POST','/api/pets',cls.a,{'name':'Luna','species':'cat'})[1]['pet_id']
        cls.milo=cls.api('POST','/api/pets',cls.a,{'name':'Luna','species':'cat'})[1]['pet_id']
        cls.other=cls.api('POST','/api/pets',cls.b,{'name':'Luna','species':'cat'})[1]['pet_id']
        cls.ev=cls.api('POST',f'/api/pets/{cls.momo}/memories',cls.a,{'observation':'Synthetic water bowl refilled; drinking unconfirmed.'})[1]['id']
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.t.join();cls.tmp.cleanup()
    @classmethod
    def api(cls,method,path,token=None,data=None,extra=None):
        c=http.client.HTTPConnection('127.0.0.1',cls.server.server_port,timeout=5)
        headers={'Host':f'127.0.0.1:{cls.server.server_port}'}
        if token is not None:headers['Authorization']='Bearer '+token
        if data is not None:headers['Content-Type']='application/json'
        if extra:headers.update(extra)
        c.request(method,path,body=json.dumps(data) if data is not None else None,headers=headers)
        r=c.getresponse();status=r.status;body=json.loads(r.read());c.close();return status,body
    def test_anonymous_denied(self):self.assertEqual(self.api('GET','/api/pets')[0],403)
    def test_known_owner_list(self):self.assertEqual(len(self.api('GET','/api/pets',self.a)[1]),2)
    def test_pet_ids_unique_same_name(self):self.assertNotEqual(self.momo,self.milo)
    def test_other_owner_cannot_list(self):self.assertEqual(len(self.api('GET','/api/pets',self.b)[1]),1)
    def test_other_owner_cannot_read(self):self.assertEqual(self.api('GET',f'/api/pets/{self.momo}/state',self.b)[0],403)
    def test_same_owner_pet_memory_isolated(self):self.assertEqual(self.api('GET',f'/api/pets/{self.milo}/state',self.a)[1]['events'],[])
    def test_other_owner_cannot_write(self):self.assertEqual(self.api('POST',f'/api/pets/{self.momo}/memories',self.b,{'observation':'X'})[0],403)
    def test_cross_pet_evidence_rejected(self):self.assertEqual(self.api('POST',f'/api/pets/{self.milo}/proposals',self.a,{'evidence_ids':[self.ev],'text':'Observe intake.'})[0],403)
    def test_cross_owner_evidence_rejected(self):self.assertEqual(self.api('POST',f'/api/pets/{self.other}/proposals',self.b,{'evidence_ids':[self.ev],'text':'Observe intake.'})[0],403)
    def test_cross_pet_decision_blocked(self):
        p=self.api('POST',f'/api/pets/{self.momo}/proposals',self.a,{'evidence_ids':[self.ev],'text':'Observe intake.'})[1]
        payload={'proposal_id':p['proposal_id'],'digest':p['digest'],'decision':'APPROVE'}
        self.assertEqual(self.api('POST',f'/api/pets/{self.milo}/decisions',self.a,payload)[0],403)
        self.assertEqual(self.api('POST',f'/api/pets/{self.momo}/decisions',self.b,payload)[0],403)
        self.assertEqual(self.api('POST',f'/api/pets/{self.momo}/decisions',self.a,payload)[0],200)
        self.assertEqual(self.api('POST',f'/api/pets/{self.momo}/decisions',self.a,payload)[0],422)
    def test_legacy_routes_never_exposed(self):
        for path in ('/api/status','/api/session','/api/infer','/api/decide'):
            with self.subTest(path=path):self.assertEqual(self.api('GET',path,self.a)[0],404)
    def test_wrong_origin_rejected(self):self.assertEqual(self.api('GET','/api/pets',self.a,extra={'Origin':'https://evil.example'})[0],403)
    def test_browser_post_without_intent_rejected(self):self.assertEqual(self.api('POST','/api/pets',self.a,{'name':'M','species':'cat'},extra={'Origin':f'http://127.0.0.1:{self.server.server_port}'})[0],403)
    def test_invalid_body_rejected(self):self.assertEqual(self.api('POST','/api/pets',self.a,{'owner_id':'forged','name':'M','species':'cat'})[0],422)
    def test_query_in_path_rejected(self):self.assertEqual(self.api('GET','/api/pets?x=1',self.a)[0],404)
    def test_wrong_host_rejected(self):self.assertEqual(self.api('GET','/api/pets',self.a,extra={'Host':'evil.example'})[0],403)

if __name__=='__main__':unittest.main()
