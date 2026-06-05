# O-RAN spec-map validation report

This is a derived traceability/readiness artifact. It validates candidate map references; it is not a formal O-RAN conformance claim.

## Summary

- Spec map: `adapters/mock_oran/oran/o_ran_spec_map.py`
- Rows checked: 47
- Implementation paths existing: 14
- Implementation paths missing: 33
- Local spec catalog checked: True
- Local spec catalog: `specs/oran/Latest_Versions`
- Local spec files indexed: 163
- Spec filename stems existing: 46
- Spec filename stems missing: 1
- Duplicate spec keys: none
- Duplicate mapped module keys: etsi/o2/o2_dms.py, etsi/o2/o2_ims.py, oam/o1.py, oam/teiv.py, ran/energy/nes.py, ran/fronthaul/cus_plane.py, ran/ric/e2ap.py, ran/ric/near_rt_ric.py, ran/ric/non_rt_ric.py, ran/ric/y1.py, ran/slicing/oran_slicing.py, security/security_service.py, security/zero_trust.py, smo/r1.py, transport/xhaul.py

## Missing implementation paths

| WG | Spec | Mapped module | Candidate status |
|---|---|---|---|
| WG1 | `O-RAN.WG1.TS.OAD-R005-v16.00` | `smo/smo_framework.py` | missing repo path |
| WG1 | `O-RAN.WG1.Network-Energy-Savings-Technical-Report-R003-v02.00` | `ran/energy/nes.py` | missing repo path |
| WG1 | `O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00` | `ran/energy/nes.py` | missing repo path |
| WG2 | `O-RAN.WG2.TS.A1AP-R005-v06.00` | `ran/ric/a1_interface.py` | missing repo path |
| WG2 | `O-RAN.WG2.TS.R1AP-R005-v10.00` | `smo/r1.py` | missing repo path |
| WG2 | `O-RAN.WG2.TS.R1GAP-R005-v13.00` | `smo/r1.py` | missing repo path |
| WG2 | `O-RAN.WG2.AIML-v01.03` | `smo/aiml.py` | missing repo path |
| WG3 | `O-RAN.WG3.TS.Y1AP-R005-v01.02` | `ran/ric/y1.py` | missing repo path |
| WG3 | `O-RAN.WG3.TS.Y1GAP-R005-v01.02` | `ran/ric/y1.py` | missing repo path |
| WG4 | `O-RAN.WG4.TS.MP.0-R005-v20.00` | `ran/fronthaul/m_plane.py` | missing repo path |
| WG4 | `O-RAN.WG4.TS.CONF.0-R005-v15.00` | `ran/fronthaul/o_ru.py` | missing repo path |
| WG6 | `O-RAN.WG6.TS.O2IMS-INTERFACE-R005-v11.00` | `etsi/o2/o2_ims.py` | missing repo path |
| WG6 | `O-RAN.WG6.TS.O2DMS-INTERFACE-K8S-PROFILE-R005-v07.00` | `etsi/o2/o2_dms.py` | missing repo path |
| WG6 | `O-RAN.WG6.O-Cloud Notification API-v04.00` | `etsi/o2/o_cloud_notification.py` | missing repo path |
| WG6 | `O-RAN.WG6.CADS-v08.01` | `etsi/o2/o2_ims.py` | missing repo path |
| WG6 | `O-RAN.WG6.ASD-R004-v02.00` | `etsi/o2/o2_dms.py` | missing repo path |
| WG9 | `O-RAN.WG9.XTRP-MGT.0-R004-v10.00` | `transport/xhaul.py` | missing repo path |
| WG9 | `O-RAN.WG9.XTRP-SYN.0-R004-v07.00` | `transport/xhaul.py` | missing repo path |
| WG9 | `O-RAN.WG9.XPSAAS.0-R005-v10.00` | `transport/xhaul.py` | missing repo path |
| WG10 | `O-RAN.WG10.TS.O1-Interface.0-R005-v18.00` | `oam/o1.py` | missing repo path |
| WG10 | `O-RAN.WG10.TS.O1NRM.0-R004-v04.00` | `oam/o1.py` | missing repo path |
| WG10 | `O-RAN.WG10.TS.O1PMeas-R005-v05.00` | `oam/pm.py` | missing repo path |
| WG10 | `O-RAN.WG10.TS.OAM-Architecture-R005-v17.00` | `oam/o1.py` | missing repo path |
| WG10 | `O-RAN.WG10.TS.TE&IV-API.0-R005-v04.00` | `oam/teiv.py` | missing repo path |
| WG10 | `O-RAN.WG10.TS.TE&IV-DM.0-R005-v04.00` | `oam/teiv.py` | missing repo path |
| WG11 | `O-RAN.WG11.TS.SecProtSpec.0-R005-v14.00` | `security/security_service.py` | missing repo path |
| WG11 | `O-RAN.WG11.TS.SRCS.0-R005-v14.00` | `security/security_service.py` | missing repo path |
| WG11 | `O-RAN.WG11.TS.STS-R005-v12.00` | `test_oran_compliance.py` | missing repo path |
| WG11 | `O-RAN.WG11.TR.ZTA-R005-v05.00` | `security/zero_trust.py` | missing repo path |
| WG11 | `O-RAN.WG11.TR.Threat-Modeling-R005-v08.00` | `security/zero_trust.py` | missing repo path |
| WG11 | `O-RAN.WG11.TR.Certficate-Management-Framework.0-R005-v06.00` | `security/cert_manager.py` | missing repo path |
| WG11 | `O-RAN.WG11.TR.OAuth2.0-Security.0-R005-v07.00` | `security/security_service.py` | missing repo path |
| WG11 | `O-RAN.WG11.TR.PQC-Security.0-R005-v02.00` | `security/pqc.py` | missing repo path |

