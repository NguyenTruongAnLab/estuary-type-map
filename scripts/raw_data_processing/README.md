# 📊 Raw Data Processing

**Purpose**: Convert raw datasets into standardized GPKG format for Machine Learning pipeline

**CRITICAL**: This folder creates the **foundation files** that the ML pipeline (scripts/ml_salinity/) depends on.

---

## 🎯 What This Folder Does

This folder processes **raw external datasets** into standardized GPKG files that serve as inputs for:
1. **Machine Learning classification** (scripts/ml_salinity/)
2. **Web visualization** (scripts/web_optimization/)
3. **Surface area calculations** (future scripts/)

**All scripts output to**: `data/processed/`

---

## 🔄 Processing Workflow

```
RAW DATA                    RAW_DATA_PROCESSING          ML_SALINITY
----------                  -------------------          -----------
GRIT v0.6    ──────────>   process_grit_all_regions.py ──────> ml_step1_extract_features.py
(20.5M segments)            ↓                                   ↓
                            rivers_grit_segments_classified_*.gpkg (7 regions)
                            ├─ global_id                        ├─ Extract features
                            ├─ salinity_zone (GlobSalt)        ├─ Add Dürr context
                            ├─ strahler_order                   ├─ Calculate distances
                            ├─ dist_to_coast_km                 └─> features_*.parquet
                            └─ geometry
                                    ↓
Dürr 2011    ──────────>   process_durr.py
(7,057 catchments)          ↓
                            durr_estuaries.geojson
                            ├─ FIN_TYP (estuary type)           ├─ Spatial join
                            ├─ Cat_Name                         └─> ML features
                            └─ geometry (catchment polygons)
                                    ↓
Baum 2024    ──────────>   process_baum.py
(271 large estuaries)       ↓
                            baum_morphometry.geojson
                            ├─ Geomorphotype                    ├─ Validation data
                            ├─ Surface area (km²)               └─> Not used in training
                            └─ geometry (point)
                                    ↓
GCC 2024     ──────────>   integrate_supplementary_data.py
(728K coastal segments)     ↓
                            durr_estuaries_enhanced.geojson
                            ├─ Coastal characteristics          ├─> OPTIONAL
                            └─ Socioeconomic data               └─> For future analysis
```

---

## 📁 Scripts in This Folder

### 🌟 1. process_grit_all_regions.py — **CRITICAL FOUNDATION**
**Purpose**: Process GRIT v0.6 into ML-ready format  
**Duration**: 40-60 minutes (ALL 7 regions)  
**Priority**: ⭐⭐⭐ **MUST RUN FIRST** - ML pipeline depends on this!

**Input**: 
- `data/raw/GRIT-Michel_2025/GRITv06_segments_{region}_EPSG4326.gpkg` (7 regions)
- `data/raw/GlobSalt/salinity_zones.geojson` (for initial classification)

**Output**: 
- `data/processed/rivers_grit_segments_classified_{region}.gpkg` (7 files)
- `data/processed/rivers_grit_reaches_classified_{region}.gpkg` (7 files, optional)

**What it does**:
1. **Loads GRIT segments** for each region (AF, AS, EU, NA, SA, SI, SP)
2. **Joins with GlobSalt salinity zones** (Venice System: <0.5, 0.5-5, 5-18, 18-30, >30 PSU)
3. **Calculates distance to coast** (network distance to nearest coastal outlet)
4. **Preliminary classification**: Estuarine vs Non-Tidal vs Endorheic
5. **Saves to GPKG** with complete attributes for ML feature extraction

**Key output columns**:
```python
{
    'global_id': int,                  # Unique segment ID (PRIMARY KEY for ML)
    'salinity_zone': str,              # Venice System (Freshwater/Oligohaline/etc.)
    'salinity_mean_psu': float,        # Mean salinity from GlobSalt
    'has_salinity': int,               # 1 if GlobSalt measurement exists, 0 otherwise
    'system_type': str,                # Estuarine/Non-Tidal/Endorheic
    'strahler_order': int,             # Stream order (1-12)
    'dist_to_coast_km': float,         # Distance to coast (for TFZ)
    'is_mainstem': bool,               # Main channel flag
    'geometry': LineString             # River segment geometry
}
```

**Why this matters for ML**:
- ✅ `has_salinity=1` segments → **Training data** (GlobSalt-validated, 0.7-25% of segments)
- ✅ `has_salinity=0` segments → **Prediction targets** (ML will classify these, 75-99.3%)
- ✅ `global_id` → Primary key to join features, predictions, and geometries

