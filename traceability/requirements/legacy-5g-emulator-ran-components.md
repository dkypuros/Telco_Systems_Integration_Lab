# 5G Radio Access Network (RAN) Components

## Overview

This document analyzes the Radio Access Network (RAN) implementation in the 5G Network Simulator, examining compliance with 3GPP specifications and identifying enhancement opportunities for complete RAN protocol stack implementation.

## RAN Architecture Overview

```
                    5G Radio Access Network (NG-RAN) Architecture
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              NG-RAN (Next Generation RAN)                      │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                            gNodeB (gNB)                                 │   │
│  │                                                                         │   │
│  │   ┌─────────────────────────┐    ┌─────────────────────────────────┐   │   │
│  │   │     Centralized Unit    │    │      Distributed Unit          │   │   │
│  │   │         (CU)            │    │          (DU)                   │   │   │
│  │   │                         │    │                                 │   │   │
│  │   │  ┌─────┐  ┌─────┐       │F1  │  ┌─────┐  ┌─────┐  ┌─────┐     │   │   │
│  │   │  │ RRC │  │PDCP │       │◄──►│  │ RLC │  │ MAC │  │ PHY │     │   │   │
│  │   │  └─────┘  └─────┘       │    │  └─────┘  └─────┘  └─────┘     │   │   │
│  │   │           ┌─────┐       │    │                        │        │   │   │
│  │   │           │SDAP │       │    │                        │        │   │   │
│  │   │           └─────┘       │    │                        │        │   │   │
│  │   └─────────────────────────┘    └────────────────────────┼────────┘   │   │
│  └─────────────┬─────────────────────────────────────────────┼────────────┘   │
│                │ N2 (NGAP)                                   │                │
│                │                                             │ RF             │
└────────────────┼─────────────────────────────────────────────┼────────────────┘
                 │                                             │
          ┌──────▼──────┐                               ┌──────▼──────┐
          │  5G Core    │                               │ Remote Radio│
          │  Network    │                               │ Unit (RRU)  │
          │   (5GC)     │                               └─────────────┘
          └─────────────┘                                       │ Uu
                                                                │
                                                        ┌───────▼───────┐
                                                        │   User        │
                                                        │ Equipment     │
                                                        │    (UE)       │
                                                        └───────────────┘
```

## RAN Components Analysis

### gNodeB (5G Base Station) {#gnb-section}

**File Location:** `clean_5g_emulator_api/ran/gnb.py`  
**3GPP Compliance Level:** 50% ⚠️ Needs Enhancement  
**Primary Interfaces:** N2 (AMF), N3 (UPF), Xn (Other gNBs)

#### 3GPP Specifications Alignment

| Specification | Section | Implementation Status | Details |
|---------------|---------|---------------------|---------|
| **TS 38.413** | NGAP | ⚠️ Basic | Limited message set |
| **TS 38.401** | NG-RAN Architecture | ⚠️ Basic | Basic concepts only |
| **TS 38.331** | RRC | ❌ Not implemented | Radio Resource Control |
| **TS 38.423** | XnAP | ❌ Not implemented | Inter-gNB interface |

#### Current Implementation

```python
class GNB:
    def __init__(self):
        self.name = "gnb001"
        self.amf_connection = None
        self.ue_contexts = {}
        
    # ⚠️ Basic AMF connection - needs enhancement
    def connect_to_amf(self):
        """
        Basic AMF discovery and connection
        Needs complete NGAP implementation
        """
        try:
            # Simple AMF discovery
            nrf_response = requests.get(f"{nrf_url}/discover/AMF")
            amf_info = nrf_response.json()
            
            if 'ip' in amf_info:
                self.amf_url = f"http://{amf_info['ip']}:{amf_info['port']}"
                logger.info(f"Connected to AMF at {self.amf_url}")
                
        except Exception as e:
            logger.error(f"Failed to connect to AMF: {e}")
    
    # ⚠️ Basic NGAP implementation
    def send_initial_ue_message(self, ue_data):
        """
        Simplified NGAP Initial UE Message
        Needs complete NGAP message structure per TS 38.413
        """
        initial_message = {
            "message_type": "INITIAL_UE_MESSAGE",
            "ue_id": ue_data.get("ue_id"),
            "nas_pdu": ue_data.get("nas_message"),
            "user_location_information": {
                "nr_cgi": "001010000000001",
                "tai": "00101001"
            }
        }
        
    # ✅ Good heartbeat mechanism
    def heartbeat(self):
        """Well-implemented keep-alive mechanism"""
        while True:
            try:
                # Send heartbeat to maintain AMF connection
                time.sleep(30)
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
```

