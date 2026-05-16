# Databricks Asset Bundles — portfolio demo jobs

Template file: **`databricks.template.yml`** (generated next to this README).

Goal: one **`train`** notebook task then **`score`** on the **same job cluster**, matching the JD story (MLflow → gold → BI CSV export).

## Prerequisites

1. **Databricks CLI v0.205+** with bundles: [Install](https://docs.databricks.com/dev-tools/cli/install.html).
2. **Auth**: `databricks auth login` (OAuth) or token via env — **never commit tokens**.
3. **Workspace URL**: e.g. `https://adb-1234567890.10.azuredatabricks.net`.

## One-time setup

```powershell
cd "path\to\portfolio-core-spaces-demo"

# Copy template to repo root (bundles resolve paths from root)
copy databricks\asset_bundle\databricks.template.yml .\databricks.yml

# Optional: edit spark_version / node_type_id for your region quota
```

Set the workspace host **either** inside `databricks.yml` under `targets.dev.workspace.host` **or** via bundle variable override:

```powershell
$env:WORKSPACE_HOST = "https://adb-xxxx.x.azuredatabricks.net"
```

If your CLI expects a profile:

```powershell
$env:DATABRICKS_CONFIG_PROFILE = "DEFAULT"
```

## Import notebooks into workspace

Bundles reference paths like `./databricks/02_train_renewal_model/train_mlflow`.

- **Repos**: clone this repo as a Databricks Repo so `/Repos/.../databricks/...` matches the **relative paths** in the bundle (adjust `notebook_path` if your repo root differs).
- **Workspace upload**: alternatively change `notebook_task.notebook_path` to `/Workspace/Users/you@corp/train_mlflow`.

Validate paths before deploy:

```powershell
databricks bundle validate --target dev
```

## Deploy job definition

```powershell
databricks bundle deploy --target dev
```

Then open **Workflows / Jobs** in the workspace UI and **Run now** on `[demo] Train renewal then score gold`.

## Option B — Jobs API (Python SDK or raw REST)

Bundled **`databricks bundle deploy`** ultimately persists job definitions through the same **Jobs API** you can call from CI without the bundle YAML layer.

### Python (recommended for pipelines)

Using repo-root **`.env`** (copy from `.env.example`) is supported; scripts call `python-dotenv` before reading these variables.

```powershell
pip install -r requirements-databricks-deploy.txt
$env:DATABRICKS_HOST = "https://adb-xxxx.x.azuredatabricks.net"
$env:DATABRICKS_TOKEN = "<personal-access-token>"
$env:NOTEBOOK_TRAIN_PATH = "/Repos/you@corp/demo/databricks/02_train_renewal_model/train_mlflow"
$env:NOTEBOOK_SCORE_PATH = "/Repos/you@corp/demo/databricks/03_score_batch/score_gold"
python scripts/databricks_deploy_demo_job.py --dry-run   # sanity-check JSON
python scripts/databricks_deploy_demo_job.py             # POST create via SDK
```

Update an existing job in place:

```powershell
$env:DEMO_JOB_ID = "123456789012345"
python scripts/databricks_deploy_demo_job.py --reset
```

Optional tuning: `DATABRICKS_SPARK_VERSION`, `DATABRICKS_NODE_TYPE_ID`, `DATABRICKS_NUM_WORKERS`, `DATABRICKS_JOB_NAME`.

Script: [`scripts/databricks_deploy_demo_job.py`](../../scripts/databricks_deploy_demo_job.py).

### Raw HTTPS (curl)

Official reference: [Jobs API — create](https://docs.databricks.com/api/workspace/jobs/create).

```bash
curl -sS -X POST "$DATABRICKS_HOST/api/2.1/jobs/create" \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -H "Content-Type: application/json" \
  -d @job-payload.json
```

Use `--dry-run` on the Python script to emit a **`job-payload.json`-shaped** document, then paste fields as needed.

### Common failures

| Symptom | Fix |
| --- | --- |
| `notebook_path` not found | Paths are workspace paths; sync Repo or fix prefix `/Repos/...`. |
| Spark version unavailable | Pick a supported runtime from workspace **Clusters → Create → Runtime**. |
| Permission denied | Job runner needs CAN MANAGE on cluster policy / notebook paths. |
| Cluster startup quota | Reduce workers or use instance pools / smaller `node_type_id`. |

## Production-shaped next steps (talk track)

- Split **train** vs **score** jobs with dependency + schedules.
- Write gold to **Delta + UC**; swap PBIP **CSV import** for **Lakehouse / Direct Lake** semantic models.
- Wire **GitHub Actions**: `databricks bundle deploy` only after tests + MLflow stage transitions.

Refresh this template anytime:

```powershell
python scripts/generate_jd_ai_scaffold.py
```
