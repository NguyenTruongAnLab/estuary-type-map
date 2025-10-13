# 🌊 Water Body Classification

**Purpose**: Classification scripts organized by methodology approach

**What This Folder Does**: Provides different classification frameworks for water bodies (rivers, estuaries, lakes, wetlands) based on various scientific criteria.

---

## 🎯 Classification Approaches

This folder organizes water body classification by **methodology**, not by dataset:

```
waterbody_classification/
├── by_salinity/              # Venice System, O'Connor TFZ framework
├── by_geomorphology/         # Dürr estuary types, basin characteristics
├── by_hydrology/             # Discharge, stream order, drainage area
├── by_biome/                 # Climate zones, ecoregions
└── integrated/               # Multi-criteria classification frameworks
```

---

## 📁 Subfolder Organization

### 1. by_salinity/ — Salinity-Based Classification
**Scientific Framework**: Venice System (1958) + O'Connor et al. (2022)

**Scripts**:
- `classify_venice_system.py` - Apply Venice System thresholds (0.5, 5, 18, 30 PSU)
- `identify_tfz_extents.py` - Identify Tidal Freshwater Zones
- `classify_by_residence_time.py` - Classify mixing zones

**Input**: 
- GlobSalt measurements
- ML salinity predictions
- Tidal extent data

**Output**:
- Freshwater, Oligohaline, Mesohaline, Polyhaline, Euhaline zones
- TFZ boundaries
- Salinity gradient classifications

**Use cases**:
- Biogeochemical modeling (GHG emissions vary by salinity zone)
- Ecosystem classification (species distributions)
- Water quality management

---

### 2. by_geomorphology/ — Geomorphological Classification
**Scientific Framework**: Dürr et al. (2011) + Baum et al. (2024)

**Scripts**:
- `classify_durr_types.py` - Apply Dürr estuary typology (7 types)
- `classify_by_basin_shape.py` - Length-width ratios, constriction factors
- `identify_deltas.py` - Delta identification (bifurcation analysis)
- `classify_fjords.py` - Fjord characteristics (depth, glacial features)

**Input**: 
- Basin boundaries (HydroSHEDS, Dürr catchments)
- Morphometric measurements (Baum dataset)
- DEM data (for depth, slope)

**Output**:
- Delta, Fjord, Lagoon, Coastal Plain, Karst, Archipelagic, Small Delta
- Morphometric parameters (area, length, width, depth)
- Shape indices

**Use cases**:
- Sediment transport modeling
- Habitat classification
- Coastal geomorphology studies

---

### 3. by_hydrology/ — Hydrological Classification
**Scientific Framework**: Stream order, discharge regimes, drainage patterns

**Scripts**:
- `classify_by_stream_order.py` - Strahler/Horton classification
- `classify_by_discharge.py` - Flow regime classification
- `classify_drainage_patterns.py` - Dendritic, trellis, radial patterns
- `identify_endorheic.py` - Closed basin identification

**Input**: 
- GRIT topology (stream order, connectivity)
- Discharge data (DynQual, station measurements)
- Basin boundaries

**Output**:
- Stream order classes (1-12)
- Flow regime types (perennial, intermittent, ephemeral)
- Drainage pattern classifications
- Endorheic vs exorheic basins

**Use cases**:
- Hydrological modeling
- Flood risk assessment
- Water resource management

---

### 4. by_biome/ — Biome-Based Classification
**Scientific Framework**: Climate zones, ecoregions, biogeography

**Scripts**:
- `classify_by_climate_zone.py` - Köppen-Geiger climate classification
- `classify_by_ecoregion.py` - Freshwater ecoregions (Abell et al.)
- `classify_by_latitude.py` - Tropical, temperate, polar zones

**Input**: 
- Climate data (temperature, precipitation)
- Ecoregion boundaries
- Latitude/longitude

**Output**:
- Climate zone classifications
- Ecoregion assignments
- Biogeographic zones

**Use cases**:
- Biodiversity studies
- Climate change impact assessment
- Conservation planning

---

### 5. integrated/ — Multi-Criteria Classification
**Scientific Framework**: Combined approaches for comprehensive classification

**Scripts**:
- `hierarchical_classification.py` - Multi-level classification tree
- `fuzzy_classification.py` - Fuzzy logic for transitional zones
- `ensemble_classification.py` - Combine multiple criteria with weights

**Input**: 
- All classification outputs from subfolders
- User-defined weights/priorities

**Output**:
- Comprehensive water body classification
- Confidence levels for each classification
- Uncertainty maps

**Use cases**:
- Atlas development (this project!)
- Policy and management (requires multiple perspectives)
- Scientific synthesis

---

## 🔄 Relationship with Other Folders

### Data Flow:

```
scripts/raw_data_processing/
    ↓
    Creates: rivers_grit_segments_classified_*.gpkg (foundation data)
    ↓
scripts/ml_salinity/
    ↓
    Creates: ML predictions for salinity (fills gaps in GlobSalt)
    ↓
scripts/waterbody_classification/  ← YOU ARE HERE
    ↓
    Applies various classification frameworks:
    ├─ by_salinity/      → Salinity zones (Venice System)
    ├─ by_geomorphology/ → Estuary types (Dürr)
    ├─ by_hydrology/     → Stream order, discharge
    ├─ by_biome/         → Climate, ecoregions
    └─ integrated/       → Combined classifications
    ↓
scripts/surface_area_calculation/ (future)
    ↓
    Calculates areas by classification
    ↓
scripts/web_optimization/
    ↓
    Creates: Web-ready GeoJSON for interactive atlas
```

