# 🗺️ Basin Data Comparison: BasinATLAS vs GRIT Catchments

**Date**: October 13, 2025  
**Purpose**: Evaluate which basin dataset to use for surface area calculations

---

## 📊 Available Basin Datasets

### 1. BasinATLAS_v10_lev07_QGIS.gpkg (HydroSHEDS)
**Location**: `data/raw/hydrosheds/BasinATLAS_v10_lev07_QGIS.gpkg`  
**Size**: 401.75 MB  
**Source**: HydroSHEDS BasinATLAS v1.0

**Characteristics**:
- **Geometry**: MultiPolygon (watershed boundaries)
- **Hierarchy**: Level 7 (Pfafstetter coding system)
- **Coverage**: Global
- **Topology**: Has NEXT_DOWN (downstream basin connectivity)

**Key Attributes**:
```python
HYBAS_ID      # Unique basin ID
NEXT_DOWN     # Downstream basin ID (topology!)
NEXT_SINK     # Terminal sink basin
MAIN_BAS      # Main basin ID
SUB_AREA      # Sub-basin area (km²)
UP_AREA       # Upstream drainage area (km²)
PFAF_ID       # Pfafstetter code
ENDO          # Endorheic flag (1=closed basin)
COAST         # Coastal basin flag (1=drains to ocean)
ORDER_        # Stream order
dis_m3_pyr    # Mean annual discharge (m³/year)
run_mm_syr    # Runoff (mm/year)
inu_pc_smn    # Inundation percentage
# + 500+ attributes (land use, climate, population, etc.)
```

**Advantages**:
- ✅ **Rich attributes**: 500+ pre-calculated catchment characteristics
- ✅ **Global coverage**: Consistent worldwide
- ✅ **Topology**: Network connectivity (NEXT_DOWN)
- ✅ **Discharge data**: Modeled discharge values
- ✅ **Well-documented**: Extensive scientific literature
- ✅ **Standard reference**: Used in many global studies

**Disadvantages**:
- ❌ **Level 7 resolution**: ~1,000-10,000 km² per basin (coarse!)
- ❌ **Does not align with GRIT segments**: Different discretization
- ❌ **Large file**: 401.75 MB (processing overhead)
- ❌ **Generic basins**: Not specific to river segments

---

### 2. GRIT Component Catchments
**Location**: `data/raw/GRIT-Michel_2025/GRITv06_component_catchments_{region}_EPSG4326.gpkg`  
**Size**: ~50-200 MB per region  
**Source**: GRIT v0.6 (Michel et al. 2025)

**Characteristics**:
- **Geometry**: Polygon (fine-resolution component watersheds)
- **Hierarchy**: Directly linked to GRIT segments
- **Coverage**: 7 regions (AF, AS, EU, NA, SA, SI, SP)
- **Topology**: Perfect alignment with GRIT river network

**Key Attributes**:
```python
global_id        # Unique catchment ID
area             # Catchment area (km²)
is_coastal       # Drains to ocean (1=yes)
strahler_order   # Stream order
segment_ids      # LINKS TO RIVER SEGMENTS! ← CRITICAL!
```

**Advantages**:
- ✅ **Perfect alignment**: 1:1 correspondence with GRIT segments
- ✅ **Fine resolution**: Each river segment has its catchment
- ✅ **Direct linkage**: No spatial join needed!
- ✅ **Consistent**: Same resolution as classification

**Disadvantages**:
- ❌ **Fewer attributes**: No land use, climate, population data
- ❌ **Regional files**: Must process 7 files separately
- ❌ **No discharge data**: Would need to add from BasinATLAS or DynQual

---

### 3. GRIT Reaches
**Location**: `data/raw/GRIT-Michel_2025/GRITv06_reaches_{region}_EPSG4326.gpkg`  
**Size**: ~1-2 GB per region  
**Source**: GRIT v0.6

**Characteristics**:
- **Geometry**: LineString (river segments with uniform length)
- **Hierarchy**: Uniform 500m-1km reaches
- **Coverage**: 7 regions
- **Width data**: grwl_width_median (satellite-derived!)

**Key Attributes**:
```python
reach_id           # Unique reach ID
segment_id         # LINKS TO SEGMENTS! ← CRITICAL FOR CLASSIFICATION!
grwl_width_median  # Width in meters (satellite) ← FOR POLYGONS!
length             # Reach length (m)
```

**Advantages**:
- ✅ **Width data**: Essential for creating polygons
- ✅ **Links to segments**: Inherits classification
- ✅ **Uniform length**: Consistent discretization
- ✅ **High resolution**: Captures detailed river geometry

**Disadvantages**:
- ❌ **LineStrings**: Not polygons (need conversion)
- ❌ **Large files**: 1-2 GB per region
- ❌ **No basin context**: Just river geometries

