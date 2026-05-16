"""Paths and version constants for the renewal portfolio pipeline."""

from __future__ import annotations

import os
from pathlib import Path

# Repo root (parent of python/)
_REPO = Path(__file__).resolve().parents[2]

DATASET_VERSION_DEFAULT = os.environ.get("DATASET_VERSION_ID", "synthetic-demo-core-intel-v2026-05-16")

# Writable base: override for Databricks, e.g. /dbfs/FileStore/portfolio_demo
BASE_OUTPUT = Path(os.environ.get("PORTFOLIO_BASE_PATH", str(_REPO))).resolve()


def bronze_dir() -> Path:
    return BASE_OUTPUT / "data" / "bronze"


def silver_dir() -> Path:
    return BASE_OUTPUT / "data" / "silver"


def gold_dir() -> Path:
    return BASE_OUTPUT / "data" / "gold"


def ensure_dirs() -> None:
    for p in (bronze_dir(), silver_dir(), gold_dir()):
        p.mkdir(parents=True, exist_ok=True)
