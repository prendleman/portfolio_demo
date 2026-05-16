"""Train renewal propensity — **sklearn + MLflow** path (pandas / single-node).

For **PySpark / Spark ML** on the same silver features and label, use
``cs_portfolio.sparkml_renewal_variant`` or run ``databricks/02b_train_sparkml_variant/train_sparkml_renewal.py``
on a Spark cluster (JD-facing Databricks ML path).

**Model registry:** ``mlflow.sklearn.log_model(..., registered_model_name=…)`` is set from env
``REGISTER_MODEL_NAME`` or ``MLFLOW_REGISTER_MODEL_NAME`` when non-empty; otherwise the name is
``None`` and only the run artifact is stored (typical for local ``file:`` tracking).
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, accuracy_score, brier_score_loss
from sklearn.model_selection import train_test_split

from cs_portfolio.config import gold_dir, silver_dir, ensure_dirs
from cs_portfolio.mlflow_paths import resolve_mlflow_experiment_name
from cs_portfolio.pipeline_def import FEATURE_COLUMNS, CAT_COLUMNS, build_pipeline


def train_and_register(*, experiment_name: str = "portfolio_renewal_demo", random_seed: int = 42) -> dict[str, object]:
    df = pd.read_parquet(silver_dir() / "lease_episode_features.parquet")

    mlflow.set_experiment(resolve_mlflow_experiment_name(experiment_name))
    with mlflow.start_run(run_name=f"train_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}"):
        X = df[FEATURE_COLUMNS + CAT_COLUMNS]
        y = df["renewed"].astype(int)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=random_seed, stratify=y
        )

        pipe = build_pipeline()
        pipe.fit(X_train, y_train)

        proba = pipe.predict_proba(X_test)[:, 1]
        pred = (proba >= 0.5).astype(int)

        metrics = {
            "test_roc_auc": float(roc_auc_score(y_test, proba)),
            "test_pr_auc": float(average_precision_score(y_test, proba)),
            "test_accuracy": float(accuracy_score(y_test, pred)),
            "test_brier": float(brier_score_loss(y_test, proba)),
            "positive_rate": float(y.mean()),
        }

        mlflow.log_params(
            {
                "random_seed": random_seed,
                "features": ",".join(FEATURE_COLUMNS + CAT_COLUMNS),
                "dataset_version_id": str(df["dataset_version_id"].iloc[0]),
            }
        )
        mlflow.log_metrics(metrics)

        p_bar = float(y_train.mean())
        baseline_pred = np.full(shape=len(y_test), fill_value=p_bar)
        mlflow.log_metric("baseline_roc_auc", float(roc_auc_score(y_test, baseline_pred)))
        mlflow.log_metric("baseline_pr_auc", float(average_precision_score(y_test, baseline_pred)))

        from mlflow.models import infer_signature

        sample_X = X_train.head(10)
        sample_pred = pipe.predict_proba(sample_X)[:, 1]
        signature = infer_signature(sample_X, sample_pred)

        register_name = (
            os.environ.get("REGISTER_MODEL_NAME", os.environ.get("MLFLOW_REGISTER_MODEL_NAME", "")).strip()
            or None
        )
        mlflow.log_param("register_model_name", register_name or "none")
        # Registry: registered_model_name is None unless REGISTER_MODEL_NAME / MLFLOW_REGISTER_MODEL_NAME is set.
        info = mlflow.sklearn.log_model(
            pipe,
            artifact_path="model",
            signature=signature,
            registered_model_name=register_name,
        )
        model_uri = info.model_uri

        run_id = mlflow.active_run().info.run_id

        meta_path = Path(__file__).resolve().parents[2] / "artifacts" / "last_train.json"
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta_payload = {
            "mode": "mlflow",
            "run_id": run_id,
            "model_uri": model_uri,
            "metrics": metrics,
            "dataset_version_id": str(df["dataset_version_id"].iloc[0]),
            "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "random_seed": random_seed,
            "register_model_name": register_name,
        }
        meta_path.write_text(json.dumps(meta_payload, indent=2), encoding="utf-8")

        return {
            "run_id": run_id,
            "metrics": metrics,
            "model_uri": model_uri,
            "register_model_name": register_name,
        }


def main() -> None:
    ensure_dirs()
    gold_dir().mkdir(parents=True, exist_ok=True)
    out = train_and_register()
    print(out)


if __name__ == "__main__":
    main()
