import unittest
from pathlib import Path
class Build61Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(__file__).resolve().parent
        cls.html=(root/'index.html').read_text(encoding='utf-8')
        cls.js=(root/'app.js').read_text(encoding='utf-8')
        cls.css=(root/'design.css').read_text(encoding='utf-8')
    def test_local_profile_fields(self):
        for field in ('pet-name','pet-species','pet-photo','pet-mode'):
            self.assertIn('id="'+field+'"',self.html)
    def test_guard_before_infer(self):
        self.assertIn('requireDemo();const result=await api(\'/api/infer\'',self.js)
    def test_guard_before_decide(self):
        self.assertIn('requireDemo();const receipt=await api(\'/api/decide\'',self.js)
    def test_preview_hides_evidence(self):
        self.assertIn('No Pika events are shown in preview mode',self.js)
        self.assertIn('Pika receipts stay hidden',self.js)
    def test_photo_local_only(self):
        self.assertIn('URL.createObjectURL(f)',self.js)
        self.assertIn('URL.revokeObjectURL(photoURL)',self.js)
        self.assertIn('4*1024*1024',self.js)
    def test_no_false_auth(self):
        self.assertNotIn('Sign in',self.html)
        self.assertIn('visual preview only',self.html)
    def test_no_new_backend_endpoint(self):
        self.assertNotIn('/api/pets',self.js)
        self.assertNotIn('/api/upload',self.js)
    def test_existing_endpoints(self):
        for route in ('/api/infer','/api/decide','/api/status','/api/session'):
            self.assertIn(route,self.js)
    def test_responsive(self):
        self.assertIn('@media(max-width:640px)',self.css)
        self.assertIn('prefers-reduced-motion',self.css)
    def test_safety_copy(self):
        for text in ('SYNTHETIC DEMO','Non-diagnostic','RECORDED_NOT_SCHEDULED','local-only'):
            self.assertIn(text.lower(),self.html.lower())
if __name__=='__main__': unittest.main()
