# Copilot for Power BI — tenant wiring (this PBIP)

Copilot is **not turned on by editing `.pbip` or TMDL**. It depends on **Microsoft Fabric / Power BI admin settings**, **capacity SKU and region**, and **where you publish** the semantic model.

Use this checklist so `CoreSpacesRenewal.pbip` works with Copilot after publish.

## 1. Admin (Fabric admin portal)

1. Enable **Copilot** for the tenant per [Copilot tenant settings](https://learn.microsoft.com/en-us/fabric/admin/service-admin-portal-copilot).
2. If capacity is **outside US or France**, Copilot defaults off until an admin enables **data can be processed outside geographic region** (same article). Align with your compliance team before switching.
3. Confirm [Fabric region availability](https://learn.microsoft.com/en-us/fabric/admin/region-availability) for Copilot on your capacity region.

## 2. Capacity and workspace

- Copilot for Fabric / Power BI requires a **paid** capacity; **trial SKUs are not supported** for Fabric Copilot ([overview](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-introduction)). Assign **Premium Per User / PPU** or **Premium P1+** / **Fabric F2+** capacity per your licensing and publish the dataset to a workspace on that capacity.
- Publish the dataset to a workspace **backed by** that capacity (Premium or Fabric).

## 3. Power BI Desktop (this repo)

1. Sign in with a work account that has access to the Copilot-enabled capacity.
2. **File → Options → Power BI Fabric** (wording varies by version): connect/link to the **workspace** that sits on Fabric / Premium capacity so local Copilot features can resolve against service metadata where required.
3. Open `powerbi/CoreSpacesRenewal.pbip`, refresh data (`GoldRenewalCsvPath` must point at a reachable CSV — see `scripts/update_pbip_gold_csv_path.py`), then **Publish** to the Copilot-capacity workspace.

## 4. Semantic model metadata for Copilot

Follow [Optimize your semantic model for Copilot](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-evaluate-data) using **clear names**, stable types, and **Descriptions** — but **do not author `description:` inside PBIP TMDL** for this repo: Power BI Desktop **April 2026** (`2.153.x`) rejects the `description` property in **`definition/model.tmdl`** and **`definition/tables/*.tmdl`** (`UnknownKeyword`). After the project opens, add **table/column/measure descriptions** in the **Properties** pane (or use **translations** under your culture), then save the project again.

For Copilot field prioritization, use **Prep data for AI** ([AI data schemas](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-prepare-data-ai-data-schema)). Optional: add **`Copilot/`** artifacts under the semantic model per [Power BI Desktop project semantic model folder](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset).

Human-readable intent that must stay in git without using `description:` is kept as **`///` comments** above tables in TMDL (comments only; not consumed by Copilot until you mirror them into Descriptions in Desktop).

## 5. Service after publish

- In the Power BI service, use the **Copilot** pane on reports/datasets your admin allows.
- Optional: mark content **Approved for Copilot** per org policy (workspace/dataset governance), if your tenant uses that control.

## Related

- Demo operations: `docs/DEMO_RUNBOOK.md`
- External Copilot Studio teaser (not Fabric Copilot): `powerbi/copilot-studio/README.md`
