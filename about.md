---
layout: default
title: About the Global Water Body Surface Area Atlas
---

**Status**: Educational/Research Project in Active Development  
**Last Updated**: October 12, 2025  
**Lead**: Nguyen Truong An

## ⚠️ Important Disclaimer

This is an **educational research project** created with AI assistance (GitHub Copilot). It demonstrates modern geospatial data processing techniques but is **NOT peer-reviewed scientific work**. Do not cite this as authoritative research.


## 🎯 Project Objectives

### Primary Goal

Create the world's **first comprehensive, polygon-based global water body surface area atlas** using direct measurement rather than statistical extrapolation. This enables precise calculations for biogeochemical modeling (GHG emissions, carbon fluxes, nutrient budgets).

### Why This Matters

**Previous Approach (Laruelle et al. 2025)**:
- Manually measured 735 estuaries
- Extrapolated to global estimate
- Result: ~734,000 km² ± 39,892 km²

**Our Approach (2025)**:
- Direct measurement of **20.5 million river reaches** globally
- Polygon-based calculation (not extrapolation)
- Higher spatial resolution and accuracy

### Specific Objectives

1. **Calculate precise surface areas** for all aquatic system types:
   - Rivers (non-tidal, tidal freshwater zone, saline reaches)
   - Estuaries (by geomorphology type: Delta, Fjord, Lagoon, etc.)
   - Lakes and reservoirs
   - Wetlands

2. **Implement O'Connor et al. (2022) Tidal Freshwater Zone framework** globally

3. **Provide open-access, reproducible methodology** - all code and data sources documented

4. **Enable next-generation biogeochemical models** with precise spatial data

5. **Compare results with Laruelle 2025** to validate methodology


## 🔬 Scientific Background

### What is an Estuary?

> *"A semi-enclosed coastal body of water that has a free connection with the open sea and within which sea water is measurably diluted with freshwater derived from land drainage."*  
> — Pritchard (1967)

### Why Classify Estuaries?

Different estuary types have fundamentally different characteristics that affect their biogeochemical function:

- **Sediment dynamics**: Deltas trap sediment, fjords export little
- **Mixing patterns**: Shallow vs stratified water columns
- **Residence time**: Hours (tidal channels) to months (lagoons)
- **Productivity**: Nutrient availability and light penetration

### The O'Connor et al. (2022) Framework

The **Tidal Freshwater Zone (TFZ)** is a distinct biogeochemical reactor:
- Salinity: 0-0.5 PSU (parts per thousand)
- Experiences tidal influence but remains freshwater
- High methane emissions (anaerobic sediments + organic matter)
- Critical for global GHG budgets


## 🛠️ Technology Stack

### Data Processing
- **Python 3.10+** with GeoPandas, Pyogrio, Pandas
- **GDAL/OGR** for format conversion
- **Spatial analysis** with Shapely, RTree

### Web Visualization
- **Leaflet.js** for interactive mapping
- **Chart.js** for statistics
- **GitHub Pages** for hosting

### Development Tools
- **VS Code** with Copilot AI assistance
- **Git/GitHub** for version control
- **Markdown** for documentation

## 📊 Dataset Overview

### Current Data Coverage

| Dataset | Features | Size | Status |
|---------|----------|------|--------|
| **GRIT v0.6** | 20.5M reaches | ~17 GB | ✅ Processing |
| **Dürr 2011** | 970 estuaries | 3 MB | ✅ Complete |
| **Baum 2024** | 271 large estuaries | 0.1 MB | ✅ Complete |
| **GlobSalt v2.0** | 270K stations | 1.2 GB | 🔄 Integrating |
| **OSM Water** | Millions polygons | 560 MB | ✅ Complete |
| **HydroSHEDS** | 73K rivers, 29K basins | 22 MB | ✅ Complete |

### Type Distribution (Dürr Dataset)
- **Delta**: 1,768 estuaries (29%)
- **Fjord**: 2,303 estuaries (38%)
- **Lagoon**: 510 estuaries (8%)
- **Coastal Plain**: 1,645 estuaries (27%)
- **Others**: Karst, tectonic, etc.

## 🎓 Intended Use Cases

### ✅ Appropriate Uses

- **Educational purposes**: Learning geospatial data processing
- **Methodology development**: Testing analytical workflows
- **Preliminary exploration**: Understanding global patterns
- **Code examples**: Reference for similar projects
- **Discussion starter**: Informing research proposals

### ❌ Inappropriate Uses

- **Policy decisions**: Not validated for regulatory use
- **Scientific publications**: Not peer-reviewed data
- **Engineering projects**: Requires professional validation
- **Commercial applications**: See license restrictions

---

## 🔍 Transparency & Limitations

### Known Limitations

1. **Not peer-reviewed**: Methodologies need scientific validation
2. **AI-assisted development**: Code may contain errors requiring expert review
3. **Data quality varies**: Depends on source dataset accuracy
4. **Processing incomplete**: Still calculating final global areas
5. **Simplified assumptions**: Real-world complexity not fully captured

### What We're Doing About It

- **Complete provenance tracking**: Every data source documented
- **Open-source code**: All processing scripts available for review
- **Validation against literature**: Comparing with Laruelle 2025, Dürr 2011
- **Continuous improvement**: Fixing issues as discovered (e.g., GRIT data integrity)
- **Clear documentation**: Honest about uncertainties and limitations

### Recent Fixes

**October 12, 2025**: Discovered and fixed critical GRIT v0.6 data integrity issue where coastal catchments were disconnected from river segments. Implemented spatial join workaround. [See full analysis](GRIT_DATA_ISSUE_ANALYSIS.md).

---

## 📚 Key References

1. **Dürr et al. (2011)**: "Worldwide Typology of Nearshore Coastal Systems" - *Estuaries and Coasts*
2. **Laruelle et al. (2025)**: "Continental shelves as a source of CO₂" - *Estuaries and Coasts*
3. **O'Connor et al. (2022)**: "The Tidal Freshwater Zone" - *Estuarine, Coastal and Shelf Science*
4. **Baum et al. (2024)**: "Structural estuaries" - Marine dataset
5. **GRIT v0.6 (2025)**: Global River Topology - Michel et al.
