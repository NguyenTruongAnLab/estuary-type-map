# 🤖 AI Agent Instructions — Project: Global Water Body Surface Area Atlas

## 🎯 Ultimate Project Objectives

1. **Create the comprehensive, polygon-based global water body surface area atlas**
2. **Calculate a bit more precise surface areas** for all aquatic system types (rivers, estuaries, lakes, wetlands)
3. **Enable next-generation biogeochemical modeling:** GHG emissions, carbon fluxes, nutrient budgets
4. **Use open-access datasets** with complete provenance
5. **Implement O'Connor et al. (2022) Tidal Freshwater Zone framework** globally
6. **Move beyond extrapolation methods:** Direct polygon measurement, not statistical estimation
7. **Maintain full transparency and reproducibility** - all code, data, methods open-source

---

## 📂 Project Structure

project-aquarius/
├── data/
│   ├── raw/                    # Original source data (not in repo if >100MB)
│   │   ├── OSM-Water-Layer-Yamazaki_2021/
│   │   ├── hydrosheds/         # HydroBASINS, HydroRIVERS, HydroATLAS
│   │   ├── GlobSalt/           # Salinity grids (1980-2023)
│   │   ├── Worldwide-typology-Shapefile-Durr_2011/
│   │   ├── Large-estuaries-Baum_2024/
│   │   └── GCC-Panagiotis-Athanasiou_2024/
│   ├── processed/              # Intermediate .gpkg files (full resolution)
│   ├── web/                    # Web-ready GeoJSON (<5MB each, zoom-optimized)
│   └── optimized/              # Legacy formats
├── scripts/                    # Organized processing pipeline
│   ├── master_pipeline.py           # 🌟 MASTER ORCHESTRATOR
│   ├── raw_data_processing/         # Data ingestion (GRIT, Dürr, Baum)
│   ├── ml_salinity/                 # ML classification pipeline
│   ├── web_optimization/            # Web-ready GeoJSON generation
│   ├── diagnostics/                 # Debugging tools
│   └── legacy/                      # Archived scripts
├── map/ (or js/)               # Interactive web application
│   ├── index.html
│   ├── css/style.css
│   └── js/map.js, filters.js, charts.js
├── docs/                       # Comprehensive documentation
│   ├── ROADMAP.md              # Task tracking (DYNAMIC)
│   ├── TECHNICAL.md            # Data schemas & processing details
│   ├── USER_GUIDE_COMPLETE.md
│   └── VISUALIZATION_MODES.md
├── .github/
│   ├── workflows/deploy.yml    # GitHub Actions CI/CD
│   └── copilot-instructions.md # This file
├── index.html                  # Main entry point
└── README.md                   # Complete project documentation

See README.md for full structure details and scientific background.

---

## 🔴 MANDATORY RULES — Always Follow

### Rule 0: Complete Implementation & Testing Protocol
Every request MUST include:
3. ✅ Test in browser: http://localhost:8000
4. ✅ Check console (F12): ZERO errors required
5. ✅ Test ALL modes: Basins, Coastline, Rivers
8. ✅ Update docs/ROADMAP.md: Mark tasks complete
9. ✅ Clean up: Remove ALL temporary/test files

### Rule 1: Data Integrity  
✅ Use ONLY real, peer-reviewed, open-access datasets
❌ NEVER use fake/sample data

### Rule 2: Code Quality
✅ Defensive code with existence checks
✅ Inline comments for complex logic
✅ Handle errors gracefully

### Rule 3: File Management
✅ Keep web files <5MB (compress if needed)
✅ Store large files (>100MB) externally  
✅ Add large files to .gitignore
❌ NEVER commit files >100MB

### Rule 4: Clean Project Hygiene
✅ Remove ALL temporary files after testing
✅ Remove ALL test/demo code
✅ Keep ONLY final, peer-review-ready results
❌ NEVER leave *_test.*, *_demo.*, *_temp.* files
❌ NEVER commit testing artifacts or backup files

### Rule 5: Script Organization — Where to Save New Files

✅ **ALWAYS save new Python scripts to the correct folder:**

