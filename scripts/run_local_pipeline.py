#!/usr/bin/env python3
"""One-shot local run: bronze → silver → train → gold CSV (pickle-first; MLflow optional)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "python"))
sys.path.insert(0, str(_REPO / "scripts"))

try:
    from repo_dotenv import load_repo_dotenv
except ImportError:
    load_repo_dotenv = lambda: None  # noqa: E731

load_repo_dotenv()

os.environ.setdefault("MLFLOW_TRACKING_URI", str(_REPO.as_uri()).replace("\\", "/") + "/mlruns")

from cs_portfolio.features import read_bronze_write_silver  # noqa: E402
from cs_portfolio.score import score_run  # noqa: E402
from cs_portfolio.synthetic import run_synthetic_to_bronze  # noqa: E402


def main() -> None:
    force_mlflow = os.environ.get("PORTFOLIO_USE_MLFLOW", "").strip().lower() in ("1", "true", "yes")

    print("Generating bronze tables…")
    print(run_synthetic_to_bronze())
    print("Building silver features…")
    print(read_bronze_write_silver())

    if force_mlflow:
        print("Training with MLflow…")
        from cs_portfolio.train import train_and_register

        print(train_and_register())
    else:
        print("Training sklearn + joblib (set PORTFOLIO_USE_MLFLOW=1 for MLflow)…")
        from cs_portfolio.train_pickled import train_and_pickled

        print(train_and_pickled())

    print("Scoring batch…")
    print(score_run())
    print(json.loads((_REPO / "artifacts" / "last_train.json").read_text(encoding="utf-8")))


if __name__ == "__main__":
    main()
