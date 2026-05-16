# Copilot Studio — design pattern (grounding contract)

This document describes a **Copilot Studio grounding pattern** for
portfolio reviewers.

It is **not** a deployed production agent in this repository.

## Purpose

Show how **renewal intelligence** can be exposed to business users
through a **grounded** conversational surface, without claiming
live tenant wiring.

## Grounding sources (design)

| Source type | Example artifact | Role |
| --- | --- | --- |
| Semantic model / BI | Power BI dataset or Fabric semantic model | Authoritative definitions for metrics and dimensions |
| Curated tables | `gold_lease_renewal_scored` (or equivalent) | Row-level renewal scores and drivers |
| Documentation | `docs/`, `research/`, `SCOPE.md` | Explainability, limitations, and governance |

## Example user intents (demo framing)

- “What is the predicted renewal rate for **Chicago** this month?”
- “Which properties are in the **top decile** of churn risk?”
- “What features most influenced this lease’s score?” (requires
  documented model cards / SHAP policy in a real deployment)

## Guardrails (recommended)

- **No SQL generation against production** unless a governed
  connector and row-level security are in place.
- **Citations**: every numeric claim should link back to a
  report visual, semantic-model measure, or governed table row
  aggregate.
- **Synthetic data disclaimer** must appear in the agent’s
  opening behavior or system prompt.

## Implementation note

This repo ships **Power BI PBIP** assets and **Databricks job**
YAML as **patterns**.

Actual Copilot Studio topics, connectors, and authentication are
**tenant-specific** and belong in a separate deployment repo or
internal wiki.

## Related reading

- [`research/README.md`](README.md)
- [`databricks/docs/governance.md`](../databricks/docs/governance.md)
- [`research/integration_architecture.md`](integration_architecture.md)
