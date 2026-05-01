"""
execution/scrape_brand.py
─────────────────────────────────────────────────────────────────
Brand Scraper — Layer 3 (Execution) script.

Usage:
    python execution/scrape_brand.py <url> [--fresh]

Arguments:
    url       Full URL of the website to scrape.
    --fresh   Bypass Firecrawl cache (maxAge=0).

Outputs (written to tmp/brand_scrape/<domain>/):
    brand_profile.json     Raw branding object from Firecrawl
    images.json            All image URLs found on the page
    css_tokens.json        CSS custom-property tokens parsed from HTML
    screenshot.txt         URL of the full-page screenshot
    brand_report.md        Human-readable brand summary
    images/                Up to 10 key brand images downloaded locally

Requires:
    pip install firecrawl-py python-dotenv requests
    FIRECRAWL_API_KEY in .env
"""

import argparse
import json
import os
import re
import sys
import time
import io
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import requests
from dotenv import load_dotenv

# ── Load environment ─────────────────────────────────────────────
load_dotenv()
API_KEY = os.getenv("FIRECRAWL_API_KEY")
if not API_KEY:
    sys.exit("[ERROR] FIRECRAWL_API_KEY not found in .env. Please add it and retry.")

# ── Lazy import Firecrawl ─────────────────────────────────────────
try:
    from firecrawl import Firecrawl
except ImportError:
    sys.exit("[ERROR] firecrawl-py not installed. Run: pip install firecrawl-py")


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────

def sanitise_domain(url: str) -> str:
    """Turn a URL into a safe directory name."""
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    return re.sub(r"[^a-zA-Z0-9._-]", "_", domain)


def is_brand_image(url: str) -> bool:
    """Heuristic: flag images that are likely logos, heroes, or banners."""
    keywords = ["logo", "hero", "banner", "header", "og", "opengraph",
                "cover", "brand", "splash", "feature", "mascot"]
    url_lower = url.lower()
    return any(kw in url_lower for kw in keywords)


def download_image(url: str, dest_dir: Path, index: int) -> str | None:
    """Download an image to dest_dir. Returns local filename or None on error."""
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "BrandScraper/1.0"})
        resp.raise_for_status()
        # Guess extension
        content_type = resp.headers.get("content-type", "")
        ext = "png"
        if "jpeg" in content_type or "jpg" in content_type:
            ext = "jpg"
        elif "svg" in content_type:
            ext = "svg"
        elif "webp" in content_type:
            ext = "webp"
        elif "gif" in content_type:
            ext = "gif"
        filename = f"image_{index:02d}.{ext}"
        (dest_dir / filename).write_bytes(resp.content)
        return filename
    except Exception as e:
        print(f"  [WARN] Could not download {url}: {e}")
        return None


def extract_css_tokens(html: str) -> dict:
    """Parse CSS custom properties (--name: value) from raw HTML."""
    tokens = {}
    # Find all :root { ... } or style blocks
    style_blocks = re.findall(r"<style[^>]*>(.*?)</style>", html, re.DOTALL | re.IGNORECASE)
    all_css = "\n".join(style_blocks)
    # Extract custom properties
    for match in re.finditer(r"(--[\w-]+)\s*:\s*([^;}\n]+)", all_css):
        name, value = match.group(1).strip(), match.group(2).strip()
        tokens[name] = value
    return tokens


