# 🤖 Machine Learning Salinity Classification

**Purpose**: ML-based salinity prediction for river segments without GlobSalt measurements

---

## 🎯 What This Folder Does

GlobSalt provides salinity measurements for only 0.7-25% of global river segments. This folder contains the **complete ML pipeline** to predict salinity for the remaining 75-99.3% using:
- Topological features (stream order, distance to coast)
- Hydrological context (Dürr catchment, drainage area)
- Physics-based model outputs (DynQual)

---

## 📁 Scripts in This Folder

### 🌟 ml_dynqual_master_pipeline.py
**Purpose**: Orchestrator for complete 5-step ML workflow  
**Duration**: 2-3 hours (all regions)  
**Usage**: `python scripts/ml_salinity/ml_dynqual_master_pipeline.py --all-regions`

**What it does**:
1. Calls ml_step1_extract_features.py
2. Calls add_dynqual_to_features.py
3. Calls ml_step2_train_model.py
4. Calls ml_step3_predict.py
5. Calls ml_step4_validate_improved.py

**This is the ONE script to run for ML!** It handles the entire workflow automatically.


## 📊 Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Feature Extraction                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   GRIT       │  │  HydroSHEDS  │  │  Dürr 2011   │         │
│  │  (Topology)  │  │  (Discharge) │  │  (Estuaries) │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                  │
│                            │                                      │
│                    15+ Features per segment                       │
│                            │                                      │
└────────────────────────────┼──────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Model Training                                         │
│  ┌─────────────────────────────────────────────────────┐       │
│  │  Training Data: GlobSalt-validated segments         │       │
│  │  • Europe: 35K segments (15% of region)             │       │
│  │  • Asia: 40K segments (10%)                          │       │
│  │  • North America: 25K (12%)                          │       │
│  │  • Other regions: 15K (2-5%)                         │       │
│  │  Total: ~115,000 training samples                   │       │
│  └────────────────────┬────────────────────────────────┘       │
│                       │                                          │
│                       ▼                                          │
│  ┌────────────────────────────────────────────────┐            │
│  │  Random Forest Classifier                      │            │
│  │  • 200 trees, balanced class weights           │            │
│  │  • 5-fold cross-validation                     │            │
│  │  • Hyperparameter tuning (Grid Search)         │            │
│  │  • Expected accuracy: 75-85%                   │            │
│  └────────────────────┬───────────────────────────┘            │
└────────────────────────┼──────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Prediction                                             │
│  ┌──────────────────────────────────────────────────┐          │
│  │  For each unclassified segment:                  │          │
│  │  1. Extract 15+ features                         │          │
│  │  2. Predict salinity class (5 classes)           │          │
│  │  3. Assign confidence based on probability:      │          │
│  │     • >85% prob → MEDIUM-HIGH confidence         │          │
│  │     • 70-85% → MEDIUM confidence                 │          │
│  │     • 55-70% → LOW confidence                    │          │
│  │     • <55% → VERY-LOW confidence                 │          │
│  └──────────────────────┬───────────────────────────┘          │
└────────────────────────┼──────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Validation                                             │
│  ┌──────────────────────────────────────────────────┐          │
│  │  Cross-validate with Dürr 2011:                  │          │
│  │  • Spatial join with 7,057 expert estuaries      │          │
│  │  • Check: Are Dürr estuaries predicted estuarine?│          │
│  │  • Calculate agreement rate                      │          │
│  │  • Expected: 70-80% agreement                    │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

### 1. ml_step1_extract_features.py
**Purpose**: Extract predictor features from GRIT, Dürr, and GCC  
**Duration**: 45-60 minutes  
**Input**: `data/processed/rivers_grit_segments_classified_*.gpkg`  
**Output**: `data/processed/ml_features/features_*.parquet` (7 files)

**Features extracted**:
- **Topology**: strahler_order, is_mainstem, bifurcation_balance
- **Distance**: dist_to_coast_km, dist_to_outlet_km
- **Dürr**: is_in_durr_catchment, durr_estuary_type
- **Hydrology**: drainage_area_in, drainage_area_out
- **GlobSalt**: salinity_mean_psu, has_salinity (for training labels)

