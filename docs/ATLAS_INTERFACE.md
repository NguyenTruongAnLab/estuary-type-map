---
layout: default
title: ATLAS INTERFACE
---

# Visualization Layers & Modes

**Last Updated**: October 10, 2025  
**Architecture**: Modular Layer System

---

## 🎯 Overview

The Global Estuary Type Map uses a **modular layer architecture** where each dataset is an independent, toggleable layer. Users can activate multiple layers simultaneously to see combined information.

### Available Layers

| Layer | Features | Type | Size | Priority |
|-------|----------|------|------|----------|
| 🗺️ **Dürr Classification** | 970 estuaries | Polygon + Point | ~3-5 MB | **Base** |
| 📐 **Baum Morphometry** | 271 estuaries | Point | ~100 KB | High |
| 💧 **GlobSalt Salinity** | 10k-50k basins | Polygon/Point | ~2-5 MB | High |
| 🏞️ **HydroSHEDS Rivers** | 500k-1M reaches | LineString | ~5-10 MB | Medium |
| 🌊 **GCC Coastal** | ~10k segments | Point | ~3-5 MB | Optional |

---

## 🗺️ Layer 1: Dürr Classification (Base Layer)

### Description
Base estuary classification from Dürr et al. (2011) worldwide typology - the foundation for all other layers.

### Data Source
- **File**: `data/processed/durr_estuaries.geojson`
- **Processor**: `scripts/process_durr.py`
- **Reference**: Dürr, H.H. et al. (2011). Estuaries and Coasts, 34(3), 441-458
- **DOI**: 10.1007/s12237-011-9381-y

### Features
- **Total**: 970 valid coastal estuarine systems
- **Geometry**: Polygon watersheds with point centroids
- **Coverage**: Global
- **Classification**: 7 geomorphological types

### Attributes
```json
{
  "name": "Chesapeake Bay",
  "type": "Coastal Plain",
  "type_detailed": "Tidal System (Type II)",
  "type_code": 2,
  "basin_area_km2": 165760,
  "lon": -76.25,
  "lat": 38.85,
  "sea_name": "Atlantic Ocean",
  "ocean_name": "Atlantic"
}
```

### Type Distribution
- **Delta**: ~280 estuaries (29%)
- **Coastal Plain**: ~300 estuaries (31%)
- **Fjord**: ~200 estuaries (21%)
- **Lagoon**: ~120 estuaries (12%)
- **Karst**: ~70 estuaries (7%)

### Color Scheme
```javascript
Delta:          #8b4513  // Brown
Coastal Plain:  #ff8c00  // Orange
Lagoon:         #50c878  // Green
Fjord:          #4a90e2  // Blue
Karst:          #9370db  // Purple
```

### Use Cases
- Base layer for all visualizations
- Geomorphological classification
- Regional distribution patterns
- Filter by estuary type

---

## 📐 Layer 2: Baum Morphometry (Enhancement Layer)

### Description
Quantitative morphometric measurements for 271 large structural estuaries worldwide.

### Data Source
- **File**: `data/processed/baum_morphometry.geojson`
- **Processor**: `scripts/process_baum.py`
- **Reference**: Baum, M.J., Schüttrumpf, H., & Siemes, R.W. (2024). Geomorphology

### Features
- **Total**: 271 large embayments
- **Geometry**: Point locations (centroid coordinates)
- **Coverage**: Global (focus on large systems)

### Attributes
```json
{
  "name": "San Francisco Bay",
  "geomorphotype": "Barrier Estuary",
  "mouth_length_km": 12.5,
  "bay_length_km": 97.2,
  "complexity_index": 0.13,
  "tectonic_setting": "trailing",
  "size_category": "Very Large",
  "confidence": 0.95,
  "lat": 37.8,
  "lon": -122.4
}
```

### Geomorphotype Classification
1. **LSE** (Large Shallow Estuary): 76 systems (28%)
2. **Rocky Bay**: 72 systems (27%)
3. **Barrier Estuary**: 58 systems (21%)
4. **Sandy Bay**: 53 systems (20%)
5. **Funnelled**: 12 systems (4%)

### Tectonic Settings
- **Collision**: 147 systems (54%) - Active plate boundaries
- **Trailing**: 76 systems (28%) - Passive margins
- **Marginal**: 48 systems (18%) - Back-arc basins

### Size Categories
Based on mouth width:
- **Medium**: <5 km
- **Large**: 5-20 km
- **Very Large**: 20-50 km
- **Mega**: >50 km

### Use Cases
- Quantitative morphometry
- Size classification and comparisons
- Tectonic context analysis
- Enrichment of Dürr base layer (spatial join)

---

## 💧 Layer 3: GlobSalt Salinity (Ecological Layer)

### Description
River and estuary salinity zones based on 15 million water quality observations aggregated by basin.

### Data Source
- **File**: `data/processed/salinity_zones.geojson`
- **Processor**: `scripts/process_globsalt.py`
- **Reference**: GlobSalt v2.0 (Moyano Salcedo et al., 2025)

