# 02b — Train Spark ML variant (optional)

This folder is an **optional parallel** to the sklearn / MLflow path in `databricks/02_train_model/`.

## When to use it

- You want to demonstrate **Spark MLlib** (`LogisticRegression` on a `VectorAssembler` pipeline) in a notebook that mirrors the sklearn story.
- You are interviewing for roles that emphasize **distributed training** even on small demo data.

## When to skip it

- Your narrative is **MLflow + sklearn + Power BI** end-to-end; the main `02_train_model` notebook is enough.

## Inputs / outputs

| Stage | Location |
| --- | --- |
| Silver features | Written by `01_build_silver` (same as main path) |
| Model artifact | Spark ML pipeline saved via `mlflow.spark.log_model` (if you wire the notebook that way) |
| Downstream scoring | Not automatically wired to `03_score_gold` — that job expects the sklearn artifact today |

## Honest boundary

**Design intent:** show you can swap the estimator without breaking the medallion layout.

**Not claimed:** full Spark ML + sklearn parity in metrics tables without extra engineering.

## Related

- [`../02_train_model/README.md`](../02_train_model/README.md)
- [`../docs/PRODUCTIONIZATION_UC_MLFLOW.md`](../docs/PRODUCTIONIZATION_UC_MLFLOW.md)
