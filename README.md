# 🌊 Project: Global Water Body Surface Area Atlas for Biogeochemical Budgeting

**The comprehensive, polygon-based inventory of global aquatic surface areas for precise greenhouse gas, carbon, and nutrient budget calculations**

*A scientific initiative supervised by Nguyen Truong An with AI agent assistance*

---

## 📋 Vision Statement

This project creates the world's **first direct, polygon-based global water body atlas** that provides precise surface area calculations for all aquatic system types, enabling the next generation of high-resolution estimates for global carbon, nutrient, and greenhouse gas (GHG) budgets.

Unlike previous studies that relied on extrapolation methods or coarse-resolution grids due to technological limitations, **Project** leverages modern high-resolution datasets (OpenStreetMap water polygons, salinity grids, HydroSHEDS) and AI-assisted processing to **calculate actual water surface areas from vector geometries** rather than statistical estimates.


## 🗺️ Live Interactive Atlas

Explore the global water body database:

🌐 **[Launch Interactive Map →](https://nguyentruonganlab.github.io/estuary-type-map/)**

### Features:
- Multi-layer visualization (rivers, estuaries, basins, salinity zones)
- Filter by water body type and salinity zone
- Real-time statistics and interactive exploration
- Downloadable datasets (GeoPackage, GeoJSON, CSV)

## 📊 Features

- **Interactive Global Map**: Explore estuaries worldwide using Leaflet.js mapping library
- **Full Global Coverage**: All ~6,200+ estuaries from Dürr et al. (2011) dataset
- **Multiple Visualization Modes**:
  - **📍 Estuary Points Mode**: View individual estuary locations as interactive markers
  - **🗺️ Basin Polygons Mode**: Display complete drainage basins as colored polygons
  - **🌐 Coastal Segments Mode**: View global coastlines colored by estuary type (8,400+ segments)
  
- **Geomorphological Classification (Corrected Dürr et al. 2011 Typology)**:
  - **NEW in v1.0.0**: 16,189 tidal basins using BasinATLAS Level 7 (0-300km from coast)
  - **Tidal systems (Type II)**: Wave/tide-dominated - Pink (4,666 basins, 28.8%)
  - **Small deltas (Type I)**: Small-medium river-dominated - Purple (4,036 basins, 24.9%)
  - **Fjords and fjaerds (Type IV)**: Glacially carved - Blue (3,516 basins, 21.7%)
  - **Lagoons (Type III)**: Barrier-protected systems - Orange (1,577 basins, 9.7%)
  - **Arheic (Type VII)**: Arid/arheic coasts - Cyan (1,218 basins, 7.5%)
  - **Large Rivers (Type Va)**: Major river systems - Light Purple (375 basins, 2.3%)
  - **Large Rivers + tidal deltas (Type Vb)**: Mekong, etc. - Dark Purple (227 basins, 1.4%)
  - **Karst (Type VI)**: Limestone karst systems - Yellow (153 basins, 0.9%)

- **Basin Polygon Visualization**: 
  - View complete watershed/drainage basins for each estuary
  - Interactive hover effects with highlighting
  - Same filtering and popup functionality as point mode
  - Optimized simplified geometries for web performance (2.8MB dataset)

- **Sidebar Legend**: Scientific definitions for each estuary type with academic references
- **Interactive Popups**: Click any estuary marker, basin polygon, or coastal segment to view detailed information including:
  - Name and location
  - Geomorphological classification (detailed typology)
  - Basin area (km²)
  - Sea/Ocean name
  - 
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 🔬 Scientific Motivation: Why This Project is Necessary

### The Critical Data Gap

Global budgets for greenhouse gases, carbon, and nutrients are fundamental to understanding Earth's climate and ecosystems. However, a **critical uncertainty in all current models is the lack of precise global water body surface area inventories**.

### Why Previous Studies Used Coarse Methods

**Dürr et al. (2011):**
- Used 0.5° catchment grids and coastline-length ratios ("Woodwell ratios")
- Estimated global estuarine area: **1.067 × 10⁶ km²**
- Method: Statistical extrapolation, not direct measurement
- Limitation: Map showed catchment areas, not actual water bodies

**Laruelle et al. (2025):**
- Manually measured/compiled 735 individual estuaries
- Developed regional extrapolation formula: `S = a(N^b)/(N+b)`
- Estimated global estuarine area: **733,801 ± 39,892 km²**
- Still relied on extrapolation, not direct polygon calculation

**From Laruelle et al. (2025):**
> *"An autonomous algorithm able to systematically determine estuarine areas over a continuous stretch of coastline has not yet been developed... Performing such a task manually by individually determining the limits of each system through GIS would be a daunting task"*

### 2025 Scientific & Technological Breakthrough
This project is now possible due to a confluence of recent, game-changing advancements:

✅ State-of-the-Art Hydrographic Networks: The release of Global River Topology (GRIT) in 2025 provides a 30m resolution network based on a superior DEM (FABDEM). For the first time, this allows for the global mapping of complex features like bifurcations, multi-threaded channels, and deltas.

✅ High-Precision Water Geometry: The maturity of OpenStreetMap (OSM) provides globally extensive, high-resolution vector polygons of actual water bodies, essential for direct surface area calculation.

✅ Advanced Scientific Frameworks: The Tidal Freshwater Zone (TFZ) framework (O'Connor et al., 2022) provides a clear, physically-based methodology for classifying river reaches into distinct biogeochemical reactors, allowing for more nuanced budget calculations.

✅ Modern Computational Power: AI-assisted coding, cloud computing, and modern GIS libraries (GeoPandas, Pyogrio) make processing terabyte-scale global datasets feasible.

## 🎯 Core Objectives

### Objective 1: Definitive Water Body Surface Area Database

Calculate precise surface areas (±uncertainty) for all global aquatic systems:

**Rivers** (3-zone classification per O'Connor et al. 2022):
- Non-tidal freshwater zone (upstream of tidal influence)
- **Tidal Freshwater Zone (TFZ):** 0 < salinity < 0.5 PSU
- **Saline reach:** salinity ≥ 0.5 PSU

**Estuaries** (by geomorphology AND salinity zone):
- Delta systems
- Tidal systems
- Lagoons
- Fjords
- Each subdivided into TFZ vs. saline portions

**Lakes & Reservoirs:**
- Natural lakes (HydroLAKES)
- Anthropogenic reservoirs (GRanD)
- Permanent vs. seasonal differentiation

**Wetlands:**
- Mangroves (Global Mangrove Watch)
- Tidal marshes
- Freshwater wetlands
- Peatlands

**Method:** Direct surface area calculation from OSM vector polygons, which are classified and contextualized using the GRIT (30m) hydrographic network and GlobSalt salinity data. This is a direct measurement, not extrapolation.

### Objective 2: Interactive Global Atlas

Professional, research-grade web platform featuring:
- Multi-layer visualization with filtering by type/zone/region
- Salinity-zone overlays (non-tidal/TFZ/saline)
- Time-series animations (1980-2023 salinity changes)
- River system highlighting (e.g., entire Mekong Delta)
- Real-time statistics and Plotly.js charts
- Downloadable filtered datasets (GeoPackage, CSV)

### Objective 3: Biogeochemical Budget Calculators

Enable precise quantification:

```
Global GHG Flux = Σ (Surface_Area_type,region × Emission_Rate_type,region ± σ)
```

- **GHG emissions:** CO₂, CH₄, N₂O by water body type
- **Organic carbon:** DOC/POC inputs, processing, burial, emission
- **Nutrient pollution:** N and P loads by source (agriculture, urban, natural)
- **Scenario modeling:** Climate change, land-use impacts

### Objective 4: Open Science & Reproducibility

- All processing code on GitHub
- Complete data provenance tracking
- Uncertainty quantification at every step
- Replication guide for researchers
- Regular updates and community contributions

---

## 📊 Key Features & Innovations

### What Makes This Groundbreaking

**1. First Direct Polygon-Based Global Database**
- Not extrapolation or statistical estimation
- Actual water surface geometries from OSM vector data
- Validated against literature (Laruelle, Dürr, regional databases)

**2. Full Vector Precision (Not 90m Raster)**
- Uses OSM vector polygons (variable resolution, typically 1-5m for mapped features)
- NOT the 90m rasterized version (which underestimates small rivers)
- Captures small tributaries and headwater streams

**3. Salinity-Zone Classification (Novel Global Application)**
- Implements O'Connor et al. (2022) Tidal Freshwater Zone framework globally
- Empirical boundary detection using 1980-2023 salinity grids
- Distinguishes biogeochemically-distinct zones

**4. Complete Water Body Typology**
- Rivers, estuaries, lakes, reservoirs, wetlands
- Goes beyond Laruelle (estuaries only)
- Comprehensive for global biogeochemical modeling

**5. Hybrid Data Synthesis**
- Water geometry: OSM vector polygons (Geofabrik/Yamazaki)
- Basin context: HydroSHEDS (HydroBASINS, HydroATLAS)
- Salinity boundaries: Monthly grids (1980-2023)
- Type classification: Dürr 2011, Baum 2024

**6. GitHub-Compatible Delivery**
- All files compressed <200MB per layer
- GeoPackage format for GIS interoperability
- CSV statistics for spreadsheet users
- Open source code (Python, JavaScript)

---

## 📚 Data Sources & Scientific Attribution

| Dataset | Provider / Citation | Role in Project | Update Frequency |
|---------|-------------------|----------------|------------------|
| **GRIT v0.6** | Wortmann et al. (2025) | Backbone hydrography, all regimes | Annual |
| **Hydrography90m** | Amatulli et al. (2022) | Auxiliary microstreams | Static |
| **OSM Water Polygons (Geofabrik, Yamazaki)** | OSM | Waterbody geometry mask | Daily |
| **HydroLAKES, GRanD v3** | Messager/Lehner et al., 2025 | Lakes/reservoir polygons | Annual |
| **GSWE, SWOT, GlobSalt** | NASA, ESA, RS | Tidal/salinity/TFZ regime grids | Monthly |
| **Wetland Datasets** | GMW, JRC, ESA | Mangrove, marshes, peatlands polygons | Annual |

### Main Estuary Typology and Geometry

**Dürr, H.H., Laruelle, G.G., van Kempen, C.M., Slomp, C.P., Meybeck, M., & Middelkoop, H. (2011)**  
*Worldwide typology of nearshore coastal systems: defining the estuarine filter of river inputs to the oceans.*  
**Estuaries and Coasts**, 34(3), 441-458.  
DOI: [10.1007/s12237-011-9381-y](https://doi.org/10.1007/s12237-011-9381-y)

This comprehensive study provides the global framework for classifying estuaries based on their geomorphological characteristics. The dataset includes ~6,200 coastal cells with estuary typology linked to river basins.

### Coastal Attributes (Land Use, Slope, Elevation) — Optional Enrichment

**Athanasiou, P., van Dongeren, A., Giardino, A., Vousdoukas, M., Ranasinghe, R., & Kwadijk, J. (2024)**  
*Global Coastal Characteristics (GCC) Database.*  
DOI: [10.5281/zenodo.8200199](https://doi.org/10.5281/zenodo.8200199)


### Large Structural Estuaries (Validation/Enrichment)

**Baum, M.J., Schüttrumpf, H., & Siemes, R.W. (2024)**  
*Large structural estuaries: Their global distribution and morphology.*  
**Geomorphology**, supplementary data.

This dataset provides morphometric data (width, length, geomorphotype) for 271 large embayments globally, used to enrich the primary Dürr dataset.

### Primary Spatial Data Sources

| Dataset | Provider / Citation | Role in Project | Update Frequency |
|---------|-------------------|----------------|------------------|
| **OSM Water Polygons (Vector)** | Geofabrik / Yamazaki Lab | Primary water body geometry (full precision) | Daily / 2021 |
| **HydroBASINS** | Lehner & Grill (HydroSHEDS) | Watershed/basin boundaries | Periodic |
| **HydroATLAS** | Lehner et al. (HydroSHEDS) | Catchment attributes (land use, climate) | Periodic |
| **Salinity Grids** | GlobSalt (1980-2023) | Empirical zone boundary detection | Monthly |
| **Dürr 2011 Typology** | Dürr et al. (2011) | Estuary type classification | Static (2011) |
| **HydroLAKES** | Messager et al. (2016) | Lake identification | Periodic |
| **GRanD** | Lehner et al. (2011) | Reservoir database | Periodic |
| **Baum 2024** | Baum et al. (2024) | Large estuary morphometry validation | Static (2024) |

### Water Body Geometry (Primary Source)

**OpenStreetMap Water Features via Multiple Access Points:**

**Option 1: Geofabrik Regional Extracts (Recommended)**
- Source: https://download.geofabrik.de/
- Format: Shapefiles (pre-organized by continent/country)
- Update: Daily
- Layers: water (area polygons), waterways (river lines)
- Resolution: Variable OSM precision (typically 1-5m for mapped features)
- **Why chosen:** Full vector precision, daily updates, easy regional processing

**Option 2: Yamazaki Lab OSM Water Layer - Vector PBF**
- Source: http://hydro.iis.u-tokyo.ac.jp/~yamadai/OSM_water/
- Citation: Yamazaki et al. (2017), Geophysical Research Letters, DOI: 10.1002/2017GL072874
- License: CC-BY 4.0 (raster), ODbL 1.0 (vector)
- Format: PBF (original OSM vector data, pre-filtered for water features globally)
- Resolution: Variable OSM precision (NOT 90m raster!)
- **Why useful:** Single global file, pre-filtered for water tags

**Option 3: osmdata.openstreetmap.de**
- Source: https://osmdata.openstreetmap.de/data/water-polygons.html
- Update: Daily
- Use case: Global ocean/large water body polygons

### Basin Boundaries & Attributes

**HydroBASINS (Essential)**
- Purpose: Watershed delineation for all water bodies
- Why critical: Links water bodies to catchments, enables land-use impact modeling
- Cannot replace: OSM has no basin boundary data

**HydroATLAS (Highly Recommended)**
- Purpose: Pre-calculated catchment characteristics
- Attributes: Land use %, climate variables, topography, population, infrastructure
- Advantage: Saves processing raw climate/land-use rasters yourself

**HydroRIVERS (Supplementary)**
- Purpose: River network connectivity, discharge estimates
- Use: Fill gaps where OSM lacks width data, validate classifications
- Not primary source for: Water surface geometry (OSM better)


## 🛠️ Technical Implementation

### Technologies Used

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Mapping Library**: [Leaflet.js](https://leafletjs.com/) v1.9.4
- **Data Format**: GeoJSON
- **Data Processing**: Python 3.x
- **Hosting**: GitHub Pages (static site)
- **Base Map**: OpenStreetMap tiles

### Project Structure

### Data Processing Pipeline

The project uses a **modular, high-performance data pipeline** in Python, designed to handle terabyte-scale source data efficiently.

**Technologies:**
```bash
# Core libraries
pip install geopandas pyogrio fiona shapely pandas numpy
pip install xarray rasterio scipy scikit-learn tqdm
```

**Architecture:** Parallel Predicate Pushdown, enabling the filtering of massive datasets at the source before loading into memory.

**Run Complete Pipeline:**
```bash
# Process all datasets in sequence (~50-60 minutes total)
python scripts/process_all_datasets.py
```

**Or Process Individually:**
```bash
python scripts/process_durr.py          # Dürr 2011 typology (1-2 min)
python scripts/process_baum.py          # Baum 2024 morphometry (<1 min)
python scripts/process_globsalt.py      # Salinity zones (20-30 min)
python scripts/compress_hydrosheds.py   # HydroSHEDS rivers/basins (30-45 min)
```

**Processing Workflow:**
Each processor follows a standard pipeline:
1. **Load:** Read source data (shapefile, CSV, GeoPackage, NetCDF)
2. **Filter:** Apply scientific thresholds (e.g., coastal proximity, stream order)
3. **Transform:** 
   - Clean and validate attributes
   - Reproject to WGS84
   - Calculate derived fields (area, width, salinity zone)
4. **Simplify:** Reduce geometry complexity for web performance
5. **Export:**
   - GeoPackage (processed/, full resolution for GIS)
   - GeoJSON (web/, <5MB target, zoom-optimized)
   - Metadata JSON (provenance, schema, citations)
6. **Validate:** Verify structure and attribute completeness

**Current Processing Status:**
- ✅ **HydroSHEDS:** 73,410 rivers + 29,145 basins (41 min processing)
- ✅ **Dürr 2011:** 6,226 estuaries with full typology
- ✅ **Baum 2024:** 271 large estuary validation dataset
- ✅ **GlobSalt:** Salinity zone boundaries (monthly 1980-2023)
- 🔄 **OSM Water Polygons:** Planned (Phase 2)
- 🔄 **Salinity-based splitting:** Planned (Phase 2)

All data sources are properly attributed with DOIs and citations in the output GeoJSON metadata files.

### Map Features Implementation

**Visualization Modes**:
- **Points Mode**: Shows individual estuary locations as interactive markers (6,226 estuaries)
- **Basin Polygons Mode**: Displays complete drainage basin polygons for all estuaries
  - Simplified geometries (tolerance=0.05°) optimized for web performance
  - Interactive hover effects with highlighting
  - Click for detailed basin information
- **Coastal Segments Mode**: Shows global coastlines colored by estuary type (8,439 segments)
- Toggle between modes with one click

**Filtering System**:
- Dynamic checkboxes for each estuary type
- "All Types" master filter
- Real-time updates across all visualization modes without page reload

**Visual Design**:
- Updated color scheme matching scientific visualization standards:
  - Delta: Purple, Fjord: Orange, Lagoon: Brown, Ria: Pink
  - Coastal Plain: Blue, Bar-Built: Green, Tectonic: Red
- Custom popup styling with detailed information
- Responsive sidebar with scientific definitions
- Professional gradient header and footer

**Interactive Elements**:
- Click markers/polygons for detailed popup information
- Hover over basin polygons for highlighting effect
- Pan and zoom to explore specific regions
- Sidebar scrolling for definitions and references

## 🚀 Project Roadmap & Status

### Phase 1: Foundation — Classification Pipeline ✅ Nearing Completion

**Timeline:** Months 1-3  
**Status:** 90% Complete (ML pipeline running)

**Completed:**
- ✅ Process GRIT v0.6 (20.5M river segments, all 7 regions)
- ✅ Process Dürr 2011 typology (7,057 estuary catchments)
- ✅ Process Baum 2024 morphometry (106 large estuaries)
- ✅ Process GlobSalt v2.0 (270K salinity stations)
- ✅ Implement ML salinity prediction pipeline
- ✅ DynQual physics-based features integration
- 🔄 **IN PROGRESS**: ML training & prediction (1-2 hours remaining)

**Outputs:**
- `rivers_grit_segments_classified_{region}.gpkg` (7 files, foundation data)
- `rivers_grit_ml_classified_{region}.gpkg` (ML predictions, in progress)
- `durr_estuaries.geojson` (geomorphology reference)
- `baum_morphometry.geojson` (validation reference)
- Interactive map v0.2 (current)

**Critical Realization**:
- ✅ Segments classified (LineStrings)
- ❌ **BUT**: Lines don't have surface area!
- 🎯 **Next**: Convert to water body polygons (Phase 2)

---

### Phase 2: Surface Area Calculation ⚡ Next Priority (THE ULTIMATE OBJECTIVE!)

**Timeline:** Months 4-5 (Weeks 1-3 of implementation)  
**Status:** Design complete, implementation starting

**Approach**:
```
ML-classified segments (LineStrings with salinity)
    +
GRIT reaches (width data from GRWL satellite)
    +
OSM water polygons (actual water body geometries)
    ↓
INTERSECT & CALCULATE
    ↓
Water body polygons with surface areas by classification!
```

**Tasks:**
- ⬜ **Week 1**: Load ML classifications + GRIT reaches with width
- ⬜ **Week 1**: Intersect with OSM water polygons (CRITICAL STEP!)
- ⬜ **Week 2**: Calculate areas by classification (Venice System, Dürr types)
- ⬜ **Week 2**: Handle missing width data (empirical relationships)
- ⬜ **Week 3**: Validate against literature (Baum, Laruelle)
- ⬜ **Week 3**: Generate global summary tables

**Outputs:**
- `water_polygons_classified_{region}.gpkg` (7 files, POLYGON geometries!)
- `summary_by_salinity_global.csv` (Venice System aggregation)
- `summary_by_geomorphology_global.csv` (Dürr types aggregation)
- `summary_combined_global.csv` (Salinity × Geomorphology)
- `validation_report.pdf` (vs. Baum & Laruelle)
- **Publication-ready results!**

**Key Innovation**:
- ✅ Uses **actual OSM water polygons** (not buffered lines)
- ✅ **Equal-area projection** (EPSG:6933) for accurate areas
- ✅ **ML-classified** (100% coverage, not just 0.7-25% GlobSalt)
- ✅ **Direct polygon measurement** (not statistical extrapolation)

---

### Phase 3: Classification Refinement & Analysis

**Timeline:** Months 6-8  
**Status:** Planned (after Phase 2 complete)

**Tasks:**
- ⬜ Implement waterbody_classification/ scripts
  - Venice System classification (by_salinity/)
  - Dürr type classification (by_geomorphology/)
  - Stream order classification (by_hydrology/)
  - Integrated multi-criteria classification
- ⬜ Calculate TFZ extents (O'Connor et al. 2022 framework)
- ⬜ Uncertainty quantification (confidence levels)
- ⬜ Regional variation analysis

**Outputs:**
- Classification framework implementation
- Uncertainty maps
- Regional comparison reports

---

### Phase 4: Complete Water Body Inventory

**Timeline:** Months 9-12  
**Status:** Planned

**Tasks:**
- ⬜ Add HydroLAKES (lakes)
- ⬜ Add GRanD (reservoirs)
- ⬜ Add wetlands (mangroves, marshes, peatlands)
- ⬜ Complete global statistics
- ⬜ Interactive map v1.0 with all layers

**Outputs:**
- Complete water body atlas
- Interactive map v1.0
- Final publication dataset
