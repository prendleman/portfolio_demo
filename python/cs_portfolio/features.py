"""Silver feature table at lease-episode grain."""

from __future__ import annotations

import pandas as pd

from cs_portfolio.config import bronze_dir, silver_dir, ensure_dirs


def build_lease_features(fact_lease: pd.DataFrame) -> pd.DataFrame:
    df = fact_lease.copy()
    df["cohort_month"] = df["leased_month"]
    # Simple derived features (all leak-safe relative to as_of_date in synthetic world)
    df["is_long_tenure"] = (df["tenure_months"] >= 15).astype("int8")
    df["high_service_load"] = ((df["work_order_count_12m"] + df["late_payment_count_12m"]) > 4).astype("int8")
    return df


def read_bronze_write_silver() -> str:
    ensure_dirs()
    fact = pd.read_parquet(bronze_dir() / "fact_lease_episode.parquet")
    silver = build_lease_features(fact)

    prop = pd.read_parquet(bronze_dir() / "dim_property.parquet")
    merge_cols = [
        c
        for c in (
            "ecosystem_segment",
            "brand_line",
            "flagship_style",
            "metro_cluster",
            "property_name",
        )
        if c in prop.columns
    ]
    silver = silver.merge(prop[["property_id", *merge_cols]], on="property_id", how="left")
    path = silver_dir() / "lease_episode_features.parquet"
    silver.to_parquet(path, index=False)
    return str(path)
