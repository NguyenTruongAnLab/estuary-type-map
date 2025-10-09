# Future Enhancement: Regional Extrapolation Pipeline

## Overview

This document outlines a planned enhancement for regional extrapolation and statistical upscaling of estuary data, similar to methodologies used in Laruelle et al. (2025).

## Purpose

While the current implementation displays ~100 representative estuaries from the Dürr et al. (2011) dataset, the complete dataset contains ~6,200 estuary catchments. A future extrapolation pipeline will:

1. **Aggregate measured data** by region and estuary type
2. **Fit statistical distributions** for area and size within each type-region combination
3. **Extrapolate** to unmeasured or smaller systems using regional patterns
4. **Provide confidence intervals** for estimated global/regional totals
5. **Calculate coverage statistics** showing measured vs. extrapolated area

## Methodology (Following Laruelle et al. Approach)

### Step 1: Regional Aggregation
- Group estuaries by:
  - Geographic region (continent, ocean basin)
  - Estuary type (from Dürr FIN_TYP classification)
- Calculate summary statistics for each region-type combination

### Step 2: Size Distribution Analysis
- Fit area/size distribution curves (e.g., log-normal, power-law)
- Determine parameters for each type-region combination
- Validate fits against observed data

### Step 3: Extrapolation
- Apply fitted distributions to estimate:
  - Total number of systems in each category
  - Total area of unmeasured systems
  - Size distribution of smaller, unmapped estuaries
- Use literature values and expert knowledge for validation

### Step 4: Uncertainty Quantification
- Calculate confidence intervals using:
  - Bootstrap resampling of observed data
  - Monte Carlo simulation of fitted distributions
  - Propagation of measurement uncertainties
- Report uncertainty ranges for all extrapolated values

### Step 5: Visualization
- Display on map sidebar:
  - Measured vs. extrapolated estuary counts
  - Total area by region and type
  - Confidence intervals
  - Coverage completeness metrics
- Add summary statistics panel with global totals

## Implementation Plan

### Phase 1: Data Aggregation (Not yet implemented)
```python
# Pseudo-code for future implementation
def aggregate_by_region_type(gdf):
    """Group estuaries and calculate statistics."""
    grouped = gdf.groupby(['region', 'FIN_TYP']).agg({
        'BASINAREA': ['count', 'sum', 'mean', 'std', 'min', 'max'],
        'geometry': 'first'  # For spatial reference
    })
    return grouped
```

### Phase 2: Distribution Fitting (Not yet implemented)
```python
# Pseudo-code for future implementation
def fit_area_distribution(areas, distribution='lognormal'):
    """Fit statistical distribution to area data."""
    from scipy import stats
    if distribution == 'lognormal':
        params = stats.lognorm.fit(areas)
    # ... additional distributions
    return params, distribution
```

### Phase 3: Extrapolation (Not yet implemented)
```python
# Pseudo-code for future implementation
def extrapolate_unmeasured(measured_data, fit_params, target_count):
    """Extrapolate to unmeasured systems using fitted distribution."""
    # Generate synthetic samples
    # Apply constraints and validation
    # Return extrapolated statistics with uncertainties
    pass
```

### Phase 4: Web Integration (Not yet implemented)
- Add statistics panel to sidebar
- Display regional breakdown
- Show methodology and assumptions
- Provide data download for extrapolated values

## Data Requirements

For robust extrapolation, we need:
- [x] Complete Dürr et al. (2011) dataset (~6,200 systems) ✓
- [x] Baum et al. (2024) large estuary data (271 systems) ✓
- [ ] Regional boundaries (continents, ocean basins)
- [ ] Literature-derived system counts for validation
- [ ] Expert-validated area ranges by type

## Scientific Basis

### Key References for Methodology

1. **Laruelle, G.G., et al. (2025)**  
   *A global classification of estuaries based on their geomorphological characteristics.*  
   Estuaries and Coasts.  
   → Provides validation statistics and upscaling methodology

2. **Dürr, H.H., et al. (2011)**  
   *Worldwide typology of nearshore coastal systems.*  
   Estuaries and Coasts, 34(3), 441-458.  
   → Primary measured data source

3. **Statistical Methods Literature**  
   - Log-normal distributions for natural size data
   - Bootstrap methods for uncertainty quantification
   - Spatial statistics for regionalization

## Validation Approach

Extrapolated values will be validated against:
- Published global/regional estuary area estimates
- Remote sensing derived coastline lengths
- Known distribution of large systems (Baum et al.)
- Expert knowledge from coastal geomorphologists
- Laruelle et al. (2025) reported statistics

## Assumptions and Limitations

### Assumptions
1. Size distributions within type-region categories follow known statistical patterns
2. Observed estuaries are representative of regional populations
3. Dürr et al. classification system captures major geomorphological variation
4. Unmeasured systems are generally smaller than measured ones

### Limitations
1. Extrapolation accuracy decreases for poorly sampled regions
2. Small estuaries may be underrepresented in source data
3. Human modifications not fully accounted for
4. Temporal changes in estuary area not captured
5. Classification boundaries may be fuzzy in nature

## Timeline

This feature is planned for future implementation. Priority will be given to:
1. **Phase 1**: Complete data aggregation and regional assignment
2. **Phase 2**: Implement distribution fitting and validation
3. **Phase 3**: Develop extrapolation algorithms with uncertainty
4. **Phase 4**: Integrate into web interface

## Contributing

If you're interested in contributing to this extrapolation pipeline:
1. Review the scientific literature on estuary size distributions
2. Propose statistical methods appropriate for the data structure
3. Implement and validate against known benchmarks
4. Submit pull requests with clear documentation of methods

## Notes

- This extrapolation is distinct from the measured data visualization
- All extrapolated values will be clearly marked as estimates
- Uncertainty ranges will always be provided
- Methodology and assumptions will be fully documented
- Validation against Laruelle et al. (2025) and other sources will be transparent

---

**Status**: Planned for future development  
**Last Updated**: 2024  
**Contact**: Open an issue on GitHub for questions or suggestions