**Usage**:
```powershell
# Process all 7 regions (recommended)
python scripts/raw_data_processing/process_grit_all_regions.py

# Or specific regions only
python scripts/raw_data_processing/process_grit_all_regions.py --regions EU NA
```

**Expected output size**: ~5.5 GB total (7 files × ~700 MB each)

**Scientific rationale**: 
GRIT provides 20.5M high-resolution river segments with:
- Satellite-derived widths (GRWL, 30m resolution)
- Complete network topology (upstream/downstream connectivity)
- Strahler stream order (discharge proxy)

This enables:
1. **Direct surface area measurement** (length × width, not extrapolation)
2. **Network distance calculations** (for TFZ extent modeling)
3. **Topological features** (stream order, bifurcations) for ML

---

### 2. process_durr.py — Estuary Geomorphology Database
**Purpose**: Process Dürr 2011 expert-classified estuary typology  
**Duration**: 5-10 minutes  
**Priority**: ⭐⭐ Important for ML features and validation

**Input**: 
- `data/raw/Worldwide-typology-Shapefile-Durr_2011/typology_catchments.shp`

**Output**: 
- `data/processed/durr_estuaries.geojson` (~3 MB)
- `data/processed/durr_estuaries_metadata.json`

**What it does**:
1. **Loads 7,057 estuary catchments** globally
2. **Classifies by geomorphology**: Delta, Fjord, Lagoon, Coastal Plain, Karst, Archipelagic, Small Deltas
3. **Extracts catchment boundaries** (watershed polygons, not salinity extent!)
4. **Generates statistics** by estuary type and continent

**Key output columns**:
```python
{
    'FIN_TYP': int,                    # Estuary type (0-6)
    'Cat_Name': str,                   # Catchment name
    'BASINAREA': float,                # Catchment area (km²)
    'Ocean': str,                      # Receiving ocean basin
    'geometry': Polygon                # Catchment boundary
}
```

**Estuary type mapping**:
```python
{
    0: 'Karst',              # Limestone dissolution features
    1: 'Coastal Plain',      # Low-gradient drowned valleys
    2: 'Delta',              # Distributary networks, high sediment
    3: 'Lagoon',             # Barrier-enclosed water bodies
    4: 'Fjord',              # Glacially carved, deep, steep
    5: 'Archipelagic',       # Island-studded systems
    6: 'Small Deltas'        # Minor distributary systems
}
```

**Why this matters for ML**:
- ✅ **ML Feature**: `is_in_durr_catchment` (binary flag)
- ✅ **ML Feature**: `durr_estuary_type` (0-6 encoded)
- ✅ **Validation**: Independent expert classification to compare against ML predictions
- ✅ **Geomorphological context**: Links salinity to physical template (deltas have longer TFZ than fjords)

**CRITICAL NOTE**: 
Dürr catchments are **watershed boundaries**, NOT salinity extent!
- A "Delta" catchment may be 99% freshwater (inland)
- Only the lower 10-50 km (near coast) is estuarine
- Use for typology and validation, NOT for direct salinity classification

**Usage**:
```powershell
python scripts/raw_data_processing/process_durr.py
```

**Scientific rationale**: 
Dürr et al. (2011) provides peer-reviewed, expert-classified estuary types based on:
- Geomorphological characteristics
- Sediment dynamics
- Mixing patterns
- 40+ years of field observations

This is **gold-standard validation data** for ML, not training data (different from GlobSalt which provides salinity measurements).

---

### 3. process_baum.py — Large Estuary Morphometry
**Purpose**: Process Baum 2024 quantitative morphometry measurements  
**Duration**: 5-10 minutes  
**Priority**: ⭐ Nice-to-have (validation only, not used in ML training)

**Input**: 
- `data/raw/Large-estuaries-Baum_2024/Baum_2024_Geomorphology.csv`

**Output**: 
- `data/processed/baum_morphometry.geojson` (~100 KB)
- `data/processed/baum_morphometry_metadata.json`

**What it does**:
1. **Loads 106 large estuaries** (>10 km² surface area)
2. **Extracts morphometric measurements**: surface area, length, width, depth, tidal range
3. **Creates point features** at estuary centroids (lat/lon from CSV)
4. **Validates against Dürr classification** (cross-reference)

