---
name: brand-scraper
description: >
  Scrapes a website using the Firecrawl API and extracts comprehensive brand data: colour palette,
  typography, fonts, logo, hero/banner images, button styles, spacing, animations, CSS custom
  properties, and a full-page screenshot. Use this skill whenever the user wants to analyse a
  competitor's brand, reverse-engineer a design system, pull brand assets before building a new
  website, or gather visual inspiration from any live site. Trigger even if they just say things
  like "grab the branding from X", "what colours does Y use?", "get me the fonts from Z", or
  "I want to build a site that looks like <url>".
---

# Brand Scraper

Extracts everything a web designer or developer needs to understand and rebuild a brand from any live website — colours, typography, logos, hero images, button styles, spacing, animations, and CSS tokens.

---

## How to use this skill

### 1. Get the URL from the user
Ask for the full URL of the website to analyse (e.g. `https://stripe.com`).

### 2. Check for the API key
Open `.env` and confirm `FIRECRAWL_API_KEY` is set. If not, ask the user to add it:
```
FIRECRAWL_API_KEY=fc-your-key-here
```

### 3. Install dependencies (first run only)
```bash
pip install firecrawl-py python-dotenv requests
```

### 4. Run the script
```bash
python execution/scrape_brand.py <url>
```

Add `--fresh` to bypass the Firecrawl cache and always get a live result:
```bash
python execution/scrape_brand.py <url> --fresh
```

### 5. Open the report
Results are saved to `tmp/brand_scrape/<domain>/`:

| File | Contents |
|------|----------|
| `brand_report.md` | Full human-readable summary (start here) |
| `brand_profile.json` | Raw branding object from Firecrawl |
| `images.json` | All image URLs found on the page |
| `css_tokens.json` | CSS custom properties parsed from HTML |
| `screenshot.txt` | URL to a full-page screenshot |
| `images/` | Up to 10 key brand images downloaded locally |

---

## What gets extracted

### Colours
Primary, secondary, accent, background, text, link, success, warning, and error colours.

### Typography
Font families (heading, body, code), font sizes (h1–h3, body), font weights, and line heights.

### Images
- Logo, favicon, OG image (from branding metadata)
- Hero, banner, and header images (heuristic filter on all page images)
- Downloaded locally to `images/`

### UI Components
- Primary and secondary button styles (background, text colour, border radius)
- Input field styles

### Spacing & Layout
- Base spacing unit
- Border radius
- Grid and layout configuration

### Effects
- Animations and transitions
- Shadows, gradients, glassmorphism patterns (where detectable)

### CSS Custom Properties
Raw `--variable: value` tokens parsed directly from `<style>` blocks in the page HTML.

---

## Directive
See `directives/brand_scraper.md` for full SOP, edge cases, and learnings.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `FIRECRAWL_API_KEY not found` | Add key to `.env` |
| Sparse colours | Site may inject styles via JS; the `branding` format uses browser rendering, so results should still be good |
| No images downloaded | Site uses CDN with auth; image URLs are still saved in `images.json` |
| Screenshot URL expired | Screenshot URLs expire in 24 hours — run again with `--fresh` |
| Rate limit hit | Firecrawl free tier has limits; wait a moment and retry |