### Features
- **Basins**: 10,000-50,000 with salinity data
- **Geometry**: Polygon basins (HydroATLAS) or aggregated points
- **Coverage**: Global river and estuary systems

### Attributes
```json
{
  "HYBAS_ID": 5080613680,
  "salinity_mean": 2.34,
  "salinity_median": 2.10,
  "salinity_std": 0.87,
  "salinity_min": 0.50,
  "salinity_max": 4.20,
  "salinity_zone": "oligohaline",
  "zone_color": "#67a9cf",
  "n_records": 247
}
```

### Salinity Zones (Venice System)
1. **Freshwater** (<0.5 ppt): True rivers
2. **Oligohaline** (0.5-5 ppt): **Head of tide** ⭐ Most interesting
3. **Mesohaline** (5-18 ppt): Upper estuary
4. **Polyhaline** (18-25 ppt): Middle estuary
5. **Euhaline** (25-35 ppt): Lower estuary/marine
6. **Hyperhaline** (>35 ppt): Hypersaline systems

### Color Scheme
```javascript
Freshwater:  #2166ac  // Dark blue
Oligohaline: #67a9cf  // Medium blue
Mesohaline:  #d1e5f0  // Light blue
Polyhaline:  #fddbc7  // Light orange
Euhaline:    #ef8a62  // Orange
Hyperhaline: #b2182b  // Red
```

### Scientific Significance
- **Tidal Freshwater Zones** (oligohaline): Critical for GHG emissions
- **Salinity Gradients**: Ecological diversity indicators
- **Saltwater Intrusion**: Climate change impacts

### Use Cases
- Ecological zonation mapping
- Tidal influence extent
- GHG emissions research
- Climate change studies (saltwater intrusion)

---

## 🏞️ Layer 4: HydroSHEDS Rivers & Basins

### Description
Global river network and watershed boundaries from HydroSHEDS RiverATLAS v1.0, filtered to coastal systems.

### Data Source
- **Files**: 
  - `data/processed/rivers_coastal.gpkg` (LineStrings)
  - `data/processed/basins_coastal_lev06.gpkg` (Polygons)
- **Processor**: `scripts/compress_hydrosheds.py`
- **DOI**: 10.5067/9SQ1S6VFQQ20

### Features
- **River Reaches**: 500,000-1,000,000 coastal segments
- **Basins**: 10,000-50,000 Level 6 watersheds
- **Geometry**: LineString (rivers), Polygon (basins)
- **Coverage**: Global coastal zones

### Attributes (Rivers)
```json
{
  "HYRIV_ID": 40000001,
  "NEXT_DOWN": 40000002,
  "MAIN_RIV": 40000000,
  "ORD_STRA": 6,
  "ele_mt_uav": 245.8,
  "run_mm_cyr": 450.2
}
```

### Attributes (Basins)
```json
{
  "HYBAS_ID": 5080613680,
  "NEXT_DOWN": 5080613681,
  "SUB_AREA": 1245.6,
  "dis_m3_pyr": 8.5e9,
  "for_pc_sse": 45.2,
  "urb_pc_sse": 12.3
}
```

### Scientific Thresholds (Applied During Processing)
- **Minimum Stream Order**: 4 (significant rivers)
- **Maximum Elevation**: 100 m (tidal influence zone)
- **Minimum Discharge**: 10 m³/s (meaningful freshwater input)

### Use Cases
- River network visualization
- Watershed delineation
- Hydrological modeling
- Link to salinity data (via HYBAS_ID)
- Discharge and runoff analysis

---

## 🌊 Layer 5: GCC Coastal Characteristics (Optional)

### Description
High-resolution coastal attributes including wave climate, tidal range, erosion rates, and human impacts.

### Data Source
- **File**: `data/processed/gcc_coastal_characteristics.geojson`
- **Processor**: `scripts/process_gcc.py` (planned)
- **Reference**: Athanasiou, P. et al. (2024). Global Coastal Characteristics
- **DOI**: 10.5281/zenodo.8200199

### Features
- **Segments**: ~10,000 near estuaries (filtered from 728,088 global)
- **Geometry**: Point (coastal transects ~1 km resolution)
- **Coverage**: Global coastlines near estuaries

### Attributes
```json
{
  "id": "BOX_N38W076_0001",
  "lon": -76.25,
  "lat": 38.85,
  "tidal_range_m": 0.8,
  "wave_height_p50_m": 0.6,
  "wave_height_p95_m": 1.8,
  "storm_surge_100yr_m": 2.3,
  "nearshore_slope": 0.002,
  "erosion_rate_m_yr": 0.15,
  "pop_10km": 125000,
  "infrastructure_score": 145
}
```

### Hydrodynamic Parameters
- **Tidal Range**: Mean high water - mean low water (m)
- **Wave Height**: p50 (median), p95 (95th percentile) in meters
- **Storm Surge**: 100-year return period water level (m)
- **Nearshore Slope**: Coastal gradient

### Human Impact Indicators
- **Population**: Within 1, 5, 10 km buffers
- **Infrastructure**: Roads, railways, ports, airports count
- **GDP**: Economic indicators (PPP USD 2017)