**Key output columns**:
```python
{
    'Estuary': str,                    # Estuary name
    'Geomorphotype': str,              # Baum classification
    'Surface_area_km2': float,         # Field-measured area
    'Along_channel_length_km': float,  # Length
    'Average_width_km': float,         # Width
    'Tidal_range_m': float,            # Tidal range
    'Lat': float,                      # Latitude
    'Long': float,                     # Longitude
    'geometry': Point                  # Centroid location
}
```

**Why this matters**:
- ✅ **Validation**: Compare GIS-calculated areas vs field measurements
- ✅ **Tidal extent estimation**: Tidal range correlates with TFZ extent
- ⚠️ **NOT used in ML training**: Only 106 estuaries (too small sample)

**Limitation**: 
Only large estuaries (>10 km²) are included. Global total of ~150,000 estuaries are mostly smaller (<1 km²). Baum validates the big ones; GRIT + ML provides comprehensive coverage of all sizes.

**Usage**:
```powershell
python scripts/raw_data_processing/process_baum.py
```

**Scientific rationale**: 
Baum et al. (2024) provides **field-measured morphometry** for large estuaries. This is ground-truth data for validating:
- Surface area calculations (GIS vs field measurements)
- Geomorphological relationships (length, width, depth)
- Tidal characteristics (range, dominance)

---

### 4. integrate_supplementary_data.py — GCC Coastal Characteristics (OPTIONAL)
**Purpose**: Add Global Coastal Characteristics (GCC) dataset to Dürr estuaries  
**Duration**: 10-15 minutes  
**Priority**: ⚪ OPTIONAL - Not required for ML pipeline

**Input**: 
- `data/processed/durr_estuaries.geojson` (from process_durr.py)
- `data/raw/GCC-Panagiotis-Athanasiou_2024/GCC_geophysical.csv`
- `data/raw/GCC-Panagiotis-Athanasiou_2024/GCC_hydrometeorological.csv`
- `data/raw/GCC-Panagiotis-Athanasiou_2024/GCC_socioeconomic.csv`

**Output**: 
- `data/processed/durr_estuaries_enhanced.geojson` (with GCC attributes)

**What it does**:
1. **Spatial join**: Dürr catchments ↔ GCC coastal segments (10 km buffer)
2. **Aggregates GCC data**: Wave height, tidal range, storm surge, population, GDP
3. **Enhances Dürr polygons** with coastal characteristics
4. **Creates enriched dataset** for socioeconomic and hazard analysis

**Key GCC attributes added**:
```python
{
    'gcc_wave_height_m': float,        # Mean significant wave height
    'gcc_tidal_range_m': float,        # Mean tidal range
    'gcc_storm_surge_m': float,        # 100-year storm surge
    'gcc_population': int,             # Coastal population
    'gcc_gdp_usd': float,              # Regional GDP
    'gcc_segment_count': int           # Number of GCC segments in estuary
}
```

**Why this is OPTIONAL**:
- ❌ **NOT used in current ML pipeline** (focused on salinity classification only)
- ✅ **Future use**: Socioeconomic analysis, hazard assessment, policy applications
- ✅ **Complementary**: Adds context to estuary classification

**Usage**:
```powershell
python scripts/raw_data_processing/integrate_supplementary_data.py
```

**When to use**:
- For socioeconomic studies (population exposure, economic value)
- For hazard assessment (storm surge, sea level rise vulnerability)
- For policy applications (prioritization, risk management)
- NOT needed for basic ML classification pipeline

---

### 5. process_globsalt_integrated.py — GlobSalt Integration (LEGACY - NOT NEEDED)
**Purpose**: Integrate GlobSalt salinity with GRIT reaches  
**Status**: ⚠️ **LEGACY** - Functionality now integrated into `process_grit_all_regions.py`

**Why this exists**:
- Historical script from earlier project phase
- Kept for reference and debugging
- Functionality merged into process_grit_all_regions.py for efficiency

**Current workflow** (better):
```
process_grit_all_regions.py (Step 1)
    ↓
Creates rivers_grit_segments_classified_*.gpkg with GlobSalt data already joined
    ↓
ml_step1_extract_features.py (Step 2)
    ↓
Extracts ML features directly from classified segments
```

**Old workflow** (inefficient):
```
process_grit_all_regions.py → basic GRIT
    ↓
process_globsalt_integrated.py → add salinity
    ↓
ml_step1_extract_features.py → extract features
```

