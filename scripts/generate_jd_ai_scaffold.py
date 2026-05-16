#!/usr/bin/env python3
"""Emit JD-aligned AI/integration artifacts (Databricks bundle template, Copilot manifest, App scaffold).

Run after cloning or when metrics vocabulary changes:
  python scripts/generate_jd_ai_scaffold.py

Secrets and workspace hosts stay out of git — template uses env-style placeholders.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def manifest() -> dict[str, Any]:
    """Copilot Studio–style manifest with explicit topic → semantic bindings (demo)."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Copilot grounding manifest (portfolio demo)",
        "description": (
            "Allowlist topics for Microsoft Copilot Studio–style agents. Production answers must resolve to "
            "governed semantic model tables/measures—never ad-hoc CSV chat over untrusted files."
        ),
        "semantic_model_entity": "GoldRenewalScores",
        "allowed_measure_topics": [
            "Renewal_Actual_Rate_by_metro",
            "Renewal_Actual_Rate_by_risk_tier",
            "Avg_Predicted_Renewal_Prob_by_ecosystem_segment",
            "Median_Monthly_Rent_by_metro_cluster",
            "Gold_table_freshness_scored_at",
        ],
        "topic_bindings": [
            {
                "topic_id": "renewal_rate_metro",
                "user_phrases": [
                    "renewal rate by city",
                    "how are we doing in Chicago",
                    "compare renewals across metros",
                ],
                "tabular_binding": {
                    "measure": "Renewal Actual Rate %",
                    "suggested_dimension": "metro",
                    "filter_hints": ["leased_month", "risk_tier"],
                },
                "citation_rule": "Echo active slicers (metro, risk_tier, leased_month) and scored_at max per gold contract.",
            },
            {
                "topic_id": "model_vs_actual_uplift",
                "user_phrases": ["model vs actual renewals", "is the model calibrated", " uplift by decile"],
                "tabular_binding": {
                    "measures": ["Renewal Actual Rate %", "Avg Predicted Renewal Prob"],
                    "suggested_dimension": "risk_tier",
                },
                "citation_rule": "State risk_tier semantics (D1 = lowest modeled churn sensitivity in this demo).",
            },
            {
                "topic_id": "portfolio_freshness",
                "user_phrases": ["when was this scored", "which model version", "dataset version"],
                "tabular_binding": {
                    "columns": ["scored_at", "mlflow_run_id", "dataset_version_id", "model_name"],
                    "aggregate": "MAX(scored_at), DISTINCT dataset_version_id",
                },
                "citation_rule": "Never fabricate lineage; if NULL, say unknown and route to ITSM ticket template.",
            },
        ],
        "refusal_topics": [
            "legal_commitments",
            "undocumented_rent_concessions",
            "individual_resident_PII",
            "unverified_financial_guidance",
            "competitive_market_share_claims_without_cited_source",
        ],
        "required_citations_pattern": (
            "Always state filter context (metro, cohort month, ecosystem segment) and data_as_of timestamp when "
            "discussing metrics."
        ),
        "synthetic_data_banner": (
            "Demo portfolio uses synthetic leases; production copilots must read from authorized lakehouse tables "
            "with RLS/CLS parity to Power BI semantic models."
        ),
        "genai_wedge_placeholder": {
            "pattern": "Retrieve-then-classify on synthetic service tickets",
            "governance_link": "databricks/docs/governance.md",
            "no_pii_banner": True,
        },
    }


def bundle_template() -> str:
    return """
# Copy to repository root as `databricks.yml` after setting `WORKSPACE_HOST` (or override `targets.dev.workspace.host`).
# CLI: databricks bundle validate  |  databricks bundle deploy --target dev
#
# Docs: https://docs.databricks.com/dev-tools/bundles/index.html

bundle:
  name: cs_renewal_portfolio_demo

variables:
  workspace_host:
    description: "Databricks workspace URL, e.g. https://adb-123.4.azuredatabricks.net"
    default: "${WORKSPACE_HOST}"

targets:
  dev:
    mode: development
    default: true
    workspace:
      host: ${var.workspace_host}

resources:
  jobs:
    demo_renewal_train_score:
      name: "[demo] Train renewal then score gold"
      max_concurrent_runs: 1
      job_clusters:
        - job_cluster_key: shared_cluster
          new_cluster:
            spark_version: 15.4.x-scala2.12
            node_type_id: Standard_DS3_v2
            num_workers: 1
      tasks:
        - task_key: train
          job_cluster_key: shared_cluster
          notebook_task:
            notebook_path: ./databricks/02_train_renewal_model/train_mlflow
            base_parameters:
              ENV: "demo"
        - task_key: score
          depends_on:
            - task_key: train
          job_cluster_key: shared_cluster
          notebook_task:
            notebook_path: ./databricks/03_score_batch/score_gold
            base_parameters:
              EXPORT_CSV_FOR_PBIP: "true"
      # Production: split jobs, add UC volumes, queueing, and approval gates — not in this template.
""".strip()


