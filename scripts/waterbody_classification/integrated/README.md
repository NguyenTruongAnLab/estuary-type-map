# 🌍 Integrated Multi-Criteria Classification

**Purpose**: Combine multiple classification approaches for comprehensive water body characterization

**Scientific Framework**: Hierarchical and ensemble methods for robust classification

---

## 🎯 Approach

### Why Integrate Multiple Classifications?

Different classification schemes capture different aspects:
- **Salinity**: Biogeochemical processes, ecosystem function
- **Geomorphology**: Physical template, sediment dynamics
- **Hydrology**: Flow regime, water resources
- **Biome**: Climate context, biodiversity patterns

**Integrated classification** provides:
1. ✅ **Comprehensive characterization** - Multiple perspectives
2. ✅ **Robust classification** - Cross-validated by multiple criteria
3. ✅ **Flexible analysis** - Users choose relevant criteria
4. ✅ **Uncertainty quantification** - Agreement across methods

---

## 📁 Scripts (To Be Implemented)

### 1. hierarchical_classification.py
**Status**: ⏳ Planned (Phase 2)  
**Purpose**: Multi-level classification tree

**Input**:
- All classification outputs from subfolders

**Output**:
- `data/processed/hierarchical_classification_*.gpkg`

**Method**:
```python
def hierarchical_classification(segment):
    """
    Classification tree:
    Level 1: Exorheic vs Endorheic
    Level 2: Estuarine vs Non-Tidal
    Level 3: Salinity class (if estuarine)
    Level 4: Geomorphology type (if estuarine)
    Level 5: Stream order (all)
    """
    
    # Level 1: Drainage
    if segment['is_endorheic']:
        return {
            'level_1': 'Endorheic',
            'level_2': 'Closed Basin',
            'final_class': 'Endorheic Lake/Playa'
        }
    
    # Level 2: Tidal influence
    if segment['dist_to_coast_km'] > 200:
        return {
            'level_1': 'Exorheic',
            'level_2': 'Non-Tidal Riverine',
            'level_3': f"Order {segment['strahler_order']}",
            'final_class': f"Non-Tidal River (Order {segment['strahler_order']})"
        }
    
    # Level 3: Salinity (estuarine)
    venice_class = segment['venice_class']
    
    # Level 4: Geomorphology
    if segment['in_durr_catchment']:
        durr_type = segment['durr_type']
        
        return {
            'level_1': 'Exorheic',
            'level_2': 'Estuarine',
            'level_3': venice_class,
            'level_4': durr_type,
            'final_class': f"{venice_class} {durr_type} Estuary"
        }
    else:
        return {
            'level_1': 'Exorheic',
            'level_2': 'Estuarine',
            'level_3': venice_class,
            'final_class': f"{venice_class} Estuary (Type Unknown)"
        }
```

---

### 2. fuzzy_classification.py
**Status**: ⏳ Planned (Phase 2)  
**Purpose**: Handle transitional zones with fuzzy logic

**Input**:
- All classification outputs
- Confidence scores from ML

**Output**:
- `data/processed/fuzzy_classification_*.gpkg`
- Membership scores for each class (0-1)

**Method**:
```python
def fuzzy_membership(segment):
    """
    Many segments are transitional (e.g., salinity gradient)
    Fuzzy logic assigns membership scores instead of hard boundaries
    """
    
    salinity = segment['salinity_psu']
    
    # Example: Oligohaline membership (0.5-5 PSU)
    if salinity < 0.5:
        oligohaline_score = 0.0
    elif salinity < 2.75:  # Mid-range
        oligohaline_score = (salinity - 0.5) / 2.25  # Ramp up
    elif salinity < 5.0:
        oligohaline_score = (5.0 - salinity) / 2.25  # Ramp down
    else:
        oligohaline_score = 0.0
    
    # Similar for all classes
    return {
        'freshwater_score': calculate_freshwater_membership(salinity),
        'oligohaline_score': oligohaline_score,
        'mesohaline_score': calculate_mesohaline_membership(salinity),
        # ... etc
        'dominant_class': class_with_max_score()
    }
```

---

### 3. ensemble_classification.py
**Status**: ⏳ Planned (Phase 2)  
**Purpose**: Weighted combination of multiple classifications

**Input**:
- All classification outputs
- User-defined weights

**Output**:
- `data/processed/ensemble_classification_*.gpkg`

