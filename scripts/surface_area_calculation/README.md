# 📐 Surface Area Calculation

**Purpose**: Convert classified river segments to water body polygons and calculate precise surface areas

**Critical Mission**: This is the **ultimate objective** of the project - calculating actual surface areas of water bodies by classification type!

---

## 🎯 The Problem We're Solving

### Current State (After ML Pipeline):
```
rivers_grit_ml_classified_{region}.gpkg
├─ LineString geometries (SEGMENTS - 1D)
├─ Salinity classification (ML predictions)
├─ Geomorphology type (Dürr)
├─ Stream order
└─ NO SURFACE AREA! (Lines don't have area)
```

### What We Need:
```
water_polygons_classified_{region}.gpkg
├─ Polygon geometries (2D - actual water bodies)
├─ Inherited classification from segments
├─ Calculated surface area (km²)
└─ Aggregated by classification type
```

---

## 🔄 Complete Workflow

```
PHASE 1: CLASSIFICATION (COMPLETED)
    ↓
raw_data_processing/process_grit_all_regions.py
    ├─ Creates: rivers_grit_segments_classified_*.gpkg (LineStrings)
    ├─ Has: Topology, stream order, preliminary classification
    └─ Missing: Surface area!
    ↓
ml_salinity/ml_dynqual_master_pipeline.py
    ├─ Creates: ML salinity predictions for ALL segments
    ├─ Output: rivers_grit_ml_classified_*.gpkg (updated classifications)
    └─ Still LineStrings - no surface area!
    ↓
PHASE 2: SURFACE AREA CALCULATION ← WE ARE HERE!
    ↓
surface_area_calculation/ (THIS FOLDER)
    ├─ Loads: ML-classified segments (LineStrings)
    ├─ Loads: GRIT reaches (LineStrings + width data)
    ├─ Loads: OSM water polygons (actual water bodies)
    ├─ Process: Intersect and assign classifications
    └─ Creates: water_polygons_classified_*.gpkg (Polygons with area!)
    ↓
waterbody_classification/
    ├─ Aggregates: Surface areas by classification
    ├─ Creates: Summary statistics by type/region
    └─ Output: Publication-ready results!
```

---

## 📁 Scripts in This Folder

### 🌟 1. calculate_surface_areas_master.py — **MASTER SCRIPT**
**Status**: ⏳ To be implemented (Phase 2, Week 1)  
**Purpose**: Orchestrate complete surface area calculation pipeline

**What it does**:
1. Loads ML-classified segments (from ml_salinity/)
2. Calls individual processing scripts
3. Validates results
4. Generates summary reports

**Usage**:
```powershell
# Process all regions
python scripts/surface_area_calculation/calculate_surface_areas_master.py --all-regions

# Process single region (testing)
python scripts/surface_area_calculation/calculate_surface_areas_master.py --region EU
```

---

### 2. step1_load_ml_classifications.py
**Status**: ⏳ To be implemented  
**Purpose**: Load ML classification results and prepare for polygon conversion

**Input**:
- `data/processed/ml_classified/rivers_grit_ml_classified_{region}.gpkg` (from ML pipeline)

**Output**:
- In-memory GeoDataFrame with complete classification

**Method**:
```python
def load_ml_classifications(region_code):
    """
    Load ML-classified segments with all attributes:
    - global_id (PRIMARY KEY)
    - salinity_class_final (ML prediction or GlobSalt)
    - confidence_level (HIGH/MEDIUM-HIGH/MEDIUM/LOW)
    - classification_method (ML_Predicted or GlobSalt_Validated)
    - durr_estuary_type (if in catchment)
    - strahler_order
    - geometry (LineString)
    """
    segments = gpd.read_file(f'data/processed/ml_classified/rivers_grit_ml_classified_{region_code}.gpkg')
    
    # Validate required columns
    required = ['global_id', 'salinity_class_final', 'confidence_level', 'geometry']
    assert all(col in segments.columns for col in required)
    
    return segments
```

