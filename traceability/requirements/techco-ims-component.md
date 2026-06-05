# IMS Component Reference

**Codebase**: BF3-5G-Demo Python IMS stack (~4,200 lines across 5 NFs)
**Base path**: `components/BF3-5G-Demo/open-digital-platform-2_0/5G_Emulator_API/`
**Framework**: FastAPI + uvicorn (all NFs)
**Transport**: HTTP/REST (not real SIP/UDP -- see "Transport model" section below)
**Port config**: `config/ports.py` (IMS range: 9030-9040)
**Spec sidecars**: `core_network/pcscf.py.spec.txt`, `icscf.py.spec.txt`, `scscf.py.spec.txt`,
`mrf.py.spec.txt`, `ims_hss.py.spec.txt`

---

## Transport Model

This IMS stack is an HTTP-mock SIP implementation, not a real SIP stack.

- All NFs bind TCP sockets for HTTP (uvicorn/ASGI). None open a UDP or TCP socket on port 5060.
- SIP messages are represented as JSON-serialized Pydantic models (`SIPRequest`, `SIPResponse`),
  not RFC 3261 text-format datagrams.
- The P-CSCF exposes `POST /sip/register`, `POST /sip/invite`, and `POST /sip/message` as REST
  endpoints. A real SIP UA cannot connect directly.
- Inter-NF forwarding (P-CSCF to I-CSCF, I-CSCF to S-CSCF) uses HTTP calls between NFs, not
  SIP proxy hops.
- The 3GPP procedure logic is faithfully implemented: UAR/UAA, MAR/MAA, SAR/SAA, Service-Route,
  P-Associated-URI, Path headers, and Cx interface flows are all present.
- The Milenage AKA algorithm uses MD5 as a stand-in for AES-128 (f1/f2/f3/f4/f5 functions).
  Auth vectors are structurally correct but not interoperable with a real USIM.

To connect a real SIP UA (sipp, Linphone, etc.), a thin SIP-to-HTTP adapter layer would need to
sit in front of the P-CSCF on port 5060. That adapter does not exist in this codebase.

---

## Startup

Dependency order (each NF given 3 s after launch before next starts):

```
IMS-HSS (9040) -> S-CSCF (9032) -> I-CSCF (9031) -> P-CSCF (9030) -> MRF (9033)
```

All five NFs verified healthy in stage 9 (PIDs 85644-86020, all `GET /health` returned 200).

**PYTHONPATH requirement**: `5G_Emulator_API/` root must be on `PYTHONPATH` so
`from config.ports import get_port` resolves.

---

## Network Functions

### P-CSCF -- Proxy Call Session Control Function

**Purpose**: First IMS contact point for the UE; proxies REGISTER and INVITE, stores contact
bindings (usrloc), performs NAT detection, and creates Rx QoS sessions toward PCRF.

**Source**: `core_network/pcscf.py` (661 lines)
**Port**: 9030
**Spec**: 3GPP TS 24.229 Sections 5.1 and 5.2
**Spec sidecar**: `core_network/pcscf.py.spec.txt`
**Based on**: Kamailio `ims_registrar_pcscf` and `ims_usrloc_pcscf` modules

**Key endpoints** (from stage 12 endpoint audit):

| Method | Path | Returns |
|--------|------|---------|
| POST | `/sip/register` | SIPResponse (200 OK or 401 challenge) |
| POST | `/sip/invite` | SIPResponse (100 Trying or 403) |
| POST | `/sip/message` | SIPResponse (generic; routes ACK, BYE, etc.) |
| GET | `/contacts` | Contact binding list (usrloc state) |
| GET | `/rx-sessions` | Rx QoS session list |
| GET | `/health` | Health status |

**Registration behavior**: On `POST /sip/register` the P-CSCF:
1. Stores the contact binding (`usrloc`): keyed on the angle-bracket AOR
   (e.g., `<sip:alice@ims.local>`).
2. Creates an Rx AAR session for the AOR.
3. Forwards the REGISTER to I-CSCF via HTTP.
4. Returns 200 OK with Service-Route, P-Associated-URI, Path, and Expires headers.

