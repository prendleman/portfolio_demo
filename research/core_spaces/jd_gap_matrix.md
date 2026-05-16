# JD ↔ portfolio demo — evidence matrix

Synthetic mapping for interview walkthroughs.

Not affiliated with Core Spaces, Inc.

## Legend

| Column | Meaning |
| --- | --- |
| JD theme | Clustered requirement area |
| Evidence in repo | Where to click in GitHub |
| Gap / follow-up | Honest boundary |

## Matrix

| JD theme | Evidence in repo | Gap / follow-up |
| --- | --- | --- |
| Hands-on Databricks | `databricks/` bundle YAML, notebooks `01`–`04`, `docs/DEMO_RUNBOOK.md` | UC + registry wiring is tenant-specific |
| MLflow lifecycle | `02_train_model.ipynb` logging; `databricks/docs/PRODUCTIONIZATION_UC_MLFLOW.md` | Promotion jobs and approval gates not automated here |
| Power BI / Fabric | `powerbi/CoreSpacesRenewal.Report/` PBIP; `scripts/sync_pbip_semantic_model.py` | No workspace publish from CI |
| Monitoring / drift | `04_monitoring.ipynb`; PSI + schema checks | Alert routing is a design stub |
| Copilot Studio | `research/COPILOT_STUDIO_DESIGN_PATTERN.md` | **Pattern only** — no deployed agent |
| AI governance | `databricks/docs/governance.md`; `SCOPE.md` out-of-scope | Full RAI committee process not simulated |
| Leadership narrative | Root `README.md` Mermaid + “implemented vs intent” | Numbers are illustrative |

## Deep links (quick paste for screen share)

- [`../README.md`](../README.md)
- [`../databricks/asset_bundle/databricks.yml`](../databricks/asset_bundle/databricks.yml)
- [`../research/COPILOT_STUDIO_DESIGN_PATTERN.md`](../research/COPILOT_STUDIO_DESIGN_PATTERN.md)
