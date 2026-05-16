# AI governance — portfolio demo framing

This repository includes **governance documentation** as **design
intent**.

It does **not** replace a corporate Responsible AI program.

## Data classification

| Class | Example in this demo | Handling |
| --- | --- | --- |
| Public / synthetic | `data/synthetic/` CSVs | Safe to share; clearly labeled |
| Internal (real tenant) | **Not present** | Would require catalog policies + encryption |
| PII | **Not modeled** | Real deployments need residency and retention policies |

## Model risk tier (suggested)

**Medium** — affects leasing and revenue planning but is not fully
autonomous:

- Human-in-the-loop for lease offers and pricing.
- Model refresh cadence tied to quarterly portfolio reviews.

## Copilot Studio positioning

Copilot Studio appears here as a **grounding and UX pattern**
only.

See
[`research/COPILOT_STUDIO_DESIGN_PATTERN.md`](../../research/COPILOT_STUDIO_DESIGN_PATTERN.md).

There is **no** live agent published from this repo.

## Monitoring obligations

| Signal | Tooling in demo | Production expectation |
| --- | --- | --- |
| Score distribution drift | PSI in `04_monitoring` | Alert + rollback playbook |
| Schema drift | Column presence checks | Block downstream scoring |
| Label latency | Documented in `SCOPE.md` | SLA with property management systems |

## Audit trail fields

The gold scoring table carries:

- `scored_at`
- `dataset_version_id`
- `mlflow_run_id`

These support **BI drill-through** and **post-incident review**,
not legal discovery by themselves.

## Related

- [`research/core_spaces/jd_gap_matrix.md`](../../research/core_spaces/jd_gap_matrix.md)
- [`docs/REPO_MAINTENANCE.md`](../../docs/REPO_MAINTENANCE.md)
