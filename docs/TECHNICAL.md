# Technical Documentation

## Data Processing Pipeline

### Overview

The data processing pipeline converts raw estuary data into a web-ready GeoJSON format suitable for Leaflet.js visualization.

### Process Flow

1. **Data Collection**: Gather estuary data from scientific sources
2. **Classification**: Assign geomorphological types based on published criteria
3. **Validation**: Verify coordinates, attributes, and data completeness
4. **GeoJSON Generation**: Convert to standardized GeoJSON format
5. **Output**: Save to `data/estuaries.geojson`

### Python Script Details

**File**: `scripts/process_estuary_data.py`

**Functions**:
- `create_sample_estuary_data()`: Creates the estuary dataset with classifications
- `main()`: Orchestrates data processing and file output

**Data Structure**:
```python
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [longitude, latitude]
            },
            "properties": {
                "name": "Estuary Name",
                "type": "Geomorphological Type",
                "country": "Country Name",
                "description": "Scientific description",
                "area_km2": 1000,
                "depth_m": 50,
                "river": "River Name"
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
