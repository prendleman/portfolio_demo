#!/usr/bin/env python3
"""Create (or reset) the demo renewal pipeline job via Databricks Jobs API — same intent as Asset Bundles CLI.

Uses the official **Databricks SDK for Python**, which wraps the Workspace REST APIs:
  https://docs.databricks.com/api/workspace/jobs/create

• Repo-root **``.env``** (optional): copy ``.env.example`` → ``.env`` for local secrets and paths; loaded automatically by deploy/sync/report scripts when ``python-dotenv`` is installed.

Auth (pick one — never commit secrets):
  • Env: ``DATABRICKS_HOST``, ``DATABRICKS_TOKEN`` (PAT)
  • Or Azure CLI / OAuth via ``databricks auth login`` then default WorkspaceClient chain
  • Or ``~/.databrickscfg`` profile + ``DATABRICKS_CONFIG_PROFILE``

Notebook paths must be **workspace paths** (e.g. ``/Repos/you@corp/portfolio-core-spaces-demo/databricks/02_train_renewal_model/train_mlflow``).

Instead of typing both paths, you can set **one** repo root and optional suffix overrides:

  • ``DATABRICKS_REPO_WORKSPACE_ROOT`` — Git folder root from Repos (no API lookup).
  • ``DATABRICKS_REPO_REMOTE_MATCH`` — substring of the repo remote URL **or** workspace path; with auth,
    the script calls the Repos API and fills in the root (useful after cloning).

Explicit ``NOTEBOOK_TRAIN_PATH`` / ``NOTEBOOK_SCORE_PATH`` still override per task when set.

Examples:
  pip install -r requirements-databricks-deploy.txt
  set DATABRICKS_HOST=https://adb-xxxx.x.azuredatabricks.net
  set DATABRICKS_TOKEN=***
  set NOTEBOOK_TRAIN_PATH=/Repos/me/demo/databricks/02_train_renewal_model/train_mlflow
  set NOTEBOOK_SCORE_PATH=/Repos/me/demo/databricks/03_score_batch/score_gold
  python scripts/databricks_deploy_demo_job.py --dry-run
  python scripts/databricks_deploy_demo_job.py

Serverless-only workspaces reject ``job_clusters`` / classic compute. Use:

  set DATABRICKS_USE_SERVERLESS=1
  python scripts/databricks_deploy_demo_job.py --dry-run
  python scripts/databricks_deploy_demo_job.py

Or pass ``--serverless``. Notebook tasks then run on serverless compute (no cluster spec); optional
``DATABRICKS_SERVERLESS_ENV_VERSION`` / ``DATABRICKS_SERVERLESS_DEPENDENCIES`` define a job ``environments``
block if you do not rely on each notebook's saved environment.

Update existing job (use the same classic vs serverless flags as create):
  set DEMO_JOB_ID=123456789012345
  python scripts/databricks_deploy_demo_job.py --reset --serverless

Optional **schedule** (Quartz cron — see Databricks Jobs scheduler docs):

  set DATABRICKS_JOB_SCHEDULE_QUARTZ=0 0 14 * * ?
  set DATABRICKS_JOB_SCHEDULE_TIMEZONE=America/New_York
  python scripts/databricks_deploy_demo_job.py --reset --serverless

Pause initially with ``DATABRICKS_JOB_SCHEDULE_PAUSED=1``. Omit ``DATABRICKS_JOB_SCHEDULE_QUARTZ`` for on-demand only.

Optional **gold CSV workspace copy** for Power BI Import (score task picks up ``gold_csv_workspace_export``):

  set DATABRICKS_GOLD_CSV_WORKSPACE_EXPORT=/Workspace/Users/you@corp/gold_renewal_scores.csv
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from repo_dotenv import load_repo_dotenv  # noqa: E402

# Default notebook paths relative to the Git folder root (matches Asset Bundle layout).
_DEFAULT_TRAIN_REL = "databricks/02_train_renewal_model/train_mlflow"
_DEFAULT_SCORE_REL = "databricks/03_score_batch/score_gold"


def _env_truthy(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _parse_dependencies_list(raw: str) -> list[str]:
    """Split newline- or comma-separated pip lines from env (e.g. DATABRICKS_SERVERLESS_DEPENDENCIES)."""
    if not raw.strip():
        return []
    lines: list[str] = []
    for part in raw.replace(",", "\n").splitlines():
        s = part.strip()
        if s:
            lines.append(s)
    return lines


def _repo_root_from_remote_match(client, substring: str) -> str:
    """Pick workspace repo root via Repos API (``substring`` matches remote URL or folder path)."""
    needle = substring.lower()
    hits = []
    for repo in client.repos.list():
        url = (repo.url or "").lower()
        path = (repo.path or "").lower()
        if needle in url or needle in path:
            hits.append(repo)

    if len(hits) == 1:
        root = hits[0].path or ""
        if not root:
            raise SystemExit("Repos API returned a match with an empty path.")
        return root.rstrip("/")

    if not hits:
        raise SystemExit(
            f"No Git folder matched DATABRICKS_REPO_REMOTE_MATCH={substring!r}. "
            "Clone or link the repo under Repos in this workspace, or set DATABRICKS_REPO_WORKSPACE_ROOT."
        )

    lines = "\n".join(f"  - {r.path!r} ({r.url})" for r in hits)
    raise SystemExit(
        "DATABRICKS_REPO_REMOTE_MATCH matched multiple repos; narrow the substring or set "
        f"DATABRICKS_REPO_WORKSPACE_ROOT explicitly:\n{lines}"
    )


def _resolve_notebook_paths(client) -> tuple[str, str]:
    """Resolve train/score workspace paths from env (explicit paths, repo root, or Repos API lookup)."""
    train_rel = os.environ.get("NOTEBOOK_TRAIN_RELATIVE", _DEFAULT_TRAIN_REL).strip().strip("/")
    score_rel = os.environ.get("NOTEBOOK_SCORE_RELATIVE", _DEFAULT_SCORE_REL).strip().strip("/")

    train_path = os.environ.get("NOTEBOOK_TRAIN_PATH", "").strip()
    score_path = os.environ.get("NOTEBOOK_SCORE_PATH", "").strip()
    base = os.environ.get("DATABRICKS_REPO_WORKSPACE_ROOT", "").strip().rstrip("/")
    remote_match = os.environ.get("DATABRICKS_REPO_REMOTE_MATCH", "").strip()

    if (not train_path or not score_path) and not base and remote_match:
        if client is None:
            raise SystemExit(
                "DATABRICKS_REPO_REMOTE_MATCH needs Databricks auth to list repos "
                "(DATABRICKS_HOST + token/profile). "
                "Alternatively set DATABRICKS_REPO_WORKSPACE_ROOT to the repo folder path."
            )
        base = _repo_root_from_remote_match(client, remote_match)

    if base:
        if not train_path:
            train_path = f"{base}/{train_rel}"
        if not score_path:
            score_path = f"{base}/{score_rel}"

    if not train_path or not score_path:
        raise SystemExit(
            "Set NOTEBOOK_TRAIN_PATH and NOTEBOOK_SCORE_PATH, or set DATABRICKS_REPO_WORKSPACE_ROOT "
            "to your Git folder root under Repos (or Workspace). "
            "Or set DATABRICKS_REPO_REMOTE_MATCH with auth so the script can resolve the root. "
            "See databricks/asset_bundle/README.md."
        )

    return train_path, score_path


def _build_job_settings(*, use_serverless: bool, train_path: str, score_path: str):  # noqa: ANN202
    from databricks.sdk.service import compute
    from databricks.sdk.service import jobs

    score_params = _score_notebook_parameters()

    spark_v = os.environ.get("DATABRICKS_SPARK_VERSION", "15.4.x-scala2.12")
    node_type = os.environ.get("DATABRICKS_NODE_TYPE_ID", "Standard_DS3_v2")
    workers = int(os.environ.get("DATABRICKS_NUM_WORKERS", "1"))
    job_name = os.environ.get("DATABRICKS_JOB_NAME", "[demo] Train renewal then score gold (API)")

    if use_serverless:
        # No job_cluster_key / new_cluster / existing_cluster_id → serverless compute (Jobs API / TF provider).
        env_key = os.environ.get("DATABRICKS_SERVERLESS_ENVIRONMENT_KEY", "demo_shared_env").strip()
        env_version = os.environ.get("DATABRICKS_SERVERLESS_ENV_VERSION", "").strip()
        deps = _parse_dependencies_list(os.environ.get("DATABRICKS_SERVERLESS_DEPENDENCIES", ""))

        environments = None
        if env_version or deps:
            resolved_version = env_version or os.environ.get(
                "DATABRICKS_SERVERLESS_ENV_VERSION_DEFAULT", "5"
            ).strip()
            if not resolved_version:
                raise SystemExit(
                    "Set DATABRICKS_SERVERLESS_ENV_VERSION when using DATABRICKS_SERVERLESS_DEPENDENCIES, "
                    "or define DATABRICKS_SERVERLESS_ENV_VERSION_DEFAULT."
                )
            spec = compute.Environment(
                environment_version=resolved_version,
                dependencies=deps or None,
            )
            environments = [jobs.JobEnvironment(environment_key=env_key, spec=spec)]

        tasks = [
            jobs.Task(
                task_key="train",
                environment_key=env_key if environments else None,
                notebook_task=jobs.NotebookTask(
                    notebook_path=train_path,
                    base_parameters={"ENV": os.environ.get("NOTEBOOK_PARAM_ENV", "demo")},
                ),
            ),
            jobs.Task(
                task_key="score",
                environment_key=env_key if environments else None,
                depends_on=[jobs.TaskDependency(task_key="train")],
                notebook_task=jobs.NotebookTask(
                    notebook_path=score_path,
                    base_parameters=score_params,
                ),
            ),
        ]
        return job_name, None, environments, tasks

    job_clusters = [
        jobs.JobCluster(
            job_cluster_key="shared_cluster",
            new_cluster=compute.ClusterSpec(
                spark_version=spark_v,
                node_type_id=node_type,
                num_workers=workers,
            ),
        )
    ]

    tasks = [
        jobs.Task(
            task_key="train",
            job_cluster_key="shared_cluster",
            notebook_task=jobs.NotebookTask(
                notebook_path=train_path,
                base_parameters={"ENV": os.environ.get("NOTEBOOK_PARAM_ENV", "demo")},
            ),
        ),
        jobs.Task(
            task_key="score",
            job_cluster_key="shared_cluster",
            depends_on=[jobs.TaskDependency(task_key="train")],
            notebook_task=jobs.NotebookTask(
                notebook_path=score_path,
                base_parameters=score_params,
            ),
        ),
    ]

    return job_name, job_clusters, None, tasks


def _dry_run_payload(job_name, job_clusters, environments, tasks) -> dict:
    body: dict = {"name": job_name, "tasks": [t.as_dict() for t in tasks]}
    if job_clusters is not None:
        body["job_clusters"] = [jc.as_dict() for jc in job_clusters]
    if environments is not None:
        body["environments"] = [e.as_dict() for e in environments]
    return body


def _optional_cron_schedule():
    """Return CronSchedule from env, or None if scheduling disabled."""
    quartz = os.environ.get("DATABRICKS_JOB_SCHEDULE_QUARTZ", "").strip()
    if not quartz:
        return None
    from databricks.sdk.service.jobs import CronSchedule
    from databricks.sdk.service.jobs import PauseStatus

    tz = os.environ.get("DATABRICKS_JOB_SCHEDULE_TIMEZONE", "UTC").strip() or "UTC"
    pause = PauseStatus.PAUSED if _env_truthy("DATABRICKS_JOB_SCHEDULE_PAUSED") else PauseStatus.UNPAUSED
    return CronSchedule(quartz_cron_expression=quartz, timezone_id=tz, pause_status=pause)


def _score_notebook_parameters() -> dict[str, str]:
    gold_export = os.environ.get("DATABRICKS_GOLD_CSV_WORKSPACE_EXPORT", "").strip()
    params = {
        "EXPORT_CSV_FOR_PBIP": os.environ.get("NOTEBOOK_PARAM_EXPORT_CSV", "true"),
    }
    if gold_export:
        params["gold_csv_workspace_export"] = gold_export
    return params


def _job_api_kwargs(job_name, job_clusters, environments, tasks, *, schedule=None):
    kw = {"name": job_name, "tasks": tasks}
    if job_clusters is not None:
        kw["job_clusters"] = job_clusters
    if environments is not None:
        kw["environments"] = environments
    if schedule is not None:
        kw["schedule"] = schedule
    return kw


def main() -> int:
    load_repo_dotenv()
    parser = argparse.ArgumentParser(description="Deploy demo renewal job via Databricks Jobs API (SDK).")
    parser.add_argument("--dry-run", action="store_true", help="Print JSON payload only; no API calls.")
    parser.add_argument(
        "--serverless",
        action="store_true",
        help="Use serverless compute (omit job_clusters). Same as DATABRICKS_USE_SERVERLESS=1.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset existing job DEMO_JOB_ID instead of creating a new job.",
    )
    args = parser.parse_args()

    try:
        from databricks.sdk import WorkspaceClient
        from databricks.sdk.service import jobs
    except ImportError:
        print("Install: pip install -r requirements-databricks-deploy.txt", file=sys.stderr)
        return 1

    train_env = os.environ.get("NOTEBOOK_TRAIN_PATH", "").strip()
    score_env = os.environ.get("NOTEBOOK_SCORE_PATH", "").strip()
    base_env = os.environ.get("DATABRICKS_REPO_WORKSPACE_ROOT", "").strip()
    remote_env = os.environ.get("DATABRICKS_REPO_REMOTE_MATCH", "").strip()
    resolve_client = None
    if remote_env and not base_env and (not train_env or not score_env):
        resolve_client = WorkspaceClient()

    train_path, score_path = _resolve_notebook_paths(resolve_client)

    use_serverless = bool(args.serverless or _env_truthy("DATABRICKS_USE_SERVERLESS"))
    job_name, job_clusters, environments, tasks = _build_job_settings(
        use_serverless=use_serverless,
        train_path=train_path,
        score_path=score_path,
    )
    schedule = _optional_cron_schedule()

    if args.dry_run:
        payload = _dry_run_payload(job_name, job_clusters, environments, tasks)
        if schedule is not None:
            payload["schedule"] = schedule.as_dict()
        print(json.dumps(payload, indent=2))
        return 0

    w = resolve_client if resolve_client is not None else WorkspaceClient()

    if args.reset:
        job_id_str = os.environ.get("DEMO_JOB_ID", "").strip()
        if not job_id_str.isdigit():
            raise SystemExit("For --reset set DEMO_JOB_ID to the numeric job id from the workspace UI.")
        job_id = int(job_id_str)
        api_kw = _job_api_kwargs(job_name, job_clusters, environments, tasks, schedule=schedule)
        settings = jobs.JobSettings(**api_kw)
        w.jobs.reset(job_id=job_id, new_settings=settings)
        print(f"Reset job_id={job_id} name={job_name!r}")
        if schedule:
            print(f"Schedule: quartz={schedule.quartz_cron_expression!r} tz={schedule.timezone_id!r} pause={schedule.pause_status}")
        return 0

    created = w.jobs.create(**_job_api_kwargs(job_name, job_clusters, environments, tasks, schedule=schedule))
    jid = getattr(created, "job_id", None)
    print(f"Created job_id={jid} name={job_name!r}")
    print("Tip: export DEMO_JOB_ID for future --reset runs.")
    if schedule:
        print(f"Schedule: quartz={schedule.quartz_cron_expression!r} tz={schedule.timezone_id!r} pause={schedule.pause_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
