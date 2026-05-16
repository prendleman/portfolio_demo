# Renewal Lens — Streamlit app

Small **Streamlit** front-end for exploring **gold lease renewal scores** and segment uplift.

## What it demonstrates

- **Read-only** consumption of scored parquet (or CSV in local dev).
- **Segment filters** (metro, risk tier) aligned with Power BI narratives.
- **Synthetic data** banner so viewers do not confuse demo with production.

## Run locally

From repo root (after installing app dependencies — see root `README.md` or `pyproject.toml`):

```powershell
cd databricks/apps/renewal_lens
streamlit run app.py
```

Configure data paths via environment variables or `st.secrets` as documented in the app source.

## Production stance

This app is **not** deployed from CI.

Container packaging, authN/Z, and reverse proxy are **out of scope** for the portfolio slice.

## Related

- [`../../docs/DEMO_RUNBOOK.md`](../../docs/DEMO_RUNBOOK.md)
- [`../../powerbi/`](../../powerbi/) (PBIP semantic layer)
