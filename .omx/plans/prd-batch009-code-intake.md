# PRD: Batch 009 Remaining Mock Core/RIC/O-RAN Code Intake

## Objective
Copy the next curated source-code slice after batch 008: remaining mock core functions and O-RAN/RIC support modules.

## Requirements
1. Discover candidate files under the canonical legacy standalone 5G emulator source root.
2. Exclude duplicates, virtualenvs, caches, generated files, and whole directories.
3. Append rows as planned before copying.
4. Copy only listed files with `shutil.copy2`.
5. Record source and destination SHA-256 checksums.
6. Run `ast.parse` on every copied Python file.
7. Record code-intake caveats: not runtime-integrated and not conformance proof.
8. Run architect verification before completion.

## Non-goals
- No runtime launch.
- No dependency install.
- No import-path refactor.
- No formal conformance claim.
