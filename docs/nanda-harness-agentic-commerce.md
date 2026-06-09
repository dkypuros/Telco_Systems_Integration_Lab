# NANDA + Harness Agentic Commerce Concept

This document captures an experimental branch concept: the Telco Systems
Integration Lab harness can become a high-level intent, governance, and safety
layer that discovers remote NANDA-style agents/skills, verifies their trust and
commercial metadata, imports a disabled local binding, and asks the human
operator before any newly discovered skill is enabled.

## Current evidence boundary

This is an experimental architecture note and deterministic local prototype. It
is not a live NANDA integration, not a payment rail, and not a formal standards conformance claim.

The external NANDA material supports the high-level direction but should be read
with roadmap discipline:

- Project NANDA describes foundational infrastructure for the Internet of AI
  Agents, with focus areas around discovery, indexing, cross-platform bridges,
  and AgentFacts-style verified discovery.
- Project NANDA describes agentic commerce, knowledge pricing, edge AI, and
  economic protocols as upcoming roadmap work.
- The NANDA/A2A FAQ frames NANDA Index as the discovery/trust/routing layer and
  A2A as the communication layer once agents are connected; it also describes
  MCP/A2A/HTTPS bridge intent.

Therefore this repo builds a **NANDA-style control-plane contract** first: how
our harness would evaluate and govern a discovered agent before it becomes a
local telco skill.

## Unified vision

```text
Human goal / steering wheel
        |
        v
Telco Harness control plane
(intent, policy, validation, human approval, audit)
        |
        v
NANDA-style discovery and trust layer
(index, AgentFacts-like metadata, protocols, commercial terms)
        |
        v
Remote agentic skill / AI factory / commercial provider
(MCP, A2A, or HTTPS endpoint; usage metering; quality/security evidence)
```

The harness stays above the agentic economy. It does not let a discovered agent
self-install just because it is useful or cheap. It asks:

1. Does this remote skill match the human's intent?
2. Is the issuer allowed?
3. Is identity/attestation metadata present?
4. Is the communication protocol allowed by local policy?
5. Are security, quality, governance, and commercial evidence present?
6. Are price and metering within the human-defined budget?
7. Does the remote skill support audit, revocation, and human approval?
8. Has a human approved enabling the imported binding?

Only then can the skill be used by a telco workflow.

## Commercial layer model

The commercial layer is represented as metadata plus policy, not as a live
payment system:

| Concern | Harness field | Purpose |
|---|---|---|
| Price | `commercial_terms.price_per_invocation` | Lets the harness enforce budget caps before use. |
| Meter | `commercial_terms.metering_unit` | Defines what is counted, such as skill invocation or token route request. |
| Settlement | `commercial_terms.settlement_mode` | Keeps billing integration explicit and swappable. |
| Quality | `quality.score` | Prevents low-quality skills from entering high-risk workflows. |
| Trust | `issuer`, `signature`, `evidence[]` | Lets policy reject untrusted or incomplete records. |
| Governance | `governance.*` | Requires audit, revocation, and human authorization. |

This aligns with a future token-metered or usage-metered agent economy without
claiming that this branch implements settlement.

## Branch prototype

See [`../experimental/nanda_harness_commerce/`](../experimental/nanda_harness_commerce/).

The prototype reads:

- a human intent,
- a NANDA-style index snapshot,
- a local harness import policy,

and emits a skill-import plan. Accepted imports are left disabled and marked
`awaiting_human_approval`.

## Why this fits the lab

The existing lab already treats telecom capabilities as governed skills. This
experiment extends the same pattern across environments:

- local standards-traceable capabilities remain under this repo's claim hygiene;
- remote agents are external profiles, not vendored source trees;
- commercial metadata is evaluated before use;
- validation and human authorization remain in the harness;
- runtime evidence can later be promoted only through the normal evidence gates.

## Next implementation steps

1. Add an adapter contract for a live NANDA Index lookup, kept external-profile
   safe.
2. Add JSON Schema for AgentFacts-like records used by this lab.
3. Add a disabled-by-default module card that displays candidate imports and
   rejection reasons.
4. Add an evidence bundle format for commercial usage and budget decisions.
5. Add an interop test profile that can be skipped unless a live NANDA-compatible
   endpoint is explicitly configured.
