# 🏔️ Geomorphology-Based Classification

**Scientific Framework**: Dürr et al. (2011) + Baum et al. (2024)

**Purpose**: Classify estuaries and water bodies by physical template and geomorphological characteristics

---

## 🎯 Classification Schemes

### Dürr et al. (2011) - 7 Estuary Types

| Type | Characteristics | Global % | Examples |
|------|----------------|----------|----------|
| **Delta** | Distributary networks, high sediment load | 29% | Nile, Mississippi, Ganges |
| **Coastal Plain** | Drowned river valleys, low gradient | 31% | Chesapeake Bay, Delaware Bay |
| **Fjord** | Glacially carved, deep, steep sides | 21% | Norwegian fjords, Puget Sound |
| **Lagoon** | Barrier-enclosed, restricted exchange | 12% | Laguna Madre, Venice Lagoon |
| **Karst** | Limestone dissolution features | 5% | Florida Springs, Adriatic coast |
| **Archipelagic** | Island-studded, complex coastline | 1% | Indonesian estuaries |
| **Small Deltas** | Minor distributary systems | 1% | Small Mediterranean rivers |

---

## 📁 Scripts (To Be Implemented)

### 1. classify_durr_types.py
**Status**: ⏳ Planned (Phase 2)  
**Purpose**: Apply Dürr classification to all coastal water bodies

**Input**:
- `data/processed/durr_estuaries.geojson` (expert-classified catchments)
- `data/processed/rivers_grit_segments_*.gpkg` (all segments)

**Output**:
- `data/processed/classified_durr_types_*.gpkg`

**Method**:
- Spatial join: Segments → Dürr catchment polygons
- Inherit estuary type from catchment
- Flag segments outside Dürr coverage

---

### 2. classify_by_basin_shape.py
**Status**: ⏳ Planned (Phase 2)  
**Purpose**: Classify based on morphometric ratios

**Input**:
- Basin boundaries (HydroSHEDS, Dürr catchments)
- Baum morphometry measurements

**Output**:
- `data/processed/classified_basin_shape_*.gpkg`

**Method**:
```python
def classify_by_shape(length_km, width_km, area_km2):
    length_width_ratio = length_km / width_km
    form_factor = area_km2 / (length_km ** 2)
    
    if length_width_ratio > 10:
        return 'Elongated (River-dominated)'
    elif length_width_ratio > 3:
        return 'Moderately elongated'
    elif form_factor > 0.5:
        return 'Circular (Lagoon-like)'
    else:
        return 'Funnel-shaped'
```

---

### 3. identify_deltas.py
**Status**: ⏳ Planned (Phase 2)  
**Purpose**: Identify delta systems using bifurcation analysis

**Input**:
- GRIT topology (bifurcation nodes)
- Sediment load data (DynQual)
- Coastal proximity

**Output**:
- `data/processed/identified_deltas_*.gpkg`

**Method**:
```python
def identify_delta(segment):
    # Deltas have:
    # 1. Multiple downstream branches (bifurcations)
    # 2. Near coast (<50 km)
    # 3. High sediment load
    
    has_bifurcations = segment['downstream_count'] > 1
    near_coast = segment['dist_to_coast_km'] < 50
    high_sediment = segment['sediment_load'] > threshold
    
    return has_bifurcations and near_coast and high_sediment
```

---

### 4. classify_fjords.py
**Status**: ⏳ Planned (Phase 2)  
**Purpose**: Identify fjord characteristics

**Input**:
- Depth data (bathymetry, if available)
- Slope analysis (DEM)
- Latitude (glacial influence)

**Output**:
- `data/processed/classified_fjords_*.gpkg`

**Method**:
```python
def identify_fjord(basin):
    # Fjords have:
    # 1. High depth/width ratio (deep, narrow)
    # 2. Steep slopes (glacially carved)
    # 3. High latitude (>45° typically)
    
    is_deep = basin['mean_depth_m'] > 50
    is_narrow = basin['width_km'] < 5
    high_latitude = abs(basin['latitude']) > 45
    
    return is_deep and is_narrow and high_latitude
```

---

## 🔬 Scientific References

1. **Dürr et al. (2011)** - Worldwide Typology
   - DOI: 10.1007/s12237-011-9381-y
   - 7,057 estuaries classified globally

2. **Baum et al. (2024)** - Large Estuary Morphometry
   - DOI: 10.1016/j.geomorph.2024.xxxxx
   - 106 large estuaries with field measurements

3. **Dalrymple et al. (1992)** - Estuarine Facies Models
   - Wave-dominated vs tide-dominated vs river-dominated

---

## 🎯 Use Cases

1. **Sediment Dynamics**
   - Deltas: High deposition, land building
   - Fjords: Deep sediment traps, anoxic layers
   - Lagoons: Fine sediment accumulation

2. **Mixing & Circulation**
   - Coastal Plain: Well-mixed, tidal pumping
   - Fjords: Strong stratification, sill effects
   - Lagoons: Restricted exchange, long residence times

3. **Habitat Classification**
   - Different estuary types = different ecosystems
   - Geomorphology influences biodiversity patterns
   - Conservation prioritization

---

## 📊 Expected Results

### Global Estuary Distribution (Dürr et al. 2011):
- **Coastal Plain**: ~2,200 estuaries (31%)
- **Delta**: ~2,000 estuaries (29%)
- **Fjord**: ~1,500 estuaries (21%)
- **Lagoon**: ~850 estuaries (12%)
- **Karst**: ~350 estuaries (5%)
- **Archipelagic**: ~70 estuaries (1%)
- **Small Deltas**: ~70 estuaries (1%)

### Regional Patterns:
- **Deltas**: Abundant in Asia (Ganges, Mekong, Yangtze, Yellow River)
- **Fjords**: Concentrated in high latitudes (Norway, Alaska, Chile, New Zealand)
- **Lagoons**: Common in Mediterranean, Gulf of Mexico, Australia
- **Coastal Plain**: Dominant in Atlantic coast (North America, Africa)

---

## 🔗 Dependencies

**Data inputs**:
- `scripts/raw_data_processing/process_durr.py` → Dürr estuary polygons
- `scripts/raw_data_processing/process_baum.py` → Morphometry measurements
- `scripts/raw_data_processing/process_grit_all_regions.py` → GRIT topology

**Outputs used by**:
- `scripts/waterbody_classification/integrated/` → Multi-criteria classification
- `scripts/surface_area_calculation/` → Calculate area by estuary type
- `scripts/web_optimization/` → Interactive geomorphology maps

---

## 🚀 Implementation Priority

**Phase 2 - Medium Priority**

1. ✅ `classify_durr_types.py` - Apply existing Dürr classification (Week 2)
2. ⚪ `identify_deltas.py` - Delta identification (Week 3)
3. ⚪ `classify_by_basin_shape.py` - Morphometric analysis (Week 4)
4. ⚪ `classify_fjords.py` - Fjord characteristics (Week 4)

---

**Created**: October 13, 2025  
**Status**: Folder structure ready, awaiting Phase 2 implementation  
**Next**: Implement classify_durr_types.py (uses existing Dürr dataset)
