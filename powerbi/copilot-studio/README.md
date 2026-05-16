# Copilot Studio and this Power BI report

**Scope honesty:** this repo includes a **Copilot Studio–style grounding pattern** (manifest JSON + report teaser link), **not** a published Copilot Studio agent with live topics, connectors, or tenant deployment. The strip is a UX affordance for interviews; production would wire a real publication URL.

This PBIP wires a lightweight **launch strip** (“Copilot Studio ▸”) beside the bottom bookmark navigator. The URL is loaded from **`publish-url.txt`** in this folder when present (first non-empty, non-comment line). If that file is missing, the generator reads the same rule from **`publish-url.example.txt`**, falling back finally to **`https://copilotstudio.microsoft.com/`**.

## Choosing where the agent runs

| Surface | Fit |
|--------|-----|
| **Copilot Studio (Microsoft 365 Agents)** | Custom topics, connectors, escalation to Power Automate, Teams / demo sites. Best when you want a **named agent** separate from Fabric Copilot billing and guardrails. |
| **Fabric / Power BI Copilot** | In-product narrative and DAX-ish assistance inside the semantic model/report context. Different product surface from Copilot Studio agents. |

For a **future** production companion, Copilot Studio is one natural surface for an **FAQ + renewal narrative bot** grounded in curated knowledge (documents, FAQs, connectors) rather than rewriting report visuals. Here it is represented by **documentation + manifest only**.

## Wire-up checklist

1. **Publish** the agent from Copilot Studio (e.g. **Demo website** or **Teams** channel) and copy the **public demo / web chat** URL Microsoft provides for that publication.
2. Create **`publish-url.txt`** next to this file with that URL on line 1 (see `.example`; keep real URLs out of git if policy requires).
3. Regenerate pages:  
   `python scripts/gen_pbip_report_pages.py`  
   That refreshes **`chrome_copilot_teaser`** on every branded page.

## If Power BI Desktop drops the hyperlink

Some builds ignore `url` inside text-run JSON. Fallback: replace the teaser with **Insert → Button → Action → Web URL**, or pin the Teams app / standalone web chat beside the embedded report.

## Going deeper

- Route the agent through **Power Automate** flows for approved read paths (e.g. SharePoint FAQs, ticketing) rather than handing the semantic model credentials to the bot.
- For **embedding**: use the publication channel Copilot Studio gives you (web component / Teams); Power BI Embedded does not substitute for that host—treat them as sibling experiences in the stakeholder demo.
