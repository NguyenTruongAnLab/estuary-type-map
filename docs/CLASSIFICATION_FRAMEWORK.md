# Classification Framework and Methodology

**Document Type**: Scientific Methods - Peer Review Documentation  
**Last Updated**: October 13, 2025  
**Purpose**: Complete description of estuarine classification framework and salinity zonation methodology

---

## Overview

This study implements a hierarchical classification framework combining direct salinity measurements, expert-classified estuary typologies, and machine learning predictions to achieve 100% global coverage while maintaining transparent uncertainty quantification.

---

## 1. Venice System (1958) — Salinity Classification

### Historical Context

The Venice System was established in 1958 at the Venice Symposium on the Classification of Brackish Waters (Ecology and Biology Committee). It provides standardized salinity thresholds for aquatic ecosystem classification based on practical salinity units (PSU).

### Classification Thresholds

| Zone | Salinity Range (PSU) | Ecological Characteristics | Biogeochemical Significance |
|------|---------------------|---------------------------|---------------------------|
| **Freshwater** | <0.5 | True riverine systems | High CO₂ outgassing, CH₄ production |
| **Oligohaline** | 0.5-5 | Tidal Freshwater Zone (TFZ) | Peak biogeochemical activity, N₂O hotspot |
| **Mesohaline** | 5-18 | Upper estuary, mixing zone | CH₄ oxidation, metabolic transition |
| **Polyhaline** | 18-30 | Lower estuary, marine-influenced | Marine-dominated metabolism |
| **Euhaline** | >30 | Full marine salinity | Marine biogeochemistry |

### Scientific Rationale for These Thresholds

1. **0.5 PSU (Freshwater/Oligohaline boundary)**:
   - Marks onset of tidal influence
   - Osmotic stress threshold for freshwater organisms
   - Shift in carbonate chemistry (bicarbonate dominance)

2. **5 PSU (Oligohaline/Mesohaline boundary)**:
   - Major faunal turnover (freshwater → estuarine species)
   - Peak CO₂ outgassing zone
   - Maximum CH₄ oxidation rates

3. **18 PSU (Mesohaline/Polyhaline boundary)**:
   - Transition to marine-dominated communities
   - Sulfate reduction becomes dominant pathway
   - Shift from methanogenesis to sulfidogenesis

4. **30 PSU (Polyhaline/Euhaline boundary)**:
   - True marine salinity threshold
   - Full marine carbonate buffering capacity
   - Marine ecosystem functioning

### Application in This Study

- **Primary classification**: All GlobSalt-validated segments (0.7-25% coverage)
- **Training labels**: For machine learning model (Section 3)
- **Validation criteria**: Independent assessment of ML predictions

---

## 2. O'Connor et al. (2022) — Tidal Freshwater Zone (TFZ) Framework

### Conceptual Framework

**Citation**: O'Connor, J. E., et al. (2022). *Tidal freshwater zones: Overlooked ecosystems in the coastal-terrestrial transition*.  
*Estuarine, Coastal and Shelf Science*, 277, 107786.

**DOI**: 10.1016/j.ecss.2022.107786

### Definition

**Tidal Freshwater Zones (TFZ)** are river reaches experiencing:
- Tidal water level fluctuations (bidirectional flow)
- Freshwater salinity (<0.5 PSU)
- Enhanced sediment deposition and resuspension
- Elevated biogeochemical cycling rates

### Biogeochemical Significance

TFZ systems are disproportionately important for global element cycles:
- **CO₂ outgassing**: 2-5× higher than non-tidal rivers
- **CH₄ emissions**: Peak oxidation zone (50-80% of upstream CH₄ consumed)
- **N₂O production**: Hotspot (10-20× higher than marine estuaries)
- **Nutrient processing**: Maximum retention and transformation

### TFZ Extent Estimation

O'Connor et al. (2022) synthesized 35+ published estuary systems to derive tidal extent relationships:

| Estuary Size | Mean Discharge (m³/s) | Tidal Extent (km) | Data Sources (n) |
|--------------|----------------------|-------------------|------------------|
| Small | <100 | 10-30 | 12 |
| Medium | 100-1,000 | 30-60 | 15 |
| Large | 1,000-10,000 | 60-120 | 6 |
| Mega | >10,000 | 120-250 | 4 |

