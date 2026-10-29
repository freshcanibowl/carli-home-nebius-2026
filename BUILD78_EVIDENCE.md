# Build 78 — Secure Agent execution evidence (2026-10-29)

## Artifact
Chat deliverable: `CARLi_Build78_Secure_Agent.zip` SHA256 `d6a486b16ce011f557503c8517e3e1b51a57d02b4fd52deb255c58d49e3a4d02`. It embeds exact original Build76 judge-site files and a new stdlib local-only `agent_runtime`.

## Executed tests (isolated container)
- `python -m unittest discover -s agent_runtime/tests -v`: **12/12 PASS**.
- `python -m agent_runtime.offline_demo`: **OFFLINE_BUILD78_PASS**; cross-pet approval blocked, SQLite receipt reconnect verified.
- `cd judge-site && npm test`: **8/8 PASS**, with provider fetch mocked during tests.
- ZIP integrity: PASS, 15 files.
- Original Windows Python backend historical 104/104 PASS at earlier pinned Build65 baseline. Not rerun for this artifact.

## Boundaries
- This is a **local-only prototype**, not a deployed authenticated backend.
- NemoClaw, OpenShell, Hermes Agent, Nebius Serverless: **NOT integrated**.
- Build76 online Nebius live call: **UNVERIFIED**; no credentials provided.
- Vercel Preview secret listing last showed **none**; no production deployment.
- User must download and run `scripts/SHIP_BUILD78.ps1` in the ZIP to commit the **actual source code** to this branch, after all local tests pass; script requires explicit `PUSH-BUILD78` and forbids missing source integrity.
- Do not merge PR #1 until source is actually pushed and CI is green.

## Access and safety
No GitHub main merge. No Devpost submission. No secrets, tenant production data or live medical decisions.
