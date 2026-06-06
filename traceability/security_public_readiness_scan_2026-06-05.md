# Public-readiness security scan — 2026-06-05

Scope: current tracked tree for `Telco_Systems_Integration_Lab`, plus a high-signal secret scan across existing Git history.

## Result

Current tracked tree is publishable from a sensitive-data perspective after this cleanup pass and the follow-up security check:

- No high-signal credential patterns found in tracked files.
- No high-signal credential patterns found in existing Git history.
- No tracked raw 3GPP/O-RAN/TM Forum/ETSI standards bundles, ZIPs, PDFs, DOCX files, JARs, nested `.git` directories, or `Codex.dmg` found.
- No tracked sensitive filenames such as `.env`, private keys, kubeconfigs, npm/pypi credentials, or PEM/P12/PFX material found.
- No current-tree private absolute path markers found after redaction.
- No private absolute path markers remain in rewritten Git history.
- `.gitignore` now blocks local secrets, runtime state, generated logs, raw standards bundles, local integration staging, and common key/cert material.

## Commands run

```bash
git diff --check
python3 -m compileall -q scripts adapters services tests lab
./lab test
python3 scripts/validate_oran_spec_map.py --format markdown --output traceability/oran_spec_map_validation.md
python3 scripts/validate_oran_spec_map.py --strict  # expected exit 1 while known gaps remain
git grep -n -I -E '<high-signal secret patterns>' -- .
git grep -n -I -E '<private/local runtime path patterns>' -- .
git ls-files | grep -Ei '<sensitive filename patterns>'
git ls-files | grep -Ei '^specs/(3gpp|oran|tmforum|ETSI|etsi)/.*\.(pdf|docx?|xlsx?|zip|jar|dmg)$|Codex\.dmg|(^|/)\.git(/|$)'
git grep -n -I -E '<high-signal secret patterns>' $(git rev-list --all) -- .
git grep -n -I -E '<private-home-path patterns>' $(git rev-list --all) -- .
python -m pip_audit -r config/requirements.txt
git ls-files -o --exclude-standard
git check-ignore -v --stdin --no-index
```

## Verification evidence

- Test suite: `24 passed` via `./lab test`.
- Markdown link check: tracked Markdown links resolved.
- O-RAN validator: report regenerates; strict mode exits `1` because it intentionally surfaces 33 missing implementation paths and 1 missing local spec filename stem.
- Ignore checks: `.env`, `.env.*`, private keys/certs, kubeconfig, `.lab/state/`, `build_logs/**`, `logs/**`, `.omx` runtime dirs, and raw standards bundle paths are ignored.
- Follow-up secret checks: no high-signal credentials in the current tracked tree or in existing Git history.
- Follow-up history rewrite: private absolute path markers were redacted from all reachable commits before public release.
- Follow-up dependency audit: `pip-audit -r config/requirements.txt` reported `No known vulnerabilities found`.
- Follow-up static security scan: `bandit -r scripts adapters services lab` reported 0 high-severity issues; remaining findings are simulator hardening items such as wildcard binds/CORS, missing HTTP timeouts, and local CLI subprocess patterns.
- Follow-up untracked check: `git ls-files -o --exclude-standard` returned no visible untracked files after adding the local ETSI standards cache and `0_to_integrate/` staging ignores.
- Final backup cleanup: the local pre-redaction history backup bundle was deleted before public sharing.

## Remediations applied

- Removed tracked local runtime state under `.lab/state/`.
- Removed tracked OMX runtime context/log/state/ultragoal artifacts while preserving repo planning files under `.omx/plans/`.
- Removed newly generated empty runtime logs under `logs/`.
- Redacted private absolute paths in tracked run evidence and traceability artifacts to placeholders such as `<LAB_ROOT>` and `<SOURCE_5G_LAB_SIMULATOR_ROOT>`.
- Replaced the NRF reusable development JWT default with an ephemeral generated key unless `NRF_JWT_SECRET` is explicitly set.
- Updated copy-manifest checksums for redacted artifacts.
- Added local-only ignores for `specs/ETSI/**`, `specs/etsi/**`, and `/0_to_integrate/` so raw ETSI standards, nested downloaded repositories, JARs, and integration staging assets do not enter public history accidentally.
- Rewrote repository history to replace private local home paths with a neutral placeholder, then verified no private home path markers remain in reachable commits.

## Remaining risks before making the repository public

1. **Mock services still use permissive CORS and wildcard binds in several FastAPI apps.** This is acceptable for a local simulator, but not for production deployment without origin restrictions and bind-host hardening.
2. **Several internal HTTP calls lack explicit timeouts.** Bandit reports these as medium-severity availability hardening issues; they are not sensitive-data blockers for public release.
3. **Dependency vulnerability audit covers tracked Python requirements only.** `pip-audit` found no known vulnerabilities for `config/requirements.txt` and `npm audit` was skipped because there are no tracked npm manifests; ignored external standards/tool caches were not audited.
4. **GitHub security alert APIs are not active while private.** Dependabot alerts and secret scanning APIs reported disabled/unavailable; enable them after changing repository visibility or through repository security settings if desired.
