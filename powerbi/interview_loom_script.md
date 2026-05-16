# Loom script (~11 minutes) — Core Spaces portfolio demo

**Before you record:** Open `CoreSpacesRenewal.pbip` in Power BI Desktop, **Refresh** the gold CSV, resize to **1280×1080** or full HD, hide unrelated apps. Use **speaker view**: synthetic data, not affiliated with Core Spaces, no proprietary ops data.

| Time | Chapter | What to show | Say (prompt — paraphrase naturally) |
| --- | --- | --- | --- |
| **0:00–0:45** | Hook | Executive page | “This is a **production-shaped** demo: Databricks-style lifecycle feeding a **governed** semantic model in Power BI. Everything is **synthetic** but the grain, KPI, and governance columns mirror how I’d wire real student-housing / BTR renewals.” |
| **0:45–2:00** | Problem & grain | `SCOPE.md` or slide | “Grain is **one lease-decision row**: renewal outcome plus ML probability and audit fields—`dataset_version_id`, `mlflow_run_id`, `scored_at`. That’s the contract BI and Copilot need to trust.” |
| **2:00–5:00** | Notebook spine | VS Code or Databricks: `00 → 01 → 02 → 03` | “Bronze/silver/gold in notebooks; training logs to **MLflow**; batch score writes gold consumed by this report. In a real tenant I’d register the model in **Unity Catalog** and drive this via **bundle jobs**.” |
| **5:00–7:30** | Power BI deep dive | **Executive** → drag **Metro / Ecosystem / Risk tier** slicers | “Consumption stays on the **semantic model**. These slicers filter the deck—same philosophy as Fabric **RLS** and Copilot **topic allowlists**: no shadow CSV narratives.” |
| **7:30–9:15** | JD glue | **AI platform & Fabric** page | “This page ties **Databricks + Fabric + Copilot governance**: model/version visuals plus manifest-driven copy from `copilot_topics_manifest.json`. Apps and notebooks serve scores; BI serves decisions.” |
| **9:15–10:30** | Business IQ | **Opportunity** + **Competitive** bookmarks | “Research is **public site capture** mapped to hypotheses—not internal strategy. The charts stay synthetic; the **language** aligns to how they describe divisions and peers.” |
| **10:30–11:00** | Close | Repo root `README.md` or GitHub | “Artifacts are reproducible: `sync_pbip_report.py` regenerates pages; `generate_jd_ai_scaffold.py` refreshes Copilot bindings and bundle templates. Happy to walk **Databricks bundle deploy** in a live workspace.” |

## Optional manual polish (after recording)

- Add **report tooltip page** on one chart (Desktop: Tooltip fields / custom tooltip page).
- Export **PBIX** via `powerbi/release/README.txt` and attach both repo link + PBIX for recruiters.
