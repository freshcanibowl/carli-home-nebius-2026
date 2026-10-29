"""Offline, synthetic-only, no-key reviewer walkthrough; never claims live inference.

Run from repository root: py judge_walkthrough65.py
This module does not start an HTTP server, call Nebius, or schedule reminders.
"""
import json
import tempfile
from pathlib import Path

from pet_vault62 import Vault, AccessDenied


def run_walkthrough():
    with tempfile.TemporaryDirectory(prefix='carli_judge65_') as folder:
        path = Path(folder) / 'synthetic_judge.sqlite3'
        vault = Vault(path)
        owner = vault.bootstrap_synthetic_owner('Synthetic Judge Owner')
        token = owner['session_token']
        a = vault.create_pet(token, 'Luna', 'cat')
        b = vault.create_pet(token, 'Luna', 'cat')
        assert a['pet_id'] != b['pet_id']
        event = vault.add_memory(token, a['pet_id'], 'Synthetic bowl refill observed; drinking quantity unconfirmed.')
        assert not vault.get_pet_state(token, b['pet_id'])['events']
        proposal = vault.propose(token, a['pet_id'], [event['id']], 'Observe and log drinking; evidence remains incomplete.')
        cross_pet_denied = False
        try:
            vault.decide(token, b['pet_id'], proposal['proposal_id'], proposal['digest'], 'APPROVE')
        except AccessDenied:
            cross_pet_denied = True
        assert cross_pet_denied, 'CROSS_PET_APPROVAL_NOT_BLOCKED'
        receipt = vault.decide(token, a['pet_id'], proposal['proposal_id'], proposal['digest'], 'APPROVE')
        assert receipt['decision'] == 'APPROVED'
        reloaded = Vault(path)
        state_a = reloaded.get_pet_state(token, a['pet_id'])
        state_b = reloaded.get_pet_state(token, b['pet_id'])
        assert len(state_a['reminders']) == 1 and len(state_b['reminders']) == 0
        assert len(state_a['receipts']) == 1 and len(state_b['receipts']) == 0
        assert state_a['reminders'][0]['status'] == 'RECORDED_NOT_SCHEDULED'
        return {'schema': 'carli-judge-walkthrough/1', 'mode': 'OFFLINE_SYNTHETIC_NO_MODEL',
                'pet_ids_distinct': True, 'cross_pet_approval_denied': cross_pet_denied,
                'pet_a_memories': len(state_a['events']), 'pet_b_memories': len(state_b['events']),
                'pet_a_recorded_reminders': len(state_a['reminders']),
                'pet_b_recorded_reminders': len(state_b['reminders']),
                'sqlite_reload_pass': True,
                'live_nvidia_call': False, 'real_notification_scheduled': False,
                'verdict': 'OFFLINE_WALKTHROUGH_PASS'}


if __name__ == '__main__':
    print(json.dumps(run_walkthrough(), indent=2))
