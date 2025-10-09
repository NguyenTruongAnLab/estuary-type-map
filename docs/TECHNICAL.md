# Technical Documentation

## Data Processing Pipeline

### Overview

The data processing pipeline reads real estuary data from open-access scientific datasets and converts them into web-ready GeoJSON format suitable for Leaflet.js visualization.

### Data Sources

1. **Dürr et al. (2011)** - Worldwide typology shapefiles (~6,200 estuary catchments)
   - File: `data/Worldwide-typology-Shapefile-Durr_2011/typology_catchments.shp`
   - Provides: Estuary typology, basin areas, ocean/sea names, geographical boundaries

2. **Baum et al. (2024)** - Large estuary morphometry CSV (271 embayments)
   - File: `data/Large-estuaries-Baum_2024/Baum_2024_Geomorphology.csv`
   - Provides: Mouth width, embayment length, geomorphotype classification

3. **Athanasiou et al. (2024)** - Global Coastal Characteristics (optional, not included)
   - File: `data/GCC-Panagiotis-Athanasiou_2024/GCC_geophysical.csv` (>200MB)
   - Provides: Land use, slope, elevation, mangrove coverage at 1km resolution
   - Download from: https://zenodo.org/records/11072020

### Process Flow

1. **Data Loading**: Read Dürr et al. (2011) shapefile with GeoPandas
2. **Filtering**: Select valid estuaries (exclude endorheic, glaciated, arheic systems)
3. **Sampling**: Choose representative estuaries for visualization (prioritize larger basins)
4. **Enrichment**: Match with Baum et al. (2024) morphometry where available
5. **Geometry Extraction**: Convert polygons to point centroids for web mapping
6. **Metadata Addition**: Add provenance fields (data sources, DOIs)
7. **GeoJSON Generation**: Write to `data/estuaries.geojson`
8. **Validation**: Verify structure and attribute completeness

### Python Script Details

**File**: `scripts/process_estuary_data.py`

**Dependencies**:
```bash
pip install geopandas pandas pyproj
```

**Functions**:
- `load_durr_data(shapefile_path)`: Loads and filters Dürr et al. (2011) shapefile
- `load_baum_data(csv_path)`: Loads Baum et al. (2024) CSV
- `create_estuary_features(durr_gdf, baum_df)`: Creates GeoJSON features with enrichment
- `main()`: Orchestrates the complete data processing pipeline

**Type Mapping** (from Dürr FIN_TYP codes):
- Type 1: Small Delta
- Type 2: Tidal System
- Type 3: Lagoon
- Type 4: Fjord/Fjaerd
- Type 5: Large River
- Type 51: Large River with Tidal Delta
- Type 6: Karst

**Output Data Structure**:
```python
{
    "type": "FeatureCollection",
    "metadata": {
        "data_sources": [...],
        "note": "Laruelle et al. (2025) used only for validation...",
        "gcc_note": "GCC data can be added by downloading...",
        "generated_date": "ISO timestamp"
    },
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [longitude, latitude]
            },
            "properties": {
                "name": "Estuary Name",
                "type": "Geomorphological Type (e.g., Small Delta (Type I))",
                "type_code": 1,
                "basin_area_km2": 1000.5,
                "sea_name": "Ocean/Sea Name",
                "ocean_name": "Ocean Name",
                "data_source": "Dürr et al. (2011)",
                "data_source_doi": "10.1007/s12237-011-9381-y",
                # Optional Baum enrichment fields:
                "baum_embayment_name": "...",
                "baum_mouth_width_m": 5000,
                "baum_length_m": 8000,
                "baum_geomorphotype": "...",
                "baum_data_source": "Baum et al. (2024)"
            }
        }
    ]
}
```

## Front-End Architecture

### HTML Structure

**index.html** uses a grid layout with four main areas:
- Header: Title and subtitle
- Sidebar: Filters, legend, and definitions
- Map: Leaflet.js interactive map
- Footer: Attribution and links

### CSS Design System

