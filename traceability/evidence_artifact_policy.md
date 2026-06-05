# Evidence Artifact and Promotion Policy

This policy defines how evidence artifacts move from local readiness records to
candidate standards evidence. It is intentionally conservative: artifacts may
support `candidate`, `reference`, or `readiness` language before they support a
formal conformance claim.

## Artifact classes

| Class | Use | Claim boundary |
|---|---|---|
| `reference_only` | Source docs, copied requirements, standards notes, or raw upstream context. | Cannot prove conformance. |
| `readiness_evidence` | Local smoke, integration, import, runtime, or demo evidence. | Supports lab readiness only. |
| `conformance_candidate` | Evidence that names a standard/API/spec release and implementation path but lacks full review. | Candidate only; no certification wording. |
| `formal_conformance_evidence` | Reviewed executable test result or official CTK/spec evidence tied to a release-register row. | May support formal language only within the recorded scope and gap. |

## Required metadata for promotion

A candidate artifact must record all of the following before it can be promoted:

1. standards body and standard/API/spec ID,
2. release or asset version tested against,
3. implementation path or copied-source artifact path,
4. executable test path or official CTK/spec evidence path,
5. result date and result status,
6. conformance level,
7. known gap to the latest open/active release,
8. next validation step,
9. reviewer or promotion decision owner,
10. sanitization/public-readiness status.

The release/register source of truth remains
[`traceability/standards_release_register.yaml`](standards_release_register.yaml).
The wording gate remains [`traceability/claim_hygiene_policy.md`](claim_hygiene_policy.md).

## Public-readiness and security scan checklist

Run this checklist before publishing, demoing, or using an artifact in external
claim language:

- [ ] No secrets, bearer tokens, API keys, private certificates, cookies, or auth
      headers are present.
- [ ] No local-only absolute paths are required to understand the evidence.
- [ ] Subscriber identifiers, IMSI/SUPI-like values, phone numbers, IP addresses,
      and vendor/customer names are sanitized or intentionally retained with
      documented approval.
- [ ] Raw standards PDFs/DOCX/ZIP bundles are not committed as evidence artifacts.
- [ ] Raw runtime logs are reduced to curated summaries under `build_logs/` or
      `traceability/evidence_snapshots/`.
- [ ] The artifact says `candidate`, `reference`, or `readiness` unless the full
      formal evidence gate is satisfied.
- [ ] Known gaps and unsupported protocol/security behavior are explicit.
- [ ] The final security scan owner has checked `.gitignore` coverage before
      public release.

## `.gitignore` sensitivity recommendations

Keep these categories ignored unless a task explicitly approves a sanitized,
curated artifact:

```gitignore
# Raw standards/spec bundles and large source drops
specs/**/*.pdf
specs/**/*.docx
specs/**/*.zip
specs/**/*.7z
specs/**/*.tar
specs/**/*.tar.gz

# Local runtime secrets and credentials
*.pem
*.key
*.crt
*.p12
*.token
*.secret
secrets/

# Local databases and unsanitized runtime captures
*.db
*.sqlite
*.sqlite3
logs/
*.pcap
*.pcapng
```

Do not rely on `.gitignore` alone for safety. Review `git status --short` and the
actual diff before committing evidence.

## Promotion wording

Allowed before full review:

- `standards-mapped candidate`
- `reference evidence`
- `runtime/demo readiness evidence`
- `formal conformance evidence missing`

Avoid unless the gate is complete:

- `certified`
- `compliant`
- `conformant`
- `release-complete`
- `production-ready`
