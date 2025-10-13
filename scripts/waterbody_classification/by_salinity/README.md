# 💧 Salinity-Based Classification

**Scientific Framework**: Venice System (1958) + O'Connor et al. (2022) Tidal Freshwater Zone

**Purpose**: Classify water bodies by salinity concentration for biogeochemical modeling

---

## 🎯 Classification Scheme

### Venice System (1958) Thresholds

| Class | Salinity Range (PSU) | Biogeochemical Characteristics |
|-------|---------------------|--------------------------------|
| **Freshwater** | <0.5 | High CO₂ outgassing, CH₄ production |
| **Oligohaline** | 0.5-5.0 | Tidal Freshwater Zone (TFZ), peak N₂O |
| **Mesohaline** | 5.0-18.0 | CH₄ oxidation, metabolic transition |
| **Polyhaline** | 18.0-30.0 | Marine-influenced, reduced CH₄ |
| **Euhaline** | >30.0 | Full marine biogeochemistry |

---

## 📁 Scripts (To Be Implemented)

### 1. classify_venice_system.py
**Status**: ⏳ Planned (Phase 2)  
**Purpose**: Apply Venice System classification to all water bodies

**Input**:
- `data/processed/rivers_grit_ml_classified_*.gpkg` (ML predictions)
- `data/processed/globsalt_stations.gpkg` (validated measurements)

**Output**:
- `data/processed/classified_venice_system_*.gpkg`

**Method**:
```python
def classify_venice_system(salinity_psu):
    if salinity_psu < 0.5: return 'Freshwater'
    elif salinity_psu < 5.0: return 'Oligohaline'
    elif salinity_psu < 18.0: return 'Mesohaline'
    elif salinity_psu < 30.0: return 'Polyhaline'
    else: return 'Euhaline'
```

---

### 2. identify_tfz_extents.py
**Status**: ⏳ Planned (Phase 2)  
**Purpose**: Identify Tidal Freshwater Zone (TFZ) boundaries

**Input**:
- Venice System classification
- Tidal extent data (literature + DynQual)
- Distance to coast measurements

**Output**:
- `data/processed/tfz_boundaries_*.gpkg`
- TFZ length by river system

**Method** (O'Connor et al. 2022):
```python
# TFZ = oligohaline zone (0.5-5 PSU) with tidal influence
# Extent varies by discharge: 10-200 km from coast
def identify_tfz(segments):
    tfz = segments[
        (segments['salinity_psu'] >= 0.5) & 
        (segments['salinity_psu'] < 5.0) &
        (segments['has_tidal_influence'] == True)
    ]
    return tfz
```

---

### 3. classify_by_residence_time.py
**Status**: ⏳ Planned (Phase 2)  
**Purpose**: Classify mixing zones by water residence time

**Input**:
- Discharge data (DynQual)
- Basin volume (from bathymetry)
- Salinity gradients

**Output**:
- `data/processed/mixing_zones_*.gpkg`
- Residence time estimates

**Method**:
```python
# Residence time = Volume / Discharge
# Influences biogeochemical processing rates
def classify_by_residence_time(volume_m3, discharge_m3s):
    residence_days = volume_m3 / (discharge_m3s * 86400)
    
    if residence_days < 1: return 'Fast-flushed'
    elif residence_days < 7: return 'Moderate'
    elif residence_days < 30: return 'Slow'
    else: return 'Very-slow (lagoon-like)'
```

---

## 🔬 Scientific References

1. **Venice System (1958)**
   - Symposium on the Classification of Brackish Waters
   - Established international salinity thresholds

2. **O'Connor et al. (2022)** - Tidal Freshwater Zones
   - DOI: 10.1016/j.ecss.2022.107786
   - Defines TFZ characteristics and biogeochemical significance

3. **Savenije (2012)** - Salinity and Tides in Alluvial Estuaries
   - Predictive equations for salinity intrusion length

---

## 🎯 Use Cases

1. **Biogeochemical Modeling**
   - GHG emissions (CO₂, CH₄, N₂O) vary by salinity zone
   - Carbon cycling and burial rates
   - Nutrient transformations

2. **Ecosystem Management**
   - Species distributions follow salinity gradients
   - Freshwater vs marine habitat delineation
   - Critical habitat identification (TFZ)

3. **Water Quality**
   - Drinking water intakes (avoid saline intrusion)
   - Irrigation suitability
   - Coastal aquifer management

---

## 📊 Expected Results

### Global Coverage:
- **Freshwater**: ~85-90% of river length
- **Oligohaline (TFZ)**: ~5-10% of river length (biogeochemically critical!)
- **Mesohaline**: ~2-3% of river length
- **Polyhaline**: ~1-2% of river length
- **Euhaline**: <1% of river length (coastal transition)

### Regional Variation:
- **High-discharge rivers** (Amazon, Congo): TFZ 50-200 km
- **Low-discharge rivers**: TFZ 10-50 km
- **Arid regions**: Shorter estuaries, less freshwater influence

---

## 🔗 Dependencies

**Data inputs** (from other folders):
- `scripts/raw_data_processing/` → GRIT segments with initial classification
- `scripts/ml_salinity/` → ML salinity predictions (fills GlobSalt gaps)

**Outputs used by**:
- `scripts/surface_area_calculation/` → Calculate area by salinity zone
- `scripts/web_optimization/` → Interactive salinity maps

---

## 🚀 Implementation Priority

**Phase 2 - High Priority**

1. ✅ `classify_venice_system.py` - Core classification (Week 1)
2. ✅ `identify_tfz_extents.py` - TFZ delineation (Week 2)
3. ⚪ `classify_by_residence_time.py` - Advanced analysis (Week 3-4)

---

**Created**: October 13, 2025  
**Status**: Folder structure ready, awaiting Phase 2 implementation  
**Next**: Implement classify_venice_system.py after ML pipeline completes
