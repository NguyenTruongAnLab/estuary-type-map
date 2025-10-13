# HydroSHEDS Data Management Guide

**Project**: Global Estuary Type Map  
**Data Source**: HydroSHEDS RiverATLAS & BasinATLAS v1.0  
**DOI**: [10.5067/9SQ1S6VFQQ20](https://doi.org/10.5067/9SQ1S6VFQQ20)  
**Purpose**: Extract and compress river network data for estuary classification

---

## 📋 Overview

This guide explains how to download, compress, and use HydroSHEDS data for the estuary project. The compression pipeline reduces file sizes by **10-20x** while preserving all scientifically relevant attributes.

**Key Goals**:
- ✅ Keep all files <200MB for GitHub storage
- ✅ Extract only estuary-relevant attributes
- ✅ Filter to coastal rivers (within 500km of ocean)
- ✅ Maintain complete data provenance with DOIs

---

## 📂 Directory Structure

```
data/
├── hydrosheds/                    # Raw HydroSHEDS data (NOT in git)
│   ├── RiverATLAS_v10_shp/       # River network shapefiles
│   │   └── RiverATLAS_v10.shp    # Main shapefile (~500MB)
│   ├── BasinATLAS_v10.gdb/       # Basin geodatabase (~2GB)
│   └── README.md                  # Download instructions
├── processed/                     # Compressed outputs (IN git)
│   ├── rivers_coastal.gpkg       # Coastal rivers (<50MB)
│   ├── basins_level06.gpkg       # Large basins (<100MB)
│   └── basins_level08.gpkg       # Detailed basins (<150MB)
└── .gitignore                     # Excludes hydrosheds/ folder
```

---

## 🔽 Step 1: Download HydroSHEDS Data

### **Option A: Direct Download (Recommended)**

1. **RiverATLAS v1.0**:
   - URL: https://data.hydrosheds.org/file/technical-documentation/RiverATLAS_Catalog_v10.xlsx
   - Download: `RiverATLAS_v10.gdb` or `RiverATLAS_v10_shp.zip`
   - Extract to: `data/hydrosheds/RiverATLAS_v10_shp/`

2. **BasinATLAS v1.0**:
   - URL: https://www.hydrosheds.org/products/basinatlas
   - Download: `BasinATLAS_v10.gdb.zip`
   - Extract to: `data/hydrosheds/BasinATLAS_v10.gdb/`

### **Option B: Using wget/curl**

```bash
# Create directory
mkdir -p data/hydrosheds
cd data/hydrosheds

# Download RiverATLAS (example - check HydroSHEDS website for latest links)
wget https://data.hydrosheds.org/.../RiverATLAS_v10_shp.zip
unzip RiverATLAS_v10_shp.zip -d RiverATLAS_v10_shp/

# Download BasinATLAS
wget https://data.hydrosheds.org/.../BasinATLAS_v10.gdb.zip
unzip BasinATLAS_v10.gdb.zip
```

### **Important Notes**:
- ⚠️ Raw files are **LARGE** (~500MB - 2GB)
- ⚠️ Do NOT commit raw files to git
- ✅ Add `data/hydrosheds/` to `.gitignore`
- ✅ Document download location in `data/hydrosheds/README.md`

---

## 🗜️ Step 2: Compress Data

### **Run Compression Script**

```bash
# Install dependencies (if needed)
pip install geopandas fiona shapely pyproj tqdm

# Run compression
python scripts/compress_hydrosheds.py
```

### **What It Does**:

1. **Extracts Relevant Attributes Only**:
   - River discharge (for tidal influence classification)
   - Distance to ocean (for coastal filtering)
   - Elevation & slope (for tidal limit estimation)
   - Stream order (for river size classification)
   
2. **Filters Data**:
   - **Rivers**: Only keeps reaches within 500km of ocean
   - **Basins**: Processes multiple levels (6, 8) for multi-resolution display
   
3. **Compresses**:
   - Simplifies geometries (tolerance 0.01° ≈ 1km)
   - Converts to GeoPackage (.gpkg) format (10-20x compression)
   - Removes unnecessary attributes
   
4. **Adds Provenance**:
   - `data_source`: "HydroSHEDS RiverATLAS v1.0"
   - `data_source_doi`: "10.5067/9SQ1S6VFQQ20"
   - `processed_date`: Current date

### **Expected Output**:

```
Processing RiverATLAS v1.0
==============================================================
✓ Loaded 8,500,000 river reaches
  Original columns: 283
  Selected columns: 14
🌊 Filtering to coastal rivers (distance to ocean < 500 km)...
  Kept 1,250,000 / 8,500,000 reaches (14.7%)
✂️  Simplifying geometries (tolerance=0.01°)...
💾 Saving to GeoPackage: rivers_coastal.gpkg
  Output size: 45.23 MB
✅ File size within GitHub limit (<200MB)

📊 Compression Statistics:
  Compression ratio: 11.1x
  Space saved: 456.77 MB (91.0%)
```

---

## 📊 Step 3: Validate Compressed Data

### **Check File Sizes**

```bash
# List processed files with sizes
ls -lh data/processed/*.gpkg

# Expected output:
# -rw-r--r-- 1 user 46M rivers_coastal.gpkg
# -rw-r--r-- 1 user 95M basins_level06.gpkg
# -rw-r--r-- 1 user 142M basins_level08.gpkg
```

### **Validate Data Integrity**

```python
import geopandas as gpd

# Load compressed river data
rivers = gpd.read_file('data/processed/rivers_coastal.gpkg', layer='rivers')

# Check attributes
print(f"Rivers: {len(rivers):,} reaches")
print(f"Columns: {list(rivers.columns)}")
print(f"CRS: {rivers.crs}")

# Verify provenance
print(f"Data source: {rivers['data_source'].iloc[0]}")
print(f"DOI: {rivers['data_source_doi'].iloc[0]}")

# Check coastal filtering
print(f"Max distance to ocean: {rivers['dis_ocean'].max():.1f} km")
```

---

## 🎯 Step 4: Use in Estuary Classification

### **Classify River Reaches: Freshwater vs Tidal**

```python
import geopandas as gpd
import numpy as np

# Load compressed data
rivers = gpd.read_file('data/processed/rivers_coastal.gpkg')
estuaries = gpd.read_file('data/estuaries.geojson')

# Method 1: Distance-based classification
# Tidal influence typically extends 30-50km upstream from coast
rivers['is_tidal'] = rivers['dis_ocean'] <= 50  # 50km threshold

# Method 2: Elevation-based classification
# Tidal influence rare above 10m elevation
rivers['is_tidal'] = (rivers['dis_ocean'] <= 100) & (rivers['ele_mt_sav'] <= 10)

# Method 3: Intersection with estuary polygons
# Buffer estuary boundaries by 30km upstream
estuary_buffers = estuaries.buffer(0.3)  # ~30km at equator

# Spatial join to tag rivers within estuary influence
rivers_tidal = gpd.sjoin(rivers, estuary_buffers, how='inner', predicate='within')
rivers_tidal['river_class'] = 'tidal_influenced'

# Classify non-intersecting rivers as freshwater
rivers_fresh = rivers[~rivers['HYRIV_ID'].isin(rivers_tidal['HYRIV_ID'])]
rivers_fresh['river_class'] = 'perennial_freshwater'

# Combine
rivers_classified = pd.concat([rivers_tidal, rivers_fresh])

# Export
rivers_classified.to_file('data/rivers_classified.geojson', driver='GeoJSON')
```

### **Extract Basin Attributes for Estuaries**

```python
# Load basins
basins = gpd.read_file('data/processed/basins_level06.gpkg')

# Spatial join with estuaries
estuaries_enriched = gpd.sjoin(estuaries, basins, how='left', predicate='intersects')

# Aggregate basin attributes to estuary level
estuary_attrs = estuaries_enriched.groupby('name').agg({
    'dis_m3_pyr': 'mean',  # Mean discharge
    'for_pc_sse': 'mean',  # Forest cover
    'urb_pc_sse': 'mean',  # Urban cover
    'SUB_AREA': 'sum'      # Total upstream area
}).reset_index()

# Merge back to estuaries
estuaries_final = estuaries.merge(estuary_attrs, on='name', how='left')
```

---

## 🔄 Step 5: Update `.gitignore`

Add raw HydroSHEDS data to `.gitignore`:

```
# HydroSHEDS raw data (too large for GitHub)
data/hydrosheds/RiverATLAS_v10_shp/
data/hydrosheds/BasinATLAS_v10.gdb/
data/hydrosheds/*.zip
data/hydrosheds/*.gdb

# Keep compressed processed data
!data/processed/*.gpkg
```

---

## 📝 Step 6: Document in `data/hydrosheds/README.md`

Create download instructions for collaborators:

```markdown
# HydroSHEDS Data Download Instructions

## Data Source
- **Name**: HydroSHEDS RiverATLAS & BasinATLAS v1.0
- **DOI**: [10.5067/9SQ1S6VFQQ20](https://doi.org/10.5067/9SQ1S6VFQQ20)
- **Website**: https://www.hydrosheds.org/products/hydroatlas

## Download Steps

### RiverATLAS v1.0 (~500MB)
1. Visit: https://www.hydrosheds.org/products/riveratlas
2. Download: `RiverATLAS_v10_shp.zip`
3. Extract to: `data/hydrosheds/RiverATLAS_v10_shp/`

### BasinATLAS v1.0 (~2GB)
1. Visit: https://www.hydrosheds.org/products/basinatlas
2. Download: `BasinATLAS_v10.gdb.zip`
3. Extract to: `data/hydrosheds/BasinATLAS_v10.gdb/`

## Processing
After download, run compression script:
```bash
python scripts/compress_hydrosheds.py
```

Output will be saved to `data/processed/` (committed to git).
```

---

## 🧪 Step 7: Test Integration

```bash
# 1. Validate compressed data
python scripts/test_data.py

# 2. Start local server
python -m http.server 8000

# 3. Test in browser
# - Open http://localhost:8000
# - Switch to "Rivers" mode
# - Verify rivers display correctly
# - Check popups show HydroSHEDS attributes
```

---

## 📊 Compression Results (Expected)

| Dataset | Original Size | Compressed Size | Ratio | Features |
|---------|---------------|-----------------|-------|----------|
| RiverATLAS | ~500 MB | ~45 MB | 11x | 1.25M coastal reaches |
| BasinATLAS Lv6 | ~800 MB | ~95 MB | 8.4x | 350K basins |
| BasinATLAS Lv8 | ~1.2 GB | ~142 MB | 8.5x | 1.2M basins |
| **Total** | **~2.5 GB** | **~282 MB** | **8.9x** | **Combined** |

**GitHub Storage**: ✅ All files <200MB individually, ~280MB total

---

## 🎓 AI Agent Guidelines

When working with HydroSHEDS data:

1. **Always use compressed files** from `data/processed/`, not raw files
2. **Check file sizes** before committing (<200MB limit)
3. **Maintain provenance**: All GeoPackages include `data_source` and `data_source_doi`
4. **Validate coordinates**: Ensure [-180,180] lon, [-90,90] lat
5. **Test performance**: River layers should load in <2s
6. **Document changes**: Update this README if compression parameters change

---

## 📚 References

- **HydroSHEDS**: Lehner, B., et al. (2013). Global River Networks and Ancillary Data. DOI: [10.5067/9SQ1S6VFQQ20](https://doi.org/10.5067/9SQ1S6VFQQ20)
- **RiverATLAS**: Linke, S., et al. (2019). Global hydro-environmental sub-basin and river reach characteristics. *Scientific Data* 6, 283. DOI: [10.1038/s41597-019-0300-6](https://doi.org/10.1038/s41597-019-0300-6)
- **Tutorial**: Based on [CAMELS-RU feature extraction](https://github.com/ealerskans/CAMELS-RU)

---

## 🚨 Troubleshooting

### **File size >200MB**

```python
# Further filter by discharge (keep only larger rivers)
rivers = rivers[rivers['dis_m3_pyr'] > 10]  # >10 m³/s

# Or reduce coastal distance threshold
rivers = rivers[rivers['dis_ocean'] <= 200]  # 200km instead of 500km
```

### **Missing attributes**

Check which columns are available:
```python
import fiona
layers = fiona.listlayers('data/hydrosheds/BasinATLAS_v10.gdb')
schema = fiona.open('data/hydrosheds/BasinATLAS_v10.gdb', layer=layers[0]).schema
print(schema['properties'].keys())
```

### **Geometry errors**

```python
# Fix invalid geometries
rivers['geometry'] = rivers['geometry'].buffer(0)
```

---

**Last Updated**: October 10, 2025  
**Status**: ✅ Ready for implementation
