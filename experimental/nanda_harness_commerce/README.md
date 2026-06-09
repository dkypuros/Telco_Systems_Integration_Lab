# NANDA + Harness Agentic Commerce Experiment

This experiment turns the branch idea into a deterministic, repo-local prototype:

> A human gives the harness an intent. The harness discovers a NANDA-style remote
> agent/skill, verifies identity, security, quality, governance, and commercial
> terms, then prepares the skill for use only after human authorization.

The prototype is intentionally **offline and deterministic**. It does not call a live NANDA Index, does not pull third-party containers, and does not execute a
remote agent. It models the control-plane contract this lab would require before
allowing a discovered agentic skill into a telco workflow.

## Why this belongs in `experimental/`

Project NANDA documentation describes current work around onboarding, indexing,
discovery, cross-platform bridges, and AgentFacts. It also describes agentic
commerce, knowledge pricing, edge AI, and economic protocols as upcoming roadmap
work. This repo therefore treats the commercial layer as a design target, not a
production claim.

## Control-plane pattern

```text
Human intent / budget / risk tolerance
        |
        v
Harness intent resolver
        |
        v
NANDA-style discovery query
        |
        v
AgentFacts-like metadata candidates
        |
        v
Harness verification gate
  - identity issuer allowlist
  - signature / attestation presence
  - protocol compatibility (MCP/A2A/HTTPS)
  - required security and governance evidence
  - quality threshold
  - commercial terms and budget cap
        |
        v
Skill import package (still disabled)
        |
        v
Human authorization gate
        |
        v
Enabled local harness skill binding
```

The harness remains the steering wheel. Discovery and commerce expand the set of
available skills, but governance decides whether a skill can enter the local
execution boundary.

## Files

| File | Purpose |
|---|---|
| `simulator.py` | Deterministic resolver/verifier/import planner. |
| `fixtures/intent.json` | Example human intent for a telco security audit skill. |
| `fixtures/nanda_index.json` | NANDA-style index response with AgentFacts-like records. |
| `fixtures/harness_policy.json` | Local harness governance, quality, budget, and protocol policy. |
| `fixtures/expected_plan.json` | Golden output for the accepted candidate. |

## Run

```bash
python3 experimental/nanda_harness_commerce/simulator.py \
  --intent experimental/nanda_harness_commerce/fixtures/intent.json \
  --index experimental/nanda_harness_commerce/fixtures/nanda_index.json \
  --policy experimental/nanda_harness_commerce/fixtures/harness_policy.json
```

Expected result: exactly one verified skill import package is produced and left
in `awaiting_human_approval` state.

## Claim boundary

This is a control-plane experiment. It demonstrates a local governance contract
for NANDA-style discovery and commercial skill import. It does **not** prove live
NANDA interoperability, live payment settlement, formal standards conformance,
or safe execution of third-party code.
