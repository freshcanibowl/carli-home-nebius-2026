# Devpost Draft — CARLi Home

## Project Name
CARLi Home — One Pet, One Memory

## Tagline
A governed personal AI that remembers each pet as an individual — with evidence, approval, and auditable actions.

## Track
Personal AI

## Inspiration
Pet parents observe small moments every day: a refilled water bowl, a walk, a change in routine. Yet those observations are scattered, easily forgotten, and often incorrectly treated as conclusions. Even two cats living with the same owner have different histories. CARLi Home explores an AI that remembers each pet separately and refuses to act on weak evidence without the owner's decision.

## What it does
CARLi Home records a longitudinal, pet-specific observation history. When the owner asks for a reflection, the system retrieves only that pet's authorized synthetic evidence and calls NVIDIA Nemotron 3 Nano through Nebius Token Factory. It validates the response against exact observation UUID citations and conservative, non-diagnostic safety checks. The result is a pending observation reminder, not an automatic action. Only an explicit owner approval writes a reminder and receipt to a pet-scoped SQLite store. The recorded reminder is **not a scheduled notification**.

## How we built it
Python standard library local API; SQLite persistent memory and receipts; unique UUID pet identities; SHA-256 canonical proposal digests; owner-scoped synthetic demo sessions; NVIDIA Nemotron 3 Nano accessed via Nebius Token Factory HTTPS Chat Completions. Separate HTTP test gates exercise unauthorized access, same-name pet isolation, cross-pet evidence rejection, and approval replay protection. A warm companion-style Pika demo illustrates a memory journal, while the newer pet-scoped inference service remains an isolated local testing flow.

## Challenges
Reasoning-mode responses initially exhausted the model output budget before producing a final answer. We corrected the request format for short, non-thinking observation reminders while preserving strict citation and human-approval checks. Windows SQLite test cleanup also required explicit connection closure. We did not bypass failed gates to create a successful-looking demo.

## What we learned
A useful personal AI is not just a chatbot. Reliable memory needs an identity boundary, evidence provenance, a bounded action contract, an approval step, and durable receipts. Testing two same-name cats revealed why pet names cannot serve as authorization keys.

## Accomplishments
The developer verified 99/99 automated tests on Windows and one actual Nebius model response (HTTP 200, approximately 1.2 seconds) followed by a rejected cross-pet approval (403), explicit owner approval, a Pet A-only recorded reminder and persistent SQLite receipt. These results relate to synthetic demo data and offline-provisioned test identities, **not production-grade authentication or medical advice**.

## What's next
Integrate the pet-scoped backend with a real authenticated, consent-based multi-pet interface; expand evidence and health safety evaluation; implement privacy-preserving user export/delete controls; and validate real-world longitudinal usefulness with opt-in studies.

## Nebius / NVIDIA Feedback — first-hand developer account (edit before submission)
The Token Factory API enabled a real NVIDIA Nemotron 3 Nano call in our local prototype without self-hosting GPU inference. Our first attempts returned no final text when the model consumed the output budget; explicit non-thinking template control enabled a short validated answer. It would help developers if model-specific thinking controls, finish reasons, and final-content formats were documented with copy-paste examples and clear parameter compatibility. **Confirm this reflects your actual developer experience before submitting.**

## URLs — MUST FILL / VERIFY
- Public repository: https://github.com/freshcanibowl/carli-home-nebius-2026/tree/feat/build6-pet-scoped-inference
- Judge-accessible URL or downloadable test build: **NOT YET VERIFIED**
- Public YouTube video (<3 minutes): **NOT YET PUBLISHED**
- Final Devpost submitted project link: **NOT YET SUBMITTED**

## Prior work and significant updates (adapt after verifying timestamps)
Describe which portions predated Aug 26, 2026. During the contest window, CARLi added real Nemotron integration on Nebius, persistent event/proposal/receipt audit, strict owner approval, emotional memory UI, unique pet identities, cross-pet HTTP isolation, and pet-scoped live inference tests. Verify timestamps with actual Git commits. Do not claim pre-contest components are new.
