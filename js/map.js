// Global Estuary Type Map - Main JavaScript
// Data source: Laruelle et al. (2024, Estuaries and Coasts)

// Color scheme for different estuary types
const ESTUARY_COLORS = {
    'Delta': '#8b4513',
    'Fjord': '#4a90e2',
    'Lagoon': '#50c878',
    'Ria': '#9370db',
    'Coastal Plain': '#ff8c00',
    'Bar-Built': '#20b2aa',
    'Tectonic': '#dc143c'
};

// Global variables
let map;
let estuaryData;
let markersLayer;
let activeFilters = new Set();

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

    // Create layer for markers
    markersLayer = L.layerGroup().addTo(map);

    // Load estuary data
    loadEstuaryData();
}

// Load and display estuary data
async function loadEstuaryData() {
    try {
        const response = await fetch('data/estuaries.geojson');
        estuaryData = await response.json();
        
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
        
        console.log(`Loaded ${estuaryData.features.length} estuaries`);
    } catch (error) {
        console.error('Error loading estuary data:', error);
        alert('Error loading estuary data. Please check the console for details.');
    }
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
        <div class="popup-title">${props.name}</div>
        <div class="popup-type ${typeClass}">${props.type}</div>
        <div class="popup-info">
            <strong>Country:</strong> ${props.country}<br>
    `;
    
    if (props.river) {
        content += `<strong>River:</strong> ${props.river}<br>`;
    }
    
    if (props.area_km2) {
        content += `<strong>Area:</strong> ${props.area_km2.toLocaleString()} km²<br>`;
    }
    
    if (props.depth_m) {
        content += `<strong>Max Depth:</strong> ${props.depth_m} m<br>`;
    }
    
    if (props.description) {
        content += `
        </div>
        <div class="popup-description">${props.description}</div>
        `;
    } else {
        content += `</div>`;
    }
    
    return content;
}

// Update markers based on active filters
function updateMarkers() {
    // Clear existing markers
    markersLayer.clearLayers();
    
    // Add markers for filtered estuaries
    estuaryData.features.forEach(feature => {
        const type = feature.properties.type;
        if (activeFilters.has('all') || activeFilters.has(type)) {
            const marker = createMarker(feature);
            markersLayer.addLayer(marker);
        }
    });
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
            updateMarkers();
        });
    });
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