**Recommendation**: 
- ✅ Use `process_grit_all_regions.py` (includes GlobSalt integration)
- ❌ Skip `process_globsalt_integrated.py` (redundant)
- 📚 Keep file for documentation and debugging reference

---

## 🔗 Relationship with ML Pipeline (scripts/ml_salinity/)

This folder creates the **foundation files** that ML uses:

```
RAW_DATA_PROCESSING                     ML_SALINITY
-------------------                     -----------

process_grit_all_regions.py   ────┐
                                   ├──> ml_step1_extract_features.py
process_durr.py               ────┤    └─> features_*.parquet
                                   │
process_baum.py               ────┘         ↓
(optional)                              ml_step2_train_model.py
                                            └─> trained model
                                                 ↓
                                            ml_step3_predict.py
                                                └─> classified segments
                                                     ↓
                                                ml_step4_validate_improved.py
                                                    └─> validation reports
```

**Key files ML needs from this folder**:
1. ✅ `rivers_grit_segments_classified_{region}.gpkg` (7 files) — **REQUIRED**
2. ✅ `durr_estuaries.geojson` — **REQUIRED** (for features + validation)
3. ⚪ `baum_morphometry.geojson` — OPTIONAL (validation only)

---

## 📋 Recommended Run Order

### **For ML Pipeline** (MINIMUM):
```powershell
# Step 1: Process GRIT (CRITICAL - creates ML input files)
python scripts/raw_data_processing/process_grit_all_regions.py

# Step 2: Process Dürr (REQUIRED - for ML features)
python scripts/raw_data_processing/process_durr.py

# Step 3: Process Baum (OPTIONAL - validation only)
python scripts/raw_data_processing/process_baum.py

# Now ready for ML pipeline!
python scripts/ml_salinity/ml_dynqual_master_pipeline.py --all-regions
```

### **For Complete Analysis** (with supplementary data):
```powershell
# All raw data processing
python scripts/raw_data_processing/process_grit_all_regions.py
python scripts/raw_data_processing/process_durr.py
python scripts/raw_data_processing/process_baum.py
python scripts/raw_data_processing/integrate_supplementary_data.py  # OPTIONAL

# Then ML pipeline
python scripts/ml_salinity/ml_dynqual_master_pipeline.py --all-regions
```

---

## 📊 Output Files Summary

| File | Size | Purpose | ML Uses? |
|------|------|---------|----------|
| `rivers_grit_segments_classified_{region}.gpkg` | ~700 MB each | GRIT segments with GlobSalt | ✅ YES - Primary input |
| `rivers_grit_reaches_classified_{region}.gpkg` | ~1.5 GB each | GRIT reaches with width | ⚪ OPTIONAL - Surface area |
| `durr_estuaries.geojson` | ~3 MB | Estuary typology | ✅ YES - Features + validation |
| `baum_morphometry.geojson` | ~100 KB | Large estuary measurements | ⚪ OPTIONAL - Validation |
| `durr_estuaries_enhanced.geojson` | ~5 MB | Dürr + GCC attributes | ❌ NO - Future analysis |

**Total storage needed**: ~6-12 GB (depending on whether you keep reaches files)

---

## 🐛 Troubleshooting

### "FileNotFoundError: rivers_grit_segments_classified_*.gpkg"
**Problem**: ML pipeline can't find GRIT segment files  
**Solution**: Run `process_grit_all_regions.py` first!
```powershell
python scripts/raw_data_processing/process_grit_all_regions.py
```

### "process_grit_all_regions.py takes too long (>2 hours)"
**Problem**: Processing all 7 regions + reaches is slow  
**Solution**: Skip reaches if you only need ML classification
```powershell
python scripts/raw_data_processing/process_grit_all_regions.py --skip-reaches
```

### "Out of memory error during GRIT processing"
**Problem**: GRIT files are large (351K-3M segments per region)  
**Solution**: Process one region at a time
```powershell
python scripts/raw_data_processing/process_grit_all_regions.py --regions EU
python scripts/raw_data_processing/process_grit_all_regions.py --regions NA
# ... etc
```

---

## 📚 Additional Documentation

- **GRIT_FILE_TYPES_GUIDE.md**: Explains segments vs reaches vs catchments
- **GLOBSALT_INTEGRATION_GUIDE.md**: Details of salinity integration (LEGACY)
- **scripts/ml_salinity/README.md**: ML pipeline documentation

---

