# Tech-Co 5G Lab Simulator: Strategic Roadmap

Drawn from the Wave 5 architect review. This document covers current state, the three
highest-leverage next moves, Red Hat lens extensions, lower-priority technical work, known
technical debt, and a customer conversation guide.

---

## Current State (post-Wave 5)

The simulator is a fully functional multi-service 5G lab environment running on a single
host via Docker Compose. All major network domains are represented.

### What is working

| Domain | Components | Status |
|--------|------------|--------|
| OSS/BSS | Order Engine (TMF622/641), Catalog API (TMF620), Storefront | Complete |
| 5G Core | NRF, AMF, SMF, UDM, UDR, NSSF | Complete |
| IMS | P-CSCF, I-CSCF, S-CSCF, MRF, IMS-HSS | Complete |
| 4G EPC | MME, SGW, PGW, HSS | Complete |
| RAN | gNB, CU, DU, Near-RT RIC, Non-RT RIC | Complete |
| AI Layer | Observer (Phase 1 observe + Phase 2 propose/execute) | Phase 2 complete |
| O2IMS | Stub + real adapter bridge | Complete |
| Provisioning | Saga pattern with rollback, legacy standalone 5G emulator and O2IMS adapters | Complete |

### Architecture patterns in place

- TMF622 product orders decompose to TMF641 service orders via the decomposer.
- Saga runner handles multi-step provisioning with compensating rollbacks.
- Adapter registry (legacy_5g_emulator_python, o2ims, o2ims_real) routes steps by rules.yaml or
  service characteristics.
- AI Observer collects cross-NF observations, generates proposals, and can execute
  autonomously when `AI_AUTO_EXECUTE=true`.
- Full 3GPP service-based interface naming (Nudm, Nsmf, Nnrf-nfm, Nnrf-disc, Nnssf).
- O-RAN A1 policy push (Non-RT RIC to Near-RT RIC) and E2 control loop (Near-RT RIC
  to gNB/CU/DU).
- OpenTelemetry tracing and Prometheus metrics on all NFs.

### Known gaps entering this roadmap

- No end-to-end demo script that captures and narrates a complete flow for an audience.
- AI Observer can propose and execute actions but cannot yet close a real feedback loop
  against the 5G core (Phase 3 gap).
- All services run on bare Docker Compose. No Kubernetes or OpenShift manifests exist.
- ODA Canvas alignment has not been started.
- Auth (JWT/RBAC) is absent from the AI Observer action API.

---

## Move 1: Demo Packaging (Highest Leverage)

### Why this is the top priority

The simulator has breadth that no customer can see in a static README. A scripted,
reproducible demo that walks through a complete order-to-activation flow, with AI
observation and auto-remediation, converts the lab from a dev tool into a field asset.
Without this, the other two moves have no delivery vehicle.

### What to build

**Guided demo script** (`scripts/demo_e2e.sh` or equivalent):

1. Seed catalog: POST a 5G eMBB slice offering and a VoNR offering to the Catalog API.
2. Place a product order via the Order Engine and poll until `completed`.
3. Show the service order decomposition (GET serviceOrders).
4. Show execution step results (GET /productOrder/{id} with expanded steps).
5. Inject a simulated fault (call an observer endpoint or manually POST an anomaly).
6. Show the AI Observer detect it, propose an action, and (with auto-execute on) execute it.
7. Show the final state restored to `completed`.

**Narrated companion** (`docs/demo_walkthrough.md`):

- What each step represents in a real telco network.
- What a Red Hat customer would replace each stub with (AAP, RHOAI, ACM).
- Expected output at each step.

**Reset script** (`scripts/demo_reset.sh`):

- Wipe the SQLite DBs and in-memory state.
- Re-seed the catalog from `data/seed_catalog.json`.
- Confirm all NFs healthy before the demo starts.

### Success criteria

