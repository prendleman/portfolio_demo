# Spark ML variant — same renewal model on Spark DataFrames

This folder is a **Databricks-first, production-shaped alternative** to the scikit-learn path in `python/cs_portfolio/train.py` + `pipeline_def.py`. It answers JD asks for **PySpark / Spark ML** explicitly: the same silver grain (`lease_episode_features.parquet`), same feature columns + `metro` one-hot, **binary renewal** label (`renewed`), trained as a **`pyspark.ml` Pipeline** (StringIndexer → OneHotEncoder → VectorAssembler → LogisticRegression).

## When to use which path

| Path | Best for |
| --- | --- |
| **sklearn + pandas** (`02_train_renewal_model`, local `run_local_pipeline.py`) | Fast iteration, MLflow sklearn flavor, small/medium Parquet on single node |
| **Spark ML** | Notebook [`train_sparkml_renewal.ipynb`](train_sparkml_renewal.ipynb); **JD-path script** [`../02b_train_sparkml_variant/train_sparkml_renewal.py`](../02b_train_sparkml_variant/train_sparkml_renewal.py); shared [`python/cs_portfolio/sparkml_renewal_variant.py`](../../python/cs_portfolio/sparkml_renewal_variant.py); CLI [`scripts/sparkml_renewal_variant.py`](../../scripts/sparkml_renewal_variant.py) | Same renewal problem on **Spark DataFrames + `pyspark.ml` Pipeline** |

## Prerequisites

- Silver features exist (`databricks/01_feature_pipeline` or local pipeline).
- Attach a cluster with Spark (DBR includes PySpark).
- Set `PORTFOLIO_REPO_ROOT` if the notebook lives outside the default relative path, and optionally `PORTFOLIO_BASE_PATH` for shared Parquet (same convention as other notebooks).

## Run

Open **`train_sparkml_renewal.ipynb`** in order, **or** run `python scripts/sparkml_renewal_variant.py` after `pip install pyspark` for a driver-local smoke train. Optional tail cells sketch **MLflow** logging for the fitted `PipelineModel` (Spark flavor) — wire your experiment + UC registry when the tenant is ready (see `databricks/docs/PRODUCTIONIZATION_UC_MLFLOW.md`).
