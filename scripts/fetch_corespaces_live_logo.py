#!/usr/bin/env python3
"""Load https://corespaces.com/ with headless Chromium (Selenium), capture header logo raster.

Writes:
  • ``branding/logomark_from_live_site.png``
  • ``powerbi/CoreSpacesRenewal.Report/StaticResources/RegisteredResources/CS_Logomark900112233.png``

**Trademark:** The site mark is Core Spaces branding. Repository use stays **portfolio / interview demo only**.
Re-run branding script after this file if wallpaper must also regenerate; PBIP consumes the PNG name above.

Requires: Chrome (or Chromium) installed locally; Selenium 4 resolves ``chromedriver`` via Selenium Manager.
"""

from __future__ import annotations

import json
import re
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

try:
    from PIL import Image
except ImportError as e:
    raise SystemExit("Install Pillow: pip install Pillow") from e

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
HOMEPAGE = "https://corespaces.com/"


def try_element_screenshot(driver, imgs: list, out_path: Path) -> tuple[bool, str]:
    """Return (ok, detail) — tries each WebElement screenshot in order."""
    from selenium.common.exceptions import WebDriverException

    for el in imgs:
        try:
            if not el.is_displayed():
                continue
            r = el.rect
            w, h = r.get("width", 0), r.get("height", 0)
            if w < 20 or h < 20:
                continue
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tpath = Path(tmp.name)
            try:
                el.screenshot(str(tpath))
                if tpath.stat().st_size < 512:
                    continue
                img = Image.open(tpath).convert("RGBA")
                img.save(out_path, format="PNG", optimize=True)
                return True, f"element screenshot {int(w)}x{int(h)}"
            finally:
                tpath.unlink(missing_ok=True)
        except WebDriverException:
            continue
    return False, "no element screenshot succeeded"


def norm_icon_url(site_url: str, href: str) -> str | None:
    href = href.strip()
    if not href or href.startswith("data:"):
        return None
    return urljoin(site_url, href)


def scrape_icon_urls(html: str, base: str) -> list[tuple[int, str]]:
    """Rough priority: png/svg apple-touch favicon."""
    urls: list[tuple[int, str]] = []

    def add(priority: int, href: str) -> None:
        u = norm_icon_url(base, href)
        if u and u not in {x[1] for x in urls}:
            urls.append((priority, u))

    for m in re.finditer(
        r'<link[^>]+rel\s*=\s*["\']([^"\']+)["\'][^>]*href\s*=\s*["\']([^"\']+)["\']',
        html,
        flags=re.I,
    ):
        rel, href = m.group(1).lower(), m.group(2)
        if any(x in rel for x in ("apple-touch-icon", "mask-icon")):
            add(90, href)
        if "icon" in rel.split():
            pri = 80 if ".png" in href.lower() or ".jpg" in href.lower() else 50
            add(pri, href)

    for m in re.finditer(
        r'<link[^>]+href\s*=\s*["\']([^"\']+)["\'][^>]*rel\s*=\s*["\']([^"\']+)["\']',
        html,
        flags=re.I,
    ):
        href, rel = m.group(1), m.group(2).lower()
        if any(x in rel for x in ("apple-touch-icon", "mask-icon")) or "icon" in rel.split():
            add(70, href)

    urls.sort(key=lambda t: (-t[0], t[1]))
    return urls


def download_bytes(url: str) -> bytes | None:
    import urllib.error
    import urllib.request

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.read()
    except urllib.error.HTTPError:
        return None


def io_bytes(b: bytes):
    import io

    return io.BytesIO(b)


def save_png_best_effort(payload: bytes, out_path: Path) -> tuple[bool, str]:
    blob = payload.lstrip()
    if blob.startswith((b"<svg", b"<?xml")):
        return False, "svg_or_xml_skip"
    try:
        im = Image.open(io_bytes(blob))
        im.load()
        im = im.convert("RGBA")
        im.save(out_path, format="PNG", optimize=True)
        return True, "downloaded raster"
    except Exception as exc:  # noqa: BLE001 — PIL probing many formats
        return False, str(exc)


def collect_logo_candidates(driver) -> list:
    from selenium.webdriver.common.by import By

    selectors = (
        "header img",
        "[class*='header'] img",
        "[class*='Header'] img",
        "[class*='logo'] img",
        "[class*='Logo'] img",
        "[class*='navbar'] img",
        "[class*='brand'] img",
        ".site-branding img",
        "nav img",
        "a[href='/'] img",
        "[data-src*='logo' i]",
    )
    seen: list = []
    dup = set()
    for css in selectors:
        for el in driver.find_elements(By.CSS_SELECTOR, css):
            k = id(el)
            if k in dup:
                continue
            dup.add(k)
            seen.append(el)
    return seen


