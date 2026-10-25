# Build 5 — Freeze & Ship gates

## Verified from user-provided Build 4 screenshot
- Synthetic timeline: 4 events; browser shows NVIDIA model and HTTP 200, 1958 ms, 554 tokens.
- APPROVED decision receipt and 1 SQLite reminder marked RECORDED_NOT_SCHEDULED.
- This screenshot does **not** prove public deployment, actual alert delivery, repository publication or restart persistence.

## Must complete before Devpost submit
- [ ] `py -m unittest discover -v` all 24 pass on Windows.
- [ ] Run `py .\ship_check.py` and inspect the report; no secrets or SQLite tracked.
- [ ] Create a NEW public GitHub repository and publish only this independent synthetic code.
- [ ] Verify published repo is public and has an OSI-approved LICENSE selected by owner (MIT recommended if appropriate).
- [ ] Record GitHub URL, git commit SHA, published timestamp, and source boundary.
- [ ] Verify a reviewer can follow README to run local demo. Do not expose local web.py to public network.
- [ ] Record <=3-minute public video showing live inference, explicit approval and receipt.
- [ ] Complete Devpost with working links, model and technical feedback; confirm official deadline and eligibility.
- [ ] Disclose pre-existing CARLi/CAIOS Background IP and identify hackathon-period additions.

## Scope
Local-only. Not a public deployment. No CAIOS production writes, no real pet data, no medical advice, no real reminders.

## Evidence archive
Save test output, ship report, screenshot, and public commit URL separately; never publish API keys, local DB, live proof files, or `.env`.
