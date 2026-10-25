# CARLi Home Build 6.3 — Pet-scoped NVIDIA Reasoning

**Scope:** isolated local-only Stage 3 pet-scoped inference API. **No change to `main`, `carli.py`, `web.py`, or the existing port 8765 demo.** All data synthetic. No actual reminder scheduling; non-diagnostic.

## Files added to Build 6.3 Worktree

- `pet_infer63.py`: real Nebius NVIDIA model call and fail-closed citation safety; enforces ownership before provider call and again during proposal persistence, binds `model_proof` to proposal digest.
- `pet_http63.py`: separate `127.0.0.1:8767` pet-scoped HTTP test server, no legacy unscoped endpoints. Offline-provisioned synthetic session tokens; **not production auth**.
- `test_pet_infer63.py`: 13 deterministic security tests, using provider stubs **only in tests**.
- `test_pet_http63.py`: 7 loopback HTTP tests, using provider stubs **only in tests**.
- `live_gate63.py`: starts its own ephemeral loopback server, provisions two same-name synthetic cats, invokes **real Nebius**, attempts cross-pet approval (403), then requires a typed explicit owner decision and verifies SQLite persistence. Does not print API keys or tokens.

## Verification (PowerShell in Build 6.3 Worktree)

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
py -m unittest discover -v
# 89 tests / OK expected (69 original + 20 new)
```

### Real inference (requires configured key; charges may apply)

```powershell
if (-not $env:NEBIUS_API_KEY) {
  $secret=Read-Host 'Nebius API Key' -AsSecureString
  $env:NEBIUS_API_KEY=[System.Net.NetworkCredential]::new('', $secret).Password
}
py .\live_gate63.py
```

No web-based account registration, photo uploads, production permission guarantees, real pet healthcare, or autonomous actions. Do not deploy the local server publicly or publish credentials.

## Limitations & decisions

1. The old localhost Pika demo on port 8765 still has its original API; never expose it publicly.
2. Stage 3 API is on port 8767, for local testing only. There is not yet one integrated multi-pet front end or secure judge-accessible hosted build.
3. Sessions are provisioned offline with synthetic identities; this is not a production login/permission service.
4. Free-form model output is validated using conservative text checks and strict UUID citations, but **not** equivalent to rigorous medical entailment verification. Failure is closed and no proposal is recorded.
5. The model call may fail due to provider access, latency, formatting or missing citations; do not substitute mock data to claim a live pass.
6. The live gate's temporary SQLite and synthetic records are deleted after the program exits; preserve sanitized output for submission evidence if needed.

## Freeze Gate

- 89/89 unittest PASS on the user's Windows computer.
- Real HTTP 200 for approved `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` provider, correct per-pet evidence and explicit decision.
- Unauthorized and cross-pet inference/approval rejected; no cross-pet receipt leak.
- `git diff main -- carli.py web.py` clean; `main` untouched.
- Do not merge or push until verified.
