"""Train renewal model without MLflow (portfolio quick-start / constrained environments)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.model_selection import train_test_split

from cs_portfolio.config import silver_dir, ensure_dirs
from cs_portfolio.pipeline_def import FEATURE_COLUMNS, CAT_COLUMNS, build_pipeline


def train_and_pickled(*, random_seed: int = 42) -> dict[str, object]:
    ensure_dirs()
    df = pd.read_parquet(silver_dir() / "lease_episode_features.parquet")

    X = df[FEATURE_COLUMNS + CAT_COLUMNS]
    y = df["renewed"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=random_seed, stratify=y
    )

    pipe = build_pipeline()
    pipe.fit(X_train, y_train)

    proba = pipe.predict_proba(X_test)[:, 1]
    metrics = {
        "test_roc_auc": float(roc_auc_score(y_test, proba)),
        "test_pr_auc": float(average_precision_score(y_test, proba)),
        "positive_rate": float(y.mean()),
    }

    p_bar = float(y_train.mean())
    baseline_pred = np.full(shape=len(y_test), fill_value=p_bar)
    metrics["baseline_roc_auc"] = float(roc_auc_score(y_test, baseline_pred))
    metrics["baseline_pr_auc"] = float(average_precision_score(y_test, baseline_pred))

    art = Path(__file__).resolve().parents[2] / "artifacts"
    art.mkdir(parents=True, exist_ok=True)

    model_path = art / "renewal_pipeline.joblib"
    joblib.dump(pipe, model_path)

    meta = {
        "mode": "pickle",
        "model_path": str(model_path),
        "metrics": metrics,
        "dataset_version_id": str(df["dataset_version_id"].iloc[0]),
        "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "random_seed": random_seed,
    }
    (art / "last_train.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


if __name__ == "__main__":
    print(train_and_pickled())
