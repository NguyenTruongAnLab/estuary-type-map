# Visualization Modes

This document describes the different visualization modes available in the Global Estuary Type Map.

## Overview

The map supports two distinct visualization modes that can be toggled with a single click:
- **📍 Estuary Points Mode**: Individual estuary locations
- **🌐 Coastal Segments Mode**: Global coastline colored by estuary type

## Mode Comparison

| Feature | Points Mode | Coastal Segments Mode |
|---------|-------------|----------------------|
| **Purpose** | Explore individual estuaries | View regional patterns |
| **Feature Count** | 6,226 estuaries | 8,439 coastline segments |
| **Geometry Type** | Point | LineString |
| **Data Source** | typology_catchments.shp | typology_coastline.shp |
| **File Size** | 3.2MB | 4.6MB |
| **Best For** | Detailed estuary info | Coastal type distribution |
| **Interactive** | Click markers for details | Click segments for type/length |

## 📍 Estuary Points Mode (Default)

### Description
Displays individual estuary locations as interactive markers on the map. Each marker represents a catchment centroid from the Dürr et al. (2011) worldwide typology dataset.

### Features
- **Total Points**: 6,226 estuaries globally
- **Coverage**: All valid estuaries from Dürr et al. (2011)
- **Color Coding**: Markers colored by estuary type
- **Interactive Popups**: Click to see:
  - Estuary name
  - Geomorphological type (simple and detailed)
  - Basin area (km²)
  - Sea/Ocean name
  - Data source with DOI

### Type Distribution
- **Fjord**: 2,303 estuaries (37%)
- **Delta**: 1,768 estuaries (28%)
- **Coastal Plain**: 1,645 estuaries (26%)
- **Lagoon**: 510 estuaries (8%)

### Use Cases
- Finding specific estuaries by name
- Comparing individual estuary characteristics
- Understanding basin-scale properties
- Detailed morphometric analysis
- Academic research and citation

### Color Scheme
```javascript
Delta: #8b4513 (brown)
Fjord: #4a90e2 (blue)
Lagoon: #50c878 (green)
Coastal Plain: #ff8c00 (orange)
```

## 🌐 Coastal Segments Mode

### Description
Displays global coastlines as colored line segments, with each segment representing a portion of coast classified by its dominant estuary type. Provides a "heat map" view of estuary type distribution along the world's coasts.

### Features
- **Total Segments**: 8,439 coastline features globally
- **Coverage**: Worldwide coastal typology
- **Color Coding**: Lines colored by estuary type
- **Interactive Popups**: Click to see:
  - Estuary type (simple and detailed)
  - Segment length (km)
  - Coastline segment ID
  - Data source with DOI

### Advantages
- **Regional Patterns**: Easily identify areas dominated by specific estuary types
- **Global Overview**: Understand worldwide distribution at a glance
- **Coastal Context**: See how estuary types relate to coastline morphology
- **Scale Understanding**: Better sense of how much coastline each type represents

### Use Cases
- Visualizing regional estuary type dominance
- Understanding global coastal patterns
- Educational demonstrations
- Policy and conservation planning
- Climate change impact assessment

### Technical Details
- **Geometry**: LineString features from typology_coastline.shp
- **Processing**: Filtered to valid estuary types (1-6)
- **Coordinates**: Simplified for web performance
- **Rendering**: Leaflet polylines with type-based styling

## Switching Between Modes

### UI Controls
Two buttons are available in the sidebar:
```
┌─────────────────────────────────────┐
│ 📍 Estuary Points  │ 🌐 Coastal Segments │
└─────────────────────────────────────┘
```

### Behavior
- **On Click**: Mode switches immediately
- **Layer Management**: Previous mode hidden, new mode displayed
- **Filter Persistence**: Active filters apply to new mode
- **Map State**: Zoom level and position maintained
- **Performance**: Efficient layer swapping with no page reload

### Implementation
```javascript
function switchMode(newMode) {
    currentMode = newMode;
    
    if (currentMode === 'points') {
        map.addLayer(markersLayer);
        map.removeLayer(coastlineLayer);
        updateMarkers();
    } else if (currentMode === 'coastline') {
        map.removeLayer(markersLayer);
        map.addLayer(coastlineLayer);
        updateCoastline();
    }
}
```