---

### 3. step2_load_grit_reaches_with_width.py
**Status**: ⏳ To be implemented  
**Purpose**: Load GRIT reaches with width measurements for polygon conversion

**Input**:
- `data/raw/GRIT-Michel_2025/GRITv06_reaches_{region}_EPSG4326.gpkg`

**Output**:
- GeoDataFrame with width data

**Method**:
```python
def load_grit_reaches(region_code):
    """
    GRIT reaches have critical width data:
    - grwl_width_median (satellite-derived width in meters)
    - length (segment length)
    - segment_id (links to classified segments)
    """
    reaches = gpd.read_file(f'data/raw/GRIT-Michel_2025/GRITv06_reaches_{region_code}_EPSG4326.gpkg')
    
    # Filter to reaches with width data
    has_width = reaches['grwl_width_median'].notna()
    print(f"Reaches with width: {has_width.sum():,} / {len(reaches):,} ({has_width.sum()/len(reaches)*100:.1f}%)")
    
    return reaches
```

---

### 4. step3_intersect_with_osm_polygons.py — **CRITICAL STEP**
**Status**: ⏳ To be implemented (extracts logic from process_grit_complete.py)  
**Purpose**: Intersect classified reaches with actual OSM water body polygons

**Input**:
- ML-classified segments (from step 1)
- GRIT reaches with width (from step 2)
- `data/raw/OSM-Water-Layer-Yamazaki_2021/OSM_WaterLayer_POLYGONS.gpkg`

**Output**:
- `data/processed/surface_areas/water_polygons_classified_{region}.gpkg`

**Method** (adapted from process_grit_complete.py lines 495-650):
```python
def intersect_with_osm_water(classified_segments, grit_reaches, osm_polygons):
    """
    The CORRECT approach for polygon-based surface area:
    1. Join classified segments with GRIT reaches (inherit classification)
    2. Convert to equal-area projection (EPSG:6933)
    3. Spatial intersection: reaches ⨂ OSM water polygons
    4. Calculate area in km²
    5. Aggregate by classification
    """
    
    # Step 1: Join classifications to reaches
    reaches_classified = grit_reaches.merge(
        classified_segments[['global_id', 'salinity_class_final', 'durr_estuary_type']],
        left_on='segment_id',
        right_on='global_id',
        how='left'
    )
    
    # Step 2: Convert to equal-area projection
    reaches_ea = reaches_classified.to_crs('EPSG:6933')
    osm_ea = osm_polygons.to_crs('EPSG:6933')
    
    # Step 3: Spatial intersection (gpd.overlay)
    water_polygons = gpd.overlay(
        reaches_ea,
        osm_ea,
        how='intersection',
        keep_geom_type=False  # Allow polygon output
    )
    
    # Step 4: Calculate area
    water_polygons['area_km2'] = water_polygons.geometry.area / 1e6
    
    # Step 5: Add metadata
    water_polygons['calculation_method'] = 'OSM_Intersection'
    water_polygons['projection'] = 'EPSG:6933_EqualArea'
    
    return water_polygons
```

**Why this is CORRECT**:
- ✅ Uses **actual water body polygons** (OSM), not buffered lines
- ✅ **Equal-area projection** (EPSG:6933) for accurate area calculation
- ✅ **Inherits ML classification** from segments
- ✅ **Direct measurement**, not estimation

---

### 5. step4_calculate_areas_by_classification.py
**Status**: ⏳ To be implemented  
**Purpose**: Aggregate surface areas by classification type

**Input**:
- Water polygons from step 3

**Output**:
- `data/processed/surface_areas/summary_by_salinity_{region}.csv`
- `data/processed/surface_areas/summary_by_geomorphology_{region}.csv`
- `data/processed/surface_areas/summary_combined_{region}.csv`

