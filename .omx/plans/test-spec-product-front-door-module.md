# Test Spec: Product Front Door Module

## Unit tests

- Validate `modules/index.json` includes `product-front-door` with a unique port.
- Validate module metadata has dependencies, recommendations, and claim boundary.
- Validate product endpoint returns the basic product and no private paths.
- Validate activation endpoint returns the correlated MVP identifiers.
- Validate timeline includes successful current steps and planned downstream gaps.
- Validate unknown routes/actions return errors and do not execute shell commands.
- Validate rendered HTML embedded JavaScript is syntactically valid when Node is available.

## Integration checks

- Run existing service-order-to-activation evidence integration test.
- Run existing module registry/dashboard tests.
- Confirm the dashboard can report the new module card from registry metadata.

## Safety checks

- `python3 -m py_compile` for touched Python modules.
- `pytest` for relevant module and MVP tests.
- `git diff --check`.
- Public-safe private path, secret, sensitive filename, and raw spec scans before commit.

## Manual smoke

- Start dashboard.
- Activate Product Front Door.
- Open the module.
- Click the fixed activation action.
- Confirm the page shows the MVP timeline and marks O-RAN/O-Cloud as planned gaps.
