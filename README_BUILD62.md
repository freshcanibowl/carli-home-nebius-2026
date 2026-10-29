# CARLi Build 6.2 — Server-side synthetic pet isolation (Stage 1)

**Scope:** Additive isolated backend contract and negative security tests. **Not** a replacement for `web.py`, **not** production authentication, **not** a working multi-pet NVIDIA UI. Avoid merging to `main`.

## What it proves

- Each owner is provisioned an opaque random demo session (only hashed token stored in SQLite).
- Each pet has stable UUID and belongs to one server-resolved owner.
- Every memory, proposal, receipt and reminder is scoped to a pet UUID, including verification at read and write.
- Same-name cats remain isolated. Crossing pets/owners, spoofed sessions, mismatched proposal/digest, replays and tampering fail closed.
- Approval is an atomic SQLite transaction, creating **RECORDED_NOT_SCHEDULED** only. No scheduling, medications or clinical actions.
- No legacy Pika data is loaded; synthetic-only per-pet observations. `propose` creates a human-authored **test** proposal, not NVIDIA reasoning.

## Installation

From Build 6.2 worktree, copy `pet_vault62.py`, `test_pet_vault62.py` into the repo root and run `py -m unittest discover -v`. Existing `web.py`/`carli.py` and UI are unchanged. You should see original 34 tests plus 19 new tests. No API endpoint is exposed by this module.

## Next gate before any public judge demo

1. Build an authenticated HTTP adapter that enforces these session + pet checks on every endpoint and **disables legacy unscoped `/api/status`, `/api/infer`, `/api/decide` from untrusted public access**.
2. Ensure live NVIDIA inference takes *only server-authorized, pet-specific evidence*, binds the exact pet ID and digest to any proposal, and remains governed by approval.
3. Add HTTP attack tests, switch-while-inference-pending tests, rate limiting, HTTPS and resource caps.
4. Replace synthetic demo auth with proper authentication before handling real customers or uploading photos.

**Do not tell judges this stage already implements login or multi-pet inference.**