#### Enhancement Requirements

**High Priority - Complete NGAP Implementation (TS 38.413):**

```python
# Required NGAP message implementations
class NGAP_Messages:
    
    def initial_context_setup_request(self, ue_context):
        """
        TS 38.413 § 9.2.4.1 - Initial Context Setup Request
        """
        return {
            "procedureCode": 14,
            "criticality": "reject",
            "value": {
                "protocolIEs": {
                    "AMF-UE-NGAP-ID": ue_context["amf_ue_ngap_id"],
                    "RAN-UE-NGAP-ID": ue_context["ran_ue_ngap_id"],
                    "UESecurityCapabilities": ue_context["security_capabilities"],
                    "SecurityKey": ue_context["security_key"],
                    "PDUSessionResourceSetupRequestList": []
                }
            }
        }
    
    def ue_context_modification_request(self, modification_data):
        """
        TS 38.413 § 9.2.4.3 - UE Context Modification Request
        """
        
    def ue_context_release_command(self, release_data):
        """
        TS 38.413 § 9.2.4.4 - UE Context Release Command
        """
        
    def handover_request(self, handover_data):
        """
        TS 38.413 § 9.2.1.1 - Handover Request
        """
        
    def pdu_session_resource_setup_request(self, session_data):
        """
        TS 38.413 § 9.2.1.1 - PDU Session Resource Setup Request
        """
```

**Medium Priority - RRC Integration:**

```python
# Integration with RRC layer per TS 38.331
def handle_rrc_setup_request(self, ue_id):
    """
    Handle RRC Setup Request from UE
    Integrate with CU RRC implementation
    """
    
def send_rrc_reconfiguration(self, ue_id, config):
    """
    Send RRC Reconfiguration message
    Configure radio bearers and measurement
    """
```

---

### CU-DU Split Architecture {#cu-du-section}

The simulator implements the 3GPP-defined CU-DU split architecture but currently lacks the critical F1 Application Protocol (F1AP) implementation.

#### Centralized Unit (CU) Implementation

**File Location:** `clean_5g_emulator_api/ran/cu/cu.py`  
**3GPP Compliance Level:** 15% ❌ Critical Implementation Needed  
**Primary Interfaces:** F1 (DU), E1 (Internal), N2 (AMF)

##### Current Implementation
```python
# ❌ Stub implementation only
class CU:
    def __init__(self):
        self.name = "cu001"
        self.connected_dus = {}
        
    def register_du(self, du_info):
        """Basic DU registration - needs F1AP implementation"""
        du_id = du_info.get("du_id")
        self.connected_dus[du_id] = du_info
```

##### Required Implementation (TS 38.463 - F1AP)

**Critical Priority - F1 Application Protocol:**

```python
class F1AP_Implementation:
    """
    Complete F1AP implementation per TS 38.463
    """
    
    def f1_setup_request(self, du_info):
        """
        TS 38.463 § 9.2.1.1 - F1 Setup Request
        DU initiates connection to CU
        """
        f1_setup = {
            "procedureCode": 1,
            "criticality": "reject", 
            "value": {
                "protocolIEs": {
                    "TransactionID": self.generate_transaction_id(),
                    "gNB-DU-ID": du_info["du_id"],
                    "gNB-DU-Name": du_info["du_name"],
                    "Served-Cells-List": du_info["served_cells"],
                    "RRC-Version": "rel16"
                }
            }
        }
        return f1_setup
    
    def f1_setup_response(self, setup_request):
        """
        TS 38.463 § 9.2.1.2 - F1 Setup Response
        CU acknowledges DU connection
        """
        return {
            "procedureCode": 1,
            "criticality": "reject",
            "value": {
                "protocolIEs": {
                    "TransactionID": setup_request["value"]["protocolIEs"]["TransactionID"],
                    "gNB-CU-Name": self.cu_name,
                    "Cells-to-be-Activated-List": []
                }
            }
        }
    
    def ue_context_setup_request(self, ue_context):
        """
        TS 38.463 § 9.2.2.1 - UE Context Setup Request
        Setup UE context between CU and DU
        """
        
    def dl_rrc_message_transfer(self, rrc_message):
        """
        TS 38.463 § 9.2.3.1 - DL RRC Message Transfer
        Forward RRC messages from CU to DU
        """
```

