# 🔧 Diagnostic Scripts

**Purpose**: Debugging and inspection tools (NOT part of main pipeline)

---

## 📋 Scripts in This Folder

### audit_raw_data.py
**Purpose**: Inspect raw dataset schemas and generate README files  
**Usage**: `python scripts/diagnostics/audit_raw_data.py --dataset durr`  
**When to use**: Before writing new processing scripts; verifies actual data structure

### inspect_durr_data.py
**Purpose**: Inspect Dürr shapefile structure (column types, values)  
**Usage**: `python scripts/diagnostics/inspect_durr_data.py`  
**When to use**: When Dürr processing fails; checks actual data types

### inspect_ml_predictions.py
**Purpose**: Inspect ML prediction outputs  
**Usage**: `python scripts/diagnostics/inspect_ml_predictions.py --region SP`  
**When to use**: When validation fails; checks prediction data structure

### inspect_validation_data.py
**Purpose**: Complete inspection of validation inputs  
**Usage**: `python scripts/diagnostics/inspect_validation_data.py --region SP`  
**When to use**: When validation crashes; verifies all input files exist and have correct schemas

### check_features.py
**Purpose**: Verify ML feature files are correctly formatted  
**Usage**: `python scripts/diagnostics/check_features.py --region SP`  
**When to use**: When ML training fails; checks feature matrix structure

### evaluate_dynqual_feasibility.py
**Purpose**: Test whether DynQual features improve ML accuracy  
**Usage**: `python scripts/diagnostics/evaluate_dynqual_feasibility.py --all-regions`  
**When to use**: After training; decides if DynQual should be kept or removed

---

## ⚠️ Important

**These scripts are NOT part of the main pipeline!**

- Located in `scripts/diagnostics/` to keep main folder clean
- Use only for debugging and inspection
- Do NOT include in `master_pipeline.py`
- Results are for diagnostic purposes only

---

## 🎯 When to Use Diagnostics

### Before Processing:
```powershell
# Check raw data structure
python scripts/diagnostics/audit_raw_data.py
```

### After Processing Fails:
```powershell
# Inspect what went wrong
python scripts/diagnostics/inspect_durr_data.py
python scripts/diagnostics/inspect_ml_predictions.py --region SP
```

### After ML Training:
```powershell
# Evaluate DynQual contribution
python scripts/diagnostics/evaluate_dynqual_feasibility.py --all-regions
```

---

**See**: `scripts/README.md` for complete documentation
