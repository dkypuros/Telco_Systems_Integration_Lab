# Models Manifest

`traceability/standards_release_register.yaml` is authoritative for standards version and tested-against claims.

## Model spaces

- `models/standard_native/3gpp/`: 3GPP-shaped models, schemas, protocol structures, or sidecar spec maps.
- `models/standard_native/tmforum/`: TM Forum Open API/SID-shaped models.
- `models/standard_native/oran/`: O-RAN information models, service-model structures, or interface models.
- `models/canonical/`: normalized lab-internal models.
- `models/mappings/`: transformations between canonical and standard-native models.

## Direction rule

Standard-native models preserve the standard's shape. Canonical models are internal convenience models. Any conversion between them must be recorded in `models/mappings/` and linked from `traceability/`.

## Version rule

No model may be treated as current without a release-register row or explicit `reference_only` label.