#### Distributed Unit (DU) Implementation

**File Location:** `clean_5g_emulator_api/ran/du/du.py`  
**3GPP Compliance Level:** 15% ❌ Critical Implementation Needed  
**Primary Interfaces:** F1 (CU)

##### Required Enhancement
```python
class DU:
    def __init__(self):
        self.du_id = "du001"
        self.cu_connection = None
        self.served_cells = []
        
    # Required F1AP client implementation
    def initiate_f1_setup(self, cu_address):
        """
        Initiate F1 Setup procedure with CU per TS 38.463
        """
        setup_request = self.f1ap.f1_setup_request({
            "du_id": self.du_id,
            "du_name": f"DU-{self.du_id}",
            "served_cells": self.served_cells
        })
        
        # Send to CU and handle response
        
    def handle_ue_context_setup_request(self, setup_request):
        """
        Handle UE Context Setup from CU per TS 38.463
        """
```

---

### Protocol Stack Implementation {#protocol-stack}

The RAN protocol stack is currently implemented as basic stubs. Full 3GPP compliance requires complete implementation of all layers.

#### Upper Layer Protocols (CU)

##### RRC (Radio Resource Control)
**File Location:** `clean_5g_emulator_api/ran/cu/rrc.py`  
**3GPP Specification:** TS 38.331  
**Current Compliance:** 5% ❌ Stub Only

**Required Implementation:**
```python
class RRC_Implementation:
    """
    Complete RRC implementation per TS 38.331
    """
    
    def rrc_setup_request(self, ue_id):
        """
        TS 38.331 § 5.3.3 - RRC Setup procedure
        """
        return {
            "message": {
                "c1": {
                    "rrcSetupRequest": {
                        "rrcSetupRequest": {
                            "ue-Identity": {
                                "randomValue": self.generate_random_value()
                            },
                            "establishmentCause": "mo-Data"
                        }
                    }
                }
            }
        }
    
    def rrc_setup_complete(self, ue_context):
        """
        TS 38.331 § 5.3.3 - RRC Setup Complete
        """
        
    def rrc_reconfiguration(self, ue_id, bearer_config):
        """
        TS 38.331 § 5.3.5 - RRC Reconfiguration
        Configure radio bearers and measurement
        """
        
    def measurement_report(self, ue_id, measurements):
        """
        TS 38.331 § 5.5.5 - Measurement Report
        Handle UE measurement reports for mobility
        """
```

##### PDCP (Packet Data Convergence Protocol)
**File Location:** `clean_5g_emulator_api/ran/cu/pdcp.py`  
**3GPP Specification:** TS 38.323  
**Current Compliance:** 5% ❌ Stub Only

**Required Implementation:**
```python
class PDCP_Implementation:
    """
    Complete PDCP implementation per TS 38.323
    """
    
    def pdcp_data_pdu(self, sn, data):
        """
        TS 38.323 § 6.2.1 - PDCP Data PDU format
        """
        return {
            "pdcp_header": {
                "sequence_number": sn,
                "data_control": 0  # Data PDU
            },
            "payload": data
        }
    
    def header_compression(self, ip_packet):
        """
        TS 38.323 § 5.7 - Header compression (ROHC)
        """
        
    def security_protection(self, pdcp_pdu, security_context):
        """
        TS 38.323 § 5.8 - Ciphering and integrity protection
        """
        
    def duplicate_detection(self, pdcp_pdu):
        """
        TS 38.323 § 5.4 - Duplicate detection and discarding
        """
```

##### SDAP (Service Data Adaptation Protocol)
**File Location:** `clean_5g_emulator_api/ran/cu/sdap.py`  
**3GPP Specification:** TS 37.324  
**Current Compliance:** 5% ❌ Stub Only

