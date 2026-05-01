# Directive: Brand Scraper

## Goal
Scrape a target website using the Firecrawl API and extract everything an agency or developer would need to understand and recreate the brand: colours, typography, logo, hero/header images, button styles, spacing, animations, and any other useful visual/design data.

---

## Inputs
| Field | Description |
|-------|-------------|
| `url` | The full URL of the website to scrape (e.g. `https://stripe.com`) |

---

## Tools / Scripts
- **Script:** `execution/scrape_brand.py`
- **API:** Firecrawl (key stored in `.env` as `FIRECRAWL_API_KEY`)
- **Output directory:** `tmp/brand_scrape/<sanitised-domain>/`

---

## What to Extract
Use Firecrawl's combined formats to maximise data quality:

| Format | Why |
|--------|-----|
| `branding` | Colours, fonts, typography scale, spacing, buttons, animations, logo URL |
| `images` | All image URLs — filter for logos, heroes, og-images, banners |
| `markdown` | Full page text — useful for tone-of-voice and copy style |
| `screenshot` | Full-page screenshot for visual reference |
| `html` | Cleaned HTML — parse for CSS custom-properties, utility classes, and effects |

---

## Steps (executed by `scrape_brand.py`)

1. **Validate** the URL is reachable.
2. **Scrape** with formats `["branding", "images", "markdown", "screenshot", "html"]`.
3. **Extract brand data** from the `branding` object and save as `brand_profile.json`.
4. **Download images** — filter for likely brand images (logo, og-image, hero, banner keywords). Save URLs list to `images.json` and download up to 10 key images into `images/`.
5. **Parse CSS custom properties** from the `html` payload — extract `--color-*`, `--font-*`, `--spacing-*`, `--radius-*`, and similar tokens.
6. **Save screenshot URL** to `screenshot.txt`.
7. **Generate `brand_report.md`** — a human-readable summary combining all extracted data (see Output Format below).

---

## Output Format (`brand_report.md`)

```markdown
# Brand Report: <domain>
Scraped: <timestamp>
Source: <url>

## Brand Identity
- Color Scheme: light / dark
- Logo: <url>
- OG Image: <url>

## Colour Palette
| Role | Hex |
|------|-----|
| Primary | #... |
| Secondary | #... |
| Accent | #... |
| Background | #... |
| Text Primary | #... |
| Text Secondary | #... |

## Typography
| Role | Family | Size | Weight |
|------|--------|------|--------|
| Heading | ... | ... | ... |
| Body | ... | ... | ... |
| Code | ... | ... | ... |

## Spacing & Layout
- Base unit: Xpx
- Border radius: Xpx
- Grid: ...

## Button Styles
- Primary: bg <hex>, text <hex>, radius <px>
- Secondary: ...

## Key Images
(list of image URLs with notes)

## Styling Effects & Notes
(animations, shadows, glassmorphism, gradients, etc.)

## CSS Custom Properties
(list of extracted tokens)

## Raw Markdown Summary
(first 500 chars of scraped markdown)
```

---

## Edge Cases & Learnings
- Some SPAs may return little HTML server-side; the `branding` format handles JS-rendered content.
- Screenshot URLs expire after 24 hours — save locally or use immediately.
- Rate limit: 1 credit per scrape. The `branding` format is included in the base scrape credit.
- If `colors` is sparse in the branding response, fall back to parsing CSS custom properties from the `html` payload.
- Large sites: this directive scrapes the homepage only. For sub-pages, run the script multiple times with different URLs.