## Filtering

### Filter Behavior
Filters work consistently across both modes:
- **Points Mode**: Shows/hides markers by type
- **Coastal Mode**: Shows/hides coastline segments by type

### Available Filters
- ☑️ All Types (master toggle)
- ☑️ Delta
- ☑️ Fjord
- ☑️ Lagoon
- ☑️ Coastal Plain

### Real-Time Updates
- Check/uncheck filters for instant updates
- No page reload required
- Counts update dynamically
- Smooth transitions

## Data Provenance

### Points Mode Data
- **Source**: Dürr et al. (2011) - typology_catchments.shp
- **DOI**: 10.1007/s12237-011-9381-y
- **Citation**: Dürr, H.H., et al. (2011). Worldwide typology of nearshore coastal systems: defining the estuarine filter of river inputs to the oceans. *Estuaries and Coasts*, 34(3), 441-458.

### Coastal Segments Mode Data
- **Source**: Dürr et al. (2011) - typology_coastline.shp
- **DOI**: 10.1007/s12237-011-9381-y
- **Citation**: Same as above

### Enrichment Data
- **Source**: Baum et al. (2024) - Large structural estuaries
- **Available in**: Points mode only
- **Provides**: Morphometry data for select large estuaries

## Performance Considerations

### Loading Time
- **Initial Load**: Both datasets loaded on page load
- **Points Mode**: ~1-2 seconds to render 6,226 markers
- **Coastal Mode**: ~1-2 seconds to render 8,439 segments
- **Mode Switch**: Instant (<100ms)

### File Sizes
- **estuaries.geojson**: 3.2MB
- **coastline.geojson**: 4.6MB
- **Total**: 7.8MB data transfer
- **Optimization**: GeoJSON with rounded coordinates

### Browser Performance
- **Recommended**: Modern browsers (Chrome, Firefox, Safari, Edge)
- **Minimum**: 4GB RAM
- **Map Library**: Leaflet.js (lightweight, fast)
- **Rendering**: Hardware-accelerated when available

## Future Enhancements

### Potential Additions
1. **Clustering**: Marker clustering for better performance at global zoom
2. **Heatmaps**: Density visualization option
3. **Animation**: Transition animations between modes
4. **Statistics**: Real-time statistics panel showing filtered data
5. **Export**: Download filtered data as GeoJSON/CSV
6. **Search**: Find estuaries by name or location
7. **Compare**: Side-by-side mode comparison

### River Network Mode
- **Status**: Planned but not yet implemented
- **Requirements**: External HydroRIVERS/HydroSHEDS data
- **Data Size**: ~100MB+ additional data needed
- **Purpose**: Show river networks leading to estuaries
- **Benefits**: Complete river-estuary system visualization

## Scientific Value

### Research Applications
- **Global Analysis**: Compare estuary types across continents
- **Regional Studies**: Focus on specific coastal regions
- **Type Distribution**: Understand global patterns
- **Climate Impacts**: Assess vulnerability by type
- **Conservation**: Identify underrepresented types

### Educational Use
- **Teaching**: Demonstrate estuary classification
- **Visualization**: Show real-world distribution
- **Interactivity**: Hands-on exploration
- **Scale**: Global to local understanding
- **Context**: Coastal geography education

## References

### Primary Data Source
Dürr, H.H., Laruelle, G.G., van Kempen, C.M., Slomp, C.P., Meybeck, M., & Middelkoop, H. (2011). Worldwide typology of nearshore coastal systems: defining the estuarine filter of river inputs to the oceans. *Estuaries and Coasts*, 34(3), 441-458. DOI: 10.1007/s12237-011-9381-y

### Supplementary Data
Baum, M.J., Schüttrumpf, H., & Siemes, R.W. (2024). Large structural estuaries: Their global distribution and morphology. *Geomorphology*, supplementary data.

### Visualization Framework
Agafonkin, V. (2022). Leaflet: An open-source JavaScript library for mobile-friendly interactive maps. https://leafletjs.com/

---

**Version**: 3.0.0 (Full Global Coverage with Dual Visualization Modes)  
**Last Updated**: 2024  
**Maintainer**: NguyenTruongAnLab