---

## 🎯 Recommendation for Surface Area Calculation

### **Use Case 1: Converting Segments to Polygons** ⭐ PRIMARY USE CASE

**Recommendation**: Use **GRIT Reaches** + **OSM Water Polygons**

**Why**:
```python
# Workflow:
ML-classified segments (has salinity/geomorphology)
    ↓
Join to GRIT reaches (via segment_id)
    ↓
GRIT reaches have width data (grwl_width_median)
    ↓
Intersect with OSM water polygons
    ↓
RESULT: Actual water body polygons with classification!
```

**Rationale**:
1. ✅ **Direct linkage**: reaches → segments → classification (no spatial join!)
2. ✅ **Width data**: grwl_width_median for polygon conversion
3. ✅ **OSM validation**: Actual water body shapes, not theoretical buffers
4. ✅ **Fine resolution**: Matches classification granularity

**BasinATLAS role**: **NOT NEEDED** for polygon conversion (wrong resolution)

---

### **Use Case 2: Precise Estuarine Basin Visualization** ⭐ IMPORTANT USE CASE

**Problem with Dürr catchments**:
```
❌ Dürr shows ENTIRE WATERSHEDS:
   - Amazon catchment = 6.9M km² (from Andes to Atlantic)
   - But estuarine area = maybe 50,000 km² (just the mouth!)
   - Makes it look like all of Brazil is "Delta" type
   - Visualization is misleading!
```

**Recommendation**: Use **BasinATLAS Level 7** for web visualization

**Why**:
```python
# Workflow:
BasinATLAS Level 7 (fine-resolution basins)
    ↓
Filter to coastal basins (COAST=1)
    ↓
Further filter (within 100 km of coast, DIST_SINK < threshold)
    ↓
Spatial join with Dürr catchments (inherit estuary type)
    ↓
RESULT: ONLY coastal portions shown with estuary types!
```

**Rationale**:
1. ✅ **Fine resolution**: ~1,000-10,000 km² per basin (not entire watersheds!)
2. ✅ **Coastal filtering**: COAST=1 + DIST_SINK filters to near-coastal basins
3. ✅ **Inherits Dürr types**: Spatial join brings estuary classification
4. ✅ **Web-appropriate**: Shows ONLY estuarine influence zones

**BasinATLAS role**: **EXCELLENT** for estuarine visualization (solves Dürr problem!)

**Script**: `scripts/web_optimization/create_coastal_basins_estuarine_types.py`

---

### **Use Case 3: Adding Catchment Attributes** ⚪ SECONDARY USE CASE

**Recommendation**: Use **GRIT Component Catchments** + **optionally** BasinATLAS

**Why**:
```python
# Workflow:
Classified segments (has classification)
    ↓
Join to GRIT component catchments (via segment_id or spatial join)
    ↓
Catchment provides: drainage area, is_coastal, basin context
    ↓
OPTIONAL: Join to BasinATLAS (via spatial overlay)
    ↓
BasinATLAS provides: land use, climate, population, discharge
    ↓
RESULT: Enriched classification with catchment attributes
```

**Rationale**:
1. ✅ **GRIT catchments**: Perfect alignment with segments (preferred)
2. ✅ **BasinATLAS**: Rich attributes for analysis (optional enhancement)
3. ⚠️ **Spatial join**: Required if using BasinATLAS (computationally expensive)

**BasinATLAS role**: **OPTIONAL** for enrichment (adds context, not essential)

---

### **Use Case 4: Discharge & Runoff Analysis** ⚪ FUTURE USE CASE

**Recommendation**: Use **BasinATLAS** attributes + **DynQual** modeled data

**Why**:
- BasinATLAS has `dis_m3_pyr` (mean annual discharge)
- BasinATLAS has `run_mm_syr` (runoff)
- DynQual has monthly time series (from ML features)
- Can compare/validate against each other

**BasinATLAS role**: **USEFUL** for discharge context (Phase 3)

---

## 📋 Decision Matrix

| Criterion | GRIT Reaches | GRIT Catchments | BasinATLAS |
|-----------|--------------|-----------------|------------|
| **Alignment with segments** | ⭐⭐⭐ Perfect | ⭐⭐⭐ Perfect | ⭐ Poor (different grid) |
| **Width data** | ⭐⭐⭐ Yes! | ❌ No | ❌ No |
| **Polygon conversion** | ⭐⭐⭐ Essential | ❌ Not needed | ❌ Not needed |
| **Estuarine visualization** | ❌ No | ❌ No | ⭐⭐⭐ YES! (solves Dürr problem) |
| **Catchment attributes** | ❌ No | ⭐⭐ Basic | ⭐⭐⭐ Rich (500+) |
| **Discharge data** | ❌ No | ❌ No | ⭐⭐⭐ Yes |
| **File size** | Large (1-2 GB) | Medium (50-200 MB) | Large (401 MB) |
| **Processing speed** | Slow | Fast | Slow |
| **Phase 2 priority** | ⭐⭐⭐ CRITICAL | ⭐ Nice-to-have | ⭐⭐ IMPORTANT (viz!) |