---

## 📋 Implementation Status

| Subfolder | Status | Priority | Scripts Planned |
|-----------|--------|----------|-----------------|
| **by_salinity/** | 🔄 Partial | ⭐⭐⭐ HIGH | 3 scripts (Venice, TFZ, mixing) |
| **by_geomorphology/** | ⏳ Planned | ⭐⭐ MEDIUM | 4 scripts (Dürr, deltas, fjords, shape) |
| **by_hydrology/** | ⏳ Planned | ⭐⭐ MEDIUM | 4 scripts (order, discharge, patterns, endorheic) |
| **by_biome/** | ⏳ Planned | ⭐ LOW | 3 scripts (climate, ecoregion, latitude) |
| **integrated/** | ⏳ Planned | ⭐⭐⭐ HIGH | 3 scripts (hierarchical, fuzzy, ensemble) |

**Current implementation**:
- ✅ `by_salinity/` partially implemented (Venice System in ML pipeline)
- ✅ `by_geomorphology/` partially implemented (Dürr in raw_data_processing)
- ⏳ Other approaches planned for Phase 2

---

## 🎓 Scientific Frameworks Reference

### Salinity Classification:
- **Venice System (1958)**: Symposium on the Classification of Brackish Waters
- **O'Connor et al. (2022)**: Tidal Freshwater Zone framework
  - DOI: 10.1016/j.ecss.2022.107786

### Geomorphology Classification:
- **Dürr et al. (2011)**: Worldwide Typology of Nearshore Coastal Systems
  - DOI: 10.1007/s12237-011-9381-y
- **Baum et al. (2024)**: Large Estuary Morphometry
  - DOI: 10.1016/j.geomorph.2024.xxxxx

### Hydrological Classification:
- **Strahler (1957)**: Quantitative analysis of watershed geomorphology
- **Horton (1945)**: Erosional development of streams

### Biome Classification:
- **Köppen-Geiger**: Climate classification system
- **Abell et al. (2008)**: Freshwater Ecoregions of the World
  - DOI: 10.1641/B580507

---

## 🚀 Quick Start

### Example: Classify by Salinity (Venice System)

```python
# Future script: by_salinity/classify_venice_system.py
import geopandas as gpd
import pandas as pd

def classify_venice_system(salinity_psu):
    """
    Classify water body by Venice System thresholds
    
    Args:
        salinity_psu: Salinity in practical salinity units (PSU)
    
    Returns:
        str: Venice System class
    """
    if salinity_psu < 0.5:
        return 'Freshwater'
    elif salinity_psu < 5.0:
        return 'Oligohaline'
    elif salinity_psu < 18.0:
        return 'Mesohaline'
    elif salinity_psu < 30.0:
        return 'Polyhaline'
    else:
        return 'Euhaline'

# Load classified segments
segments = gpd.read_file('data/processed/rivers_grit_ml_classified_*.gpkg')

# Apply Venice classification
segments['venice_class'] = segments['salinity_psu'].apply(classify_venice_system)

# Save
segments.to_file('data/processed/classified_by_salinity.gpkg')
```

---

## 📚 Additional Resources

### Documentation:
- **docs/CLASSIFICATION_FRAMEWORK.md** - Complete scientific methodology
- **docs/DATA_SOURCES.md** - Input datasets and provenance
- **scripts/ml_salinity/README.md** - ML salinity prediction

### Related Scripts:
- **scripts/raw_data_processing/** - Foundation data creation
- **scripts/ml_salinity/** - Salinity prediction (fills gaps)
- **scripts/web_optimization/** - Web-ready output generation

---

## 🔮 Future Development (Phase 2)

### Priority 1: Complete by_salinity/
```powershell
# Implement Venice System classification
scripts/waterbody_classification/by_salinity/classify_venice_system.py

# Implement TFZ identification
scripts/waterbody_classification/by_salinity/identify_tfz_extents.py
```

### Priority 2: Complete by_geomorphology/
```powershell
# Implement Dürr classification
scripts/waterbody_classification/by_geomorphology/classify_durr_types.py

# Implement delta identification
scripts/waterbody_classification/by_geomorphology/identify_deltas.py
```

### Priority 3: Integrated classification
```powershell
# Hierarchical classification combining all approaches
scripts/waterbody_classification/integrated/hierarchical_classification.py
```

---

## 🎯 Design Principles

### 1. Separation of Concerns
Each classification approach in its own subfolder:
- ✅ **Modular**: Easy to add new approaches
- ✅ **Maintainable**: Clear organization
- ✅ **Reusable**: Mix and match classifications

### 2. Scientific Transparency
Every classification based on peer-reviewed literature:
- ✅ **Documented**: Citations and DOIs provided
- ✅ **Reproducible**: Clear methodology
- ✅ **Validated**: Independent verification

### 3. Flexibility
Support multiple classification needs:
- ✅ **Single-criterion**: Use one approach (e.g., salinity only)
- ✅ **Multi-criterion**: Combine approaches (e.g., salinity + geomorphology)
- ✅ **Weighted**: User-defined priorities

---

## 📖 See Also

- **README.md** (project root) - Complete project documentation
- **docs/CLASSIFICATION_FRAMEWORK.md** - Detailed scientific methods
- **ROADMAP.md** - Project timeline and priorities

---

**Created**: October 13, 2025  
**Status**: Folder structure established, scripts to be implemented in Phase 2  
**Next Steps**: Implement by_salinity/ scripts (highest priority)
