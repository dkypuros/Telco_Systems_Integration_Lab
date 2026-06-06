# Tech-Co 5G Lab Simulator: REST API Reference

All endpoints verified from source. Ports are host-mapped values from docker-compose. Internal
container ports match unless noted.

---

## Table of Contents

1. [Order Engine (port 8080)](#1-order-engine-port-8080)
2. [Catalog API (port 8081)](#2-catalog-api-port-8081)
3. [AI Observer (port 8090)](#3-ai-observer-port-8090)
4. [5G Core Network Functions](#4-5g-core-network-functions)
   - [NRF (port 8000)](#41-nrf-port-8000)
   - [AMF (port 9000)](#42-amf-port-9000)
   - [SMF (port 9001)](#43-smf-port-9001)
   - [UDR (port 9005)](#44-udr-port-9005)
   - [UDM (port 9004)](#45-udm-port-9004)
   - [NSSF (port 9010)](#46-nssf-port-9010)
5. [IMS Network Functions](#5-ims-network-functions)
   - [P-CSCF (port 9030)](#51-p-cscf-port-9030)
   - [I-CSCF (port 9031)](#52-i-cscf-port-9031)
   - [S-CSCF (port 9032)](#53-s-cscf-port-9032)
   - [MRF (port 9033)](#54-mrf-port-9033)
   - [IMS-HSS (port 9040)](#55-ims-hss-port-9040)
6. [EPC Network Functions (4G)](#6-epc-network-functions-4g)
   - [MME (port 9020)](#61-mme-port-9020)
   - [SGW (port 9021)](#62-sgw-port-9021)
   - [PGW (port 9022)](#63-pgw-port-9022)
   - [HSS (port 9023)](#64-hss-port-9023)
7. [RAN Components](#7-ran-components)
   - [gNB (port 38412)](#71-gnb-port-38412)
   - [CU (port 38472)](#72-cu-port-38472)
   - [DU (port 38473)](#73-du-port-38473)
   - [Near-RT RIC (port 8095)](#74-near-rt-ric-port-8095)
   - [Non-RT RIC (port 8096)](#75-non-rt-ric-port-8096)
8. [Storefront API Client](#8-storefront-api-client)

---

## 1. Order Engine (port 8080)

Source: `src/order_engine/`
Base paths: `/tmf-api/productOrderingManagement/v4` (TMF622), `/tmf-api/serviceOrdering/v4` (TMF641)

### 1.1 TMF622 Product Ordering Management

Source: `src/order_engine/app/api/tmf622.py`

#### GET /tmf-api/productOrderingManagement/v4/productOrder

List all product orders.

| Parameter | Type    | Default | Description              |
|-----------|---------|---------|--------------------------|
| offset    | integer | 0       | Pagination offset        |
| limit     | integer | 20      | Max records to return    |

**Response 200**: Array of ProductOrder objects.

```json
[
  {
    "id": "uuid",
    "href": "/tmf-api/productOrderingManagement/v4/productOrder/uuid",
    "state": "acknowledged",
    "orderDate": "2024-01-01T00:00:00Z",
    "productOrderItem": [],
    "serviceOrderIds": []
  }
]
```

```bash
curl http://localhost:8080/tmf-api/productOrderingManagement/v4/productOrder?limit=10
```

---

#### POST /tmf-api/productOrderingManagement/v4/productOrder

Create a new product order. Decomposition into service orders and saga execution run as
background task. Order is returned immediately in `acknowledged` state.

**Request body** (ProductOrderCreate):

```json
{
  "description": "Provision 5G enterprise slice",
  "category": "network-slice",
  "priority": "4",
  "externalId": "ext-001",
  "productOrderItem": [
    {
      "id": "01",
      "action": "add",
      "productOffering": {
        "id": "offering-uuid",
        "name": "5G-Slice-eMBB"
      }
    }
  ]
}
```

**Response 201**: ProductOrder with assigned `id`, `href`, and initial state `acknowledged`.

```bash
curl -X POST http://localhost:8080/tmf-api/productOrderingManagement/v4/productOrder \
  -H "Content-Type: application/json" \
  -d '{"description":"test","productOrderItem":[{"action":"add","productOffering":{"id":"o1"}}]}'
```

---

#### GET /tmf-api/productOrderingManagement/v4/productOrder/{order_id}

Retrieve a single product order by ID.

**Response 200**: ProductOrder object.
**Response 404**: TMFError with code, reason, message.

```bash
curl http://localhost:8080/tmf-api/productOrderingManagement/v4/productOrder/uuid-here
```

---

#### PATCH /tmf-api/productOrderingManagement/v4/productOrder/{order_id}

Partial update. Only these fields are mutable after creation: `description`, `priority`,
`category`, `notificationContact`, `note`.

**Request body**: JSON object with any subset of allowed fields.

**Response 200**: Updated ProductOrder.
**Response 404**: Not found.

```bash
curl -X PATCH http://localhost:8080/tmf-api/productOrderingManagement/v4/productOrder/uuid \
  -H "Content-Type: application/json" \
  -d '{"priority":"1"}'
```

---

#### DELETE /tmf-api/productOrderingManagement/v4/productOrder/{order_id}

Delete a product order record.

**Response 204**: No content.
**Response 404**: Not found.

```bash
curl -X DELETE http://localhost:8080/tmf-api/productOrderingManagement/v4/productOrder/uuid
```

---

### 1.2 TMF641 Service Ordering Management

Source: `src/order_engine/app/api/tmf641.py`

Note: the actual base path in source is `/tmf-api/serviceOrdering/v4` (not
`serviceOrderingManagement`).

#### GET /tmf-api/serviceOrdering/v4/serviceOrder

List all service orders (created by the decomposer from product orders).

| Parameter | Type    | Default | Description           |
|-----------|---------|---------|-----------------------|
| offset    | integer | 0       | Pagination offset     |
| limit     | integer | 20      | Max records           |

**Response 200**: Array of ServiceOrder objects.

```bash
curl http://localhost:8080/tmf-api/serviceOrdering/v4/serviceOrder
```

---

#### POST /tmf-api/serviceOrdering/v4/serviceOrder

Direct service order creation is not implemented. Returns 501 Not Implemented.
Service orders are created internally by the decomposer.

**Response 501**: Not Implemented.

---

#### GET /tmf-api/serviceOrdering/v4/serviceOrder/{order_id}

Retrieve a single service order.

**Response 200**: ServiceOrder object including state and serviceOrderItem list.
**Response 404**: Not found.

```bash
curl http://localhost:8080/tmf-api/serviceOrdering/v4/serviceOrder/uuid-here
```

---

#### DELETE /tmf-api/serviceOrdering/v4/serviceOrder/{order_id}

Delete a service order record.

**Response 204**: No content.
**Response 404**: Not found.

```bash
curl -X DELETE http://localhost:8080/tmf-api/serviceOrdering/v4/serviceOrder/uuid
```

---

## 2. Catalog API (port 8081)

Source: `src/catalog_api/app/api/tmf620.py`
Base path: `/tmf-api/productCatalogManagement/v4`

All list endpoints support: `fields` (comma-separated projection), `offset`, `limit`.
The `fields` parameter always preserves `id` and `href`.

### 2.1 ProductCatalog

#### GET /tmf-api/productCatalogManagement/v4/productCatalog

List all product catalogs.

| Parameter | Type    | Default | Description                        |
|-----------|---------|---------|------------------------------------|
| fields    | string  | null    | Comma-separated field projection   |
| offset    | integer | 0       | Pagination offset                  |
| limit     | integer | 100     | Max 500                            |

**Response 200**: Array of catalog objects.

```bash
curl "http://localhost:8081/tmf-api/productCatalogManagement/v4/productCatalog?limit=5"
```

---

#### GET /tmf-api/productCatalogManagement/v4/productCatalog/{catalog_id}

Retrieve a single catalog.

**Response 200**: Catalog object.
**Response 404**: Not found.

```bash
curl http://localhost:8081/tmf-api/productCatalogManagement/v4/productCatalog/cat-001
```

---

### 2.2 Category

#### GET /tmf-api/productCatalogManagement/v4/category

List all categories.

| Parameter | Type    | Default | Description                        |
|-----------|---------|---------|------------------------------------|
| fields    | string  | null    | Comma-separated field projection   |
| offset    | integer | 0       |                                    |
| limit     | integer | 100     | Max 500                            |

**Response 200**: Array of category objects.

```bash
curl http://localhost:8081/tmf-api/productCatalogManagement/v4/category
```

---

#### GET /tmf-api/productCatalogManagement/v4/category/{category_id}

Retrieve a single category.

**Response 200**: Category object.
**Response 404**: Not found.

```bash
curl http://localhost:8081/tmf-api/productCatalogManagement/v4/category/cat-5g-slice
```

---

### 2.3 ProductOffering

#### GET /tmf-api/productCatalogManagement/v4/productOffering

List product offerings with optional lifecycle status filter.

| Parameter       | Type    | Default | Description                         |
|-----------------|---------|---------|-------------------------------------|
| fields          | string  | null    | Field projection                    |
| lifecycleStatus | string  | null    | Filter by status (e.g., "Active")   |
| offset          | integer | 0       |                                     |
| limit           | integer | 100     | Max 500                             |

**Response 200**: Array of offering objects.

```bash
curl "http://localhost:8081/tmf-api/productCatalogManagement/v4/productOffering?lifecycleStatus=Active"
```

---

#### GET /tmf-api/productCatalogManagement/v4/productOffering/{offering_id}

Retrieve a single offering.

**Response 200**: Offering object.
**Response 404**: Not found.

```bash
curl http://localhost:8081/tmf-api/productCatalogManagement/v4/productOffering/offer-001
```

---

#### POST /tmf-api/productCatalogManagement/v4/productOffering

Create a new product offering.

**Request body**: JSON. If `id` is omitted, a UUID is assigned. `lifecycleStatus` defaults
to "Active". `@type` defaults to "ProductOffering".

```json
{
  "name": "5G-Slice-eMBB",
  "lifecycleStatus": "Active",
  "@type": "ProductOffering",
  "category": [{"id": "cat-5g"}]
}
```

**Response 201**: Created offering with `id`, `href`, `lastUpdate` filled in.

```bash
curl -X POST http://localhost:8081/tmf-api/productCatalogManagement/v4/productOffering \
  -H "Content-Type: application/json" \
  -d '{"name":"5G-Slice-eMBB","lifecycleStatus":"Active"}'
```

---

#### PATCH /tmf-api/productCatalogManagement/v4/productOffering/{offering_id}

Partial update of an offering. `id` and `href` in the patch body are ignored. `lastUpdate`
is always refreshed.

**Response 200**: Updated offering.
**Response 404**: Not found.

```bash
curl -X PATCH http://localhost:8081/tmf-api/productCatalogManagement/v4/productOffering/offer-001 \
  -H "Content-Type: application/json" \
  -d '{"lifecycleStatus":"Retired"}'
```

---

#### DELETE /tmf-api/productCatalogManagement/v4/productOffering/{offering_id}

Delete an offering.

**Response 204**: No content.
**Response 404**: Not found.

```bash
curl -X DELETE http://localhost:8081/tmf-api/productCatalogManagement/v4/productOffering/offer-001
```

---

### 2.4 ProductSpecification

#### GET /tmf-api/productCatalogManagement/v4/productSpecification

List all product specifications.

**Response 200**: Array of specification objects.

```bash
curl http://localhost:8081/tmf-api/productCatalogManagement/v4/productSpecification
```

---

#### GET /tmf-api/productCatalogManagement/v4/productSpecification/{spec_id}

Retrieve a single specification.

**Response 200**: Specification object.
**Response 404**: Not found.

```bash
curl http://localhost:8081/tmf-api/productCatalogManagement/v4/productSpecification/spec-001
```

---

#### POST /tmf-api/productCatalogManagement/v4/productSpecification

Create a new product specification. Same auto-fill rules as productOffering.
`@type` defaults to "ProductSpecification".

**Response 201**: Created specification.

```bash
curl -X POST http://localhost:8081/tmf-api/productCatalogManagement/v4/productSpecification \
  -H "Content-Type: application/json" \
  -d '{"name":"5G-eMBB-Spec","version":"1.0"}'
```

---

### 2.5 ProductOfferingPrice

#### GET /tmf-api/productCatalogManagement/v4/productOfferingPrice

List all prices. Supports `lifecycleStatus` and `priceType` query filters.

| Parameter       | Type   | Description                          |
|-----------------|--------|--------------------------------------|
| lifecycleStatus | string | Filter by status                     |
| priceType       | string | Filter by type (e.g., "recurring")   |
| fields          | string | Field projection                     |

**Response 200**: Array of price objects.

```bash
curl "http://localhost:8081/tmf-api/productCatalogManagement/v4/productOfferingPrice?priceType=recurring"
```

---

#### GET /tmf-api/productCatalogManagement/v4/productOfferingPrice/{price_id}

Retrieve a single price entry.

**Response 200**: Price object.
**Response 404**: Not found.

---

#### POST /tmf-api/productCatalogManagement/v4/productOfferingPrice

Create a new price entry. `@type` defaults to "ProductOfferingPrice".

**Response 201**: Created price.

```bash
curl -X POST http://localhost:8081/tmf-api/productCatalogManagement/v4/productOfferingPrice \
  -H "Content-Type: application/json" \
  -d '{"name":"eMBB-Monthly","priceType":"recurring","price":{"value":500,"unit":"USD"}}'
```

---

#### PATCH /tmf-api/productCatalogManagement/v4/productOfferingPrice/{price_id}

Partial update of a price entry.

**Response 200**: Updated price.
**Response 404**: Not found.

---

#### DELETE /tmf-api/productCatalogManagement/v4/productOfferingPrice/{price_id}

Delete a price entry.

**Response 204**: No content.
**Response 404**: Not found.

---

## 3. AI Observer (port 8090)

Source: `src/ai_observer/`

### 3.1 Root and Health

#### GET /

Returns service info and version.

**Response 200**: JSON with service metadata.

```bash
curl http://localhost:8090/
```

---

#### GET /health

Health check.

**Response 200**: `{"status": "ok"}` (or equivalent).

```bash
curl http://localhost:8090/health
```

---

### 3.2 Observations

Source: `src/ai_observer/app/api/observations.py`

#### GET /observations

List all observations collected by the observer.

| Parameter | Type    | Description                          |
|-----------|---------|--------------------------------------|
| type      | string  | Filter by observation type           |
| limit     | integer | Max observations to return           |

**Response 200**: Array of observation objects.

```bash
curl "http://localhost:8090/observations?limit=50"
```

---

#### GET /observations/{obs_type}

Retrieve observations of a specific type.

**Response 200**: Array of observations filtered by type.

```bash
curl http://localhost:8090/observations/anomaly
```

---

#### GET /alerts

List active alerts generated from observations.

**Response 200**: Array of alert objects.

```bash
curl http://localhost:8090/alerts
```

---

#### GET /summary

Return an aggregated summary of current system observations and alert counts.

**Response 200**: Summary object.

```bash
curl http://localhost:8090/summary
```

---

### 3.3 Actions and Auto-Execute

Source: `src/ai_observer/app/api/actions.py`

No authentication in Phase 2. JWT/RBAC is documented as future work.

#### GET /proposed-actions

Return all pending (and previously pending) action proposals from the ActionEngine.

**Response 200**: Array of proposal objects.

```bash
curl http://localhost:8090/proposed-actions
```

---

#### GET /actions

Return all actions that have been executed by the engine.

**Response 200**: Array of execution record objects.

```bash
curl http://localhost:8090/actions
```

---

#### POST /actions/{proposal_id}/approve

Manually approve a pending proposal. Triggers async execution of the plan via the
registered actuator. Returns 404 if the proposal is not found or not in `pending` state.

**Response 200**: Confirmation with record.

```json
{
  "message": "Proposal 'uuid' approved and queued for execution",
  "record": { ... }
}
```

**Response 404**: Proposal not found or not pending.

```bash
curl -X POST http://localhost:8090/actions/proposal-uuid/approve
```

---

#### GET /auto-execute

Return the current auto-execute setting.

**Response 200**:

```json
{
  "enabled": false,
  "note": "Set AI_AUTO_EXECUTE=true env var or use PATCH /auto-execute to toggle",
  "warning": "No authentication in Phase 2 -- add auth before production use"
}
```

```bash
curl http://localhost:8090/auto-execute
```

---

#### PATCH /auto-execute

Toggle auto-execute mode at runtime. When `enabled: true`, the ActionEngine executes plans
automatically when confidence >= threshold.

**Request body**:

```json
{ "enabled": true }
```

**Response 200**:

```json
{
  "enabled": true,
  "message": "auto-execute set to true",
  "warning": "No authentication in Phase 2 -- add auth before production use"
}
```

```bash
curl -X PATCH http://localhost:8090/auto-execute \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

---

## 4. 5G Core Network Functions

### 4.1 NRF (port 8000)

Source: `core_network/nrf.py`
Reference: 3GPP TS 29.510

Includes full OAuth2 token issuance, NF instance management, NF discovery, and subscriptions.

#### POST /oauth2/token

Issue an OAuth2 access token (client credentials grant). Required by 3GPP NF-to-NF
service authorization.

**Request body** (form-encoded or JSON):

```
grant_type=client_credentials&nfInstanceId=uuid&nfType=AMF&targetNfType=SMF
```

**Response 200**: `{"access_token": "...", "token_type": "Bearer", "expires_in": 3600}`

```bash
curl -X POST http://localhost:8000/oauth2/token \
  -d "grant_type=client_credentials&nfInstanceId=amf-uuid&nfType=AMF&targetNfType=SMF"
```

---

#### PUT /nnrf-nfm/v1/nf-instances/{nfInstanceId}

Register or update an NF instance (NF heartbeat / re-registration).

**Response 201** (new) or **200** (update).

```bash
curl -X PUT http://localhost:8000/nnrf-nfm/v1/nf-instances/amf-uuid \
  -H "Content-Type: application/json" \
  -d '{"nfType":"AMF","nfStatus":"REGISTERED","ipv4Addresses":["10.0.0.1"]}'
```

---

#### GET /nnrf-nfm/v1/nf-instances/{nfInstanceId}

Retrieve a registered NF instance profile.

**Response 200**: NF profile.
**Response 404**: Not found.

```bash
curl http://localhost:8000/nnrf-nfm/v1/nf-instances/amf-uuid
```

---

#### PATCH /nnrf-nfm/v1/nf-instances/{nfInstanceId}

Update selected fields of an NF instance (e.g., heartbeat timestamp, load).

**Response 200**: Updated NF profile.

---

#### DELETE /nnrf-nfm/v1/nf-instances/{nfInstanceId}

Deregister an NF instance.

**Response 204**: No content.

---

#### GET /nnrf-disc/v1/nf-instances

NF discovery: return registered instances matching query criteria.

| Parameter    | Type   | Description              |
|--------------|--------|--------------------------|
| target-nf-type | string | NF type to discover    |
| requester-nf-type | string | Caller NF type      |

**Response 200**: Array of matching NF profiles.

```bash
curl "http://localhost:8000/nnrf-disc/v1/nf-instances?target-nf-type=SMF"
```

---

#### POST /nnrf-nfm/v1/subscriptions

Subscribe to NF instance lifecycle events (REGISTERED, DEREGISTERED, etc.).

**Response 201**: Subscription record with `subscriptionId`.

---

#### GET /health

**Response 200**: `{"status": "healthy"}`

#### GET /metrics

Prometheus-format metrics.

#### POST /register (legacy)

Legacy NF registration (kept for backward compat). Use `PUT /nnrf-nfm/v1/nf-instances/` instead.

#### GET /discover/{nf_type} (legacy)

Legacy NF discovery. Use `GET /nnrf-disc/v1/nf-instances?target-nf-type=` instead.

---

### 4.2 AMF (port 9000)

Source: `core_network/amf.py`
Reference: 3GPP TS 29.518, TS 38.413 (NGAP)

Supports both stub HTTP mode and real NGAP over SCTP/TCP (`PROTOCOL_MODE=real`).

#### NGAP Procedures

| Method | Path                              | Description                        |
|--------|-----------------------------------|------------------------------------|
| POST   | /ngap/ng-setup                    | NG Setup (gNB connects to AMF)     |
| POST   | /ngap/initial-ue-message          | Initial UE Message (attach start)  |
| POST   | /ngap/uplink-nas-transport        | Uplink NAS transport from gNB      |
| POST   | /ngap/ue-context-release          | UE Context Release                 |
| POST   | /ngap/paging                      | Paging request                     |
| POST   | /ngap/error-indication            | Error indication from gNB          |
| POST   | /ngap/downlink-nas-transport      | Downlink NAS to gNB                |

```bash
curl -X POST http://localhost:9000/ngap/ng-setup \
  -H "Content-Type: application/json" \
  -d '{"globalRANNodeID":{"gNB-ID":"001"},"supportedTAList":[{"tac":"001"}]}'
```

---

#### UE Management

| Method | Path                          | Description                         |
|--------|-------------------------------|-------------------------------------|
| GET    | /amf/ue/{ue_id}               | Retrieve UE context                 |
| POST   | /amf/ue/{ue_id}               | Create or update UE context         |
| POST   | /amf/ue/register              | Register a UE (authentication flow) |
| POST   | /amf/ue/{supi}/deregister     | Deregister a UE                     |

---

#### PDU Session and Mobility

| Method | Path                     | Description                   |
|--------|--------------------------|-------------------------------|
| POST   | /amf/pdu-session/create  | Trigger PDU session creation  |
| POST   | /amf/handover            | Initiate handover procedure   |

---

#### Status and Metrics

| Method | Path                     | Description              |
|--------|--------------------------|--------------------------|
| GET    | /health                  | Health check             |
| GET    | /amf/transport-stats     | Transport statistics     |
| GET    | /metrics                 | Prometheus metrics       |

---

### 4.3 SMF (port 9001)

Source: `core_network/smf.py`
Reference: 3GPP TS 29.502

#### POST /nsmf-pdusession/v1/sm-contexts

Create a PDU session SM context (Nsmf_PDUSession_CreateSMContext). Called by AMF during
PDU session establishment.

**Request body**: SMContextCreateData including SUPI, DNN, S-NSSAI, N1 SM message.

**Response 201**: SM context with `smContextRef`.

```bash
curl -X POST http://localhost:9001/nsmf-pdusession/v1/sm-contexts \
  -H "Content-Type: application/json" \
  -d '{"supi":"imsi-001","dnn":"internet","sNssai":{"sst":1}}'
```

---

| Method | Path                        | Description                        |
|--------|-----------------------------|------------------------------------|
| GET    | /smf/sessions               | List active PDU sessions           |
| GET    | /smf_service                | SMF service info                   |
| GET    | /smf/transport-stats        | PFCP and N4 transport stats        |
| GET    | /health                     | Health check                       |

The SMF sends PFCP session establishment to the UPF at `/n4/sessions`.

---

### 4.4 UDR (port 9005)

Source: `core_network/udr.py`
Backend: SQLite (`udr.db`)

#### POST /register_user

Register a subscriber in the UDR.

**Request body**:

```json
{"imsi": "001010000000001", "key": "hex-key", "opc": "hex-opc"}
```

**Response 200** or **201**: Registered user record.

---

#### GET /get_user/{imsi}

Retrieve subscriber data by IMSI.

**Response 200**: Subscriber profile.
**Response 404**: Not found.

```bash
curl http://localhost:9005/get_user/001010000000001
```

---

#### GET /health

Health check.

---

### 4.5 UDM (port 9004)

Source: `core_network/udm.py`
Reference: 3GPP TS 29.503, TS 29.505

Uses Milenage algorithm for authentication vector generation.

#### Nudm_UECM (UE Context Management)

| Method | Path                                                 | Description              |
|--------|------------------------------------------------------|--------------------------|
| POST   | /nudm-uecm/v1/{supi}/registrations/amf-3gpp-access  | AMF registers UE         |
| GET    | /nudm-uecm/v1/{supi}/registrations/amf-3gpp-access  | Get AMF registration     |
| PATCH  | /nudm-uecm/v1/{supi}/registrations/amf-3gpp-access  | Update AMF registration  |
| DELETE | /nudm-uecm/v1/{supi}/registrations/amf-3gpp-access  | Deregister from AMF      |

---

#### Nudm_SDM (Subscription Data Management)

| Method | Path                            | Description                     |
|--------|---------------------------------|---------------------------------|
| GET    | /nudm-sdm/v1/{supi}/am-data     | Access and mobility data        |
| GET    | /nudm-sdm/v1/{supi}/sm-data     | Session management data         |
| GET    | /nudm-sdm/v1/{supi}/nssai       | Subscribed S-NSSAIs             |

```bash
curl http://localhost:9004/nudm-sdm/v1/imsi-001010000000001/am-data
```

---

#### Nudm_UEAU (UE Authentication)

| Method | Path                                                     | Description              |
|--------|----------------------------------------------------------|--------------------------|
| POST   | /nudm-ueau/v1/{supi}/security-information/generate-auth-data | Generate auth vectors |

```bash
curl -X POST http://localhost:9004/nudm-ueau/v1/imsi-001/security-information/generate-auth-data \
  -H "Content-Type: application/json" \
  -d '{"servingNetworkName":"5G:mnc001.mcc001.3gppnetwork.org","ausfInstanceId":"ausf-uuid"}'
```

---

| Method | Path          | Description           |
|--------|---------------|-----------------------|
| GET    | /udm_service  | Legacy service info   |
| GET    | /health       | Health check          |
| GET    | /metrics      | Prometheus metrics    |

---

### 4.6 NSSF (port 9010)

Source: `core_network/nssf.py`
Reference: 3GPP TS 29.531

#### Nnssf_NSSelection

#### GET /nnssf-nsselection/v1/network-slice-information

Select network slice(s) for a UE. Returns allowed NSSAI and NRF for the selected slice.

| Parameter | Type   | Description                  |
|-----------|--------|------------------------------|
| nf-type   | string | Requesting NF type (e.g., AMF) |
| nf-id     | string | Requesting NF instance ID    |
| slice-info-request-for-registration | JSON | Requested NSSAIs |

```bash
curl "http://localhost:9010/nnssf-nsselection/v1/network-slice-information?nf-type=AMF"
```

---

#### Nnssf_NSSAIAvailability

| Method | Path                                                   | Description                        |
|--------|--------------------------------------------------------|------------------------------------|
| PUT    | /nnssf-nssaiavailability/v1/nssai-availability/{nfId} | Publish available NSSAIs for an NF |
| PATCH  | /nnssf-nssaiavailability/v1/nssai-availability/{nfId} | Update NSSAI availability          |
| DELETE | /nnssf-nssaiavailability/v1/nssai-availability/{nfId} | Remove NSSAI availability          |
| POST   | /nnssf-nssaiavailability/v1/nssai-availability/subscriptions | Subscribe to NSSAI events   |
| DELETE | /nnssf-nssaiavailability/v1/nssai-availability/subscriptions/{subscriptionId} | Unsubscribe |

---

| Method | Path                  | Description               |
|--------|-----------------------|---------------------------|
| GET    | /nssf/configuration   | Current NSSF config       |
| GET    | /nssf/slices          | Configured slice list     |
| GET    | /health               | Health check              |
| GET    | /metrics              | Prometheus metrics        |

---

## 5. IMS Network Functions

### 5.1 P-CSCF (port 9030)

Source: `core_network/pcscf.py`
Reference: 3GPP TS 24.229

#### SIP Proxy

| Method | Path          | Description                    |
|--------|---------------|--------------------------------|
| POST   | /sip/register | SIP REGISTER (IMS registration)|
| POST   | /sip/invite   | SIP INVITE (session setup)     |
| POST   | /sip/message  | SIP MESSAGE (instant message)  |

```bash
curl -X POST http://localhost:9030/sip/register \
  -H "Content-Type: application/json" \
  -d '{"from":"sip:user@ims.lab","to":"sip:pcscf.ims.lab","contact":"sip:user@10.0.0.5"}'
```

---

#### Contact Management

| Method | Path                        | Description              |
|--------|-----------------------------|--------------------------|
| GET    | /contacts                   | List registered contacts |
| GET    | /contacts/{contact_id}      | Get a contact            |
| DELETE | /contacts/{contact_id}      | Remove a contact         |

---

#### Rx Interface (Policy and Charging)

| Method | Path                                    | Description                   |
|--------|-----------------------------------------|-------------------------------|
| GET    | /rx-sessions                            | List Rx policy sessions       |
| POST   | /rx-sessions/{session_id}/terminate     | Terminate an Rx session       |

---

#### IPsec Security (Gm interface)

| Method | Path                           | Description               |
|--------|--------------------------------|---------------------------|
| POST   | /security/ipsec/setup          | Set up IPsec SA for a UE  |
| DELETE | /security/ipsec/{contact_id}   | Remove IPsec SA            |

---

| Method | Path    | Description   |
|--------|---------|---------------|
| GET    | /       | Service info  |
| GET    | /health | Health check  |

---

### 5.2 I-CSCF (port 9031)

Source: `core_network/icscf.py`
Reference: 3GPP TS 24.229

#### SIP Routing

| Method | Path          | Description                               |
|--------|---------------|-------------------------------------------|
| POST   | /sip/register | Route REGISTER to appropriate S-CSCF     |
| POST   | /sip/invite   | Route INVITE via assigned S-CSCF         |
| POST   | /sip/message  | Route MESSAGE                             |

---

#### Cx Interface (to HSS)

| Method | Path    | Description                              |
|--------|---------|------------------------------------------|
| POST   | /cx/uar | User Authorization Request               |
| POST   | /cx/lir | Location Information Request             |

---

#### S-CSCF Pool Management

| Method | Path                                   | Description                  |
|--------|----------------------------------------|------------------------------|
| GET    | /scscf-pool                            | List available S-CSCFs       |
| POST   | /scscf-pool                            | Add an S-CSCF to the pool    |
| DELETE | /scscf-pool/{scscf_id}                 | Remove an S-CSCF             |
| PUT    | /scscf-pool/{scscf_id}/load            | Update S-CSCF load metric    |

---

#### User Assignments

| Method | Path              | Description              |
|--------|-------------------|--------------------------|
| GET    | /user-assignments | List UE-to-S-CSCF mapping|

---

| Method | Path    | Description   |
|--------|---------|---------------|
| GET    | /       | Service info  |
| GET    | /health | Health check  |

---

### 5.3 S-CSCF (port 9032)

Source: `core_network/scscf.py`
Reference: 3GPP TS 24.229

#### SIP Serving

| Method | Path          | Description                              |
|--------|---------------|------------------------------------------|
| POST   | /sip/register | Process final SIP REGISTER (with iFC)   |
| POST   | /sip/invite   | Serve INVITE (apply service triggers)    |
| POST   | /sip/message  | Serve MESSAGE                            |

---

#### Cx Interface (to HSS)

| Method | Path    | Description                             |
|--------|---------|-----------------------------------------|
| POST   | /cx/sar | Server Assignment Request               |
| POST   | /cx/mar | Multimedia Authentication Request       |

---

#### User Registry

| Method | Path                        | Description                   |
|--------|-----------------------------|-------------------------------|
| GET    | /users                      | List registered IMS users     |
| GET    | /users/{impu}               | Get user by IMPU              |
| DELETE | /users/{impu}               | Remove user                   |
| GET    | /users/{impu}/contacts      | Get user's registered contacts|

---

| Method | Path    | Description   |
|--------|---------|---------------|
| GET    | /       | Service info  |
| GET    | /health | Health check  |

---

### 5.4 MRF (port 9033)

Source: `core_network/mrf.py`
Reference: 3GPP TS 23.218

#### Conference Management

| Method | Path                                 | Description                     |
|--------|--------------------------------------|---------------------------------|
| POST   | /conferences                         | Create a conference             |
| GET    | /conferences                         | List conferences                |
| GET    | /conferences/{id}                    | Get a conference                |
| DELETE | /conferences/{id}                    | Delete a conference             |
| POST   | /conferences/{id}/lock               | Lock a conference               |
| POST   | /conferences/{id}/unlock             | Unlock a conference             |

---

#### Member Management

| Method | Path                                                  | Description               |
|--------|-------------------------------------------------------|---------------------------|
| POST   | /conferences/{id}/members                             | Add a member              |
| DELETE | /conferences/{id}/members/{member_id}                 | Remove a member           |
| POST   | /conferences/{id}/members/{member_id}/mute            | Mute a member             |
| POST   | /conferences/{id}/members/{member_id}/unmute          | Unmute a member           |
| POST   | /conferences/{id}/members/{member_id}/deaf            | Deaf a member             |
| POST   | /conferences/{id}/members/{member_id}/undeaf          | Undeaf a member           |
| POST   | /conferences/{id}/mute-all                            | Mute all members          |
| POST   | /conferences/{id}/unmute-all                          | Unmute all members        |

---

#### Announcements and Media

| Method | Path                          | Description                    |
|--------|-------------------------------|--------------------------------|
| POST   | /announcements                | Create announcement            |
| GET    | /announcements                | List announcements             |
| POST   | /play                         | Play media into a conference   |
| DELETE | /play/{session_id}            | Stop a play session            |

---

#### Transcoding

| Method | Path                        | Description                  |
|--------|-----------------------------|------------------------------|
| POST   | /transcode                  | Start a transcode session    |
| GET    | /transcode                  | List transcode sessions      |
| DELETE | /transcode/{session_id}     | Stop a transcode session     |

---

| Method | Path         | Description            |
|--------|--------------|------------------------|
| POST   | /sdp/modify  | SDP offer/answer modify|
| GET    | /statistics  | MRF statistics         |
| GET    | /            | Service info           |
| GET    | /health      | Health check           |

---

### 5.5 IMS-HSS (port 9040)

Source: `core_network/ims_hss.py`
Reference: 3GPP TS 29.228, TS 29.229

Uses Milenage for IMS authentication.

#### Cx Interface

| Method | Path     | Description                                   |
|--------|----------|-----------------------------------------------|
| POST   | /cx/uar  | User Authorization Request (from I-CSCF)      |
| POST   | /cx/lir  | Location Information Request (from I-CSCF)    |
| POST   | /cx/mar  | Multimedia Authentication Request (from S-CSCF)|
| POST   | /cx/sar  | Server Assignment Request (from S-CSCF)       |
| POST   | /cx/rtr  | Registration Termination Request (HSS push)   |
| POST   | /cx/ppr  | Push Profile Request (HSS push)               |

```bash
curl -X POST http://localhost:9040/cx/uar \
  -H "Content-Type: application/json" \
  -d '{"publicIdentity":"sip:user@ims.lab","visitedNetwork":"ims.lab","authType":"REGISTRATION"}'
```

---

#### Subscription Management

| Method | Path                              | Description                 |
|--------|-----------------------------------|-----------------------------|
| GET    | /subscriptions                    | List all subscriptions      |
| GET    | /subscriptions/{impi}             | Get subscription by IMPI    |
| DELETE | /subscriptions/{impi}             | Delete a subscription       |
| POST   | /subscriptions                    | Create a subscription       |
| PUT    | /subscriptions/{impi}/ifc         | Update Initial Filter Criteria |

---

| Method | Path    | Description   |
|--------|---------|---------------|
| GET    | /       | Service info  |
| GET    | /health | Health check  |

---

## 6. EPC Network Functions (4G)

### 6.1 MME (port 9020)

Source: `core_network/mme.py`
Reference: 3GPP TS 23.401

#### Health and Config

| Method | Path                   | Description              |
|--------|------------------------|--------------------------|
| GET    | /health                | Health check             |
| GET    | /mme/v1/configuration  | MME configuration        |

---

#### S1AP (eNB interface)

| Method | Path                         | Description                    |
|--------|------------------------------|--------------------------------|
| POST   | /s1ap/v1/enb/setup           | eNB S1 Setup Request           |
| POST   | /s1ap/v1/handover/required   | Handover Required              |
| POST   | /s1ap/v1/handover/notify     | Handover Notify                |

---

#### EMM (Evolved Mobility Management)

| Method | Path                        | Description              |
|--------|-----------------------------|--------------------------|
| POST   | /emm/v1/attach              | UE Attach Request        |
| POST   | /emm/v1/detach              | UE Detach Request        |
| POST   | /emm/v1/service-request     | Service Request          |
| POST   | /emm/v1/tau                 | Tracking Area Update     |

```bash
curl -X POST http://localhost:9020/emm/v1/attach \
  -H "Content-Type: application/json" \
  -d '{"imsi":"001010000000001","tai":{"plmnId":{"mcc":"001","mnc":"01"},"tac":"001"}}'
```

---

#### ESM (Evolved Session Management)

| Method | Path                        | Description                  |
|--------|-----------------------------|------------------------------|
| POST   | /esm/v1/pdn-connectivity    | PDN Connectivity Request     |
| POST   | /esm/v1/pdn-disconnect      | PDN Disconnect Request       |

---

#### UE Registry

| Method | Path                 | Description              |
|--------|----------------------|--------------------------|
| GET    | /mme/v1/ue           | List all UE contexts     |
| GET    | /mme/v1/ue/{ue_id}   | Get UE context           |
| GET    | /mme/v1/statistics   | MME statistics           |

---

### 6.2 SGW (port 9021)

Source: `core_network/sgw.py`
Reference: 3GPP TS 23.401

#### Health and Config

| Method | Path                   | Description       |
|--------|------------------------|-------------------|
| GET    | /health                | Health check      |
| GET    | /sgw/v1/configuration  | SGW configuration |

---

#### S11 Interface (to MME)

| Method | Path                              | Description                      |
|--------|-----------------------------------|----------------------------------|
| POST   | /s11/v1/create-session            | Create Session Request (from MME)|
| POST   | /s11/v1/modify-bearer             | Modify Bearer Request            |
| POST   | /s11/v1/delete-session            | Delete Session Request           |
| POST   | /s11/v1/release-access-bearers    | Release Access Bearers           |

```bash
curl -X POST http://localhost:9021/s11/v1/create-session \
  -H "Content-Type: application/json" \
  -d '{"imsi":"001010000000001","apn":"internet","ratType":"EUTRAN"}'
```

---

#### S5 Interface (to PGW)

| Method | Path                   | Description              |
|--------|------------------------|--------------------------|
| POST   | /s5/v1/create-bearer   | Create Bearer Request    |

---

#### Data Plane

| Method | Path                      | Description                  |
|--------|---------------------------|------------------------------|
| POST   | /sgw/v1/data-notification | Downlink data notification   |
| POST   | /sgw/v1/traffic           | Inject test traffic          |

---

#### Session Registry

| Method | Path                               | Description              |
|--------|------------------------------------|--------------------------|
| GET    | /sgw/v1/sessions                   | List active sessions     |
| GET    | /sgw/v1/sessions/{s11_sgw_teid}    | Get session by TEID      |
| GET    | /sgw/v1/statistics                 | SGW statistics           |

---

### 6.3 PGW (port 9022)

Source: `core_network/pgw.py`
Reference: 3GPP TS 23.401

#### Health and Config

| Method | Path                   | Description       |
|--------|------------------------|-------------------|
| GET    | /health                | Health check      |
| GET    | /pgw/v1/configuration  | PGW configuration |

---

#### S5 Interface (from SGW)

| Method | Path                       | Description              |
|--------|----------------------------|--------------------------|
| POST   | /s5/v1/create-session      | Create Session           |
| POST   | /s5/v1/delete-session      | Delete Session           |
| POST   | /s5/v1/modify-bearer       | Modify Bearer            |

---

#### Bearer Management

| Method | Path                         | Description              |
|--------|------------------------------|--------------------------|
| POST   | /pgw/v1/create-bearer        | Create dedicated bearer  |
| DELETE | /pgw/v1/delete-bearer        | Delete dedicated bearer  |

---

#### Gx / Gy Interfaces (Policy and Charging)

| Method | Path                        | Description                    |
|--------|-----------------------------|--------------------------------|
| POST   | /gx/v1/install-rule         | Install a PCC rule (from PCRF) |
| DELETE | /gx/v1/remove-rule          | Remove a PCC rule              |
| POST   | /gy/v1/report-usage         | Report usage to OCS            |

---

#### Session Registry

| Method | Path                           | Description              |
|--------|--------------------------------|--------------------------|
| GET    | /pgw/v1/sessions               | List active sessions     |
| GET    | /pgw/v1/sessions/{session_id}  | Get session by ID        |
| GET    | /pgw/v1/statistics             | PGW statistics           |

---

### 6.4 HSS (port 9023)

Source: `core_network/hss.py`
Reference: 3GPP TS 29.272

Uses Milenage for LTE authentication vector generation.

#### Health and Config

| Method | Path                   | Description       |
|--------|------------------------|-------------------|
| GET    | /health                | Health check      |
| GET    | /hss/v1/configuration  | HSS configuration |

---

#### S6a Interface (to MME, Diameter-mapped over HTTP)

| Method | Path               | Description                              |
|--------|--------------------|------------------------------------------|
| POST   | /s6a/v1/air        | Authentication Information Request       |
| POST   | /s6a/v1/ulr        | Update Location Request                  |
| POST   | /s6a/v1/pur        | Purge UE Request                         |
| POST   | /s6a/v1/clr        | Cancel Location Request (HSS-initiated)  |
| POST   | /s6a/v1/idr        | Insert Subscriber Data Request           |

```bash
curl -X POST http://localhost:9023/s6a/v1/air \
  -H "Content-Type: application/json" \
  -d '{"imsi":"001010000000001","visitedPlmn":{"mcc":"001","mnc":"01"},"numVectors":1}'
```

---

#### Subscriber Management

| Method | Path                              | Description                  |
|--------|-----------------------------------|------------------------------|
| GET    | /hss/v1/subscribers               | List all subscribers         |
| POST   | /hss/v1/subscribers               | Create a subscriber          |
| GET    | /hss/v1/subscribers/{imsi}        | Get subscriber by IMSI       |
| PUT    | /hss/v1/subscribers/{imsi}        | Replace subscriber profile   |
| DELETE | /hss/v1/subscribers/{imsi}        | Delete a subscriber          |
| POST   | /hss/v1/subscribers/{imsi}/apn    | Add an APN profile           |

---

| Method | Path                 | Description      |
|--------|----------------------|------------------|
| GET    | /hss/v1/statistics   | HSS statistics   |

---

## 7. RAN Components

### 7.1 gNB (port 38412)

Source: `ran/gnb.py`
Reference: 3GPP TS 38.413 (NGAP), TS 38.401

NGAP port 38412 handles SCTP in real mode. HTTP endpoints on the same process.

#### NGAP Procedures

| Method | Path                                        | Description                        |
|--------|---------------------------------------------|------------------------------------|
| POST   | /ngap/initial-ue-message                    | Send initial UE message to AMF     |
| POST   | /ngap/downlink-nas-transport                | Forward downlink NAS to UE         |
| POST   | /ngap/ue-context-setup-request              | UE context setup from AMF          |
| POST   | /ngap/pdu-session-resource-setup-request    | PDU session resource setup         |
| POST   | /ngap/handover-request                      | Handover request from AMF          |
| POST   | /ngap/uplink-nas-transport                  | Send uplink NAS to AMF             |
| POST   | /initial_ue_message                         | Legacy alias                       |

```bash
curl -X POST http://localhost:38412/ngap/initial-ue-message \
  -H "Content-Type: application/json" \
  -d '{"ue_id":"ue-001","nas_pdu":"hex-encoded-pdu","tai":{"tac":"0x001"}}'
```

---

#### Status and Monitoring

| Method | Path                     | Description              |
|--------|--------------------------|--------------------------|
| GET    | /gnb_status              | gNB operational status   |
| GET    | /gnb/ue-contexts         | List active UE contexts  |
| GET    | /gnb/cell-contexts       | List active cells        |
| GET    | /gnb/transport-stats     | Transport statistics     |
| GET    | /health                  | Health check             |
| GET    | /metrics                 | Prometheus metrics       |

---

### 7.2 CU (port 38472)

Source: `ran/cu.py`
Reference: 3GPP TS 38.472 (F1AP), 3GPP E2 interface

#### F1AP (to DU)

| Method | Path                              | Description                     |
|--------|-----------------------------------|---------------------------------|
| POST   | /f1ap/f1-setup-request            | F1 Setup from DU                |
| POST   | /f1ap/initial-ul-rrc-message      | Initial UL RRC from DU          |
| POST   | /f1ap/dl-rrc-message-transfer     | DL RRC transfer to DU           |
| POST   | /f1ap/ue-context-setup-response   | UE context setup response       |

---

#### RRC

| Method | Path                 | Description          |
|--------|----------------------|----------------------|
| POST   | /rrc/create-setup    | Create RRC setup     |

---

#### E2 Interface (to Near-RT RIC)

| Method | Path                                  | Description               |
|--------|---------------------------------------|---------------------------|
| POST   | /e2/subscription                      | Create E2 subscription    |
| DELETE | /e2/subscription/{ric_request_id}     | Remove E2 subscription    |
| POST   | /e2/control                           | Send E2 control message   |
| GET    | /e2/status                            | E2 connection status      |

---

| Method | Path         | Description        |
|--------|--------------|--------------------|
| GET    | /cu/status   | CU operational status |
| GET    | /cu/ue-contexts | List UE contexts |
| GET    | /health      | Health check       |

---

### 7.3 DU (port 38473)

Source: `ran/du.py`
Reference: 3GPP TS 38.473 (F1AP)

#### F1AP (to CU)

| Method | Path                              | Description                   |
|--------|-----------------------------------|-------------------------------|
| POST   | /f1ap/f1-setup-response           | F1 Setup Response to CU       |
| POST   | /f1ap/initial-ul-rrc-message      | Forward initial UL RRC to CU  |

---

#### Layer 2 Processing

| Method | Path                  | Description              |
|--------|-----------------------|--------------------------|
| POST   | /mac/process-pdu      | Process MAC PDU          |
| POST   | /rlc/process-sdu      | Process RLC SDU          |
| POST   | /pdcp/process-sdu     | Process PDCP SDU         |
| POST   | /phy/process-prach    | Process PRACH burst      |

---

#### E2 Interface (to Near-RT RIC)

| Method | Path                                  | Description               |
|--------|---------------------------------------|---------------------------|
| POST   | /e2/subscription                      | Create E2 subscription    |
| DELETE | /e2/subscription/{ric_request_id}     | Remove E2 subscription    |
| POST   | /e2/control                           | Send E2 control message   |
| GET    | /e2/status                            | E2 connection status      |

---

| Method | Path       | Description       |
|--------|------------|-------------------|
| GET    | /du/status | DU status         |
| GET    | /health    | Health check      |

---

### 7.4 Near-RT RIC (port 8095)

Source: `ran/ric/near_rt_ric.py`
Reference: O-RAN.WG3.E2AP, O-RAN.WG2.A1AP

#### E2 Interface Management

| Method | Path                           | Description                         |
|--------|--------------------------------|-------------------------------------|
| POST   | /e2/setup                      | E2 Setup from gNB/CU/DU             |
| POST   | /e2/subscription               | Register E2 subscription (201)      |
| GET    | /e2/subscriptions              | List all E2 subscriptions           |
| GET    | /e2/subscriptions/{id}         | Get E2 subscription                 |
| DELETE | /e2/subscriptions/{id}         | Remove E2 subscription              |
| POST   | /e2/indication                 | Receive E2 indication from node     |
| POST   | /e2/control                    | Send E2 control to node             |
| POST   | /e2/query                      | Query E2 node metrics               |

---

#### RIC Management

| Method | Path                  | Description              |
|--------|-----------------------|--------------------------|
| GET    | /ric/e2-nodes         | List connected E2 nodes  |
| GET    | /ric/e2-nodes/{id}    | Get an E2 node           |
| GET    | /ric/xapps            | List loaded xApps        |
| POST   | /ric/xapps            | Register an xApp         |
| DELETE | /ric/xapps/{id}       | Remove an xApp           |

---

#### A1 Interface (from Non-RT RIC)

| Method | Path                  | Description                     |
|--------|-----------------------|---------------------------------|
| POST   | /a1/policies          | Receive A1 policy (201)         |
| GET    | /a1/policies          | List A1 policies                |
| DELETE | /a1/policies/{id}     | Remove an A1 policy             |
| POST   | /a1/enrichment        | Receive A1 enrichment data      |

```bash
curl -X POST http://localhost:8095/a1/policies \
  -H "Content-Type: application/json" \
  -d '{"policyTypeId":"ORAN_TrafficSteeringPreference","scope":{"ueId":"ue-001"},"policyObject":{}}'
```

---

#### Radio Monitoring

| Method | Path                     | Description                       |
|--------|--------------------------|-----------------------------------|
| GET    | /ric/radio/ue/{ue_id}    | Radio metrics for a specific UE   |
| GET    | /ric/radio/cells         | Radio metrics for all cells       |

---

| Method | Path         | Description        |
|--------|--------------|--------------------|
| GET    | /health      | Health check       |
| GET    | /ric/status  | RIC status         |
| GET    | /metrics     | Prometheus metrics |

---

### 7.5 Non-RT RIC (port 8096)

Source: `ran/ric/non_rt_ric.py`
Reference: O-RAN.WG2.A1AP, O-RAN.WG2.A1-EI

#### A1-P (Policy Management towards Near-RT RIC)

| Method | Path                                                          | Description                          |
|--------|---------------------------------------------------------------|--------------------------------------|
| GET    | /a1-p/policytypes                                             | List policy types                    |
| GET    | /a1-p/policytypes/{id}                                        | Get policy type schema               |
| PUT    | /a1-p/policytypes/{id}                                        | Register a policy type               |
| GET    | /a1-p/policytypes/{id}/policies                               | List policies of a type              |
| PUT    | /a1-p/policytypes/{id}/policies/{policy_id}                   | Create or update a policy instance   |
| GET    | /a1-p/policytypes/{id}/policies/{policy_id}                   | Get a policy instance                |
| DELETE | /a1-p/policytypes/{id}/policies/{policy_id}                   | Delete a policy instance             |
| GET    | /a1-p/policytypes/{id}/policies/{policy_id}/status            | Get policy enforcement status        |

```bash
curl -X PUT http://localhost:8096/a1-p/policytypes/ORAN_TrafficSteeringPreference/policies/policy-001 \
  -H "Content-Type: application/json" \
  -d '{"scope":{"ueId":"ue-001"},"policyObject":{"preferredBearer":"slice-1"}}'
```

---

#### A1-EI (Enrichment Information)

| Method | Path                                  | Description                    |
|--------|---------------------------------------|--------------------------------|
| GET    | /a1-ei/eitypes                        | List EI types                  |
| PUT    | /a1-ei/eitypes/{id}                   | Register an EI type            |
| GET    | /a1-ei/eijobs                         | List EI jobs                   |
| PUT    | /a1-ei/eijobs/{id}                    | Create or update an EI job     |
| DELETE | /a1-ei/eijobs/{id}                    | Delete an EI job               |
| POST   | /a1-ei/eijobs/{id}/deliver            | Deliver enrichment data to job |

---

#### rApp Management

| Method | Path               | Description           |
|--------|--------------------|-----------------------|
| GET    | /ric/rapps         | List registered rApps |
| POST   | /ric/rapps         | Register an rApp      |
| DELETE | /ric/rapps/{id}    | Remove an rApp        |

---

#### O1 Interface (Network Management)

| Method | Path                                | Description                    |
|--------|-------------------------------------|--------------------------------|
| GET    | /o1/intents                         | List O1 management intents     |
| POST   | /o1/intents                         | Create an O1 intent            |
| GET    | /o1/vnf-instances                   | List VNF instances             |
| POST   | /o1/vnf-instances/{vnf_id}/scale    | Scale a VNF instance           |

---

#### Analytics

| Method | Path                   | Description                    |
|--------|------------------------|--------------------------------|
| GET    | /ric/analytics         | Historical analytics           |
| GET    | /ric/analytics/latest  | Latest analytics snapshot      |

---

| Method | Path         | Description        |
|--------|--------------|--------------------|
| GET    | /health      | Health check       |
| GET    | /ric/status  | Non-RT RIC status  |
| GET    | /metrics     | Prometheus metrics |

---

## 8. Storefront API Client

Source: `src/storefront/src/lib/api.ts`

The Storefront is a TypeScript/Next.js frontend. It does not expose its own REST API. Instead,
it consumes the Catalog API (port 8081) and the Order Engine (port 8080) via the `api.ts` client
module.

To browse the catalog or submit orders from the Storefront UI, access:

```
http://localhost:3000
```

The `api.ts` module exports typed fetch wrappers that call:

- `GET /tmf-api/productCatalogManagement/v4/productOffering` (catalog browse)
- `GET /tmf-api/productCatalogManagement/v4/productOffering/{id}` (offering detail)
- `POST /tmf-api/productOrderingManagement/v4/productOrder` (place order)
- `GET /tmf-api/productOrderingManagement/v4/productOrder/{id}` (order status)

For direct integration without the Storefront UI, call the Order Engine and Catalog API
endpoints documented in sections 1 and 2 above.

---

*All endpoints verified from source code in `core_network/`, `ran/`, `src/order_engine/`,
`src/catalog_api/`, and `src/ai_observer/`. Ports are host-mapped values from docker-compose.*

<!-- Public-tree note: source labels have been normalized to the clean lab naming policy. -->
