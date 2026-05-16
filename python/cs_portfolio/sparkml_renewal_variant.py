"""PySpark ML renewal classifier — same features as ``pipeline_def`` (Spark variant).

Use on a Databricks cluster or any Spark session with ``pyspark`` installed.
Mirrors ``databricks/04_sparkml_variant/train_sparkml_renewal.ipynb`` for importable,
obvious JD-facing code (not only notebook cells).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from cs_portfolio.pipeline_def import CAT_COLUMNS, FEATURE_COLUMNS

if TYPE_CHECKING:
    from pyspark.sql import SparkSession


def default_silver_parquet_path() -> str:
    """Resolve silver Parquet: ``PORTFOLIO_BASE_PATH``/silver/... or repo ``data/silver``."""
    repo = Path(os.environ.get("PORTFOLIO_REPO_ROOT", Path(__file__).resolve().parents[2])).resolve()
    base = os.environ.get("PORTFOLIO_BASE_PATH")
    if base:
        return f"{base.rstrip('/')}/silver/lease_episode_features.parquet"
    return str(repo / "data" / "silver" / "lease_episode_features.parquet")


def build_renewal_spark_pipeline():
    """Return an unfitted ``pyspark.ml.Pipeline`` (StringIndexer → OHE → Assembler → LR)."""
    from pyspark.ml import Pipeline
    from pyspark.ml.classification import LogisticRegression
    from pyspark.ml.feature import OneHotEncoder, StringIndexer, VectorAssembler

    if len(CAT_COLUMNS) != 1 or CAT_COLUMNS[0] != "metro":
        raise ValueError("sparkml_renewal_variant expects CAT_COLUMNS == ['metro']")
    metro_col = CAT_COLUMNS[0]
    num_cols = list(FEATURE_COLUMNS)

    metro_indexer = StringIndexer(
        inputCol=metro_col, outputCol="metro_idx", handleInvalid="keep"
    )
    metro_ohe = OneHotEncoder(
        inputCols=["metro_idx"], outputCols=["metro_vec"], dropLast=True
    )
    assembler = VectorAssembler(
        inputCols=num_cols + ["metro_vec"],
        outputCol="features",
        handleInvalid="skip",
    )
    lr = LogisticRegression(
        featuresCol="features",
        labelCol="renewed",
        maxIter=200,
        family="binomial",
        standardization=True,
    )
    return Pipeline(stages=[metro_indexer, metro_ohe, assembler, lr])


def read_silver_for_training(spark: "SparkSession", path: str | None = None):
    """Load silver Parquet, cast numerics + label, optional ``lease_id`` grain."""
    from pyspark.sql import functions as F

    p = path or default_silver_parquet_path()
    raw = spark.read.parquet(p)
    for c in FEATURE_COLUMNS:
        raw = raw.withColumn(c, F.col(c).cast("double"))
    grain = ["lease_id"] if "lease_id" in raw.columns else []
    df = raw.select(*(grain + list(FEATURE_COLUMNS) + ["metro", "renewed"])).dropna(
        subset=["renewed"]
    )
    return df.withColumn("renewed", F.col("renewed").cast("double"))


def train_renewal_sparkml(
    spark: "SparkSession",
    *,
    silver_path: str | None = None,
    train_fraction: float = 0.75,
    seed: int = 42,
) -> tuple[Any, float]:
    """Fit pipeline; return ``(model, test_auroc)``."""
    from pyspark.ml.evaluation import BinaryClassificationEvaluator

    df = read_silver_for_training(spark, silver_path)
    train_df, test_df = df.randomSplit([train_fraction, 1.0 - train_fraction], seed=seed)
    model = build_renewal_spark_pipeline().fit(train_df)
    pred = model.transform(test_df)
    auc = BinaryClassificationEvaluator(
        rawPredictionCol="rawPrediction",
        labelCol="renewed",
        metricName="areaUnderROC",
    ).evaluate(pred)
    return model, float(auc)
