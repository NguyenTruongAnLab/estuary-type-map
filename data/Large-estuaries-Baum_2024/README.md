# Large Structural Estuaries - Baum et al. (2024)

## Overview

This directory contains supplementary morphometric data for large structural estuaries from:

**Baum, M.J., Schüttrumpf, H., & Siemes, R.W. (2024)**  
*Large structural estuaries: Their global distribution and morphology.*  
**Geomorphology**, supplementary data.

## Data File

**Baum_2024_Geomorphology.csv**

This CSV file contains morphometric measurements for 271 large embayments globally, including:

- **Embayment**: Name of the estuary/embayment
- **Lm**: Mouth width (meters)
- **Lb**: Embayment length (meters)
- **Lat**: Latitude (decimal degrees)
- **Long**: Longitude (decimal degrees)
- **C**: Circularity ratio (Lm/Lb)
- **Tectonic Coast Classification**: Geological setting (collision, trailing, marginal)
- **Geomorphotype**: Classification (LSE, Rocky Bay, Sandy Bay, Barrier Estuary)
- **Cluster Weight (ω)**: Statistical weight in cluster analysis

## Usage in Pipeline

The `process_estuary_data.py` script uses this data to enrich estuaries from the Dürr et al. (2011) dataset by:
1. Matching estuary names between datasets
2. Adding morphometric attributes (mouth width, length, geomorphotype)
3. Including these as supplementary properties in the output GeoJSON

This provides additional morphological detail for major estuaries where available.

## Data Characteristics

- **Coverage**: 271 large structural estuaries worldwide
- **Focus**: Major embayments with significant morphological features
- **Purpose**: Understanding global distribution and morphology of large coastal water bodies
- **Spatial Resolution**: Point locations (lat/long) with morphometric measurements

## Citation

When using this data, please cite:

```
Baum, M.J., Schüttrumpf, H., & Siemes, R.W. (2024). 
Large structural estuaries: Their global distribution and morphology. 
Geomorphology, supplementary data.
```