**Method**:
```python
def aggregate_surface_areas(water_polygons):
    """
    Calculate surface areas by:
    1. Salinity class (Venice System)
    2. Geomorphology type (Dürr)
    3. Combined (salinity + geomorphology)
    4. Stream order
    5. Confidence level
    """
    
    # By salinity class
    by_salinity = water_polygons.groupby('salinity_class_final').agg({
        'area_km2': ['sum', 'mean', 'std', 'count'],
        'confidence_level': lambda x: x.mode()[0] if len(x) > 0 else 'Unknown'
    })
    
    # By geomorphology
    by_geomorph = water_polygons.groupby('durr_estuary_type').agg({
        'area_km2': ['sum', 'mean', 'std', 'count']
    })
    
    # Combined (salinity × geomorphology)
    by_combined = water_polygons.groupby(['salinity_class_final', 'durr_estuary_type']).agg({
        'area_km2': ['sum', 'mean', 'std', 'count']
    })
    
    return {
        'by_salinity': by_salinity,
        'by_geomorphology': by_geomorph,
        'by_combined': by_combined
    }
```

---

### 6. step5_handle_missing_width_data.py
**Status**: ⏳ To be implemented  
**Purpose**: Estimate width for reaches without GRWL measurements

**Input**:
- Reaches without width data (~50-70% of reaches)

**Output**:
- Estimated widths using hydraulic relationships

**Method**:
```python
def estimate_width_from_drainage_area(drainage_area_km2, strahler_order):
    """
    Empirical width-discharge relationships (Andreadis et al. 2013)
    
    Width (m) = a × DrainageArea^b
    
    Coefficients by stream order:
    Order 1-2: a=2.0, b=0.4
    Order 3-4: a=3.5, b=0.5
    Order 5-6: a=5.0, b=0.6
    Order 7+:   a=8.0, b=0.7
    """
    if strahler_order <= 2:
        a, b = 2.0, 0.4
    elif strahler_order <= 4:
        a, b = 3.5, 0.5
    elif strahler_order <= 6:
        a, b = 5.0, 0.6
    else:
        a, b = 8.0, 0.7
    
    width_m = a * (drainage_area_km2 ** b)
    
    return width_m
```

---

### 7. step6_validate_against_literature.py
**Status**: ⏳ To be implemented  
**Purpose**: Validate calculated areas against published estimates

**Input**:
- Calculated surface areas (from step 4)
- Baum 2024 measurements (106 large estuaries)
- Laruelle 2025 estimates

**Output**:
- Validation report with comparisons

**Method**:
```python
def validate_against_literature(calculated_areas):
    """
    Compare to:
    1. Baum et al. (2024): 106 large estuary measurements
    2. Laruelle et al. (2025): Global estuarine area = 733,801 km²
    3. Dürr et al. (2011): Global estuarine area = 1,067,000 km²
    
    Calculate:
    - Percent difference
    - RMSE for Baum systems
    - Systematic bias assessment
    """
    
    # Load Baum reference data
    baum = gpd.read_file('data/processed/baum_morphometry.geojson')
    
    # Match by name and location
    matched = match_systems(calculated_areas, baum)
    
    # Calculate metrics
    rmse = np.sqrt(np.mean((matched['calculated_area'] - matched['baum_area'])**2))
    bias = np.mean(matched['calculated_area'] - matched['baum_area'])
    
    return {
        'rmse_km2': rmse,
        'bias_km2': bias,
        'percent_diff': (bias / matched['baum_area'].mean()) * 100
    }
```

---

## 🔑 Key Design Decisions

### Why Use OSM Polygons Instead of Buffering?
**❌ WRONG Approach** (what some studies do):
```python
# Buffer river lines by width
river_polygon = river_line.buffer(width / 2)
```
**Problems**:
- Circular buffers don't match real river shapes
- Overlaps and gaps at confluences
- No lakes, wetlands, or wide estuaries

**✅ CORRECT Approach** (what we do):
```python
# Intersect with actual water body polygons
water_polygon = geopandas.overlay(river_line, osm_water_polygon)
```
**Advantages**:
- Actual water body shapes (not circles!)
- Includes lakes, reservoirs, wide estuaries
- Validated by satellite imagery (OSM source)