**Known quirk**: Contact AOR key uses angle-bracket form. Lookup for ACK/BYE via
`POST /sip/message` must pass `from_uri` in the same angle-bracket form or the lookup
fails. A standards-compliant UA sends from_uri without angle brackets.

**Status**: Working (stage 9, stage 12 verified). All `/health` 200 OK. Contact bindings
persist across calls.

---

### I-CSCF -- Interrogating Call Session Control Function

**Purpose**: Entry point for terminating registrations and calls; performs UAR and LIR queries
against IMS-HSS to locate the serving S-CSCF; routes REGISTER and INVITE forward.

**Source**: `core_network/icscf.py` (694 lines)
**Port**: 9031
**Spec**: 3GPP TS 24.229 Section 5.3
**Spec sidecar**: `core_network/icscf.py.spec.txt`
**Based on**: Kamailio `ims_icscf` module

**Key endpoints** (stage 12 audit):

| Method | Path | Returns |
|--------|------|---------|
| POST | `/sip/register` | SIPResponse (100 with route to S-CSCF) |
| POST | `/sip/invite` | SIPResponse (100 with route; performs LIR to HSS) |
| POST | `/sip/message` | SIPResponse (generic) |
| GET | `/health` | Health status |

**Routing behavior**: On INVITE, I-CSCF sends a Location-Info-Request (LIR) to IMS-HSS
(`POST /cx/lir`). HSS returns the stored S-CSCF name from the SAR done at registration.
I-CSCF builds a Route header `[<sip:scscf.ims.example.com:6060;lr>]` and forwards.

**Status**: Working (stage 12). LIR-to-HSS-to-LIA chain verified end-to-end.

---

### S-CSCF -- Serving Call Session Control Function

**Purpose**: Session control and registration state for served subscribers; handles originating
and terminating call legs; challenges UEs with AKAv1-MD5; interfaces with IMS-HSS via Cx.

**Source**: `core_network/scscf.py` (1096 lines)
**Port**: 9032
**Spec**: 3GPP TS 24.229 Section 5.4
**Spec sidecar**: `core_network/scscf.py.spec.txt`
**Based on**: Kamailio `ims_registrar_scscf`, `ims_auth`, `ims_isc` modules

**Key endpoints** (stage 12 audit):

| Method | Path | Returns |
|--------|------|---------|
| POST | `/sip/register` | SIPResponse (401 challenge on first attempt, 200 OK after auth) |
| POST | `/sip/invite` | SIPResponse (100 Trying; routes originating and terminating legs) |
| POST | `/sip/message` | SIPResponse (generic) |
| GET | `/users` | List of registered users and contact records |
| GET | `/health` | Health status |

**Two-phase registration flow** (verified stage 12):
1. S-CSCF receives REGISTER (no auth). Sends MAR to IMS-HSS (`POST /cx/mar`). HSS returns
   MAA with real RAND/AUTN/CK/IK derived from AKAv1-MD5. S-CSCF returns 401 + WWW-Authenticate
   with nonce.
2. UE resubmits REGISTER with Authorization. S-CSCF validates response, sends SAR to IMS-HSS
   (`POST /cx/sar`). HSS stores `scscf_name` and returns SAA 2001 (DIAMETER_SUCCESS).
   S-CSCF returns 200 OK + Authentication-Info (nextnonce).

**Status**: Working (stage 9, stage 12). Two-phase AKAv1-MD5 challenge verified for alice and
bob. HSS subscription updated with S-CSCF assignment after each registration.

---

### MRF -- Media Resource Function

**Purpose**: Conference bridge and media resource management; allocates RTP port pairs from a
pool (30000-32000); models codec transcoding and DTMF injection.

**Source**: `core_network/mrf.py` (863 lines)
**Port**: 9033
**Spec**: 3GPP TS 23.228 Sections 4.2.5 and 4.2.6
**Spec sidecar**: `core_network/mrf.py.spec.txt`
**Based on**: FreeSWITCH `mod_conference`

**Key endpoints** (stage 12 audit):

| Method | Path | Returns |
|--------|------|---------|
| POST | `/conferences` | Conference object with ID and state=active |
| POST | `/conferences/{id}/members` | Member joined; RTP port pair allocated |
| DELETE | `/conferences/{id}` | Conference destroyed; RTP ports released to pool |
| GET | `/statistics` | Active conferences, port pool usage, session counts |
| GET | `/health` | Health status |