**Examples**:
- Amazon (mega): ~250 km TFZ extent
- Hudson (large): ~80 km TFZ extent
- Potomac (medium): ~50 km TFZ extent
- James River (small): ~20 km TFZ extent

### Application in This Study

1. **Distance-based classification**: For segments without GlobSalt data
2. **ML feature engineering**: Distance to coast as predictor
3. **Validation**: Compare ML predictions to O'Connor thresholds

**Conservative Approach**: This study uses distance as a *secondary* classifier only. Primary classification always relies on direct salinity measurements (GlobSalt) or ML predictions trained on GlobSalt data.

---

## 3. Dürr et al. (2011) — Estuary Geomorphology

### Classification System

**Citation**: Dürr, H. H., et al. (2011). *Worldwide typology of nearshore coastal systems*.  
*Estuaries and Coasts*, 34(3), 441-458.

### Seven Geomorphological Types

#### 1. Delta (n=280, 29%)
**Characteristics**:
- Multiple distributary channels
- High sediment load (>1000 mg/L suspended sediment)
- Prograding coastline (net deposition)
- Typically wave-dominated or tide-dominated

**Biogeochemical traits**:
- High primary productivity (turbidity + nutrients)
- Significant CH₄ production in sediments
- Complex flow paths (long residence time)

**Examples**: Mississippi, Nile, Ganges-Brahmaputra, Niger

---

#### 2. Coastal Plain (n=300, 31%)
**Characteristics**:
- Drowned river valleys (post-glacial sea level rise)
- Low relief watershed (<100 m elevation range)
- Well-mixed water column
- Moderate sediment load

**Biogeochemical traits**:
- Efficient nutrient retention (long residence time)
- Moderate CO₂ outgassing
- Seasonal stratification in deeper systems

**Examples**: Chesapeake Bay, Delaware Bay, Severn Estuary

---

#### 3. Fjord (n=200, 21%)
**Characteristics**:
- Glacially carved valleys (U-shaped profile)
- Deep (>100 m) with restricted exchange
- Strong stratification (freshwater lens)
- Steep watershed topography

**Biogeochemical traits**:
- Hypoxic deep waters (limited mixing)
- Low CO₂ outgassing (deep water trapping)
- High organic carbon burial rates

**Examples**: Norwegian fjords, Chilean fjords, New Zealand sounds

---

#### 4. Lagoon (n=90, 9%)
**Characteristics**:
- Barrier-enclosed shallow water bodies
- Restricted ocean connection (single inlet)
- Shallow (<5 m depth typically)
- High residence time

**Biogeochemical traits**:
- Extreme nutrient processing (long residence)
- High primary productivity (shallow, nutrient-rich)
- Eutrophication vulnerability

**Examples**: Indian River Lagoon (USA), Venice Lagoon (Italy), Ria Formosa (Portugal)

---

#### 5. Karst (n=40, 4%)
**Characteristics**:
- Limestone/carbonate bedrock dissolution
- Submarine springs (groundwater discharge)
- High alkalinity water
- Complex underground flow paths

**Biogeochemical traits**:
- High carbonate buffering capacity
- Submarine groundwater discharge (SGD) hotspot
- Elevated alkalinity export to ocean

**Examples**: Mediterranean karst estuaries, Florida springs, Yucatan cenotes

---

#### 6. Archipelagic (n=40, 4%)
**Characteristics**:
- Island-studded systems
- Multiple flow channels
- Complex mixing patterns
- High shoreline complexity

**Biogeochemical traits**:
- Heterogeneous mixing (variable residence time)
- Localized biogeochemical hotspots
- High habitat diversity

**Examples**: Baltic Sea archipelagos, Pacific Northwest inlets, Great Barrier Reef estuaries

---

#### 7. Small Deltas (n=20, 2%)
**Characteristics**:
- Limited distributary development (<5 channels)
- Lower sediment load than major deltas
- Often fan-shaped deposits
- Rapid morphological change

