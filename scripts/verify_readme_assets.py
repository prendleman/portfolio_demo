#!/usr/bin/env python3
"""Fail if README.md references local images or files that are missing from the repo."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _is_remote(url: str) -> bool:
    u = url.lower()
    return u.startswith("http://") or u.startswith("https://") or u.startswith("//")


def _strip_md_target(raw: str) -> str:
    t = raw.strip()
    if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
        t = t[1:-1]
    if " " in t and not t.startswith("/"):
        t = t.split()[0]
    return t.strip()


def main() -> int:
    root = _repo_root()
    readme = root / "README.md"
    if not readme.is_file():
        print("Missing README.md", file=sys.stderr)
        return 1
    text = readme.read_text(encoding="utf-8")

    missing: list[str] = []

    for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", text):
        target = _strip_md_target(m.group(1))
        if not target or _is_remote(target):
            continue
        path = (root / target).resolve()
        if not path.is_file():
            missing.append(f"markdown image: {target!r} (resolved {path})")

    for m in re.finditer(r'<img[^>]+src="([^"]+)"', text, flags=re.I):
        target = m.group(1).strip()
        if not target or _is_remote(target):
            continue
        path = (root / target).resolve()
        if not path.is_file():
            missing.append(f"HTML img src: {target!r} (resolved {path})")

    if missing:
        print("README asset check failed — missing files:", file=sys.stderr)
        for line in missing:
            print(f"  - {line}", file=sys.stderr)
        return 1
    print("README asset paths OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
