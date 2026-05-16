# Core Spaces — departmental opportunity map (public signals)

**Disclaimer:** This document **infers** plausible AI / analytics opportunities from **public** marketing and careers copy. It is **not** an internal strategy document, not affiliated with Core Spaces, and **not** validated against operating data.

**Sources (captured in-repo):**

- Marketing careers overview: [`site/pages/careers.md`](site/pages/careers.md) (`https://corespaces.com/careers`)
- Division definitions: [`site/pages/our-divisions.md`](site/pages/our-divisions.md) (`https://corespaces.com/our-divisions`)
- Corporate strategy page: [`site/pages/strategy.md`](site/pages/strategy.md)
- Build-to-rent line: [`site/pages/build-to-rent.md`](site/pages/build-to-rent.md)
- Student housing line: [`site/pages/student-housing.md`](site/pages/student-housing.md)
- Culture / DEI framing: [`site/pages/culture.md`](site/pages/culture.md)

## Career portal (ATS) caveat

The main site links to **`careers.corespaces.com`** (Jibe/ICIMS stack; see internal links in [`careers.md`](site/pages/careers.md)). That host’s [`robots.txt`](https://careers.corespaces.com/robots.txt) allows crawling but specifies **`crawl-delay: 5`**. This portfolio did **not** bulk-scrape the ATS; role-level detail should be added via a **separate** slow job (≥5s/request) or manual export to stay polite.

## Department buckets from careers page (verbatim themes)

From extracted text on `/careers`, public job exploration is organized around (HTML entities decoded):

| Bucket (as listed) | Notes from public copy |
| --- | --- |
| Accounting & Finance | Aligned with corporate “Ministry of Math” narrative on divisions page |
| Acquisitions | Deal sourcing / underwriting |
| Asset Management | Lifecycle of investments |
| Construction | Delivery |
| Design & Architecture | Experience & built environment |
| Entitlements | PSA → construction start; “hurdles and red tape” |
| Food & Beverage | Ancillary / experience |
| Investments | Capital relationships |
| Maintenance | Physical assets; partner with prop tech |
| Training | Enablement |
| Marketing | Brand, demand gen, resident journey |
| People | HR / People Operations / DEI partnerships (TalentAlly mentioned on careers page) |
| Operations | Broad operating layer |
| Property Management | “Live the dream”; leasing, service, systems |
| Sales & Leasing | Revenue & occupancy |
| Technology | Internal tools, integrations, helpdesk, analytics stack mentions (e.g. Entrata, Sisense in divisions copy) |

## Division-level map (from `/our-divisions`)

The divisions page narrates **Investment, Entitlements, Acquisitions, Finance, Design, Pre-Construction & Construction, Legal, Technology, Marketing, Property Management, Management Services, People Operations** with concrete responsibility blurbs—useful for aligning **data products** to org language in interviews.

Each row below maps a **public** function to **hypothesis** wedges (label: *H*).

| Function | Observable pain / aspiration (public) | *H* — Databricks / ML / GenAI wedge |
| --- | --- | --- |
| People Operations | Benefits, DEI, TalentAlly partnership, accommodations | *H* Attrition/engagement risk models on **synthetic** benchmarks; copilot FAQ grounded in policy docs (governed) |
| Investment | Capital formation, partner confidence | *H* Scenario simulators for pipeline / fund cash needs (BI + ML optional) |
| Entitlements | Scheduling, stakeholder alignment | *H* Document-heavy workflow: RAG over **public** regs + internal trackers (if ever available)—demo stays **synthetic** |
| Acquisitions | Sourcing, comps, underwriting | *H* Geospatial + market feature store; lead scoring for land/seller outreach (*H*) |
| Finance | AP/AR, draws, reporting, tax | *H* Anomaly detection on spend; close automation; **this repo** already shows batch scoring pattern transferable to AP subledger |
| Design | Awards, sensory UX | *H* Content tagging, visual asset search (GenAI) |
| Pre-Construction & Construction | Schedule/budget risk | *H* Forecast delays from historical patterns (synthetic analog) |
| Legal | Contracts, JVs | *H* Clause retrieval + obligation tracking (*H*), heavy governance |
| Technology | Entrata / Sisense mentions, helpdesk | *H* Lakehouse as system of analysis; Databricks Apps for internal tools—see `jd_gap_matrix.md` |
| Marketing | Journey, campaigns, agencies | *H* Multi-touch attribution (*H*); creative variant testing |
| Property Management | Leasing, CX, maintenance | *H* Renewal / churn propensity (**this repo’s demo KPI**), staffing, sentiment from tickets (*H*) |
| Management Services | Capex, vendors, life safety | *H* Warranty & vendor SLA scoring |
| Sales & Leasing | Funnel velocity | *H* Lead scoring, tour-to-lease conversion |

## Cross-cutting themes (public)

- **Vertically integrated** operator (development + operations) → data products that **span** CRM, PMS, ERP handoffs are interview gold (stubs only in this repo).
- **Hospitality-framed** PM copy → measurement of **service quality** proxies (response times, rework) as ML features (*H*).
- **DEI + accessible hiring** messaging → responsible AI / monitoring for **bias** in ranking tools if ML touches hiring (governance).

## Next research step (optional)

1. Run a **slow** (`crawl-delay: 5`) fetcher against `https://careers.corespaces.com/sitemap.xml` to tabulate **live role titles**—or manually paste a snapshot CSV into `research/core_spaces/careers_roles_sample.csv` after downloading from the public UI.
2. Map 3–5 roles you care about to **portfolio** tickets (e.g. renewal model → PM; acquisition comp model → Acquisitions).
