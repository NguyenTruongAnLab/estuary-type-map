# 🚀 How to Run the Complete ML Pipeline

**Date**: October 13, 2025  
**Status**: ✅ Ready to run with GCC features!

---

## ✅ **ANSWER: Yes, Just Run One Script!**

```bash
python scripts/ml_salinity/ml_dynqual_master_pipeline.py --all-regions
```

**That's it!** This single script runs all 6 steps automatically.

---

## 📊 **What This Script Does** (1-2 hours total)

### **Step 1: Extract Baseline Features** (45-60 min)
- Loads GRIT segments
- Extracts topology (23 features)
- Adds Dürr estuary types
- Loads GlobSalt measurements (ground truth)
- **Output**: `features_{region}.parquet` (23 columns)

### **Step 2: Add DynQual Features** (30-45 min)
- Loads DynQual NetCDF files
- Extracts discharge, salinity, temperature
- Adds 8 features + interaction terms
- **Output**: Updates feature files (31 columns)

### **Step 3: Add GCC Features** (<1 min!) ⭐ **NEW!**
- Loads GCC coastal transects (728K points)
- Spatial matching to GRIT segments
- Adds 32 features (tidal range!, waves, slopes, land cover)
- **Output**: Updates feature files (60+ columns)

### **Step 4: Train Model** (20-30 min)
- Loads 6 regions (AF, AS, EU, NA, SA, SI)
- Holdout: SP (never used in training!)
- Hyperparameter tuning (24 combinations)
- **Output**: Trained model + feature importance

### **Step 5: Predict** (10-15 min)
- Applies model to all 7 regions
- Adds confidence levels
- **Output**: Classified segments (`.gpkg` files)

### **Step 6: Validate** (5-10 min)
- Multiple validation methods
- GlobSalt holdout (primary)
- Distance patterns
- **Output**: Validation reports

---

## 🎯 **Key Updates from GCC Integration**

### **Before**:
```bash
# Old pipeline (WITHOUT GCC)
python scripts/ml_dynqual_master_pipeline.py --all-regions

Features: 23 (baseline) + 8 (DynQual) = 31 total
Problem: No tidal range → Overestimates estuarine extent (69% @ 0-20km!)
```

### **After** (Current):
```bash
# NEW pipeline (WITH GCC) ⭐
python scripts/ml_dynqual_master_pipeline.py --all-regions

Features: 23 (baseline) + 8 (DynQual) + 32 (GCC) = 63 total
Solution: Tidal range included → Realistic extent (40-50% @ 0-20km!)
```

---

## 📋 **Command Options**

### **Full Pipeline** (Recommended):
```bash
python scripts/ml_dynqual_master_pipeline.py --all-regions
```

### **Test on Single Region**:
```bash
python scripts/ml_dynqual_master_pipeline.py --region SP
```

### **Skip Completed Steps**:
```bash
# If you already have features
python scripts/ml_dynqual_master_pipeline.py --all-regions --skip-baseline --skip-dynqual --skip-gcc

# If you already have trained model
python scripts/ml_dynqual_master_pipeline.py --all-regions --skip-training

# Just run validation
python scripts/ml_dynqual_master_pipeline.py --all-regions --skip-baseline --skip-dynqual --skip-gcc --skip-training --skip-prediction
```

---

## ⏰ **Expected Timeline**

| Step | Duration | Output |
|------|----------|--------|
| 1. Baseline features | 45-60 min | features_*.parquet (23 cols) |
| 2. DynQual features | 30-45 min | Updated (31 cols) |
| 3. GCC features ⭐ | **<1 min!** | Updated (60+ cols) |
| 4. Train model | 20-30 min | random_forest_model.pkl |
| 5. Predict | 10-15 min | rivers_grit_ml_classified_*.gpkg |
| 6. Validate | 5-10 min | Validation reports |
| **TOTAL** | **1-2 hours** | Complete classification! |

---

## ✅ **What to Check After Completion**

### **1. Feature Files** (`data/processed/ml_features/`)
```bash
# Check feature count
python -c "import pandas as pd; df = pd.read_parquet('data/processed/ml_features/features_sp.parquet'); print(f'Features: {len(df.columns)}'); gcc_features = [c for c in df.columns if c.startswith('gcc_')]; print(f'GCC features: {len(gcc_features)}')"

# Expected output:
Features: 60
GCC features: 32
```

### **2. Model Files** (`data/processed/ml_models/`)
- ✅ `random_forest_model.pkl` exists
- ✅ `feature_importance.csv` shows `gcc_tidal_range` in top 10
- ✅ `holdout_region.txt` contains "SP"

