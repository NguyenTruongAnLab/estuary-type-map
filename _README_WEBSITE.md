# Website Structure README

## Overview

This website uses **Jekyll** for multi-page navigation with an automated gallery system for visualizations.

## Quick Start

### Generate Gallery Index
```bash
python scripts/generate_gallery_index.py
```

### Test Locally
```bash
jekyll serve
# Visit http://localhost:4000
```

### Deploy
```bash
git add .
git commit -m "Update gallery"
git push
```

## Adding New Visualizations

1. Save HTML files to `diagnostics_html/`
2. Run `python scripts/generate_gallery_index.py`
3. Commit and push

**Auto-categorization** by filename:
- Contains `river` → River Network Analysis
- Contains `basin` → Tidal Basin Analysis  
- Contains `salinity` → Salinity Classification
- etc.

## Creating New Pages

Create `newpage.md`:
```markdown
---
layout: default
title: New Page Title
---

# Content here
```

Page automatically appears at `/newpage.html`

## File Structure

```
├── _config.yml          # Jekyll configuration
├── _layouts/            # Page templates
│   └── default.html     # Main template
├── _includes/           # Reusable components
│   ├── navigation.html  # Site navbar
│   └── footer.html      # Site footer
├── _data/               # Data files
│   └── gallery_index.json  # Generated gallery index
├── gallery.html         # Automated gallery page
├── index.html           # Interactive map (homepage)
├── dataset.md           # Dataset downloads
├── methodology.md       # Technical docs
└── about.md             # Project info
```

## Gallery System

### How It Works
1. Script scans `diagnostics_html/`
2. Categorizes files by filename patterns
3. Generates `_data/gallery_index.json`
4. Gallery page loads JSON and builds dropdowns

### Customizing Categories
Edit `scripts/generate_gallery_index.py`:
```python
patterns = [
    (['keyword'], 'Category Name'),
    # Add more patterns
]
```

## Troubleshooting

**Gallery not showing**: Run `python scripts/generate_gallery_index.py`  
**Navigation missing**: Check `_includes/navigation.html` exists  
**Styles broken**: Clear cache (Ctrl+F5)

## Documentation

See `docs/WEBSITE_UPGRADE_COMPLETE.md` for full details.
