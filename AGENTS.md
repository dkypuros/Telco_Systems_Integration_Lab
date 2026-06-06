# Codex / Agent Security Rules

This repository is intended to be safe to publish. Follow these rules for every automated change, copy batch, evidence update, and public-release review.

## Public-safe content rules

- Do **not** commit private, user-specific absolute paths such as macOS home paths, personal workspace roots, or machine-local source paths. Use placeholders like `<LAB_ROOT>`, `<SOURCE_WORKSPACE>`, `<USER_HOME>`, or `<TMP_ARTIFACT>` in docs, manifests, and evidence.
- Generic non-identifying runtime paths are allowed only when they are part of the lab contract, for example a documented temporary runtime directory. Prefer environment variables for anything machine-specific.
- Do **not** commit secrets or credential-adjacent files: `.env`, `.env.*`, private keys/certs, kubeconfigs, `.npmrc`, `.pypirc`, `.netrc`, API tokens, OAuth tokens, cloud credentials, or bearer tokens.
- Do **not** commit raw standards bundles, downloaded spec archives, vendor downloads, nested cloned repositories, generated binaries, DMGs, PDFs/ZIPs/JARs, or local integration staging trees. Commit derived traceability, inventories, mappings, checksums, and `.gitkeep` placeholders instead.
- Do **not** commit local runtime state: `.lab/state/`, generated logs, `.omx` runtime state, caches, virtual environments, or test caches. Durable planning docs under `.omx/plans/*.md` are the only `.omx` content intended to be tracked.
- Prefer committed `.gitignore` rules over local `.git/info/exclude` for any protection future agents must inherit.

## External implementation profile rules

- Treat third-party/open-source/vendor telco systems as external implementation profiles or interoperability targets, not as source trees to blindly absorb.
- Do **not** copy full upstream projects such as free5GC, Open5GS, OpenAirInterface/OAI, or similar products into this public repository without an accepted ADR that overrides this rule.
- Commit public-safe metadata, vendor profiles, adapter contracts, runbooks, and interoperability tests instead of full upstream trees.
- Do not infer end-to-end telco completeness from any single external profile. IMS/voice, TM Forum OSS/BSS, storefront/e-commerce flows, orchestration, assurance, charging, RAN, O-RAN, and core-network domains must be mapped as separate capabilities with explicit evidence.
- Use [`docs/adr/0001-external-implementation-profiles.md`](docs/adr/0001-external-implementation-profiles.md) as the architectural source of truth for this policy. OMX plans may sequence work, but they do not override the ADR or these rules.

## Required checks before public-facing commits

Run these checks before committing anything that affects docs, traceability, copied source, ignore rules, release evidence, or public-readiness state:

```bash
git status --short --branch
git ls-files -o --exclude-standard
git diff --check
git diff --cached --check
git grep -n -I -E '/(Users|home)/[^[:space:]]+' -- . ':!.git'
git grep -n -I -E 'AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|-----BEGIN (RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----|ghp_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35}|ya29\.[0-9A-Za-z_-]+|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}' -- . ':!.git'
git ls-files | grep -Ei '(^|/)(\.env|.*\.pem|.*\.key|.*id_rsa.*|.*id_dsa.*|.*id_ed25519.*|.*kubeconfig.*|credentials|secrets?|token|private|\.npmrc|\.pypirc|netrc)(\.|$|/)'
git ls-files | grep -Ei '(^specs/(3gpp|oran|tmforum|ETSI|etsi)/.*\.(pdf|docx?|xlsx?|zip|jar|dmg|7z|tar|gz)$)|Codex\.dmg|(^|/)\.git(/|$)'
```

Expected result for the grep commands above is no output unless the match is a documented false positive. A clean grep may exit with status 1 because it found no matches; treat output, not the clean no-match exit code, as the exposure signal. If a check exposes sensitive material, fix the exposure before committing.

## Public-release gate

Before changing repository visibility to public, run the `security-review` skill or an equivalent security pass that includes:

- current-tree and full-history high-signal secret scans;
- current-tree and full-history private path scans;
- current/history sensitive filename scans;
- current/history raw spec, binary, and nested `.git` scans;
- dependency audit for tracked manifests where tooling is available;
- static Python security scan for copied services and scripts where tooling is available;
- verification that local backup bundles containing pre-redaction history do not exist or remain private and outside the repository.

If any sensitive material ever enters history, keep the repository private until the current tree and reachable history are remediated and re-scanned.
