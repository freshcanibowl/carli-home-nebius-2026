import unittest,tempfile,sqlite3,json
from contextlib import closing
from pathlib import Path
from pet_vault62 import Vault,AccessDenied,InvalidOperation

class PetIsolationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'isolation.sqlite3';self.v=Vault(self.path)
        self.a=self.v.bootstrap_synthetic_owner('Owner A')['session_token']
        self.b=self.v.bootstrap_synthetic_owner('Owner B')['session_token']
        self.m=self.v.create_pet(self.a,'Momo','cat')['pet_id']
        self.n=self.v.create_pet(self.a,'Momo','cat')['pet_id']
        self.x=self.v.create_pet(self.b,'Pika','dog')['pet_id']
        self.ma=self.v.add_memory(self.a,self.m,'Momo A prefers quiet corners')['id']
        self.na=self.v.add_memory(self.a,self.n,'Momo B prefers windows')['id']
    def tearDown(self):self.tmp.cleanup()
    def test_same_name_unique_id(self):self.assertNotEqual(self.m,self.n)
    def test_same_owner_memory_isolated(self):
        self.assertEqual(len(self.v.list_memory(self.a,self.m)),1)
        self.assertNotIn('windows',json.dumps(self.v.get_pet_state(self.a,self.m)))
    def test_other_owner_memory_denied(self):
        with self.assertRaises(AccessDenied):self.v.list_memory(self.b,self.m)
    def test_owner_id_not_accepted_as_token(self):
        with self.assertRaises(AccessDenied):self.v.list_memory('not-a-real-token',self.m)
    def test_cross_pet_evidence_rejected(self):
        with self.assertRaises(AccessDenied):self.v.propose(self.a,self.m,[self.na],'Observe Momo A')
    def test_cross_owner_evidence_rejected(self):
        with self.assertRaises(AccessDenied):self.v.propose(self.b,self.x,[self.ma],'Observe Pika')
    def test_proposal_binding_to_pet(self):
        p=self.v.propose(self.a,self.m,[self.ma],'Observe Momo A')
        with self.assertRaises(AccessDenied):self.v.decide(self.a,self.n,p['proposal_id'],p['digest'],'APPROVE')
    def test_other_owner_cannot_approve(self):
        p=self.v.propose(self.a,self.m,[self.ma],'Observe Momo A')
        with self.assertRaises(AccessDenied):self.v.decide(self.b,self.m,p['proposal_id'],p['digest'],'APPROVE')
    def test_valid_approval_bound(self):
        p=self.v.propose(self.a,self.m,[self.ma],'Observe Momo A')
        r=self.v.decide(self.a,self.m,p['proposal_id'],p['digest'],'APPROVE')
        self.assertTrue(r['write_performed'])
        self.assertEqual(self.v.get_pet_state(self.a,self.n)['reminders'],[])
        self.assertEqual(self.v.get_pet_state(self.a,self.m)['reminders'][0]['status'],'RECORDED_NOT_SCHEDULED')
    def test_deny_without_write(self):
        p=self.v.propose(self.a,self.m,[self.ma],'Observe Momo A')
        r=self.v.decide(self.a,self.m,p['proposal_id'],p['digest'],'DENY')
        self.assertFalse(r['write_performed']);self.assertEqual(self.v.get_pet_state(self.a,self.m)['reminders'],[])
    def test_replay_rejected(self):
        p=self.v.propose(self.a,self.m,[self.ma],'Observe Momo A')
        self.v.decide(self.a,self.m,p['proposal_id'],p['digest'],'APPROVE')
        with self.assertRaises(InvalidOperation):self.v.decide(self.a,self.m,p['proposal_id'],p['digest'],'APPROVE')
    def test_bad_digest_rejected(self):
        p=self.v.propose(self.a,self.m,[self.ma],'Observe Momo A')
        with self.assertRaises(InvalidOperation):self.v.decide(self.a,self.m,p['proposal_id'],'0'*64,'APPROVE')
        self.assertEqual(self.v.get_pet_state(self.a,self.m)['pending'][0]['proposal_id'],p['proposal_id'])
    def test_tampered_proposal_rejected(self):
        p=self.v.propose(self.a,self.m,[self.ma],'Observe Momo A')
        # sqlite3.Connection context managers commit/rollback but DO NOT close.
        # Explicitly close before TemporaryDirectory cleanup (WinError 32 on Windows).
        with closing(sqlite3.connect(self.path)) as c:
            with c:
                obj=json.loads(c.execute('SELECT body FROM proposals WHERE id=?',(p['proposal_id'],)).fetchone()[0])
                obj['text']='Give medication'
                c.execute('UPDATE proposals SET body=? WHERE id=?',(json.dumps(obj),p['proposal_id']))
        with self.assertRaises(InvalidOperation):self.v.decide(self.a,self.m,p['proposal_id'],p['digest'],'APPROVE')
    def test_reload_persistent_owner_scope(self):
        self.assertEqual(len(Vault(self.path).get_pet_state(self.a,self.m)['events']),1)
        with self.assertRaises(AccessDenied):Vault(self.path).get_pet_state(self.b,self.m)
    def test_unknown_token(self):
        with self.assertRaises(AccessDenied):self.v.list_pets('X'*60)
    def test_invalid_species(self):
        with self.assertRaises(InvalidOperation):self.v.create_pet(self.a,'Mimo','parrot')
    def test_unauthorized_create_memory(self):
        with self.assertRaises(AccessDenied):self.v.add_memory(self.b,self.m,'bad cross-owner')
    def test_cross_pet_receipt_hidden(self):
        p=self.v.propose(self.a,self.m,[self.ma],'Observe Momo A');self.v.decide(self.a,self.m,p['proposal_id'],p['digest'],'APPROVE')
        self.assertEqual(self.v.get_pet_state(self.a,self.n)['receipts'],[])
    def test_no_live_inference_claim(self):
        self.assertFalse(self.v.get_pet_state(self.a,self.m)['live_inference_available'])
if __name__=='__main__':unittest.main()
