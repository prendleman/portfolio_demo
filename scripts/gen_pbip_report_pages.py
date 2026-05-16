"""Generate PBIR pages for CoreSpacesRenewal.Report — deck layouts + chrome & bookmarks."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

try:
    from repo_dotenv import load_repo_dotenv
except ImportError:

    def load_repo_dotenv() -> None:
        return


from pbip_research_copy import hero_strings_competition, hero_strings_opportunity, research_callout_lines

SCHEMA_VIS = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json"
SCHEMA_PG = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/1.4.0/schema.json"
SCHEMA_BK_META = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmarksMetadata/1.0.0/schema.json"
SCHEMA_BK = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmark/1.4.0/schema.json"

PAGE_W = 1280
PAGE_H = 912
CREAM = "'#FAF8F4'"
ACCENT_INDIGO = "#4C1D95"
ACCENT_TEAL = "#115E59"

# Registered image file names — must match report.json RegisteredResources.Image items
IMG_WALL = "CS_Wallpaper900112233.png"
IMG_LOGO = "CS_Logomark900112233.png"

CHROME_NAV_H = 72

BOOKMARK_ROWS: list[tuple[str, str, str]] = [
    ("Executive", "Executive overview", "aa10_exec_overview"),
    ("Operations", "Operations & leasing", "aa20_operations"),
    ("Finance", "Finance & economics", "aa30_finance"),
    ("Marketing", "Marketing & velocity", "aa40_marketing"),
    ("Governance", "Governance & lineage", "aa50_governance"),
    ("AI platform", "AI platform & Fabric", "aa55_ai_platform"),
    ("Opportunity", "Opportunity deep dive", "aa60_opportunity_lab"),
    ("Competition", "Competitive intelligence", "aa70_competition_lens"),
    ("Renewal drill", "Renewal drilldown", "eef0portfoliorenew01"),
]


def bookmark_id(page_folder: str) -> str:
    return hashlib.sha1(f"bkmk:cscore:{page_folder}".encode()).hexdigest()[:20]


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def read_copilot_studio_publish_url(repo_root: Path) -> str:
    """Reads optional local URL file (not committed with secrets — use .example as template)."""
    env_url = os.environ.get("COPILOT_STUDIO_PUBLISH_URL", "").strip().strip('"').strip("'")
    if env_url:
        return env_url
    p = repo_root / "powerbi/copilot-studio/publish-url.txt"
    if p.is_file():
        for line in p.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                return s.rstrip('"').lstrip('"')
    ex = repo_root / "powerbi/copilot-studio/publish-url.example.txt"
    if ex.is_file():
        for line in ex.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                return s.rstrip('"').lstrip('"')
    return "https://copilotstudio.microsoft.com/"


def page_stub(pid: str, display_name: str) -> dict:
    return {
        "$schema": SCHEMA_PG,
        "name": pid,
        "displayName": display_name,
        "displayOption": "FitToPage",
        "height": PAGE_H,
        "width": PAGE_W,
        "objects": {
            "background": [
                {
                    "properties": {
                        "color": {
                            "solid": {
                                "color": {
                                    "expr": {"Literal": {"Value": CREAM}},
                                }
                            }
                        },
                        "transparency": {"expr": {"Literal": {"Value": "0D"}}},
                    }
                }
            ]
        },
    }


def _resource_registered_image(fname: str) -> dict:
    return {
        "expr": {"ResourcePackageItem": {"PackageName": "RegisteredResources", "PackageType": 1, "ItemName": fname}}
    }


def backdrop_visual(fname: str = IMG_WALL) -> dict:
    return {
        "$schema": SCHEMA_VIS,
        "name": "chrome_backdrop_wall",
        "position": {
            "x": 0,
            "y": 0,
            "z": 12,
            "width": float(PAGE_W),
            "height": float(PAGE_H),
            "tabOrder": 12,
        },
        "visual": {
            "visualType": "image",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "imageUrl": _resource_registered_image(fname),
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": False,
        },
    }


def chrome_logo_visual(fname: str = IMG_LOGO) -> dict:
    return {
        "$schema": SCHEMA_VIS,
        "name": "chrome_logo_mark",
        "position": {
            "x": float(PAGE_W - 132),
            "y": 18,
            "z": 9240,
            "width": 64,
            "height": 64,
            "tabOrder": 9240,
        },
        "visual": {
            "visualType": "image",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "imageUrl": _resource_registered_image(fname),
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": False,
        },
    }


def bookmark_navigator_visual() -> dict:
    return {
        "$schema": SCHEMA_VIS,
        "name": "chrome_bookmark_navigator",
        "position": {
            "x": 168,
            "y": float(PAGE_H - CHROME_NAV_H),
            "z": 9300,
            "width": 1096,
            "height": float(CHROME_NAV_H - 14),
            "tabOrder": 9300,
        },
        "visual": {"visualType": "bookmarkNavigator", "drillFilterOtherVisuals": False},
    }


def copilot_teaser_textbox(url: str) -> dict:
    """Thin launch strip; `url` on textRuns may resolve to hyperlink — if Desktop strips it, set Action manually."""
    trimmed = url if len(url) < 210 else url[:207] + "…"
    return {
        "$schema": SCHEMA_VIS,
        "name": "chrome_copilot_teaser",
        "position": {
            "x": 48,
            "y": float(PAGE_H - CHROME_NAV_H + 14),
            "z": 9280,
            "width": 176,
            "height": 36,
            "tabOrder": 9280,
        },
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {
                                            "value": "Copilot Studio ▸",
                                            "url": trimmed,
                                            "textStyle": {
                                                "fontFace": "Segoe UI Semibold",
                                                "fontSize": 11,
                                                "color": "#3F68EB",
                                            },
                                        },
                                    ]
                                },
                                {
                                    "textRuns": [
                                        {
                                            "value": "Demo agent",
                                            "textStyle": {"fontFace": "Segoe UI", "fontSize": 9},
                                        },
                                    ]
                                },
                            ]
                        }
                    },
                ]
            },
            "drillFilterOtherVisuals": False,
        },
    }


def write_global_chrome_and_bookmarks(report_def: Path, repo_root: Path) -> None:
    bk_dir = report_def / "bookmarks"
    bk_meta: list[dict[str, str]] = []
    for short, lbl, pname in BOOKMARK_ROWS:
        bid = bookmark_id(pname)
        bk_meta.append({"name": bid})
        exploration = {
            "version": "1.3",
            "activeSection": pname,
            "filters": {"byExpr": []},
            "sections": {},
            "objects": {"merge": {}},
        }
        doc = {
            "$schema": SCHEMA_BK,
            "displayName": short,
            "name": bid,
            "explorationState": exploration,
            "options": {"targetVisualNames": []},
        }
        write_json(bk_dir / f"{bid}.bookmark.json", doc)

    write_json(bk_dir / "bookmarks.json", {"$schema": SCHEMA_BK_META, "items": bk_meta})

    url = read_copilot_studio_publish_url(repo_root)
    base_pages = report_def / "pages"
    chrome_pages = {
        "aa10_exec_overview",
        "aa20_operations",
        "aa30_finance",
        "aa40_marketing",
        "aa50_governance",
        "aa55_ai_platform",
        "aa60_opportunity_lab",
        "aa70_competition_lens",
        "eef0portfoliorenew01",
    }

    for pdir in chrome_pages:
        visuals = base_pages / pdir / "visuals"
        write_json(visuals / "chrome_backdrop/visual.json", backdrop_visual())
        write_json(visuals / "chrome_logo/visual.json", chrome_logo_visual())
        write_json(visuals / "chrome_book_nav/visual.json", bookmark_navigator_visual())
        write_json(visuals / "chrome_copilot_teaser/visual.json", copilot_teaser_textbox(url))


def chrome_bottom_reserve() -> float:
    """Gap between charts and bookmark strip."""
    return float(CHROME_NAV_H + 10)


def _lit_str(s: str) -> dict:
    return {"expr": {"Literal": {"Value": "'" + s.replace("'", "''") + "'"}}}


def title_objects(chart_title: str) -> dict[str, list]:
    return {
        "title": [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "fontSize": {"expr": {"Literal": {"Value": "13D"}}},
                    "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}},
                    "text": _lit_str(chart_title),
                }
            }
        ]
    }


def utc_stamp(path: Path) -> str:
    ts = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return ts.strftime("%Y-%m-%d")


def ai_platform_hero_copy(repo_root: Path) -> tuple[str, str, str, str]:
    """Pull headline/lede from generated Copilot manifest when present."""
    p = repo_root / "research" / "copilot_topics_manifest.json"
    eyebrow = "Databricks · Fabric · Copilot governance"
    headline = "Serve ML through governed semantic models—not shadow spreadsheets"
    lede = (
        "Lakehouse lifecycle (bronze→gold), MLflow-backed scoring, and Fabric/Power BI consumption mirror "
        "the JD stack narrative; Copilot stays topic-bound to explicit measures."
    )
    whisper = "Regenerate bindings with scripts/generate_jd_ai_scaffold.py after JD demos evolve."
    if not p.is_file():
        return eyebrow, headline, lede, whisper
    doc = json.loads(p.read_text(encoding="utf-8"))
    banner = doc.get("synthetic_data_banner")
    topics = doc.get("allowed_measure_topics") or []
    if banner:
        lede = banner + (
            " Allowlisted semantic surfaces in this demo: "
            + ", ".join(t.replace("_", " ") for t in topics[:6])
            + ("." if topics else "")
        )
    cite = doc.get("required_citations_pattern")
    if cite:
        whisper = cite[:320] + ("…" if len(cite) > 320 else "")
    return eyebrow, headline, lede.strip(), whisper


def multiline_notes_textbox(
    name: str,
    z: int,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    body: str,
) -> dict:
    """Margin notes fed by repo markdown — one paragraph per line in ``body``."""
    paragraphs = [
        {
            "textRuns": [
                {
                    "value": title,
                    "textStyle": {"fontFace": "Segoe UI Semibold", "fontSize": 10, "color": ACCENT_TEAL},
                }
            ]
        }
    ]
    for line in body.split("\n"):
        paragraphs.append(
            {
                "textRuns": [
                    {"value": line if line.strip() else " ", "textStyle": {"fontFace": "Segoe UI", "fontSize": 9.25}}
                ]
            }
        )

    return {
        "$schema": SCHEMA_VIS,
        "name": name,
        "position": {
            "x": x,
            "y": y,
            "z": float(680 + z),
            "width": w,
            "height": h,
            "tabOrder": 680 + z,
        },
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [{"properties": {"paragraphs": paragraphs}}],
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
            },
            "drillFilterOtherVisuals": False,
        },
    }


def hero_textbox(
    name: str,
    z: int,
    eyebrow: str,
    headline: str,
    lede: str,
    whisper: str,
    *,
    top: float = 16,
    height: float = 164,
    width: float = 1104,
) -> dict:
    paragraphs = [
        {
            "textRuns": [
                {
                    "value": eyebrow,
                    "textStyle": {"fontFace": "Segoe UI Semibold", "fontSize": 11},
                }
            ]
        },
        {
            "textRuns": [
                {
                    "value": headline,
                    "textStyle": {"fontFace": "Segoe UI Semibold", "fontSize": 28},
                }
            ]
        },
        {
            "textRuns": [
                {"value": lede, "textStyle": {"fontFace": "Segoe UI", "fontSize": 13.5}}
            ]
        },
        {
            "textRuns": [
                {
                    "value": whisper,
                    "textStyle": {"fontFace": "Segoe UI", "fontSize": 11},
                }
            ]
        },
    ]
    paragraphs[0]["textRuns"][0]["textStyle"]["color"] = ACCENT_TEAL

    return {
        "$schema": SCHEMA_VIS,
        "name": name,
        "position": {
            "x": 48,
            "y": top,
            "z": float(660 + z),
            "height": height,
            "width": width,
            "tabOrder": 660 + z,
        },
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [{"properties": {"paragraphs": paragraphs}}],
                "background": [
                    {"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}
                ],
            },
            "drillFilterOtherVisuals": False,
        },
    }


def card_visual(name: str, x: float, y: float, w: float, h: float, z: int, measures: list[str]) -> dict:
    projs = []
    for m in measures:
        projs.append(
            {
                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": m}},
                "queryRef": f"GoldRenewalScores.{m}",
                "nativeQueryRef": m,
            }
        )
    return {
        "$schema": SCHEMA_VIS,
        "name": name,
        "position": {"x": x, "y": y, "z": float(z), "width": w, "height": h, "tabOrder": z},
        "visual": {
            "visualType": "cardVisual",
            "query": {"queryState": {"Data": {"projections": projs}}},
            "drillFilterOtherVisuals": False,
            "objects": {
                "background": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "transparency": {"expr": {"Literal": {"Value": "82D"}}},
                        }
                    }
                ],
                "border": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#DCE3F0'"}}}}},
                            "width": {"expr": {"Literal": {"Value": "1D"}}},
                        }
                    }
                ],
            },
        },
    }


def bar_metroy(
    name: str,
    x: float,
    y: float,
    w: float,
    h: float,
    z: int,
    y_measures: list[str],
    chart_title: str,
) -> dict:
    cats = [
        {
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": "metro"}},
            "queryRef": "GoldRenewalScores.metro",
            "active": True,
        }
    ]
    ys = []
    for m in y_measures:
        ys.append(
            {
                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": m}},
                "queryRef": f"GoldRenewalScores.{m}",
                "nativeQueryRef": m,
            }
        )
    return {
        "$schema": SCHEMA_VIS,
        "name": name,
        "position": {"x": x, "y": y, "z": float(z), "width": w, "height": h, "tabOrder": z},
        "visual": {
            "visualType": "clusteredBarChart",
            "query": {"queryState": {"Category": {"projections": cats}, "Y": {"projections": ys}}},
            "objects": title_objects(chart_title),
            "drillFilterOtherVisuals": True,
        },
    }


def donut_cat_measure(
    name: str,
    x: float,
    y: float,
    w: float,
    h: float,
    z: int,
    cat_col: str,
    measure: str,
    chart_title: str,
) -> dict:
    """Donut / ring visual — aligns with layered ‘O’ brand metaphor in dashboards only."""
    cats = [
        {
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": cat_col}},
            "queryRef": f"GoldRenewalScores.{cat_col}",
            "active": True,
        }
    ]
    ys = [
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": measure}},
            "queryRef": f"GoldRenewalScores.{measure}",
            "nativeQueryRef": measure,
        }
    ]
    return {
        "$schema": SCHEMA_VIS,
        "name": name,
        "position": {"x": x, "y": y, "z": float(z), "width": w, "height": h, "tabOrder": z},
        "visual": {
            "visualType": "donutChart",
            "query": {"queryState": {"Category": {"projections": cats}, "Y": {"projections": ys}}},
            "objects": title_objects(chart_title),
            "drillFilterOtherVisuals": True,
        },
    }


def line_chart_month(
    name: str,
    x: float,
    y: float,
    w: float,
    h: float,
    z: int,
    y_measures: list[str],
    chart_title: str,
) -> dict:
    cats = [
        {
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": "leased_month"}},
            "queryRef": "GoldRenewalScores.leased_month",
            "active": True,
        }
    ]
    ys = []
    for m in y_measures:
        ys.append(
            {
                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": m}},
                "queryRef": f"GoldRenewalScores.{m}",
                "nativeQueryRef": m,
            }
        )
    return {
        "$schema": SCHEMA_VIS,
        "name": name,
        "position": {"x": x, "y": y, "z": float(z), "width": w, "height": h, "tabOrder": z},
        "visual": {
            "visualType": "lineChart",
            "query": {"queryState": {"Category": {"projections": cats}, "Y": {"projections": ys}}},
            "objects": title_objects(chart_title),
            "drillFilterOtherVisuals": True,
        },
    }


def stacked_col_series(
    name: str,
    x: float,
    y: float,
    w: float,
    h: float,
    z: int,
    category_col: str,
    legend_col: str,
    y_measures: list[str],
    chart_title: str,
) -> dict:
    cats = [
        {
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": category_col}},
            "queryRef": f"GoldRenewalScores.{category_col}",
            "active": True,
        }
    ]
    series = [
        {
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": legend_col}},
            "queryRef": f"GoldRenewalScores.{legend_col}",
            "active": True,
        }
    ]
    ys = []
    for m in y_measures:
        ys.append(
            {
                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": m}},
                "queryRef": f"GoldRenewalScores.{m}",
                "nativeQueryRef": m,
            }
        )
    return {
        "$schema": SCHEMA_VIS,
        "name": name,
        "position": {"x": x, "y": y, "z": float(z), "width": w, "height": h, "tabOrder": z},
        "visual": {
            "visualType": "clusteredColumnChart",
            "query": {"queryState": {"Category": {"projections": cats}, "Series": {"projections": series}, "Y": {"projections": ys}}},
            "objects": title_objects(chart_title),
            "drillFilterOtherVisuals": True,
        },
    }


def brand_mix_bar_cat_measure(
    name: str,
    x: float,
    y: float,
    w: float,
    h: float,
    z: int,
    cat_col: str,
    measure: str,
    chart_title: str,
) -> dict:
    """Horizontal clustered bar — reliable PBIR substitute for treemap on single category + one measure."""
    cats = [
        {
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": cat_col}},
            "queryRef": f"GoldRenewalScores.{cat_col}",
            "active": True,
        }
    ]
    ys = [
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": measure}},
            "queryRef": f"GoldRenewalScores.{measure}",
            "nativeQueryRef": measure,
        }
    ]
    return {
        "$schema": SCHEMA_VIS,
        "name": name,
        "position": {"x": x, "y": y, "z": float(z), "width": w, "height": h, "tabOrder": z},
        "visual": {
            "visualType": "clusteredBarChart",
            "query": {"queryState": {"Category": {"projections": cats}, "Y": {"projections": ys}}},
            "objects": title_objects(chart_title),
            "drillFilterOtherVisuals": True,
        },
    }


def slicer_dropdown_column(
    name: str,
    x: float,
    y: float,
    w: float,
    h: float,
    z: int,
    column: str,
    header: str,
) -> dict:
    """Dropdown slicer — filters other visuals when report defaultFilterActionIsDataFilter is true."""
    proj = [
        {
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": column}},
            "queryRef": f"GoldRenewalScores.{column}",
            "nativeQueryRef": column,
            "active": True,
        }
    ]
    return {
        "$schema": SCHEMA_VIS,
        "name": name,
        "position": {"x": x, "y": y, "z": float(z), "width": w, "height": h, "tabOrder": z},
        "visual": {
            "visualType": "slicer",
            "query": {"queryState": {"Values": {"projections": proj}}},
            "objects": {
                **title_objects(header),
                "data": [
                    {
                        "properties": {
                            "mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}},
                        }
                    }
                ],
            },
            "drillFilterOtherVisuals": True,
        },
    }


def scatter_rent_vs_model(
    name: str,
    x: float,
    y: float,
    w: float,
    h: float,
    z: int,
    legend_col: str,
    chart_title: str,
) -> dict:
    legend = [
        {
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": legend_col}},
            "queryRef": f"GoldRenewalScores.{legend_col}",
            "active": True,
        }
    ]
    x_axis = [
        {
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": "monthly_rent"}},
            "queryRef": "GoldRenewalScores.monthly_rent",
            "active": True,
        }
    ]
    y_axis = [
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": "renewal_probability_ml"}},
            "queryRef": "GoldRenewalScores.renewal_probability_ml",
            "nativeQueryRef": "renewal_probability_ml",
        }
    ]
    return {
        "$schema": SCHEMA_VIS,
        "name": name,
        "position": {"x": x, "y": y, "z": float(z), "width": w, "height": h, "tabOrder": z},
        "visual": {
            "visualType": "scatterChart",
            "query": {"queryState": {"Series": {"projections": legend}, "X": {"projections": x_axis}, "Y": {"projections": y_axis}}},
            "objects": title_objects(chart_title),
            "drillFilterOtherVisuals": True,
        },
    }


def col_cat(
    name: str,
    x: float,
    y: float,
    w: float,
    h: float,
    z: int,
    cat_col: str,
    y_measures: list[str],
    chart_title: str,
) -> dict:
    cats = [
        {
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": cat_col}},
            "queryRef": f"GoldRenewalScores.{cat_col}",
            "active": True,
        }
    ]
    ys = []
    for m in y_measures:
        ys.append(
            {
                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}}, "Property": m}},
                "queryRef": f"GoldRenewalScores.{m}",
                "nativeQueryRef": m,
            }
        )
    return {
        "$schema": SCHEMA_VIS,
        "name": name,
        "position": {"x": x, "y": y, "z": float(z), "width": w, "height": h, "tabOrder": z},
        "visual": {
            "visualType": "clusteredColumnChart",
            "query": {"queryState": {"Category": {"projections": cats}, "Y": {"projections": ys}}},
            "objects": title_objects(chart_title),
            "drillFilterOtherVisuals": True,
        },
    }


def main() -> None:
    load_repo_dotenv()
    root = Path(__file__).resolve().parents[1]
    report_def = root / "powerbi" / "CoreSpacesRenewal.Report" / "definition"
    base = report_def / "pages"

    research_dir = root / "research" / "core_spaces"
    opp_md = research_dir / "opportunity_map.md"
    comp_md = research_dir / "competitive_landscape.md"
    for p in (opp_md, comp_md):
        if not p.is_file():
            raise SystemExit(f"Missing expected research markdown: {p}")
    hero_opp = hero_strings_opportunity(opp_md)
    hero_comp = hero_strings_competition(comp_md)
    digest_op, digest_comp = research_callout_lines(opp_md, comp_md)

    card_w = 286
    card_gap = 14
    card_y = 200
    card_h = 128
    card_left = 48

    chrome_r = chrome_bottom_reserve()

    # Executive
    pid = "aa10_exec_overview"
    write_json(base / pid / "page.json", page_stub(pid, "Executive"))
    write_json(
        base / pid / "visuals/vhero/visual.json",
        hero_textbox(
            "ex_hero",
            0,
            "Portfolio renewal intelligence",
            "Who renews next—and where economics tilt?",
            (
                "Synthetic leases anchor three beats: geo economics (metro + ecosystem lanes), modeled churn tiers "
                "(risk ladder + leasing posture), and lineage-friendly gold exports for BI—without claiming proprietary ops."
            ),
            "Refresh gold CSV after each score run; bookmark navigator carries the narrative spine.",
            width=764,
        ),
    )
    write_json(
        base / pid / "visuals/vdonuteco/visual.json",
        donut_cat_measure(
            "ex_donut_eco",
            828,
            18,
            404,
            156,
            2148,
            "ecosystem_segment",
            "Gold Lease Rows",
            "Lease volume by ecosystem lane (synthetic portfolio)",
        ),
    )

    kpis_exec = ["Renewal Actual Rate %", "Avg Predicted Renewal Prob", "Gold Lease Rows", "Median Monthly Rent $"]
    for i, meas in enumerate(kpis_exec):
        x = card_left + i * (card_w + card_gap)
        write_json(base / pid / f"visuals/vcard{i}/visual.json", card_visual(f"ex_card{i}", x, card_y, card_w, card_h, 1500 + i, [meas]))

    slicer_y_ex = float(card_y + card_h + 6)
    slicer_h_ex = 74.0
    slicer_gap_ex = 12.0
    sw_sl = (PAGE_W - 2 * card_left - 2 * slicer_gap_ex) / 3
    for i, (col, hdr) in enumerate(
        [("metro", "Metro"), ("ecosystem_segment", "Ecosystem"), ("risk_tier", "Risk tier")]
    ):
        write_json(
            base / pid / f"visuals/vslicer{i}/visual.json",
            slicer_dropdown_column(
                f"ex_slicer_{col}",
                card_left + i * (sw_sl + slicer_gap_ex),
                slicer_y_ex,
                sw_sl,
                slicer_h_ex,
                1380 + i,
                col,
                hdr,
            ),
        )

    charts_y = slicer_y_ex + slicer_h_ex + 14
    chart_h = PAGE_H - charts_y - chrome_r

    split_gap_ex = 20.0
    split_w_ex = (PAGE_W - 2 * card_left - split_gap_ex) / 2
    write_json(
        base / pid / "visuals/vbar/visual.json",
        bar_metroy(
            "ex_bar",
            card_left,
            charts_y,
            split_w_ex,
            chart_h,
            2100,
            ["Renewal Actual Rate %", "Avg Predicted Renewal Prob"],
            "Renewal actuals vs modeled probability — by metro cohort",
        ),
    )
    write_json(
        base / pid / "visuals/vtreemapbrandexec/visual.json",
        brand_mix_bar_cat_measure(
            "ex_tree_brand",
            card_left + split_w_ex + split_gap_ex,
            charts_y,
            split_w_ex,
            chart_h,
            2160,
            "brand_line",
            "Gold Lease Rows",
            "Synthetic brand concentration — complements metro posture view",
        ),
    )

    pid = "aa20_operations"
    slicer_y_op = 174.0
    slicer_h_op = 88.0
    slicer_gap_op = 12.0
    sw_op = (PAGE_W - 2 * card_left - 2 * slicer_gap_op) / 3
    for i, (col, hdr) in enumerate(
        [("metro", "Metro"), ("ecosystem_segment", "Ecosystem"), ("flagship_style", "Flagship style")]
    ):
        write_json(
            base / pid / f"visuals/vslicer{i}/visual.json",
            slicer_dropdown_column(
                f"op_slicer_{col}",
                card_left + i * (sw_op + slicer_gap_op),
                slicer_y_op,
                sw_op,
                slicer_h_op,
                1380 + i,
                col,
                hdr,
            ),
        )

    deck_top_op = slicer_y_op + slicer_h_op + 14.0
    deck_h = float(PAGE_H - deck_top_op - chrome_r - 12.0)

    split_gap = 20.0
    split_w = (PAGE_W - 2 * card_left - split_gap) / 2

    write_json(base / pid / "page.json", page_stub(pid, "Operations & leasing"))
    write_json(
        base / pid / "visuals/vhero/visual.json",
        hero_textbox(
            "op_hero",
            0,
            "Portfolio operations",
            "Leasing posture by modeled risk tier",
            "Operational read on renewal stress for asset + onsite teams—velocity, service load, and modeled churn.",
            "All tiers are heuristic labels over synthetic renewal scores (D = highest modeled churn sensitivity).",
            top=16,
            height=152,
        ),
    )
    write_json(
        base / pid / "visuals/vcol/visual.json",
        col_cat(
            "op_col",
            card_left,
            deck_top_op,
            split_w,
            deck_h,
            2000,
            "risk_tier",
            ["Renewal Actual Rate %", "Avg Predicted Renewal Prob"],
            "Renewal posture by modeled risk ladder",
        ),
    )
    write_json(
        base / pid / "visuals/vcoleco/visual.json",
        col_cat(
            "op_colec",
            card_left + split_w + split_gap,
            deck_top_op,
            split_w,
            deck_h,
            2050,
            "ecosystem_segment",
            ["Renewal Actual Rate %", "Avg Predicted Renewal Prob"],
            "Same signals by synthetic ecosystem lane (student · BFR · hybrid)",
        ),
    )

    charts_y = card_y + card_h + 26
    chart_h = PAGE_H - charts_y - chrome_r

    pid = "aa30_finance"
    write_json(base / pid / "page.json", page_stub(pid, "Finance & asset economics"))
    write_json(
        base / pid / "visuals/vhero/visual.json",
        hero_textbox(
            "fn_hero",
            0,
            "Asset economics lens",
            "Rent intensity vs modeled renewal softness",
            "Synthetic exposures for JV / lender conversations — underwriting stays illustrative until real rent rolls land.",
            "Bars pair median vs average monthly rent proxies to spotlight distribution skew.",
        ),
    )

    kpis_fin = ["Median Monthly Rent $", "Avg Monthly Rent $", "Avg Risk Score", "Distinct Dataset Versions"]
    for i, meas in enumerate(kpis_fin):
        x = card_left + i * (card_w + card_gap)
        write_json(base / pid / f"visuals/vcard{i}/visual.json", card_visual(f"fn_card{i}", x, card_y, card_w, card_h, 1500 + i, [meas]))

    split_gap_fn = 20.0
    split_w_fn = (PAGE_W - 2 * card_left - split_gap_fn) / 2
    write_json(
        base / pid / "visuals/vbar/visual.json",
        bar_metroy(
            "fn_bar",
            card_left,
            charts_y,
            split_w_fn,
            chart_h,
            2100,
            ["Median Monthly Rent $", "Avg Monthly Rent $"],
            "Rent curve by metro — underwriting-friendly orientation",
        ),
    )
    write_json(
        base / pid / "visuals/vflag/visual.json",
        col_cat(
            "fn_flag",
            card_left + split_w_fn + split_gap_fn,
            charts_y,
            split_w_fn,
            chart_h,
            2150,
            "flagship_style",
            ["Avg Risk Score"],
            "Modeled churn sensitivity by flagship style archetype",
        ),
    )

    pid = "aa40_marketing"
    cy2 = card_y - 52
    ch2 = PAGE_H - cy2 - chrome_r
    write_json(base / pid / "page.json", page_stub(pid, "Marketing & velocity"))
    write_json(
        base / pid / "visuals/vhero/visual.json",
        hero_textbox(
            "mk_hero",
            0,
            "Go-to-market timing",
            "Where lease-origin months cluster on renewal lifts",
            "Think of leased_month as a lightweight surrogate for funnel timing when CRM payloads are detached.",
            "Pair actual renewals against ML probability so marketing + ops narratives stay aligned.",
            top=16,
            height=152,
        ),
    )
    split_gap_mk = 20.0
    split_w_mk = (PAGE_W - 2 * card_left - split_gap_mk) / 2
    deck_mk = ch2 - 146 - 20
    write_json(
        base / pid / "visuals/vcol/visual.json",
        col_cat(
            "mk_col",
            card_left,
            cy2 + 146,
            split_w_mk,
            deck_mk,
            2000,
            "leased_month",
            ["Renewal Actual Rate %", "Avg Predicted Renewal Prob"],
            "Cohort pacing — leases originating by month stamp",
        ),
    )
    write_json(
        base / pid / "visuals/vcolmetrocluster/visual.json",
        col_cat(
            "mk_mc",
            card_left + split_w_mk + split_gap_mk,
            cy2 + 146,
            split_w_mk,
            deck_mk,
            2050,
            "metro_cluster",
            ["Renewal Actual Rate %", "Avg Predicted Renewal Prob"],
            "Renewals by metro archetype cluster (portfolio fiction)",
        ),
    )

    pid = "aa50_governance"
    write_json(base / pid / "page.json", page_stub(pid, "Governance & lineage"))
    write_json(
        base / pid / "visuals/vhero/visual.json",
        hero_textbox(
            "gv_hero",
            0,
            "Responsible AI + dataset hygiene",
            "Controls you can storytell around an enterprise warehouse",
            "dataset_version_id, mlflow_run_id vs local_pickles, scored_at, model_name baked into synthetic gold feeds.",
            "MetaPortfolio holds narrative FAQ rows; extend the semantic model when you wire real systems of record.",
            top=16,
            height=168,
        ),
    )

    gv_kpis = ["Distinct Dataset Versions", "Avg Predicted Renewal Prob", "Gold Lease Rows"]
    gv_w = 390
    for i, meas in enumerate(gv_kpis):
        x = card_left + i * (gv_w + card_gap)
        write_json(base / pid / f"visuals/vcard{i}/visual.json", card_visual(f"gv_card{i}", x, 214, gv_w, 122, 1500 + i, [meas]))

    write_json(
        base / pid / "visuals/vnotes/visual.json",
        hero_textbox(
            "gv_notes",
            1,
            "MetaPortfolio",
            "Operational FAQ anchored in the semantic model",
            "Use these rows alongside gold renewals when you explain versioning, pickles vs MLflow, and dataset discipline.",
            "Keep MetaPortfolio orthogonal to facts tables (no hidden joins) unless you extend the schema on purpose.",
            top=382,
            height=154,
        ),
    )

    # AI platform / Fabric stance — grounded in copilot_topics_manifest.json when generated
    pid = "aa55_ai_platform"
    ai_eb, ai_hd, ai_ld, ai_wh = ai_platform_hero_copy(root)
    copilot_m = root / "research" / "copilot_topics_manifest.json"
    ai_whisper = ai_wh + (f" Manifest UTC stamp {utc_stamp(copilot_m)}." if copilot_m.is_file() else "")
    write_json(base / pid / "page.json", page_stub(pid, "AI platform & Fabric"))
    write_json(
        base / pid / "visuals/vhero/visual.json",
        hero_textbox(
            "ai_hero",
            0,
            ai_eb,
            ai_hd,
            ai_ld,
            ai_whisper,
            top=22,
            height=158,
            width=PAGE_W - 96,
        ),
    )
    ai_cards = ["Distinct Dataset Versions", "Gold Lease Rows", "Avg Predicted Renewal Prob", "Median Monthly Rent $"]
    ai_w = 286
    ai_y = 212
    ai_h = 122
    for i, meas in enumerate(ai_cards):
        x = card_left + i * (ai_w + card_gap)
        write_json(base / pid / f"visuals/vcard{i}/visual.json", card_visual(f"ai_card{i}", x, ai_y, ai_w, ai_h, 1500 + i, [meas]))
    ai_chrome_rr = chrome_bottom_reserve()
    ai_ch_top = ai_y + ai_h + 22
    ai_ch_h = PAGE_H - ai_ch_top - ai_chrome_rr
    ai_gap = 18.0
    ai_upper_h = ai_ch_h * 0.52
    ai_lower_y = ai_ch_top + ai_upper_h + ai_gap
    ai_lower_h = max(168.0, PAGE_H - ai_lower_y - ai_chrome_rr - 14.0)
    ai_mid = (PAGE_W - 2 * card_left - ai_gap) / 2
    write_json(
        base / pid / "visuals/vmodelmix/visual.json",
        col_cat(
            "ai_model_mix",
            card_left,
            ai_ch_top,
            ai_mid,
            ai_upper_h,
            2100,
            "model_name",
            ["Renewal Actual Rate %", "Avg Predicted Renewal Prob"],
            "Model lineage posture — renewal lift vs calibrated probability",
        ),
    )
    write_json(
        base / pid / "visuals/vversions/visual.json",
        donut_cat_measure(
            "ai_versions",
            card_left + ai_mid + ai_gap,
            ai_ch_top,
            ai_mid,
            ai_upper_h,
            2150,
            "dataset_version_id",
            "Gold Lease Rows",
            "Dataset versions landed in synthetic gold — mimics UC revision audits",
        ),
    )
    write_json(
        base / pid / "visuals/vstackplat/visual.json",
        stacked_col_series(
            "ai_stack_metro_eco",
            card_left,
            ai_lower_y,
            PAGE_W - 2 * card_left,
            ai_lower_h,
            2300,
            "metro",
            "ecosystem_segment",
            ["Renewal Actual Rate %"],
            "Fabric-ready segmentation — metro × ecosystem renewal actuals",
        ),
    )

    # Opportunity deep dive — hero + appendix text regenerated from opportunity_map.md
    pid = "aa60_opportunity_lab"
    write_json(base / pid / "page.json", page_stub(pid, "Opportunity deep dive"))
    chrome_rr = chrome_bottom_reserve()
    trio_y = 246.0
    trio_h = 348.0
    gw = 379.0
    gspace = 22.0
    write_json(
        base / pid / "visuals/vhero/visual.json",
        hero_textbox(
            "opp_hero",
            0,
            hero_opp[0],
            hero_opp[1],
            hero_opp[2],
            f"Synthetic KPIs · research source last updated {utc_stamp(opp_md)} (UTC file date)",
            top=26,
            height=140,
            width=734,
        ),
    )
    write_json(
        base / pid / "visuals/vdigest/visual.json",
        multiline_notes_textbox(
            "opp_digest",
            8,
            800.0,
            26.0,
            432.0,
            218.0,
            "Structured digest (parsed in-repo)",
            digest_op,
        ),
    )
    write_json(
        base / pid / "visuals/vdoneco/visual.json",
        donut_cat_measure("opp_eco", 48.0, trio_y, gw, trio_h, 2100, "ecosystem_segment", "Gold Lease Rows", "Concentration by ecosystem lane"),
    )
    write_json(
        base / pid / "visuals/vlinecohort/visual.json",
        line_chart_month(
            "opp_lines",
            48 + gw + gspace,
            trio_y,
            gw,
            trio_h,
            2150,
            ["Renewal Actual Rate %", "Avg Predicted Renewal Prob"],
            "Cohort trend — renewal lift vs modeled probability",
        ),
    )
    write_json(
        base / pid / "visuals/vtreemapbrand/visual.json",
        brand_mix_bar_cat_measure(
            "opp_tree",
            48 + 2 * (gw + gspace),
            trio_y,
            gw,
            trio_h,
            2200,
            "brand_line",
            "Gold Lease Rows",
            "Portfolio weight inside synthetic brand lines",
        ),
    )
    stk_y = trio_y + trio_h + 26.0
    stk_h = max(210.0, float(PAGE_H) - stk_y - chrome_rr - 24.0)
    write_json(
        base / pid / "visuals/vstackrisk/visual.json",
        stacked_col_series(
            "opp_stack",
            card_left,
            stk_y,
            PAGE_W - 2 * card_left,
            stk_h,
            2300,
            "risk_tier",
            "ecosystem_segment",
            ["Renewal Actual Rate %"],
            "Stacked renewal rate — modeled risk ladder × ecosystem lane",
        ),
    )

    # Competitive intelligence — hero + appendix from competitive_landscape.md
    pid = "aa70_competition_lens"
    write_json(base / pid / "page.json", page_stub(pid, "Competitive intelligence"))
    write_json(
        base / pid / "visuals/vhero/visual.json",
        hero_textbox(
            "co_hero",
            0,
            hero_comp[0],
            hero_comp[1],
            hero_comp[2],
            f"Synthetic portfolio only · competitive copy last aligned to disk {utc_stamp(comp_md)} (UTC file date)",
            top=26,
            height=144,
            width=734,
        ),
    )
    write_json(
        base / pid / "visuals/vdigest/visual.json",
        multiline_notes_textbox(
            "co_digest",
            8,
            800.0,
            26.0,
            432.0,
            218.0,
            "Peer map excerpt (parsed in-repo)",
            digest_comp,
        ),
    )
    sc_y = 258.0
    sc_h = 322.0
    write_json(
        base / pid / "visuals/vscatterrent/visual.json",
        scatter_rent_vs_model(
            "co_scatter",
            card_left,
            sc_y,
            596.0,
            sc_h,
            2600,
            "ecosystem_segment",
            "Rent vs modeled renewal probability (color = ecosystem lane)",
        ),
    )
    write_json(
        base / pid / "visuals/vlinemacro/visual.json",
        line_chart_month(
            "co_lines",
            664.0,
            sc_y,
            568.0,
            sc_h,
            2650,
            ["Median Monthly Rent $", "Avg Risk Score"],
            "Macro-style pressure curve — rents vs modeled softness by lease cohort",
        ),
    )
    st2_y = sc_y + sc_h + 24.0
    st2_h = max(200.0, float(PAGE_H) - st2_y - chrome_rr - 22.0)
    write_json(
        base / pid / "visuals/vstackmetro/visual.json",
        stacked_col_series(
            "co_stack",
            card_left,
            st2_y,
            PAGE_W - 2 * card_left,
            st2_h,
            2700,
            "metro_cluster",
            "flagship_style",
            ["Gold Lease Rows"],
            "Mix of synthetic communities — metro archetype × flagship posture",
        ),
    )

    # Drill detail page — regenerate hero + shrink charts above chrome strip
    pid = "eef0portfoliorenew01"
    write_json(
        base / pid / "page.json",
        {
            "$schema": SCHEMA_PG,
            "name": pid,
            "displayName": "Renewal drilldown",
            "displayOption": "FitToPage",
            "height": PAGE_H,
            "width": PAGE_W,
            "objects": {
                "outspacePane": [
                    {
                        "properties": {
                            "width": {"expr": {"Literal": {"Value": "200L"}}},
                        }
                    }
                ],
                "background": [
                    {
                        "properties": {
                            "color": {
                                "solid": {"color": {"expr": {"Literal": {"Value": CREAM}}}}
                            },
                            "transparency": {"expr": {"Literal": {"Value": "0D"}}},
                        }
                    }
                ],
            },
        },
    )

    dv_h = PAGE_H - 206 - chrome_r - 14
    write_json(
        base / pid / "visuals/vtexttitle01/visual.json",
        {
            "$schema": SCHEMA_VIS,
            "name": "vtexttitle01",
            "position": {"x": 48, "y": 16, "z": 1000, "height": 168, "width": 1108, "tabOrder": 1000},
            "visual": {
                "visualType": "textbox",
                "objects": {
                    "general": [
                        {
                            "properties": {
                                "paragraphs": [
                                    {
                                        "textRuns": [
                                            {
                                                "value": "Drill corridor · modeled lease renewals",
                                                "textStyle": {"fontFace": "Segoe UI Semibold", "fontSize": 11, "color": "#3F68EB"},
                                            }
                                        ]
                                    },
                                    {
                                        "textRuns": [
                                            {
                                                "value": "Metro vs risk tier juxtaposition",
                                                "textStyle": {"fontFace": "Segoe UI Semibold", "fontSize": 34},
                                            }
                                        ]
                                    },
                                    {
                                        "textRuns": [
                                            {
                                                "value": (
                                                    "Grain includes dataset_version_id, mlflow_run_id "
                                                    "(or pickle token fallback), scored_at — slice for interviewer-led probes."
                                                ),
                                                "textStyle": {"fontFace": "Segoe UI", "fontSize": 13.5},
                                            }
                                        ]
                                    },
                                ]
                            }
                        },
                    ]
                },
                "drillFilterOtherVisuals": False,
            },
        },
    )

    metro_chart = bar_metroy(
        "vbarmetro01",
        48,
        206,
        582,
        dv_h,
        2000,
        ["Renewal Actual Rate %", "Avg Predicted Renewal Prob"],
        "Renewal actuals vs model — by metro",
    )
    metro_chart["visual"]["query"]["sortDefinition"] = {
        "sort": [
            {
                "field": {
                    "Measure": {
                        "Expression": {"SourceRef": {"Entity": "GoldRenewalScores"}},
                        "Property": "Renewal Actual Rate %",
                    }
                },
                "direction": "Descending",
            }
        ]
    }
    metro_chart["visual"]["objects"]["title"][0]["properties"]["fontSize"] = {"expr": {"Literal": {"Value": "13D"}}}
    metro_chart["visual"]["objects"]["title"][0]["properties"]["fontFamily"] = {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}}
    write_json(base / pid / "visuals/vbarmetro01/visual.json", metro_chart)

    tier_chart = col_cat(
        "vcoltier01",
        650,
        206,
        582,
        dv_h,
        3000,
        "risk_tier",
        ["Renewal Actual Rate %", "Avg Predicted Renewal Prob"],
        "Mix by modeled risk decile (D1 = lowest churn risk)",
    )
    tier_chart["visual"]["objects"]["title"][0]["properties"]["fontSize"] = {"expr": {"Literal": {"Value": "13D"}}}
    tier_chart["visual"]["objects"]["title"][0]["properties"]["fontFamily"] = {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}}
    write_json(base / pid / "visuals/vcoltier01/visual.json", tier_chart)

    write_global_chrome_and_bookmarks(report_def, root)

    pages_order = [
        "aa10_exec_overview",
        "aa20_operations",
        "aa30_finance",
        "aa40_marketing",
        "aa50_governance",
        "aa55_ai_platform",
        "aa60_opportunity_lab",
        "aa70_competition_lens",
        "eef0portfoliorenew01",
    ]
    write_json(
        base / "pages.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
            "pageOrder": pages_order,
            "activePageName": "aa10_exec_overview",
        },
    )
    print("OK", pages_order)


if __name__ == "__main__":
    main()
