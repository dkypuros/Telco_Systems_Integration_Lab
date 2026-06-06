# External implementation profile template

Use this template for third-party/open-source/vendor telco systems. Profiles are
metadata and runbook boundaries only; they are not vendored source trees.

## Identity

- Profile name:
- Upstream project/vendor:
- Upstream URL:
- Tag, commit, release, or image digest:
- License:
- Profile owner:
- Last reviewed:

## Intended lab role

- Capability slices supported:
- Standards families touched:
- Runtime role: `external implementation profile` / `interoperability target`
- Current standards-evidence label:
- Target standards-evidence label:

## Source-intake boundary

- Full upstream source copied into this repository: **no**
- Excluded artifacts: raw standards bundles, nested `.git`, generated binaries,
  secrets/certs/keys, local runtime logs, databases, package caches
- Any small copied/derived artifact must be listed in
  `traceability/source_inventory.csv` and `traceability/copy_manifest.csv`.

## Runtime expectations

- How the runtime is obtained:
- Required services/images:
- Required ports:
- Required environment variables or secrets:
- Public-safe placeholder names for local paths:

## Adapter contract

- Lab-owned adapter path:
- Inputs accepted by the adapter:
- Outputs/evidence returned by the adapter:
- Failure/skip behavior when the external runtime is unavailable:

## Evidence boundary

- Interoperability test path:
- Evidence snapshot path:
- Known gap to latest/formal conformance:
- Next validation step:
