# 📜 Scripts Documentation — Project Aquarius

**Last Updated**: October 13, 2025  
**Purpose**: Complete guide to processing pipeline structure and execution

---

## 🎯 Quick Start

### One Command to Rule Them All:

```powershell
# Complete pipeline (3-4.5 hours, run overnight)
python scripts/master_pipeline.py --all
```

**That's it!** This runs everything from raw data to web-ready outputs.

---

## 📂 Folder Structure

```
scripts/
├── master_pipeline.py           # 🌟 MASTER ORCHESTRATOR (START HERE!)
├── README.md                    # This file
│
├── raw_data_processing/         # 📊 STAGE 1: Process raw datasets
│   ├── README.md                     # Detailed folder documentation
│   ├── process_grit_all_regions.py   # GRIT v0.6 (7 regions)
│   ├── process_durr.py               # Dürr 2011 estuaries
│   ├── process_baum.py               # Baum 2024 morphometry
│   └── process_globsalt_integrated.py # GlobSalt integration
│
├── ml_salinity/                 # 🤖 STAGE 2: Machine learning
│   ├── README.md                     # Detailed folder documentation
│   ├── ml_dynqual_master_pipeline.py # ML orchestrator
│   ├── ml_step1_extract_features.py  # Feature extraction
│   ├── add_dynqual_to_features.py    # DynQual integration
│   ├── ml_step2_train_model.py       # Train Random Forest
│   ├── ml_step3_predict.py           # Predict classifications
│   └── ml_step4_validate_improved.py # Multi-method validation
│
├── web_optimization/            # 🌐 STAGE 3: Web deployment
│   ├── README.md                     # Detailed folder documentation
│   ├── optimize_data_final.py        # Generate web GeoJSON
│   └── convert_gpkg_to_geojson.py    # Format conversion
│
├── diagnostics/                 # 🔧 Debugging tools (NOT in pipeline)
│   ├── README.md                     # Detailed folder documentation
│   ├── audit_raw_data.py             # Audit raw dataset schemas
│   ├── inspect_durr_data.py          # Inspect Dürr shapefile
│   ├── inspect_ml_predictions.py     # Inspect ML outputs
│   ├── inspect_validation_data.py    # Validation inspection
│   ├── check_features.py             # Check ML features
│   └── evaluate_dynqual_feasibility.py # Test DynQual
│
└── legacy/                      # 📦 Old/replaced scripts (archive)
    ├── README.md
    └── ... (historical files)
```

---

## 🎯 Folder Overview

### 📊 raw_data_processing/
**Purpose**: Convert raw external datasets to standardized GPKG format  
**Duration**: 60-90 minutes  
**Scripts**: 4 files  
**See**: `raw_data_processing/README.md` for detailed documentation

**Key scripts**:
- `process_grit_all_regions.py` - Process 20.5M river reaches (7 regions)
- `process_durr.py` - Process 7,057 estuary catchments
- `process_baum.py` - Process 106 large estuary measurements
- `process_globsalt_integrated.py` - Integrate 270K salinity stations

**Outputs**: `data/processed/*.gpkg` (full-resolution)

---

### 🤖 ml_salinity/
**Purpose**: ML-based salinity prediction for unmeasured segments  
**Duration**: 2-3 hours  
**Scripts**: 6 files (1 orchestrator + 5 steps)  
**See**: `ml_salinity/README.md` for detailed documentation

**Key script**: `ml_dynqual_master_pipeline.py` (runs entire ML workflow)

**What it does**:
1. Extract features (topology, distance, Dürr type)
2. Add DynQual physics-based predictions
3. Train Random Forest (spatial holdout validation)
4. Predict salinity for all segments
5. Multi-method validation

**Why**: GlobSalt covers only 0.7-25% of segments. ML fills the gaps.

**Outputs**: `data/processed/ml_classified/*.gpkg` + validation reports

---

### 🌐 web_optimization/
**Purpose**: Generate web-ready GeoJSON (<5MB each)  
**Duration**: 30 minutes  
**Scripts**: 2 files  
**See**: `web_optimization/README.md` for detailed documentation

**Key scripts**:
- `optimize_data_final.py` - Simplify geometries, filter attributes
- `convert_gpkg_to_geojson.py` - Batch GPKG → GeoJSON conversion

**Optimization**: Geometry simplification, attribute filtering, file splitting

**Outputs**: `data/web/*.geojson` (web-ready, <5MB each)

---

### 🔧 diagnostics/
**Purpose**: Debugging and inspection tools  
**Scripts**: 6 files  
**See**: `diagnostics/README.md` for detailed documentation

**NOT part of main pipeline!** Use only for troubleshooting.

---

### 📦 legacy/
**Purpose**: Archive of old/replaced scripts  
**DO NOT USE** - Kept for historical reference only

---

## 🚀 How to Run

### Method 1: Master Script (Recommended)

```powershell
# Complete pipeline (3-4.5 hours)
python scripts/master_pipeline.py --all
```

**What it does**:
1. Runs all scripts in correct order
2. Tracks progress (Stage 1/3, 2/3, 3/3)
3. Handles errors gracefully
4. Provides final summary

---

### Method 2: Stage-by-Stage

```powershell
# Stage 1: Raw Data Processing (60-90 min)
python scripts/master_pipeline.py --stage preprocessing

# Stage 2: Machine Learning (2-3 hours)
python scripts/master_pipeline.py --stage ml

# Stage 3: Web Optimization (30 min)
python scripts/master_pipeline.py --stage web
```

---

### Method 3: Individual Folders (For Development)

