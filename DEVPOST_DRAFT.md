# CARLi Home — Governed Pet Memory Agent

**Tagline:** Pika's care, with evidence. Observe the context, propose a safe next step, ask the owner first.

## Inspiration
Pet owners collect fragmented daily observations. An AI assistant should distinguish an unobserved event from a proven absence and ask permission before recording an action.

## What it does
CARLi Home displays a synthetic longitudinal pet-memory timeline, sends that bounded context to an NVIDIA Nemotron model via Nebius Token Factory, generates a citation-bearing low-risk observation reminder, and requires explicit owner approval or denial. Approved reminders and decision receipts are stored in local SQLite.

## How we built it
Python standard library HTTP server, vanilla JavaScript, SQLite, Nebius Token Factory chat completions, NVIDIA Nemotron. Safety gates reject unsupported event IDs and selected unsafe claims. Digest-bound approval and replay protection guard writes.

## Challenges
Model responses vary and can fail evidence-citation gates. Windows Unicode output required explicit UTF-8 handling. A successful HTTP response is not proof of clinical validity.

## Accomplishments
Local Build 4 browser evidence shows HTTP 200 inference (1,958 ms; 554 tokens), a synthetic approved reminder and linked receipt. Local core + Web tests passed 24/24 in the build environment; reproduce on your Windows machine before submission.

## What's next
Expand grounded evidence checks and add a separate production-grade authentication and scheduling system only after appropriate privacy, safety, and security review.

## Limitations
Synthetic-only, non-diagnostic, local-only, no scheduled alerts, no real device actions. Public hosted demo NOT implemented.

## Background IP disclosure
CARLi and CAIOS pre-existed this submission. This independent hackathon prototype uses only synthetic data and standalone demonstration code. Confirm actual commit history and dates before asserting which features were newly written during the competition.

## Links (fill after verification)
GitHub: [PENDING]  Video: [PENDING]  Demo: local-only, installation steps in README.
