#!/usr/bin/env python3
"""Create a **Databricks Repo** (Git-linked folder) via the Repos API — alternative when the UI clone fails.

Uses the same workspace auth as ``databricks_deploy_demo_job.py`` (``DATABRICKS_HOST``, PAT or profile).

Two separate secrets:

  • **Databricks** PAT → ``DATABRICKS_TOKEN`` (talks to Databricks APIs).
  • **Git** PAT → ``GIT_PERSONAL_ACCESS_TOKEN`` (Databricks stores it as *Git credentials* to clone/pull).

Steps:

  1. (Usually once) Register Git credentials with Databricks:

       python scripts/databricks_create_git_repo.py --register-git-credentials

     Requires ``GIT_CREDENTIAL_PROVIDER`` (e.g. ``gitHub``), ``GIT_PERSONAL_ACCESS_TOKEN``, and typically
     ``GIT_EMAIL``. Values are case-insensitive per provider — see SDK docs.

  2. Create the repo clone:

       python scripts/databricks_create_git_repo.py --dry-run
       python scripts/databricks_create_git_repo.py

Env for create:

  • ``GIT_REPO_URL`` — HTTPS clone URL (e.g. ``https://github.com/org/repo.git``).
  • ``GIT_REPO_PROVIDER`` — e.g. ``gitHub``, ``azureDevOpsServices``, ``gitLab``, ``bitbucketCloud``.
    If omitted, a coarse guess is made from the hostname (GitHub/GitLab/Azure DevOps/Bitbucket Cloud).
  • ``DATABRICKS_REPO_PATH`` — optional full workspace path. If unset, uses
    ``/Repos/{your_databricks_login}/{repo-basename}`` (basename from URL).

Never commit Git or Databricks tokens. ``.env`` is gitignored — copy from ``.env.example``.

API refs: ``POST /api/2.0/repos``, ``POST /api/2.0/git-credentials``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from repo_dotenv import load_repo_dotenv  # noqa: E402


def _infer_git_provider(repo_url: str) -> str | None:
    host = (urlparse(repo_url).hostname or "").lower()
    if "github.com" in host:
        return "gitHub"
    if "gitlab.com" in host:
        return "gitLab"
    if "dev.azure.com" in host or "visualstudio.com" in host:
        return "azureDevOpsServices"
    if "bitbucket.org" in host:
        return "bitbucketCloud"
    return None


def _repo_basename(repo_url: str) -> str:
    path = urlparse(repo_url.rstrip("/")).path.strip("/")
    segment = path.split("/")[-1] if path else "repo"
    return segment[:-4] if segment.endswith(".git") else segment


def _default_repos_path(repo_url: str, user_email: str) -> str:
    folder = user_email.strip()
    name = _repo_basename(repo_url)
    return f"/Repos/{folder}/{name}"


def _register_git_credentials(client) -> int:
    token = os.environ.get("GIT_PERSONAL_ACCESS_TOKEN", "").strip()
    provider = (
        os.environ.get("GIT_CREDENTIAL_PROVIDER")
        or os.environ.get("GIT_REPO_PROVIDER")
        or ""
    ).strip()
    if not provider:
        raise SystemExit(
            "Set GIT_CREDENTIAL_PROVIDER (e.g. gitHub, azureDevOpsServices) for --register-git-credentials."
        )
    if not token:
        raise SystemExit("Set GIT_PERSONAL_ACCESS_TOKEN (Git provider PAT — not the Databricks PAT).")

    git_email = os.environ.get("GIT_EMAIL", "").strip() or None
    git_username = os.environ.get("GIT_USERNAME", "").strip() or None
    name = os.environ.get("GIT_CREDENTIAL_NAME", "").strip() or None

    resp = client.git_credentials.create(
        git_provider=provider,
        personal_access_token=token,
        git_email=git_email,
        git_username=git_username,
        name=name,
        is_default_for_provider=True,
    )
    print(
        "Registered Git credential:",
        json.dumps(resp.as_dict(), indent=2),
    )
    print(
        "You can remove GIT_PERSONAL_ACCESS_TOKEN from .env after this succeeds "
        "(credential is stored server-side)."
    )
    return 0


def _create_repo_payload(repo_url: str, provider: str, path: str) -> dict:
    return {"url": repo_url, "provider": provider, "path": path}


def main() -> int:
    load_repo_dotenv()
    parser = argparse.ArgumentParser(description="Create Databricks Repo via Repos API.")
    parser.add_argument(
        "--register-git-credentials",
        action="store_true",
        help="POST Git PAT to Databricks (git-credentials). Run once before clone if UI/API clone fails.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print POST body only for repo create.")
    parser.add_argument(
        "--list-repos",
        action="store_true",
        help="Print repos visible to your user (paths + URLs).",
    )
    args = parser.parse_args()

    try:
        from databricks.sdk import WorkspaceClient
    except ImportError:
        print("Install: pip install -r requirements-databricks-deploy.txt", file=sys.stderr)
        return 1

    client = WorkspaceClient()

    if args.register_git_credentials:
        return _register_git_credentials(client)

    if args.list_repos:
        rows = []
        for r in client.repos.list():
            rows.append({"path": r.path, "url": r.url, "id": r.id, "branch": r.branch})
        print(json.dumps(rows, indent=2))
        return 0

    repo_url = os.environ.get("GIT_REPO_URL", "").strip()
    if not repo_url:
        raise SystemExit("Set GIT_REPO_URL (HTTPS clone URL).")

    provider = os.environ.get("GIT_REPO_PROVIDER", "").strip()
    if not provider:
        provider = _infer_git_provider(repo_url) or ""
    if not provider:
        raise SystemExit(
            "Set GIT_REPO_PROVIDER (e.g. gitHub). Could not infer from GIT_REPO_URL hostname."
        )

    explicit_path = os.environ.get("DATABRICKS_REPO_PATH", "").strip()
    if explicit_path:
        path = explicit_path.rstrip("/")
    else:
        me = client.current_user.me()
        user_email = (me.user_name or "").strip()
        if not user_email:
            raise SystemExit(
                "Could not read workspace user email for default path; set DATABRICKS_REPO_PATH explicitly."
            )
        path = _default_repos_path(repo_url, user_email)

    body = _create_repo_payload(repo_url, provider, path)

    if args.dry_run:
        print(json.dumps(body, indent=2))
        return 0

    resp = client.repos.create(url=body["url"], provider=body["provider"], path=body["path"])
    print("Created repo:", json.dumps(resp.as_dict(), indent=2))
    print(f"Tip: set DATABRICKS_REPO_WORKSPACE_ROOT={resp.path!r} or DATABRICKS_REPO_REMOTE_MATCH in .env")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
