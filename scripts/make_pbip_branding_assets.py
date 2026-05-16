#!/usr/bin/env python3
"""Generate registered image assets for PBIP (wallpaper + layered ring mark).

Drop an official PNG at ``branding/logomark.png`` to override everything. Otherwise, if you've run
``scripts/fetch_corespaces_live_logo.py``, the importer uses ``branding/logomark_from_live_site.png``.
When neither exists, synthesizes a layered "O".
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter  # type: ignore[import-not-found]
except ImportError as e:  # pragma: no cover
    raise SystemExit("Pillow is required. Install with: pip install Pillow") from e

BOTTOM_SWATCH = "#EDE7F9"
# Four bands + solid white core (matches brand-style “nested O”: dark outer → violet → blue → lavender).
RING_BANDS_HEX = ["#291452", "#5B29D9", "#3D7FFB", "#B9AEF5"]
CORE_WHITE = "#FFFFFF"

# Harmonize with mask-icon violet + site blues (public cues only). Geometry is illustrative, not traced IP.


def bookmark_id(page_folder: str) -> str:
    return hashlib.sha1(f"bkmk:cscore:{page_folder}".encode()).hexdigest()[:20]


def _parse_rgb(hex_rgb: str) -> tuple[int, int, int]:
    hx = hex_rgb.lstrip("#")
    return int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)


def make_wallpaper(path: Path, w: int = 2400, h: int = 1350, *, accent_bottom: str = BOTTOM_SWATCH) -> None:
    canvas = Image.new("RGB", (w, h), "#FAF8F4")
    bottom_px = _parse_rgb(accent_bottom)

    overlay = Image.new("RGB", (w, h))
    od = ImageDraw.Draw(overlay)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(round(250 + (bottom_px[0] - 250) * t * 0.35))
        g = int(round(248 + (bottom_px[1] - 248) * t * 0.5))
        b = int(round(244 + (bottom_px[2] - 244) * t * 0.55))
        od.line([(0, y), (w, y)], fill=(r, g, b))
    blended = Image.blend(canvas, overlay, alpha=0.42)

    seed = []
    x = 0x9E3779B9
    for i in range(w * h):
        x = (x ^ (x << 13) ^ (x >> 17) ^ i) & 0xFFFFFFFF
        seed.append(x % 24)
    noise = Image.new("L", (w, h))
    nd = noise.load()
    i = 0
    for yy in range(h):
        for xx in range(w):
            nd[xx, yy] = 228 + seed[i % len(seed)]
            i += 1
    noise = noise.filter(ImageFilter.GaussianBlur(radius=2.2))
    n_rgb = Image.merge("RGB", (noise, noise, noise))
    img = Image.blend(blended, n_rgb, alpha=0.028)

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=True)


def make_logo_layered_o(path: Path, sz: int = 512, *, supersample: int = 4) -> None:
    """Concentric bands + white core — filled annuli read as layered rings when downsampled."""
    s = sz * supersample
    canvas = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    cx = cy = s / 2.0

    margin = max(14, int(round(s * 0.036)))
    r_outer = s / 2.0 - margin
    r_core = max(36.0, r_outer * 0.26)

    bands = [*RING_BANDS_HEX, CORE_WHITE]
    n = len(bands)
    step = (r_outer - r_core) / max(n - 1, 1)

    for i, hex_c in enumerate(bands):
        r = r_outer - i * step
        bbox = (cx - r, cy - r, cx + r, cy + r)
        d.ellipse(bbox, fill=_parse_rgb(hex_c) + (255,))

    logo = canvas.resize((sz, sz), resample=Image.Resampling.LANCZOS)

    path.parent.mkdir(parents=True, exist_ok=True)
    logo.save(path, format="PNG", optimize=True)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    reg = root / "powerbi" / "CoreSpacesRenewal.Report" / "StaticResources" / "RegisteredResources"
    wall = reg / "CS_Wallpaper900112233.png"
    logo = reg / "CS_Logomark900112233.png"
    make_wallpaper(wall)

    bespoke = root / "branding" / "logomark.png"
    live_snap = root / "branding" / "logomark_from_live_site.png"
    if bespoke.is_file():
        shutil.copy2(bespoke, logo)
        print("PNG (logomark from branding/logomark.png):", bespoke.relative_to(root), "->", logo.relative_to(root))
    elif live_snap.is_file():
        shutil.copy2(live_snap, logo)
        print("PNG (logomark from branding/logomark_from_live_site.png):", live_snap.relative_to(root), "->", logo.relative_to(root))
    else:
        make_logo_layered_o(logo, sz=512)

    pages = [
        ("aa10_exec_overview", "Executive lane"),
        ("aa20_operations", "Operations lane"),
        ("aa30_finance", "Finance lane"),
        ("aa40_marketing", "Marketing lane"),
        ("aa50_governance", "Governance lane"),
        ("aa55_ai_platform", "AI platform"),
        ("aa60_opportunity_lab", "Opportunity deep dive"),
        ("aa70_competition_lens", "Competitive lens"),
        ("eef0portfoliorenew01", "Renewal drilldown"),
    ]

    print("PNG:", wall.relative_to(root), ",", logo.relative_to(root))
    for pname, lbl in pages:
        print(f"bookmark {bookmark_id(pname)}  {lbl}  ({pname})")


if __name__ == "__main__":
    main()
