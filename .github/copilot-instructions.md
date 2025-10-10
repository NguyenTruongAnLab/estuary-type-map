# 🌊 Global Estuary Type Map — Copilot AI Agent Instructions

## 📋 Project Mandate

### **Mission**
Create and maintain a fully transparent, reproducible global estuary mapping platform based only on real, scientifically-cited, open-access data sources.  
Visualize, analyze, and summarize the world's estuarine systems by geomorphological type at global scale, supporting future extensions for GHG and land-use studies.

---

## 🛰️ Repository Structure

### **data/**
- `Worldwide-typology-Shapefile-Durr_2011/`: Global estuary polygons/shapes (main type backbone)
- `GCC-Panagiotis-Athanasiou_2024/`: High-res coastal characteristics (attribute enrichment only)
- `Large-estuaries-Baum_2024/`: Large/structural estuary supplement (optional)
- `estuaries.geojson` / `estuaries.gpkg`: Final, ready-to-map, merged dataset

### **scripts/**
- `process_estuary_data.py`: All pipeline data handling and transformation
- `test_data.py`: Validation tests for generated GeoJSON data
- *(future: extrapolate_estuary_area.py)*: For Laruelle-style statistical upscaling

### **docs/**
- `TECHNICAL.md`: Technical data management and workflow detail
- `QUICKSTART.md`: Minimal setup for new users/developers
- `PROJECT_SUMMARY.md`: Science, intent, use-cases, impact
- `DEPLOYMENT.md`: Deployment instructions for various platforms
- `EXTRAPOLATION_PIPELINE.md`: Future enhancement for regional extrapolation

### **Frontend (Web Application)**
- `index.html`: Main interactive map interface
- `css/style.css`: Responsive styling
- `js/map.js`: Leaflet.js map logic and filtering

### **CI/CD**
- `.github/workflows/update-data.yml`: Automated data processing workflow

---

## 🛠️ Project Status — What's Done/What's Next

| Status         | Task                                                      | Details/Files                                      |
| -------------- | --------------------------------------------------------- | -------------------------------------------------- |
| ✅ Complete    | Replace all sample/fake data                              | Only use real, source-attributed records           |
| ✅ Complete    | Dürr et al. (2011) shapefiles operational                 | In main data folder, read with GeoPandas           |
| ✅ Complete    | Baum et al. (2024) data parsed as CSV                     | For attribute supplement (not main classification)  |
| ✅ Complete    | Remove Laruelle as data source                            | Only used as stats/validation                      |
| ✅ Complete    | Output valid `estuaries.geojson` from pipeline            | Includes provenance fields                         |
| ✅ Complete    | Interactive web map with Leaflet.js                       | Filtering, popups, responsive design               |
| ✅ Complete    | Comprehensive documentation                               | README, TECHNICAL, QUICKSTART, etc.                |
| ⚡ In Progress | GCC attributes spatial join/aggregation                   | See enrichment step in workflow                    |
| ⚡ In Progress | README, docs update with new data and workflow            | Update all citations and quickstart                |
| 🟦 Planned     | Extrapolation/statistical upscaling (Laruelle emulation)  | Standalone pipeline, regional summary, error bars   |
| 🟦 Planned     | Web UI extension for new attributes/scenario toggling     | e.g., land use overlays, climate metrics           |

---

## 📂 Data Provenance and Locations

### **Primary Data Sources (Main Classification)**

