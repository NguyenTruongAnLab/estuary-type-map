# HydroSHEDS Data Attributes Dictionary

**Data Source**: HydroSHEDS RiverATLAS & BasinATLAS v1.0  
**DOI**: [10.5067/9SQ1S6VFQQ20](https://doi.org/10.5067/9SQ1S6VFQQ20)  
**Purpose**: Reference guide for all extracted attributes

---

## 📊 RiverATLAS Attributes (14 selected from 283 total)

### Identification & Network

| Attribute | Type | Unit | Range | Description | Use in Project |
|-----------|------|------|-------|-------------|----------------|
| `HYRIV_ID` | int64 | - | 1 - 8,472,302 | Unique river reach identifier | Linking, joining datasets |
| `NEXT_DOWN` | int64 | - | 0 - 8,472,302 | ID of downstream reach (0 = ocean) | Network topology, flow routing |
| `MAIN_RIV` | string | - | - | Name of main river | Display, labeling |
| `LENGTH_KM` | float | km | 0.01 - 500 | Reach length | Scale, context |

### Hydrology (Tidal Classification)

| Attribute | Type | Unit | Range | Description | Use in Project |
|-----------|------|------|-------|-------------|----------------|
| `dis_m3_pyr` | float | m³/s | 0 - 300,000 | Mean annual discharge | **Primary tidal classifier**: Large rivers maintain tidal influence further upstream |
| `dis_m3_pmn` | float | m³/s | 0 - 200,000 | Mean monthly minimum discharge | Seasonal variation, low flow |
| `dis_m3_pmx` | float | m³/s | 0 - 400,000 | Mean monthly maximum discharge | Seasonal variation, high flow |
| `run_mm_syr` | float | mm/year | 0 - 10,000 | Mean annual runoff | Watershed wetness |

### Coastal Proximity (Primary Filter)

| Attribute | Type | Unit | Range | Description | Use in Project |
|-----------|------|------|-------|-------------|----------------|
| `dis_ocean` | float | km | 0 - 500 | Distance to ocean | **Coastal filtering**: Only keep reaches within 500km. **Tidal zone**: <50km typically tidal |

### Topography (Tidal Limit)

| Attribute | Type | Unit | Range | Description | Use in Project |
|-----------|------|------|-------|-------------|----------------|
| `ele_mt_sav` | float | m | -10 - 6,000 | Mean elevation of reach | **Tidal limit**: Tidal influence rare above 10m elevation |
| `slp_dg_sav` | float | degrees | 0 - 45 | Mean slope of reach | Gradient, flow velocity |

### River Classification

| Attribute | Type | Unit | Range | Description | Use in Project |
|-----------|------|------|-------|-------------|----------------|
| `ord_stra` | int | - | 1 - 12 | Strahler stream order | River size, importance |
| `ord_clas` | int | - | 1 - 10 | Stream order class | Simplified classification |

### Climate Context

| Attribute | Type | Unit | Range | Description | Use in Project |
|-----------|------|------|-------|-------------|----------------|
| `tmp_dc_syr` | float | °C | -30 - 35 | Mean annual temperature | Climate context |
| `pre_mm_syr` | float | mm/year | 0 - 10,000 | Mean annual precipitation | Freshwater input |
| `aet_mm_syr` | float | mm/year | 0 - 2,000 | Mean annual evapotranspiration | Water balance |

---

## 🌊 River Classification Thresholds

### Tidal-Influenced Rivers
```python
is_tidal = (
    (dis_ocean <= 50) &      # Within 50km of coast
    (ele_mt_sav <= 10) &     # Below 10m elevation
    (dis_m3_pyr > 1)         # Active flow
)
```

**Criteria**:
- Distance to ocean: **≤ 50 km** (standard tidal limit)
- Elevation: **≤ 10 m** (tidal influence rare above this)
- Discharge: **> 1 m³/s** (excludes intermittent streams)

**Extended tidal zone for large rivers**:
```python
is_tidal_large = (
    (dis_ocean <= 100) &     # Within 100km for large rivers
    (ele_mt_sav <= 10) &
    (dis_m3_pyr > 100)       # Large discharge (>100 m³/s)
)
```

### Freshwater Perennial Rivers
```python
is_freshwater = ~is_tidal
```

All other rivers beyond tidal influence zone.

---

## 🗺️ BasinATLAS Attributes (13 selected from 281 total)

### Identification

| Attribute | Type | Unit | Range | Description | Use in Project |
|-----------|------|------|-------|-------------|----------------|
| `HYBAS_ID` | int64 | - | - | Unique basin identifier | Linking, joining |
| `NEXT_DOWN` | int64 | - | - | Downstream basin ID | Network topology |
| `MAIN_BAS` | int64 | - | - | Main basin ID | Grouping |
| `SUB_AREA` | float | km² | 0.01 - 5,000,000 | Sub-basin area | Context, scale |

### Hydrology

| Attribute | Type | Unit | Range | Description | Use in Project |
|-----------|------|------|-------|-------------|----------------|
| `dis_m3_pyr` | float | m³/s | 0 - 300,000 | Mean annual discharge | Estuary enrichment |

### Land Cover (Estuary Context)

| Attribute | Type | Unit | Range | Description | Use in Project |
|-----------|------|------|-------|-------------|----------------|
| `for_pc_sse` | float | % | 0 - 100 | Forest cover percentage | Land use analysis |
| `crp_pc_sse` | float | % | 0 - 100 | Cropland cover percentage | Agricultural impact |
| `urb_pc_sse` | float | % | 0 - 100 | Urban cover percentage | Anthropogenic pressure |
| `wet_pc_sse` | float | % | 0 - 100 | Wetland cover percentage | Ecosystem context |

### Soil Characteristics

| Attribute | Type | Unit | Range | Description | Use in Project |
|-----------|------|------|-------|-------------|----------------|
| `soc_th_sav` | float | tons/ha | 0 - 500 | Soil organic carbon | Nutrient context |
| `cly_pc_sav` | float | % | 0 - 100 | Clay content | Sediment characteristics |
| `snd_pc_sav` | float | % | 0 - 100 | Sand content | Sediment characteristics |

---

## 📈 Data Coverage & Completeness

### RiverATLAS (Coastal Reaches)
- **Total reaches**: 8,472,302 (global)
- **Coastal reaches** (<500km): 1,248,673 (14.7%)
- **Attribute completeness**: >99% for selected fields
- **Geographic coverage**: Global, excluding Antarctica
- **Spatial resolution**: Variable, ~500m - 5km

### BasinATLAS (Levels 6 & 8)
- **Level 6 basins**: ~350,000 (larger basins)
- **Level 8 basins**: ~1,200,000 (detailed basins)
- **Attribute completeness**: >95% for selected fields
- **Geographic coverage**: Global terrestrial drainage basins

---

## 🔄 Data Processing Pipeline

```mermaid
graph LR
    A[Raw HydroSHEDS<br/>~2.5GB] --> B[Filter Coastal<br/>-85%]
    B --> C[Select Attributes<br/>-95%]
    C --> D[Simplify Geometry<br/>-70%]
    D --> E[Compressed<br/>~280MB]
```

**Compression stages**:
1. **Coastal filtering**: 8.5M → 1.25M reaches (85% reduction)
2. **Attribute selection**: 283 → 14 columns (95% reduction)
3. **Geometry simplification**: 0.01° tolerance (70% reduction)
4. **GeoPackage format**: Native compression (30% reduction)

**Overall compression**: ~2.5GB → ~280MB (**11x compression**)

---

## 💡 Usage Examples

### Example 1: Find large tidal rivers

```python
import geopandas as gpd

rivers = gpd.read_file('data/hydrosheds/processed/rivers_coastal.gpkg')

# Large tidal rivers (>50 m³/s, within tidal zone)
large_tidal = rivers[
    (rivers['dis_ocean'] <= 50) &
    (rivers['ele_mt_sav'] <= 10) &
    (rivers['dis_m3_pyr'] > 50)
]

print(f"Found {len(large_tidal):,} large tidal rivers")
print(large_tidal[['MAIN_RIV', 'dis_m3_pyr', 'dis_ocean']].head(10))
```

### Example 2: Classify by distance to ocean

```python
# Create distance categories
rivers['distance_category'] = pd.cut(
    rivers['dis_ocean'],
    bins=[0, 10, 50, 100, 500],
    labels=['Estuary (<10km)', 'Tidal (10-50km)', 
            'Coastal (50-100km)', 'Inland (100-500km)']
)

# Count by category
print(rivers['distance_category'].value_counts())
```

### Example 3: Export high-discharge reaches

```python
# Export reaches with discharge > 100 m³/s
high_discharge = rivers[rivers['dis_m3_pyr'] > 100].copy()

high_discharge.to_file(
    'data/rivers_high_discharge.geojson',
    driver='GeoJSON'
)

print(f"Exported {len(high_discharge):,} high-discharge reaches")
```

---

## 📚 References

### Primary Publications

1. **Linke, S., Lehner, B., et al.** (2019). Global hydro-environmental sub-basin and river reach characteristics at high spatial resolution. *Scientific Data*, 6, 283. DOI: [10.1038/s41597-019-0300-6](https://doi.org/10.1038/s41597-019-0300-6)

2. **Lehner, B., Grill, G.** (2013). Global river hydrography and network routing: baseline data and new approaches to study the world's large river systems. *Hydrological Processes*, 27(15), 2171-2186. DOI: [10.1002/hyp.9740](https://doi.org/10.1002/hyp.9740)

### Documentation

- **HydroATLAS Documentation**: https://www.hydrosheds.org/products/hydroatlas
- **Technical Paper**: https://www.nature.com/articles/s41597-019-0300-6
- **Attribute Catalog**: https://data.hydrosheds.org/file/technical-documentation/RiverATLAS_Catalog_v10.xlsx

---

## 🔗 Related Documentation

- [Download Guide](DOWNLOAD_GUIDE.md) - Step-by-step download instructions
- [Processing Guide](PROCESSING_GUIDE.md) - Data compression workflow
- [Main README](../raw/README.md) - Complete HydroSHEDS guide
- [Project Technical Docs](../../../docs/TECHNICAL.md) - Overall project documentation

---

**Last Updated**: October 10, 2025  
**Version**: 1.0  
**Maintainer**: Global Estuary Type Map Project
