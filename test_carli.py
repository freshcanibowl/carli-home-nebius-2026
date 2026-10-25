import unittest,tempfile,json
from pathlib import Path
from unittest.mock import patch
import carli
GOOD='Water intake has not been measured in these synthetic notes (evt-001); observe and log drinking. Evidence is incomplete.'
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.patch=patch.object(carli,'DB',Path(self.tmp.name)/'test.sqlite3');self.patch.start()
 def tearDown(self):self.patch.stop();self.tmp.cleanup()
 def proposal(self):return carli.create_proposal(GOOD)
 def test_data(self):self.assertEqual(len(carli.events()),4)
 def test_no_key(self):
  with patch.dict('os.environ',{'NEBIUS_API_KEY':''}):
   with self.assertRaisesRegex(RuntimeError,'LIVE_INFERENCE_BLOCKED'):carli.infer()
 def test_approved_persists_across_connections(self):
  p=self.proposal();r=carli.decide(p['proposal_id'],p['digest'],'APPROVE');self.assertTrue(r['write_performed']);self.assertEqual(len(carli.status()['reminders']),1)
 def test_replay(self):
  p=self.proposal();carli.decide(p['proposal_id'],p['digest'],'APPROVE')
  with self.assertRaisesRegex(RuntimeError,'NO_PENDING'):carli.decide(p['proposal_id'],p['digest'],'APPROVE')
 def test_deny_no_reminder(self):
  p=self.proposal();self.assertFalse(carli.decide(p['proposal_id'],p['digest'],'DENY')['write_performed']);self.assertFalse(carli.status()['reminders'])
 def test_wrong_digest(self):
  p=self.proposal()
  with self.assertRaisesRegex(ValueError,'BINDING'):carli.decide(p['proposal_id'],'bad','APPROVE')
  self.assertEqual(len(carli.status()['pending']),1)
 def test_tamper_text(self):
  p=self.proposal()
  with carli.db() as c:
   altered=dict(p);altered['text']='changed';c.execute('UPDATE proposals SET body=? WHERE id=?',(carli.canon(altered),p['proposal_id']))
  with self.assertRaisesRegex(ValueError,'TAMPERED'):carli.decide(p['proposal_id'],p['digest'],'APPROVE')
  self.assertFalse(carli.status()['reminders'])
 def test_missing_water_not_zero(self):
  with self.assertRaisesRegex(ValueError,'UNSAFE'):carli.create_proposal('No water consumption observed (evt-001).')
 def test_fake_citation(self):
  with self.assertRaisesRegex(ValueError,'UNVERIFIED'):carli.create_proposal('Please observe (evt-999).')
 def test_no_citation(self):
  with self.assertRaisesRegex(ValueError,'UNVERIFIED'):carli.create_proposal('Please observe and log drinking.')
 def test_no_medication(self):
  with self.assertRaisesRegex(ValueError,'UNSAFE'):carli.create_proposal('Give medication (evt-001).')
 def test_invalid_decision(self):
  p=self.proposal()
  with self.assertRaisesRegex(ValueError,'INVALID_DECISION'):carli.decide(p['proposal_id'],p['digest'],'YES')
 def test_receipt_bound_to_reminder(self):
  p=self.proposal();r=carli.decide(p['proposal_id'],p['digest'],'APPROVE');self.assertEqual(carli.status()['reminders'][0]['id'],r['reminder_id'])
 def test_no_pending(self):
  with self.assertRaisesRegex(RuntimeError,'NO_PENDING'):carli.decide('missing','missing','APPROVE')
if __name__=='__main__':unittest.main()
