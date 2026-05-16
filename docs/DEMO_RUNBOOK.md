# Demo operating runbook (Databricks → Power BI)

Synthetic portfolio renewal demo — **no proprietary Core Spaces data**.

## Prerequisites

- Databricks workspace with Repos + serverless-compatible Jobs (this repo targets serverless notebook tasks).
- Power BI Desktop for `powerbi/CoreSpacesRenewal.pbip`.
- Local clone aligned with GitHub (`scripts/verify_github_repo_remote.py`).

## Repeatable pipeline

1. **Repos** — Pull latest Git folder (`portfolio_demo` or your fork path).
2. **Train + score** — Run job `[demo] Train renewal then score gold (API)` (or equivalent bundle).

   ```powershell
   cd path\to\portfolio-core-spaces-demo
   python scripts/databricks_deploy_demo_job.py --reset --serverless
   ```

   Optional **daily schedule** — set `DATABRICKS_JOB_SCHEDULE_QUARTZ`, `DATABRICKS_JOB_SCHEDULE_TIMEZONE`, then `--reset` again.

3. **Gold CSV for BI**

   - **Local PBIP**: refresh scores locally (`scripts/run_local_pipeline.py`) or copy CSV from Databricks, then:

     ```powershell
     python scripts/update_pbip_gold_csv_path.py
     ```

   - **Workspace copy**: set `DATABRICKS_GOLD_CSV_WORKSPACE_EXPORT=/Workspace/Users/you@corp/gold_renewal_scores.csv` and redeploy job — score task copies CSV after write.

4. **PBIR refresh**

   ```powershell
   python scripts/sync_pbip_report.py
   ```

5. **Power BI** — Open `CoreSpacesRenewal.pbip`, **Refresh** semantic model, verify pages under bookmark navigator.

## Operational checks

| Check | Where |
|--------|--------|
| Job last run | Workflows → Jobs → run history |
| MLflow experiment | `/Shared/portfolio_renewal_demo` (Databricks workspace MLflow) |
| Copilot in Power BI (Fabric tenant) | `powerbi/COPILOT_TENANT.md` (admin + capacity; then publish PBIP) |
| Copilot teaser URL | `COPILOT_STUDIO_PUBLISH_URL` or `scripts/gen_pbip_report_pages.py` |

## Repo hygiene

- Canonical demo remote today: **`prendleman/portfolio_demo`** (rename/description in GitHub if you fork).
- Never commit `.env` — rotate PATs if leaked.
