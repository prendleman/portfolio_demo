#!/usr/bin/env python3
"""PSI check on ``renewal_probability_ml`` (or another score column) — runnable monitoring artifact.

Defaults compare a baseline Parquet to a current Parquet relative to the repo root.

  python monitoring/psi_check.py
  python monitoring/psi_check.py data/gold/a.parquet data/gold/b.parquet

For schema + thresholds use ``scripts/monitoring_psi_schema.py``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "python"))

from cs_portfolio.psi import population_stability_index, read_score_column  # noqa: E402


def main() -> None:
    root = _REPO
    default = root / "data" / "gold" / "gold_renewal_scores.parquet"
    p = argparse.ArgumentParser(description="PSI between two scored Parquet files.")
    p.add_argument("baseline", nargs="?", type=Path, default=default)
    p.add_argument("current", nargs="?", type=Path, default=default)
    p.add_argument("--column", default="renewal_probability_ml")
    p.add_argument("--n-bins", type=int, default=10)
    args = p.parse_args()

    for path in (args.baseline, args.current):
        if not path.is_file():
            print(f"Missing file: {path} (run scripts/run_local_pipeline.py first)", file=sys.stderr)
            raise SystemExit(2)

    b = read_score_column(args.baseline, args.column)
    c = read_score_column(args.current, args.column)
    psi = population_stability_index(b, c, n_bins=args.n_bins)
    print(f"baseline: {args.baseline}")
    print(f"current:  {args.current}")
    print(f"column:   {args.column}")
    print(f"PSI:      {psi:.6f}")


if __name__ == "__main__":
    main()