**style.css** implements:
- CSS Grid for responsive layout
- Color scheme based on estuary types
- Custom popup styling
- Mobile-responsive breakpoints
- Professional typography and spacing

### JavaScript Components

**map.js** includes:

**Core Functions**:
- `initMap()`: Initialize Leaflet map
- `loadEstuaryData()`: Fetch and parse GeoJSON
- `createMarker()`: Generate custom markers
- `createPopupContent()`: Build popup HTML
- `updateMarkers()`: Refresh displayed markers
- `setupFilters()`: Initialize filter checkboxes

**Data Management**:
- `estuaryData`: GeoJSON feature collection
- `markersLayer`: Leaflet layer group for markers
- `activeFilters`: Set of currently active type filters

**Event Handlers**:
- Filter checkbox changes
- Window resize events
- Marker click events

## Estuary Type Definitions

### Delta
**Formation**: Sediment deposition at river mouth  
**Characteristics**: 
- High sediment load
- Distributary networks
- Active land building
- Often triangular or bird's-foot shape

**Examples**: Ganges-Brahmaputra, Nile, Mississippi

### Fjord
**Formation**: Glacial erosion  
**Characteristics**:
- Deep, narrow inlets
- Steep sides
- U-shaped valleys
- Threshold sills at mouth
- High latitude locations

**Examples**: Sognefjord, Milford Sound

### Lagoon
**Formation**: Barrier island/reef separation  
**Characteristics**:
- Shallow water bodies
- Restricted ocean connection
- Variable salinity
- Protected from wave energy

**Examples**: Venetian Lagoon, Pamlico Sound

### Ria
**Formation**: Drowned river valley  
**Characteristics**:
- V-shaped cross-section
- Branching pattern
- Deeper than coastal plain estuaries
- Follow original valley morphology

**Examples**: Ria de Vigo, Sydney Harbour

### Coastal Plain
**Formation**: Sea level rise in low-relief areas  
**Characteristics**:
- Wide, shallow
- Funnel-shaped
- Gradual slopes
- Common on passive margins

**Examples**: Chesapeake Bay, Thames Estuary

### Bar-Built
**Formation**: Sediment barriers from wave action  
**Characteristics**:
- Protected by barriers
- Offshore bars or spits
- Reduced wave energy
- Variable circulation

**Examples**: Singapore Strait, Murray Mouth

### Tectonic
**Formation**: Geological faulting/subsidence  
**Characteristics**:
- Structurally controlled
- Fault-bounded
- Variable morphology
- Less predictable patterns

**Examples**: San Francisco Bay

## Color Scheme

The project uses distinct colors for each estuary type to enhance visual differentiation:

- **Delta**: `#8b4513` (Saddle Brown) - representing sediment
- **Fjord**: `#4a90e2` (Bright Blue) - representing deep water
- **Lagoon**: `#50c878` (Emerald Green) - representing shallow, protected waters
- **Ria**: `#9370db` (Medium Purple) - representing drowned valleys
- **Coastal Plain**: `#ff8c00` (Dark Orange) - representing wide estuaries
- **Bar-Built**: `#20b2aa` (Light Sea Green) - representing barriers
- **Tectonic**: `#dc143c` (Crimson) - representing geological activity

## Performance Considerations

### Current Implementation
- Static GeoJSON file (~31 estuaries)
- Simple marker rendering
- Client-side filtering
- No clustering (not needed for current dataset size)

### Scaling Strategy
For datasets with 1000+ estuaries:
1. Implement marker clustering (Leaflet.markercluster)
2. Use spatial indexing for faster filtering
3. Consider server-side API for data delivery
4. Implement lazy loading for definitions
5. Add search functionality

## Browser Compatibility

Tested and compatible with:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)

### Required Features
- ES6 JavaScript support
- CSS Grid support
- Fetch API
- SVG rendering for markers

## Accessibility

Current implementation includes:
- Semantic HTML structure
- ARIA labels (to be enhanced)
- Keyboard navigation for checkboxes
- Color contrast ratios meeting WCAG AA standards
- Responsive design for different screen sizes