**Next Steps**: After running these scripts, proceed to `scripts/ml_salinity/` for machine learning classification!
- Loads morphometry data for 106 large global estuaries
- Extracts width, length, area, volume, depth metrics
- Links to tidal characteristics
- Provides validation for automated surface area calculations

**Scientific rationale**: Baum provides detailed field measurements of large estuaries. This validates our automated GIS-based surface area calculations and provides ground-truth data.

**Usage**:
```powershell
python scripts/raw_data_processing/process_baum.py
```

**Key output columns**:
- `estuary_name`: Estuary identifier
- `surface_area_km2`: Measured surface area
- `length_km`: Along-channel length
- `width_avg_km`: Average width
- `tidal_range_m`: Mean tidal range

---

### 4. process_globsalt_integrated.py
**Purpose**: Integrate GlobSalt salinity measurements with GRIT network  
**Duration**: 30-45 minutes  
**Input**: `data/raw/GlobSalt/*.csv` + GRIT segments  
**Output**: Updated GRIT files with salinity zones

**What it does**:
- Loads GlobSalt v2.0 (270K stations, 15M measurements)
- Converts conductivity to salinity (PSU)
- Creates salinity zones with 10 km buffers
- Spatially joins with GRIT river segments
- Classifies using Venice System thresholds

**Scientific rationale**: GlobSalt provides field measurements of actual salinity. This is the GOLD STANDARD for estuarine classification, far superior to distance-based proxies.

**Usage**:
```powershell
python scripts/raw_data_processing/process_globsalt_integrated.py
```

**Key output**: Adds `salinity_mean_psu` and `salinity_zone` columns to GRIT segments

---

## 🔄 Execution Order

These scripts should be run in this order (handled automatically by `master_pipeline.py`):

1. **process_grit_all_regions.py** (foundational)
2. **process_durr.py** (validation data)
3. **process_baum.py** (validation data)
4. **process_globsalt_integrated.py** (if updating salinity)

---

## 📊 Output Files

All scripts output to `data/processed/`:

```
data/processed/
├── rivers_grit_segments_classified_af.gpkg     # Africa
├── rivers_grit_segments_classified_as.gpkg     # Asia
├── rivers_grit_segments_classified_eu.gpkg     # Europe
├── rivers_grit_segments_classified_na.gpkg     # North America
├── rivers_grit_segments_classified_sa.gpkg     # South America
├── rivers_grit_segments_classified_si.gpkg     # Siberia
├── rivers_grit_segments_classified_sp.gpkg     # South Pacific
├── durr_estuaries.geojson                      # Dürr catchments
├── durr_estuaries_metadata.json                # Dürr metadata
├── baum_morphometry.geojson                    # Baum estuaries
└── baum_morphometry_metadata.json              # Baum metadata
```

---

## 🔬 Scientific Context

### Why These Datasets?

1. **GRIT v0.6**: State-of-the-art global river network with satellite-derived widths
2. **Dürr 2011**: Only global estuary typology database (peer-reviewed)
3. **Baum 2024**: Most comprehensive large estuary measurements
4. **GlobSalt v2.0**: Largest global river salinity database

### Classification Framework

**Venice System (1958)** - Salinity zones:
- Freshwater: <0.5 PSU
- Oligohaline: 0.5-5 PSU (Tidal Freshwater Zone)
- Mesohaline: 5-18 PSU
- Polyhaline: 18-30 PSU
- Euhaline: >30 PSU

**O'Connor et al. (2022)** - Tidal Freshwater Zone concept:
- River reaches with tidal influence but freshwater salinity
- Highly biogeochemically active
- Extent: 10-200 km from coast (discharge-dependent)

---

## ⚠️ Important Notes

### Data Coverage Limitations
- GlobSalt covers only 0.7-25% of river segments (region-dependent)
- ML pipeline (in `ml_salinity/`) fills gaps for unmeasured segments

### Performance
- GRIT processing requires 8-16 GB RAM
- Process takes 40-60 minutes for all regions
- Can run single regions with `--region` flag for testing

### Data Quality
- All scripts validate CRS (must be EPSG:4326)
- Duplicate segments are automatically removed
- Invalid geometries are fixed or filtered

---

## 🔗 Related Folders

- **ml_salinity/**: Uses processed GRIT data for ML classification
- **web_optimization/**: Converts processed data to web formats
- **diagnostics/**: Tools to inspect processed outputs

---

**See**: `scripts/README.md` for complete project documentation
