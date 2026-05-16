# Databricks: run as a Python task or `%run ./train_sparkml_renewal` from a notebook on a Spark cluster.
"""
Compact Spark ML renewal trainer — same features/label as the sklearn path.

- Reads silver ``lease_episode_features.parquet`` (``PORTFOLIO_BASE_PATH`` or repo ``data/silver``).
- Fits ``pyspark.ml`` Pipeline: StringIndexer → OneHotEncoder → VectorAssembler → LogisticRegression.
- Prints test AUROC. Extend with ``mlflow.spark.log_model`` when your experiment is wired.

Requires PySpark (included on Databricks runtimes). For local smoke: ``pip install pyspark``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> None:
    repo = _repo_root()
    os.environ.setdefault("PORTFOLIO_REPO_ROOT", str(repo))
    sys.path.insert(0, str(repo / "python"))

    try:
        from pyspark.sql import SparkSession
    except ImportError as e:
        raise SystemExit(
            "PySpark is required. On Databricks use a Spark cluster; locally: pip install pyspark"
        ) from e

    from cs_portfolio.sparkml_renewal_variant import default_silver_parquet_path, train_renewal_sparkml

    silver = default_silver_parquet_path()
    print("Silver path:", silver)

    spark = SparkSession.builder.appName("train_sparkml_renewal_02b").getOrCreate()
    try:
        model, auc = train_renewal_sparkml(spark, silver_path=silver)
        print(f"Test AUROC: {auc:.4f}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
