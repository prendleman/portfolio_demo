#!/usr/bin/env python3
"""CLI entry: train Spark ML renewal pipeline on local Spark or Databricks driver.

Requires ``pip install pyspark`` (not in base ``requirements.txt`` — add on demand).

  python scripts/sparkml_renewal_variant.py
  python scripts/sparkml_renewal_variant.py --silver /path/to/lease_episode_features.parquet
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "python"))


def main() -> None:
    try:
        from pyspark.sql import SparkSession
    except ImportError:
        print("Install PySpark: pip install pyspark", file=sys.stderr)
        raise SystemExit(1) from None

    p = argparse.ArgumentParser(description="Train renewal Spark ML pipeline on silver Parquet.")
    p.add_argument(
        "--silver",
        default=None,
        help="Override silver Parquet path (default: env PORTFOLIO_BASE_PATH or repo data/silver).",
    )
    args = p.parse_args()

    from cs_portfolio.sparkml_renewal_variant import (
        default_silver_parquet_path,
        train_renewal_sparkml,
    )

    silver = args.silver or default_silver_parquet_path()
    print("Silver:", silver)

    spark = SparkSession.builder.appName("renewal_sparkml_variant").getOrCreate()
    try:
        model, auc = train_renewal_sparkml(spark, silver_path=silver)
        print(f"Test AUROC: {auc:.4f}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