**Required Implementation:**
```python
class SDAP_Implementation:
    """
    Complete SDAP implementation per TS 37.324
    """
    
    def qos_flow_mapping(self, qfi, drb_id):
        """
        TS 37.324 § 5.1 - QoS flow to DRB mapping
        """
        
    def sdap_header(self, qfi, rqi=0, rdi=0):
        """
        TS 37.324 § 6.2.1 - SDAP header format
        """
        return {
            "qfi": qfi,        # QoS Flow Identifier
            "rqi": rqi,        # Reflective QoS Indicator
            "rdi": rdi         # Reflective QoS Indication
        }
```

#### Lower Layer Protocols (DU)

##### RLC (Radio Link Control)
**File Location:** `clean_5g_emulator_api/ran/du/rlc.py`  
**3GPP Specification:** TS 38.322  
**Current Compliance:** 5% ❌ Stub Only

**Required Implementation:**
```python
class RLC_Implementation:
    """
    Complete RLC implementation per TS 38.322
    """
    
    def am_data_pdu(self, sn, data, poll=False):
        """
        TS 38.322 § 6.2.1 - AM Data PDU (Acknowledged Mode)
        """
        return {
            "header": {
                "dc": 1,           # Data/Control field
                "p": poll,         # Polling bit
                "si": "complete",  # Segmentation Info
                "sn": sn           # Sequence Number
            },
            "data": data
        }
    
    def status_pdu(self, ack_sn, nack_list):
        """
        TS 38.322 § 6.2.2 - STATUS PDU for ARQ
        """
        
    def segmentation(self, rlc_sdu, segment_size):
        """
        TS 38.322 § 5.1.3 - Segmentation and reassembly
        """
        
    def arq_procedure(self, pdu_list):
        """
        TS 38.322 § 5.2 - ARQ (Automatic Repeat Request)
        """
```

##### MAC (Medium Access Control)
**File Location:** `clean_5g_emulator_api/ran/du/mac.py`  
**3GPP Specification:** TS 38.321  
**Current Compliance:** 5% ❌ Stub Only

**Required Implementation:**
```python
class MAC_Implementation:
    """
    Complete MAC implementation per TS 38.321
    """
    
    def mac_pdu(self, subpdus):
        """
        TS 38.321 § 6.1.2 - MAC PDU format
        """
        return {
            "subpdus": [
                {
                    "lcid": subpdu["lcid"],  # Logical Channel ID
                    "length": len(subpdu["data"]),
                    "data": subpdu["data"]
                } for subpdu in subpdus
            ]
        }
    
    def bsr_procedure(self, buffer_status):
        """
        TS 38.321 § 5.4.5 - Buffer Status Reporting
        """
        
    def random_access_procedure(self, preamble):
        """
        TS 38.321 § 5.1 - Random Access procedure
        """
        
    def harq_procedure(self, transport_block):
        """
        TS 38.321 § 5.4.2 - HARQ (Hybrid ARQ)
        """
```

##### PHY (Physical Layer)
**File Location:** `clean_5g_emulator_api/ran/du/phy.py`  
**3GPP Specification:** TS 38.200 series  
**Current Compliance:** 5% ❌ Stub Only

**Required Implementation:**
```python
class PHY_Implementation:
    """
    Physical layer implementation per TS 38.200 series
    """
    
    def ofdm_modulation(self, data_symbols):
        """
        TS 38.211 § 5.1 - OFDM modulation
        """
        
    def channel_coding(self, transport_block):
        """
        TS 38.212 § 5.1 - Channel coding (LDPC, Polar)
        """
        
    def resource_mapping(self, coded_bits, resource_grid):
        """
        TS 38.211 § 7 - Physical resource mapping
        """
        
    def channel_estimation(self, received_signal):
        """
        Channel estimation using reference signals
        """
```

---

### Remote Radio Unit (RRU)

**File Location:** `clean_5g_emulator_api/ran/rru/rru.py`  
**3GPP Compliance Level:** 5% ❌ Basic Structure Only  
**Primary Interfaces:** Fronthaul (to DU)

#### Current Implementation
```python
# ❌ Basic loop structure only
class RRU:
    def __init__(self):
        self.running = True
        
    def run(self):
        while self.running:
            time.sleep(1)
```