- Any engineer can run the demo from a cold start in under 5 minutes.
- The full flow (order through AI remediation) completes without manual intervention.
- The demo video can be recorded against this script and replayed for customers.

---

## Move 2: AI Active Control (Phase 3)

### Why this is second

Phase 2 proved the observe-propose-execute loop works in isolation. Phase 3 closes the
loop against the actual 5G core, making the AI Observer a genuine closed-loop controller
rather than a side-car. This is the technical differentiator that separates this simulator
from any off-the-shelf demo.

### What Phase 3 adds

**Real actuator integration:**

The AI Observer's `ActionEngine` currently calls a registered actuator stub. Replace the
stub with actuators that call real NF endpoints:

| Action type | Target NF | Endpoint |
|-------------|-----------|----------|
| Slice throttle | SMF | PATCH /nsmf-pdusession/v1/sm-contexts/{id} |
| UE handover trigger | AMF | POST /amf/handover |
| A1 policy push | Non-RT RIC | PUT /a1-p/policytypes/{id}/policies/{policy_id} |
| xApp control | Near-RT RIC | POST /e2/control |
| Order rollback | Order Engine | PATCH /productOrder/{id} + saga compensate |

**Confidence-gated execution:**

The engine already has a threshold concept. Wire it to per-action-type thresholds stored
in a config file (`config/ai_thresholds.yaml`) so operators can tune aggressiveness per
action class without code changes.

**Feedback loop closure:**

After executing an action, the Observer must re-observe the affected NFs and confirm the
metric returned to acceptable range. Add a `verify` phase to the action execution flow
with configurable timeout.

**Auth on the action API:**

Before Phase 3 goes into any customer demo, add at minimum an API key header check on
`POST /actions/{id}/approve` and `PATCH /auto-execute`. Full JWT/RBAC is follow-on.

### Success criteria

- AI Observer detects a synthetic SMF session anomaly and issues an A1 policy without
  human intervention.
- The feedback loop confirms the anomaly resolved and marks the action `verified`.
- Auto-execute can be toggled at runtime without restart.

---

## Move 3: Containerize on OpenShift via ODA Canvas

### Why this is third

Moves 1 and 2 prove the technology. Move 3 proves it runs on the platform Red Hat sells.
ODA Canvas alignment positions this simulator as a reference implementation for telco
operators evaluating OpenShift for their OSS/BSS and network automation stacks.

### Kubernetes manifests

Create `deploy/k8s/` with one Deployment, Service, and ConfigMap per component.
Group by domain (oss-bss, core-5g, ims, epc, ran, ai-observer).

Priority order for initial manifests:

1. Order Engine + Catalog API (the BSS/OSS layer most customers start with)
2. NRF + AMF + SMF (minimal 5G core for a PDU session)
3. AI Observer
4. Full core, IMS, EPC, RAN

### OpenShift-specific additions

- `deploy/openshift/` with Route objects replacing Ingress.
- Resource requests and limits tuned for a shared lab cluster (not a performance cluster).
- A Namespace manifest with appropriate RBAC for the lab service accounts.
- Liveness and readiness probes wired to the `/health` endpoints already present on all NFs.

### ODA Canvas alignment

TM Forum ODA Canvas expects components to be packaged as Helm charts with standardized
metadata (component type, exposed APIs, consumed APIs).

Steps:

1. Create a Helm chart per logical component group (oss-bss, 5g-core, ai-observer, ran).
2. Add `canvas-component.yaml` metadata to each chart following the ODA Component
   Specification.
3. Declare exposed APIs (TMF620, TMF622, TMF641) and consumed APIs (NRF discovery,
   SMF session) in the canvas metadata.
4. Register with the Canvas operator (if available in the target cluster) to get
   automated API gateway and service mesh integration.

### OpenShift operator hooks

- Use Ansible Automation Platform (AAP) to drive Day 2 operations (scale, update, reset).
- Use Red Hat Advanced Cluster Management (ACM) for multi-cluster placement if the demo
  expands to simulate a distributed operator scenario.