---

### Why Equal-Area Projection (EPSG:6933)?
**Problem with WGS84 (EPSG:4326)**:
```python
# WGS84 (degrees) - area calculation is WRONG!
area_wrong = polygon_wgs84.geometry.area  # Units: deg²  ← WRONG!
```

**Solution with Equal-Area**:
```python
# Convert to equal-area projection
polygon_ea = polygon_wgs84.to_crs('EPSG:6933')  # World Cylindrical Equal Area
area_km2 = polygon_ea.geometry.area / 1e6  # Units: m² → km²  ← CORRECT!
```

**EPSG:6933 Advantages**:
- ✅ Preserves area globally (equal-area property)
- ✅ Suitable for global analysis
- ✅ Standard for global area calculations

---

### Why Join ML Classifications to Reaches?
**Data structure**:
```
GRIT Segments (LineStrings):
- global_id: unique ID
- Topology: upstream/downstream
- NO width data ❌

GRIT Reaches (LineStrings):
- reach_id: unique ID  
- segment_id: links to segments ✅
- grwl_width_median: satellite width ✅
- Uniform length (500m-1km)

ML Classifications:
- global_id: links to segments ✅
- salinity_class_final: ML prediction ✅
```

**Join strategy**:
1. ML classifies **segments** (has segment IDs)
2. Reaches link to **segments** (has segment_id foreign key)
3. **Join**: reaches ← segments (inherit classification)
4. **Intersect**: reaches ⨂ OSM polygons (get actual water bodies)

---

## 📊 Expected Outputs

### Final Surface Area Database:
```
data/processed/surface_areas/
├── water_polygons_classified_af.gpkg      # Africa
├── water_polygons_classified_as.gpkg      # Asia
├── water_polygons_classified_eu.gpkg      # Europe
├── water_polygons_classified_na.gpkg      # North America
├── water_polygons_classified_sa.gpkg      # South America
├── water_polygons_classified_si.gpkg      # Siberia
├── water_polygons_classified_sp.gpkg      # South Pacific
├── summary_by_salinity_global.csv         # Aggregated by Venice System
├── summary_by_geomorphology_global.csv    # Aggregated by Dürr types
├── summary_combined_global.csv            # Salinity × Geomorphology
└── validation_report.pdf                  # Comparison to literature
```

### Example Summary Table (by_salinity_global.csv):
| Salinity Class | Total Area (km²) | Mean Area (km²) | Count | % of Total |
|----------------|------------------|-----------------|-------|------------|
| Freshwater     | 1,245,000        | 0.15            | 8.3M  | 85%        |
| Oligohaline    | 89,500           | 2.5             | 35K   | 6%         |
| Mesohaline     | 45,200           | 8.2             | 5.5K  | 3%         |
| Polyhaline     | 28,700           | 15.3            | 1.8K  | 2%         |
| Euhaline       | 12,100           | 45.6            | 265   | 1%         |
| **TOTAL**      | **1,420,500**    | -               | 8.34M | 100%       |

---

## 🔗 Dependencies

**Input from other folders**:
1. ✅ `scripts/ml_salinity/` → ML classification results (PRIMARY INPUT!)
2. ✅ `data/raw/GRIT-Michel_2025/` → Reaches with width data
3. ✅ `data/raw/OSM-Water-Layer-Yamazaki_2021/` → Water body polygons
4. ✅ `scripts/raw_data_processing/process_baum.py` → Validation data

**Outputs used by**:
- `scripts/waterbody_classification/` → Classification aggregations
- `scripts/web_optimization/` → Web atlas visualization
- **Publication**: Main results tables and figures!

---

## 🚀 Implementation Priority

**Phase 2 - Highest Priority (THE ULTIMATE OBJECTIVE!)**

