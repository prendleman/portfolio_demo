# Productionization — Unity Catalog, MLflow, and job gates

This document explains how the **Databricks bundle** in this repo
maps to **production patterns**.

It does **not** assume your workspace already has Unity Catalog
(UC) or a Model Registry enabled.

## What this demonstrates

| Concern | Where it shows up | Production note |
| --- | --- | --- |
| Asset bundle | `databricks/asset_bundle/databricks.yml` | Parameterize `dev/prod` targets; use service principals and secret scopes |
| MLflow tracking | Training notebooks log params, metrics, and the model | Point `MLFLOW_TRACKING_URI` at your workspace tracking server |
| Model artifacts | `renewal_lr` logged as sklearn | Register in **MLflow Model Registry** when UC policies allow |
| Batch scoring | `03_score_gold` job | Schedule with **Workflows / Jobs**; pass `dataset_version_id` |
| Monitoring | `04_monitoring` job | Wire alerts to email / Slack / PagerDuty in a real tenant |
| Governance | `databricks/docs/governance.md` | RAI reviews, data contracts, and access control live outside this demo |

## Unity Catalog (UC) — design intent

In a UC-enabled workspace you would typically:

1. Register **catalog.schema.table** locations for bronze, silver,
   and gold.
2. Grant **SELECT** to service principals used by jobs only where
   needed.
3. Use **MLflow Unity Catalog integration** for model registry and
   lineage (workspace version dependent).

This demo uses **relative paths** and generic bundle variables so
it can run in a simple dev workspace.

## MLflow — what is logged today

- **Parameters**: `test_size`, `random_state`, feature list hash
  (if implemented in notebook).
- **Metrics**: ROC-AUC, PR-AUC, baseline comparisons.
- **Artifact**: pickled sklearn `LogisticRegression` pipeline.

## Job DAG mental model

```text
ingest_synthetic → build_silver → train_model → score_gold → monitoring
```

Failures in `monitoring` should be treated as **data-quality
gates** in production (PSI drift, schema mismatch).

## Related files

- [`databricks/asset_bundle/README.md`](../asset_bundle/README.md)
- [`databricks/docs/governance.md`](governance.md)
- [`docs/DEMO_RUNBOOK.md`](../../docs/DEMO_RUNBOOK.md)