**Scientific rationale**: Literature (O'Connor 2022, Savenije 2012) shows tidal extent correlates with stream order, distance, and discharge. These features capture those patterns.

**Usage**:
```powershell
# All regions
python scripts/ml_salinity/ml_step1_extract_features.py --all-regions

# Single region (testing)
python scripts/ml_salinity/ml_step1_extract_features.py --region SP
```

---

### 2. add_dynqual_to_features.py
**Purpose**: Add DynQual physics-based model predictions as ensemble features  
**Duration**: 30-45 minutes  
**Input**: ML features + `data/raw/DynQual-Jones_2023/*.nc`  
**Output**: Updated feature files with DynQual columns

**Features added**:
- `dynqual_salinity_psu`: TDS-derived salinity (10 km resolution)
- `dynqual_discharge_m3s`: Modeled river discharge
- `dynqual_temperature_C`: Modeled water temperature
- Derived: `log_dynqual_salinity`, `salinity_x_distance` (interaction terms)

**Scientific rationale**: DynQual (Jones 2023) provides independent physics-based estimates from a hydrological model. Adding as ensemble features tests if it improves ML accuracy beyond topology alone.

**Critical feature**: Data sanitization removes impossible values (>45 PSU) from NetCDF fill values.

**Usage**:
```powershell
python scripts/ml_salinity/add_dynqual_to_features.py --all-regions
```

---

### 3. ml_step2_train_model.py
**Purpose**: Train Random Forest classifier on GlobSalt-validated segments  
**Duration**: 20-30 minutes  
**Input**: Features from 6 regions (AF, AS, EU, NA, SA, SI)  
**Output**: `data/processed/ml_models/salinity_classifier_rf.pkl` + metadata

**Model configuration**:
- Algorithm: Random Forest (200 trees, max_depth=15)
- Training: 6 regions (SP held out for independent validation)
- Classes: Freshwater, Oligohaline, Mesohaline
- Validation: 5-fold cross-validation + spatial holdout

**Why spatial holdout**: Prevents data leakage. The model must generalize to entirely unseen geographic regions (not just unseen segments within training regions).

**Expected performance**:
- Cross-validation: 85-88% (on training regions)
- True holdout (SP): 72-78% (honest independent assessment)

**Usage**:
```powershell
python scripts/ml_salinity/ml_step2_train_model.py
```

**Key output files**:
- `salinity_classifier_rf.pkl`: Trained model
- `label_encoder.pkl`: Class encoder
- `feature_columns.txt`: Feature names
- `feature_importance.csv`: Feature rankings
- `holdout_region.txt`: Spatial holdout config (SP)

---

### 4. ml_step3_predict.py
**Purpose**: Predict salinity class for all segments (validated + unvalidated)  
**Duration**: 10-15 minutes  
**Input**: Trained model + features for all 7 regions  
**Output**: `data/processed/ml_classified/rivers_grit_ml_classified_*.gpkg`

**Prediction logic**:
- Segments with GlobSalt: Use measured salinity (HIGH confidence, `classification_method=GlobSalt_Validated`)
- Segments without GlobSalt: Use ML prediction (confidence from model probability)

**Confidence levels**:
- HIGH: >80% prediction probability or GlobSalt validation
- MEDIUM: 60-80% probability
- LOW: <60% probability

**Usage**:
```powershell
# All regions
python scripts/ml_salinity/ml_step3_predict.py --all-regions

# Single region
python scripts/ml_salinity/ml_step3_predict.py --region SP
```

**Output schema**:
- `salinity_class_final`: Predicted/measured class
- `classification_method`: GlobSalt_Validated / ML_Predicted
- `confidence_level`: HIGH / MEDIUM / LOW
- `prediction_probability`: Model confidence (0-1)

---

### 5. ml_step4_validate_improved.py
**Purpose**: Multi-method independent validation of ML predictions  
**Duration**: 5-10 minutes  
**Input**: ML predictions + validation datasets (Dürr, GlobSalt holdout)  
**Output**: `data/processed/validation_improved/*.csv` (validation reports)

**Validation methods**:
1. **GlobSalt Spatial Holdout** (GOLD STANDARD): 
   - Runs actual `model.predict()` on SP region features
   - Compares to GlobSalt measurements (never seen in training)
   - Expected: 72-78% accuracy (honest assessment)

2. **Distance-Stratified Analysis**: 
   - Tests if predictions follow distance-decay patterns
   - Expected: Oligohaline <50 km, Freshwater >100 km

3. **Literature Tidal Extents**: 
   - Compares to 35+ published estuary systems
   - Tests if TFZ extent matches field observations

4. **Discharge Proxy**: 
   - Tests Savenije 2012 empirical formula
   - Validates salinity-discharge relationships

5. **Dürr Patterns** (EXPLORATORY): 
   - Checks if geomorphology correlates with salinity
   - Not primary validation (Dürr doesn't measure salinity directly)

**Why multiple methods**: No single validation is perfect. Convergence across independent methods builds confidence.

**Usage**:
```powershell
# All regions (but only SP validates - others were in training!)
python scripts/ml_salinity/ml_step4_validate_improved.py --all-regions

# Just SP (true holdout)
python scripts/ml_salinity/ml_step4_validate_improved.py --region SP
```

**Key validation files**:
- `globsalt_holdout_sp.csv`: Detailed holdout validation results
- `distance_stratified_sp.csv`: Distance-based validation
- `validation_summary.csv`: Aggregated results across all methods

---

## 🔄 Execution Order

Run in this sequence (or use `ml_dynqual_master_pipeline.py`):

```
1. ml_step1_extract_features.py (all regions)
   ↓
2. add_dynqual_to_features.py (all regions)
   ↓
3. ml_step2_train_model.py (trains on 6 regions, excludes SP)
   ↓
4. ml_step3_predict.py (all regions)
   ↓
5. ml_step4_validate_improved.py (validates on SP only)
```

---

## 📊 Output Files

```
data/processed/
├── ml_features/
│   ├── features_af.parquet        # Feature matrix (Africa)
│   ├── features_as.parquet        # (Asia)
│   ├── ... (7 regions total)
│
├── ml_models/
│   ├── salinity_classifier_rf.pkl # Trained Random Forest
│   ├── label_encoder.pkl          # Class encoder
│   ├── feature_columns.txt        # Feature names
│   ├── feature_importance.csv     # Feature rankings
│   └── holdout_region.txt         # Spatial holdout (SP)
│
├── ml_classified/
│   ├── rivers_grit_ml_classified_af.gpkg  # Final classified segments
│   ├── rivers_grit_ml_classified_as.gpkg
│   ├── ... (7 regions)
│
└── validation_improved/
    ├── globsalt_holdout_sp.csv    # Gold standard validation
    ├── distance_stratified_*.csv  # Distance-based validation
    └── validation_summary.csv     # Aggregated results
```

---

## 🔬 Scientific Context

### Why Machine Learning?

**Problem**: GlobSalt provides direct salinity measurements for only 0.7-25% of segments  
**Solution**: ML learns patterns from topology and hydrology to predict salinity for unmeasured segments

**Alternative approaches rejected**:
- ❌ Distance-only: Oversimplified (ignores discharge, morphology)
- ❌ Simple rules: Can't capture non-linear interactions
- ❌ Physics models alone: DynQual has 10 km resolution (too coarse)

**Why Random Forest**:
- ✅ Handles non-linear relationships (e.g., discharge × distance)
- ✅ Robust to missing data (median imputation)
- ✅ Interpretable feature importance
- ✅ No hyperparameter tuning needed (good defaults)

### Spatial Holdout Strategy

**CRITICAL DESIGN DECISION**: SP region excluded from training

**Why this matters**:
- **Wrong**: Train on all regions, validate on random 20% segments → 100% accuracy (data leakage!)
- **Correct**: Train on 6 regions, validate on entire 7th region → 74% accuracy (honest!)

The model must generalize to **unseen geographic regions**, not just unseen segments. This is a much harder test and provides honest performance estimates.

### Expected Performance

**Cross-validation (training regions)**: 85-88%
- Model sees these regions during training
- Optimistic estimate

**Spatial holdout (SP region)**: 72-78%
- Model never sees SP during training
- Honest, publication-ready estimate
- **This is what you report in papers!**

**Why not 100%**:
- Minority classes (Oligohaline) are hard to predict
- GlobSalt has measurement uncertainty
- Tidal extent is dynamic (varies seasonally)
- 74% is excellent for 3-class problem with class imbalance!

---

## 🚨 Common Issues

### Issue: 100% validation accuracy
**Problem**: Data leakage - comparing pre-assigned labels to same labels  
**Fix**: Validation now uses `model.predict()` on actual features  
**Check**: Only SP region should validate (others were in training)

### Issue: DynQual shows impossible salinity values
**Problem**: NetCDF fill values (21,606 PSU!) not sanitized  
**Fix**: `add_dynqual_to_features.py` now caps at 45 PSU  
**Check**: Max salinity should be <45 PSU in feature files

### Issue: Out of memory
**Solution**: Process regions one at a time:
```powershell
python scripts/ml_salinity/ml_step1_extract_features.py --region AF
python scripts/ml_salinity/ml_step1_extract_features.py --region AS
# ... repeat for each region
```

---

## 🔗 Related Folders

- **raw_data_processing/**: Provides GRIT input data
- **diagnostics/**: Tools to inspect features and predictions
- **web_optimization/**: Uses ML-classified segments for web outputs

---

## 📖 Key Documentation

- **docs/OVERNIGHT_RUN_GUIDE.md**: Detailed ML pipeline options
- **docs/HYBRID_CLASSIFICATION_SOLUTION.md**: Classification hierarchy
- **copilot-instructions.md**: Project memory bank (ML section)

---

**Quick Start**: `python scripts/ml_salinity/ml_dynqual_master_pipeline.py --all-regions`
