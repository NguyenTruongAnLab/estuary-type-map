# 📚 Legacy Scripts — Archived for Reference

**Purpose**: Archive of superseded scripts kept for reference and code reuse  
**Date Archived**: October 12, 2025 (Updated: October 13, 2025)  
**⚠️ DO NOT USE THESE SCRIPTS IN CURRENT PIPELINE!**

These scripts have been superseded by improved implementations. They are kept for:
1. **Historical reference** - Understanding project evolution
2. **Code reuse** - Useful functions/approaches that may be needed later
3. **Documentation** - What was tried and why it was changed

---

## 🔴 Key Scripts Analyzed

### process_grit_complete.py — **SUPERSEDED BUT CONTAINS VALUABLE CODE**
**Superseded by**: `scripts/raw_data_processing/process_grit_all_regions.py`

**What it does**:
1. Process GRIT segments (classification)
2. Process GRIT reaches (width data)
3. **🌟 UNIQUE**: Intersect with OSM water polygons for surface area calculation

**Why it's superseded**:
- ❌ **Hardcoded to Asia only** (not generalized for all 7 regions)
- ❌ **Older approach** (inefficient spatial joins)
- ❌ **Steps 1-2 redundant** (now handled by process_grit_all_regions.py)

**What's still valuable**:
- ✅ **Step 3: OSM intersection logic** (lines 495-650)
  - Correct approach for calculating water surface areas
  - Uses `gpd.overlay()` to intersect GRIT reaches with OSM water polygons
  - Converts to equal-area projection (EPSG:6933) for accurate areas
  - **Could be extracted** to new script: `calculate_surface_areas.py` (future work)

**Recommendation**:
- ⛔ **DO NOT RUN** - Use process_grit_all_regions.py instead
- 📚 **KEEP FOR REFERENCE** - OSM intersection approach is valuable
- 🔮 **FUTURE WORK**: Extract surface area logic (Phase 2 of project)

---

## 📋 Complete Superseded Scripts List

| Script | Superseded By | Status | Notes |
|--------|---------------|--------|-------|
| **process_grit_complete.py** | process_grit_all_regions.py | ⚠️ Keep for OSM logic | Contains valuable surface area code |
| process_grit_segments.py | process_grit_all_regions.py | 🗑️ Can delete | Functionality absorbed |
| process_globsalt.py | process_globsalt_integrated.py | 🗑️ Can delete | Integrated version better |
| complete_process.py | process_globsalt_integrated.py | 🗑️ Can delete | Alternative approach, not used |
| process_estuary_data.py | Core processors | 🗑️ Can delete | Functionality absorbed |
| join_salinity_with_geometries.py | process_globsalt_integrated.py | 🗑️ Can delete | Integrated approach |
| integrate_supplementary_data.py | - | ⚪ Optional | Moved to raw_data_processing (GCC data) |
| regenerate_data_with_tidal_zones.py | - | 🗑️ Can delete | Functionality absorbed |

---

## 🗂️ Legacy Documentation (from raw_data_processing/)

### GRIT_FILE_TYPES_GUIDE.md
**Purpose**: Explains GRIT data structure (segments vs reaches vs catchments)  
**Status**: ✅ Keep for reference  
**Why here**: Too detailed for main folder, but useful for deep understanding

### GLOBSALT_INTEGRATION_GUIDE.md
**Purpose**: Detailed guide on GlobSalt-GRIT integration  
**Status**: ✅ Keep for reference  
**Why here**: Superseded by integration in process_grit_all_regions.py, but documents the approach

---

## 🔄 Migration Guide

### OLD Workflow (Legacy - Asia Only):
```powershell
python scripts/legacy/process_grit_complete.py  # ❌ Don't use!
```
**Output**: 
- rivers_grit_segments_classified_asia.gpkg (Asia only)
- rivers_grit_water_polygons_asia.gpkg (with surface areas!)

### NEW Workflow (Current - All 7 Regions):
```powershell
python scripts/raw_data_processing/process_grit_all_regions.py  # ✅ Use this!
```
**Output**: 
- rivers_grit_segments_classified_{region}.gpkg (7 files, ALL regions)
- Ready for ML pipeline!

**Trade-off**: 
- ✅ Gained: Global coverage (all 7 regions)
- ❌ Lost: Surface area calculation (OSM intersection)
- 🔮 Future: Implement global surface area script (Phase 2)

---

## 🔮 Future Work: Surface Area Calculation

**Proposed new script**: `scripts/calculate_surface_areas.py`

**Purpose**: Extract OSM intersection logic from process_grit_complete.py and generalize for all regions

**Pseudo-code**:
```python
def calculate_surface_areas(region_code: str):
    """
    Calculate water surface areas by intersecting GRIT reaches with OSM water polygons.
    
    Input:
        - data/processed/rivers_grit_reaches_classified_{region}.gpkg
        - data/raw/OSM-Water-Layer-Yamazaki_2021/OSM_WaterLayer_POLYGONS.gpkg
    
    Output:
        - data/processed/surface_areas_{region}.gpkg
        - data/processed/surface_areas_summary_{region}.csv
    
    Method:
        1. Load GRIT reaches with classification
        2. Load OSM water polygons
        3. Convert to equal-area projection (EPSG:6933)
        4. Spatial intersection (gpd.overlay)
        5. Calculate areas in km²
        6. Aggregate by system_type and salinity_zone
    
    Reference: process_grit_complete.py lines 495-650
    """
    pass
```

**When to implement**:
- Phase 2: After ML classification complete
- When biogeochemical budget calculations needed
- Requires OSM PBF conversion completed first

---

## 🎯 Summary

| Question | Answer |
|----------|--------|
| **Use these scripts?** | ❌ NO - Use current implementations |
| **Delete these scripts?** | ⚠️ NO - Keep for reference |
| **Why keep them?** | OSM intersection logic, historical reference |
| **What to use instead?** | `scripts/raw_data_processing/process_grit_all_regions.py` |

---

## 📖 See Also

- **scripts/raw_data_processing/README.md** - Current data processing workflow
- **scripts/ml_salinity/README.md** - Machine learning pipeline
- **ROADMAP.md** - Future enhancements (Phase 2: surface area calculations)

---

**Last Updated**: October 13, 2025  
**Key Finding**: process_grit_complete.py contains valuable OSM intersection code for future surface area calculations