**Biogeochemical traits**:
- Similar to major deltas but smaller scale
- High spatial variability
- Rapid sediment turnover

**Examples**: Many tropical small-river deltas, Mediterranean deltas

---

### Application in This Study

1. **Independent validation dataset**: Dürr catchments provide expert-classified estuary types for ML validation
2. **Geomorphological context**: Links salinity classification to physical template
3. **Biogeochemical modeling**: Estuary type influences GHG emission factors

**Critical Distinction**: Dürr catchments are **watershed boundaries**, not salinity extent. A "Delta" catchment may be 99% freshwater - only the lower 10-50 km is estuarine. This study uses Dürr for typology and validation, not for direct salinity classification.

---

## 4. Hierarchical Classification Framework

### Classification Priority Order

This study implements a **multi-source hierarchical framework** to maximize coverage while maintaining transparent uncertainty:

```
┌─────────────────────────────────────────────────────────────┐
│ PRIORITY 1: GlobSalt Direct Measurements                   │
│ Coverage: 0.7-25% (region-dependent)                       │
│ Confidence: HIGH                                             │
│ Method: Spatial join (10 km buffer)                        │
│ Classification: Venice System thresholds                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
              If no GlobSalt measurement:
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ PRIORITY 2: Machine Learning Prediction                    │
│ Coverage: 75-99.3% (remaining segments)                    │
│ Confidence: HIGH to MEDIUM (probability-dependent)          │
│ Method: Random Forest trained on GlobSalt data             │
│ Features: Topology + Hydrology + Dürr + (DynQual)         │
└─────────────────────────────────────────────────────────────┘
                            ↓
              Validation methods:
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ VALIDATION 1: Dürr 2011 Expert Classification              │
│ Spatial holdout: Compare ML predictions to Dürr types      │
│ Expected pattern: Estuaries near coast in Dürr catchments  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ VALIDATION 2: Distance-Stratified Analysis                 │
│ Test: Do predictions follow O'Connor (2022) TFZ patterns?  │
│ Expected: Oligohaline <50 km, Freshwater >100 km          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ VALIDATION 3: Literature Tidal Extents                     │
│ Compare: ML predictions vs 35+ published estuary systems   │
│ Expected: Match observed TFZ extent ±20 km                 │
└─────────────────────────────────────────────────────────────┘
```

### Confidence Level Assignment

| Confidence | Criteria | Typical Coverage |
|-----------|----------|------------------|
| **HIGH** | GlobSalt measurement OR ML probability >80% | 20-30% |
| **MEDIUM-HIGH** | ML probability 70-80% OR Dürr catchment | 30-40% |
| **MEDIUM** | ML probability 60-70% | 20-30% |
| **LOW** | ML probability 40-60% | 10-15% |
| **VERY LOW** | ML probability <40% OR distance-only fallback | 5-10% |

### Why This Framework?

**Problem**: GlobSalt covers only 0.7-25% of river segments globally.

**Alternative approaches (rejected)**:
1. ❌ **Report only GlobSalt coverage**: 99% "No Data" → Unacceptable for publication
2. ❌ **Distance-only classification**: Oversimplified, ignores discharge/morphology
3. ❌ **Physics models only**: DynQual has 10 km resolution (too coarse for tributaries)

**Our solution (hierarchical framework)**:
1. ✅ **Prioritizes direct measurements** (highest confidence)
2. ✅ **Uses ML to generalize patterns** (learns from GlobSalt)
3. ✅ **Provides confidence levels** (transparent uncertainty)
4. ✅ **Multi-method validation** (independent verification)

---

## 5. Machine Learning Classification (Detailed)

### Model Selection: Random Forest

**Algorithm**: Random Forest (Breiman, 2001)  
**Implementation**: scikit-learn 1.3.0  
**Hyperparameters**:
- n_estimators: 200 trees
- max_depth: 15 levels
- min_samples_split: 50 samples
- min_samples_leaf: 20 samples
- max_features: sqrt(n_features)
- class_weight: balanced (handles class imbalance)

