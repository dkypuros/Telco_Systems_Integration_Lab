# Copy Exclusion Policy

Default intake from source workspaces is copy-only and curated. Exclude these source-workspace artifacts unless explicitly approved and recorded in `copy_manifest.csv`:

Note: target-local `.omx/` files may be created by OMX workflow tracking. That does not permit copying `.omx/` or `.omc/` directories from source workspaces.

- `.git/`
- `.omc/`, `.omx/`
- `node_modules/`
- `venv/`, `.venv/`, `test_venv/`
- `__pycache__/`, `.pytest_cache/`
- `.next/`
- PID files and service process files
- raw runtime logs unless curated into `build_logs/`
- SQLite/db files unless explicitly retained as evidence
- generated build outputs
- `.DS_Store`
- raw standards bundles under `specs/`, including PDFs, DOC/DOCX, ZIPs, local
  generated/auxiliary spec files, and `Codex.dmg`; commit derived inventories,
  matrices, or evidence summaries instead

Operational evidence rule: curated run evidence goes in `build_logs/`; traceability entries point to it. Raw logs stay out unless intentionally curated.