- **Raw data processing** → `scripts/raw_data_processing/`
  - Processing external datasets (GRIT, Dürr, Baum, GlobSalt, etc.)
  - Converting formats (PBF → GPKG, NetCDF → GeoJSON)
  - Naming: `process_<dataset>.py`

- **ML classification** → `scripts/ml_salinity/`
  - Feature extraction, model training, prediction, validation
  - Anything related to salinity prediction pipeline
  - Naming: `ml_step<number>_<action>.py` or `add_<feature>_to_features.py`

- **Web optimization** → `scripts/web_optimization/`
  - Geometry simplification, attribute filtering
  - GeoJSON generation for web deployment
  - Naming: `optimize_*.py` or `convert_*.py`

- **Debugging tools** → `scripts/diagnostics/`
  - Inspection, auditing, checking data quality
  - NOT part of main pipeline
  - Naming: `inspect_*.py`, `check_*.py`, `audit_*.py`

- **Archive only** → `scripts/legacy/`
  - Old/replaced scripts (DO NOT add new files here!)

❌ **NEVER save scripts to root `scripts/` folder** (except `master_pipeline.py`)

✅ **Update documentation after creating new scripts:**
1. Add description to folder's README.md
2. Update `master_pipeline.py` if part of main workflow
3. Update `.github/copilot-instructions.md` if significant addition

### Rule 6: Performance Targets
- Initial page load: <5 seconds (3G connection)
- User interaction: <100ms response
- Memory usage: <500MB total
- File sizes: <5MB per GeoJSON

### Rule 7: Documentation Standards — Academic & Peer-Review Focus

**CRITICAL**: Documentation is for scientific understanding, NOT troubleshooting logs!

#### ✅ ALWAYS Do:
- Update README.md for scientific methodology changes
- Update docs/TECHNICAL.md for data schemas, algorithms, processing pipelines
- Update docs/ROADMAP.md ONLY for task status tracking
- Write documentation for PEER REVIEWERS and FUTURE RESEARCHERS
- Focus on: WHY methods were chosen, HOW they work scientifically, WHAT data flows exist
- Document relationships between script groups and project objectives
- Explain scientific rationale behind code decisions

#### ❌ NEVER Do:
- Create "fix summary" or "bug resolution" documents (explain fixes in chat only!)
- Create "validation error fixed" or "data leakage fixed" docs (troubleshooting ≠ documentation!)
- Document AI agent conversations or implementation details
- Write verbose testing logs or debug session summaries
- Create temporary summary files about "what we accomplished today"
- Duplicate information across multiple markdown files
- Write documentation about the documentation process

