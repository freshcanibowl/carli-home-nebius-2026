# CARLi Home — Build 6.5 Judge Access (downloadable, offline mode)

**Pinned baseline**: `8c6d2ba0eb612643a4102159a312649637ae4d13` on `feat/build6-pet-scoped-inference`. The new Build 6.5 commit, when created, supersedes this baseline; record the new SHA in the submission.

## Judge access mode 1 — no credentials, offline and synthetic

Prerequisites: public repository clone, Python 3.11+ (standard library only); `feat/build65-judge-access` branch, pinned to the eventual Build 6.5 commit.

```powershell
py judge_walkthrough65.py
py -m unittest test_judge_walkthrough65 -v
py judge_test64.py
```

`judge_walkthrough65.py` creates a temporary SQLite database, creates **two cats with the same name and distinct pet IDs**, writes one synthetic observation to Cat A, verifies Cat B sees none, creates a *human-authored* pending reminder proposal (NOT a model output), blocks cross-pet approval, approves Cat A in a predetermined offline test, and verifies receipts after a SQLite reconnection. It prints `OFFLINE_WALKTHROUGH_PASS` on success and automatically removes its temporary database.

**This is a deterministic technical test, not the live NVIDIA demo, not browser UI, and not an owner-interactive approval flow.** The scripted APPROVE checks Vault behavior only.

## Judge access mode 2 — real Nebius inference, separately authorized

`py live_gate63.py` exercises **real** NVIDIA Nemotron 3 Nano via Nebius Token Factory, requires an independently authorized `NEBIUS_API_KEY` environment variable and explicitly asks the operator to type APPROVE/DENY. This is not free or universally available to judges. Never put the API key or session token in GitHub, the browser bundle, screenshots or Devpost.

## Security and limitations

No public hosted demo has been built or deployed in this stage. The legacy and pet-scoped localhost APIs must **not** be exposed via tunnelling or host binding. The synthetic sessions are not production login, and the saved observation reminder is `RECORDED_NOT_SCHEDULED`, **not** an OS alert. This Judge Access Mode 1 allows independent offline inspection without secrets but does not prove the full live-inference experience to judges. Verify organizer acceptance of a downloadable test build and how judges obtain authorized inference access before claiming the competition's working-demo requirement is fulfilled.

## Submission evidence placeholders (do not fill until real)

- Judge access URL / downloadable package: **PENDING**
- Public YouTube (<3 minutes): **PENDING**
- Final Devpost project page: **PENDING**
- Access through judging end-date: **PENDING**
