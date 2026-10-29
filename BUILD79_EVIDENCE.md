# Build79 Local Agent Gate — Verification Receipt

Date: 2026-10-29. Artifact: `CARLi_Build79_Agent_Gates.zip`.

SHA256: `6a712de6614d6d5fdb8da2e1c4d87ce48d99d40f71e33e13a55e0eca9d710508`

## Locally executed
- Python tests: **26/26 PASS**; includes 14 new gate tests and 12 original Build78 tests.
- Node serverless API tests: **8/8 PASS** (provider mocked in tests).
- Offline local approval demo: **PASS**, `RECORDED_NOT_SCHEDULED`, denied cross-pet action, no network use.
- ZIP CRC integrity: **PASS** (19 files).

## What Build79 adds
- `agent_runtime/agent_gate79.py`: explicit model allowlist, evidence ID syntax/uniqueness, risk rejection, action allowlist, owner approval gate.
- `agent_runtime/tests/test_agent_gate79.py`: 14 tests.
- `scripts/PUSH_BUILD79.ps1`: verifies earlier Build78 code has been pushed, then tests and asks user to approve Git commit/push.

## NOT VERIFIED
- Actual source push of Build78 or Build79 into GitHub branch.
- Active NemoClaw, OpenShell, Hermes Agent installation, or Nebius Serverless execution.
- Real model inference from Build76 Preview (Vercel env was empty at last check).
- Server-side production auth, cryptographic model proof, official evidence-store verification or publicly available judge access.

Never merge `main` or submit Devpost on this receipt alone.