- Use Red Hat OpenShift AI (RHOAI) to replace the current rule-based anomaly detection in
  the AI Observer with a trained inference model served via RHOAI Model Serving.

### Success criteria

- `helm install tech-co-oss-bss deploy/helm/oss-bss/` produces a running Order Engine
  and Catalog API on an OpenShift cluster.
- The full demo from Move 1 runs end-to-end on OpenShift with no Docker Compose dependency.
- At least one component chart passes ODA Canvas metadata validation.

---

## Red Hat Lens Extensions

These additions layer Red Hat product specifics onto the three moves without changing
the simulator's core architecture.

### Ansible Automation Platform (AAP)

- Wrap the demo reset script as an Ansible playbook.
- Wrap the saga compensating actions as AAP job templates so remediation actions appear
  in the AAP activity stream.
- This makes the AI Observer's actuator calls auditable through AAP, which is exactly
  what a telco network operations center expects.

### Red Hat OpenShift AI (RHOAI)

- The AI Observer currently uses threshold-based anomaly detection. Replace the detection
  stage with an RHOAI-served inference endpoint (e.g., an isolation forest or LSTM model
  trained on synthetic NF metric traces).
- The rest of the proposal-execute pipeline stays unchanged. Only the observation scoring
  function changes.
- This demonstrates RHOAI as the inference backbone for closed-loop network automation,
  which is the primary use case in the Red Hat telco AI story.

### Keycloak (Red Hat SSO)

- Add Keycloak as the identity provider for the AI Observer action API (addresses the
  Phase 3 auth gap).
- NRF OAuth2 token issuance can optionally delegate to Keycloak for a fully standards-
  aligned token flow.

### AMQ Streams (Kafka)

- Replace the in-memory observation queue in the AI Observer with a Kafka topic.
- This makes the observer horizontally scalable and allows external systems (e.g., a
  separate analytics pipeline) to consume the same observation stream.
- Aligns with the streaming telemetry pattern Red Hat sells for telco data platforms.

---

## Lower-Priority Technical Work

These items improve correctness and completeness but are not blockers for customer demos.

### Protocol fidelity

- Replace HTTP-over-SCTP simulation in AMF and gNB with actual SCTP using the existing
  `PROTOCOL_MODE=real` path. Currently the real mode is wired but not exercised in CI.
- Add PFCP message encoding/decoding in the SMF-UPF N4 interface (currently stub payloads).
- Wire the Diameter Cx commands (UAR, LIR, MAR, SAR) through a proper Diameter stack
  instead of the HTTP mapping. This is a large effort and only needed for Diameter
  interop testing.

### Data persistence

- UDR uses SQLite. The Order Engine uses async SQLAlchemy with SQLite. For multi-instance
  or OpenShift deployments, replace SQLite with PostgreSQL (available as a Red Hat
  supported operator on OpenShift).
- Add database migration support (Alembic is already a common pattern with SQLAlchemy).

### Test coverage

- End-to-end integration tests that exercise the full TMF622 to 5G core path (order
  placed, NFs provisioned, state verified).
- Contract tests for each TMF API against the TM Forum CTK schemas.
- Chaos tests: kill a single NF mid-saga and verify rollback completes correctly.

### Observability

- Unified Grafana dashboard wiring all Prometheus `/metrics` endpoints into a single
  pane of glass for the demo.
- Distributed trace correlation: wire the OpenTelemetry trace IDs through from the
  Order Engine into the 5G core NFs so a single product order is traceable end-to-end.

---

## Known Technical Debt

