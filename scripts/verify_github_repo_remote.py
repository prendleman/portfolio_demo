#!/usr/bin/env python3
"""Compare ``git remote get-url origin`` with ``GIT_REPO_URL`` from ``.env`` (normalized).

Exit 0 if either GIT_REPO_URL is unset (skip) or URLs match after normalization.
Exit 1 on mismatch — avoids accidental pushes to the wrong GitHub repo.

Usage:
  python scripts/verify_github_repo_remote.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    from repo_dotenv import load_repo_dotenv
except ImportError:

    def load_repo_dotenv() -> None:
        return


def _normalize(url: str) -> str:
    u = url.strip().rstrip("/")
    if u.endswith(".git"):
        u = u[:-4]
    if u.startswith("git@"):
        rest = u[4:]
        if ":" not in rest:
            return rest.lower()
        host, path = rest.split(":", 1)
        host = host.lower()
        path = path.strip("/").lower()
        if host == "github.com":
            return f"github:{path}"
        return f"{host}:{path}"
    p = urlparse(u if "://" in u else "https://" + u)
    host = (p.hostname or "").lower()
    path = (p.path or "").strip("/").lower()
    if host == "github.com":
        return f"github:{path}"
    return f"{host}:{path}".lower()


def main() -> int:
    load_repo_dotenv()
    import os

    expected = os.environ.get("GIT_REPO_URL", "").strip()
    if not expected:
        print("verify_github_repo_remote: GIT_REPO_URL unset — skip.")
        return 0

    root = Path(__file__).resolve().parents[1]
    try:
        origin = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            cwd=str(root),
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        print("verify_github_repo_remote: no git remote origin — skip.", file=sys.stderr)
        return 0

    a, b = _normalize(origin), _normalize(expected)
    if a != b:
        print(f"MISMATCH:\n  origin={origin!r}\n  GIT_REPO_URL={expected!r}", file=sys.stderr)
        print(f"Normalized: {a!r} vs {b!r}", file=sys.stderr)
        return 1
    print(f"verify_github_repo_remote: OK ({origin})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