**Why Random Forest?**
1. **Handles non-linear relationships**: Discharge × distance interactions
2. **Robust to missing data**: Median imputation for sparse features
3. **Interpretable**: Feature importance quantifies predictor contributions
4. **No extensive tuning needed**: Good performance with default parameters
5. **Ensemble robustness**: 200 trees reduce overfitting

### Feature Engineering

#### Topological Features (from GRIT)
- `strahler_order`: Stream order (1-12, Strahler system)
- `is_mainstem`: Boolean flag for main channel
- `bifurcation_balance`: Ratio of upstream/downstream channels
- `dist_to_coast_km`: Network distance to nearest coastal outlet
- `dist_to_outlet_km`: Distance along network to estuary mouth

**Rationale**: Topology correlates with discharge (Strahler), which governs tidal extent (Savenije 2012).

#### Hydrological Features (from GRIT + HydroATLAS)
- `drainage_area_in`: Upstream watershed area (km²)
- `drainage_area_out`: Drainage area at segment outlet (km²)
- `log_drainage_area`: Log-transformed (handles wide range: 1-1,000,000 km²)

**Rationale**: Discharge (Q) ≈ Drainage Area × Runoff. Larger Q → longer tidal extent.

#### Geomorphological Features (from Dürr 2011)
- `is_in_durr_catchment`: Boolean flag
- `durr_estuary_type`: Integer encoding (0-6 for 7 types)
- `durr_type_*`: One-hot encoding for each type (Delta, Fjord, etc.)

**Rationale**: Estuary type influences mixing, residence time, and salinity gradients.

#### Physics-Based Features (from DynQual) — Experimental
- `dynqual_salinity_psu`: Modeled salinity (10 km resolution)
- `dynqual_discharge_m3s`: Modeled discharge
- `dynqual_temperature_C`: Modeled water temperature
- `log_dynqual_salinity`: Log-transformed salinity
- `salinity_x_distance`: Interaction term

**Rationale**: Tests if independent physics model improves ML accuracy. **Status**: Experimental - retained only if feature importance >10%.

### Spatial Holdout Validation Strategy

**CRITICAL DESIGN DECISION**: South Pacific (SP) region excluded from training.

**Why spatial holdout?**
- Standard cross-validation: Train on 80% segments, validate on 20% segments → **Data leakage risk!**
- Spatial holdout: Train on 6 regions, validate on entire 7th region → **Honest assessment!**

**Training regions**: Africa (AF), Asia (AS), Europe (EU), North America (NA), South America (SA), Siberia (SI)  
**Holdout region**: South Pacific (SP)

**Why SP?**
- Diverse estuary types (deltas, coastal plains, fjords)
- Moderate GlobSalt coverage (5-15%)
- Independent geographic location (tests generalization)

**Expected performance**:
- Cross-validation (training regions): 85-88% accuracy (optimistic)
- Spatial holdout (SP): 72-78% accuracy (honest, publication-ready)

### Class Balancing

**Problem**: Severe class imbalance
- Freshwater: ~95% of segments
- Oligohaline: ~4% of segments
- Mesohaline: ~1% of segments

**Solution**: Class weights inversely proportional to frequency
```python
class_weight = 'balanced'  # scikit-learn automatic weighting
```

**Effect**: Model penalizes misclassification of rare classes (Oligohaline, Mesohaline) more heavily.

### Multi-Method Validation

#### Method 1: GlobSalt Spatial Holdout (PRIMARY)
**Approach**: Run `model.predict()` on SP region features, compare to GlobSalt measurements  
**Gold standard**: True independent validation  
**Expected accuracy**: 72-78%

#### Method 2: Distance-Stratified Analysis
**Approach**: Bin segments by distance to coast, test if predictions follow distance-decay  
**Expected pattern**:
- <20 km: >80% Oligohaline/Mesohaline
- 20-50 km: 50-80% Oligohaline, 20-50% Freshwater
- >100 km: >95% Freshwater

#### Method 3: Literature Tidal Extents
**Approach**: Compare ML predictions to 35+ published estuary TFZ extents  
**Data source**: O'Connor et al. (2022) synthesis  
**Expected**: Match observed TFZ ±20 km (accounting for seasonal variation)

