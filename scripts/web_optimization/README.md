# 🌐 Web Optimization

**Purpose**: Generate web-ready GeoJSON files for interactive atlas deployment

---

## 🎯 What This Folder Does

Converts large GPKG files (1-5 GB) into optimized GeoJSON (<5MB each) for fast web loading. Implements geometry simplification, attribute filtering, and file splitting to meet GitHub Pages deployment requirements.

---

## 📁 Scripts in This Folder

### 1. optimize_data_final.py
**Purpose**: Generate web-ready GeoJSON with geometry simplification  
**Duration**: 20-30 minutes  
**Input**: `data/processed/*.gpkg` (full-resolution files)  
**Output**: `data/web/*.geojson` (<5MB each)

**What it does**:
- **Geometry simplification**: Douglas-Peucker algorithm (tolerance 0.001°)
- **Attribute filtering**: Keeps only display-needed fields
- **File splitting**: Splits large datasets by region or type
- **Statistics generation**: Creates summary CSVs for charts

**Optimization targets**:
- File size: <5MB per GeoJSON (GitHub Pages limit)
- Load time: <2 seconds per file (3G connection)
- Memory: <200MB for full atlas

**Usage**:
```powershell
python scripts/web_optimization/optimize_data_final.py
```

**Output files**:
```
data/web/
├── rivers_af.geojson           # Simplified river networks
├── rivers_as.geojson
├── ... (7 regions)
├── estuaries_durr.geojson      # Dürr catchments (simplified)
├── estuaries_baum.geojson      # Baum morphometry
├── salinity_zones.geojson      # GlobSalt zones
└── summary_statistics.csv      # Global statistics
```

**Simplification settings**:
- Tolerance: 0.001° (~100m at equator)
- Preserves topology (no self-intersections)
- Retains key attributes only

---

### 2. convert_gpkg_to_geojson.py
**Purpose**: Batch convert all GPKG files to GeoJSON format  
**Duration**: 5-10 minutes  
**Input**: All `data/processed/*.gpkg` files  
**Output**: Matching `.geojson` files

**What it does**:
- Scans `data/processed/` for all GPKG files
- Converts to GeoJSON with proper CRS (EPSG:4326)
- Maintains full attribute schema (no simplification)
- Generates matching metadata JSON files

**Why separate from optimize_data_final.py**:
- This creates FULL-RESOLUTION GeoJSON (for downloads)
- optimize_data_final.py creates SIMPLIFIED versions (for web display)
- Users can download full data, but web loads simplified versions

**Usage**:
```powershell
python scripts/web_optimization/convert_gpkg_to_geojson.py
```

**Output location**: Same as GPKG (in `data/processed/`)

**File size note**: These are NOT web-optimized! Use `optimize_data_final.py` outputs for web deployment.

---

## 🔄 Execution Order

Run in this sequence:

```
1. optimize_data_final.py
   ↓
2. convert_gpkg_to_geojson.py (optional - for full-resolution downloads)
```

**Note**: `master_pipeline.py` runs both automatically in Stage 3.

---

## 📊 Output Files

### Web-Optimized (data/web/)
```
data/web/
├── rivers_af.geojson           # 2-4 MB (simplified)
├── rivers_as.geojson
├── rivers_eu.geojson
├── rivers_na.geojson
├── rivers_sa.geojson
├── rivers_si.geojson
├── rivers_sp.geojson
├── estuaries_durr.geojson      # 3-5 MB (simplified)
├── estuaries_baum.geojson      # <1 MB
├── salinity_zones.geojson      # 2-3 MB
└── summary_statistics.csv      # <10 KB
```

### Full-Resolution (data/processed/)
```
data/processed/
├── rivers_grit_ml_classified_af.geojson   # 50-200 MB (full)
├── ... (7 regions)
├── durr_estuaries.geojson                 # 10-30 MB (full)
└── baum_morphometry.geojson               # 1-5 MB (full)
```

