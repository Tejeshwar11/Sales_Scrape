---
name: brand-guidelines
description: Applies brand colors, typography, and visual identity to any artifact. Use it when brand colors or style guidelines, visual formatting, or company design standards apply — either from Anthropic's official guidelines OR from scraped brand data extracted by the brand-scraper skill. Trigger whenever the user mentions branding, design systems, visual identity, style guides, color palettes, fonts, logos, or wants to make something "look like" a specific company or website. Currently includes scraped data for: Feastables (feastables.com).
license: Complete terms in LICENSE.txt
---

# Brand Styling Guidelines

## Overview

Apply brand identity and style to any artifact — documents, presentations, websites, or components. This skill supports two modes:

1. **Anthropic Brand** — use the built-in Anthropic guidelines below.
2. **Scraped Brand** — use data extracted by the `brand-scraper` skill from any website (located in `tmp/brand_scrape/<domain>/brand_profile.json` and `brand_report.md`).

**Keywords**: branding, corporate identity, visual identity, post-processing, styling, brand colors, typography, brand guidelines, visual formatting, visual design, design system, color palette, fonts, logo, buttons, spacing, animations

---

## Anthropic Brand Guidelines

### Colors

**Main Colors:**

| Name | Hex | Usage |
|------|-----|-------|
| Dark | `#141413` | Primary text and dark backgrounds |
| Light | `#faf9f5` | Light backgrounds and text on dark |
| Mid Gray | `#b0aea5` | Secondary elements |
| Light Gray | `#e8e6dc` | Subtle backgrounds |

**Accent Colors:**

| Name | Hex | Usage |
|------|-----|-------|
| Orange | `#d97757` | Primary accent |
| Blue | `#6a9bcc` | Secondary accent |
| Green | `#788c5d` | Tertiary accent |

### Typography

| Role | Family | Fallback |
|------|--------|---------|
| Headings (24pt+) | Poppins | Arial |
| Body text | Lora | Georgia |

### Spacing & Layout

- Non-text shapes use accent colors, cycling through orange → blue → green
- Smart color selection based on background contrast
- Preserves text hierarchy and formatting

---

## Using Scraped Brand Data

When a user wants to apply branding from a scraped website, load the outputs from the `brand-scraper` skill:

```
tmp/brand_scrape/<domain>/
├── brand_report.md       ← Human-readable summary (read this first)
├── brand_profile.json    ← Full branding object (colours, fonts, components)
├── css_tokens.json       ← CSS custom properties
├── images.json           ← All image URLs
├── screenshot.txt        ← Full-page screenshot URL
└── images/               ← Downloaded logo, hero, og-image etc.
```

### Extracted Brand Profile Structure

When applying a scraped brand, reference these fields from `brand_profile.json`:

#### Colours
```json
{
  "colors": {
    "primary":        "#...",
    "secondary":      "#...",
    "accent":         "#...",
    "background":     "#...",
    "textPrimary":    "#...",
    "textSecondary":  "#...",
    "link":           "#...",
    "success":        "#...",
    "warning":        "#...",
    "error":          "#..."
  }
}
```

#### Typography
```json
{
  "typography": {
    "fontFamilies": {
      "primary":  "...",
      "heading":  "...",
      "code":     "..."
    },
    "fontSizes": {
      "h1": "48px", "h2": "36px", "h3": "24px", "body": "16px"
    },
    "fontWeights": {
      "light": 300, "regular": 400, "medium": 500, "bold": 700
    },
    "lineHeights": {
      "heading": "1.2", "body": "1.6"
    }
  }
}
```

#### Spacing & Layout
```json
{
  "spacing": {
    "baseUnit":     8,
    "borderRadius": "8px",
    "padding":      "...",
    "margins":      "..."
  }
}
```

#### UI Components (Buttons etc.)
```json
{
  "components": {
    "buttonPrimary": {
      "background":   "#...",
      "textColor":    "#...",
      "borderRadius": "8px"
    },
    "buttonSecondary": {
      "background":   "transparent",
      "textColor":    "#...",
      "borderColor":  "#...",
      "borderRadius": "8px"
    },
    "input": {
      "background":   "#...",
      "borderColor":  "#...",
      "textColor":    "#..."
    }
  }
}
```

#### Brand Images
```json
{
  "images": {
    "logo":    "https://...",
    "favicon": "https://...",
    "ogImage": "https://..."
  }
}
```

#### Animations & Effects
```json
{
  "animations": {
    "transitionDuration": "200ms",
    "easing":             "ease-in-out"
  }
}
```

#### Brand Personality
```json
{
  "personality": {
    "tone":           "professional",
    "energy":         "calm",
    "targetAudience": "developers"
  }
}
```

---

## Applying Brand to Artifacts

### For Web / HTML / CSS

Use CSS custom properties from `css_tokens.json` directly, or generate them from the brand profile:

```css
:root {
  --color-primary:       <colors.primary>;
  --color-secondary:     <colors.secondary>;
  --color-accent:        <colors.accent>;
  --color-bg:            <colors.background>;
  --color-text:          <colors.textPrimary>;
  --color-text-muted:    <colors.textSecondary>;
  --font-heading:        '<typography.fontFamilies.heading>', sans-serif;
  --font-body:           '<typography.fontFamilies.primary>', sans-serif;
  --font-code:           '<typography.fontFamilies.code>', monospace;
  --radius:              <spacing.borderRadius>;
  --spacing-unit:        <spacing.baseUnit>px;
  --transition:          all <animations.transitionDuration> <animations.easing>;
}
```

### For Documents / Presentations (python-pptx)

