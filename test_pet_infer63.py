"""Deterministic provider stubs test guards; they are NEVER displayed as live model proof."""
import json, tempfile, unittest, os, io, urllib.request
from unittest.mock import patch
from pathlib import Path
from pet_vault62 import Vault, AccessDenied, InvalidOperation
from pet_infer63 import infer_for_pet, validate_response, ModelRejected, MODEL

class ScopedInferenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.v=Vault(Path(self.tmp.name)/'pet.db')
        self.a=self.v.bootstrap_synthetic_owner('A')['session_token']
        self.b=self.v.bootstrap_synthetic_owner('B')['session_token']
        self.p=self.v.create_pet(self.a,'Luna','cat')['pet_id']
        self.q=self.v.create_pet(self.a,'Luna','cat')['pet_id']
        self.r=self.v.create_pet(self.b,'Luna','cat')['pet_id']
        self.e=self.v.add_memory(self.a,self.p,'Bowl was refilled; consumption not measured.')['id']
        self.f=self.v.add_memory(self.a,self.q,'A short walk reported.')['id']
        self.calls=[]
    def tearDown(self):self.tmp.cleanup()
    def provider(self,messages):
        self.calls.append(json.loads(messages[1]['content']))
        e=self.calls[-1]['evidence'][0]['id']
        return {'response':{'choices':[{'message':{'content':f'Observe and log more. Evidence is incomplete. Source {e}.'}}]},'proof':{'live_http_status':200,'requested_model':MODEL,'returned_model':MODEL,'usage':{'total_tokens':22},'latency_ms':8,'timestamp_utc':'synthetic-test','synthetic':True}}
    def test_nebius_request_disables_thinking_and_preserves_model(self):
        from pet_infer63 import call_nebius
        captured={}
        class Reply:
            status=200
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self):return b'{"model":"nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B","choices":[{"message":{"content":"ok"}}]}'
        def send(req, timeout):
            captured['url']=req.full_url
            captured['body']=json.loads(req.data.decode('utf-8'))
            return Reply()
        with patch.dict(os.environ,{'NEBIUS_API_KEY':'test-never-real','NEBIUS_MODEL':MODEL,'NEBIUS_BASE_URL':'https://api.tokenfactory.nebius.com/v1'}), patch.object(urllib.request,'urlopen',side_effect=send):
            out=call_nebius([{'role':'user','content':'synthetic'}])
        self.assertEqual(captured['body']['model'],MODEL)
        self.assertIs(captured['body']['chat_template_kwargs']['enable_thinking'],False)
        self.assertLessEqual(captured['body']['max_tokens'],512)
        self.assertEqual(out['proof']['live_http_status'],200)
        self.assertTrue(captured['url'].startswith('https://api.tokenfactory.nebius.com/v1/'))

    def test_scoped_prompt(self):
        output=infer_for_pet(self.v,self.a,self.p,self.provider)
        self.assertEqual(self.calls[0]['pet']['pet_id'],self.p)
        self.assertEqual([x['id'] for x in self.calls[0]['evidence']],[self.e])
        self.assertNotIn(self.f,json.dumps(self.calls))
        self.assertEqual(output['proposal']['pet_id'],self.p)
    def test_same_name_different_pet(self):
        infer_for_pet(self.v,self.a,self.q,self.provider)
        self.assertEqual(self.calls[0]['evidence'][0]['id'],self.f)
    def test_unauthorized_zero_provider_calls(self):
        with self.assertRaises(AccessDenied):infer_for_pet(self.v,self.b,self.p,self.provider)
        self.assertEqual(self.calls,[])
    def test_no_evidence_zero_calls(self):
        z=self.v.create_pet(self.a,'None','dog')['pet_id']
        with self.assertRaises(InvalidOperation):infer_for_pet(self.v,self.a,z,self.provider)
        self.assertEqual(self.calls,[])
    def test_cross_pet_citation_fail_closed(self):
        def wrong(msg):
            d=self.provider(msg)
            d['response']['choices'][0]['message']['content']=f'Evidence incomplete. Observe more. {self.f}'
            return d
        with self.assertRaises(ModelRejected):infer_for_pet(self.v,self.a,self.p,wrong)
        self.assertEqual(self.v.get_pet_state(self.a,self.p)['pending'],[])
    def test_no_citation(self):
        with self.assertRaises(ModelRejected):validate_response({'choices':[{'message':{'content':'Observe more; incomplete evidence.'}}]},{self.e})
    def test_empty_model_text_fail_closed(self):
        with self.assertRaisesRegex(ModelRejected,'MODEL_CONTENT_EMPTY'):
            validate_response({'choices':[{'message':{'content':''}}]},{self.e})
    def test_long_model_text_fail_closed(self):
        with self.assertRaisesRegex(ModelRejected,'MODEL_CONTENT_TOO_LONG'):
            validate_response({'choices':[{'message':{'content':'x'*501}}]},{self.e})
    def test_wrong_type_fail_closed(self):
        with self.assertRaisesRegex(ModelRejected,'MODEL_CONTENT_WRONG_TYPE'):
            validate_response({'choices':[{'message':{'content':42}}]},{self.e})
    def test_missing_content_distinguished(self):
        with self.assertRaisesRegex(ModelRejected,'MODEL_CONTENT_MISSING'):
            validate_response({'choices':[{'finish_reason':'stop','message':{'content':None}}]},{self.e})
    def test_reasoning_budget_exhausted_fails_closed(self):
        with self.assertRaisesRegex(ModelRejected,'MODEL_OUTPUT_BUDGET_EXHAUSTED'):
            validate_response({'choices':[{'finish_reason':'length','message':{'content':None}}]},{self.e})
    def test_typed_text_parts_accepted_and_validated(self):
        text=f'Observe and log; intake remains unconfirmed. Evidence: {self.e}'
        actual,cites=validate_response({'choices':[{'message':{'content':[{'type':'text','text':text}]}}]},{self.e})
        self.assertEqual(actual,text)
        self.assertEqual(cites,[self.e])
    def test_mixed_text_nontext_rejected(self):
        with self.assertRaisesRegex(ModelRejected,'MODEL_CONTENT_UNSUPPORTED_PARTS'):
            validate_response({'choices':[{'message':{'content':[{'type':'text','text':'hi'},{'type':'image','url':'x'}]}}]},{self.e})
    def test_reasoning_text_never_used_as_answer(self):
        with self.assertRaisesRegex(ModelRejected,'MODEL_CONTENT_MISSING'):
            validate_response({'choices':[{'message':{'content':None,'reasoning_content':f'Observe; incomplete. {self.e}'}}]},{self.e})
    def test_medication_rejected(self):
        with self.assertRaises(ModelRejected):validate_response({'choices':[{'message':{'content':f'Prescribe medication; evidence incomplete {self.e}'}}]},{self.e})
    def test_uncertainty_required(self):
        with self.assertRaises(ModelRejected):validate_response({'choices':[{'message':{'content':f'Observe your cat {self.e}'}}]},{self.e})
    def test_digested_model_proof_persisted(self):
        p=infer_for_pet(self.v,self.a,self.p,self.provider)['proposal']
        self.assertEqual(p['model_proof']['requested_model'],MODEL)
        self.assertEqual(self.v.get_pet_state(self.a,self.p)['pending'][0]['digest'],p['digest'])
    def test_cross_pet_approval_rejected(self):
        p=infer_for_pet(self.v,self.a,self.p,self.provider)['proposal']
        with self.assertRaises(AccessDenied):self.v.decide(self.a,self.q,p['proposal_id'],p['digest'],'APPROVE')
        self.assertEqual(self.v.get_pet_state(self.a,self.q)['reminders'],[])
    def test_approved_binds_receipt(self):
        p=infer_for_pet(self.v,self.a,self.p,self.provider)['proposal']
        receipt=self.v.decide(self.a,self.p,p['proposal_id'],p['digest'],'APPROVE')
        self.assertEqual(receipt['pet_id'],self.p)
        self.assertEqual(self.v.get_pet_state(self.a,self.p)['reminders'][0]['status'],'RECORDED_NOT_SCHEDULED')
        self.assertFalse(self.v.get_pet_state(self.a,self.q)['receipts'])
    def test_switching_pet_changes_only_target(self):
        p=infer_for_pet(self.v,self.a,self.p,self.provider)['proposal']
        infer_for_pet(self.v,self.a,self.q,self.provider)
        self.assertEqual(p['pet_id'],self.p)
        self.assertEqual(len(self.v.get_pet_state(self.a,self.q)['pending']),1)
        self.assertEqual(self.v.get_pet_state(self.a,self.p)['pending'][0]['proposal_id'],p['proposal_id'])
    def test_provider_not_verified(self):
        def bad(msg):
            d=self.provider(msg);d['proof']['live_http_status']=0;return d
        with self.assertRaises(ModelRejected):infer_for_pet(self.v,self.a,self.p,bad)

if __name__=='__main__':unittest.main()
