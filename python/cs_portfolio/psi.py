"""Population stability index (PSI) helpers for score drift checks."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def population_stability_index(
    baseline: pd.Series, current: pd.Series, *, n_bins: int = 10
) -> float:
    """PSI using quantile bins from baseline only."""
    b = baseline.dropna().to_numpy(dtype=float)
    c = current.dropna().to_numpy(dtype=float)
    if b.size < n_bins * 5 or c.size < n_bins * 5:
        return float("nan")
    edges = np.unique(np.quantile(b, np.linspace(0, 1, n_bins + 1)))
    if edges.size < 3:
        return float("nan")
    exp_counts, _ = np.histogram(b, bins=edges)
    act_counts, _ = np.histogram(c, bins=edges)
    exp = exp_counts / max(b.size, 1)
    act = act_counts / max(c.size, 1)
    eps = 1e-6
    exp = np.clip(exp, eps, 1.0)
    act = np.clip(act, eps, 1.0)
    return float(np.sum((act - exp) * np.log(act / exp)))


def read_score_column(path: Path, column: str) -> pd.Series:
    df = pd.read_parquet(path, columns=[column])
    if column not in df.columns:
        raise ValueError(f"Column {column!r} missing in {path}")
    return pd.to_numeric(df[column], errors="coerce")
