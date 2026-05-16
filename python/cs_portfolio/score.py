"""Batch score all lease episodes and emit gold table for Power BI."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from cs_portfolio.config import gold_dir, silver_dir, ensure_dirs
from cs_portfolio.mlflow_paths import resolve_mlflow_experiment_name
from cs_portfolio.pipeline_def import FEATURE_COLUMNS, CAT_COLUMNS


def _load_model_from_last_train(art: Path) -> tuple[object, dict[str, object]]:
    lt = art / "last_train.json"
    if not lt.exists():
        raise FileNotFoundError("Run training first (artifacts/last_train.json missing).")

    meta_train = json.loads(lt.read_text(encoding="utf-8"))
    mode = meta_train.get("mode", "mlflow")

    if mode == "pickle":
        model_path = Path(str(meta_train["model_path"]))
        return joblib.load(model_path), meta_train

    import mlflow

    run_id = meta_train.get("run_id")
    if not run_id:
        raise ValueError("last_train.json missing run_id for MLflow mode.")
    model = mlflow.sklearn.load_model(meta_train.get("model_uri") or f"runs:/{run_id}/model")
    return model, meta_train


def _latest_run_fallback() -> str | None:
    try:
        import mlflow

        exp = mlflow.get_experiment_by_name(resolve_mlflow_experiment_name("portfolio_renewal_demo"))
        if exp is None:
            return None
        runs = mlflow.search_runs(
            experiment_ids=[exp.experiment_id],
            order_by=["attributes.start_time DESC"],
            max_results=1,
        )
        if runs.empty:
            return None
        return str(runs.iloc[0]["run_id"])
    except Exception:
        return None


def score_run(*, override_run_id: str | None = None) -> str:
    ensure_dirs()
    repo_root = Path(__file__).resolve().parents[2]
    art = repo_root / "artifacts"
    silver = pd.read_parquet(silver_dir() / "lease_episode_features.parquet")
    X = silver[FEATURE_COLUMNS + CAT_COLUMNS]

    if override_run_id:
        import mlflow

        model = mlflow.sklearn.load_model(f"runs:/{override_run_id}/model")
        meta_train = {"mode": "mlflow", "run_id": override_run_id}
    else:
        model, meta_train = _load_model_from_last_train(art)

    proba = model.predict_proba(X)[:, 1]
    thr = 0.5

    out = silver.copy()
    out["renewal_probability_ml"] = np.round(proba, 5)
    out["predicted_renewed_flag"] = (proba >= thr).astype("int8")
    out["risk_score"] = np.round(1.0 - proba, 5)
    out["risk_tier"] = pd.qcut(
        out["risk_score"].rank(method="first"),
        q=10,
        labels=["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10"],
    ).astype(str)

    if meta_train.get("mode") == "pickle":
        out["mlflow_run_id"] = "n/a-local-pickle"
        out["model_name"] = "renewal_propensity_logreg_joblib"
    else:
        rid = str(meta_train.get("run_id")) or _latest_run_fallback() or ""
        out["mlflow_run_id"] = rid
        out["model_name"] = "renewal_propensity_classifier_mlflow"

    out["scored_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    gdir = gold_dir()
    gdir.mkdir(parents=True, exist_ok=True)
    parquet_path = gdir / "gold_renewal_scores.parquet"
    csv_path = gdir / "gold_renewal_scores.csv"
    out.to_parquet(parquet_path, index=False)
    out.to_csv(csv_path, index=False)

    meta_score = {
        "train_mode": meta_train.get("mode"),
        "mlflow_run_id": None if meta_train.get("mode") == "pickle" else str(meta_train.get("run_id")),
        "rows": int(len(out)),
        "scored_at": out["scored_at"].iloc[0],
        "gold_parquet": str(parquet_path),
        "gold_csv": str(csv_path),
    }
    meta_path = repo_root / "artifacts" / "last_score.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta_score, indent=2), encoding="utf-8")
    return str(csv_path)


def main() -> None:
    print(score_run())


if __name__ == "__main__":
    main()
