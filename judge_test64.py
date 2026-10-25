"""Simple regression runner; models are mocked only within existing unit tests."""
import subprocess, sys, os
if __name__=='__main__':
    env=os.environ.copy();env['PYTHONUTF8']='1';env['PYTHONIOENCODING']='utf-8'
    print('Running local automated regression. Provider stubs in unit tests are NOT live Nebius evidence.',flush=True)
    rc=subprocess.call([sys.executable,'-m','unittest','discover','-q'],env=env)
    if rc:sys.exit(rc)
    print('UNIT_TEST_GATE_PASS; real inference must be separately verified via live_gate63.py',flush=True)