def renewal_lens_app_py() -> str:
    return '''\
"""Renewal Lens — Databricks App / Streamlit surrogate for local dev.

In Databricks: wrap with Databricks Apps deployment; set GOLD_TABLE or mount path.
Locally:  streamlit run app.py
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PARQUET = REPO_ROOT / "data" / "gold" / "gold_renewal_scores.parquet"


@st.cache_data(show_spinner=True)
def load() -> pd.DataFrame:
    raw = os.environ.get("GOLD_PARQUET_PATH", str(DEFAULT_PARQUET))
    path = Path(raw)
    if not path.is_file():
        st.error(f"Gold file not found: {path}")
        st.stop()
    return pd.read_parquet(path)


def main() -> None:
    st.set_page_config(page_title="Renewal Lens", layout="wide")
    st.title("Renewal Lens (synthetic)")
    st.caption(
        "Databricks Apps adjacency: lakehouse consumers who will not live only in Power BI. "
        "Data is synthetic — see SCOPE.md."
    )
    df = load()
    metros = sorted(df["metro"].dropna().unique().tolist()) if "metro" in df.columns else []
    msel = st.multiselect("Metro", metros, default=metros[:3] if len(metros) >= 3 else metros)
    tiered = df if not msel else df[df["metro"].isin(msel)]
    c1, c2, c3 = st.columns(3)
    if "renewed" in tiered.columns:
        c1.metric("Rows", f"{len(tiered):,}")
        c2.metric("Renewal rate %", f"{100 * tiered['renewed'].mean():.2f}")
    if "renewal_probability_ml" in tiered.columns:
        c3.metric("Mean p(renew)", f"{tiered['renewal_probability_ml'].mean():.3f}")
    st.subheader("Risk tier vs model")
    if "risk_tier" in tiered.columns and "renewal_probability_ml" in tiered.columns:
        g = (
            tiered.groupby("risk_tier", dropna=False)["renewal_probability_ml"]
            .mean()
            .sort_index()
            .reset_index()
        )
        st.bar_chart(g.set_index("risk_tier"))
    st.dataframe(tiered.head(200), use_container_width=True)


if __name__ == "__main__":
    main()
'''


def renewal_lens_requirements() -> str:
    return """streamlit>=1.28.0
pandas>=2.1.0
pyarrow>=14.0.0
"""


def renewal_lens_readme() -> str:
    return """# Renewal Lens (Databricks Apps adjacency)

Synthetic Streamlit surface over `data/gold/gold_renewal_scores.parquet`.

## Local

```bash
pip install -r requirements.txt
set GOLD_PARQUET_PATH=..\\..\\..\\data\\gold\\gold_renewal_scores.parquet
streamlit run app.py
```

## Databricks Apps

1. Materialize gold as Delta in UC; point the app environment variable `GOLD_PARQUET_PATH` at a mounted path
   **or** swap `read_parquet` for `spark.table("catalog.schema.gold_renewal_scores").toPandas()` behind a small abstraction.
2. Register the app per workspace documentation; logging/auditing mirrors `databricks/docs/governance.md`.

Programmatic refresh: `python scripts/generate_jd_ai_scaffold.py`
"""


def genai_wedge_md() -> str:
    return """# GenAI wedge sketch — synthetic ticket triage (governed pattern)

_Generated by `scripts/generate_jd_ai_scaffold.py`. Edit narrative; keep disclaimers._

## Intent (JD: traditional ML vs GenAI)

- **Traditional:** renewal propensity + calibrated monitoring (PSI, ROC) — already shown in notebooks.
- **GenAI (small):** retrieve similar historical maintenance tickets (synthetic), propose **category + priority** suggestions; **human-in-the-loop** required before any resident-facing reply.

## Governance controls (must ship with the demo story)

| Control | Implementation sketch |
| --- | --- |
| Source of truth | Ticket store in lakehouse table with `ticket_id`, `hashed_unit_ref`, `labels`, `embedding_version` |
| Grounding | Retrieval only from **approved** corpora; refusal on PII prompts |
| Audit | Log `prompt_hash`, `model_name`, `temperature`, `policy_version` alongside recommendation |
| Evaluation | Offline precision@k on labeled synthetic set; online shadow mode before automation |

## Explicit non-goals

- No resident PII in notebooks committed to git.
- No unsupervised send to SMS/email without workflow tool approval.

## Tie-in to Power BI / Fabric

BI shows **volume, SLA, and suggestion acceptance rate** by property cluster; Copilot topics remain allowlisted per `research/copilot_topics_manifest.json`.
"""


def main() -> None:
    copilot_path = ROOT / "research" / "copilot_topics_manifest.json"
    copilot_path.write_text(json.dumps(manifest(), indent=2), encoding="utf-8")
    print(f"Wrote {copilot_path.relative_to(ROOT)}")

    bundle_path = ROOT / "databricks" / "asset_bundle" / "databricks.template.yml"
    _write_text(bundle_path, bundle_template())
    print(f"Wrote {bundle_path.relative_to(ROOT)}")

    app_dir = ROOT / "databricks" / "apps" / "renewal_lens"
    _write_text(app_dir / "app.py", renewal_lens_app_py())
    _write_text(app_dir / "requirements.txt", renewal_lens_requirements())
    _write_text(app_dir / "README.md", renewal_lens_readme())
    print(f"Wrote {app_dir.relative_to(ROOT)}/ (app + requirements + README)")

    wedge = ROOT / "research" / "genai_ticket_triage_wedge.md"
    _write_text(wedge, genai_wedge_md())
    print(f"Wrote {wedge.relative_to(ROOT)}")
    print("Done.")


if __name__ == "__main__":
    main()