### Week 1: Core Infrastructure
1. ✅ `step1_load_ml_classifications.py` - Load ML results
2. ✅ `step2_load_grit_reaches_with_width.py` - Load GRIT reaches
3. ✅ `step3_intersect_with_osm_polygons.py` - **CRITICAL** OSM intersection

### Week 2: Area Calculation
4. ✅ `step4_calculate_areas_by_classification.py` - Aggregate areas
5. ⚪ `step5_handle_missing_width_data.py` - Width estimation

### Week 3: Validation & Master Script
6. ⚪ `step6_validate_against_literature.py` - Literature comparison
7. ✅ `calculate_surface_areas_master.py` - Master orchestrator

---

## ⚠️ Critical Notes

### About process_globsalt_integrated.py:
**Status**: ⚠️ **OBSOLETE** - DO NOT USE!

**Why obsolete**:
- Uses raw GlobSalt data (only 0.7-25% coverage)
- Does NOT use ML predictions (which fill gaps to 100%!)
- Superseded by this folder's workflow

**Correct workflow**:
```
❌ OLD: process_globsalt_integrated.py (raw GlobSalt → surface areas)
✅ NEW: ml_salinity/ (ML predictions) → surface_area_calculation/ (this folder)
```

### About OSM_WaterLayer_POLYGONS.gpkg:
**File size**: ~560 MB (manageable!)  
**Format**: GPKG with single 'water_polygons' layer  
**Coverage**: Global water bodies from OSM  
**Source**: Yamazaki et al. (2021) processing of OSM data

**How to use**:
```python
# Load OSM water polygons
osm_water = gpd.read_file('data/raw/OSM-Water-Layer-Yamazaki_2021/OSM_WaterLayer_POLYGONS.gpkg')

# Filter to region (use bounding box for efficiency)
region_bbox = get_region_bbox('EU')
osm_region = osm_water.cx[region_bbox[0]:region_bbox[2], region_bbox[1]:region_bbox[3]]
```

### About BasinATLAS_v10_lev07_QGIS.gpkg:
**File size**: 401.75 MB  
**Format**: GPKG with global watershed polygons  
**Coverage**: Global, Level 7 (Pfafstetter hierarchy)  
**Source**: HydroSHEDS BasinATLAS v1.0

**Why NOT used for polygon conversion**:
- ❌ Level 7 is too coarse (1,000-10,000 km² per basin)
- ❌ Does NOT align with GRIT segments (different discretization)
- ❌ No direct linkage to river segments
- ❌ Wrong resolution for fine-scale classification

**When to use BasinATLAS** (Phase 3 - Future):
- ✅ **Enrichment attributes**: Land use, climate, population (500+ attributes)
- ✅ **Discharge estimates**: Mean annual discharge (dis_m3_pyr)
- ✅ **Runoff data**: Annual runoff (run_mm_syr)
- ✅ **Validation**: Compare against DynQual modeled data

**For Phase 2, use instead**:
- ✅ **GRIT Component Catchments**: Perfect alignment with segments
- ✅ **GRIT Reaches**: Width data for polygon conversion
- ✅ **OSM Water Polygons**: Actual water body shapes

**See**: `docs/BASIN_DATA_COMPARISON.md` for complete analysis

---

## 📖 Scientific References

1. **Yamazaki et al. (2021)** - OSM Water Layer Processing
   - DOI: 10.1002/2017GL072874
   - High-resolution global water body database

2. **Andreadis et al. (2013)** - Width-Discharge Relationships
   - For estimating widths where GRWL unavailable

3. **Laruelle et al. (2025)** - Global Estuarine Area Estimates
   - Validation reference: 733,801 ± 39,892 km²

4. **Baum et al. (2024)** - Large Estuary Morphometry
   - Validation reference: 106 measured systems

---

**Created**: October 13, 2025  
**Status**: Folder structure ready, scripts to be implemented in Phase 2  
**Priority**: ⭐⭐⭐ **HIGHEST** - This is the ultimate objective!  
**Next**: Implement step1-step3 (Week 1 of Phase 2)