## Missing local spec filenames

| WG | Spec stem | Mapped module | Candidate status |
|---|---|---|---|
| WG6 | `O-RAN.WG6.TS.O2DMS-INTERFACE-K8S-PROFILE-R005-v07.00` | `etsi/o2/o2_dms.py` | missing local spec file |

## Resolved mapped paths

| WG | Spec | Mapped module | Resolved repo path | Local spec file |
|---|---|---|---|---|
| WG1 | `O-RAN.WG1.TS.OAD-R005-v16.00` | `smo/smo_framework.py` | missing | `O-RAN.WG1.TS.OAD-R005-v16.00.docx` |
| WG1 | `O-RAN.WG1.TS.Slicing-Architecture-R004-v14.01` | `ran/slicing/oran_slicing.py` | `adapters/mock_ran/ran/slicing/oran_slicing.py` | `O-RAN.WG1.TS.Slicing-Architecture-R004-v14.01.pdf` |
| WG1 | `O-RAN.WG1.Study-on-O-RAN-Slicing-v02.00` | `ran/slicing/oran_slicing.py` | `adapters/mock_ran/ran/slicing/oran_slicing.py` | `O-RAN.WG1.Study-on-O-RAN-Slicing-v02.00.pdf` |
| WG1 | `O-RAN.WG1.Network-Energy-Savings-Technical-Report-R003-v02.00` | `ran/energy/nes.py` | missing | `O-RAN.WG1.Network-Energy-Savings-Technical-Report-R003-v02.00.pdf` |
| WG1 | `O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00` | `ran/energy/nes.py` | missing | `O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00.pdf` |
| WG2 | `O-RAN.WG2.TS.Non-RT-RIC-ARCH-R004-v07.00` | `ran/ric/non_rt_ric.py` | `adapters/mock_ran/ran/ric/non_rt_ric.py` | `O-RAN.WG2.TS.Non-RT-RIC-ARCH-R004-v07.00.docx` |
| WG2 | `O-RAN.WG2.TS.A1AP-R005-v06.00` | `ran/ric/a1_interface.py` | missing | `O-RAN.WG2.TS.A1AP-R005-v06.00.pdf` |
| WG2 | `O-RAN.WG2.TS.A1TD-R005-v11.01` | `ran/ric/non_rt_ric.py` | `adapters/mock_ran/ran/ric/non_rt_ric.py` | `O-RAN.WG2.TS.A1TD-R005-v11.01.pdf` |
| WG2 | `O-RAN.WG2.TS.R1AP-R005-v10.00` | `smo/r1.py` | missing | `O-RAN.WG2.TS.R1AP-R005-v10.00.pdf` |
| WG2 | `O-RAN.WG2.TS.R1GAP-R005-v13.00` | `smo/r1.py` | missing | `O-RAN.WG2.TS.R1GAP-R005-v13.00.pdf` |
| WG2 | `O-RAN.WG2.AIML-v01.03` | `smo/aiml.py` | missing | `O-RAN.WG2.AIML-v01.03.pdf` |
| WG3 | `O-RAN.WG3.TS.E2AP-R004-v08.00` | `ran/ric/e2ap.py` | `adapters/mock_ran/ran/ric/e2ap.py` | `O-RAN.WG3.TS.E2AP-R004-v08.00.docx` |
| WG3 | `O-RAN.WG3.TS.E2GAP-R004-v08.00` | `ran/ric/near_rt_ric.py` | `adapters/mock_ran/ran/ric/near_rt_ric.py` | `O-RAN.WG3.TS.E2GAP-R004-v08.00.docx` |
| WG3 | `O-RAN.WG3.TS.RICARCH-R005-v08.00` | `ran/ric/near_rt_ric.py` | `adapters/mock_ran/ran/ric/near_rt_ric.py` | `O-RAN.WG3.TS.RICARCH-R005-v08.00.docx` |
| WG3 | `O-RAN.WG3.TS.E2SM-KPM-R004-v07.00` | `ran/ric/e2ap.py` | `adapters/mock_ran/ran/ric/e2ap.py` | `O-RAN.WG3.TS.E2SM-KPM-R004-v07.00.docx` |
| WG3 | `O-RAN.WG3.TS.E2SM-RC-R004-v09.00` | `ran/ric/e2ap.py` | `adapters/mock_ran/ran/ric/e2ap.py` | `O-RAN.WG3.TS.E2SM-RC-R004-v09.00.pdf` |
| WG3 | `O-RAN.WG3.TS.E2SM-CCC-R004-v06.00` | `ran/ric/e2sm_ccc.py` | `adapters/mock_ran/ran/ric/e2sm_ccc.py` | `O-RAN.WG3.TS.E2SM-CCC-R004-v06.00.pdf` |
| WG3 | `ORAN-WG3.E2SM-NI-v01.00` | `ran/ric/e2sm_ni.py` | `adapters/mock_ran/ran/ric/e2sm_ni.py` | `ORAN-WG3.E2SM-NI-v01.00.pdf` |
| WG3 | `O-RAN.WG3.TS.E2SM-LLC-R004-v01.00` | `ran/ric/e2sm_llc.py` | `adapters/mock_ran/ran/ric/e2sm_llc.py` | `O-RAN.WG3.TS.E2SM-LLC-R004-v01.00.pdf` |
| WG3 | `O-RAN.WG3.TS.Y1AP-R005-v01.02` | `ran/ric/y1.py` | missing | `O-RAN.WG3.TS.Y1AP-R005-v01.02.docx` |
| WG3 | `O-RAN.WG3.TS.Y1GAP-R005-v01.02` | `ran/ric/y1.py` | missing | `O-RAN.WG3.TS.Y1GAP-R005-v01.02.docx` |
| WG4 | `O-RAN.WG4.TS.CUS.0-R005-v20.00` | `ran/fronthaul/cus_plane.py` | `adapters/mock_ran/ran/fronthaul/cus_plane.py` | `O-RAN.WG4.TS.CUS.0-R005-v20.00.docx` |
| WG4 | `O-RAN.WG4.TS.MP.0-R005-v20.00` | `ran/fronthaul/m_plane.py` | missing | `O-RAN.WG4.TS.MP.0-R005-v20.00.docx` |
| WG4 | `O-RAN.WG4.TS.CONF.0-R005-v15.00` | `ran/fronthaul/o_ru.py` | missing | `O-RAN.WG4.TS.CONF.0-R005-v15.00.docx` |
| WG4 | `O-RAN.WG4.CTI-TMP.0-R003-v04.00` | `ran/fronthaul/cus_plane.py` | `adapters/mock_ran/ran/fronthaul/cus_plane.py` | `O-RAN.WG4.CTI-TMP.0-R003-v04.00.pdf` |
| WG6 | `O-RAN.WG6.TS.O2IMS-INTERFACE-R005-v11.00` | `etsi/o2/o2_ims.py` | missing | `O-RAN.WG6.TS.O2IMS-INTERFACE-R005-v11.00.pdf` |
| WG6 | `O-RAN.WG6.TS.O2DMS-INTERFACE-K8S-PROFILE-R005-v07.00` | `etsi/o2/o2_dms.py` | missing | missing |
| WG6 | `O-RAN.WG6.O-Cloud Notification API-v04.00` | `etsi/o2/o_cloud_notification.py` | missing | `O-RAN.WG6.O-Cloud Notification API-v04.00.docx` |
| WG6 | `O-RAN.WG6.CADS-v08.01` | `etsi/o2/o2_ims.py` | missing | `O-RAN.WG6.CADS-v08.01.pdf` |
| WG6 | `O-RAN.WG6.ASD-R004-v02.00` | `etsi/o2/o2_dms.py` | missing | `O-RAN.WG6.ASD-R004-v02.00.pdf` |
| WG9 | `O-RAN.WG9.XTRP-MGT.0-R004-v10.00` | `transport/xhaul.py` | missing | `O-RAN.WG9.XTRP-MGT.0-R004-v10.00.pdf` |
| WG9 | `O-RAN.WG9.XTRP-SYN.0-R004-v07.00` | `transport/xhaul.py` | missing | `O-RAN.WG9.XTRP-SYN.0-R004-v07.00.pdf` |
| WG9 | `O-RAN.WG9.XPSAAS.0-R005-v10.00` | `transport/xhaul.py` | missing | `O-RAN.WG9.XPSAAS.0-R005-v10.00.pdf` |
| WG10 | `O-RAN.WG10.TS.O1-Interface.0-R005-v18.00` | `oam/o1.py` | missing | `O-RAN.WG10.TS.O1-Interface.0-R005-v18.00.pdf` |
| WG10 | `O-RAN.WG10.TS.O1NRM.0-R004-v04.00` | `oam/o1.py` | missing | `O-RAN.WG10.TS.O1NRM.0-R004-v04.00.pdf` |
| WG10 | `O-RAN.WG10.TS.O1PMeas-R005-v05.00` | `oam/pm.py` | missing | `O-RAN.WG10.TS.O1PMeas-R005-v05.00.pdf` |
| WG10 | `O-RAN.WG10.TS.OAM-Architecture-R005-v17.00` | `oam/o1.py` | missing | `O-RAN.WG10.TS.OAM-Architecture-R005-v17.00.pdf` |
| WG10 | `O-RAN.WG10.TS.TE&IV-API.0-R005-v04.00` | `oam/teiv.py` | missing | `O-RAN.WG10.TS.TE&IV-API.0-R005-v04.00.pdf` |
| WG10 | `O-RAN.WG10.TS.TE&IV-DM.0-R005-v04.00` | `oam/teiv.py` | missing | `O-RAN.WG10.TS.TE&IV-DM.0-R005-v04.00.pdf` |
| WG11 | `O-RAN.WG11.TS.SecProtSpec.0-R005-v14.00` | `security/security_service.py` | missing | `O-RAN.WG11.TS.SecProtSpec.0-R005-v14.00.docx` |
| WG11 | `O-RAN.WG11.TS.SRCS.0-R005-v14.00` | `security/security_service.py` | missing | `O-RAN.WG11.TS.SRCS.0-R005-v14.00.docx` |
| WG11 | `O-RAN.WG11.TS.STS-R005-v12.00` | `test_oran_compliance.py` | missing | `O-RAN.WG11.TS.STS-R005-v12.00.docx` |
| WG11 | `O-RAN.WG11.TR.ZTA-R005-v05.00` | `security/zero_trust.py` | missing | `O-RAN.WG11.TR.ZTA-R005-v05.00.docx` |
| WG11 | `O-RAN.WG11.TR.Threat-Modeling-R005-v08.00` | `security/zero_trust.py` | missing | `O-RAN.WG11.TR.Threat-Modeling-R005-v08.00.docx` |
| WG11 | `O-RAN.WG11.TR.Certficate-Management-Framework.0-R005-v06.00` | `security/cert_manager.py` | missing | `O-RAN.WG11.TR.Certficate-Management-Framework.0-R005-v06.00.docx` |
| WG11 | `O-RAN.WG11.TR.OAuth2.0-Security.0-R005-v07.00` | `security/security_service.py` | missing | `O-RAN.WG11.TR.OAuth2.0-Security.0-R005-v07.00.docx` |
| WG11 | `O-RAN.WG11.TR.PQC-Security.0-R005-v02.00` | `security/pqc.py` | missing | `O-RAN.WG11.TR.PQC-Security.0-R005-v02.00.docx` |
