# Sales Scrape

> A 3-layer AI agent system that scrapes brand identity data from any website using the Firecrawl API — extracting colours, typography, logos, images, button styles, and more.

---

## What This Does

Point it at any website and it automatically extracts:

- 🎨 **Colour palette** — primary, secondary, accent, background, text
- 🔤 **Typography** — font families, sizes, weights
- 🖼️ **Brand images** — logo, favicon, OG image, hero/banner images (downloaded locally)
- 🔘 **UI components** — button styles, input styles, border radius
- 📐 **Spacing & layout** — base unit, border radius, grid info
- ✨ **Animations & effects** — transitions, shadows, glassmorphism
- 🧩 **CSS custom properties** — parsed from `<style>` blocks
- 📸 **Full-page screenshot** — via Firecrawl

---

## Architecture

This project follows a **3-layer agent architecture** (see `AGENTS.md`):

```
Layer 1 — Directive    directives/          Natural language SOPs
Layer 2 — Orchestration  You (the AI)       Intelligent routing & decision making
Layer 3 — Execution    execution/           Deterministic Python scripts
```

---

## Project Structure

```
Sales_Scrape/
├── AGENTS.md                          # Agent instructions & architecture
├── .gitignore                         # Excludes .env, brand-data/, tmp/
│
├── directives/
│   └── brand_scraper.md               # SOP: what to extract, edge cases, learnings
│
├── execution/
│   └── scrape_brand.py                # Python script — the actual scraper
│
├── brand-scraper/
│   └── skill_brandxtractor.md         # Skill card for the brand scraper
│
├── brand-guidelines/
│   └── skill_brand_guidelines.md      # Brand guidelines skill (Anthropic + scraped brands)
│
└── skill-creator/                     # Skill creation toolkit
    ├── skill_creator.md
    ├── agents/
    ├── scripts/
    ├── eval-viewer/
    └── references/
```

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/Tejeshwar11/Sales_Scrape.git
cd Sales_Scrape
```

### 2. Set up your environment

```bash
# Install dependencies
pip install firecrawl-py python-dotenv requests

# Create your .env file
echo "FIRECRAWL_API_KEY=fc-your-key-here" > .env
```

Get your API key at [firecrawl.dev](https://firecrawl.dev).

### 3. Run the scraper

```bash
python execution/scrape_brand.py https://stripe.com --out brand-data
```

Add `--fresh` to bypass cache and always get live data:

```bash
python execution/scrape_brand.py https://stripe.com --out brand-data --fresh
```

### 4. View the results

```
brand-data/<domain>/
├── brand_report.md        ← Start here — full human-readable summary
├── brand_profile.json     ← Raw Firecrawl branding object
├── images.json            ← All image URLs from the page
├── css_tokens.json        ← CSS custom properties
├── screenshot.txt         ← Full-page screenshot URL
└── images/                ← Up to 10 brand images downloaded locally
```

---

## Example Output

Scraped from **feastables.com**:

| Field | Value |
|-------|-------|
| Primary colour | `#72E2FF` (sky blue) |
| Secondary colour | `#CEFC17` (neon lime) |
| Background | `#F2EBE0` (warm cream) |
| Font | `Kanit` — condensed, bold |
| Button radius | `0px` (sharp square corners) |
| Personality | Playful · High energy |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `FIRECRAWL_API_KEY` | Your Firecrawl API key — **never commit this** |

---

## What's Ignored (`.gitignore`)

- `.env` — API keys
- `brand-data/` — Scraped images & raw API responses
- `tmp/` — Intermediate files
- `credentials.json`, `token.json` — OAuth credentials
- `__pycache__/` — Python cache

---

## Skills

| Skill | Description |
|-------|-------------|
| `brand-scraper` | Scrapes brand data from any website |
| `brand-guidelines` | Applies brand identity to artifacts (supports Anthropic + scraped brands) |
| `skill-creator` | Creates and iterates on new skills |

---

## Built With

- [Firecrawl](https://firecrawl.dev) — Web scraping API
- Python 3.x
- `firecrawl-py`, `python-dotenv`, `requests`

---

## License

See individual skill `LICENSE.txt` files for terms.
