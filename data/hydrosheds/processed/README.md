# Processed HydroSHEDS Data

This directory contains compressed HydroSHEDS data optimized for the estuary project.

## Files (When Generated)

- `rivers_coastal.gpkg` - Coastal river reaches (<50MB)
- `basins_level06.gpkg` - Large drainage basins (<100MB)
- `basins_level08.gpkg` - Detailed drainage basins (<150MB)

## How to Generate

1. Download raw data: `python scripts/download_hydrosheds.py`
2. Compress data: `python scripts/compress_hydrosheds.py`
3. Validate output: `python scripts/validate_hydrosheds.py`

See `data/hydrosheds/raw/README.md` for complete instructions.

---

**Note**: These files will be generated after running the compression script.
They are <200MB each and ARE tracked in git for GitHub Pages deployment.
