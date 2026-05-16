"""Databricks-compatible MLflow experiment names."""

from __future__ import annotations

import os

DEFAULT_EXPERIMENT_BASENAME = "portfolio_renewal_demo"


def resolve_mlflow_experiment_name(name: str | None = None) -> str:
    """Return an experiment id/path suitable for ``mlflow.set_experiment`` / ``get_experiment_by_name``.

    On Databricks, experiment names must be workspace paths (e.g. ``/Shared/my-exp``).
    Locally (no ``DATABRICKS_RUNTIME_VERSION``), a short name is allowed.
    Override anytime with ``MLFLOW_EXPERIMENT_PATH`` (full path).
    """
    n = (name or DEFAULT_EXPERIMENT_BASENAME).strip()
    if not n:
        n = DEFAULT_EXPERIMENT_BASENAME
    if n.startswith("/"):
        return n
    forced = os.environ.get("MLFLOW_EXPERIMENT_PATH", "").strip()
    if forced:
        return forced
    if os.environ.get("DATABRICKS_RUNTIME_VERSION"):
        prefix = os.environ.get("MLFLOW_EXPERIMENT_PREFIX", "/Shared").strip().rstrip("/") or "/Shared"
        return f"{prefix}/{n}"
    return n