**RTP port allocation**: Each conference member gets a unique RTP+RTCP port pair from the pool.
Stage 12 verified: alice allocated 127.0.0.1:30000, bob allocated 127.0.0.1:30002. After
`DELETE /conferences/{id}`, ports returned to pool (`rtp_ports_available` returned to 998).

**Media plane note**: MRF allocates port numbers in memory. It does not open UDP sockets,
send RTP packets, or perform actual audio mixing. The media plane is entirely absent.

**Status**: Working (stage 12). Conference lifecycle (create, join two members, destroy)
verified end-to-end.

---

### IMS-HSS -- IMS Home Subscriber Server

**Purpose**: IMS subscriber database; provides Cx interface for UAR/UAA, LIR/LIA, MAR/MAA,
SAR/SAA procedures; stores registered S-CSCF name per subscriber.

**Source**: `core_network/ims_hss.py` (893 lines)
**Port**: 9040
**Spec**: 3GPP TS 29.228, TS 29.229 (Cx/Dx interface)
**Spec sidecar**: `core_network/ims_hss.py.spec.txt`

**Key endpoints** (stage 12 audit):

| Method | Path | Returns |
|--------|------|---------|
| POST | `/cx/uar` | UAA (User-Authorization-Answer, S-CSCF selection) |
| POST | `/cx/lir` | LIA (Location-Info-Answer, serving S-CSCF lookup) |
| POST | `/cx/mar` | MAA (Multimedia-Auth-Answer, AKAv1-MD5 auth vectors) |
| POST | `/cx/sar` | SAA (Server-Assignment-Answer, S-CSCF registration) |
| POST | `/subscriptions` | Provision subscriber (query params: impi, impu, k, op) |
| GET | `/subscriptions` | List all subscribers |
| GET | `/health` | Health status |

**Pre-provisioned subscribers**: user1, user2, user3 (seeded at startup). alice and bob are
provisioned by the test client (`POST /subscriptions?impi=alice@ims.local&impu=...`).

**Query-params note**: `POST /subscriptions` accepts query parameters, not a JSON body
(FastAPI default for non-Pydantic parameters). External tools must use `params=` not `json=`.

**Status**: Working (stage 9, stage 12). 5 subscriptions confirmed after VoNR call test
(3 pre-provisioned + alice + bob).

---

## VoNR Call Flow

Full signaling chain verified in stage 12. Test driver:
`src/ims_test_client/test_vonr_call.py`
Demo wrapper: `scripts/demo_vonr_call.sh`

### Prerequisites

All 5 IMS NFs running and healthy. Core 5G NFs do not need to be running for IMS-only tests.

### REGISTER Procedure

Two-phase AKAv1-MD5 registration for each UE:

```
UE (test client)
  |
  POST /sip/register (no auth) --> P-CSCF (9030)
                                      |
                                   forward --> I-CSCF (9031)
                                                  |
                                               UAR --> IMS-HSS (9040) --> UAA (S-CSCF selected)
                                                  |
                                               forward --> S-CSCF (9032)
                                                              |
                                                           MAR --> IMS-HSS --> MAA (RAND/AUTN/CK/IK)
                                                              |
                                                           <-- 401 + WWW-Authenticate (AKAv1-MD5)
  |
  POST /sip/register (with auth) --> P-CSCF
                                      |
                                   forward --> I-CSCF --> S-CSCF
                                                              |
                                                           SAR --> IMS-HSS --> SAA 2001
                                                              |
                                                           <-- 200 OK + Service-Route + Authentication-Info
  |
  <-- 200 OK (P-Associated-URI, Path, Expires=3600)
```

Stage 12 result for alice: P-CSCF usrloc count=1, S-CSCF users registered=1,
HSS registration_state=registered with scscf_name set.

### INVITE Procedure (alice calls bob)