---

## ✅ Final Recommendations

### **For Phase 2: Surface Area Calculation + Visualization**

**For Surface Area Calculation**:
1. ✅ **GRIT Reaches** (width data for polygon conversion) - CRITICAL
2. ✅ **OSM Water Polygons** (actual water body shapes) - CRITICAL
3. ✅ **ML-classified segments** (salinity/geomorphology) - CRITICAL

**For Estuarine Visualization** (NEW!):
4. ✅ **BasinATLAS Level 7** (fine-resolution coastal basins) - IMPORTANT
   - Solves Dürr problem (shows only coastal portions, not entire watersheds!)
   - Script: `scripts/web_optimization/create_coastal_basins_estuarine_types.py`

**Optional**:
5. ⚪ **GRIT Component Catchments** (basic basin context if needed)

**Workflow**:
```
Surface Area:
Step 1: Load ML-classified segments
Step 2: Join to GRIT reaches (inherit classification + get width)
Step 3: Intersect with OSM polygons (get actual water bodies)
Step 4: Calculate area in equal-area projection
Step 5: Aggregate by classification

Visualization:
Step 1: Load BasinATLAS Level 7
Step 2: Filter to coastal basins (COAST=1, DIST_SINK < threshold)
Step 3: Join with Dürr (inherit estuary types)
Step 4: Simplify for web, export GeoJSON
Step 5: Use for interactive map (NOT Dürr full catchments!)
```

**Critical**: Do NOT use BasinATLAS for polygon conversion (wrong resolution), BUT DO use it for visualization!

---

### **For Phase 3: Enrichment & Analysis** (Future)

**Use BasinATLAS for**:
- Land use analysis (agriculture, urban, forest coverage)
- Climate context (temperature, precipitation, runoff)
- Discharge validation (compare to DynQual)
- Population exposure (coastal vulnerability)
- Socioeconomic analysis (GDP, infrastructure)

**Method**:
```python
# Spatial overlay (computationally expensive, but one-time)
segments_enriched = gpd.overlay(
    classified_segments,
    basinATLAS[['HYBAS_ID', 'dis_m3_pyr', 'run_mm_syr', 'inu_pc_smn']],
    how='left'
)
```

---

## 📖 When to Use Each Dataset

| Task | Use GRIT Reaches | Use GRIT Catchments | Use BasinATLAS |
|------|------------------|---------------------|----------------|
| **Convert segments to polygons** | ✅ YES | ❌ NO | ❌ NO |
| **Calculate surface areas** | ✅ YES | ❌ NO | ❌ NO |
| **Get drainage area** | ❌ NO | ✅ YES | ⚪ OPTIONAL |
| **Identify endorheic basins** | ❌ NO | ⚪ BASIC | ✅ YES (ENDO flag) |
| **Get discharge estimates** | ❌ NO | ❌ NO | ✅ YES |
| **Land use analysis** | ❌ NO | ❌ NO | ✅ YES |
| **Climate context** | ❌ NO | ❌ NO | ✅ YES |
| **Population exposure** | ❌ NO | ❌ NO | ✅ YES |

---

## 🚀 Implementation Priority

### **Phase 2 (Now)**:
```
✅ GRIT Reaches (CRITICAL - width data)
✅ OSM Water Polygons (CRITICAL - actual shapes)
✅ ML-classified segments (CRITICAL - classification)
⚪ GRIT Component Catchments (NICE-TO-HAVE - basic context)
❌ BasinATLAS (NOT NEEDED - wrong resolution)
```

### **Phase 3 (Later)**:
```
⚪ BasinATLAS (OPTIONAL - enrichment attributes)
⚪ DynQual discharge (COMPARISON - validate BasinATLAS)
```

---

## 💡 Key Insight

**BasinATLAS is valuable but NOT for polygon conversion!**

- ✅ **Rich attributes**: 500+ catchment characteristics
- ✅ **Future use**: Phase 3 enrichment and analysis
- ❌ **Wrong resolution**: Level 7 is too coarse for GRIT segments
- ❌ **No alignment**: Different discretization than GRIT
- ❌ **Not needed**: For Phase 2 surface area calculation

**Keep BasinATLAS for later, focus on GRIT Reaches + OSM now!**

---

**Created**: October 13, 2025  
**Decision**: Use GRIT Reaches + OSM for Phase 2, defer BasinATLAS to Phase 3  
**Rationale**: Alignment with classification is more important than attribute richness
