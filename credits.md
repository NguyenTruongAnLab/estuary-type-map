# 👥 Credits & Attribution

**Project**: Global Water Body Surface Area Atlas  
**Last Updated**: October 12, 2025

---

## 🎓 Project Lead & Supervision

**Nguyen Truong An**  
*Principal Investigator & Project Supervisor*

- **Affiliation**: [Your Institution/Lab]
- **Role**: Scientific direction, methodology design, validation oversight
- **Expertise**: Aquatic biogeochemistry, estuarine science, GHG budgets
- **Contact**: [GitHub Profile](https://github.com/NguyenTruongAnLab)

**Supervision Framework:**
- Defines project objectives and scientific requirements
- Reviews AI-generated code for accuracy and best practices
- Validates results against peer-reviewed literature
- Ensures data provenance and methodology transparency

---

## 🤖 AI-Assisted Development

This project was developed with **substantial AI assistance** using:

### GitHub Copilot
- **Code generation**: ~70-80% of code written with AI suggestions
- **Documentation**: AI-assisted markdown and comment writing
- **Debugging**: Error resolution and optimization suggestions
- **Learning tool**: Helped supervisor learn modern Python/GIS workflows

### Important Notes

**✅ What AI Did Well:**
- Rapid prototyping of data processing scripts
- Boilerplate code generation
- Format conversion utilities
- Documentation structure

**⚠️ What Required Human Oversight:**
- Scientific methodology validation
- Data integrity checks (e.g., discovering GRIT coastal catchment issue)
- Academic accuracy and references
- Critical debugging and logic verification

**Transparency Principle:**
> This project demonstrates that AI can accelerate scientific workflows **when supervised by domain experts**. It is not a replacement for scientific training or peer review.

---

## 📊 Data Sources & Original Authors

### Primary Datasets

#### 1. Dürr et al. (2011) — Estuary Typology
```
Dürr, H. H., Laruelle, G. G., van Kempen, C. M., Slomp, C. P., Meybeck, M., & Middelkoop, H. (2011).
Worldwide Typology of Nearshore Coastal Systems: Defining the Estuarine Filter of River Inputs to the Oceans.
Estuaries and Coasts, 34(3), 441-458.
DOI: 10.1007/s12237-011-9381-y
```
**What we use**: 7,057 estuarine catchment polygons with geomorphology classification

#### 2. GRIT v0.6 (2025) — Global River Topology
```
Michel, L., Hawker, L., Liu, Y., Slater, L., & Neal, J. (2025).
Global River Topology v0.6.
Zenodo.
DOI: 10.5281/zenodo.11072020
```
**What we use**: 20.5M river reaches with width data and topology

#### 3. GlobSalt v2.0 — Salinity Measurements
```
Linked Earth Data Portal
270,000+ stations with 15M salinity measurements (1980-2023)
```
**What we use**: Spatial salinity data for zone classification

#### 4. Baum et al. (2024) — Large Structural Estuaries
```
Baum, A., et al. (2024).
Structural estuaries morphometry dataset.
Marine database, 271 large estuaries worldwide
```
**What we use**: Validation data for major estuaries

#### 5. HydroSHEDS — Basin Boundaries
```
Lehner, B., & Grill, G. (2013).
Global river hydrography and network routing: baseline data and new approaches.
Hydrological Processes, 27(15), 2171-2186.
DOI: 10.5067/9SQ1S6VFQQ20
```
**What we use**: Watershed boundaries and river network

#### 6. OpenStreetMap Water Layer (Yamazaki et al. 2018)
```
Yamazaki, D., et al. (2018).
Development of a global ~90m water body map.
DOI: 10.1002/2017GL072874
```
**What we use**: High-resolution water polygon geometries

---

## 🛠️ Software & Tools

### Core Libraries
- **GeoPandas** (BSD License) - Spatial data processing
- **Pandas** (BSD License) - Tabular data manipulation
- **Shapely** (BSD License) - Geometric operations
- **GDAL/OGR** (MIT License) - Geospatial data translation
- **Pyogrio** (MIT License) - Fast I/O for GeoPackage

### Web Technologies
- **Leaflet.js** (BSD License) - Interactive mapping
- **Chart.js** (MIT License) - Data visualization
- **GitHub Pages** (GitHub Terms) - Website hosting

### Development Environment
- **Python 3.10+** (PSF License)
- **Visual Studio Code** (MIT License)
- **GitHub Copilot** (Subscription service)
- **Git** (GPL v2)

---

## 📚 Foundational Literature

This project builds upon decades of estuarine science:

### Estuarine Classification
- **Pritchard (1967)**: Classic estuary definition
- **Perillo (1995)**: *Geomorphology and Sedimentology of Estuaries*
- **Dyer (1997)**: *Estuaries: A Physical Introduction*

### Biogeochemical Frameworks
- **O'Connor et al. (2022)**: Tidal Freshwater Zone concept - *Estuarine, Coastal and Shelf Science*
- **Laruelle et al. (2025)**: Modern estuarine CO₂ budgets - *Estuaries and Coasts*
- **Bauer et al. (2013)**: Coastal ocean carbon fluxes - *Nature*

### Global Water Mapping
- **Allen & Pavelsky (2018)**: Global river width database - *Water Resources Research*
- **Pekel et al. (2016)**: Global surface water - *Nature*
- **Yamazaki et al. (2018)**: OSM water body map - *Geophysical Research Letters*

---

## 🙏 Acknowledgments

### Open Science Community
This project is only possible because of the open-access movement in science. Thank you to all researchers who:
- Publish data with permissive licenses
- Share code on GitHub/Zenodo
- Contribute to OpenStreetMap
- Develop open-source GIS tools

### GitHub Copilot
While AI cannot replace scientific expertise, it significantly accelerated development and helped teach modern workflows. This project demonstrates responsible AI-human collaboration in research.

---

## ⚖️ License & Usage

### Project Code
**MIT License** — Free to use, modify, and distribute with attribution

```
Copyright (c) 2025 Nguyen Truong An

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

See [LICENSE](LICENSE) file for full text.

### Data
All **source datasets** retain their original licenses (see above citations).  
**Derived products** from this project are shared under **CC BY 4.0**.

### Citation

If referencing this project for educational purposes:

```bibtex
@software{nguyen2025_water_atlas,
  author = {Nguyen, Truong An},
  title = {Global Water Body Surface Area Atlas for Biogeochemical Budgeting},
  year = {2025},
  url = {https://github.com/NguyenTruongAnLab/estuary-type-map},
  note = {Educational research project with AI assistance. Not peer-reviewed.}
}
```

**Important**: For scientific publications, cite the **original data sources** (Dürr 2011, GRIT 2025, etc.), not this project.

---

## 🔗 Connect

- **GitHub**: [NguyenTruongAnLab/estuary-type-map](https://github.com/NguyenTruongAnLab/estuary-type-map)
- **Issues**: [Report bugs or suggest features](https://github.com/NguyenTruongAnLab/estuary-type-map/issues)
- **Documentation**: [Technical docs](docs/TECHNICAL.md) | [Roadmap](docs/ROADMAP.md)

---

**Thank you for exploring this project!** 🌊
