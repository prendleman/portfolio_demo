#!/usr/bin/env python3
"""Polite public fetch of corespaces.com from sitemap.xml, with optional deep discovery.

Default: sitemap-only URLs (original behavior).
``--deep``: after the sitemap pass, fetch additional internal links discovered in HTML
that were not present in the sitemap (second pass, capped).

Identifiable User-Agent, ~0.45s delay between requests, no authentication.
Outputs: research/core_spaces/sitemap_inventory.json, site/pages/*.md, site/raw_html/*.html,
captures_dashboard.json, site/capture_manifest.md, and optionally derived/company_intel.{json,md}.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "PortfolioResearchBot/1.0 (independent hiring portfolio; polite crawl)"
DELAY_SECONDS = 0.45
SITEMAP_URL = "https://corespaces.com/sitemap.xml"
BASE_HOST = "corespaces.com"
HOMEPAGE = "https://corespaces.com/"


@dataclass
class PageCapture:
    url: str
    fetched_at_iso: str
    http_status: int | None
    content_type: str | None
    title: str
    meta_description: str
    headings: list[list[str]]
    text_excerpt: str
    internal_links: list[str]
    external_links: list[str]
    error: str | None


def extract_html(html: str) -> tuple[str, str, list[tuple[str, str]], str]:
    tit = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.I | re.S)
    title = " ".join(re.sub(r"\s+", " ", tit.group(1)).split()) if tit else ""
    md = re.search(
        r'<meta[^>]*name\s*=\s*["\']description["\'][^>]*content\s*=\s*["\']([^"\']*)["\']',
        html,
        flags=re.I,
    )
    if not md:
        md = re.search(
            r'<meta[^>]*content\s*=\s*["\']([^"\']*)["\'][^>]*name\s*=\s*["\']description["\']',
            html,
            flags=re.I,
        )
    meta_description = md.group(1).strip() if md else ""
    headings: list[tuple[str, str]] = []
    for m in re.finditer(r"<h([123])[^>]*>(.*?)</h\1>", html, flags=re.I | re.S):
        tag = "h" + m.group(1)
        txt = re.sub(r"<[^>]+>", " ", m.group(2))
        txt = re.sub(r"\s+", " ", txt).strip()[:600]
        if txt:
            headings.append((tag, txt))
    stripped = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    stripped = re.sub(r"(?is)<style.*?>.*?</style>", " ", stripped)
    stripped = re.sub(r"(?is)<noscript.*?>.*?</noscript>", " ", stripped)
    stripped = re.sub(r"<[^>]+>", " ", stripped)
    body = re.sub(r"\s+", " ", stripped).strip()
    excerpt = body[:12000]
    return title, meta_description, headings[:100], excerpt


def fetch_url(url: str) -> tuple[int | None, str | None, bytes | None, str | None]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            ctype = resp.headers.get("Content-Type")
            raw = resp.read()
            return resp.getcode(), ctype, raw, None
    except urllib.error.HTTPError as e:
        data = None
        try:
            data = e.read()
        except Exception:
            pass
        return e.code, e.headers.get("Content-Type") if e.headers else None, data, repr(e)
    except Exception as e:
        return None, None, None, repr(e)


def link_buckets(html: str) -> tuple[list[str], list[str]]:
    hrefs = re.findall(r'<a\s+[^>]*href\s*=\s*["\']([^"\']+)["\']', html, flags=re.I)
    internal, external = set(), set()
    for h in hrefs:
        h = (h or "").strip()
        if not h or h.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        if h.startswith("//"):
            h = "https:" + h
        if h.startswith("/"):
            internal.add(("https://" + BASE_HOST + h).split("#")[0])
        elif h.lower().startswith("http"):
            parts = h.split("#")[0]
            if BASE_HOST in parts.lower():
                internal.add(parts)
            else:
                external.add(parts)
    return sorted(internal), sorted(external)[:120]


def slug_from_url(url: str) -> str:
    u = url.replace("https://corespaces.com/", "").strip("/") or "index"
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", u)[:115] + ".md"


def _dedupe_urls(urls: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def load_sitemap_pairs() -> list[tuple[str, str | None]]:
    status, ctype, raw, err = fetch_url(SITEMAP_URL)
    if raw is None:
        raise SystemExit(f"sitemap fetch failed: {err}")
    sm_txt = raw.decode("utf-8", errors="replace")
    root = ET.fromstring(sm_txt)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    pairs: list[tuple[str, str | None]] = []
    for uel in root.findall(".//sm:url", ns):
        loc = uel.find("sm:loc", ns)
        lm = uel.find("sm:lastmod", ns)
        if loc is not None and loc.text:
            pairs.append((loc.text.strip(), lm.text if lm is not None and lm.text else None))
    return pairs


def maybe_sleep(idx: int) -> None:
    if idx:
        time.sleep(DELAY_SECONDS)


def capture_one(idx: int, total: int, url: str, pages_dir: Path, raw_dir: Path) -> PageCapture:
    maybe_sleep(idx)
    print(f"[{idx + 1}/{total}] {url}")
    st, ct, body, ferr = fetch_url(url)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    title, meta, heads, excerpt = "", "", [], ""
    inl: list[str] = []
    ext: list[str] = []
    emsg = ferr
    if body and ct and ("html" in ct.lower() or b"<html" in body[:2500].lower()):
        ht = body.decode("utf-8", errors="replace")
        slug = slug_from_url(url).replace(".md", ".html")
        (raw_dir / slug).write_text(ht[:900_000], encoding="utf-8", errors="replace")
        title, meta, heads, excerpt = extract_html(ht)
        inl, ext = link_buckets(ht)
    elif body and ct:
        emsg = (emsg or "") + f" non-html({ct})"
    cp = PageCapture(
        url=url,
        fetched_at_iso=ts,
        http_status=st,
        content_type=ct,
        title=title,
        meta_description=meta,
        headings=[[lvl, txt] for lvl, txt in heads],
        text_excerpt=excerpt,
        internal_links=inl,
        external_links=ext,
        error=emsg,
    )

    slug_md = slug_from_url(url)
    md_lines = [
        "---",
        f"source_url: {url}",
        f"captured_at: {ts}",
        f"http_status: {st}",
        "---",
        "",
        f"# {title or '(no title)'}",
        "",
        f"> Meta description: {meta or '*none*'}",
        "",
    ]
    if heads:
        md_lines.append("## Headings (h1–h3)")
        for lvl, txt in heads[:60]:
            md_lines.append(f"- **{lvl}**: {txt}")
        md_lines.append("")
    if excerpt:
        md_lines.extend(["## Extracted visible text (truncated)", "", excerpt[:10000], ""])
    if inl:
        md_lines.extend(["## Internal links", ""])
        md_lines.extend(f"- `{x}`" for x in inl[:80])
        md_lines.append("")
    if ext:
        md_lines.extend(["## External links (sample)", ""])
        md_lines.extend(f"- `{x}`" for x in ext[:50])
        md_lines.append("")
    if emsg:
        md_lines.extend(["## Fetch notes", "", f"`{emsg}`", ""])

    (pages_dir / slug_md).write_text("\n".join(md_lines), encoding="utf-8")
    return cp


def _norm_url(url: str) -> str:
    return url.split("#", 1)[0].rstrip("/")


def deep_extra_candidates(captures: list[PageCapture], known_urls: Iterable[str], cap: int) -> list[str]:
    known_norm = {_norm_url(u) for u in known_urls}
    inner: dict[str, str] = {}  # norm -> preferred URL (first seen canonical form)

    for c in captures:
        for u in c.internal_links:
            if not u.lower().startswith("https://corespaces.com"):
                continue
            n = _norm_url(u)
            if n not in inner:
                inner[n] = u.split("#", 1)[0]

    found: list[str] = []
    for n in sorted(inner.keys()):
        if n in known_norm:
            continue
        low = inner[n].lower()
        if any(low.endswith(ext) for ext in (".pdf", ".zip", ".png", ".jpg", ".jpeg", ".webp")):
            continue
        found.append(inner[n])
        if len(found) >= cap:
            break
    return found


def synthesize_intel(*, captures: list[PageCapture], deep_extras_applied: int) -> tuple[dict, str]:
    """Heuristic rollup for portfolio narrative—not official company research."""
    combined = "\n".join(c.text_excerpt for c in captures if c.text_excerpt)
    lc = combined.lower()

    partner_hit = [
        (r"j\.?\s*p\.?\s*morgan|\bjpmorgan\b", "J.P. Morgan"),
        (r"\bpgim\b", "PGIM"),
        (r"\btalkspace\b", "Talkspace"),
    ]
    named_partners: list[str] = []
    for pat, label in partner_hit:
        if re.search(pat, lc):
            named_partners.append(label)

    h1_collect: list[str] = []
    for c in captures:
        for lvl, txt in c.headings:
            if lvl == "h1" and txt:
                h1_collect.append(txt)
    h1_uniq: list[str] = []
    for h in h1_collect:
        if h not in h1_uniq:
            h1_uniq.append(h)

    ecosystem_tokens: list[str] = []
    for phrase in (
        "student housing",
        "build-to-rent",
        "single family",
        "multifamily",
        "hospitality",
        "innovation",
        "ecosystem",
        "partners",
    ):
        if phrase in lc:
            ecosystem_tokens.append(phrase)

    brand_shape_keywords: list[str] = []
    for phrase in ("live your core", "liveyourcore", "ōliv", "oliv", "core spaces"):
        if phrase in lc:
            brand_shape_keywords.append(phrase)

    raw_dir_note = "see site/raw_html/*.html — optional JSON-LD blocks can be mined offline"

    profile: dict = {
        "source_domain": BASE_HOST,
        "synthesized_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pages_captured": len(captures),
        "deep_extra_urls_fetched": deep_extras_applied,
        "disclaimer": "Independent portfolio capture; not affiliated with Core Spaces; not for investment decisions.",
        "public_positioning_snippets": {
            "headline_phrases_sample": h1_uniq[:25],
            "ecosystem_language_hits_sorted": sorted(set(ecosystem_tokens)),
            "named_partner_mentions_in_text": sorted(set(named_partners)),
            "landing_copy_tokens": sorted(set(brand_shape_keywords)),
        },
        "synthetic_data_alignment_hints": [
            "Weight metros toward collegiate + growth corridors (student-heavy + sunbelt mixes).",
            "Split narratives between dense student beds and dispersed BFR lots (dual ecosystem).",
            "Keep hospitality / service tenor in MetaPortfolio captions (interview storytelling).",
            "Design language: layered concentric rings / multi-tone 'O' motifs map to donut + gradient chrome in BI only.",
        ],
        "technical_note": raw_dir_note,
    }

    partners_md = profile["public_positioning_snippets"]["named_partner_mentions_in_text"]
    partner_lines = [f"- {p}" for p in partners_md] if partners_md else ["- _(none extracted)_"]
    h1_lines = profile["public_positioning_snippets"]["headline_phrases_sample"][:15]
    headline_md = [f"- {h}" for h in h1_lines] if h1_lines else ["- _(none)_"]

    md = "\n".join(
        [
            "# Core Spaces — synthesized public intel (portfolio-only)",
            "",
            f"*Generated {profile['synthesized_at']} from {profile['pages_captured']} captures "
            f"({profile['deep_extra_urls_fetched']} deep extras).*",
            "",
            "> " + profile["disclaimer"],
            "",
            "## What the crawl emphasized",
            "",
            "- Ecosystem vocabulary hits: "
            + (", ".join(profile["public_positioning_snippets"]["ecosystem_language_hits_sorted"]) or "_(none extracted)_"),
            "",
            "## Partner mentions (regex on visible text)",
            "",
            "\n".join(partner_lines),
            "",
            "## H1 headline sample",
            "",
            "\n".join(headline_md),
            "",
            "## Hints wired into synthetic leases / PBIR",
            "",
            *(f"- {h}" for h in profile["synthetic_data_alignment_hints"]),
            "",
        ]
    )
    return profile, md


def run_crawl(
    *,
    deep: bool,
    deep_extra_cap: int,
) -> None:
    repo = Path(__file__).resolve().parents[1]
    out_root = repo / "research" / "core_spaces"
    pages_dir = out_root / "site" / "pages"
    raw_dir = out_root / "site" / "raw_html"
    derived_dir = out_root / "derived"
    pages_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    derived_dir.mkdir(parents=True, exist_ok=True)

    sm_pairs = load_sitemap_pairs()
    sm_ordered = _dedupe_urls([HOMEPAGE] + [u for u, _ in sm_pairs])
    known_all = list(sm_ordered)

    inv_path = out_root / "sitemap_inventory.json"
    inv_path.write_text(
        json.dumps({"source": SITEMAP_URL, "url_count": len(sm_pairs), "urls": [{"url": u, "lastmod": lm} for u, lm in sm_pairs]}, indent=2),
        encoding="utf-8",
    )

    captures: list[PageCapture] = []
    ts0 = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for idx, url in enumerate(sm_ordered):
        captures.append(capture_one(idx, len(sm_ordered), url, pages_dir, raw_dir))

    deep_extra_count = 0
    extras: list[PageCapture] = []
    if deep:
        cand = deep_extra_candidates(captures, known_all, deep_extra_cap)
        n0 = len(sm_ordered)
        for j, url in enumerate(cand):
            extras.append(capture_one(n0 + j, n0 + len(cand), url, pages_dir, raw_dir))
        captures.extend(extras)
        deep_extra_count = len(extras)

    manifest = out_root / "site" / "capture_manifest.md"
    ok = sum(1 for c in captures if (c.http_status or 0) == 200 and c.text_excerpt)
    manifest.write_text(
        "\n".join(
            [
                "# Core Spaces — public capture manifest",
                "",
                f"- **Robots**: [https://corespaces.com/robots.txt](https://corespaces.com/robots.txt)",
                f"- **Sitemap**: `{SITEMAP_URL}`",
                f"- **Deep mode**: `{deep}` (extra internal URLs cap `{deep_extra_cap}`)",
                f"- **Run started**: {ts0}",
                f"- **User-Agent**: `{USER_AGENT}`",
                f"- **Delay**: {DELAY_SECONDS}s between requests",
                f"- **Primary list size**: {len(sm_ordered)} (homepage de-duped with sitemap)",
                f"- **Deep extras fetched**: {deep_extra_count}",
                f"- **Total captures**: {len(captures)}",
                f"- **Likely-readable HTML extracts**: ~{ok}",
                "",
                "## Output layout",
                "",
                "- [`../sitemap_inventory.json`](../sitemap_inventory.json) — URL list",
                "- [`../derived/`](../derived/) — synthesized `company_intel` rollup",
                "- [`pages/`](pages/) — one markdown synopsis per URL",
                "- [`raw_html/`](raw_html/) — saved HTML payloads (truncated if very large)",
                "",
                "## Index",
                "",
                "| Status | Title | URL |",
                "| --- | --- | --- |",
                *(
                    [
                        f"| {c.http_status or '—'} | {(c.title or '')[:70].replace('|', '/') } | `{c.url}` |"
                        for c in captures
                    ]
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )

    dash_path = out_root / "captures_dashboard.json"
    dash_path.write_text(json.dumps([asdict(c) for c in captures], indent=2), encoding="utf-8")

    profile, synth_md = synthesize_intel(captures=captures, deep_extras_applied=deep_extra_count)
    (derived_dir / "company_intel.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")
    (derived_dir / "company_intel.md").write_text(synth_md, encoding="utf-8")

    print("Done.")
    print(inv_path)
    print(manifest)
    print(derived_dir / "company_intel.md")


def main() -> None:
    ap = argparse.ArgumentParser(description="Polite crawl of corespaces.com for portfolio research captures.")
    ap.add_argument(
        "--deep",
        action="store_true",
        help="Second pass: fetch internal links discovered in-pass that are absent from sitemap.",
    )
    ap.add_argument(
        "--deep-extra-cap",
        type=int,
        default=140,
        help="Maximum additional internal URLs beyond the merged sitemap+homepage pass.",
    )
    args = ap.parse_args()
    run_crawl(deep=args.deep, deep_extra_cap=max(1, args.deep_extra_cap))


if __name__ == "__main__":
    main()
