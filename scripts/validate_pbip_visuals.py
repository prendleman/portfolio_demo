#!/usr/bin/env python3
"""Cheap structural validation for programmatically generated Fabric / PBIR visuals.

Power BI Desktop is still authoritative for semantic rendering; this catches missing buckets and JSON typos early.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def req(qs: dict, keys: tuple[str, ...]) -> list[str]:
    missing = [k for k in keys if k not in qs or not qs.get(k)]
    return [f"missing projection {k!r}" for k in missing]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    pages = root / "powerbi" / "CoreSpacesRenewal.Report" / "definition" / "pages"
    errors: list[str] = []

    for vjson in sorted(pages.rglob("**/visuals/*/visual.json")):
        doc = json.loads(vjson.read_text(encoding="utf-8"))
        vis = doc.get("visual") if isinstance(doc, dict) else None
        if not isinstance(vis, dict):
            continue
        vt = vis.get("visualType")
        qs = vis.get("query", {}).get("queryState", {})

        vt_errors: list[str] = []
        if vt in {"clusteredBarChart"}:
            vt_errors.extend(req(qs, ("Category", "Y")))
        elif vt == "clusteredColumnChart":
            vt_errors.extend(req(qs, ("Category", "Y")))
        elif vt in {"donutChart", "pieChart"}:
            vt_errors.extend(req(qs, ("Category", "Y")))
        elif vt == "lineChart":
            vt_errors.extend(req(qs, ("Category", "Y")))
        elif vt == "scatterChart":
            vt_errors.extend(req(qs, ("Series", "X", "Y")))
        elif vt == "cardVisual":
            vt_errors.extend(req(qs, ("Data",)))
        elif vt == "slicer":
            vt_errors.extend(req(qs, ("Values",)))
        elif vt in {"image", "textbox", "bookmarkNavigator"}:
            continue

        for e in vt_errors:
            errors.append(f"{vjson.relative_to(root)} ({vt}) — {e}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    visuals = sorted(pages.rglob("**/visuals/*/visual.json"))
    print(f"OK - checked {len(visuals)} visual.json files under definition/pages/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
