#!/usr/bin/env python3
"""
Concrete monitoring helpers for batch scoring outputs (synthetic demo).

- PSI (population stability index) on a numeric score column between two Parquet files
  (e.g. baseline gold export vs a newer scoring run).
- Schema drift: column set + pyarrow type string comparison.

Usage:
  python scripts/monitoring_psi_schema.py \\
    --baseline data/gold/gold_renewal_scores.parquet \\
    --current data/gold/gold_renewal_scores.parquet \\
    --score-column renewal_probability_ml

Exit code 1 if schema drift is detected or PSI exceeds --psi-threshold.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "python"))

from cs_portfolio.psi import population_stability_index, read_score_column  # noqa: E402


def schema_report(path: Path) -> dict[str, str]:
    schema = pq.read_schema(path)
    return {f.name: str(f.type) for f in schema}


def main() -> None:
    p = argparse.ArgumentParser(description="PSI + schema drift between two Parquet files.")
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--current", type=Path, required=True)
    p.add_argument(
        "--score-column",
        default="renewal_probability_ml",
        help="Numeric column for PSI (e.g. renewal_probability_ml).",
    )
    p.add_argument("--n-bins", type=int, default=10)
    p.add_argument(
        "--psi-threshold",
        type=float,
        default=0.25,
        help="Fail if PSI exceeds this (common rule-of-thumb; tune per policy).",
    )
    p.add_argument(
        "--fail-on-schema-drift",
        action="store_true",
        help="Exit 1 if column names or types differ.",
    )
    p.add_argument(
        "--fail-on-psi",
        action="store_true",
        help="Exit 1 if PSI exceeds --psi-threshold.",
    )
    args = p.parse_args()

    if not args.baseline.is_file() or not args.current.is_file():
        print("ERROR: baseline and current must exist.", file=sys.stderr)
        raise SystemExit(2)

    sb = schema_report(args.baseline)
    sc = schema_report(args.current)
    drift = sb != sc
    print("=== Schema ===")
    if drift:
        only_b = sorted(set(sb) - set(sc))
        only_c = sorted(set(sc) - set(sb))
        type_mismatch = sorted(k for k in set(sb) & set(sc) if sb[k] != sc[k])
        if only_b:
            print("Columns only in baseline:", only_b)
        if only_c:
            print("Columns only in current:", only_c)
        if type_mismatch:
            for k in type_mismatch:
                print(f"Type drift {k}: {sb[k]} -> {sc[k]}")
    else:
        print("No schema drift (names + pyarrow types match).")

    base_s = read_score_column(args.baseline, args.score_column)
    cur_s = read_score_column(args.current, args.score_column)
    psi = population_stability_index(base_s, cur_s, n_bins=args.n_bins)
    print("\n=== PSI ===")
    print(f"Column: {args.score_column}")
    print(f"PSI (baseline vs current): {psi:.6f}" if np.isfinite(psi) else "PSI: nan (insufficient data or bins)")

    code = 0
    if args.fail_on_schema_drift and drift:
        print("\nFAIL: schema drift.", file=sys.stderr)
        code = 1
    if args.fail_on_psi and np.isfinite(psi) and psi > args.psi_threshold:
        print(f"\nFAIL: PSI {psi:.4f} > {args.psi_threshold}.", file=sys.stderr)
        code = 1
    raise SystemExit(code)


if __name__ == "__main__":
    main()
