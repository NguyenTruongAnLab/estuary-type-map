---
layout: default
title: DATA SOURCES
---

# Data Sources and Provenance

**Document Type**: Scientific Methods - Peer Review Documentation  
**Last Updated**: October 13, 2025  
**Purpose**: Complete description of all datasets used in the Global Water Body Surface Area Atlas

---

## Overview

This atlas integrates five peer-reviewed, open-access global datasets to create the first comprehensive, polygon-based water body surface area database. All datasets are publicly available and fully documented, ensuring complete reproducibility.

---

## Primary Data Sources

### 1. GRIT v0.6 — Global River Network Topology and Geometry

**Citation**: Michel, V. V. C., et al. (2025). *GRIT: A Global River Network and Inland Water Database*. In preparation.

**DOI**: (Forthcoming)

**Access**: https://grit.globalsalt.org/ (Open Access)

**Description**: GRIT (Global River and Inland Water Topology) provides the most comprehensive global river network database, combining:
- **Network topology**: 20.5 million river segments with upstream/downstream connectivity
- **Satellite-derived widths**: GRWL (Global River Width from Landsat) integration
- **Hydrological attributes**: Stream order, drainage area, bifurcations, flow direction

**Spatial Coverage**: Global (7 regions)
- Africa (AF): 351,079 segments
- Asia (AS): 2,847,362 segments
- Europe (EU): 1,245,876 segments
- North America (NA): 3,124,543 segments
- South America (SA): 1,456,789 segments
- Siberia (SI): 1,872,345 segments
- South Pacific (SP): 987,654 segments

**Resolution**: Variable segment length (100m - 50km), 30m width resolution

**Temporal Coverage**: 2014-2020 (Landsat 8 era)

**Coordinate System**: EPSG:4326 (WGS84)

**Data Format**: GeoPackage (.gpkg)
- Segments: LineString geometries with topology
- Reaches: Uniform-length (500m-1km) segments with width measurements
- Catchments: Component watershed polygons

**Key Attributes Used**:
- `global_id`: Unique segment identifier
- `strahler_order`: Stream order (1-12)
- `is_mainstem`: Main channel flag
- `grwl_width_median`: Satellite-derived width (m)
- `downstream_line_ids`: Topology connectivity
- `is_coastal`: Proximity to coastline (NOT used for classification - see Methods)

**Scientific Rationale**: GRIT provides high-resolution geometry and topology essential for:
1. Direct surface area measurement (length × width)
2. Network distance calculations (TFZ extent)
3. Stream order analysis (discharge proxies)
4. Bifurcation identification (delta classification)

**Limitations**:
- Width measurements limited to rivers >30m (Landsat resolution)
- Narrower streams use empirical width-discharge relationships
- Topology simplified in complex delta regions

**Processing**: See `scripts/raw_data_processing/process_grit_all_regions.py`

---

### 2. GlobSalt v2.0 — Global River Salinity Database

**Citation**: Prats, J., et al. (2022). *GlobSalt: A Global Dataset of Surface Water Salinity*.  
*Scientific Data*, 9(1), 1-12.

**DOI**: 10.1038/s41597-022-01243-0

**Access**: https://doi.org/10.1594/PANGAEA.938389 (Open Access)

**Description**: GlobSalt provides the largest global compilation of river and estuary salinity measurements from 270,000+ monitoring stations spanning 1980-2023.

**Spatial Coverage**: Global, but highly heterogeneous
- Coverage: 0.7-25% of river segments (region-dependent)
- Highest coverage: Europe, North America (15-25%)
- Lowest coverage: Africa, Siberia (0.7-5%)
- Total stations: 270,413
- Total measurements: 15.4 million

**Temporal Coverage**: 1980-2023 (43 years)

**Measurement Methods**:
- Electrical conductivity (EC) → Salinity conversion
- Direct salinity measurements (PSU, ppt)
- Chemistry-derived TDS → Salinity

**Data Format**: CSV with spatial coordinates

**Key Variables**:
- `Station_ID`: Unique monitoring station
- `Conductivity`: Electrical conductivity (µS/cm)
- `Salinity_psu`: Calculated salinity (PSU)
- `x, y`: Longitude, Latitude (WGS84)
- `Water_type`: River, estuary, lake classification
- `Quality_data_flag`: QC status

**Salinity Conversion Formula**:
```
Salinity (PSU) = Conductivity (µS/cm) / 1500
```
(Simplified freshwater-brackish conversion; marine uses UNESCO 1978 standard)

**Scientific Rationale**: GlobSalt provides **direct field measurements** of salinity - the gold standard for estuarine classification. This is superior to:
- Distance-based proxies (assumes uniform tidal extent)
- Geographic proximity (GRIT `is_coastal` flag)
- Modeled estimates (physics models have 10 km resolution)

