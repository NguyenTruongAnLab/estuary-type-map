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

---

## 📝 Citation

If you use this data in your research, please cite:

### Primary Citation:
```
Nguyen, T. A. (2025). Global Water Body Surface Area Atlas v1.0. 
GitHub: https://github.com/NguyenTruongAnLab/estuary-type-map
```

### Method Paper (In Preparation):
```
Nguyen, T. A., et al. (2025). Direct Polygon-Based Measurement of Global 
Water Body Surface Areas for Biogeochemical Budgeting. [Journal TBD]
```

### Key Data Sources to Cite:
- **Dürr et al. (2011)**: Dürr, H. H., et al. (2011). Worldwide Typology of Nearshore Coastal Systems. *Estuaries and Coasts*, 34(3), 441-458.
- **GRIT**: Wortmann, M., et al. (2025). GRIT: Global River Network Topology. *Zenodo*.
- **HydroSHEDS**: Lehner, B., & Grill, G. (2013). Global river hydrography and network routing: Baseline data and new approaches. *Hydrological Processes*, 27(15), 2171-2186.

---

## 📜 License

### Our Data:
- **Processed datasets** (tidal basins, classifications): **CC-BY 4.0**
- **Source code**: **MIT License**
- **Website content**: **CC-BY 4.0**

### Third-Party Data:
Please respect original data licenses when using raw data sources (see table above).

---

## 🤝 Data Access & Support

### Download Issues?
- Files >100MB may take time to load
- Use Git LFS for large files: `git lfs pull`
- Contact: [your-email@institution.edu]

### Need Different Format?
We can provide data in additional formats:
- Shapefiles
- CSV (attribute tables)
- NetCDF (raster versions)
- PostgreSQL/PostGIS dumps

### Bulk Download:
```bash
# Clone entire repository with data
git clone https://github.com/NguyenTruongAnLab/estuary-type-map.git
cd estuary-type-map
git lfs pull  # Download large files
```

---

## 📈 Data Updates

| Version | Release Date | Changes |
|---------|--------------|---------|
| **v1.0** | Oct 2025 | Initial release: Tidal basins, Dürr classification, 6 datasets |
| **v1.1** | Q1 2026 (planned) | ML salinity predictions, TFZ delineation |
| **v2.0** | Q2 2026 (planned) | Surface area calculations, OSM water polygons |

Check the [GitHub Releases](https://github.com/NguyenTruongAnLab/estuary-type-map/releases) page for latest updates.

---

## 🌐 Web Services (Future)

We plan to offer:
- **REST API** for querying classifications
- **OGC WMS/WFS** for GIS integration
- **Python package** for programmatic access
- **STAC catalog** for geospatial metadata

Stay tuned for announcements!