#### 📋 Approved Document Types ONLY:
1. **README.md** - Project overview, scientific objectives, dataset descriptions
2. **docs/TECHNICAL.md** - Data schemas, processing algorithms, file formats, API specifications
3. **docs/ROADMAP.md** - Task status tracking (DYNAMIC, minimal text)
4. **docs/METHODOLOGY.md** - Scientific methods, classification frameworks, validation approaches
5. **docs/*_GUIDE.md** - User guides for specific workflows (overnight runs, data integration)
6. **scripts/README_*.md** - Script group explanations (purpose, relationships, usage)

#### 🎯 Documentation Purpose Hierarchy:
**Primary Audience**: Peer reviewers, collaborating scientists, future researchers
**Secondary Audience**: Users replicating the analysis or using the atlas
**NOT for**: Debugging logs, AI agent interaction history, implementation troubleshooting

#### 📚 When to Create New Documentation:
- New scientific method implemented → Update METHODOLOGY.md
- New dataset integrated → Update TECHNICAL.md (schema) + README.md (description)
- New script group created → Create scripts/README_[GROUP].md explaining purpose
- Processing pipeline changed → Update TECHNICAL.md (workflow diagram)
- Classification framework refined → Update METHODOLOGY.md (scientific rationale)

**Golden Rule**: If you're documenting "how we fixed X", explain it in CHAT, not in a new .md file!

---

## 🧠 PROJECT MEMORY BANK — Critical Context for AI Agents

### 🎯 Core Scientific Problem
**Challenge**: Existing global water body atlases use statistical extrapolation, not direct measurement  
**Impact**: Biogeochemical models have 30-50% uncertainty in GHG emissions from aquatic systems  
**Solution**: Direct polygon-based measurement of ALL global water bodies using modern high-resolution datasets

### 📊 Current Project Status (October 2025)

**Completed Components**:
1. ✅ GRIT v0.6 integration (20.5M river reaches, 7 regions)
2. ✅ GlobSalt v2.0 integration (270K stations, salinity-based classification)
3. ✅ Dürr 2011 estuary typology (7,057 catchments)
4. ✅ Baum 2024 morphometry (large estuaries)
5. ✅ Hybrid classification framework (GlobSalt → Dürr → Distance → Fallback)
6. ✅ ML classification pipeline with spatial holdout validation

**Active Development**:
- 🔄 Machine learning salinity prediction for segments without GlobSalt coverage
- 🔄 DynQual (Jones 2023) ensemble features evaluation
- 🔄 Multi-method validation framework (5 independent methods)

**Known Limitations**:
- GlobSalt covers only 0.7-25% of river segments (region-dependent)
- DynQual has 10 km resolution (coarse for small tributaries)
- Tidal extent estimation relies on literature proxies (not direct measurement)

### 🗂️ Script Architecture & Relationships

#### **scripts/raw_data_processing/** - Data Ingestion
**Purpose**: Convert raw datasets to standardized GPKG format  
**Files**: 4 scripts  
- `process_grit_all_regions.py` - Process 20.5M river reaches (7 regions)
- `process_durr.py` - Process 7,057 estuary catchments
- `process_baum.py` - Process 106 large estuary measurements
- `process_globsalt_integrated.py` - Integrate 270K salinity stations

**Output**: `data/processed/*.gpkg` (full-resolution)  
**Why**: Unified schema from diverse formats (PBF, SHP, CSV, NetCDF)

#### **scripts/ml_salinity/** - Machine Learning Classification
**Purpose**: Predict salinity for segments without GlobSalt measurements  
**Scientific Rationale**: GlobSalt covers only 0.7-25%; ML fills gaps using topology + hydrology  
**Files**: 6 scripts (1 orchestrator + 5 steps)
- `ml_dynqual_master_pipeline.py` - **Orchestrator for entire ML workflow**
- `ml_step1_extract_features.py` - Extract predictors
- `add_dynqual_to_features.py` - Add DynQual physics-based features
- `ml_step2_train_model.py` - Train Random Forest (spatial holdout)
- `ml_step3_predict.py` - Predict for all segments
- `ml_step4_validate_improved.py` - Multi-method validation

**Critical Design**: SP region excluded from training (prevents data leakage)  
**Expected Performance**: 72-78% on true holdout (honest, publishable)

#### **scripts/web_optimization/** - Web Deployment
**Purpose**: Generate web-ready GeoJSON (<5MB per file)  
**Files**: 2 scripts
- `optimize_data_final.py` - Simplify geometries, filter attributes
- `convert_gpkg_to_geojson.py` - Batch GPKG → GeoJSON

**Output**: `data/web/*.geojson` (<5MB each for GitHub Pages)  
**Why**: Fast loading (GPKG files are 1-5 GB, too large for web)

#### **scripts/diagnostics/** - Debugging Tools
**Purpose**: Inspection and troubleshooting (NOT in main pipeline)  
**Files**: 6 scripts
- `audit_raw_data.py` - Audit raw dataset schemas
- `inspect_*.py` - Inspect processed outputs
- `check_*.py` - Verify data quality
- `evaluate_dynqual_feasibility.py` - Test DynQual integration

**Why**: Debugging separate from production pipeline

### 🔬 Key Scientific Frameworks

#### Venice System (1958) - Salinity Classification
```
Freshwater:   <0.5 PSU   (inland rivers, lakes)
Oligohaline:  0.5-5 PSU  (tidal freshwater zone - TFZ)
Mesohaline:   5-18 PSU   (upper estuary)
Polyhaline:   18-30 PSU  (lower estuary)
Euhaline:     >30 PSU    (marine)
```
**Biogeochemical Significance**: Each zone has distinct metabolic processes (CO₂ outgassing, CH₄ oxidation, N₂O production)

#### O'Connor et al. (2022) - Tidal Freshwater Zone (TFZ)
**Definition**: River reaches with tidal influence but freshwater salinity (<0.5 PSU)  
**Importance**: Highly biogeochemically active; often misclassified in global models  
**Extent**: 10-200 km from coast (discharge-dependent)

#### Dürr et al. (2011) - Estuary Geomorphology
**7 Types**: Delta, Fjord, Lagoon, Coastal Plain, Karst, Archipelagic, Small Deltas  
**Why Geomorphology Matters**: Controls mixing, residence time, nutrient processing

### 🚨 Common Pitfalls to Avoid

1. **GRIT `is_coastal` attribute ≠ estuarine**  
   - 89% of river networks flagged as coastal (includes inland rivers near coast)
   - Use distance to ocean + salinity instead

2. **DynQual resolution limitations**  
   - 10 km grid cannot resolve small tributaries
   - Sanitize impossible values (e.g., 21,606 PSU from NetCDF fill values)

3. **Data leakage in validation**  
   - Training and validation regions MUST be spatially independent
   - Never compare pre-assigned labels to recalculated labels from same source

4. **Dürr catchments ≠ salinity extent**  
   - A "Delta" catchment is 99% freshwater inland
   - Only coastal portions (<50 km) are estuarine

### 🎓 Programming Style Guide

**Defensive Coding**:
```python
# ✅ GOOD: Check existence before using
if 'column_name' in df.columns:
    df['new_col'] = df['column_name'] * 2

# ❌ BAD: Assume column exists
df['new_col'] = df['column_name'] * 2  # Crashes if missing!
```

**Data Type Verification**:
```python
# ✅ GOOD: Inspect actual data structure
print(df['FIN_TYP'].dtype)  # Might be int32, not string!

# ❌ BAD: Assume data types
for estuary_type in df['FIN_TYP']:  # Crashes if int!
    print(f"{estuary_type:20s}")
```

**Scientific Transparency**:
```python
# ✅ GOOD: Document assumptions
# Using 45 PSU as max plausible (Dead Sea is 34 PSU)
MAX_SALINITY_PSU = 45.0

# ❌ BAD: Magic numbers
if salinity > 45:  # Why 45? Not documented!
```

---

## 🔬 Scientific Standards

Approved Data Sources:
1. **Dürr et al. (2011)** - DOI: 10.1007/s12237-011-9381-y (PRIMARY - Estuary typology)
2. **Yamazaki OSM Water Layer (2018)** - DOI: 10.1002/2017GL072874 (PRIMARY - Water polygons)
3. **HydroSHEDS** - DOI: 10.5067/9SQ1S6VFQQ20 (PRIMARY - Basins & rivers) ✅ PROCESSED
4. **GlobSalt** - Monthly salinity grids 1980-2023 (PRIMARY - Zone boundaries) ✅ PROCESSED
5. **Baum et al. (2024)** - Large structural estuaries (VALIDATION) ✅ PROCESSED
6. **Athanasiou et al. (2024)** - DOI: 10.5281/zenodo.8200199 (OPTIONAL - Coastal characteristics)
7. **O'Connor et al. (2022)** - DOI: 10.1016/j.ecss.2022.107786 (FRAMEWORK - TFZ definition)
8. **Laruelle et al. (2025)** - DOI: 10.1007/s12237-024-01463-3 (VALIDATION ONLY - never raw data source)

---

## ⚡ Performance Optimization

Point features (6K+ markers): MUST use leaflet.markercluster
Polygon features (6K+ basins): Multi-resolution versions, zoom-based loading
Data loading: Lazy load by mode, gzip compression, CDN libraries

---

## 🎯 Workflow for Every Request

1. Understand: Read README.md and docs/ROADMAP.md
2. Plan: Check existing code, avoid duplication
3. Implement: Clean, commented, defensive code
5. Test: Start server, test in browser, check console
6. Profile: Verify performance targets met
7. Clean: Remove ALL temporary and test files
8. Document: Update README.md and ROADMAP.md
9. Commit: Only final, peer-review-ready code


## 📚 Reference Documents

- README.md - Complete project documentation
- docs/TECHNICAL.md - Data schemas and API
- docs/ROADMAP.md - Current status and priorities (DYNAMIC)