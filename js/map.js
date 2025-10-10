// Global Estuary Type Map - Main JavaScript
// Data sources: Dürr et al. (2011), Baum et al. (2024)

// Color scheme for different estuary types (updated to match task specification)
const ESTUARY_COLORS = {
    'Delta': '#9467bd',        // Purple
    'Fjord': '#ff7f0e',        // Orange
    'Lagoon': '#8c564b',       // Brown
    'Ria': '#e377c2',          // Pink
    'Coastal Plain': '#1f77b4', // Blue (Tidal River)
    'Bar-Built': '#2ca02c',    // Green
    'Tectonic': '#d62728',     // Red
    'Unknown': '#808080'       // Gray
};

// Global variables
let map;
let estuaryData;
let coastlineData;
let basinData;
let markersLayer;
let coastlineLayer;
let basinLayer;
let activeFilters = new Set();
let currentMode = 'points'; // 'points', 'coastline', or 'basins'

// Initialize the map
function initMap() {
    // Create map centered on global view
    map = L.map('map', {
        center: [20, 0],
        zoom: 2,
        minZoom: 2,
        maxZoom: 18,
        worldCopyJump: true
    });

    // Add tile layer (OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);

    // Create layers for different visualization modes
    markersLayer = L.layerGroup().addTo(map);
    coastlineLayer = L.layerGroup();
    basinLayer = L.layerGroup();

    // Load estuary data
    loadEstuaryData();
    loadCoastlineData();
    loadBasinData();
}

// Load and display estuary data
async function loadEstuaryData() {
    try {
        const response = await fetch('data/estuaries.geojson');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        estuaryData = await response.json();
        
        // Validate data structure
        if (!estuaryData || !estuaryData.features || !Array.isArray(estuaryData.features)) {
            throw new Error('Invalid GeoJSON structure');
        }
        
        console.log(`✓ Loaded ${estuaryData.features.length} estuaries`);
        
        // Initialize all filters as active
        const types = getEstuaryTypes();
        types.forEach(type => activeFilters.add(type));
        activeFilters.add('all');
        
        // Update counts
        updateCounts();
        
        // Display markers
        updateMarkers();
        
        // Setup filter event listeners
        setupFilters();
        
    } catch (error) {
        console.error('Error loading estuary data:', error);
        showError(error.message);
    }
}

// Load coastline data for coastal segmentation mode
async function loadCoastlineData() {
    try {
        const response = await fetch('data/coastline.geojson');
        
        if (!response.ok) {
            console.warn('Coastline data not available');
            return;
        }
        
        coastlineData = await response.json();
        
        if (!coastlineData || !coastlineData.features || !Array.isArray(coastlineData.features)) {
            throw new Error('Invalid coastline GeoJSON structure');
        }
        
        console.log(`✓ Loaded ${coastlineData.features.length} coastline segments`);
        
    } catch (error) {
        console.error('Error loading coastline data:', error);
    }
}

// Load basin polygon data for basin visualization mode
async function loadBasinData() {
    try {
        const response = await fetch('data/basins_simplified.geojson');
        
        if (!response.ok) {
            console.warn('Basin data not available');
            return;
        }
        
        basinData = await response.json();
        
        if (!basinData || !basinData.features || !Array.isArray(basinData.features)) {
            throw new Error('Invalid basin GeoJSON structure');
        }
        
        console.log(`✓ Loaded ${basinData.features.length} basin polygons`);
        
    } catch (error) {
        console.error('Error loading basin data:', error);
    }
}

// Show error message
function showError(message) {
    const mapElement = document.getElementById('map');
    mapElement.innerHTML = `
        <div style="
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 400px;
        ">
            <h3 style="color: #dc143c; margin-bottom: 1rem;">⚠️ Data Loading Error</h3>
            <p style="color: #495057; margin-bottom: 1rem;">
                Unable to load estuary data. Please refresh the page or check your connection.
            </p>
            <p style="color: #6c757d; font-size: 0.85rem;">
                Error: ${message}
            </p>
            <button onclick="location.reload()" style="
                margin-top: 1rem;
                padding: 0.5rem 1.5rem;
                background: #1e3c72;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            ">Refresh Page</button>
        </div>
    `;
}

