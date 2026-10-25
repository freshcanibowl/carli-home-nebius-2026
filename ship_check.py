"""Read-only release preflight. No uploads, git mutations, or network calls."""
from pathlib import Path
import json, subprocess, sys, hashlib
ROOT=Path(__file__).resolve().parent
REQUIRED=['carli.py','web.py','app.js','index.html','synthetic_memory.json','test_carli.py','test_web.py','README.md','SHIP_CHECKLIST.md','DEVPOST_DRAFT.md','VIDEO_SCRIPT.md']
EXCLUDED=['.env','live_proof.json','pending.json','receipts.jsonl']
issues=[]
for name in REQUIRED:
 if not (ROOT/name).is_file(): issues.append('MISSING '+name)
for name in EXCLUDED:
 if (ROOT/name).exists(): issues.append('LOCAL SENSITIVE FILE PRESENT: '+name+' (do not publish)')
for f in ROOT.rglob('*'):
 if f.is_file() and (f.suffix in ('.sqlite3','.db','.pyc') or f.name.startswith('.env')): issues.append('DO NOT PUBLISH: '+str(f.relative_to(ROOT)))
checksums={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in REQUIRED if (ROOT/name).exists()}
report={'result':'PASS' if not issues else 'REVIEW_REQUIRED','issues':issues,'sha256':checksums,'note':'Read-only packaging check; not proof of public publication or clinical validity.'}
print(json.dumps(report,indent=2))
sys.exit(0 if not issues else 1)
