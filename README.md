# CARLi Home Build 4 — Local Interactive Web Demo

## Verified scope

Build 4 wraps the Build 3.1 `carli.py` functions without modifying their approval, evidence, digest, or SQLite semantics. Browser UI displays four synthetic memory events, performs **real** Nebius Token Factory inference, presents an explicit APPROVE/DENY gate, and shows durable receipts and reminders. It is not a production web application.

## Windows PowerShell

```powershell
Set-Location "$env:USERPROFILE\Downloads\CARLi_Build4\carli_home_build4"
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
$env:NEBIUS_MODEL = 'nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B'
$env:NEBIUS_BASE_URL = 'https://api.tokenfactory.nebius.com/v1'
# If key is not set, enter it without echoing:
if (-not $env:NEBIUS_API_KEY) {
    $secret = Read-Host 'Nebius API Key' -AsSecureString
    $env:NEBIUS_API_KEY = [System.Net.NetworkCredential]::new('', $secret).Password
}
py -m unittest discover -v
py .\web.py
```

Open http://127.0.0.1:8765/ on **the same computer**. Keep the terminal running; Ctrl+C stops the server. Use a different port via `py .\web.py --port 8766` if necessary.

## Important data boundaries

- The included `carli_synthetic.sqlite3` is **not** distributed. Build 4 starts a new, empty local SQLite database. Build 3.1 data stays in the Build 3.1 folder. To use the **same** historical Build 3.1 synthetic DB, explicitly set `CARLI_DB_PATH` to its full path **before starting** the server. Never copy real or private CAIOS data into this demo.
- A recorded reminder has `RECORDED_NOT_SCHEDULED` status; it is **not** a scheduled alert.
- API key stays in the Python server environment and is never returned to the browser.
- Local-only server binds `127.0.0.1`, enforces Host/Origin, requires a per-process CSRF token on writes, and limits request size. This is a demo guard, not production authentication. Do **not** deploy it publicly.
- A live inference may be rejected by the safety gate. A rejected result does not create a pending proposal; no mocked inference fallback.
- No clinical diagnosis, medication, device actuation, or external side effects.

## Acceptance gates

1. `py -m unittest discover -v` passes **24 tests** (14 core + 10 HTTP).
2. Browser timeline shows four synthetic events.
3. Live reasoning returns a model proof and a pending proposal, or clearly shows a fail-closed gate error.
4. Owner reviews and explicitly approves or denies; no automatic approval.
5. Refresh browser: recorded reminder/receipt persist. Restart server: SQLite still persists.
6. Attempt replay via same proposal must be rejected.

## Privacy / IP

Independent hackathon prototype. No CAIOS private code, production credentials, real animal health data, or real actions included. Keep `.env`, SQLite, proofs, and API keys out of Git.


## Build 5 submission kit
See SHIP_CHECKLIST.md, DEVPOST_DRAFT.md, VIDEO_SCRIPT.md. Run `py ship_check.py` before any publication. MIT LICENSE applies only to files intentionally released in this standalone repository; it does not grant rights to external CARLi/CAIOS background IP.