**Method**:
```python
def ensemble_classification(segment, weights):
    """
    Combine multiple classifications with user-defined weights
    
    Example weights:
    {
        'salinity': 0.4,      # 40% (most important for biogeochem)
        'geomorphology': 0.3, # 30% (physical template)
        'hydrology': 0.2,     # 20% (flow regime)
        'biome': 0.1          # 10% (climate context)
    }
    """
    
    # Get classification from each method
    salinity_class = segment['venice_class']
    geomorph_class = segment['durr_type']
    hydro_class = segment['stream_order_class']
    biome_class = segment['climate_zone']
    
    # Convert to numeric scores
    salinity_score = encode_salinity(salinity_class)
    geomorph_score = encode_geomorphology(geomorph_class)
    hydro_score = encode_hydrology(hydro_class)
    biome_score = encode_biome(biome_class)
    
    # Weighted average
    ensemble_score = (
        weights['salinity'] * salinity_score +
        weights['geomorphology'] * geomorph_score +
        weights['hydrology'] * hydro_score +
        weights['biome'] * biome_score
    )
    
    # Convert back to class
    final_class = decode_ensemble_score(ensemble_score)
    
    return {
        'ensemble_class': final_class,
        'confidence': calculate_confidence(segment, weights),
        'agreement': calculate_agreement_across_methods(segment)
    }
```

---

## 🔬 Scientific Rationale

### Hierarchical Classification:
- **Pro**: Clear decision tree, easy to interpret
- **Con**: Hard boundaries, doesn't capture transitions
- **Use when**: Need simple, categorical classification

### Fuzzy Classification:
- **Pro**: Captures gradients and transitions naturally
- **Con**: More complex, harder to map
- **Use when**: Studying transitional zones (e.g., salinity gradients)

### Ensemble Classification:
- **Pro**: Flexible, user can prioritize criteria
- **Con**: Requires weight selection (subjective)
- **Use when**: Different stakeholders have different priorities

---

## 🎯 Use Cases

### 1. Biogeochemical Modeling
**Priority**: Salinity (40%), Geomorphology (30%), Hydrology (20%), Biome (10%)

**Rationale**: GHG emissions primarily driven by salinity, modified by physical template and flow regime

### 2. Biodiversity Assessment
**Priority**: Biome (35%), Salinity (30%), Geomorphology (25%), Hydrology (10%)

**Rationale**: Climate and salinity are primary drivers of species distributions

### 3. Water Resource Management
**Priority**: Hydrology (50%), Salinity (25%), Biome (15%), Geomorphology (10%)

**Rationale**: Flow regime and water quality are management priorities

---

## 📊 Expected Results

### Classification Agreement:
- **High agreement** (>80% across methods): ~60% of segments
  - Clear freshwater rivers, clear marine estuaries
- **Moderate agreement** (50-80%): ~30% of segments
  - Transitional zones, complex systems
- **Low agreement** (<50%): ~10% of segments
  - Novel or ambiguous systems, data gaps

### Uncertainty Patterns:
- **Low uncertainty**: Large rivers, well-studied estuaries
- **High uncertainty**: Small streams, remote regions, complex deltas

---

## 🔗 Dependencies

**Data inputs** (from all classification folders):
- `by_salinity/` → Venice System, TFZ
- `by_geomorphology/` → Dürr types, basin shape
- `by_hydrology/` → Stream order, discharge regime
- `by_biome/` → Climate zones (future)

**Outputs used by**:
- `scripts/surface_area_calculation/` → Calculate area by integrated class
- `scripts/web_optimization/` → Interactive multi-layer maps
- **Publication**: Tables and figures for manuscript

---

## 🚀 Implementation Priority

**Phase 2 - High Priority (After individual classifications)**

1. ✅ `hierarchical_classification.py` - Decision tree (Week 5)
2. ⚪ `ensemble_classification.py` - Weighted combination (Week 6)
3. ⚪ `fuzzy_classification.py` - Transitional zones (Week 7)

---

## 📖 Example Use Case

### Global Estuary Atlas (This Project!)

**User story**: Create comprehensive estuary classification for GHG modeling

**Approach**:
1. Run all classification scripts (by_salinity, by_geomorphology, by_hydrology)
2. Use `ensemble_classification.py` with biogeochemical weights:
   ```python
   weights = {
       'salinity': 0.5,      # Primary driver of GHG emissions
       'geomorphology': 0.3, # Affects residence time, mixing
       'hydrology': 0.2      # Flow regime affects loading
   }
   ```
3. Generate final classification with confidence levels
4. Calculate surface areas by integrated class
5. Apply emission factors by class
6. Aggregate to global GHG budget

---

**Created**: October 13, 2025  
**Status**: Folder structure ready, awaiting Phase 2 implementation  
**Next**: Implement after individual classification methods complete (Week 5+)