def score_candidate(el, viewport_h_top: float = 220.0) -> float:
    try:
        r = el.rect
        area = float(r["width"]) * float(r["height"])
        src = el.get_attribute("src") or ""
        y = float(r.get("y", 9999))
        s = area
        if y > viewport_h_top:
            s *= 0.15
        if re.search(r"logo|brand|core|symbol|mark|icon", src, flags=re.I):
            s *= 2.8
        if "partner" in src.lower():
            s *= 0.01
        low = src.lower()
        for bad in ("jpmorgan", "jp-morgan", "pgim", "talkspace", "facebook", "twitter", "instagram"):
            if bad in low:
                s *= 0.01
        return s
    except Exception:
        return 0.0


def main() -> None:
    import sys

    _sd = Path(__file__).resolve().parent
    if str(_sd) not in sys.path:
        sys.path.insert(0, str(_sd))
    try:
        from repo_dotenv import load_repo_dotenv
    except ImportError:
        pass
    else:
        load_repo_dotenv()

    root = Path(__file__).resolve().parents[1]
    out_registered = root / "powerbi" / "CoreSpacesRenewal.Report" / "StaticResources" / "RegisteredResources" / "CS_Logomark900112233.png"
    out_mirror = root / "branding" / "logomark_from_live_site.png"
    manifest_path = root / "research" / "core_spaces" / "derived" / "live_logo_capture.json"

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait
    except ImportError as e:
        raise SystemExit("Install Selenium: pip install selenium") from e

    opts = ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1200")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument(f"--user-agent={USER_AGENT}")
    opts.add_argument("--lang=en-US")

    driver = webdriver.Chrome(options=opts)
    try:
        driver.set_page_load_timeout(45)
        driver.get(HOMEPAGE)
        WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        try:
            WebDriverWait(driver, 12).until(lambda d: d.execute_script("return document.readyState") == "complete")
        except Exception:
            pass
        time.sleep(1.2)
        driver.execute_script("window.scrollTo(0, 0);")
        try:
            WebDriverWait(driver, 8).until(
                lambda d: d.execute_script(
                    "const n=[...document.querySelectorAll('header img, nav img')];"
                    "return n.some(i=>i.complete && i.naturalWidth>24 && i.getBoundingClientRect().top<160);"
                )
            )
        except Exception:
            pass
        candidate_imgs = collect_logo_candidates(driver)
        candidate_imgs.sort(key=score_candidate, reverse=True)

        out_mirror.parent.mkdir(parents=True, exist_ok=True)
        out_registered.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)

        ok_el, detail = try_element_screenshot(driver, candidate_imgs[:18], out_mirror)
        if ok_el:
            import shutil

            shutil.copy2(out_mirror, out_registered)
        else:
            html = driver.page_source
            for _pri, u in scrape_icon_urls(html, HOMEPAGE):
                raw = download_bytes(u)
                if not raw:
                    continue
                gd, gd_msg = save_png_best_effort(raw, out_mirror)
                if gd:
                    import shutil

                    shutil.copy2(out_mirror, out_registered)
                    detail = gd_msg + " " + u
                    ok_el = True
                    break
            if not ok_el:
                fp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                fp.close()
                p = Path(fp.name)
                try:
                    driver.save_screenshot(str(p))
                    # crop top strip heuristically
                    im = Image.open(p).convert("RGBA")
                    crop = im.crop((48, 18, 48 + 220, 18 + 80))
                    crop.save(out_mirror, format="PNG", optimize=True)
                    detail = "viewport crop fallback (inspect manually)"
                    import shutil

                    shutil.copy2(out_mirror, out_registered)
                    ok_el = True
                finally:
                    p.unlink(missing_ok=True)

        if not ok_el:
            raise SystemExit("Could not capture logo from live site.")

        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        manifest = {
            "captured_at_utc": stamp,
            "url": HOMEPAGE,
            "method": detail,
            "outputs": {"registeredResource": str(out_registered.relative_to(root)), "mirror": str(out_mirror.relative_to(root))},
            "disclaimer": "Trademark/logo belongs to Core Spaces; portfolio demo only — not endorsed.",
        }
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        print("OK:", detail)
        print("=>", out_registered.relative_to(root))
        print("=>", manifest_path.relative_to(root))
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
