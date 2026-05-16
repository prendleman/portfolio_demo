# Interview Review Guide

This repository is a synthetic portfolio demo showing how I would approach a practical AI architecture problem in a real estate / property operations environment.

It demonstrates:

- Databricks-style bronze / silver / gold data flow
- Feature engineering for renewal intelligence
- scikit-learn + MLflow model path
- PySpark / Spark ML variant
- Batch scoring for BI consumption
- Power BI / PBIP delivery
- PSI and schema-drift monitoring
- Copilot Studio grounding design pattern
- Unity Catalog / MLflow productionization plan
- Governance and responsible AI considerations

## How to Review in 5 Minutes

1. Start with `README.md`.
2. Review the Spark ML path: `databricks/02b_train_sparkml_variant/`.
3. Review productionization: `databricks/docs/PRODUCTIONIZATION_UC_MLFLOW.md`.
4. Review monitoring: `monitoring/psi_check.py` and `scripts/monitoring_psi_schema.py`.
5. Review business-facing explanation: `powerbi/interview_loom_script.md`.

## What This Is

This is a synthetic demo. It does not use Core Spaces proprietary data.

## What This Is Not

This is not a live production deployment, a deployed Copilot Studio agent, or a claim of access to Core Spaces systems.

## Interview Talking Point

The purpose of this repo is to show how I think: moving from business problem to data architecture, feature logic, model path, scoring output, BI consumption, monitoring, governance, and adoption.

## How I Would Approach the First 30 / 60 / 90 Days

### First 30 Days

- Inventory high-value AI and analytics use cases.
- Review current data platforms, source systems, BI assets, and governance gaps.
- Identify quick wins where AI/ML can improve operational visibility without creating unnecessary risk.
- Meet with business and technical stakeholders to understand pain points, current reporting flows, and adoption barriers.

### First 60 Days

- Prioritize 2–3 practical AI use cases tied to measurable business outcomes.
- Define source-system contracts, ownership, model-risk controls, and adoption path.
- Build prototype-to-production patterns using Databricks, MLflow, Power BI/Fabric, and Microsoft AI tooling.
- Establish lightweight governance patterns that support delivery without slowing the team down.

### First 90 Days

- Move the highest-value prototype toward governed production.
- Establish repeatable patterns for monitoring, drift detection, documentation, and stakeholder review.
- Build an adoption roadmap for business users, analysts, and technical teams.
- Define the longer-term AI roadmap based on practical business value, data readiness, and supportability.

## Known Limitations

This is a portfolio demo, so some production elements are intentionally represented as patterns rather than live tenant deployments.

| Area | Current State | Production Next Step |
| --- | --- | --- |
| Source systems | Synthetic data | Replace with governed Yardi / Salesforce / ERP feeds |
| Model registry | Local / optional MLflow path | Register and promote through Unity Catalog |
| Copilot Studio | Grounding contract / design pattern | Deploy as tenant-approved Copilot Studio agent |
| Monitoring | PSI / schema scripts | Add scheduled jobs, alerts, thresholds, and ownership |
| Power BI | PBIP / import demo | Publish governed semantic model or DirectLake path |
| Databricks app | Demo/local pattern | Wire to governed gold table or Databricks SQL |
| Enterprise integrations | Architecture and field contracts | Connect to actual property, leasing, ERP, CRM, and internal systems |
