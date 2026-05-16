#!/usr/bin/env python3
"""Write illustrative README preview PNGs under screenshots/ (synthetic, not live captures)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _fonts() -> tuple[ImageFont.ImageFont, ImageFont.ImageFont, ImageFont.ImageFont]:
    pairs: list[tuple[Path, Path]] = [
        (
            Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
            Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        ),
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ),
    ]
    default = ImageFont.load_default()
    for bold_path, regular_path in pairs:
        if not bold_path.is_file() or not regular_path.is_file():
            continue
        try:
            return (
                ImageFont.truetype(str(bold_path), 44),
                ImageFont.truetype(str(regular_path), 26),
                ImageFont.truetype(str(regular_path), 20),
            )
        except OSError:
            continue
    return default, default, default


def _card(path: Path, *, title: str, lines: tuple[str, ...], accent: tuple[int, int, int]) -> None:
    w, h = 1280, 720
    bg = (15, 23, 36)
    img = Image.new("RGB", (w, h), color=bg)
    draw = ImageDraw.Draw(img)
    title_f, body_f, small_f = _fonts()

    draw.rectangle([0, 0, w, 6], fill=accent)
    y = 100
    draw.text((72, y), title, fill=(238, 242, 255), font=title_f)
    y += 72
    for line in lines:
        draw.text((72, y), line, fill=(180, 190, 210), font=body_f)
        y += 40
    foot = "Synthetic portfolio preview — not proprietary or tenant production data."
    draw.text((72, h - 64), foot, fill=(120, 132, 156), font=small_f)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=True)


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    out = repo / "screenshots"
    _card(
        out / "powerbi_overview.png",
        title="Power BI — Renewal intelligence (demo)",
        lines=(
            "PBIP storyline: segments, renewal scores, governance callouts",
            "Open CoreSpacesRenewal.pbip in Power BI Desktop to explore the full model",
        ),
        accent=(0, 120, 212),
    )
    _card(
        out / "renewal_lens_app.png",
        title="Renewal Lens — Databricks App (concept)",
        lines=(
            "Streamlit path under databricks/apps/renewal_lens/",
            "Parquet gold by default; optional SQL warehouse / governed table",
        ),
        accent=(36, 158, 163),
    )
    _card(
        out / "monitoring_output.png",
        title="Monitoring — PSI & schema drift (illustrative)",
        lines=(
            "Executable scripts: monitoring/psi_check.py, scripts/monitoring_psi_schema.py",
            "CI smoke in .github/workflows/validate.yml — alerts are design intent",
        ),
        accent=(245, 158, 11),
    )
    print("Wrote:", out / "powerbi_overview.png")
    print("Wrote:", out / "renewal_lens_app.png")
    print("Wrote:", out / "monitoring_output.png")


if __name__ == "__main__":
    main()