```powershell
# 1. Raw Data Processing
python scripts/raw_data_processing/process_grit_all_regions.py
python scripts/raw_data_processing/process_durr.py
python scripts/raw_data_processing/process_baum.py

# 2. Machine Learning (use orchestrator!)
python scripts/ml_salinity/ml_dynqual_master_pipeline.py --all-regions

# 3. Web Optimization
python scripts/web_optimization/optimize_data_final.py
python scripts/web_optimization/convert_gpkg_to_geojson.py
```

**Note**: See folder-specific README.md files for detailed options

---

## 📋 Detailed Documentation

Each folder has its own comprehensive README.md with:
- ✅ Script-by-script explanation
- ✅ Scientific rationale
- ✅ Usage examples
- ✅ Input/output specifications
- ✅ Common issues and solutions

**Read these for complete details:**

1. 📊 **`raw_data_processing/README.md`** - Data ingestion and standardization
2. 🤖 **`ml_salinity/README.md`** - Machine learning classification pipeline
3. 🌐 **`web_optimization/README.md`** - Web deployment optimization
4. 🔧 **`diagnostics/README.md`** - Debugging tools

---

## 🎯 Common Workflows

### First-Time Setup
```powershell
# Run complete pipeline (recommended)
python scripts/master_pipeline.py --all
```

### After Adding New Raw Data
```powershell
# Reprocess affected stages
python scripts/master_pipeline.py --stage preprocessing
python scripts/master_pipeline.py --stage ml
```

### Testing ML Changes
```powershell
# Test on single region first
python scripts/ml_salinity/ml_step1_extract_features.py --region SP
python scripts/ml_salinity/ml_step2_train_model.py
python scripts/ml_salinity/ml_step4_validate_improved.py --region SP
```

### Debugging Data Issues
```powershell
# Use diagnostic tools
python scripts/diagnostics/audit_raw_data.py
python scripts/diagnostics/inspect_durr_data.py
python scripts/diagnostics/inspect_ml_predictions.py --region SP
```

---

## 🌟 Quick Reference

### master_pipeline.py - Master Orchestrator
**Purpose**: Orchestrates complete pipeline (3 stages)  
**Duration**: 3-4.5 hours

**Options**:
```powershell
# Complete pipeline
python scripts/master_pipeline.py --all

# Individual stages
python scripts/master_pipeline.py --stage preprocessing  # 60-90 min
python scripts/master_pipeline.py --stage ml             # 2-3 hours
python scripts/master_pipeline.py --stage web            # 30 min

# Skip specific steps
python scripts/master_pipeline.py --all --skip-grit
python scripts/master_pipeline.py --all --skip-training
```

---

## 📊 Output Files Structure

```
data/processed/
├── rivers_grit_segments_classified_*.gpkg      # GRIT (7 regions)
├── durr_estuaries.geojson                      # Dürr catchments
├── baum_morphometry.geojson                    # Baum estuaries
├── ml_features/features_*.parquet              # ML features
├── ml_models/salinity_classifier_rf.pkl        # Trained model
├── ml_classified/rivers_grit_ml_classified_*.gpkg  # Final results
└── validation_improved/*.csv                   # Validation reports

data/web/
└── *.geojson                                   # Web-ready (<5MB)
```

---

## ⚠️ Key Points to Remember

### Spatial Holdout (Critical!)
- SP region is **NEVER** used in training
- Only SP provides true independent validation
- Expected accuracy: 72-78% on SP (honest assessment)

### Data Quality
- DynQual: Sanitize values >45 PSU (NetCDF fill values)
- Dürr FIN_TYP: Integer type, not strings
- GlobSalt: Covers only 0.7-25% of segments (ML fills gaps)

### System Requirements
- RAM: 16+ GB recommended
- Storage: 10+ GB for processed files
- Duration: 3-4.5 hours (complete pipeline)

---

## 🆘 Troubleshooting

### Issue: "File not found"
```powershell
python scripts/diagnostics/audit_raw_data.py  # Check raw data structure
```

### Issue: ML shows 100% accuracy
**Problem**: Data leakage!  
**Solution**: Check `holdout_region.txt` = SP, validation uses `model.predict()`

### Issue: Out of memory
**Solution**: Process regions one at a time or close other applications

### Issue: Scripts not found after reorganization
**Problem**: Old paths in custom scripts  
**Solution**: Update to use new folder structure:
- `scripts/process_grit_all_regions.py` → `scripts/raw_data_processing/process_grit_all_regions.py`
- `scripts/ml_step1_extract_features.py` → `scripts/ml_salinity/ml_step1_extract_features.py`
- etc.

---

## 📖 Related Documentation

- **Folder READMEs**: Detailed documentation for each script group
  - `raw_data_processing/README.md`
  - `ml_salinity/README.md`
  - `web_optimization/README.md`
  - `diagnostics/README.md`

- **Project Documentation**:
  - `README.md` - Project overview
  - `docs/METHODOLOGY.md` - Scientific methods
  - `docs/TECHNICAL.md` - Technical specifications
  - `docs/OVERNIGHT_RUN_GUIDE.md` - ML pipeline guide
  - `.github/copilot-instructions.md` - Project memory bank

---

## 🎓 For AI Copilot Agents

When writing new Python scripts:

1. **Save to correct folder**:
   - Raw data processing → `scripts/raw_data_processing/`
   - ML classification → `scripts/ml_salinity/`
   - Web optimization → `scripts/web_optimization/`
   - Debugging tools → `scripts/diagnostics/`

2. **Update documentation**:
   - Add script description to folder README.md
   - Update `master_pipeline.py` if part of main workflow

3. **Follow naming conventions**:
   - Processing: `process_<dataset>.py`
   - ML steps: `ml_step<number>_<action>.py`
   - Diagnostics: `inspect_<target>.py` or `check_<target>.py`

---

**Questions?** Read folder-specific README.md files for complete details!

---

**That's it!** Clean, organized, and well-documented. 🎉
