# Changelog

All notable changes to this portfolio repository are documented here. This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for **tagged snapshots** you share with employers; day-to-day demo improvements may land on `main` between tags.

## [1.0.0] — 2026-05-15

### Summary

Synthetic **Databricks / MLflow / Power BI** renewal-intelligence demo: bronze–silver–gold flow, sklearn + Spark ML paths, batch scoring, PBIP consumption, PSI/schema monitoring scripts, Copilot Studio **grounding design pattern** (not a deployed agent), and UC/MLflow productionization **patterns** in docs.

### Added

- Root `README.md` with architecture Mermaid map, honest “implemented vs design intent” table, Databricks/Power BI runbooks, and link to `INTERVIEW_REVIEW.md`.
- `INTERVIEW_REVIEW.md` for a five-minute hiring-manager skim: synthetic framing, first 30/60/90 days, known limitations.
- `screenshots/` illustrative preview cards + `scripts/gen_screenshot_placeholders.py` to regenerate them; README **Visual Preview** uses an HTML table for reliable GitHub rendering.
- `scripts/verify_readme_assets.py` and CI step in `.github/workflows/validate.yml` to fail on broken README image paths.
- `scripts/push_github_repo_metadata.py` improvements (PAT env fallbacks, TLS via certifi).
- `.gitattributes` Linguist hints (PBIP JSON, research raw HTML vendoring; Markdown `eol=lf`).

### Notes

- Replace placeholder PNGs under `screenshots/` with your own captures when convenient (`screenshots/README.md`).
- Copy-paste blurbs for resumes and profiles: [`docs/OUTREACH_SNIPPETS.md`](docs/OUTREACH_SNIPPETS.md).

[1.0.0]: https://github.com/prendleman/portfolio_demo/releases/tag/v1.0.0
