# Screenshots

PNG files in this folder are **illustrative preview cards** generated for the root `README.md` **Visual Preview** table. They are **not** captured from a live tenant, proprietary systems, or production Power BI / Databricks workspaces.

When you have real exports:

1. Replace `powerbi_overview.png`, `renewal_lens_app.png`, and `monitoring_output.png` with your own images (same filenames keep the README links stable), **or**
2. Add new files and update the table in `README.md`.

Regenerate the placeholder cards from the repo root:

```bash
python scripts/gen_screenshot_placeholders.py
```

`scripts/verify_readme_assets.py` (run in CI) checks that every local `README.md` image path exists on disk.