**Usage**:
- **web/**: Deploy to GitHub Pages (loads fast)
- **processed/**: Provide as downloads (full detail)

---

## 🎨 Optimization Techniques

### 1. Geometry Simplification
**Algorithm**: Douglas-Peucker  
**Tolerance**: 0.001° (~100m)

**Before**: River segment with 500 points  
**After**: Same segment with 50 points (90% reduction)

**Trade-off**: Visual accuracy vs file size
- At zoom level 1-8: Simplified is visually identical
- At zoom level 9+: Some detail loss, but acceptable

### 2. Attribute Filtering
**Kept**:
- `global_id`: Unique identifier
- `salinity_zone`: Classification
- `system_type`: Estuarine/Non-Tidal
- `strahler_order`: Stream order
- `geometry`: Simplified geometry

**Removed**:
- Internal IDs (segment_id, reach_id)
- Detailed hydrology (drainage_area_in, drainage_area_out)
- ML metadata (prediction_probability, confidence_level)
- Processing metadata (classification_method, timestamp)

**Reasoning**: Web display only needs minimal attributes. Full data available in processed/ folder.

### 3. File Splitting
**Strategy**: Split by region AND type

**Why**:
- Single global file = 500 MB → Too large!
- 7 regional files = 50-80 MB each → Still too large!
- 7 regions × 3 types = 21 files of 5-10 MB → Perfect!

**Implementation**:
- Rivers: Split by region (AF, AS, EU, NA, SA, SI, SP)
- Estuaries: Split by source (Dürr, Baum)
- Salinity: Combined (already small)

### 4. Coordinate Precision
**Original**: 15 decimal places (`-122.419415236547`)  
**Optimized**: 6 decimal places (`-122.419415`)

**Precision**: 6 decimals = ~10 cm accuracy (more than sufficient!)  
**File size reduction**: ~20-30%

---

## 🌐 Web Deployment Checklist

After running optimization scripts:

1. ✅ **Verify file sizes**:
   ```powershell
   Get-ChildItem "data\web\*.geojson" | Select-Object Name, @{N='SizeMB';E={$_.Length/1MB}}
   ```
   All files should be <5MB

2. ✅ **Test loading locally**:
   ```powershell
   python -m http.server 8000
   # Open http://localhost:8000 in browser
   # Check Network tab: files load <2 seconds
   ```

3. ✅ **Check geometry validity**:
   ```powershell
   # Load GeoJSON in QGIS
   # Check: No missing features, no self-intersections
   ```

4. ✅ **Verify attributes**:
   ```powershell
   # Inspect one GeoJSON file
   # Ensure salinity_zone, system_type present
   ```

5. ✅ **Deploy to GitHub Pages**:
   ```powershell
   git add data/web/*.geojson
   git commit -m "Update web-optimized GeoJSON"
   git push origin main
   # GitHub Actions deploys automatically
   ```

---

## 📈 Performance Benchmarks

### Before Optimization
- File sizes: 50-200 MB per region
- Load time: 15-30 seconds (3G)
- Memory: 1-2 GB peak
- Render time: 5-10 seconds

### After Optimization
- File sizes: 2-5 MB per region
- Load time: 1-2 seconds (3G)
- Memory: 100-200 MB peak
- Render time: <1 second

**Improvement**: 10-40x faster loading, 10x less memory!

---

## 🔧 Customization Options

### Adjust Simplification Tolerance

In `optimize_data_final.py`:
```python
# More aggressive (smaller files, less detail)
TOLERANCE = 0.005  # ~500m

# Less aggressive (larger files, more detail)
TOLERANCE = 0.0005  # ~50m

# Default (balanced)
TOLERANCE = 0.001  # ~100m
```

### Change Attribute Set

In `optimize_data_final.py`:
```python
# Keep more attributes (larger files)
KEEP_ATTRS = [
    'global_id', 'salinity_zone', 'system_type',
    'strahler_order', 'confidence_level'  # Add this
]

# Keep fewer attributes (smaller files)
KEEP_ATTRS = [
    'global_id', 'salinity_zone'  # Minimal
]
```

### Split Threshold

In `optimize_data_final.py`:
```python
# Smaller split threshold (more files)
MAX_FILE_SIZE_MB = 3.0

# Larger split threshold (fewer files)
MAX_FILE_SIZE_MB = 10.0

# Default
MAX_FILE_SIZE_MB = 5.0  # GitHub Pages limit
```

---

## 🚨 Common Issues

### Issue: Files still >5MB after optimization
**Solutions**:
1. Increase tolerance: `TOLERANCE = 0.002`
2. Reduce attributes: Remove `strahler_order`
3. Split further: By salinity zone within regions

### Issue: Geometry appears blocky
**Problem**: Tolerance too high  
**Solution**: Reduce tolerance: `TOLERANCE = 0.0005`

### Issue: Loading still slow
**Check**:
1. File size OK? (<5MB)
2. CDN configured? (jsDelivr for libraries)
3. Browser cache enabled?
4. GZIP compression active? (GitHub Pages auto-compresses)

---

## 🔗 Related Folders

- **raw_data_processing/**: Provides full-resolution input data
- **ml_salinity/**: Provides classified segments for web display

---

## 📖 Key Documentation

- **docs/VISUALIZATION_MODES.md**: Web atlas interface design
- **index.html**: Web atlas implementation
- **js/map.js**: Leaflet map configuration

---

**Quick Start**: `python scripts/web_optimization/optimize_data_final.py`
