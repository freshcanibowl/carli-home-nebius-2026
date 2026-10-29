# CARLi Home Build 77 — integration ledger (2026-10-29)

## Source lineage
- Base: `feat/build65-judge-access` (verified pinned source `c271d6c8de7736d6a08b31e518b397cbc8912fbc`; historical Windows Python tests: 104/104 PASS).
- Earlier build6 branches are incremental ancestors relative to main; avoid duplicate cherry-picks.
- Build76 Vercel serverless judge UI+API is NOT included until the `judge-site/` source files are committed to this branch.
- Build76 local API tests: 8/8 PASS (mocked upstream, **not live inference**).

## Verified Vercel deployment receipts (independent project)
Vercel project: `freshcanibowl-8248s-projects/carli-home-build73-judge-preview`.
- `https://carli-home-build73-judge-preview-l1lz0qzrw.vercel.app` — Ready.
- `https://carli-home-build73-judge-preview-d1879jilv.vercel.app` — Ready; `GET /api/status` returned `SYNTHETIC_ONLY`.
- `https://carli-home-build73-judge-preview-djq7olqym.vercel.app` — Ready; status `SYNTHETIC_ONLY`.
- `https://carli-home-build73-judge-preview-2tm59jrxy.vercel.app` — Ready; no fresh endpoint response yet.
- Preview requests used authenticated `vercel curl`; no anonymous judge accessibility proof. Production domain unchanged.
- `vercel env ls` explicitly showed no environment variables for the independent project; subsequent `env add` attempts failed because a Git branch was supplied even though this project has no connected Git repo. Do NOT assert secret/configuration success.

## Scope and truth labels
- Browser-only UI receipts are local and synthetic, not backend-persisted.
- Approval authorization, tenant-isolation, and durable server receipts are NOT production-grade in Build76.
- `/api/status` is real Vercel Function; `/api/infer` exists but live Nebius response remains UNVERIFIED.
- README and Devpost must not claim judge public access, live model proof or submission as complete.
- Never commit API keys, `.env*`, `.vercel`, local sqlite, receipts containing personal data.
- No changes to existing production project or default branch.

## Remaining release gates
1. Copy verified Build76 files under `judge-site/` (with `api/`, `tests/`, and Vercel config).
2. Run `node --test judge-site/tests/*.test.js`; run Python tests from project root.
3. Commit changes to this isolated integration branch, record exact commit SHA.
4. Independently deploy from `judge-site/` to separate judge Preview and capture SHA/deploy mapping (not yet done).
5. Configure Preview secrets via Vercel UI/CLI with **blank Git branch**; verify `env ls` before redeploy.
6. Record real `/api/infer` HTTP result and the operating model/host; retain deployment protection until access tested.
7. Review PR; no automatic merge to main, no formal Devpost submit.

## Tested behavior and limits
`LIVE_CONFIGURED_NOT_VERIFIED` means variables are present; it is **not** model success. A successful `LIVE_NEBIUS` response is a provider reply, not a reminder sent or a persistence proof.
