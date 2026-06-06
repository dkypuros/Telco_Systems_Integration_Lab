# Vendor and external implementation profiles

This directory stores public-safe metadata for external telco implementations.
It must not contain full upstream source trees.

Use [`TEMPLATE.md`](TEMPLATE.md) for new profiles. A profile records the upstream
identity, license, pinned version, runtime expectations, adapter boundary,
standards areas touched, current evidence label, known gaps, and next validation
step.

Profiles support ADR 0001: external systems are implementation profiles and
interoperability targets, not this repository's source of truth.