### Use Cases
- **Hydrodynamic Classification**: Wave vs. tide dominated
- **Risk Assessment**: Storm surge exposure, erosion vulnerability
- **Human Impact**: Population pressure, development intensity
- **Climate Adaptation**: Vulnerability studies

---

## 🎮 Interactive Features

### Layer Controls
```javascript
// Checkbox toggles for each layer
☑️ 🗺️ Dürr Classification (Base - always on)
☐ 📐 Baum Morphometry
☐ 💧 GlobSalt Salinity  
☐ 🏞️ HydroSHEDS Rivers
☐ 🌊 GCC Coastal
```

### Display Modes Per Layer
Each layer can be displayed as:
- **Points**: Estuary/feature centroids
- **Polygons**: Watershed boundaries (where applicable)
- **Lines**: River reaches (HydroSHEDS only)

### Combined Popups
When multiple layers are active, clicking shows integrated information:

```
📍 Chesapeake Bay
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗺️ Dürr Classification
   Type: Coastal Plain (Tidal System)
   Basin Area: 165,760 km²

📐 Baum Morphometry
   Geomorphotype: Barrier Estuary
   Mouth Width: 35.2 km
   Bay Length: 298.5 km
   Tectonic: Trailing coast

💧 GlobSalt Salinity
   Zone: Oligohaline (Head of tide)
   Median Salinity: 3.2 ppt
   Observations: 1,247

🌊 GCC Coastal
   Tidal Range: 0.8 m
   Wave Height (mean): 0.6 m
   Storm Surge (100yr): 2.3 m
   Population (10km): 125,000
```

### Filtering Options
- **By Type**: Filter Dürr layer by geomorphotype
- **By Size**: Filter Baum layer by size category
- **By Salinity**: Filter GlobSalt by zone
- **By Stream Order**: Filter HydroSHEDS by order

---

## ⚡ Performance Optimization

### Layer Loading Strategy
1. **Base Layer** (Dürr): Loaded on page init
2. **Small Layers** (Baum): Loaded on toggle
3. **Large Layers** (HydroSHEDS): Lazy loaded, zoom-dependent
4. **Optional Layers** (GCC): User-triggered download

### Techniques Applied
- **Marker Clustering**: For point-heavy layers (>1000 features)
- **Geometry Simplification**: 0.01° tolerance (~1 km)
- **Zoom-based Rendering**: Show/hide based on zoom level
- **Gzip Compression**: Server-side for GeoJSON files
- **Progressive Loading**: Load visible extent first

### File Size Targets
- Individual layers: <5 MB (GeoJSON)
- Total page load: <15 MB
- Initial load (base layer): <5 MB

---

## 📚 Data Integration Workflow

### Spatial Joins
Layers can be joined for combined analysis:

```python
# Example: Enrich Dürr estuaries with Baum morphometry
durr = gpd.read_file('durr_estuaries.gpkg')
baum = gpd.read_file('baum_morphometry.gpkg')

# Nearest neighbor within 50km
enriched = durr.sjoin_nearest(baum, max_distance=50000, how='left')
```

### Common Join Keys
- **HYBAS_ID**: Links GlobSalt ↔ HydroSHEDS basins
- **Coordinates**: Spatial proximity joins (Dürr ↔ Baum ↔ GCC)
- **Name matching**: Fallback (unreliable, use spatial instead)

---

## 🎯 Use Case Examples

### 1. Find Large, Tide-Dominated Estuaries
- Enable: Dürr + Baum + GCC layers
- Filter: Baum size = "Very Large" or "Mega"
- Filter: GCC tidal_range > 4m
- Result: Macro-tidal mega-estuaries (e.g., Bay of Fundy)

### 2. Identify Vulnerable Estuaries
- Enable: Dürr + GCC layers
- Filter: GCC storm_surge_100yr > 3m AND pop_10km > 50000
- Result: High-risk population centers

### 3. Map Tidal Freshwater Zones
- Enable: GlobSalt + HydroSHEDS layers
- Filter: Salinity zone = "oligohaline"
- Result: Head-of-tide zones critical for GHG research

### 4. Compare Tectonic Settings
- Enable: Dürr + Baum layers
- Group by: Baum tectonic_setting
- Analyze: Size distributions across collision/trailing coasts

---

## 📖 References

1. **Dürr et al. (2011)**: Worldwide Typology of Nearshore Coastal Systems. *Estuaries and Coasts*, 34(3), 441-458. DOI: 10.1007/s12237-011-9381-y

2. **Baum et al. (2024)**: Large structural estuaries: Their global distribution and morphology. *Geomorphology*.

3. **Moyano Salcedo et al. (2025)**: GlobSalt v2.0: Global river salinity database.

4. **Lehner et al. (2022)**: HydroSHEDS v1.0. DOI: 10.5067/9SQ1S6VFQQ20

5. **Athanasiou et al. (2024)**: Global Coastal Characteristics. DOI: 10.5281/zenodo.8200199

---

**Status**: Architecture defined, layers ready for implementation  
**Next Step**: Process datasets → Integrate into map.js

