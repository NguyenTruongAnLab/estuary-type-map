# 🌊 Global Estuary Type Map

An interactive web mapping framework for visualizing world estuaries classified by geomorphological shape types. This project uses open-access scientific datasets from Dürr et al. (2011), Baum et al. (2024), and optionally Athanasiou et al. (2024) for coastal characteristics.

## 🗺️ Live Demo

Visit the interactive map: [https://nguyentruonganlab.github.io/estuary-type-map/](https://nguyentruonganlab.github.io/estuary-type-map/)

## 📊 Features

- **Interactive Global Map**: Explore estuaries worldwide using Leaflet.js mapping library
- **Geomorphological Classification**: Filter estuaries by shape type:
  - **Delta**: River-dominated, sediment-rich formations
  - **Fjord**: Glacially carved, deep narrow inlets
  - **Lagoon**: Coastal water bodies separated by barrier islands
  - **Ria**: Drowned river valleys
  - **Coastal Plain**: Wide, shallow estuaries on flat coastal areas
  - **Bar-Built**: Formed behind barrier islands or spits
  - **Tectonic**: Formed by geological faulting or subsidence

- **Sidebar Legend**: Scientific definitions for each estuary type with academic references
- **Interactive Popups**: Click any estuary marker to view detailed information including:
  - Name and location
  - Geomorphological classification
  - Area (km²)
  - Depth (m)
  - Associated rivers
  - Scientific description

- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 🔬 Scientific Background

### What is an Estuary?

An estuary is a partially enclosed coastal body of water where freshwater from rivers meets and mixes with saltwater from the ocean. Estuaries are among the most productive ecosystems on Earth, serving as critical habitats for diverse species and providing important ecosystem services.

### Geomorphological Classification

This project uses a geomorphological classification system based on the physical shape and formation processes of estuaries, as outlined in recent scientific literature. The classification helps understand:

- **Formation processes**: How the estuary was created (glaciation, river deposition, tectonic activity, etc.)
- **Physical characteristics**: Depth, width, sediment composition
- **Hydrodynamic behavior**: Mixing patterns, circulation, tidal influence
- **Ecological implications**: Habitat types, productivity patterns

## 📚 Data Sources & Scientific Attribution

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

Because the GCC_geophysical.csv file is >200MB, it is **not included** in this repository.  
To use GCC data enrichment:
1. Download the latest GCC geophysical CSV from [Zenodo GCC Download](https://zenodo.org/records/11072020/files/GCC_geophysical.csv?download=1)
2. Place it in `data/GCC-Panagiotis-Athanasiou_2024/`
3. The processing pipeline can be extended to extract and join coastal attributes for estuary polygons

### Large Structural Estuaries (Validation/Enrichment)

**Baum, M.J., Schüttrumpf, H., & Siemes, R.W. (2024)**  
*Large structural estuaries: Their global distribution and morphology.*  
**Geomorphology**, supplementary data.

This dataset provides morphometric data (width, length, geomorphotype) for 271 large embayments globally, used to enrich the primary Dürr dataset.

### Validation and Context

_Note: Laruelle et al. (2025) "A global classification of estuaries based on their geomorphological characteristics" (Estuaries and Coasts) is used solely for validation and global area statistics. No shape, polygon, or direct attribute data is sourced from this study._

### Supporting Scientific References


**Pritchard, D.W. (1967)**  
*What is an estuary: physical viewpoint.*  
In G.H. Lauff (Ed.), **Estuaries** (pp. 3-5). AAAS Publication 83.

**Dalrymple, R.W., Zaitlin, B.A., & Boyd, R. (1992)**  
*Estuarine facies models: conceptual basis and stratigraphic implications.*  
**Journal of Sedimentary Research**, 62(6), 1130-1146.

**Perillo, G.M.E. (1995)**  
*Definitions and geomorphologic classifications of estuaries.*  
In G.M.E. Perillo (Ed.), **Geomorphology and Sedimentology of Estuaries** (pp. 17-47). Elsevier.

## 🛠️ Technical Implementation

### Technologies Used

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Mapping Library**: [Leaflet.js](https://leafletjs.com/) v1.9.4
- **Data Format**: GeoJSON
- **Data Processing**: Python 3.x
- **Hosting**: GitHub Pages (static site)
- **Base Map**: OpenStreetMap tiles

### Project Structure

```
estuary-type-map/
├── index.html              # Main HTML page
├── css/
│   └── style.css          # Custom styles
├── js/
│   └── map.js             # Map functionality and interactivity
├── data/
│   ├── estuaries.geojson  # GeoJSON data file with estuary locations
│   ├── Worldwide-typology-Shapefile-Durr_2011/
│   │   ├── typology_catchments.shp  # Primary source data
│   │   └── typology_coastline.shp
│   ├── Large-estuaries-Baum_2024/
│   │   └── Baum_2024_Geomorphology.csv
│   └── GCC-Panagiotis-Athanasiou_2024/
│       └── GCC_geophysical.csv  # Optional, not included (>200MB)
├── scripts/
│   └── process_estuary_data.py  # Python script for data processing
├── docs/                  # Additional documentation
└── README.md              # This file
```

### Data Processing

The Python script `scripts/process_estuary_data.py` processes real estuary data from open-access sources:

```bash
# Install dependencies
pip install geopandas pandas pyproj

# Process data
python3 scripts/process_estuary_data.py
```

This script:
1. Reads Dürr et al. (2011) shapefile with ~6,200 estuary catchments
2. Filters and selects representative estuaries for visualization
3. Enriches with Baum et al. (2024) morphometry data where available
3. Generates a GeoJSON file for web mapping with complete provenance metadata
4. Validates data structure and completeness

All data sources are properly attributed with DOIs and citations in the output GeoJSON.

### Map Features Implementation

**Filtering System**:
- Dynamic checkboxes for each estuary type
- "All Types" master filter
- Real-time marker updates without page reload

**Visual Design**:
- Color-coded markers by estuary type
- Custom popup styling with detailed information
- Responsive sidebar with scientific definitions
- Professional gradient header and footer

**Interactive Elements**:
- Click markers for detailed popup information
- Pan and zoom to explore specific regions
- Sidebar scrolling for definitions and references

## 🚀 Local Development

### Prerequisites

- Python 3.x (for data processing)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Local web server (optional but recommended)

### Running Locally

1. Clone the repository:
```bash
git clone https://github.com/NguyenTruongAnLab/estuary-type-map.git
cd estuary-type-map
```

2. Process the data (if needed):
```bash
python3 scripts/process_estuary_data.py
```

3. Serve the site locally:

**Option A: Python HTTP Server**
```bash
python3 -m http.server 8000
```
Then visit: `http://localhost:8000`

**Option B: Node.js HTTP Server**
```bash
npx http-server
```

**Option C: VS Code Live Server**
- Install "Live Server" extension
- Right-click `index.html` and select "Open with Live Server"

### Testing

Open the map in your browser and verify:
- [ ] Map loads correctly with all markers visible
- [ ] Sidebar displays all estuary types with correct counts
- [ ] Filter checkboxes show/hide markers appropriately
- [ ] Clicking markers opens popups with correct information
- [ ] Responsive design works on different screen sizes
- [ ] All scientific definitions are displayed correctly
- [ ] References section is complete and formatted properly

## 📖 Usage Guide

### For Researchers

This tool can be used for:
- **Comparative studies**: Analyze distribution patterns of different estuary types
- **Educational purposes**: Demonstrate geomorphological classification concepts
- **Data visualization**: Present estuary data in publications and presentations
- **Preliminary analysis**: Identify case study locations for field research

### For Educators

- Use as a teaching tool for coastal geomorphology courses
- Demonstrate real-world applications of classification systems
- Interactive exploration of global coastal environments
- Reference scientific definitions and primary literature

### For Students

- Learn about estuary types and their characteristics
- Explore global distribution of coastal systems
- Access scientific references for research papers
- Understand connection between geomorphology and ecology

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- **Data Enhancement**: Add more estuaries from additional sources
- **Feature Development**: Implement additional filters (by size, region, etc.)
- **Scientific Content**: Expand definitions with more references
- **Visualization**: Add charts, statistics, or comparative views
- **Accessibility**: Improve screen reader support and keyboard navigation

### For Contributors and AI Agents

**📋 Copilot Instructions**: If you're using GitHub Copilot or other AI assistants, please review the comprehensive project guidelines in [`.github/copilot-instructions.md`](.github/copilot-instructions.md). This document covers:
- Project mandate and scientific principles
- Data sources and provenance requirements
- Code standards and documentation guidelines
- Common tasks and workflows
- Testing and validation procedures

To contribute:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add YourFeature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available for educational and research purposes. Please cite the original data sources when using this tool in academic work:

- **Primary data**: Dürr et al. (2011) - DOI: 10.1007/s12237-011-9381-y
- **Supplementary data**: Baum et al. (2024)
- **Optional enrichment**: Athanasiou et al. (2024) - DOI: 10.5281/zenodo.8200199

## 🙏 Acknowledgments

- **Dr. Hans H. Dürr**, **Dr. Goulven G. Laruelle**, and colleagues for the comprehensive worldwide typology of nearshore coastal systems
- **Dr. Moritz J. Baum** and colleagues for large structural estuaries morphometry data
- **Dr. Panagiotis Athanasiou** and colleagues for the Global Coastal Characteristics database
- **OpenStreetMap contributors** for base map tiles
- **Leaflet.js team** for the excellent mapping library
- **GitHub Pages** for free hosting of this educational resource

## 📧 Contact

For questions, suggestions, or collaboration opportunities:
- Open an issue on GitHub
- Repository: [https://github.com/NguyenTruongAnLab/estuary-type-map](https://github.com/NguyenTruongAnLab/estuary-type-map)

## 🔄 Updates

**Current Version**: 2.0.0 (Real Data Implementation)

**Changes in v2.0.0:**
- ✅ Replaced sample/fake data with real open-access datasets
- ✅ Primary data from Dürr et al. (2011) worldwide typology (~6,200 estuaries)
- ✅ Enriched with Baum et al. (2024) large estuary morphometry
- ✅ Full provenance tracking in GeoJSON output
- ✅ Proper scientific attribution with DOIs

Future updates will include:
- Integration of GCC (Athanasiou et al. 2024) coastal attributes
- Regional extrapolation pipeline (similar to Laruelle et al. methodology)
- Advanced filtering by basin area, ocean, region
- Time-series data on estuary changes
- Enhanced morphometric analysis

---

**Citation**: If you use this tool in your research, please cite:
```
NguyenTruongAnLab. (2024). Global Estuary Type Map: Interactive visualization of world estuaries 
by geomorphological classification. GitHub. https://github.com/NguyenTruongAnLab/estuary-type-map
```

And the primary data sources:
```
Dürr, H.H., et al. (2011). Worldwide typology of nearshore coastal systems: defining the 
estuarine filter of river inputs to the oceans. Estuaries and Coasts, 34(3), 441-458. 
DOI: 10.1007/s12237-011-9381-y
```

