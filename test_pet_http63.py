import http.client,json,tempfile,threading,unittest
from pathlib import Path
from pet_http63 import create_server
from pet_infer63 import MODEL

class ScopedHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.calls=[]
        def provider(msg):
            payload=json.loads(msg[1]['content']);cls.calls.append(payload)
            eid=payload['evidence'][0]['id']
            return {'response':{'choices':[{'message':{'content':f'Observe more. Evidence is incomplete. {eid}'}}]},'proof':{'live_http_status':200,'requested_model':MODEL,'returned_model':MODEL,'synthetic':True,'latency_ms':1,'usage':{},'timestamp_utc':'test'}}
        cls.server=create_server(str(Path(cls.tmp.name)/'pet.db'),0,provider)
        cls.t=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.t.start()
        cls.v=cls.server.RequestHandlerClass.vault
        cls.a=cls.v.bootstrap_synthetic_owner('A')['session_token']
        cls.b=cls.v.bootstrap_synthetic_owner('B')['session_token']
        cls.p=cls.v.create_pet(cls.a,'Cat','cat')['pet_id']
        cls.q=cls.v.create_pet(cls.a,'Cat','cat')['pet_id']
        cls.v.add_memory(cls.a,cls.p,'Synthetic bowl refilled; intake unconfirmed.')
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.t.join();cls.tmp.cleanup()
    def api(self,path,token=None,body=None,origin=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        h={'Content-Type':'application/json','Host':f'127.0.0.1:{self.server.server_port}'}
        if token:h['Authorization']='Bearer '+token
        if origin:h.update({'Origin':origin,'X-CARLI-Intent':'synthetic-demo'})
        c.request('POST',path,body=json.dumps(body if body is not None else {}),headers=h)
        r=c.getresponse();status=r.status;out=json.loads(r.read());c.close();return status,out
    def test_anonymous_before_provider(self):
        n=len(self.calls);self.assertEqual(self.api(f'/api/pets/{self.p}/infer')[0],403);self.assertEqual(len(self.calls),n)
    def test_cross_owner_before_provider(self):
        n=len(self.calls);self.assertEqual(self.api(f'/api/pets/{self.p}/infer',self.b)[0],403);self.assertEqual(len(self.calls),n)
    def test_empty_pet_no_inference(self):
        n=len(self.calls);self.assertEqual(self.api(f'/api/pets/{self.q}/infer',self.a)[0],422);self.assertEqual(len(self.calls),n)
    def test_valid_scoped_http(self):
        code,res=self.api(f'/api/pets/{self.p}/infer',self.a)
        self.assertEqual(code,200);self.assertEqual(res['proposal']['pet_id'],self.p)
    def test_extra_post_fields_rejected(self):
        n=len(self.calls);self.assertEqual(self.api(f'/api/pets/{self.p}/infer',self.a,{'pet_id':self.q})[0],422);self.assertEqual(len(self.calls),n)
    def test_legacy_api_not_exposed(self):
        self.assertEqual(self.api('/api/infer',self.a)[0],404)
    def test_cross_origin(self):
        n=len(self.calls);self.assertEqual(self.api(f'/api/pets/{self.p}/infer',self.a,origin='https://evil.example')[0],403);self.assertEqual(len(self.calls),n)

    def test_local_validation_gate_reason_opt_in(self):
        import os
        from unittest.mock import patch
        from pet_infer63 import ModelRejected
        def rejected(_messages):raise ModelRejected('CROSS_PET_OR_MISSING_CITATIONS')
        before=self.server.provider
        self.server.provider=rejected
        try:
            with patch.dict(os.environ, {'CARLI_LOCAL_GATE_DIAGNOSTICS':'1'}):
                status,result=self.api(f'/api/pets/{self.p}/infer',self.a)
                self.assertEqual(status,422)
                self.assertEqual(result.get('gate_reason'),'CROSS_PET_OR_MISSING_CITATIONS')
            with patch.dict(os.environ, {'CARLI_LOCAL_GATE_DIAGNOSTICS':'0'}):
                status,result=self.api(f'/api/pets/{self.p}/infer',self.a)
                self.assertEqual(status,422)
                self.assertNotIn('gate_reason',result)
        finally:self.server.provider=before

if __name__=='__main__':unittest.main()
