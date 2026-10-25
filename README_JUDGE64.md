# CARLi Home — Judge Kit, Build 6.4

**Project:** CARLi Home — Governed Personal AI for Longitudinal Pet Memory  
**Track:** Personal AI, Nebius × NVIDIA Global AI Hackathon 2026  
**Pinned source:** `freshcanibowl/carli-home-nebius-2026`, Build 6.3 baseline `9e2d825c7fc0b91514fda0b80069da267146664d`.

## What is verified

- Windows Build 6.3 baseline: 99 passing unit/integration tests.
- One real NVIDIA Nemotron 3 Nano inference via Nebius Token Factory completed with HTTP 200 and 1195 ms as reported by the developer's Windows log.
- In that synthetic demo, Pet A had one evidence-grounded proposal; Pet B approval was denied with 403; Pet A owner explicitly typed APPROVE; exactly one Pet A reminder was **recorded, not scheduled**; Pet B had none; SQLite reload passed.

**Not production:** Session identity is provisioned offline for synthetic tests; there is no public multi-user authentication, medical decisioning, cloud push alerts or physical action. The original Pika web frontend (port 8765) is unscoped and must never be exposed to the Internet. The pet-scoped Stage 3 API is loopback-only (8767). There is no hosted judge URL yet.

## Reviewer quick start (Windows / PowerShell)

1. Clone the repository and checkout the `feat/build6-pet-scoped-inference` branch (or a verified, pinned judging build). Verify its commit SHA.
2. Install Python 3.11+; standard library only. Do not paste credentials into any repository file.
3. Run `py -m unittest discover -q`, then `py judge_test64.py` and `py judge_preflight64.py` after adding this Judge Kit.
4. **To run real model inference:** provide a personally authorized `NEBIUS_API_KEY` in the process environment, run `py live_gate63.py`. A real Nebius endpoint/API key is required. The test creates its own temporary, synthetic-only database and asks for an explicit `APPROVE` or `DENY` decision.
5. The local test harness is not an independently hosted demo; to meet competition judge-access requirements, provide a properly secured hosted demo or judge test build with authorized inference access and cost caps.

## How it works

Authenticated *synthetic session token* → owner-scoped pet ID → pet-only SQLite memory → bounded evidence → Nebius Token Factory (NVIDIA Nemotron 3 Nano) → UUID citation + non-diagnostic safety validation → digest-bound pending proposal → owner approval → pet-scoped SQLite receipt and `RECORDED_NOT_SCHEDULED` reminder.

## Key security evidence

- Identical pet names are intentionally supported; identity is a unique pet UUID.
- Foreign-owner/pet reads, writes, citations, approvals and replays are rejected.
- No provider inference is performed before authorization or when target pet evidence is absent.
- Original Pika server (`web.py`, 8765) remains independent and unsafe for public Internet exposure.
- Deterministic provider stubs in automated unit tests are **mocked**. Only `live_gate63.py` with an actual API response verifies live NVIDIA inference.

## Legal and eligibility checks

Verify repository public visibility, top-level OSI license, and significant hackathon-period change evidence on GitHub. Public YouTube video <3 minutes. Provide an English project description, track, explicit Nebius/NVIDIA technology feedback, and a judge-accessible test build or hosted URL. Keep access available through Dec 15, 2026. Do not state these gates are passed until independently verified.
