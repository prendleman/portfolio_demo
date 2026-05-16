# LinkedIn data — what we do **not** automate here

We **do not** add scripts that:

- Log in with your username/password or stored cookies from `.env`
- Wait for or step through **MFA** and then scrape the LinkedIn feed, search, or member profiles
- Bulk-harvest “employee info” from behind an authenticated session

That pattern violates the [LinkedIn User Agreement](https://www.linkedin.com/legal/user-agreement) and common scraping policies, creates **account suspension** risk, and encourages **credential handling in tooling** (even in a local `.env`, that is easy to leak by mistake).

## Safer alternatives for interview / research prep

1. **Public company marketing site** (already in this repo): `python scripts/fetch_corespaces_public.py --deep` captures `corespaces.com` including [`/team`](https://corespaces.com/team) HTML into `research/core_spaces/site/`.
2. **Manual LinkedIn export / notes**: copy public-facing titles from company or people pages you are allowed to use; keep a private doc outside git.
3. **Official APIs (compliance path)**: use LinkedIn’s documented developer products only with the right app type, OAuth, and data entitlements — not general “employee scraping.”
4. **HR / talent systems of record** (if you ever join a team): Workday / Greenhouse exports under contract — out of scope for this portfolio repo.

If you need a **structured local directory** of people (name, title, source URL) for *hand-curated* rows, use a small CSV template under `research/` and fill it manually; we can wire that into a Copilot / FAQ doc, but not automate LinkedIn login.
