#!/usr/bin/env python3
"""Patch ``GoldRenewalCsvPath`` in the PBIR semantic model from env or repo-local gold CSV.

Reads ``GOLD_RENEWAL_CSV_ABSOLUTE_PATH`` when set; otherwise ``<repo>/data/gold/gold_renewal_scores.csv``.
Run after scoring locally or download from Databricks before opening Power BI Desktop.

Usage:
  python scripts/update_pbip_gold_csv_path.py
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

try:
    from repo_dotenv import load_repo_dotenv
except ImportError:

    def load_repo_dotenv() -> None:
        return


def main() -> int:
    load_repo_dotenv()
    root = Path(__file__).resolve().parents[1]
    tmdl = root / "powerbi" / "CoreSpacesRenewal.SemanticModel" / "definition" / "expressions.tmdl"
    if not tmdl.is_file():
        print(f"Missing {tmdl}", file=sys.stderr)
        return 1

    raw = os.environ.get("GOLD_RENEWAL_CSV_ABSOLUTE_PATH", "").strip().strip('"').strip("'")
    if raw:
        csv_path = Path(raw)
    else:
        csv_path = root / "data" / "gold" / "gold_renewal_scores.csv"

    posix = csv_path.resolve().as_posix()
    text = tmdl.read_text(encoding="utf-8")
    replacement = (
        f'expression GoldRenewalCsvPath = "{posix}" '
        "meta [IsParameterQuery=true, Type=\"Text\", IsParameterQueryRequired=true]"
    )
    new_text, n = re.subn(
        r"^expression GoldRenewalCsvPath = .*",
        replacement,
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if n != 1:
        print("Could not find GoldRenewalCsvPath expression to patch.", file=sys.stderr)
        return 1
    tmdl.write_text(new_text, encoding="utf-8")
    print(f"Patched GoldRenewalCsvPath -> {posix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