Future improvements:
- Screen reader announcements for filter changes
- Keyboard navigation for map markers
- High contrast mode support
- Focus indicators for all interactive elements

## API Reference

### Map Configuration

```javascript
map = L.map('map', {
    center: [20, 0],      // Latitude, Longitude
    zoom: 2,              // Initial zoom level
    minZoom: 2,           // Minimum zoom (global view)
    maxZoom: 18,          // Maximum zoom
    worldCopyJump: true   // Wrap around globe
});
```

### Marker Creation

```javascript
const icon = L.divIcon({
    className: 'custom-marker',
    html: '<div style="..."></div>',
    iconSize: [16, 16],
    iconAnchor: [8, 8]
});

const marker = L.marker([lat, lng], { icon: icon });
```

### Popup Binding

```javascript
marker.bindPopup(content, {
    maxWidth: 300,
    className: 'estuary-popup'
});
```

## Testing Checklist

### Functional Testing
- [ ] Map loads with correct center and zoom
- [ ] All 31 estuaries display as markers
- [ ] Each marker has correct color for its type
- [ ] Popups open with complete information
- [ ] Filters show/hide markers correctly
- [ ] "All Types" master filter works
- [ ] Individual type filters work independently
- [ ] Counts update correctly

### Visual Testing
- [ ] Header gradient displays properly
- [ ] Sidebar scrolls smoothly
- [ ] Markers are visible against map tiles
- [ ] Popups are readable and well-formatted
- [ ] Colors match specification
- [ ] Responsive design works on mobile
- [ ] Footer stays at bottom

### Content Testing
- [ ] All scientific definitions are accurate
- [ ] References are complete and formatted
- [ ] No spelling or grammar errors
- [ ] Links work correctly

### Performance Testing
- [ ] Initial load time < 3 seconds
- [ ] Filter changes are instant
- [ ] No console errors
- [ ] Memory usage is reasonable

## Deployment

### GitHub Pages Setup

1. Push code to GitHub repository
2. Go to repository Settings
3. Navigate to Pages section
4. Select branch (usually `main`)
5. Select root directory
6. Save and wait for deployment

### URL Structure
`https://[username].github.io/[repository-name]/`

For this project:
`https://nguyentruonganlab.github.io/estuary-type-map/`

### Custom Domain (Optional)
1. Add CNAME file with custom domain
2. Configure DNS records at domain provider
3. Enable HTTPS in GitHub Pages settings

## Maintenance

### Regular Updates
- Review and update scientific references
- Add new estuaries from published literature
- Verify coordinate accuracy
- Update Leaflet.js version
- Check for broken links

### Version Control
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Tag releases in Git
- Maintain CHANGELOG.md
- Document breaking changes

## Troubleshooting

### Common Issues

**Issue**: Map doesn't load
- Check browser console for errors
- Verify Leaflet.js CDN is accessible
- Check GeoJSON file path

**Issue**: Markers not displaying
- Verify GeoJSON format is valid
- Check coordinate order (longitude, latitude)
- Inspect console for JavaScript errors

**Issue**: Filters not working
- Check checkbox event listeners are attached
- Verify activeFilters Set is updating
- Test updateMarkers() function

**Issue**: Popups show wrong information
- Verify GeoJSON properties structure
- Check createPopupContent() logic
- Inspect feature.properties in console

## Future Enhancements

### Short-term
- Add search functionality
- Implement marker clustering
- Add statistics dashboard
- Export filtered data as CSV

### Medium-term
- Integration with scientific databases
- Time-series visualizations
- Comparative analysis tools
- User-submitted estuaries (with moderation)

### Long-term
- 3D terrain visualization
- Satellite imagery overlay
- Ecosystem health indicators
- Climate change impact data

## References

### Leaflet.js Documentation
- [Leaflet API Reference](https://leafletjs.com/reference.html)
- [Leaflet Tutorials](https://leafletjs.com/examples.html)
- [GeoJSON Specification](https://geojson.org/)

### Estuary Science
- Estuaries and Coasts (Journal)
- Coastal Research Library (Book Series)
- LOICZ Reports and Publications