- Use `RGBColor` with hex values from `colors`
- Apply heading font from `typography.fontFamilies.heading`
- Apply body font from `typography.fontFamilies.primary`
- Use accent colors for shapes and decorative elements

### Logo & Images

- Load from `tmp/brand_scrape/<domain>/images/` (locally downloaded)
- Reference `brand_profile.json → images.logo` for the primary logo URL
- Hero/banner images are in `images/` directory

---

## Technical Details

### Font Management

- Use fonts specified in `typography.fontFamilies` when available
- Fallback order: system fonts → Arial (headings) → Georgia (body)
- For web: load via Google Fonts if the family is available there
- For desktop: pre-install the font for best results

### Color Application

- Use RGB/hex values directly from the brand profile
- For `python-pptx`: use `RGBColor` class
- For CSS: use hex values as-is or convert to HSL for manipulation
- For dark/light mode: check `colorScheme` field in brand profile

### CSS Custom Properties Priority

When both `css_tokens.json` and `brand_profile.json` are available:
1. Prefer `brand_profile.json` for semantic roles (primary, secondary, etc.)
2. Use `css_tokens.json` for exact token names the site uses (e.g. `--primary-500`)
3. Merge both for maximum fidelity

---

## Scraped Brand Data: Feastables

> **Source:** https://feastables.com/pages/our-coco-story
> **Scraped:** 2026-05-02
> **Files:** `brand-data/feastables.com/`

### Brand Identity

| Field | Value |
|-------|-------|
| Color Scheme | Light |
| Logo | [Feastables_Rebrand_Non_Tilted.png](https://feastables.com/cdn/shop/files/Feastables_Rebrand_Non_Tilted.png?v=1715198993&width=180) |
| Logo Alt | Feastables Wordmark |
| Favicon | [32x32 lockup](https://feastables.com/cdn/shop/files/Feastables_Rebrand_Lockup_Secondary__Square_32x32.png?v=1704497884) |
| OG Image | [meta.jpg](https://cdn.shopify.com/s/files/1/0551/6060/2784/files/meta.jpg?v=1696550380) |

### Colour Palette

| Role | Hex | Notes |
|------|-----|-------|
| Primary | `#72E2FF` | Sky blue — dominant CTA colour |
| Secondary | `#CEFC17` | Neon chartreuse / lime — high energy accent |
| Accent | `#72E2FF` | Same as primary |
| Background | `#F2EBE0` | Warm off-white / cream |
| Text Primary | `#000000` | Pure black |
| Link | `#F2EBE0` | Cream (matches background — inverted links) |

### Typography

| Role | Family | Stack | Size |
|------|--------|-------|------|
| Heading | Kanit | `Kanit, sans-serif` | h1/h2: 36px |
| Body | Kanit | `Kanit, sans-serif` | 24px |
| Paragraph | Kanit | `Kanit, sans-serif` | — |

**All fonts detected on page:**
- `Kanit` (primary brand font — bold, condensed)
- `Helvetica Neue` / `Helvetica` / `Arial` (fallbacks)
- `Sohne` (editorial/supporting)

### Spacing & Layout

| Property | Value |
|----------|-------|
| Base unit | `4px` |
| Border radius | `6px` (global) |
| Button radius | `0px` (sharp square corners) |
| Input radius | `0px` (sharp square corners) |

### Button Styles

| Type | Background | Text | Border Radius | Shadow |
|------|-----------|------|--------------|--------|
| Primary | `#72E2FF` (sky blue) | `#000000` | `0px` (square) | none |
| Secondary | `#0084AD` (deep blue) | `#FFFFFF` | `0px` (square) | none |

**Note:** Feastables uses sharp, zero-radius square buttons — no rounded corners.

### Input Fields

| Property | Value |
|----------|-------|
| Background | `#FFFFFF` |
| Text | `#000000` |
| Border radius | `0px` |
| Border | none detected |

### Brand Personality

| Dimension | Value |
|-----------|-------|
| Tone | **Playful** |
| Energy | **High** |
| Target Audience | Young adults and families |

### CSS as Custom Properties

```css
:root {
  /* Feastables Brand — feastables.com */
  --color-primary:      #72E2FF;   /* Sky blue */
  --color-secondary:    #CEFC17;   /* Neon lime */
  --color-accent:       #72E2FF;
  --color-bg:           #F2EBE0;   /* Warm cream */
  --color-text:         #000000;
  --color-link:         #F2EBE0;
  --color-btn-primary:  #72E2FF;
  --color-btn-secondary:#0084AD;

  --font-heading:       'Kanit', 'Helvetica Neue', Arial, sans-serif;
  --font-body:          'Kanit', 'Helvetica Neue', Arial, sans-serif;
  --font-editorial:     'Sohne', 'Helvetica Neue', Arial, sans-serif;

  --font-size-h1:       36px;
  --font-size-h2:       36px;
  --font-size-body:     24px;

  --radius:             6px;
  --radius-btn:         0px;       /* Square buttons */
  --spacing-unit:       4px;
}
```

### Design Notes for Rebuilding

- **Square buttons** with no border-radius are a key Feastables brand signature — avoid rounded buttons.
- The **neon lime** (`#CEFC17`) and **sky blue** (`#72E2FF`) combo on cream (`#F2EBE0`) creates high-energy contrast.
- `Kanit` is a condensed, bold-weight Google Font — weight 600–800 is typical for headings.
- The site has a **playful, high-energy** character — expect large type, bright colours, bold imagery.
- No CSS custom properties were found in server-rendered HTML (Shopify inlines styles via JS).
- Raw brand assets are in `brand-data/feastables.com/images/` (4 images downloaded).

### Screenshot

`brand-data/feastables.com/screenshot.txt` — live URL (expires 24h from scrape).
