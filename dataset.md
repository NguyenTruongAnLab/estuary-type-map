---
layout: default
title: Dataset Downloads
nav_order: 4
---

# Dataset Downloads (Dữ liệu Tải Về)

## 📦 Processed Data (Ready to Use)

All processed datasets are available for download. These have been cleaned, classified, and are ready for analysis.

| Dataset | Format | Size | Description | Download |
|---------|--------|------|-------------|----------|
| **Tidal Basins (Level 7)** | GeoPackage | 380 MB | 16,189 tidal basins classified by Dürr typology | [Download](data/processed/tidal_basins_river_based_lev07.gpkg) |
| **Coastal Basins (Web)** | GeoJSON | 5.1 MB | Simplified for web display | [Download](data/web/tidal_basins_precise.geojson) |
| **Dürr Estuaries** | GeoJSON | 1.8 MB | 6,226 estuaries with typology | [Download](data/web/durr_estuaries.geojson) |
| **Baum Morphometry** | GeoJSON | 50 KB | 271 large estuaries with measurements | [Download](data/web/baum_morphometry.geojson) |
| **GlobSalt Stations** | GeoJSON | 330 KB | 2,500 salinity monitoring stations | [Download](data/web/globsalt_stations.geojson) |
| **DynQual Rivers** | GeoJSON | 350 KB | 1,660 river segments with hydrology | [Download](data/web/dynqual_river_characteristics.geojson) |
| **GCC Coastal** | GeoJSON | 500 KB | 1,252 coastal characteristic segments | [Download](data/web/gcc_coastal_characteristics.geojson) |

---

## 🗃️ Raw Data Sources

All analyses are based on peer-reviewed, open-access datasets:

| Dataset | Provider | DOI/Link | License | Purpose |
|---------|----------|----------|---------|---------|
| **GRIT v0.6** | Wortmann et al. 2025 | [Link](https://doi.org/10.5281/zenodo.8278616) | CC-BY 4.0 | Global river network (20.5M segments) |
| **HydroSHEDS BasinATLAS** | WWF / McGill | [Link](https://www.hydrosheds.org/products/basinatlas) | Free for non-commercial | Watershed boundaries (520K basins) |
| **Dürr et al. (2011)** | Dürr et al. | [DOI](https://doi.org/10.1007/s12237-011-9381-y) | Academic use | Estuary typology (6,226 systems) |
| **GlobSalt v2.0** | GEMS/Water, GRDC | [Link](https://gemstat.org/globsalt/) | Public Domain | Salinity monitoring (22,937 stations) |
| **DynQual** | Jones et al. 2023 | [DOI](https://doi.org/10.5194/essd-15-5287-2023) | CC-BY 4.0 | Global hydrology (10 km resolution) |
| **GCC** | Athanasiou et al. 2024 | [DOI](https://doi.org/10.5194/essd-16-3847-2024) | CC-BY 4.0 | Coastal characteristics (728K segments) |
| **OSM Water Layer** | Yamazaki et al. 2018 | [DOI](https://doi.org/10.1002/2017GL072874) | Open Data | Water polygon geometries |

---

## 📊 Machine Learning Models (Coming Soon)

ML models for salinity classification will be available after Phase 1 completion:

- **Hybrid Random Forest Models** (Coastal + Inland)
  - Trained on 270K GlobSalt measurements
  - Features: GRIT topology + DynQual + GCC
  - Predicts Venice System salinity classes
  - **Status**: 🔄 In Development
