# Build 6.5 submission gate — evidence only

| Gate | State | Evidence / action |
|---|---|---|
| Build 6.4 frozen SHA | PASS | `8c6d2ba0eb612643a4102159a312649637ae4d13`, user-verified remote |
| Baseline Windows tests | PASS | 102 tests OK in Windows on Build 6.4 |
| Baseline Judge preflight | PASS | 15/15 reported in Windows |
| Build 6.5 offline walkthrough | WAIT WINDOWS | Execute `py judge_walkthrough65.py`; no provider or credentials |
| Build 6.5 full regression | WAIT WINDOWS | Expected 104 tests (102 + 2) |
| Build 6.5 GitHub SHA | WAIT WINDOWS | Commit and push dedicated branch, compare SHA |
| Real pet-scoped Nebius inference | PASS historical | User Windows Build 6.3 log: HTTP 200, cross-pet 403, owner approval, SQLite reload; not re-run in Build 6.5 |
| Independently accessible live demo | BLOCKED | No secure hosted site or independent authorized live inference established |
| Public YouTube <3m | BLOCKED | Need actual video URL |
| Devpost submitted confirmation | BLOCKED | Need confirmation URL/receipt |
| Judge access throughout review | BLOCKED | Need actual access and longevity plan |

**GO for offline downloadable reviewer walkthrough only** after Windows validation. **NO-GO for final competition submission completeness** until organizer's working-demo access requirement and external deliverables are demonstrably satisfied. Do not expose localhost or share personal/provider secrets.
