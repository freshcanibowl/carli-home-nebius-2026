"""Deterministic tests of the no-secret reviewer path."""
import unittest
from judge_walkthrough65 import run_walkthrough


class ReviewerWalkthroughTests(unittest.TestCase):
    def test_offline_review(self):
        proof = run_walkthrough()
        self.assertEqual(proof['verdict'], 'OFFLINE_WALKTHROUGH_PASS')
        self.assertTrue(proof['cross_pet_approval_denied'])
        self.assertTrue(proof['sqlite_reload_pass'])
        self.assertFalse(proof['live_nvidia_call'])
        self.assertFalse(proof['real_notification_scheduled'])
        self.assertEqual(proof['pet_b_recorded_reminders'], 0)

    def test_deterministic_counts(self):
        proof = run_walkthrough()
        self.assertEqual(proof['pet_a_memories'], 1)
        self.assertEqual(proof['pet_b_memories'], 0)
        self.assertEqual(proof['pet_a_recorded_reminders'], 1)


if __name__ == '__main__':
    unittest.main()
