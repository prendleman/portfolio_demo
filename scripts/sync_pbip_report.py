#!/usr/bin/env python3
"""Chain branding → page JSON codegen → structural validation (CLI-friendly CI hook)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "scripts"))
    try:
        from repo_dotenv import load_repo_dotenv
    except ImportError:
        load_repo_dotenv = lambda: None  # noqa: E731
    load_repo_dotenv()

    py = sys.executable

    for argv in (
        [py, str(root / "scripts" / "make_pbip_branding_assets.py")],
        [py, str(root / "scripts" / "gen_pbip_report_pages.py")],
        [py, str(root / "scripts" / "update_pbip_gold_csv_path.py")],
        [py, str(root / "scripts" / "validate_pbip_visuals.py")],
    ):
        proc = subprocess.run(argv, cwd=str(root))
        if proc.returncode != 0:
            return proc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