| Item | Location | Impact | Remediation |
|------|----------|--------|-------------|
| No auth on AI Observer action API | `src/ai_observer/app/api/actions.py` | Demo only, not production-safe | Add API key or JWT before any customer exposure |
| In-memory state in all NFs (except UDR/Order Engine) | All NFs in `core_network/`, `ran/` | State lost on container restart | Accept for lab; add persistence before OpenShift deploy |
| SQLite in UDR and Order Engine | `core_network/udr.py`, `src/order_engine/` | Not horizontally scalable | Replace with PostgreSQL for OpenShift path |
| rules.yaml adapter routing is static | `src/order_engine/app/decomposition/` | Cannot react to catalog changes at runtime | Load rules from catalog metadata |
| Direct creation of TMF641 service orders returns 501 | `src/order_engine/app/api/tmf641.py` | Limits external integration | Implement if external SO orchestrators are needed |
| AI_AUTO_EXECUTE toggles globally, no per-action-type control | `src/ai_observer/app/control/action_engine.py` | Coarse-grained, risky in demos | Move to per-action-type threshold config (Phase 3) |
| No network policies between containers | `docker-compose.yml` | All NFs can reach all others | Add explicit allowed-paths for OpenShift deploy |

---

## Customer Conversation Guide

Use this section to anchor technical conversations to the customer's language and priorities.

### For a telco OSS/BSS modernization conversation

Lead with: the Order Engine implements TM Forum TMF622 and TMF641 over a saga pattern
with compensating rollbacks. That is what production order orchestration looks like when
you decompose product orders into service orders. The Catalog API (TMF620) feeds both
the Storefront and the decomposer rules.

Red Hat angle: OpenShift as the runtime for the BSS/OSS layer, AAP for Day 2 operations,
and Keycloak for API security. The ODA Canvas Helm charts (Move 3) make this directly
portable to a customer's OpenShift cluster.

### For a 5G core automation conversation

Lead with: all six 5G core NFs implement their 3GPP service-based interface paths. The
NRF does OAuth2 token issuance. The AMF runs NGAP procedures. The SMF creates PDU session
contexts via Nsmf. Show the full UE attach flow from the demo script.

Red Hat angle: these NFs would run as containerized network functions (CNFs) on OpenShift.
The AI Observer watching them is the closed-loop automation story.

### For an AI / closed-loop automation conversation

Lead with: the AI Observer is a three-phase system. Phase 1 observes. Phase 2 proposes
and executes with human approval or auto-execute. Phase 3 closes the feedback loop with
verified remediation. The confidence threshold gate means the system does not act unless
it is confident. Show the PATCH /auto-execute endpoint and the proposal approval flow.

Red Hat angle: replace the rule-based anomaly scorer with an RHOAI inference endpoint.
The rest of the pipeline is identical. That is how Red Hat adds intelligence to a network
automation stack without rearchitecting the control plane.

### For an O-RAN conversation

Lead with: the Near-RT RIC manages E2 subscriptions from the CU and DU, receives
indications, and pushes E2 control messages. The Non-RT RIC manages A1 policies and
enrichment information. Show the A1 policy push from the Non-RT RIC and the E2 indication
flow from the gNB.

Red Hat angle: Near-RT RIC and Non-RT RIC would run as containerized workloads on
OpenShift. Red Hat ACM provides the multi-cluster placement for a distributed RAN
deployment.

### Common objections

**"This is a simulation, not real network software."**

The protocols and interfaces are real (3GPP TS references throughout). The simulator
exercises the same API contracts that production NFs expose. A customer replacing any
single component with a real NF (or a vendor's NF) can do so by pointing at the same
endpoint paths.

**"How do you handle scale?"**

Move 3 addresses this. The current single-host deployment is a lab, not a production
topology. The OpenShift + ODA Canvas path gives the same components a scalable,
multi-cluster runtime.

**"Where does Red Hat's software actually fit?"**

OpenShift runs the containers. AAP automates Day 2. RHOAI runs the inference models in
the AI Observer. ACM manages multi-cluster placement. Keycloak secures the APIs. Every
component in the simulator has a clear Red Hat product mapping.
