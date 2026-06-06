# Evidence Batch 006 Claim Caveats

Date: 2026-06-05  
Batch: `evidence-batch-006`  
Recorded at: `2026-06-05T02:02:20Z`

## Purpose

Batch 006 preserves copied API/reference/component documentation exactly as copied from the source workspace. Some artifacts contain source-authored compliance, conformance, pass-rate, or completeness language.

Those phrases are preserved as **source evidence**, not accepted as current lab conclusions.

## Claim-heavy examples

- `traceability/requirements/techco-operations.md` line 18: | Node.js | 18+ | Storefront (optional), Newman CTK conformance |
- `traceability/requirements/techco-operations.md` line 456: | `Order ends in state=partial` | legacy standalone 5G emulator NF not fully healthy, typically UDR not ready | Run `bash scripts/status.sh`. Check `build_logs/run/legacy_5g_emulator_nfs.log`. The integration sweep's `wai
- `traceability/requirements/techco-ims-component.md` line 24: - The 3GPP procedure logic is faithfully implemented: UAR/UAA, MAR/MAA, SAR/SAA, Service-Route,
- `traceability/requirements/techco-ims-component.md` line 82: fails. A standards-compliant UA sends from_uri without angle brackets.
- `traceability/requirements/techco-ims-component.md` line 319: | No PRACK / 100rel | RFC 3262 reliable provisional responses not supported. | IMS compliance gap; VoNR precondition signaling requires PRACK. |
- `traceability/requirements/techco-ims-component.md` line 324: | Simplified Milenage | AES-128 replaced with MD5 in f1/f2/f3/f4/f5 functions. RAND/AUTN/XRES/CK/IK generated but non-compliant with 3GPP TS 35.206. | Auth vectors would not intero
- `traceability/requirements/techco-ims-component.md` line 326: | AOR key mismatch | P-CSCF stores contacts keyed with angle brackets (`<sip:alice@ims.local>`). A compliant UA sends from_uri without angle brackets. | ACK/BYE from a real UA woul
- `traceability/requirements/techco-order-engine-component.md` line 15: customer product orders from the storefront (or any TMF622-compliant northbound caller),
- `traceability/requirements/techco-order-engine-component.md` line 245: **TMF622 CTK conformance: 100% (63/63 assertions)** per stage 13.
- `traceability/requirements/legacy_5g_emulator-testing.md` line 1: # 3GPP Compliance Testing Guide
- `traceability/requirements/legacy_5g_emulator-testing.md` line 5: This document provides comprehensive testing procedures for validating 3GPP compliance across all components of the 5G Network Simulator. It includes automated test suites, manual 
- `traceability/requirements/legacy_5g_emulator-testing.md` line 10:                     3GPP Compliance Testing Framework
- `traceability/requirements/legacy_5g_emulator-testing.md` line 14: │  │                    Compliance Test Suite                               │   │
- `traceability/requirements/legacy_5g_emulator-testing.md` line 24: │  │  │   Message    │ │  Compliance  │ │   Timeline   │ │ Performance  │  │   │
- `traceability/requirements/legacy_5g_emulator-testing.md` line 41: ### 1. Protocol Compliance Tests
- `traceability/requirements/legacy_5g_emulator-testing.md` line 45: **File:** `test_3gpp_compliance.py` (Enhanced)
- `traceability/requirements/legacy_5g_emulator-testing.md` line 55: class ProtocolComplianceTests:
- `traceability/requirements/legacy_5g_emulator-testing.md` line 57:     Comprehensive 3GPP protocol compliance testing
- `traceability/requirements/legacy_5g_emulator-testing.md` line 62:         self.compliance_scores = {}
- `traceability/requirements/legacy_5g_emulator-testing.md` line 64:     async def test_n11_interface_compliance(self):

## Caveat rule

Batch-006 artifacts are documentation/reference evidence only. They are not formal TM Forum, 3GPP, IMS/VoNR, RAN/EPC, O-RAN, or RIC conformance proof unless separately tied to official target releases, executable test evidence, checksums, and explicit conformance review.

## Handling instruction

Do not quote these artifacts as formal compliance claims in README, release notes, demos, or future conformance summaries without a new release-specific test/certification review.
