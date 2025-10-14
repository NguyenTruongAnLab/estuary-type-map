# 📦 Release Dataset Files - v1.0.0

## 🎯 Files for GitHub Release Attachment

**Version**: v1.0.0  
**Generated**: October 14, 2025  
**Purpose**: Primary datasets and visualizations for milestone release

---

## 🌊 Primary Datasets (Essential)

### tidal_basins_river_based_lev07.gpkg
- **Path**: `data/processed/tidal_basins_river_based_lev07.gpkg`
- **Size**: 111.4 MB
- **Description**: Primary dataset - 16,189 tidal basins with corrected Dürr classification
- **Priority**: CRITICAL - Main release artifact

### tidal_basins_web.html
- **Path**: `diagnostics_html/tidal_basins_web.html`
- **Size**: ~24 MB
- **Description**: Interactive web map with dual-layer visualization and pie charts
- **Priority**: HIGH - Main visualization

### tidal_basins_precise.geojson
- **Path**: `data/web/tidal_basins_precise.geojson`
- **Size**: 28.5 MB
- **Description**: Web-optimized GeoJSON for online applications
- **Priority**: HIGH - Web deployment

---


## 🗺️ Additional Visualizations (Optional)

### coastal_basins.html
- **Path**: `diagnostics_html/coastal_basins.html`
- **Size**: ~5 MB
- **Description**: Coastal basin visualization
- **Priority**: LOW - Supplementary

### gcc_comprehensive.html
- **Path**: `diagnostics_html/gcc_comprehensive.html`
- **Size**: ~24 MB
- **Description**: GCC coastal characteristics map
- **Priority**: LOW - Supplementary

---

## 📋 Release Instructions

### Automated Upload (if GitHub CLI available):
```bash
python scripts/automated_release.py --tag v1.0.0
```

### Manual Upload:
1. Go to: https://github.com/NguyenTruongAnLab/estuary-type-map/releases/new
2. Tag: `v1.0.0`
3. Title: `v1.0.0 - High-Resolution Global Tidal Basin Atlas`
4. Description: Copy from `docs/RELEASE_NOTES_v1.0.0.md`
5. Attach files marked as CRITICAL and HIGH priority above

---

## 📊 File Summary

- **Essential files**: 3 files (~164 MB)
- **Supporting datasets**: 3 files (~1.1 GB)
- **Additional visualizations**: 2 files (~29 MB)
- **Total**: 8 files (~1.3 GB)

**Recommendation**: Upload essential files (164 MB) for main release, add supporting datasets as needed.