### **3. Predictions** (`data/processed/ml_classified/`)
- ✅ 7 `.gpkg` files (one per region)
- ✅ Columns: `salinity_class_final`, `confidence_level`

### **4. Validation** (`data/processed/validation_improved/`)
- ✅ `globsalt_holdout_sp.csv` shows accuracy 75-85%
- ✅ `distance_stratified_sp.csv` shows <50% estuarine @ 0-20km

---

## 🔬 **Scientific Checks**

### **Feature Importance** (Check this!):
```bash
# View top 10 features
python -c "import pandas as pd; df = pd.read_csv('data/processed/ml_models/feature_importance.csv'); print(df.head(10))"

# Expected top features:
1. gcc_tidal_range (⭐⭐⭐⭐⭐ PRIMARY!)
2. dist_to_coast_km
3. dynqual_salinity_psu
4. gcc_swh_p50 (wave energy)
5. log_upstream_area
...
```

### **Distance Pattern** (Should be realistic!):
```bash
# Check validation report
python -c "import pandas as pd; df = pd.read_csv('data/processed/validation_improved/distance_stratified_sp.csv'); print(df[['distance_bin', 'estuarine_pct']])"

# Expected pattern:
0-20 km: 40-50% estuarine (NOT 69%!)
20-50 km: 10-20% estuarine
50-100 km: 2-5% estuarine
>100 km: <1% estuarine (correct!)
```

---

## 🚨 **Troubleshooting**

### **Issue 1: GCC features not found**
```bash
# Re-run GCC integration
python scripts/ml_salinity/add_gcc_to_features.py --all-regions
```

### **Issue 2: Model training fails**
```bash
# Check if all feature files exist
ls data/processed/ml_features/

# Should see 7 files: features_af.parquet, features_as.parquet, etc.
```

### **Issue 3: Out of memory**
```bash
# Process regions one at a time
python scripts/ml_salinity/ml_dynqual_master_pipeline.py --region AF
python scripts/ml_salinity/ml_dynqual_master_pipeline.py --region AS
# ... etc
```

---

## 📈 **Expected Results**

### **Before GCC** (Old model):
```
Test accuracy: 85%
Distance pattern: 69% estuarine @ 0-20km (TOO HIGH!)
Feature importance: dist_to_coast (top 1)
Problem: Overestimates everywhere
```

### **After GCC** (Current model):
```
Test accuracy: 80-85% (similar)
Distance pattern: 40-50% estuarine @ 0-20km (realistic!)
Feature importance: gcc_tidal_range (top 1) ⭐
Solution: Physics-based predictions (Savenije 2012)
```

---

## 🎉 **Success Criteria**

✅ **Pipeline completes without errors**  
✅ **60+ features** (baseline + DynQual + GCC)  
✅ **`gcc_tidal_range` exists** in feature files  
✅ **Model accuracy >75%** on test set  
✅ **Distance pattern realistic** (<50% @ 0-20km)  
✅ **Holdout validation >70%** on SP region  
✅ **All 7 regions predicted** (.gpkg files exist)

---

## 🚀 **Next Steps After ML Pipeline**

### **Phase 2: Surface Area Calculation**

Once classifications are complete:
1. Convert classified segments (LineStrings) to water body polygons
2. Calculate surface areas by classification type
3. Aggregate by region, basin, estuary type
4. Generate publication-ready results

**Script**: `scripts/surface_area_calculation/calculate_surface_areas_master.py` (to be implemented)

---

## 📚 **Key Files to Review**

1. **Feature importance**: `data/processed/ml_models/feature_importance.csv`
   - Check if `gcc_tidal_range` is in top 5

2. **Training metadata**: `data/processed/ml_models/training_metadata.json`
   - Verify 60+ features, SP holdout

3. **Validation report**: `data/processed/validation_improved/globsalt_holdout_sp.csv`
   - Check accuracy (expected 75-85%)

4. **Distance validation**: `data/processed/validation_improved/distance_stratified_sp.csv`
   - Check realistic pattern (not 69% @ 0-20km!)

---

## ✅ **Summary**

**Question**: Do I need to run anything else?  
**Answer**: ❌ **NO!** Just run:

```bash
python scripts/ml_salinity/ml_dynqual_master_pipeline.py --all-regions
```

**This ONE script**:
- ✅ Extracts features (baseline + DynQual + GCC)
- ✅ Trains model (with tidal range!)
- ✅ Predicts for all segments
- ✅ Validates with multiple methods
- ✅ Saves all outputs

**Time**: 1-2 hours  
**Output**: Complete classification with GCC features!  
**Next**: Surface area calculation → Publication!

🎉 **Your breakthrough is one command away!**