1. **Dürr et al. (2011)** - Worldwide typology of nearshore coastal systems
   - **File**: `data/Worldwide-typology-Shapefile-Durr_2011/typology_catchments.shp`
   - **DOI**: [10.1007/s12237-011-9381-y](https://doi.org/10.1007/s12237-011-9381-y)
   - **Provides**: ~6,200 estuary catchments with geomorphological typology (FIN_TYP codes)
   - **Usage**: PRIMARY source for geometry and classification
   - **Fields**: RECORDNAME, FIN_TYP, BASINAREA, SEANAME, OCEANNAME, geometry

### **Supplementary Data Sources (Enrichment Only)**

2. **Baum et al. (2024)** - Large structural estuaries
   - **File**: `data/Large-estuaries-Baum_2024/Baum_2024_Geomorphology.csv`
   - **Provides**: Morphometry data (width, length, geomorphotype) for 271 large embayments
   - **Usage**: OPTIONAL enrichment via name matching with Dürr data
   - **Note**: Not a replacement for Dürr classification

3. **Athanasiou et al. (2024)** - Global Coastal Characteristics (GCC)
   - **File**: `data/GCC-Panagiotis-Athanasiou_2024/GCC_geophysical.csv` (>200MB, NOT included in repo)
   - **DOI**: [10.5281/zenodo.8200199](https://doi.org/10.5281/zenodo.8200199)
   - **Download**: https://zenodo.org/records/11072020/files/GCC_geophysical.csv?download=1
   - **Provides**: Coastal land use, slope, elevation, mangrove coverage at 1km resolution
   - **Usage**: FUTURE spatial join for coastal attribute enrichment
   - **Note**: Must be downloaded separately, add to `.gitignore`

### **Reference/Validation Sources (NOT for raw data)**

4. **Laruelle et al. (2025)** - Global classification of estuaries
   - **Journal**: Estuaries and Coasts
   - **Usage**: ONLY for validation statistics and global area summaries
   - **Note**: ⚠️ **NEVER use as raw data source for shapes, polygons, or direct attributes**

### **Data Storage Guidelines**

- *All shapefiles, CSVs, and code needed for end-to-end processing are in `data/` and `scripts/`.*
- *No raw files >100MB should be tracked in git history (keep large data external or in `.gitignore`).*
- *GeoPackage (`.gpkg`) used for most efficient archive and direct mapping/analysis access.*
- *All generated files must include provenance metadata with DOIs and citations.*

---

## 📝 AI Agent — Core Principles and Guidelines

### **1. Data Integrity and Attribution**
- ✅ **DO**: Use only real, scientifically-cited, open-access data sources
- ✅ **DO**: Always include DOI and full citation for every data source
- ✅ **DO**: Add provenance fields to all generated datasets (source, DOI, date)
- ❌ **DON'T**: Use fake, sample, or placeholder data
- ❌ **DON'T**: Reference non-existent or retracted sources
- ❌ **DON'T**: Use Laruelle et al. (2025) as a raw data source (validation only)

### **2. Code and Documentation**
- ✅ **DO**: Write clear, defensive code with existence checks before file operations
- ✅ **DO**: Document every major transformation: source → output with provenance notes
- ✅ **DO**: Update all relevant documentation when making changes
- ✅ **DO**: Check `TECHNICAL.md` and `PROJECT_SUMMARY.md` before implementing features
- ❌ **DON'T**: Repeat data processing unless explicitly requested
- ❌ **DON'T**: Create redundant code or duplicate functionality

### **3. File Management**
- ✅ **DO**: Maintain all generated files in expected locations
- ✅ **DO**: Update `.gitignore` for large files (>100MB) like GCC data
- ✅ **DO**: Use GeoPackage (.gpkg) format for efficient spatial data storage
- ✅ **DO**: Validate output files against documentation
- ❌ **DON'T**: Commit large binary files (>100MB) to git
- ❌ **DON'T**: Remove or modify existing valid data files without confirmation

### **4. Feature Development**
- ✅ **DO**: Consult existing documentation before proposing new features
- ✅ **DO**: Check against existing To-Do's to avoid redundancy
- ✅ **DO**: List source, transformation steps, and scientific value for new features
- ✅ **DO**: Ask for user input before major new dependencies or downloads
- ❌ **DON'T**: Implement features that conflict with project mandate
- ❌ **DON'T**: Add dependencies without security and compatibility review

### **5. Quality Assurance**
- ✅ **DO**: Run tests after code changes (`python3 scripts/test_data.py`)
- ✅ **DO**: Verify GeoJSON/GeoPackage structure and completeness
- ✅ **DO**: Check coordinate validity ([-180,180] lon, [-90,90] lat)
- ✅ **DO**: Validate all required properties are present
- ❌ **DON'T**: Skip validation steps
- ❌ **DON'T**: Commit broken or incomplete data files

---

## 🔄 Data Processing Workflow

### **Current Pipeline (`scripts/process_estuary_data.py`)**

1. **Load Dürr et al. (2011) shapefile**
   - Read `typology_catchments.shp` with GeoPandas
   - Filter out invalid types (endorheic, glaciated, arheic)
   - Filter small catchments (<100 km² basin area)

2. **Load Baum et al. (2024) CSV (optional)**
   - Read `Baum_2024_Geomorphology.csv` with Pandas
   - Parse morphometry fields (width, length, geomorphotype)

3. **Sample representative estuaries**
   - Sort by BASINAREA (descending)
   - Select top 100 for visualization (configurable)
   - Prioritize diversity of types and geographic distribution

4. **Create GeoJSON features**
   - Extract centroid coordinates from polygons
   - Map FIN_TYP codes to human-readable types
   - Match with Baum data by name (fuzzy matching possible)
   - Add all provenance fields

5. **Generate output**
   - Write `data/estuaries.geojson` with metadata
   - Include data sources, DOIs, generation timestamp
   - Add notes about Laruelle and GCC usage

6. **Validate output**
   - Run `scripts/test_data.py` to verify structure
   - Check coordinates, properties, and type codes

### **Type Mapping (Dürr FIN_TYP to Display Types)**

```python
DURR_TYPE_MAP = {
    1: "Small Delta (Type I)",
    2: "Tidal System (Type II)",
    3: "Lagoon (Type III)",
    4: "Fjord/Fjaerd (Type IV)",
    5: "Delta",  # Large rivers with deltas
    51: "Delta",  # Large rivers with tidal deltas
    6: "Coastal Plain",  # Karst systems
    7: "Coastal Plain"
}

SIMPLE_TYPE_MAP = {
    1: "Delta",
    2: "Ria",
    3: "Lagoon",
    4: "Fjord",
    5: "Delta",
    51: "Delta",
    6: "Coastal Plain",
    7: "Coastal Plain"
}
```

### **Future Enhancement: GCC Spatial Join**

When implementing GCC enrichment:
1. Download `GCC_geophysical.csv` from Zenodo
2. Load with Pandas/GeoPandas
3. Perform spatial join between GCC points and estuary polygons/centroids
4. Aggregate GCC attributes by estuary (mean, median, mode as appropriate)
5. Add GCC fields to estuary properties with provenance
6. Update documentation with new attribute descriptions

### **Future Enhancement: Statistical Upscaling (Laruelle-style)**

For regional extrapolation pipeline:
1. Aggregate measured data by region and estuary type
2. Fit statistical distributions (lognormal, gamma, etc.) for area/size
3. Extrapolate to unmeasured systems using regional patterns
4. Provide confidence intervals for estimated totals
5. Calculate coverage statistics (measured vs extrapolated area)
6. Document methodology and assumptions clearly
7. Reference Laruelle et al. (2025) methodology for context

---

## 🧪 Testing and Validation

### **Running Tests**
```bash
# Install dependencies
pip install geopandas pandas pyproj

# Process data
python3 scripts/process_estuary_data.py

# Validate output
python3 scripts/test_data.py
```

### **Test Checklist**
- [ ] Valid GeoJSON FeatureCollection structure
- [ ] All features have required properties (name, type, coordinates)
- [ ] Coordinates within valid ranges ([-180,180], [-90,90])
- [ ] Type codes match Dürr typology
- [ ] Provenance fields present (data_source, data_source_doi)
- [ ] Metadata includes all data sources with citations
- [ ] No duplicate features
- [ ] File size reasonable for web use (<5MB recommended)

### **Web Application Testing**
- [ ] Map loads with all markers visible
- [ ] Filters work correctly (show/hide by type)
- [ ] Popups display correct information
- [ ] Responsive design on mobile/tablet/desktop
- [ ] No console errors in browser
- [ ] Scientific definitions display correctly
- [ ] Citations and references are complete

---

## 📚 Key Documentation Files to Review

### **Before Making Changes**
1. `README.md` - Project overview, data sources, citations
2. `docs/TECHNICAL.md` - Technical details, data structure, API
3. `PROJECT_SUMMARY.md` - Project goals, status, metrics
4. `QUICKSTART.md` - Setup and usage instructions

### **For Specific Tasks**
- **Data processing**: Review `scripts/process_estuary_data.py` comments
- **New features**: Check `docs/EXTRAPOLATION_PIPELINE.md` for planned enhancements
- **Deployment**: See `docs/DEPLOYMENT.md` for hosting options
- **Contributing**: Read `CONTRIBUTING.md` for guidelines

---

## 🎯 Common Tasks and How to Approach Them

### **Task: Add more estuaries to the map**
1. Review filtering logic in `load_durr_data()` function
2. Adjust sampling logic in `main()` (currently top 100 by basin area)
3. Consider performance implications (clustering for >500 markers)
4. Re-run processing script and tests
5. Update documentation with new count

### **Task: Integrate GCC data for coastal attributes**
1. Check if GCC CSV is downloaded (not in repo by default)
2. Add to `.gitignore` if not already present
3. Implement spatial join in `process_estuary_data.py`
4. Decide on aggregation method (mean, median, mode)
5. Add new properties to GeoJSON features
6. Update `docs/TECHNICAL.md` with new attribute descriptions
7. Update frontend to display new attributes in popups
8. Test and validate output

### **Task: Implement statistical upscaling**
1. Create new script `scripts/extrapolate_estuary_area.py`
2. Follow methodology in `docs/EXTRAPOLATION_PIPELINE.md`
3. Group data by region and type
4. Fit distributions (scipy.stats)
5. Generate summary statistics with uncertainties
6. Create visualization/dashboard for results
7. Document methodology clearly with references

### **Task: Fix a bug in data processing**
1. Review error message and traceback
2. Check input data files exist and are valid
3. Add defensive checks (file existence, data types)
4. Test fix with minimal sample data first
5. Run full pipeline and validation
6. Document fix in commit message

### **Task: Update scientific citations**
1. Verify new reference is peer-reviewed and published
2. Add to appropriate section in `README.md`
3. Update inline citations in code comments
4. Add DOI to metadata in generated GeoJSON
5. Update `docs/TECHNICAL.md` data sources section
6. Consider adding to sidebar definitions if relevant

---

## 🚫 Common Mistakes to Avoid

1. **Using Laruelle et al. (2025) as raw data**
   - ❌ Wrong: Extracting polygons or attributes from Laruelle
   - ✅ Right: Using Laruelle for validation statistics only

2. **Committing large files to git**
   - ❌ Wrong: Adding GCC_geophysical.csv (>200MB) to repo
   - ✅ Right: Adding to `.gitignore` and documenting download location

3. **Overwriting valid data without backup**
   - ❌ Wrong: Directly modifying `estuaries.geojson` manually
   - ✅ Right: Regenerating from processing script with version control

4. **Adding features without documentation**
   - ❌ Wrong: Adding new properties to GeoJSON without explaining source
   - ✅ Right: Documenting every new field with source, transformation, and scientific value

5. **Breaking existing functionality**
   - ❌ Wrong: Changing type codes without updating frontend filters
   - ✅ Right: Maintaining backward compatibility or updating all dependent code

6. **Ignoring test failures**
   - ❌ Wrong: Committing changes despite failing validation tests
   - ✅ Right: Fixing issues and ensuring all tests pass before commit

---

## 📈 Proposed Next Steps and Features

### **Short-term Enhancements**
1. Implement marker clustering for better performance with more estuaries
2. Add search/filter by name or region
3. Export filtered data as CSV/GeoJSON download
4. Add statistics panel showing counts by type/region

### **Medium-term Enhancements**
1. Integrate GCC coastal attributes (land use, elevation, slope)
2. Implement regional extrapolation pipeline
3. Add time-series data (if available from future studies)
4. Create comparative analysis tools

### **Long-term Vision**
1. Incorporate GHG emission data (CO2, CH4, N2O)
2. Add climate change impact scenarios
3. Integrate with land-use change datasets
4. Build predictive models for estuary evolution

### **Infrastructure Improvements**
1. Add automated testing in CI/CD
2. Implement code quality checks (linting, formatting)
3. Create Docker container for reproducible environment
4. Add database backend for dynamic data updates

---

## 🔍 Code Review Checklist

When reviewing or writing code for this project:

### **Python Scripts**
- [ ] Imports are necessary and properly organized
- [ ] Functions have docstrings with Args/Returns
- [ ] Error handling for file operations
- [ ] Type hints where appropriate
- [ ] Defensive programming (check file existence, data validity)
- [ ] Proper use of GeoPandas/Pandas APIs
- [ ] Output includes provenance metadata
- [ ] Code is readable and maintainable

### **JavaScript (Frontend)**
- [ ] ES6+ syntax used consistently
- [ ] No console errors in browser
- [ ] Proper event handler cleanup
- [ ] Responsive design tested on multiple devices
- [ ] Accessible (keyboard navigation, screen readers)
- [ ] GeoJSON loading error handling
- [ ] Filter logic works correctly

### **Documentation**
- [ ] All new features documented in README
- [ ] Technical details in TECHNICAL.md
- [ ] Data sources properly cited with DOIs
- [ ] Installation/usage instructions updated
- [ ] Examples provided where helpful
- [ ] Markdown formatting correct
- [ ] Links are valid and accessible

---

## 🎓 Scientific Context and Background

### **What are Estuaries?**
Partially enclosed coastal water bodies where freshwater from rivers meets and mixes with saltwater from the ocean. They are among the most productive ecosystems on Earth.

### **Why Geomorphological Classification?**
Understanding the physical shape and formation processes helps predict:
- Hydrodynamic behavior (mixing, circulation, tidal influence)
- Ecological characteristics (habitat types, productivity)
- Sediment transport and deposition patterns
- Vulnerability to climate change and sea level rise
- Human impacts and management needs

### **Main Classification Types (Dürr et al. 2011)**
- **Type 1**: Small Delta - River-dominated with sediment buildup
- **Type 2**: Tidal System - Dominated by tidal currents (Rias)
- **Type 3**: Lagoon - Separated by barrier islands
- **Type 4**: Fjord/Fjaerd - Glacially carved, deep and narrow
- **Type 5**: Large River - Major river systems, can be deltaic
- **Type 6-7**: Coastal Plain/Karst - Wide, shallow systems

### **Importance for Research**
- Carbon cycling and GHG emissions
- Nutrient filtering and water quality
- Coastal protection and erosion
- Biodiversity and fisheries
- Climate change impacts

---

## 📖 Sample README Data Attribution Block

```markdown
## Data Sources & Attribution

**Main Typology:** Dürr, H.H., et al. (2011)  
*Worldwide typology of nearshore coastal systems*  
DOI: [10.1007/s12237-011-9381-y](https://doi.org/10.1007/s12237-011-9381-y)

**Land Use/Context:** Athanasiou, P., et al. (2024, GCC)  
*Global Coastal Characteristics Database*  
DOI: [10.5281/zenodo.8200199](https://doi.org/10.5281/zenodo.8200199)

**Large estuary morphometry:** Baum, M.J., et al. (2024)  
*Large structural estuaries: Their global distribution and morphology*  
Geomorphology, supplementary data.

**Validation statistics:** Laruelle et al. (2025)  
*A global classification of estuaries based on their geomorphological characteristics*  
Estuaries and Coasts (context/stats only, never as raw data)
```

---

## 🧭 Quick Reference for AI Agents

### **Understanding the Full Landscape**
1. ✅ Review all data locations in `data/` directory
2. ✅ Check current outputs (`estuaries.geojson`)
3. ✅ Read README and all citations before making changes
4. ✅ Understand the distinction: Dürr (data) vs Laruelle (validation)

### **Before Writing Code**
1. ✅ Check file existence and data sizes
2. ✅ Review existing functions to avoid duplication
3. ✅ Document transformation steps
4. ✅ Verify correct linking between datasets

### **Before Committing**
1. ✅ Run all tests (`test_data.py`)
2. ✅ Validate GeoJSON structure
3. ✅ Check for console errors in web app
4. ✅ Update relevant documentation
5. ✅ Verify provenance fields are present

### **When Proposing Features**
1. ✅ Check TECHNICAL.md for context
2. ✅ Review planned features in To-Do list
3. ✅ List source data, transformation, and scientific value
4. ✅ Ask for confirmation before major changes

---

## ⚡ Emergency Procedures

### **If Data Processing Fails**
1. Check if source files exist in expected locations
2. Verify GeoPandas and dependencies are installed
3. Check file permissions and disk space
4. Review error messages for missing columns or invalid geometries
5. Test with smaller subset of data first
6. Consult TECHNICAL.md for expected data structure

### **If Web Map Doesn't Load**
1. Check browser console for JavaScript errors
2. Verify `estuaries.geojson` exists and is valid JSON
3. Test with simple Python server (`python3 -m http.server`)
4. Check if Leaflet.js CDN is accessible
5. Validate GeoJSON at https://geojson.io
6. Clear browser cache and try again

### **If Tests Fail**
1. Run `python3 scripts/test_data.py` to see specific failures
2. Check if data file was modified unexpectedly
3. Verify coordinate ranges ([-180,180], [-90,90])
4. Check for missing required properties
5. Regenerate data from processing script
6. Review recent commits for breaking changes

---

## 📞 Contact and Support

For questions or issues:
1. Check existing documentation first (README, TECHNICAL, QUICKSTART)
2. Review this instruction file for guidance
3. Search GitHub issues for similar problems
4. Open a new issue with detailed description and error messages
5. Tag with appropriate labels (bug, enhancement, documentation, etc.)

---

## 🎯 Success Criteria for AI Agent Work

Your work is successful when:
- ✅ All tests pass without errors
- ✅ Documentation is updated and accurate
- ✅ Data provenance is complete and traceable
- ✅ No breaking changes to existing functionality
- ✅ Code is readable and maintainable
- ✅ Scientific integrity is maintained
- ✅ User-facing features work as expected
- ✅ Performance is acceptable (<5s load time)

Remember: **Transparency, reproducibility, and scientific rigor are the core values of this project.**
