"""Renewal Lens — Databricks App / Streamlit surrogate for local dev.

In Databricks: deploy as a Databricks App; prefer ``GOLD_TABLE`` (Unity Catalog / Hive)
or ``GOLD_SQL`` when a SparkSession exists (set ``PORTFOLIO_ALLOW_SPARK_GOLD=1`` locally
to force the Spark path for testing). Otherwise use ``GOLD_PARQUET_PATH`` or the repo
default Parquet under ``data/gold/``.

Locally: ``streamlit run app.py``
"""
from __future__ import annotations

import io
import os
from pathlib import Path

import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PARQUET = REPO_ROOT / "data" / "gold" / "gold_renewal_scores.parquet"

_CSS = """
<style>
    .block-container { padding-top: 1.25rem; max-width: 1180px; }
    div[data-testid="stVerticalBlock"] > div:first-child {
        background: linear-gradient(115deg, #115E59 0%, #1B2333 48%, #3F68EB 100%);
        padding: 1.1rem 1.25rem 1rem 1.25rem;
        border-radius: 12px;
        margin-bottom: 0.75rem;
        box-shadow: 0 10px 28px rgba(17,94,89,0.25);
    }
    div[data-testid="stVerticalBlock"] > div:first-child h1 {
        color: #FAF8F4 !important;
        font-weight: 650 !important;
        letter-spacing: -0.02em;
    }
    div[data-testid="stVerticalBlock"] > div:first-child .stCaption {
        color: #E8E2D9 !important;
        opacity: 0.95;
    }
</style>
"""


def _load_from_spark_table(table: str) -> pd.DataFrame | None:
    """UC / Hive table via active SparkSession (Databricks App / cluster)."""
    try:
        from pyspark.sql import SparkSession

        spark = SparkSession.builder.getOrCreate()
        return spark.table(table).toPandas()
    except Exception:
        return None


def _load_from_spark_sql(sql: str) -> pd.DataFrame | None:
    try:
        from pyspark.sql import SparkSession

        spark = SparkSession.builder.getOrCreate()
        return spark.sql(sql).toPandas()
    except Exception:
        return None


@st.cache_data(show_spinner=True)
def load() -> pd.DataFrame:
    spark_gold_enabled = bool(os.environ.get("DATABRICKS_RUNTIME_VERSION")) or os.environ.get(
        "PORTFOLIO_ALLOW_SPARK_GOLD", ""
    ).strip().lower() in ("1", "true", "yes")

    gold_table = os.environ.get("GOLD_TABLE", "").strip()
    if gold_table and spark_gold_enabled:
        df = _load_from_spark_table(gold_table)
        if df is not None and len(df) > 0:
            return df
        if gold_table:
            st.warning(
                f"GOLD_TABLE={gold_table!r} did not return rows via Spark; falling back to Parquet."
            )

    gold_sql = os.environ.get("GOLD_SQL", "").strip()
    if gold_sql and spark_gold_enabled:
        df = _load_from_spark_sql(gold_sql)
        if df is not None and len(df) > 0:
            return df
        if gold_sql:
            st.warning("GOLD_SQL did not return rows via Spark; falling back to Parquet.")

    raw = os.environ.get("GOLD_PARQUET_PATH", str(DEFAULT_PARQUET))
    path = Path(raw)
    if not path.is_file():
        st.error(
            f"Gold file not found: {path}. "
            "Set GOLD_PARQUET_PATH, or GOLD_TABLE / GOLD_SQL on a Databricks Spark runtime."
        )
        st.stop()
    return pd.read_parquet(path)


def main() -> None:
    st.set_page_config(page_title="Renewal Lens", layout="wide", initial_sidebar_state="collapsed")
    st.markdown(_CSS, unsafe_allow_html=True)
    st.title("Renewal Lens")

    spark_gold = bool(os.environ.get("DATABRICKS_RUNTIME_VERSION")) or os.environ.get(
        "PORTFOLIO_ALLOW_SPARK_GOLD", ""
    ).strip().lower() in ("1", "true", "yes")
    _gt = os.environ.get("GOLD_TABLE", "").strip()
    _gsql = os.environ.get("GOLD_SQL", "").strip()
    if (_gt or _gsql) and not spark_gold:
        st.info(
            "**GOLD_TABLE** / **GOLD_SQL** are set, but the Spark read path is off locally "
            "(no `DATABRICKS_RUNTIME_VERSION` and `PORTFOLIO_ALLOW_SPARK_GOLD` is not true). "
            "Using **Parquet** (`GOLD_PARQUET_PATH` / default). On a Databricks App or cluster, Spark is on by default. "
            "See `databricks/apps/renewal_lens/README.md`."
        )

    st.caption(
        "Databricks Apps adjacency — default **Parquet** (`GOLD_PARQUET_PATH` / `data/gold/`). "
        "On cluster/App set **GOLD_TABLE** (e.g. `main.demo.gold_renewal_scores`) or **GOLD_SQL** when Spark is available. "
        "Synthetic leases — see SCOPE.md and docs/DEMO_RUNBOOK.md."
    )

    df = load()

    metros = sorted(df["metro"].dropna().unique().tolist()) if "metro" in df.columns else []
    default_sel = metros[: min(5, len(metros))] if metros else []

    tab_ov, tab_tier, tab_raw = st.tabs(["Overview", "Tier ladder", "Export"])

    with tab_ov:
        msel = st.multiselect("Metro focus", metros, default=default_sel)
        tiered = df if not msel else df[df["metro"].isin(msel)]
        c1, c2, c3, c4 = st.columns(4)
        if "renewed" in tiered.columns:
            c1.metric("Rows", f"{len(tiered):,}")
            c2.metric("Renewal rate %", f"{100 * tiered['renewed'].mean():.2f}")
        if "renewal_probability_ml" in tiered.columns:
            c3.metric("Mean p(renew)", f"{tiered['renewal_probability_ml'].mean():.3f}")
        if "risk_score" in tiered.columns:
            c4.metric("Mean risk score", f"{tiered['risk_score'].mean():.3f}")

        if "ecosystem_segment" in tiered.columns and "renewal_probability_ml" in tiered.columns:
            st.subheader("Probability by ecosystem lane")
            seg = (
                tiered.groupby("ecosystem_segment", dropna=False)["renewal_probability_ml"]
                .mean()
                .sort_values(ascending=False)
                .reset_index()
            )
            st.bar_chart(seg.set_index("ecosystem_segment"))

    with tab_tier:
        if "risk_tier" in df.columns and "renewal_probability_ml" in df.columns:
            st.subheader("Mean modeled probability by risk decile")
            g = (
                df.groupby("risk_tier", dropna=False)["renewal_probability_ml"]
                .mean()
                .sort_index()
                .reset_index()
            )
            st.bar_chart(g.set_index("risk_tier"))
            st.caption("D10 = highest modeled churn sensitivity in this synthetic ladder.")
        else:
            st.info("risk_tier column missing — rerun scoring.")

    with tab_raw:
        st.dataframe(df.head(400), use_container_width=True, height=420)
        buf = io.BytesIO()
        df.head(5000).to_csv(buf, index=False)
        buf.seek(0)
        st.download_button(
            label="Download CSV preview (first 5k rows)",
            data=buf,
            file_name="renewal_lens_preview.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
