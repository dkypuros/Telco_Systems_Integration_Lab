# Conformance Boundary

This lab is standards-traceable, not automatically standards-conformant. The distinction
is intentional.

## What is currently proven

The current repository can support these bounded claims when the referenced evidence is
present and current:

- copied files are tracked by manifest/checksum records,
- copied Python source parses cleanly when recorded in batch evidence,
- wrapper-driven runtime smoke checks can prove local import/readiness conditions,
- the `lab` command can provide repeatable local demo/readiness evidence,
- standards releases, local tested-against baselines, known gaps, and next steps are
  tracked in the release register.

## What is not proven by those facts

The following are not established by copied code, folder names, mock endpoints, or smoke
logs alone:

- formal 3GPP conformance,
- formal O-RAN conformance,
- formal TM Forum API conformance,
- production readiness,
- complete protocol-stack implementation,
- release-complete implementation for any standards body.

## Required evidence before stronger claims

Before making a formal standards claim, record:

1. official standard/API/spec release or asset version,
2. implementation path,
3. executable conformance test path or official CTK/spec evidence,
4. test run date and result,
5. conformance level,
6. known gap to latest,
7. next step.

The authoritative policy is [`traceability/claim_hygiene_policy.md`](../traceability/claim_hygiene_policy.md).

## Safe wording

Use language like:

> The lab includes standards-traceable evidence and runnable mock services for local
> integration/readiness work. Formal conformance remains gated by release-specific
> executable evidence.

For the copied transport helpers, use language like:

> The copied mock 5G core includes standards-inspired transport helpers for minimal GTP-U
> G-PDU header handling over UDP/2152, minimal PFCP header/message-type handling over
> UDP/8805, JSON-modeled NGAP-like messages over length-prefixed TCP on port 38412, and
> best-effort Linux TUN integration.

## Wording to avoid without proof

Avoid claiming complete compliance, production-grade conformance, or release-complete
coverage unless the release register and executable evidence support it. In particular,
do not copy older demo language that asserts complete standards compliance without
current release-specific proof.