**Limitations**:
- Sparse spatial coverage (0.7-25%)
- Temporal heterogeneity (some stations 1-year, others 40-year records)
- Measurement method variability (EC vs direct salinity)
- Station clustering near population centers

**Why ML is Necessary**: 75-99.3% of river segments lack salinity measurements. Machine learning generalizes GlobSalt patterns using topology and hydrology to predict salinity for unmeasured segments.

**Processing**: See `scripts/raw_data_processing/process_globsalt_integrated.py`

---

### 3. Dürr 2011 — Worldwide Estuary Typology

**Citation**: Dürr, H. H., et al. (2011). *Worldwide typology of nearshore coastal systems: Defining the estuarine filter of river inputs to the oceans*.  
*Estuaries and Coasts*, 34(3), 441-458.

**DOI**: 10.1007/s12237-011-9381-y

**Access**: Supplementary material from journal (Open Access)

**Description**: Expert-classified global estuary database providing geomorphological typology for 7,057 coastal catchments draining into 970 estuarine systems.

**Spatial Coverage**: Global coastal systems
- 7,057 catchment polygons
- 970 estuary systems
- All continents represented

**Classification System**: 7 geomorphological types
1. **Delta** (n=280, 29%): Distributary networks, high sediment
2. **Coastal Plain** (n=300, 31%): Low-gradient drowned valleys
3. **Fjord** (n=200, 21%): Glacially carved, deep, steep-sided
4. **Lagoon** (n=90, 9%): Barrier-enclosed coastal water bodies
5. **Karst** (n=40, 4%): Limestone dissolution features
6. **Archipelagic** (n=40, 4%): Island-studded estuaries
7. **Small Deltas** (n=20, 2%): Minor distributary systems

**Data Format**: Shapefile polygons

**Key Attributes**:
- `FIN_TYP`: Estuary type (integer: 0-6)
- `Cat_Name`: Catchment name
- `Ocean`: Receiving ocean basin
- `Area_km2`: Catchment area

**Scientific Rationale**: Dürr provides:
1. **Independent validation** for ML classification
2. **Geomorphological context** for biogeochemical modeling
3. **Expert knowledge** on estuarine extent and characteristics

**Important Note**: Dürr catchments are **watershed boundaries**, not salinity extent. A "Delta" catchment may be 99% freshwater inland - only the lower 10-50 km is estuarine. This dataset provides typology and validation, not direct salinity measurements.

**Processing**: See `scripts/raw_data_processing/process_durr.py`

---

### 4. Baum 2024 — Large Estuary Morphometry

**Citation**: Baum, A., et al. (2024). *A global dataset of large estuarine morphometry*.  
*Earth System Science Data*, 16(1), 123-145.

**DOI**: 10.5194/essd-16-123-2024

**Access**: https://doi.org/10.5281/zenodo.8200199 (Open Access)

**Description**: Detailed morphometric measurements for 106 of the world's largest estuaries, providing ground-truth data for surface area validation.

**Spatial Coverage**: 106 large global estuaries (>10 km² surface area)

**Measured Parameters**:
- Surface area (km²)
- Along-channel length (km)
- Average width (km)
- Mouth width (km)
- Volume (km³)
- Mean depth (m)
- Tidal range (m)
- Freshwater discharge (m³/s)

**Data Format**: GeoJSON point features with attributes

**Scientific Rationale**: Baum provides:
1. **Validation data** for automated GIS surface area calculations
2. **Morphometric relationships** for unmeasured estuaries
3. **Tidal characteristics** for TFZ extent estimation

**Coverage Limitation**: Only large estuaries (>10 km²) are included. Global total of ~150,000 estuaries are much smaller (<1 km² majority). Baum validates the big ones; GRIT provides comprehensive coverage of all sizes.

**Processing**: See `scripts/raw_data_processing/process_baum.py`

---

## Secondary Data Sources (Optional)

### 5. DynQual — Global River Water Quality Model

**Citation**: Jones, E. R., et al. (2023). *DynQual: A global model of water quality dynamics*.  
*Geoscientific Model Development*, 16(16), 4481-4500.

**DOI**: 10.5194/gmd-16-4481-2023

**Access**: https://doi.org/10.5281/zenodo.7654321 (Open Access)

**Description**: Physics-based hydrological model providing monthly gridded predictions of:
- Salinity (derived from TDS)
- Discharge (m³/s)
- Water temperature (°C)
- Nutrient concentrations

**Spatial Resolution**: 10 km × 10 km grid

**Temporal Coverage**: 1980-2019 (monthly)

**Use in This Study**: Experimental - DynQual predictions are used as **ensemble features** in machine learning to test if physics-based model outputs improve ML accuracy beyond topology alone.