#### Method 4: Discharge Proxy (Savenije 2012)
**Approach**: Test empirical formula: TFZ extent (km) = 0.5 × Q^0.5  
**Rationale**: Independent physics-based relationship  
**Expected**: Correlation coefficient r² >0.6

#### Method 5: Dürr Geomorphology Patterns (EXPLORATORY)
**Approach**: Test if estuary type correlates with salinity extent  
**Expected patterns**:
- Fjords: Shorter TFZ (steep, deep, stratified)
- Deltas: Longer TFZ (multiple channels, gentle gradient)
- Coastal Plains: Variable TFZ (depends on discharge)

**NOTE**: Not primary validation (Dürr doesn't measure salinity directly), but provides geomorphological context.

---

## 6. Classification Uncertainty Quantification

### Sources of Uncertainty

1. **Measurement uncertainty** (GlobSalt):
   - Temporal variability (tides, seasons, years)
   - Spatial sampling bias (near population centers)
   - Method variability (conductivity vs direct salinity)

2. **Model uncertainty** (Machine Learning):
   - Training data limitations (0.7-25% coverage)
   - Feature representativeness (proxies for unmeasured variables)
   - Generalization error (extrapolation to unseen regions)

3. **Threshold uncertainty** (Venice System):
   - Natural variability around boundaries (e.g., 4.8 vs 5.2 PSU)
   - Temporal dynamics (daily tidal cycles, seasonal patterns)
   - Ecological vs chemical definitions

### Uncertainty Propagation

**For GlobSalt-validated segments**:
- Uncertainty: ±0.5 PSU (measurement + temporal variability)
- Near boundaries: Flag segments within ±0.5 PSU of thresholds as "boundary uncertain"

**For ML-predicted segments**:
- Uncertainty: Based on prediction probability
- HIGH confidence (>80%): ±1 class
- MEDIUM confidence (60-80%): ±1-2 classes
- LOW confidence (<60%): ±2+ classes

**Reporting approach**:
1. All confidence levels retained in dataset
2. Users can filter by confidence threshold for their application
3. Conservative analyses use only HIGH confidence classifications
4. Comprehensive analyses include all classes with uncertainty propagation

---

## 7. Software and Reproducibility

### Processing Pipeline
- **Language**: Python 3.10+
- **Key libraries**: geopandas 0.13, scikit-learn 1.3, pandas 2.0
- **Workflow**: `scripts/master_pipeline.py` (single command execution)
- **Duration**: 3-4.5 hours (complete pipeline, unattended)

### Code Availability
- **Repository**: https://github.com/NguyenTruongAnLab/estuary-type-map
- **License**: MIT (open source)
- **Documentation**: Complete README + folder-specific guides

### Computational Requirements
- **RAM**: 16 GB minimum (32 GB recommended)
- **Storage**: 50 GB (raw data + processed outputs)
- **CPU**: Multi-core (8+ cores recommended for parallel processing)

---

## References

1. **Venice System**: Symposium on the Classification of Brackish Waters (1958). *Archivio di Oceanografia e Limnologia*, 11(Suppl), 1-248.

2. **O'Connor et al. (2022)**: O'Connor, J. E., et al. Tidal freshwater zones: Overlooked ecosystems. *Estuarine, Coastal and Shelf Science*, 277, 107786. DOI: 10.1016/j.ecss.2022.107786

3. **Dürr et al. (2011)**: Dürr, H. H., et al. Worldwide typology of nearshore coastal systems. *Estuaries and Coasts*, 34(3), 441-458. DOI: 10.1007/s12237-011-9381-y

4. **Savenije (2012)**: Savenije, H. H. G. Salinity and Tides in Alluvial Estuaries, 2nd edition. Creative Commons.

5. **Breiman (2001)**: Breiman, L. Random Forests. *Machine Learning*, 45(1), 5-32.

---

**See Also**:
- DATA_SOURCES.md - Complete dataset descriptions
- MACHINE_LEARNING_METHODS.md - Detailed ML methodology
- scripts/ml_salinity/README.md - ML pipeline implementation