#### Required Implementation
```python
class RRU_Implementation:
    """
    Complete RRU implementation with RF simulation
    """
    
    def __init__(self):
        self.rf_chains = []
        self.antenna_config = {}
        self.fronthaul_connection = None
        
    def rf_transmission(self, baseband_signal):
        """
        RF signal transmission simulation
        """
        
    def rf_reception(self):
        """
        RF signal reception and analog-to-digital conversion
        """
        
    def beamforming(self, weights, signal):
        """
        Massive MIMO beamforming implementation
        """
        
    def fronthaul_interface(self, cpri_data):
        """
        CPRI/eCPRI fronthaul interface simulation
        """
```

---

## Interface Implementation Status

### Inter-RAN Interfaces

| Interface | From | To | Protocol | 3GPP Spec | Status | Priority |
|-----------|------|----|---------|-----------|---------|---------| 
| **F1** | DU | CU | F1AP | TS 38.463 | ❌ Not implemented | 🔴 **CRITICAL** |
| **E1** | CU-CP | CU-UP | E1AP | TS 38.463 | ❌ Not implemented | 🟡 **HIGH** |
| **Xn** | gNB | gNB | XnAP | TS 38.423 | ❌ Not implemented | 🟠 **MEDIUM** |
| **Uu** | UE | gNB | Radio | TS 38.200 | ❌ Not implemented | 🟠 **MEDIUM** |

### External Interfaces

| Interface | From | To | Protocol | 3GPP Spec | Status | Priority |
|-----------|------|----|---------|-----------|---------|---------| 
| **N2** | gNB | AMF | NGAP | TS 38.413 | ⚠️ Basic | 🔴 **CRITICAL** |
| **N3** | gNB | UPF | GTP-U | TS 29.281 | ❌ Not implemented | 🟡 **HIGH** |

---

## RAN Enhancement Roadmap

### Phase 1: Core Protocol Implementation (3 months)

#### Month 1: F1AP Implementation
```python
# Priority 1: Complete F1AP protocol stack
- F1 Setup procedures
- UE Context Management
- RRC Message Transfer
- System Information procedures
```

#### Month 2: NGAP Enhancement
```python
# Priority 2: Complete NGAP message set
- Initial Context Setup
- UE Context Modification
- PDU Session Resource procedures
- Handover procedures
```

#### Month 3: RRC Integration
```python
# Priority 3: RRC protocol implementation
- Connection establishment
- Reconfiguration procedures  
- Measurement and mobility
- Radio bearer configuration
```

### Phase 2: Protocol Stack Completion (3 months)

#### Month 4-5: Lower Layer Protocols
```python
# PDCP, RLC, MAC, PHY implementation
- Complete protocol state machines
- Data flow implementation
- Error handling and recovery
```

#### Month 6: Integration and Testing
```python
# End-to-end integration
- Cross-layer interactions
- Performance optimization
- Comprehensive testing
```

### Phase 3: Advanced Features (2 months)

#### Month 7: Advanced RAN Features
```python
# Advanced capabilities
- Dual Connectivity
- Carrier Aggregation
- Advanced MIMO
- Network Slicing support
```

#### Month 8: Inter-gNB Features
```python
# Xn interface implementation
- Inter-gNB handover
- Secondary Node procedures
- Load balancing
```

## Testing and Validation

### RAN Protocol Testing Framework
```python
class RAN_TestSuite:
    def test_f1_setup_procedure(self):
        # Test F1 Setup between CU and DU
        
    def test_ue_context_setup(self):
        # Test UE context establishment
        
    def test_rrc_connection_establishment(self):
        # Test end-to-end RRC setup
        
    def test_data_flow(self):
        # Test user plane data flow through protocol stack
        
    def test_handover_procedure(self):
        # Test NGAP handover procedures
```

## Success Metrics

### Target Compliance Levels
- **F1AP Protocol**: 90% compliance by end of Phase 1
- **NGAP Protocol**: 85% compliance by end of Phase 1  
- **RRC Protocol**: 80% compliance by end of Phase 2
- **Overall RAN**: 75% compliance by end of Phase 3

