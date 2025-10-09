# Global Coastal Characteristics (GCC) Data

## Overview

This directory is for the Global Coastal Characteristics (GCC) database by Athanasiou et al. (2024), which provides high-resolution coastal attributes including land use, slope, elevation, mangrove coverage, and other geophysical characteristics at ~1km transect points along global coastlines.

## Download Required

**The GCC_geophysical.csv file is NOT included in this repository due to its large size (>200MB).**

To use GCC data for estuary enrichment:

1. **Download the file** from Zenodo:
   - URL: https://zenodo.org/records/11072020/files/GCC_geophysical.csv?download=1
   - Size: ~200MB (zipped)

2. **Place the file** in this directory:
   ```
   data/GCC-Panagiotis-Athanasiou_2024/GCC_geophysical.csv
   ```

3. **Extend the processing pipeline** in `scripts/process_estuary_data.py` to:
   - Load the GCC CSV file
   - Spatially join GCC points to estuary polygons/centroids
   - Add relevant coastal attributes (land use, slope, elevation, etc.) to estuary properties

## Data Citation

**Athanasiou, P., van Dongeren, A., Giardino, A., Vousdoukas, M., Ranasinghe, R., & Kwadijk, J. (2024)**  
*Global Coastal Characteristics (GCC) Database.*  
DOI: [10.5281/zenodo.8200199](https://doi.org/10.5281/zenodo.8200199)

## Data Attributes

The GCC database includes (~1km coastal transects):
- Land use/land cover classifications
- Elevation and slope
- Distance to urban areas
- Mangrove coverage
- Vegetation indices
- Hydrological characteristics
- And many more geophysical attributes

See `meta_data.yml` in this directory for full attribute descriptions.

## Future Integration

The data processing pipeline is designed to support GCC integration. Once downloaded, the CSV can be used to enrich estuary data with:
- Coastal land use characteristics
- Topographic attributes
- Ecological indicators (mangroves, vegetation)
- Anthropogenic pressure indicators

This enrichment will provide a more comprehensive view of estuary characteristics beyond basic typology and morphometry.
