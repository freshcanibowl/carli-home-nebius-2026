# CARLi Build 6.2 Stage 2 — Local Synthetic Pet HTTP Isolation

## Scope

This is a **separate localhost-only test server** on `127.0.0.1:8766` that provides a pet-scoped HTTP facade for Stage 1 `pet_vault62.Vault`.

- **DOES NOT modify or replace** `web.py`, `carli.py`, Build 5 `main` or the Build 6.1 UI.
- **DOES NOT provide login, production authorization or live NVIDIA inference.** Only synthetic server-provisioned owner bearer tokens can authenticate. They are **not** real login sessions.
- Never expose this server outside localhost. Never commit session tokens or live customer data.
- Legacy `/api/status`, `/api/session`, `/api/infer`, `/api/decide` endpoints are NOT provided on this port.

## API (synthetic test only)

- `GET /api/pets` — authenticated owner's pet list
- `POST /api/pets` — synthetic pet creation: `{ "name": "Luna", "species": "cat" }`
- `GET /api/pets/{pet_id}/state` — only that owner's pet data
- `POST /api/pets/{pet_id}/memories` — `{ "observation": "..." }`
- `POST /api/pets/{pet_id}/proposals` — human-authored synthetic proposal with evidence IDs
- `POST /api/pets/{pet_id}/decisions` — explicit approval or denial, matching bound proposal and digest

Every endpoint requires `Authorization: Bearer <opaque synthetic session token>`. Tokens are only provisioned using `Vault.bootstrap_synthetic_owner()` in a local test harness (never through HTTP). For browser-originated POST requests, a same-origin check and `X-CARLI-Intent: synthetic-demo` are required. These **are not substitutes for production authentication or CSRF protection**. Server bind: `127.0.0.1` only.

## Installation

Run PowerShell from `C:\Users\Asus\Downloads\CARLi_Build6_2`. Copy only `pet_http62.py`, `test_pet_http62.py`, and this README into the worktree. Do not overwrite Stage 1 `pet_vault62.py` or `test_pet_vault62.py`.

```powershell
py -m unittest test_pet_http62 -v
if ($LASTEXITCODE -ne 0) { throw 'Stage 2 failed' }
py -m unittest discover -v
if ($LASTEXITCODE -ne 0) { throw 'Full regression failed' }
```

Expected: **16 new Stage 2 tests** + **53 earlier tests** = **69 total tests** (provided Stage 1 Windows SQLite fix is installed).

## Non-goals / failure gates

- Old `web.py` remains a separately running Pika-only localhost demo on port 8765. **Do not publicly expose either server**.
- This is **not full multi-pet inference**. A separate future gate must bind `pet_id`, owner session, evidence set, model proposal, and decision in one authorization flow; do not route new pets to legacy `carli.infer()`.
- Confirm that cross-owner and cross-pet attempts fail **at the HTTP boundary**, not merely via UI buttons. Confirm a legitimate owner can still approve and that replay fails.
- Synthetic only, non-diagnostic; approved reminders `RECORDED_NOT_SCHEDULED`, not scheduled alerts.
- No commit/push/merge until Windows tests pass. Keep main intact.