```
alice UE
  |
  POST /sip/invite + SDP --> P-CSCF (9030)
                               |
                             Rx QoS session created (media QCI=1, 64 kbps UL/DL)
                               |
                             POST /sip/invite --> S-CSCF (9032) [originating]
                                                    |
                                                  iFC checked (no match for ims.local)
                                                    |
                                                  POST /sip/invite --> I-CSCF (9031) [terminating query]
                                                                         |
                                                                       LIR --> IMS-HSS --> LIA (bob's S-CSCF)
                                                                         |
                                                                       POST /sip/invite --> S-CSCF (9032) [terminating]
                                                                                             |
                                                                                           bob contact found
                                                                                             |
                                                                                           180 Ringing (simulated)
                                                                                           200 OK (simulated)
```

Call-ID verified round-trip: `0a15359ffe3f4433839f36a9ff3f0dff@127.0.0.1`

### BYE Procedure

```
alice UE
  |
  POST /sip/message (method=BYE) --> P-CSCF (9030)
                                       |
                                     usrloc.lookup_contact(from_uri)
                                       |
                                     <-- 100 Trying (mock acknowledgement)
```

Note: BYE does not trigger Rx session teardown or S-CSCF dialog cleanup in this implementation.

### MRF Conference (executed in parallel to INVITE flow)

```
POST /conferences                        --> MRF (9033)  -> conference ID, state=active
POST /conferences/{id}/members (alice)   --> MRF          -> RTP 127.0.0.1:30000
POST /conferences/{id}/members (bob)     --> MRF          -> RTP 127.0.0.1:30002
GET  /conferences/{id}                   --> MRF          -> state=active, 2 members
DELETE /conferences/{id}                 --> MRF          -> ports released
```

---

## Known Gaps

| Gap | Description | Impact |
|-----|-------------|--------|
| No dedicated BYE endpoint | BYE routed through `/sip/message` generic handler. No BYE-triggered dialog teardown, Rx session cleanup, or S-CSCF session removal. | Call teardown does not release IMS resources. Rx sessions accumulate. |
| No CANCEL endpoint | Cannot abort in-progress INVITE. | Unanswered calls cannot be cancelled. |
| No PRACK / 100rel | RFC 3262 reliable provisional responses not supported. | IMS compliance gap; VoNR precondition signaling requires PRACK. |
| No SDP negotiation | SDP body carried as a string; not parsed. No codec intersection, no SDP answer generated. | No answer SDP produced; codecs not negotiated. |
| No real RTP transport | MRF allocates port numbers in memory only. No UDP sockets opened, no RTP packets sent, no audio mixing. | Media plane is entirely absent. |
| No dialog state machine | Neither P-CSCF nor S-CSCF maintains a dialog (Call-ID + From-tag + To-tag) state machine. Methods arriving mid-dialog are not correlated to the original INVITE. | Parallel calls would be indistinguishable. |
| No preconditions (RFC 3312) | QoS preconditions signaling (SDP `a=des:qos`, `a=curr:qos`) not implemented. | Required for IMS voice calls before ringing. |
| Simplified Milenage | AES-128 replaced with MD5 in f1/f2/f3/f4/f5 functions. RAND/AUTN/XRES/CK/IK generated but non-compliant with 3GPP TS 35.206. | Auth vectors would not interop with a real USIM. |
| No IPSec/TLS on Gm | P-CSCF has `ipsec_enabled=True` in config but no actual IPSec SA setup. | No transport-layer security for UE-P-CSCF hop. |
| AOR key mismatch | P-CSCF stores contacts keyed with angle brackets (`<sip:alice@ims.local>`). A compliant UA sends from_uri without angle brackets. | ACK/BYE from a real UA would fail usrloc lookup. |
| No Rx session teardown | Rx sessions created on REGISTER and INVITE are never deleted. | Sessions accumulate; would exhaust PCRF resources in production. |
| No 180/200 relay | S-CSCF has no mechanism to receive a real response from the callee UE and relay it back. Provisional and final responses are simulated by the test client. | No real response flow from callee to caller. |

---

## Cross-References

- VoNR test client: `src/ims_test_client/test_vonr_call.py`
- VoNR demo script: `scripts/demo_vonr_call.sh`
- 5G core NFs (AMF, SMF, UPF): `docs/components/5g_core.md`
- EPC (4G): `docs/components/epc.md`
- RAN: `docs/components/ran.md`
