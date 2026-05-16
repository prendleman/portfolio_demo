# Portfolio scope — JD alignment (synthetic demo)

This demo is **synthetic** and **not** affiliated with Core
Spaces, Inc.

It is shaped to mirror an **AI Architect & Engineering
Director**–style brief:

- **Databricks-style** ML lifecycle
- BI consumption
- Governance narrative
- Honest **design intent** where tenant systems are not wired

## Primary outcome (KPI)

**Lease renewal propensity** at the end of a lease episode:

- Binary target `renewed`
- `1` = renewed / signed follow-on lease
- `0` = moved out or did not renew within the modeled window

## Entity grain

**One row per lease episode** at the decision point
(`as_of_date`), keyed by `lease_id`.

Each row links to a property, unit, resident proxy, and cohort
month.

## Success metrics (modeling)

- **ROC-AUC** and **PR-AUC** on a held-out test split
  (stratified).
- **Baseline**: majority-class classifier and a simple rules
  proxy (documented in the training notebook).
- **Calibration note**: scores are `renewal_probability_ml` on
  \[0, 1\] from `predict_proba` (logistic regression).

Optional Platt-style calibration is not required for the demo.

## Secondary analytics (BI)

- **Segment / uplift view**: compare **actual renewal rate** vs
  **average predicted probability** by `metro` and by
  `risk_tier` (deciles of predicted risk).
- **Freshness**: `scored_at`, `dataset_version_id`, and
  `mlflow_run_id` columns are carried into the gold table for
  audit-style reporting.

## Out of scope (explicit)

- Live Yardi / Salesforce / ERP connectivity — see integration
  stubs in
  [`research/integration_architecture.md`](research/integration_architecture.md)
  and the root [`README.md`](README.md).
- **Production** Copilot Studio agents — see
  [`databricks/docs/governance.md`](databricks/docs/governance.md)
  and
  [`research/COPILOT_STUDIO_DESIGN_PATTERN.md`](research/COPILOT_STUDIO_DESIGN_PATTERN.md)
  for grounded-answer **patterns** only (design contract, not a
  deployed agent).