// Get unique estuary types from data
function getEstuaryTypes() {
    const types = new Set();
    estuaryData.features.forEach(feature => {
        types.add(feature.properties.type);
    });
    return Array.from(types);
}

// Update estuary count displays
function updateCounts() {
    const typeCounts = {};
    let totalCount = 0;
    
    estuaryData.features.forEach(feature => {
        const type = feature.properties.type;
        typeCounts[type] = (typeCounts[type] || 0) + 1;
        totalCount++;
    });
    
    // Update all count
    const allCountElement = document.getElementById('count-all');
    if (allCountElement) {
        allCountElement.textContent = totalCount;
    }
    
    // Update individual type counts
    Object.keys(typeCounts).forEach(type => {
        const countId = 'count-' + type.replace(/\s+/g, '-');
        const countElement = document.getElementById(countId);
        if (countElement) {
            countElement.textContent = typeCounts[type];
        }
    });
}

// Create marker for an estuary
function createMarker(feature) {
    const coords = feature.geometry.coordinates;
    const props = feature.properties;
    
    // Create custom icon based on type
    const icon = L.divIcon({
        className: 'custom-marker',
        html: `<div style="
            background-color: ${ESTUARY_COLORS[props.type]};
            width: 12px;
            height: 12px;
            border-radius: 50%;
            border: 2px solid white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        "></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    });
    
    // Create marker
    const marker = L.marker([coords[1], coords[0]], { icon: icon });
    
    // Create popup content
    const popupContent = createPopupContent(props);
    marker.bindPopup(popupContent, {
        maxWidth: 300,
        className: 'estuary-popup'
    });
    
    return marker;
}

// Create popup content for an estuary
function createPopupContent(props) {
    const typeClass = props.type.toLowerCase().replace(/\s+/g, '-');
    
    let content = `
        <div class="popup-title">${props.name || 'Unnamed'}</div>
        <div class="popup-type ${typeClass}">${props.type}</div>
        <div class="popup-info">
    `;
    
    if (props.type_detailed) {
        content += `<strong>Type:</strong> ${props.type_detailed}<br>`;
    }
    
    if (props.basin_area_km2) {
        content += `<strong>Basin Area:</strong> ${props.basin_area_km2.toLocaleString()} km²<br>`;
    }
    
    if (props.sea_name) {
        content += `<strong>Sea:</strong> ${props.sea_name}<br>`;
    }
    
    if (props.ocean_name) {
        content += `<strong>Ocean:</strong> ${props.ocean_name}<br>`;
    }
    
    if (props.baum_embayment_name) {
        content += `<strong>Baum Data:</strong> ${props.baum_embayment_name}<br>`;
    }
    
    content += `
        <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #6c757d;">
            <em>Source: ${props.data_source}</em>
        </div>
    `;
    
    content += `</div>`;
    
    return content;
}

// Create popup content for coastline segment
function createCoastlinePopupContent(props) {
    const typeClass = props.type.toLowerCase().replace(/\s+/g, '-');
    
    let content = `
        <div class="popup-title">Coastal Segment</div>
        <div class="popup-type ${typeClass}">${props.type}</div>
        <div class="popup-info">
    `;
    
    if (props.type_detailed) {
        content += `<strong>Type:</strong> ${props.type_detailed}<br>`;
    }
    
    if (props.length_km) {
        content += `<strong>Length:</strong> ${props.length_km.toLocaleString()} km<br>`;
    }
    
    content += `
        <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #6c757d;">
            <em>Source: ${props.data_source}</em>
        </div>
    `;
    
    content += `</div>`;
    
    return content;
}

// Update markers based on active filters
function updateMarkers() {
    // Clear existing markers
    markersLayer.clearLayers();
    
    if (!estuaryData) return;
    
    // Add markers for filtered estuaries
    estuaryData.features.forEach(feature => {
        const type = feature.properties.type;
        if (activeFilters.has('all') || activeFilters.has(type)) {
            const marker = createMarker(feature);
            markersLayer.addLayer(marker);
        }
    });
}

// Update coastline based on active filters
function updateCoastline() {
    // Clear existing coastline
    coastlineLayer.clearLayers();
    
    if (!coastlineData) return;
    
    // Add coastline segments for filtered types
    coastlineData.features.forEach(feature => {
        const type = feature.properties.type;
        if (activeFilters.has('all') || activeFilters.has(type)) {
            const line = createCoastline(feature);
            coastlineLayer.addLayer(line);
        }
    });
}

// Create coastline segment
function createCoastline(feature) {
    const coords = feature.geometry.coordinates.map(coord => [coord[1], coord[0]]);
    const props = feature.properties;
    
    // Create polyline with color based on type
    const line = L.polyline(coords, {
        color: ESTUARY_COLORS[props.type] || '#808080',
        weight: 3,
        opacity: 0.7
    });
    
    // Create popup content
    const popupContent = createCoastlinePopupContent(props);
    line.bindPopup(popupContent, {
        maxWidth: 300,
        className: 'estuary-popup'
    });
    
    return line;
}

// Update basin polygons based on active filters
function updateBasins() {
    // Clear existing basins
    basinLayer.clearLayers();
    
    if (!basinData) return;
    
    // Add basin polygons for filtered types
    basinData.features.forEach(feature => {
        const type = feature.properties.type;
        if (activeFilters.has('all') || activeFilters.has(type)) {
            const basin = createBasin(feature);
            basinLayer.addLayer(basin);
        }
    });
}

// Create basin polygon
function createBasin(feature) {
    const props = feature.properties;
    
    // Convert GeoJSON coordinates to Leaflet format
    let coords;
    if (feature.geometry.type === 'Polygon') {
        coords = feature.geometry.coordinates.map(ring => 
            ring.map(coord => [coord[1], coord[0]])
        );
    } else if (feature.geometry.type === 'MultiPolygon') {
        coords = feature.geometry.coordinates.map(polygon =>
            polygon.map(ring => ring.map(coord => [coord[1], coord[0]]))
        );
    }
    
    // Create polygon with color based on type
    const polygon = L.polygon(coords, {
        fillColor: ESTUARY_COLORS[props.type] || '#808080',
        fillOpacity: 0.6,
        color: 'white',
        weight: 1,
        opacity: 1
    });
    
    // Add hover effects
    polygon.on('mouseover', function(e) {
        e.target.setStyle({
            fillOpacity: 0.9,
            weight: 3
        });
    });
    
    polygon.on('mouseout', function(e) {
        e.target.setStyle({
            fillOpacity: 0.6,
            weight: 1
        });
    });
    
    // Create popup content
    const popupContent = createPopupContent(props);
    polygon.bindPopup(popupContent, {
        maxWidth: 300,
        className: 'estuary-popup'
    });
    
    return polygon;
}

// Switch visualization mode
function switchMode(newMode) {
    currentMode = newMode;
    
    if (currentMode === 'points') {
        // Show points, hide others
        if (!map.hasLayer(markersLayer)) {
            map.addLayer(markersLayer);
        }
        if (map.hasLayer(coastlineLayer)) {
            map.removeLayer(coastlineLayer);
        }
        if (map.hasLayer(basinLayer)) {
            map.removeLayer(basinLayer);
        }
        updateMarkers();
    } else if (currentMode === 'coastline') {
        // Show coastline, hide others
        if (map.hasLayer(markersLayer)) {
            map.removeLayer(markersLayer);
        }
        if (!map.hasLayer(coastlineLayer)) {
            map.addLayer(coastlineLayer);
        }
        if (map.hasLayer(basinLayer)) {
            map.removeLayer(basinLayer);
        }
        updateCoastline();
    } else if (currentMode === 'basins') {
        // Show basins, hide others
        if (map.hasLayer(markersLayer)) {
            map.removeLayer(markersLayer);
        }
        if (map.hasLayer(coastlineLayer)) {
            map.removeLayer(coastlineLayer);
        }
        if (!map.hasLayer(basinLayer)) {
            map.addLayer(basinLayer);
        }
        updateBasins();
    }
    
    // Update mode toggle buttons
    const pointsBtn = document.getElementById('mode-points');
    const coastlineBtn = document.getElementById('mode-coastline');
    const basinsBtn = document.getElementById('mode-basins');
    
    if (pointsBtn) pointsBtn.classList.remove('active');
    if (coastlineBtn) coastlineBtn.classList.remove('active');
    if (basinsBtn) basinsBtn.classList.remove('active');
    
    if (currentMode === 'points' && pointsBtn) {
        pointsBtn.classList.add('active');
    } else if (currentMode === 'coastline' && coastlineBtn) {
        coastlineBtn.classList.add('active');
    } else if (currentMode === 'basins' && basinsBtn) {
        basinsBtn.classList.add('active');
    }
}

// Setup filter checkbox event listeners
function setupFilters() {
    const checkboxes = document.querySelectorAll('.filter-checkbox');
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const value = this.value;
            
            if (value === 'all') {
                // Handle "all" checkbox
                if (this.checked) {
                    activeFilters.add('all');
                    // Check all other checkboxes
                    checkboxes.forEach(cb => {
                        if (cb.value !== 'all') {
                            cb.checked = true;
                            activeFilters.add(cb.value);
                        }
                    });
                } else {
                    activeFilters.clear();
                    // Uncheck all other checkboxes
                    checkboxes.forEach(cb => {
                        if (cb.value !== 'all') {
                            cb.checked = false;
                        }
                    });
                }
            } else {
                // Handle individual type checkbox
                if (this.checked) {
                    activeFilters.add(value);
                    // Check if all types are now selected
                    const allTypesChecked = Array.from(checkboxes)
                        .filter(cb => cb.value !== 'all')
                        .every(cb => cb.checked);
                    if (allTypesChecked) {
                        activeFilters.add('all');
                        const allCheckbox = document.querySelector('.filter-checkbox[value="all"]');
                        if (allCheckbox) allCheckbox.checked = true;
                    }
                } else {
                    activeFilters.delete(value);
                    activeFilters.delete('all');
                    // Uncheck "all" checkbox
                    const allCheckbox = document.querySelector('.filter-checkbox[value="all"]');
                    if (allCheckbox) allCheckbox.checked = false;
                }
            }
            
            // Update map
            if (currentMode === 'points') {
                updateMarkers();
            } else if (currentMode === 'coastline') {
                updateCoastline();
            } else if (currentMode === 'basins') {
                updateBasins();
            }
        });
    });
    
    // Setup mode toggle buttons
    const pointsBtn = document.getElementById('mode-points');
    const coastlineBtn = document.getElementById('mode-coastline');
    const basinsBtn = document.getElementById('mode-basins');
    
    if (pointsBtn) {
        pointsBtn.addEventListener('click', function() {
            switchMode('points');
        });
    }
    
    if (coastlineBtn) {
        coastlineBtn.addEventListener('click', function() {
            switchMode('coastline');
        });
    }
    
    if (basinsBtn) {
        basinsBtn.addEventListener('click', function() {
            switchMode('basins');
        });
    }
}

// Initialize map when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initMap();
});

// Handle window resize
window.addEventListener('resize', function() {
    if (map) {
        map.invalidateSize();
    }
});