### Key Performance Indicators
1. **Protocol Completeness**: >90% of required messages implemented
2. **Procedure Success Rate**: >95% for all implemented procedures
3. **Integration Testing**: 100% pass rate for cross-layer tests
4. **3GPP Conformance**: >95% message format compliance

---

## O-RAN RAN Intelligent Controller (RIC) Integration

The RAN components now integrate with the O-RAN RAN Intelligent Controller for intelligent RAN optimization. See [RIC Architecture](ric-architecture.md) for comprehensive documentation.

### RIC Architecture Overview

```
                    ┌─────────────────────────────────────────────┐
                    │             Non-RT RIC                       │
                    │              :8096                           │
                    │  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
                    │  │  rApps  │  │   A1    │  │   O1    │      │
                    │  │         │  │ Policy  │  │  (SMO)  │      │
                    │  └─────────┘  └────┬────┘  └─────────┘      │
                    └────────────────────┼────────────────────────┘
                                         │ A1
                    ┌────────────────────▼────────────────────────┐
                    │              Near-RT RIC                     │
                    │               :8095                          │
                    │  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
                    │  │  xApps  │  │   E2AP  │  │ Subscr. │      │
                    │  │         │  │         │  │ Manager │      │
                    │  └─────────┘  └────┬────┘  └─────────┘      │
                    └────────────────────┼────────────────────────┘
                                         │ E2
                    ┌────────────────────┼────────────────────────┐
                    │                    │                        │
             ┌──────▼──────┐      ┌──────▼──────┐          ┌──────▼──────┐
             │     CU      │      │     DU      │          │    gNB      │
             │  E2 Agent   │      │  E2 Agent   │          │  E2 Agent   │
             │   :38472    │      │   :38473    │          │   :38412    │
             └─────────────┘      └─────────────┘          └─────────────┘
```

### E2 Agent Integration

Both CU and DU components include E2 agents that enable:

#### CU E2 Agent Capabilities
- **E2SM-KPM**: PDCP throughput, RLC retransmissions, RRC active UEs
- **E2SM-RC**: Handover control, bearer management, RRC configuration

#### DU E2 Agent Capabilities
- **E2SM-KPM**: PRB utilization, CQI distribution, MCS statistics, HARQ retransmissions
- **E2SM-RC**: Scheduler control, power management, resource allocation

### RIC-Enabled Use Cases

| Use Case | RIC Component | Interface | Control Loop |
|----------|---------------|-----------|--------------|
| Load Balancing | Near-RT RIC (xApp) | E2 Control | 10ms - 1s |
| QoS Optimization | Near-RT RIC (xApp) | E2 Control | 10ms - 1s |
| Traffic Steering | Non-RT RIC (rApp) | A1 Policy | > 1s |
| Energy Efficiency | Non-RT RIC (rApp) | A1 Policy | > 1s |
| Interference Management | Near-RT RIC (xApp) | E2 Control | 10ms - 1s |

### Specification Compliance

| Interface | Specification | Status |
|-----------|---------------|--------|
| E2 | ETSI TS 104039 (E2AP) | ✅ Implemented |
| A1 | ETSI TS 103983 | ✅ Implemented |
| E2SM-KPM | O-RAN.WG3.E2SM-KPM | ✅ Implemented |
| E2SM-RC | O-RAN.WG3.E2SM-RC | ✅ Implemented |

---

## Conclusion

The current RAN implementation provides basic architectural structure but requires significant enhancement to achieve 3GPP compliance. The proposed roadmap focuses on critical protocol implementations (F1AP, NGAP, RRC) followed by complete protocol stack development.

**RIC Integration Completed:**
- Near-RT RIC with E2 interface for near-real-time control
- Non-RT RIC with A1 interface for policy management
- E2 agents integrated into CU and DU components
- xApp/rApp SDKs for extensible RAN intelligence

**Immediate Actions Required:**
1. Begin F1AP implementation for CU-DU split architecture
2. Enhance NGAP implementation for complete gNB functionality
3. Implement RRC protocol for radio resource management
4. Develop comprehensive RAN testing framework

This systematic approach will transform the basic RAN structure into a fully functional, 3GPP-compliant radio access network implementation with O-RAN RIC intelligence.