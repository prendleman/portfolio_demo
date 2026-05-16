# Repo maintenance notes

This page is for **owners** maintaining the GitHub remote and
language statistics.

Reviewers can skip it unless they are updating the public repo
profile.

## Recommended GitHub description

Databricks / MLflow / Power BI portfolio demo for real estate
renewal prediction, AI governance, monitoring, and BI integration.

## Recommended GitHub topics

Use the GitHub UI **Topics** field, or the CLI/script below.

Individual topics (one token per line for readability):

- databricks
- mlflow
- powerbi
- fabric
- machine-learning
- mlops
- copilot-studio
- real-estate-analytics
- ai-governance
- python
- pyspark

### Copy/paste topic string (comma-separated)

When GitHub expects a single comma-separated list (e.g. some forms
or notes), use:

`databricks`, `mlflow`, `powerbi`, `fabric`, `machine-learning`, `mlops`, `copilot-studio`, `real-estate-analytics`, `ai-governance`

## Reviewer positioning

This repository is a **synthetic portfolio demo**.

It does **not** use Core Spaces proprietary data.

The purpose is to demonstrate how a business problem can be
translated into:

1. Source-system thinking (stubs and event contracts, not live ERP
   connectors).
2. Feature engineering (silver layer).
3. Databricks-style ML workflow (bronze → silver → gold).
4. MLflow experiment tracking and **productionization patterns**
   (Unity Catalog / registry are **tenant-dependent**).
5. Power BI / Fabric-ready consumption (PBIP import demo).
6. Monitoring (executable PSI + schema checks; job gates are
   **design intent**).
7. Copilot Studio **grounding design** (not a deployed tenant
   agent).
8. Governance and responsible AI documentation.

## Applying description and topics

### Option A — GitHub CLI

From a machine with [`gh`](https://cli.github.com/) installed and
authenticated:

```powershell
gh repo edit prendleman/portfolio_demo --description "Databricks / MLflow / Power BI portfolio demo for real estate renewal prediction, AI governance, monitoring, and BI integration."
```

```powershell
gh repo edit prendleman/portfolio_demo --add-topic "databricks" --add-topic "mlflow" --add-topic "powerbi" --add-topic "fabric" --add-topic "machine-learning" --add-topic "mlops" --add-topic "copilot-studio" --add-topic "real-estate-analytics" --add-topic "ai-governance"
```

Adjust `owner/repo` if your remote differs (`python
scripts/verify_github_repo_remote.py`).

### Option B — PAT + stdlib script (no `gh`)

Set `GH_TOKEN` or `GITHUB_TOKEN`, then from the repo root:

```powershell
python scripts/push_github_repo_metadata.py
```

Preview only:

```powershell
python scripts/push_github_repo_metadata.py --dry-run
```

See `.env.example` for optional `GH_TOKEN` notes.

Fine-grained or classic PATs need permission to edit repository
metadata and topics.

## Language bar (Linguist)

PBIP report JSON can skew GitHub’s language statistics.

This repo uses **`.gitattributes`** (`linguist-vendored` on large
report trees under `powerbi/CoreSpacesRenewal.Report/`) so the
project reads more like **Python / Databricks** than HTML/JSON
noise.

Changes apply after GitHub reindexes.

## Maintenance checklist (before sharing)

- [ ] README and Mermaid diagrams render on GitHub.
- [ ] Tables render without broken pipes.
- [ ] Links resolve (especially `docs/` and `research/`).
- [ ] [`.github/workflows/validate.yml`](../.github/workflows/validate.yml) passes on `main`.
- [ ] Synthetic-data disclaimer is visible in README and `SCOPE.md`.
- [ ] Copilot Studio is described as a **design pattern / grounding contract**, not a production agent.
- [ ] No secrets, tokens, or employer-only data in the tree.
