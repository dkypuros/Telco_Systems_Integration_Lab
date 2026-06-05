# Testing

The lab separates ordinary software tests, runtime smoke checks, regression evidence,
interoperability work, and formal conformance evidence.

## Test buckets

| Bucket | Purpose | Can support formal conformance claims? |
|---|---|---|
| [`tests/unit/`](../tests/unit/) | Local behavior and helper/unit checks. | No, unless tied to a formal test plan and release row. |
| [`tests/integration/`](../tests/integration/) | Multi-file or command integration checks. | Usually no; useful for readiness. |
| [`tests/regression/`](../tests/regression/) | Copy identity and behavior regression checks. | No; protects preservation/readiness. |
| [`tests/interoperability/`](../tests/interoperability/) | Future cross-component/vendor compatibility checks. | Possible only with explicit standard/vendor criteria. |
| [`tests/conformance/`](../tests/conformance/) | Formal conformance test location. | Yes, if tied to official release/CTK/spec evidence. |
| [`build_logs/`](../build_logs/) | Curated runtime/test evidence. | Runtime evidence only unless explicitly promoted. |

## Current repeatable commands

```bash
./lab smoke
./lab test
./lab status
```

The top-level [README](../README.md) and [Quickstart](../QUICKSTART.md) describe the
operator flow.

## Current evidence references

- [`traceability/evidence_stage15_code_testing_summary.md`](../traceability/evidence_stage15_code_testing_summary.md)
- [`traceability/evidence_stage16_lab_operator_loop_summary.md`](../traceability/evidence_stage16_lab_operator_loop_summary.md)
- [`build_logs/stage15_test_report.json`](../build_logs/stage15_test_report.json)
- [`build_logs/stage14_runtime_smoke.json`](../build_logs/stage14_runtime_smoke.json)
- [`build_logs/stage14_runtime_smoke_with_deps.json`](../build_logs/stage14_runtime_smoke_with_deps.json)

## Promotion rule

A test result can be promoted toward a standards claim only when it links to:

1. a standards-release register row,
2. an implementation path,
3. an executable test or official CTK/spec evidence path,
4. a conformance level,
5. a known gap and next step.

See [Conformance Boundary](conformance-boundary.md) for the claim gate.
