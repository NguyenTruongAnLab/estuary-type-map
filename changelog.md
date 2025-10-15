---
layout: default
title: Changelog
permalink: /changelog/
---

# Changelog

## Version 1.0.0 - October 14, 2025

### 🎯 Major Achievement: First Direct Polygon-Based Global Tidal Basin Database

This release marks a **breakthrough in estuarine biogeochemistry**: the world's first comprehensive, high-resolution tidal basin atlas using **direct polygon measurement** from BasinATLAS Level 7, classified with the corrected Dürr et al. (2011) typology.

---

## 📊 Dataset Summary

### Primary Dataset: `tidal_basins_river_based_lev07.gpkg`
- **16,189 tidal basins** (BasinATLAS Level 7 resolution)
- **36.6 million km²** total catchment area
- **0-300 km from coast** (tidal influence zone)
- **Dual classification**: Dürr coastline (ocean basins) + catchments (upstream)

### Classification Breakdown (Corrected Dürr 2011 Types)
| Type | Count | Area (km²) | % | Description |
|------|-------|-----------|---|-------------|
| **Tidal systems** (Type II) | 4,666 | 11,100,845 | 28.8% | Wave/tide-dominated |
| **Small deltas** (Type I) | 4,036 | 9,915,216 | 24.9% | River-dominated, small-medium |
| **Fjords and fjaerds** (Type IV) | 3,516 | 6,677,945 | 21.7% | Glacially carved |
| **Lagoons** (Type III) | 1,577 | 3,513,555 | 9.7% | Barrier-protected |
| **Arheic** (Type VII) | 1,218 | 2,576,910 | 7.5% | Arid/arheic coasts |
| **Large Rivers** (Type Va) | 375 | 1,015,438 | 2.3% | Major rivers |
| **Large Rivers + tidal deltas** (Type Vb) | 227 | 605,466 | 1.4% | Major deltas (Mekong, etc.) |
| **Karst** (Type VI) | 153 | 433,585 | 0.9% | Limestone karst systems |
| **Unclassified** | 421 | 725,316 | 2.6% | No Dürr match |

---

## 🔬 Scientific Corrections Implemented

### 1. Corrected Dürr et al. (2011) Type Mapping

```python
# CORRECTED MAPPING
0:  'Endorheic or Glaciated'
1:  'Small deltas'              # Type I (was wrongly "Delta")
2:  'Tidal systems'             # Type II (was wrongly "Lagoon")
3:  'Lagoons'                   # Type III (was wrongly "Fjord")
4:  'Fjords and fjaerds'        # Type IV (was wrongly "Coastal Plain")
5:  'Large Rivers'              # Type Va (was wrongly "Karst")
51: 'Large Rivers with tidal deltas'  # Type Vb (was wrongly "Small deltas")
6:  'Karst'                     # Type VI
7:  'Arheic'                    # Type VII
```

**Impact**: 
- ✅ Mekong Delta now correctly classified as "Large Rivers with tidal deltas" (Type Vb)
- ✅ Saigon River now correctly classified as "Tidal systems" (Type II)

### 2. Strict Classification Priority
**Ocean basins** (DIST_SINK=0): **Coastline classification ONLY** (absolute priority)
**Upstream basins**: Use catchment classification
**Fallback**: Ocean basins without coastline match use catchment

This ensures coastal morphology determines ocean basin types, not inland watershed characteristics.

---

## 🗺️ Interactive Visualization Improvements

### Diagnostic Maps (diagnostics_html/)
1. **tidal_basins_web.html** (22.8 MB)
   - Clean map with basins, Dürr coastline, Dürr catchments
   - Side-by-side pie charts (bottom-right)
   - Layer control with checkboxes

2. **tidal_basins_with_rivers.html** (175.5 MB)
   - Same as above + 148,824 large river segments (GRIT)
   - Rivers filtered: Strahler order ≥ 6 OR mainstem
   - For diagnostic/validation purposes

### Features
- ✅ **Real pie charts** (Chart.js) showing area distribution
- ✅ **Checkbox layer control** (toggle on/off)
- ✅ **Correct Dürr colors** matching official types
- ✅ **Tooltips** with basin details (name, type, area, distance)

---

## 🔧 Technical Implementation

### Data Processing Pipeline
```
1. BasinATLAS Level 7 (520,000 basins globally)
   ↓ Filter: ENDO=0 & DIST_SINK ≤ 300 km
   ↓ 16,194 tidal basins

2. Classify with Dürr 2011
   ↓ Method 1: Spatial intersection with catchments
   ↓ Method 2: Nearest coastline for ocean basins
   ↓ Priority: Coastline > Catchment

3. Clean & Filter
   ↓ Remove basins < 5 km²
   ↓ 16,189 final basins

4. Output
   ↓ GPKG (full resolution): 380 MB
   ↓ GeoJSON (web): 28.5 MB (simplified geometries)
```

### Key Scripts
- **`scripts/diagnostics/create_tidal_basins_river_based.py`**: Main processing script
- **`scripts/web_optimization/create_web_tidal_basins.py`**: Web optimization

---

## 📁 Files Included in This Release

### Data Files (data/processed/)
- ✅ `tidal_basins_river_based_lev07.gpkg` (380 MB) - **PRIMARY DATASET**
- ✅ `tidal_basins_river_based_lev07_web.geojson` (5.1 MB) - Web version

### Web Files (data/web/)
- ✅ `tidal_basins_precise.geojson` (28.5 MB) - **NEW! For website**
- ✅ `tidal_basins_stats.json` - Summary statistics

### Diagnostic Maps (diagnostics_html/)
- ✅ `tidal_basins_web.html` (22.8 MB)
- ✅ `tidal_basins_with_rivers.html` (175.5 MB)

### Documentation
- ✅ Updated README.md with corrected Dürr types
- ✅ This RELEASE_NOTES.md

---

## 🔮 Next Steps

### Immediate (v1.1)
- [ ] Add GlobSalt salinity predictions
- [ ] Integrate DynQual physics-based features
- [ ] ML model for gaps in Dürr classification

### Future (v2.0)
- [ ] Delineate Tidal Freshwater Zones (TFZ) globally
- [ ] Add OSM water body polygons (actual water surface)
- [ ] Calculate precise water surface areas (not catchments)

---

## 🙏 Acknowledgments

### Data Sources
- **Dürr et al. (2011)**: Estuary typology framework
- **HydroSHEDS BasinATLAS v1.0**: Level 7 basin polygons
- **GRIT v0.6**: Global river network topology
- **GlobSalt v2.0**: Salinity monitoring network

### Software
- **GeoPandas, Folium, Chart.js**: Geospatial processing & visualization
- **AI-Assisted Development**: GitHub Copilot for rapid prototyping

---

## 📜 Citation

When using this dataset, please cite:

```
Nguyen, T. A. (2025). Global Tidal Basin Surface Area Atlas v1.0. 
GitHub: https://github.com/NguyenTruongAnLab/estuary-type-map
Based on Dürr et al. (2011) DOI: 10.1007/s12237-011-9381-y
```
