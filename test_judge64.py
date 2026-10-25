import unittest, tempfile, subprocess, pathlib, sys
from judge_preflight64 import run
class JudgeKitTests(unittest.TestCase):
    def test_preflight_has_no_secret_contents(self):
        d=run(pathlib.Path.cwd())
        self.assertEqual(d['schema'],'carli-judge-preflight/1')
        self.assertNotIn('NEBIUS_API_KEY',str(d))
    def test_preflight_reports_expected_files(self):
        d=run(pathlib.Path.cwd())
        self.assertTrue(d['checks']['file_pet_infer63.py'])
        self.assertTrue(d['checks']['file_live_gate63.py'])
    def test_preflight_does_not_claim_deploy(self):
        self.assertIn('not proof of public judge access',run(pathlib.Path.cwd())['limitations'])
if __name__=='__main__': unittest.main()
