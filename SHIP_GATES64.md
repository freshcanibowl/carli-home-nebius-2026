# Build 6.4 SHIP / NO-SHIP gates

Source of truth: official https://nebiusglobalaihackathon.devpost.com/rules (checked Oct 25, 2026).

| Gate | Evidence | Current |
|---|---|---|
| Stage 6.3 pinned commit | `9e2d825c7fc0b91514fda0b80069da267146664d` remote matching user Windows log | PASS |
| Synthetic real model E2E | `STAGE3 LIVE GATE PASS` logged, Nemotron via Nebius HTTP 200 | PASS |
| Windows full regression | `Ran 99 tests ... OK` reported | PASS |
| Public repository / root license | Check `main` / branch visibility and LICENSE in submission | VERIFY |
| Reviewer install instructions | README_JUDGE64.md | DRAFT |
| Judge-accessible running app or test build | Persistent URL OR supported downloadable demo + authorized access; local 127.0.0.1 is **not accessible to judges** | BLOCKED |
| Protected API keys / cost controls | Requires separate hosted delivery security review | BLOCKED |
| Public YouTube under 3m | Real recording, public video URL | BLOCKED |
| Devpost submission | Confirmation page / URL and official mandatory fields | BLOCKED |
| Test access through Dec 15 | Access control, uptime and credits plan | BLOCKED |

**Deadline:** Oct 30 2026 10AM PDT = Oct 31 2026 1AM Malaysia Time (MYT).

No public expose of local `web.py`, `pet_http62.py` or `pet_http63.py`. Synthetic session tokens are test identities, not user authentication. Do not suggest exposing those ports with a tunnel as a shortcut.

**Reviewer access trade-off:** An emailed/downloadable local test build with the included Python script can prove memory/approval offline; it cannot demonstrate live Nebius without independently authorized model credentials or a secured inference gateway. Do not mark hosted demo PASS based on a zip alone.
