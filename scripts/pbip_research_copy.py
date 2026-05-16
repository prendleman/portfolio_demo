#!/usr/bin/env python3
"""Pull short, interview-safe prose from repo markdown for PBIR textboxes."""

from __future__ import annotations

import re
from pathlib import Path


def extract_section_bullets(md_text: str, heading_needle: str, *, max_items: int = 6) -> list[str]:
    """Lines like `- foo` under the first `##` heading that contains `heading_needle`."""
    lines = md_text.splitlines()
    i = 0
    needle_l = heading_needle.lower()
    while i < len(lines):
        ln = lines[i].strip()
        if ln.startswith("#") and needle_l in ln.lower():
            i += 1
            bullets: list[str] = []
            while i < len(lines):
                s = lines[i].strip()
                if re.match(r"^##\s", s) and needle_l not in s.lower():
                    break
                if s.startswith(("- ", "* ")):
                    t = _clean_inline_md(s[2:].strip())
                    if t:
                        bullets.append(t)
                    if len(bullets) >= max_items:
                        return bullets
                i += 1
            return bullets
        i += 1
    return []


def extract_labeled_bullet_block(md_text: str, line_start_needle: str, *, max_items: int = 8) -> list[str]:
    """Bullets following a line that contains line_start_needle (e.g. 'Sources')."""
    lines = md_text.splitlines()
    needle = line_start_needle.lower()
    for i, raw in enumerate(lines):
        if needle in raw.lower() and "**" in raw:
            bullets: list[str] = []
            j = i + 1
            while j < len(lines):
                s = lines[j].strip()
                if not s:
                    if bullets:
                        break
                    j += 1
                    continue
                if re.match(r"^##\s", s):
                    break
                if s.startswith(("- ", "* ")):
                    t = _clean_inline_md(s[2:].strip())
                    if t:
                        bullets.append(t)
                    if len(bullets) >= max_items:
                        return bullets
                j += 1
            return bullets
    return []


def extract_table_first_column(md_text: str, heading_needle: str, *, max_rows: int = 8) -> list[str]:
    """First column of the first markdown table after a heading that contains `heading_needle`."""
    lines = md_text.splitlines()
    i = 0
    needle_l = heading_needle.lower()
    header_keys = {"organization", "function"}
    while i < len(lines):
        if lines[i].strip().startswith("#") and needle_l in lines[i].lower():
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("|"):
                hdr = lines[i].strip()
                if re.match(r"^##\s", hdr):
                    return []
                i += 1
            rows: list[str] = []
            while i < len(lines):
                s = lines[i].strip()
                if not s.startswith("|"):
                    break
                cells = [c.strip() for c in s.split("|")[1:-1]]
                if not cells:
                    i += 1
                    continue
                first = cells[0]
                if re.match(r"^[\s\-:|]+$", first):
                    i += 1
                    continue
                cleaned = _clean_inline_md(first)
                if cleaned and cleaned.lower() not in header_keys:
                    rows.append(cleaned)
                    if len(rows) >= max_rows:
                        return rows
                i += 1
            return rows
        i += 1
    return []


def _clean_inline_md(s: str) -> str:
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = s.replace("`", "")
    return re.sub(r"\s+", " ", s).strip()


def join_digest(parts: list[str], *, max_chars: int = 520, sep: str = " ") -> str:
    parts = [p for p in parts if p]
    if not parts:
        return ""
    out = sep.join(parts)
    if len(out) <= max_chars:
        return out
    trimmed = out[: max_chars - 1].rsplit(" ", 1)[0]
    return trimmed + "…"


def research_callout_lines(
    opportunity_md: Path,
    competitive_md: Path,
    *,
    rel_root_display: str = "research/core_spaces/",
) -> tuple[str, str]:
    """Returns (opportunity_block, competitive_block) for static text visuals."""
    om = opportunity_md.read_text(encoding="utf-8")
    cm = competitive_md.read_text(encoding="utf-8")

    src = extract_labeled_bullet_block(om, "Sources (captured")
    themes = extract_section_bullets(om, "Cross-cutting themes", max_items=4)

    opp_lines = [
        "In-repo research digest — public signals only.",
        f"Primary file: {rel_root_display}opportunity_map.md",
    ]
    if src:
        opp_lines.append("Sources captured:")
        for s in src[:5]:
            opp_lines.append(f"  • {_truncate(s, 110)}")
    if themes:
        opp_lines.append("Themes:")
        for t in themes:
            opp_lines.append(f"  • {_truncate(t, 130)}")

    base_pos = extract_section_bullets(cm, "Core Spaces publicly positions", max_items=4)
    sh_peers = extract_table_first_column(cm, "Student-housing", max_rows=5)
    btr_peers = extract_table_first_column(cm, "Build-to-rent", max_rows=5)

    comp_lines = [
        "In-repo research digest — peers are illustrative.",
        f"Primary file: {rel_root_display}competitive_landscape.md",
    ]
    if base_pos:
        comp_lines.append("Positioning (baseline):")
        for t in base_pos:
            comp_lines.append(f"  • {_truncate(t, 130)}")
    if sh_peers:
        comp_lines.append(f"Student-housing sample: {_truncate(', '.join(sh_peers), 420)}.")
    if btr_peers:
        comp_lines.append(f"BFR / horizontal sample: {_truncate(', '.join(btr_peers), 420)}.")

    return "\n".join(opp_lines), "\n".join(comp_lines)


def hero_strings_opportunity(md_path: Path) -> tuple[str, str, str]:
    """Eyebrow, headline, lede — whisper fixed in caller or short."""
    text = md_path.read_text(encoding="utf-8")
    themes = extract_section_bullets(text, "Cross-cutting themes", max_items=3)
    if not themes:
        lede = (
            "Public careers and divisions pages suggest vertically integrated workflows—use this synthetic portfolio "
            "to rehearse renewal analytics against that narrative spine."
        )
    else:
        lede = join_digest(themes, max_chars=560)
    return (
        "Opportunity signals (public)",
        "Where org language meets governed analytics wedges",
        lede or "Synthetic renewal KPIs anchored to publicly described operating lanes.",
    )


def hero_strings_competition(md_path: Path) -> tuple[str, str, str]:
    text = md_path.read_text(encoding="utf-8")
    base = extract_section_bullets(text, "Core Spaces publicly positions", max_items=3)
    sh = extract_table_first_column(text, "Student-housing", max_rows=6)
    btr = extract_table_first_column(text, "Build-to-rent", max_rows=6)
    extra = []
    if sh:
        extra.append("Student-heavy comparables mentioned in-repo include " + ", ".join(sh[:4]) + ".")
    if btr:
        extra.append("BFR-adjacent names include " + ", ".join(btr[:4]) + ".")
    mid = join_digest(base + extra, max_chars=580)
    if not mid:
        mid = (
            "Interview framing only: juxtapose renewal propensity with how operators publicly describe portfolios "
            "(student versus rental platforms)."
        )
    return ("Competitive framing (public)", "Benchmarking axes for renewal narrative", mid)


def _truncate(s: str, n: int) -> str:
    s = s.strip()
    if len(s) <= n:
        return s
    return s[: n - 1].rsplit(" ", 1)[0] + "…"