def build_report(url: str, domain: str, branding: dict, images: list,
                 css_tokens: dict, screenshot_url: str, markdown: str,
                 downloaded: list) -> str:
    """Construct the human-readable brand_report.md."""

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colors = branding.get("colors", {})
    fonts = branding.get("fonts", [])
    typography = branding.get("typography", {})
    spacing = branding.get("spacing", {})
    components = branding.get("components", {})
    animations = branding.get("animations", {})
    personality = branding.get("personality", {})
    brand_images = branding.get("images", {})

    # ── Colour table ─────────────────────────────
    color_rows = "\n".join(
        f"| {role.replace('text', 'Text ').capitalize()} | `{val}` |"
        for role, val in colors.items() if val
    ) or "| — | — |"

    # ── Typography table ─────────────────────────
    font_families = typography.get("fontFamilies", {})
    font_sizes = typography.get("fontSizes", {})
    font_weights = typography.get("fontWeights", {})
    typo_rows = "\n".join(
        f"| {role.capitalize()} | {family} | {font_sizes.get(role, '—')} | {font_weights.get('regular', '—')} |"
        for role, family in font_families.items()
    ) or "| — | — | — | — |"

    # ── Button styles ─────────────────────────────
    def fmt_component(comp: dict) -> str:
        return ", ".join(f"{k}: `{v}`" for k, v in comp.items())

    btn_primary = fmt_component(components.get("buttonPrimary", {})) or "—"
    btn_secondary = fmt_component(components.get("buttonSecondary", {})) or "—"

    # ── Key images ───────────────────────────────
    brand_image_section = ""
    for key, img_url in brand_images.items():
        if img_url:
            brand_image_section += f"- **{key.capitalize()}**: {img_url}\n"

    # Priority images (brand heuristic) from images list
    priority = [u for u in images if is_brand_image(u)][:10]
    if priority:
        brand_image_section += "\n**Other likely brand images:**\n"
        brand_image_section += "\n".join(f"- {u}" for u in priority)

    if downloaded:
        brand_image_section += "\n\n**Downloaded locally (images/ folder):**\n"
        brand_image_section += "\n".join(f"- {f}" for f in downloaded)

    # ── Effects & animations ─────────────────────
    effects = []
    if animations:
        effects.append(f"**Animations:** {json.dumps(animations, indent=2)}")
    if spacing.get("borderRadius"):
        effects.append(f"**Border radius:** {spacing['borderRadius']}")
    if spacing.get("baseUnit"):
        effects.append(f"**Spacing base unit:** {spacing['baseUnit']}px")
    effects_text = "\n\n".join(effects) or "None detected."

    # ── CSS tokens ───────────────────────────────
    token_lines = "\n".join(f"- `{k}`: `{v}`" for k, v in list(css_tokens.items())[:50])
    if not token_lines:
        token_lines = "No CSS custom properties found."

    # ── Personality ──────────────────────────────
    personality_text = json.dumps(personality, indent=2) if personality else "—"

    report = f"""# Brand Report: {domain}

**Scraped:** {now}
**Source:** {url}

---

## Brand Identity

- **Color Scheme:** {branding.get("colorScheme", "unknown")}
- **Logo:** {branding.get("logo") or brand_images.get("logo") or "—"}
- **OG Image:** {brand_images.get("ogImage") or "—"}
- **Favicon:** {brand_images.get("favicon") or "—"}

---

## Colour Palette

| Role | Value |
|------|-------|
{color_rows}

---

## Typography

| Role | Family | Size | Weight |
|------|--------|------|--------|
{typo_rows}

**All font families found on page:**
{chr(10).join(f"- {f.get('family', '—')}" for f in fonts) or "—"}

---

## Spacing & Layout

- **Base unit:** {spacing.get("baseUnit", "—")}px
- **Border radius:** {spacing.get("borderRadius", "—")}
- **Padding:** {spacing.get("padding", "—")}
- **Margins:** {spacing.get("margins", "—")}

---

## Button Styles

- **Primary:** {btn_primary}
- **Secondary:** {btn_secondary}

---

## Key Images

{brand_image_section or "No images detected."}

---

## Styling Effects & Notes

{effects_text}

---

## Brand Personality

```json
{personality_text}
```

---

## CSS Custom Properties (from parsed HTML)

{token_lines}

---

## Screenshot

{screenshot_url or "No screenshot available."}

---

## Raw Markdown (first 1000 chars)

```
{(markdown or "")[:1000]}
```
"""
    return report


# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Scrape brand data from a website using Firecrawl.")
    parser.add_argument("url", help="Full URL to scrape (e.g. https://stripe.com)")
    parser.add_argument("--fresh", action="store_true", help="Bypass Firecrawl cache")
    parser.add_argument("--out", default="brand-data", help="Root output folder (default: brand-data)")
    args = parser.parse_args()

    url = args.url
    domain = sanitise_domain(url)
    max_age = 0 if args.fresh else 172800000  # 0 = bypass cache, else 2 days

    # ── Set up output directory ───────────────────
    base_dir = Path(args.out) / domain
    images_dir = base_dir / "images"
    base_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(exist_ok=True)

    print(f"\n[SCRAPING] {url}")
    print(f"[OUTPUT]   {base_dir}/\n")

    # ── Initialise Firecrawl ──────────────────────
    firecrawl = Firecrawl(api_key=API_KEY)

    # ── Scrape ────────────────────────────────────
    print("[API] Calling Firecrawl (formats: branding, images, markdown, screenshot, html)...")
    start = time.time()
    try:
        result = firecrawl.scrape(
            url,
            formats=["branding", "images", "markdown", "screenshot", "html"],
            max_age=max_age,
        )
    except Exception as e:
        sys.exit(f"[ERROR] Firecrawl scrape failed: {e}")

    elapsed = round(time.time() - start, 1)
    print(f"[DONE] Scraped in {elapsed}s\n")

    # ── Extract data ──────────────────────────────
    # Handle both dict and object-style responses
    def get(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    branding = get(result, "branding") or {}
    images = get(result, "images") or []
    markdown = get(result, "markdown") or ""
    screenshot_url = get(result, "screenshot") or ""
    html = get(result, "html") or ""

    # ── Save raw branding profile ─────────────────
    (base_dir / "brand_profile.json").write_text(
        json.dumps(branding if isinstance(branding, dict) else branding.__dict__, indent=2, default=str),
        encoding="utf-8"
    )
    print("[SAVED] brand_profile.json")

    # ── Save images list ──────────────────────────
    (base_dir / "images.json").write_text(
        json.dumps(images, indent=2), encoding="utf-8"
    )
    print(f"[SAVED] images.json ({len(images)} URLs)")

    # ── Parse CSS custom properties ───────────────
    css_tokens = extract_css_tokens(html)
    (base_dir / "css_tokens.json").write_text(
        json.dumps(css_tokens, indent=2), encoding="utf-8"
    )
    print(f"[SAVED] css_tokens.json ({len(css_tokens)} tokens)")

    # ── Save screenshot URL ───────────────────────
    (base_dir / "screenshot.txt").write_text(screenshot_url or "N/A", encoding="utf-8")
    print("[SAVED] screenshot.txt")

    # ── Download key images ───────────────────────
    brand_img_urls = []
    # Priority: branding.images object
    branding_images = (branding if isinstance(branding, dict) else vars(branding)).get("images", {}) if branding else {}
    for _, img_url in (branding_images.items() if isinstance(branding_images, dict) else []):
        if img_url and img_url not in brand_img_urls:
            brand_img_urls.append(img_url)

    # Then: heuristic-filtered from images list
    for img_url in images:
        if isinstance(img_url, str) and is_brand_image(img_url) and img_url not in brand_img_urls:
            brand_img_urls.append(img_url)

    brand_img_urls = brand_img_urls[:10]
    print(f"\n[IMAGES] Downloading up to {len(brand_img_urls)} brand images...")
    downloaded = []
    for i, img_url in enumerate(brand_img_urls):
        filename = download_image(img_url, images_dir, i + 1)
        if filename:
            downloaded.append(filename)
            print(f"  [OK] {filename}")

    # ── Generate report ───────────────────────────
    print("\n[REPORT] Generating brand_report.md...")
    report = build_report(
        url=url,
        domain=domain,
        branding=branding if isinstance(branding, dict) else (vars(branding) if branding else {}),
        images=images,
        css_tokens=css_tokens,
        screenshot_url=screenshot_url,
        markdown=markdown,
        downloaded=downloaded,
    )
    (base_dir / "brand_report.md").write_text(report, encoding="utf-8")
    print("[SAVED] brand_report.md")

    # ── Summary ───────────────────────────────────
    print("\n" + "="*50)
    print("  Brand Scrape Complete!")
    print("="*50)
    print(f"  Domain  : {domain}")
    print(f"  Output  : {base_dir}")
    print(f"  Images  : {len(downloaded)}")
    print(f"  CSS Vars: {len(css_tokens)}")
    print("="*50)
    print("  Open brand_report.md for a full summary.\n")


if __name__ == "__main__":
    main()
