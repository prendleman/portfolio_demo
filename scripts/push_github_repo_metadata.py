#!/usr/bin/env python3
"""
Set GitHub repo description + topics without the `gh` CLI (stdlib only).

Requires a fine-grained or classic PAT with **Contents: read/write** and **Metadata: read**
(and **Administration: read/write** if your org restricts topic edits).

  set GH_TOKEN=ghp_...   # or pass --token
  python scripts/push_github_repo_metadata.py --owner prendleman --repo portfolio_demo

Dry-run (default):

  python scripts/push_github_repo_metadata.py --dry-run

Env fallbacks: GITHUB_REPOSITORY=owner/name, or GIT_REPO_URL from .env via repo_dotenv.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

_DEFAULT_DESCRIPTION = (
    "Databricks / MLflow / Power BI portfolio demo for real estate renewal prediction, "
    "AI governance, and BI integration."
)
_DEFAULT_TOPICS = [
    "databricks",
    "mlflow",
    "powerbi",
    "fabric",
    "machine-learning",
    "mlops",
    "copilot-studio",
    "real-estate-analytics",
    "ai-governance",
]


def _request(
    method: str,
    url: str,
    *,
    token: str,
    body: dict | None = None,
) -> tuple[int, str]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "portfolio-demo-metadata-script",
        },
    )
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 — fixed GitHub API URLs
            return resp.getcode(), resp.read().decode("utf-8", errors="replace")[:2000]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:4000]


def main() -> None:
    p = argparse.ArgumentParser(description="PATCH GitHub repo description + replace topics.")
    p.add_argument("--owner", default=os.environ.get("GITHUB_REPO_OWNER", "prendleman"))
    p.add_argument("--repo", default=os.environ.get("GITHUB_REPO_NAME", "portfolio_demo"))
    p.add_argument("--token", default="")
    p.add_argument("--description", default=_DEFAULT_DESCRIPTION)
    p.add_argument(
        "--topics",
        default=",".join(_DEFAULT_TOPICS),
        help="Comma-separated topic names (GitHub: lowercase, no spaces).",
    )
    p.add_argument("--dry-run", action="store_true", help="Print actions only (default if no token).")
    args = p.parse_args()

    _repo = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(_repo / "scripts"))
    try:
        from repo_dotenv import load_repo_dotenv

        load_repo_dotenv()
    except ImportError:
        pass

    gh_repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if gh_repo and "/" in gh_repo:
        o, r = gh_repo.split("/", 1)
        args.owner, args.repo = o, r

    token = (args.token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")).strip()
    topics = [t.strip().lower() for t in args.topics.split(",") if t.strip()]
    repo_full = f"{args.owner}/{args.repo}"

    base = f"https://api.github.com/repos/{args.owner}/{args.repo}"
    dry = args.dry_run or not token
    print("Repo:", repo_full)
    print("Description:", args.description[:120] + ("…" if len(args.description) > 120 else ""))
    print("Topics:", ", ".join(topics))
    if dry:
        print("\nDRY-RUN: set GH_TOKEN or GITHUB_TOKEN and omit --dry-run to apply.")
        print(f"  PATCH {base}")
        print(f"  PUT   {base}/topics")
        raise SystemExit(0)

    code, body = _request("PATCH", base, token=token, body={"description": args.description})
    print(f"\nPATCH repo → HTTP {code}")
    if code >= 400:
        print(body, file=sys.stderr)
        raise SystemExit(1)

    code2, body2 = _request("PUT", f"{base}/topics", token=token, body={"names": topics})
    print(f"PUT topics → HTTP {code2}")
    if code2 >= 400:
        print(body2, file=sys.stderr)
        raise SystemExit(1)
    print("Done — refresh github.com/{0}/{1}".format(args.owner, args.repo))


if __name__ == "__main__":
    main()