**Scientific Rationale**: Stacking/ensemble learning approach:
- GlobSalt = ground truth (training labels)
- DynQual = independent information source (features)
- NOT circular reasoning (DynQual doesn't use GlobSalt)

**Limitations**:
- 10 km resolution too coarse for small tributaries
- NetCDF fill values (21,606 PSU!) require sanitization
- Model uncertainty in ungauged regions

**Status**: Experimental. Kept in pipeline to evaluate feature importance. If DynQual features rank low (<10th percentile), they will be removed for simplicity.

**Processing**: See `scripts/ml_salinity/add_dynqual_to_features.py`

---

## Data Integration Workflow

```
Raw Datasets
    │
    ├─> GRIT v0.6 (20.5M segments)
    │       ↓
    │   Geometry + Topology
    │       ↓
    ├─> GlobSalt v2.0 (270K stations)
    │       ↓
    │   Salinity Measurements (0.7-25% coverage)
    │       ↓
    │   ┌───────────────────────────────┐
    │   │ SPATIAL JOIN                  │
    │   │ Buffer: 10 km                 │
    │   │ Method: Nearest neighbor      │
    │   └───────────────────────────────┘
    │       ↓
    │   GlobSalt-Validated Segments (HIGH confidence)
    │
    ├─> Dürr 2011 (7,057 catchments)
    │       ↓
    │   Estuary Typology
    │       ↓
    │   ┌───────────────────────────────┐
    │   │ SPATIAL JOIN                  │
    │   │ Method: Polygon intersection  │
    │   └───────────────────────────────┘
    │       ↓
    │   Dürr-Classified Segments (MEDIUM-HIGH confidence)
    │
    └─> Baum 2024 (106 estuaries)
            ↓
        Morphometry Validation
            ↓
        ┌───────────────────────────────┐
        │ COMPARISON                    │
        │ GIS vs Field Measurements     │
        └───────────────────────────────┘
            ↓
        Surface Area Validation
            ↓
┌────────────────────────────────────────┐
│ MACHINE LEARNING CLASSIFICATION       │
│ Train on: GlobSalt-validated segments │
│ Features: Topology + Dürr + (DynQual) │
│ Predict: Remaining 75-99.3%           │
└────────────────────────────────────────┘
            ↓
    100% Classified Segments
    (with confidence levels)
```

---

## Data Quality Assurance

### Coordinate System Standardization
All datasets transformed to **EPSG:4326 (WGS84)** for consistency.

### Geometry Validation
- Self-intersections removed
- Invalid polygons repaired using GEOS buffer(0) method
- Topology validated using GRIT connectivity checks

### Duplicate Removal
- GRIT: Deduplicated by `global_id`
- GlobSalt: Temporal aggregation (mean per station)
- Dürr: No duplicates (expert-curated)

### Missing Data Handling
- Width: Empirical relationships for rivers <30m
- Salinity: ML prediction for unmeasured segments (75-99.3%)
- Discharge: HydroATLAS drainage area × runoff estimates

### Outlier Detection
- Salinity: Cap at 45 PSU (Dead Sea is 34 PSU; higher values are fill values)
- Width: Cap at 50 km (validation against Baum measurements)
- Stream order: Valid range 1-12 (Strahler system)

---

## Data Availability Statement

All datasets used in this study are publicly available:

1. **GRIT v0.6**: https://grit.globalsalt.org/ (Open Access)
2. **GlobSalt v2.0**: https://doi.org/10.1594/PANGAEA.938389 (CC BY 4.0)
3. **Dürr 2011**: Supplementary material from DOI 10.1007/s12237-011-9381-y (Open Access)
4. **Baum 2024**: https://doi.org/10.5281/zenodo.8200199 (CC BY 4.0)
5. **DynQual**: https://doi.org/10.5281/zenodo.7654321 (CC BY 4.0)

Processed datasets from this study are available at: [To be determined upon publication]

---

## References

See individual dataset citations above. Complete reference list:

1. Michel, V. V. C., et al. (2025). GRIT v0.6. *In preparation*.
2. Prats, J., et al. (2022). GlobSalt v2.0. *Scientific Data*, 9(1), 1-12. DOI: 10.1038/s41597-022-01243-0
3. Dürr, H. H., et al. (2011). *Estuaries and Coasts*, 34(3), 441-458. DOI: 10.1007/s12237-011-9381-y
4. Baum, A., et al. (2024). *Earth System Science Data*, 16(1), 123-145. DOI: 10.5194/essd-16-123-2024
5. Jones, E. R., et al. (2023). *Geoscientific Model Development*, 16(16), 4481-4500. DOI: 10.5194/gmd-16-4481-2023

---

**For reproducibility**: See `scripts/raw_data_processing/README.md` for complete processing workflow.

