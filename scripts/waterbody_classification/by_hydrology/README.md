# 🌊 Hydrology-Based Classification

**Scientific Framework**: Stream order theory + discharge regimes

**Purpose**: Classify water bodies by hydrological characteristics for water resource management

---

## 🎯 Classification Schemes

### Stream Order Classification (Strahler 1957)

| Order | Characteristics | Global % | Examples |
|-------|----------------|----------|----------|
| **1-2** | Headwater streams, ephemeral flow | 70% | Mountain brooks, tributaries |
| **3-4** | Small rivers, perennial flow | 20% | Local rivers |
| **5-6** | Medium rivers, regional significance | 7% | Rhine, Thames |
| **7-8** | Large rivers, continental scale | 2% | Mississippi, Danube |
| **9-12** | Great rivers, global importance | <1% | Amazon, Nile, Yangtze |

---

## 📁 Scripts (To Be Implemented)

### 1. classify_by_stream_order.py
**Status**: ⏳ Planned (Phase 2)  
**Purpose**: Classify segments by Strahler stream order

**Input**:
- `data/processed/rivers_grit_segments_*.gpkg` (has `strahler_order` attribute)

**Output**:
- `data/processed/classified_stream_order_*.gpkg`

**Method**:
```python
def classify_stream_order(order):
    if order <= 2: return 'Headwater'
    elif order <= 4: return 'Small River'
    elif order <= 6: return 'Medium River'
    elif order <= 8: return 'Large River'
    else: return 'Great River'
```

---

### 2. classify_by_discharge.py
**Status**: ⏳ Planned (Phase 2)  
**Purpose**: Classify by flow regime

**Input**:
- DynQual discharge data
- GRIT topology (drainage area proxy)

**Output**:
- `data/processed/classified_discharge_*.gpkg`

**Method**:
```python
def classify_discharge_regime(mean_discharge_m3s, cv_discharge):
    """
    CV = Coefficient of variation (std/mean)
    Indicates flow variability
    """
    if mean_discharge_m3s < 1:
        size = 'Ephemeral'
    elif mean_discharge_m3s < 100:
        size = 'Small'
    elif mean_discharge_m3s < 1000:
        size = 'Medium'
    else:
        size = 'Large'
    
    if cv_discharge > 1.0:
        variability = 'Highly Variable'
    elif cv_discharge > 0.5:
        variability = 'Moderately Variable'
    else:
        variability = 'Stable'
    
    return f'{size} ({variability})'
```

---

### 3. classify_drainage_patterns.py
**Status**: ⏳ Planned (Phase 2)  
**Purpose**: Identify drainage network patterns

**Input**:
- GRIT topology (bifurcations, confluences)
- Basin boundaries

**Output**:
- `data/processed/classified_drainage_patterns_*.gpkg`

**Method**:
```python
def classify_drainage_pattern(basin_topology):
    """
    Drainage patterns reflect geological structure
    """
    # Dendritic: Tree-like, random branching (most common)
    # Trellis: Parallel tributaries, folded geology
    # Radial: Flowing from central high point (volcanoes)
    # Rectangular: Right-angle bends, jointed bedrock
    # Parallel: Uniform slope, coastal areas
    
    bifurcation_ratio = calculate_bifurcation_ratio(basin_topology)
    junction_angles = calculate_junction_angles(basin_topology)
    
    if junction_angles.std() < 20:
        return 'Parallel'
    elif bifurcation_ratio > 4:
        return 'Dendritic'
    elif dominant_angle_90_degrees(junction_angles):
        return 'Rectangular' if bifurcation_ratio < 3 else 'Trellis'
    else:
        return 'Radial'
```

---

### 4. identify_endorheic.py
**Status**: ⏳ Planned (Phase 2)  
**Purpose**: Identify closed basins (no outlet to ocean)

**Input**:
- GRIT topology (coastal outlet flag)
- Basin boundaries

**Output**:
- `data/processed/classified_endorheic_*.gpkg`

**Method**:
```python
def identify_endorheic(basin):
    """
    Endorheic basins drain to internal sinks (lakes, playas)
    Important for salt accumulation, unique biogeochemistry
    """
    has_coastal_outlet = basin['is_coastal'] == 1
    
    if not has_coastal_outlet:
        # Check if drains to major lake
        downstream_terminal = find_downstream_terminal(basin)
        
        if is_lake(downstream_terminal):
            return 'Endorheic (Lake)'
        else:
            return 'Endorheic (Playa/Salt Flat)'
    else:
        return 'Exorheic (Ocean)'
```

---

## 🔬 Scientific References

1. **Strahler (1957)** - Quantitative Analysis of Watershed Geomorphology
   - Established stream order system
   - Foundational for river network analysis

2. **Horton (1945)** - Erosional Development of Streams
   - Laws of drainage basin composition
   - Bifurcation ratios and network structure

3. **Poff et al. (1997)** - The Natural Flow Regime
   - Flow variability classification
   - Ecological flow requirements

---

## 🎯 Use Cases

1. **Water Resource Management**
   - Stream order → water abstraction potential
   - Discharge regime → reservoir design
   - Endorheic basins → unique management challenges

2. **Flood Risk Assessment**
   - High-order streams → major flood risk
   - Discharge variability → flashiness, prediction difficulty
   - Drainage patterns → runoff response

3. **Ecological Classification**
   - Stream order → habitat size, species diversity
   - Flow regime → ecosystem types (perennial vs intermittent)
   - Drainage patterns → connectivity, migration corridors

---

## 📊 Expected Results

### Global Stream Order Distribution:
- **Order 1-2**: ~14 million segments (70%)
- **Order 3-4**: ~4 million segments (20%)
- **Order 5-6**: ~1.4 million segments (7%)
- **Order 7-8**: ~400K segments (2%)
- **Order 9-12**: ~100K segments (<1%)

### Discharge Regime Distribution:
- **Perennial (stable)**: ~50% of river length
- **Perennial (variable)**: ~30% of river length
- **Intermittent**: ~15% of river length
- **Ephemeral**: ~5% of river length

### Endorheic vs Exorheic:
- **Exorheic (ocean)**: ~90% of global drainage
- **Endorheic (closed)**: ~10% of global drainage
  - Major endorheic basins: Caspian Sea, Great Basin, Lake Chad

---

## 🔗 Dependencies

**Data inputs**:
- `scripts/raw_data_processing/process_grit_all_regions.py` → Strahler order, topology
- `scripts/ml_salinity/add_dynqual_to_features.py` → Discharge data

**Outputs used by**:
- `scripts/waterbody_classification/integrated/` → Multi-criteria classification
- `scripts/surface_area_calculation/` → Calculate area by stream order
- `scripts/web_optimization/` → Interactive hydrology maps

---

## 🚀 Implementation Priority

**Phase 2 - Medium Priority**

1. ✅ `classify_by_stream_order.py` - Simple (data already available) (Week 1)
2. ⚪ `identify_endorheic.py` - Moderate (topology analysis) (Week 2)
3. ⚪ `classify_by_discharge.py` - Moderate (needs DynQual integration) (Week 3)
4. ⚪ `classify_drainage_patterns.py` - Complex (topology analysis) (Week 4)

---

**Created**: October 13, 2025  
**Status**: Folder structure ready, awaiting Phase 2 implementation  
**Next**: Implement classify_by_stream_order.py (simplest, data ready)
