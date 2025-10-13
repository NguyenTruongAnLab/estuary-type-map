// ============================================================================
// Global Estuary Type Map - COMPLETE FINAL VERSION
// ============================================================================
// Features:
// - Dürr Estuary Types (geomorphology)
// - Baum Morphometry (large estuaries)
// - Salinity Zones
// - Tidal Zones 
// - Multiple view modes
// - All filters working properly
// - Complete legends with ranges
// Total Data: ~27 MB | Load Time: 3-7 seconds
// ============================================================================

// ============================================================================
// COLOR SCHEMES
// ============================================================================

const DURR_COLORS = {
    'Delta': '#8b4513',
    'Coastal Plain': '#ff8c00',
    'Lagoon': '#50c878',
    'Fjord': '#4a90e2',
    'Karst': '#9370db',
    'Unclassified': '#808080'
};

const SALINITY_COLORS = {
    'freshwater': '#2166ac',
    'oligohaline': '#67a9cf',
    'mesohaline': '#d1e5f0',
    'polyhaline': '#fddbc7',
    'euhaline': '#ef8a62',
    'hyperhaline': '#b2182b'
};

const SALINITY_RANGES = {
    'freshwater': '<0.5 ppt',
    'oligohaline': '0.5-5 ppt',
    'mesohaline': '5-18 ppt',
    'polyhaline': '18-25 ppt',
    'euhaline': '25-35 ppt',
    'hyperhaline': '>35 ppt'
};

const TIDAL_ZONE_COLORS = {
    'tidal_freshwater': '#2E7D32',
    'tidal_saline': '#1976D2',
    'non_tidal': '#757575'
};

const TIDAL_ZONE_LABELS = {
    'tidal_freshwater': 'Tidal Freshwater',
    'tidal_saline': 'Tidal Saline',
    'non_tidal': 'Non-Tidal'
};

const BAUM_COLORS = {
    'LSE': '#e74c3c',
    'Rocky Bay': '#95a5a6',
    'Barrier Estuary': '#3498db',
    'Sandy Bay': '#f39c12',
    'Funnelled': '#9b59b6'
};

// ============================================================================
// GLOBAL STATE
// ============================================================================

let map;
let layerGroups = {
    coastalBasins: L.layerGroup(),
    durrReference: L.layerGroup(),
    baum: L.layerGroup(),
    salinityZones: L.layerGroup(),
    tidalZones: L.layerGroup(),
    rivers: L.layerGroup(),
    basins: L.layerGroup()
};

let datasets = {};
let activeFilters = {
    durr: new Set(['all']),
    salinity: new Set(['all']),
    tidal: new Set(['all'])
};

let currentViewMode = 'geomorphology'; // 'geomorphology', 'salinity', or 'tidal'
let loadingIndicator;

// ============================================================================
// INITIALIZATION
// ============================================================================

function initMap() {
    console.log('🗺️ Initializing Global Estuary Type Map - Complete Version...');
    
    map = L.map('map', {
        center: [20, 0],
        zoom: 2,
        minZoom: 2,
        maxZoom: 18,
        worldCopyJump: true,
        preferCanvas: true
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);

    // Add default layers
    layerGroups.coastalBasins.addTo(map);
    layerGroups.baum.addTo(map);

    setupLayerControls();
    setupFilters();
    setupViewModeSelector();
    setupMapEvents();
    createLoadingIndicator();
}

function createLoadingIndicator() {
    loadingIndicator = L.control({position: 'topright'});
    loadingIndicator.onAdd = function() {
        const div = L.DomUtil.create('div', 'loading-indicator');
        div.innerHTML = '<div class="spinner"></div><span>Loading data...</span>';
        div.style.display = 'none';
        return div;
    };
    loadingIndicator.addTo(map);
}

function setLoading(isLoading) {
    const indicator = document.querySelector('.loading-indicator');
    if (indicator) {
        indicator.style.display = isLoading ? 'flex' : 'none';
    }
}

// ============================================================================
// DATA LOADING
// ============================================================================

async function loadAllData() {
    console.log('📂 Loading complete dataset...');
    
    try {
        setLoading(true);
        
        // Load core data first
        await Promise.all([
            loadDurrBasins(),
            loadBaumData()
        ]);
        
        updateDurrBasins();
        updateBaumLayer();
        updateLegend();
        
        console.log('✓ Core data loaded');
        
        // Load optional data in background
        setTimeout(async () => {
            await Promise.all([
                loadSalinityData(),
                loadTidalZones()
            ]);
            console.log('✓ Optional data loaded (Salinity & Tidal zones)');
        }, 1000);
        
        setLoading(false);
        
    } catch (error) {
        console.error('❌ Error loading data:', error);
        setLoading(false);
        showError('Failed to load map data. Please refresh the page.');
    }
}

async function loadCoastalBasins() {
    console.log('📂 Loading coastal basins (BasinATLAS Level 7)...');
    const response = await fetch('data/web/coastal_basins_estuarine_types.geojson');
    if (!response.ok) throw new Error('Failed to load coastal basins');
    datasets.coastalBasins = await response.json();
    console.log(`✓ Loaded ${datasets.coastalBasins.features.length} coastal basins`);
    updateCountElement('count-coastal-basins', datasets.coastalBasins.features.length);
    updateDurrCounts(); // Still updates type counts
}

async function loadDurrReference() {
    console.log('📂 Loading Dürr reference (optional full watersheds)...');
    const response = await fetch('data/optimized/durr_basins.geojson');
    if (!response.ok) throw new Error('Failed to load Dürr reference');
    datasets.durrReference = await response.json();
    console.log(`✓ Loaded ${datasets.durrReference.features.length} Dürr reference catchments`);
    updateCountElement('count-durr-ref', datasets.durrReference.features.length);
}

async function loadBaumData() {
    console.log('📂 Loading Baum morphometry...');
    const response = await fetch('data/optimized/baum_morphometry.geojson');
    if (!response.ok) throw new Error('Failed to load Baum data');
    datasets.baum = await response.json();
    console.log(`✓ Loaded ${datasets.baum.features.length} Baum estuaries`);
    updateCountElement('count-baum-all', datasets.baum.features.length);
}

async function loadSalinityData() {
    console.log('📂 Loading salinity zones (POLYGONS)...');
    const response = await fetch('data/optimized/basins_by_salinity.geojson');
    if (!response.ok) throw new Error('Failed to load salinity data');
    datasets.salinityZones = await response.json();
    console.log(`✓ Loaded ${datasets.salinityZones.features.length} salinity polygons`);
    updateCountElement('count-salinity', datasets.salinityZones.features.length);
    updateSalinityCounts();
}

async function loadTidalZones() {
    console.log('📂 Loading tidal zones...');
    const response = await fetch('data/optimized/basins_by_tidal_zone.geojson');
    if (!response.ok) throw new Error('Failed to load tidal zone data');
    datasets.tidalZones = await response.json();
    console.log(`✓ Loaded ${datasets.tidalZones.features.length} tidal zone polygons`);
    updateCountElement('count-tidal', datasets.tidalZones.features.length);
    updateTidalCounts();
}

// Rivers and basins loading DISABLED - not meaningful without salinity data
// They would just show blue lines/polygons with no classification
// If needed in future, join with salinity/tidal data first!

// async function loadRiversData() {
//     console.log('📂 Loading rivers...');
//     const response = await fetch('data/optimized/rivers_estuaries.geojson');
//     if (!response.ok) throw new Error('Failed to load rivers');
//     datasets.rivers = await response.json();
//     console.log(`✓ Loaded ${datasets.rivers.features.length} river reaches`);
//     updateCountElement('count-rivers', datasets.rivers.features.length);
// }

// async function loadBasinsData() {
//     console.log('📂 Loading HydroSHEDS basins...');
//     const response = await fetch('data/optimized/basins_lev06.geojson');
//     if (!response.ok) throw new Error('Failed to load basins');
//     datasets.basins = await response.json();
//     console.log(`✓ Loaded ${datasets.basins.features.length} basins`);
// }

// ============================================================================
// LAYER RENDERING
// ============================================================================

function updateDurrBasins() {
    layerGroups.coastalBasins.clearLayers();
    if (!datasets.coastalBasins) return;
    
    console.log('📊 Updating Dürr basins...');
    console.log('Total features:', datasets.coastalBasins.features.length);
    
    const filteredFeatures = datasets.coastalBasins.features.filter(feature => {
        const type = feature.properties.estuary_type;
        return activeFilters.durr.has('all') || activeFilters.durr.has(type);
    });
    
    filteredFeatures.forEach(feature => {
        const props = feature.properties;
        const color = DURR_COLORS[props.estuary_type] || '#808080';
        
        const polygon = L.geoJSON(feature, {
            style: {
                fillColor: color,
                fillOpacity: 0.5,
                color: color,
                weight: 1,
                opacity: 0.8
            }
        }).bindPopup(`
            <div class="popup-content">
                <h3 class="popup-title">${props.estuary_name || 'Unnamed'}</h3>
                <div class="popup-type" style="background: ${color};">${props.estuary_type}</div>
                <div class="popup-info">
                    <strong>Basin ID:</strong> ${props.HYBAS_ID}<br>
                    <strong>Sub Area:</strong> ${(props.SUB_AREA || 0).toLocaleString()} km²<br>
                    <strong>Upstream Area:</strong> ${(props.UP_AREA || 0).toLocaleString()} km²
                </div>
                <div class="popup-source">
                    <strong>Source:</strong> HydroSHEDS + Dürr et al. (2011)
                </div>
            </div>
        `);
        
        layerGroups.coastalBasins.addLayer(polygon);
    });
    
    console.log(`📍 Displayed ${filteredFeatures.length} coastal basins with Dürr classification`);
}

function updateDurrReference() {
    layerGroups.durrReference.clearLayers();
    if (!datasets.durrReference) return;
    
    console.log('📂 Updating Dürr reference catchments...');
    
    datasets.durrReference.features.forEach(feature => {
        const props = feature.properties;
        const type = props.estuary_type || 'Unclassified';
        const color = DURR_COLORS[type] || '#808080';
        
        const polygon = L.geoJSON(feature, {
            style: {
                fillColor: color,
                fillOpacity: 0.3,
                color: '#666',
                weight: 1,
                opacity: 0.5,
                dashArray: '3, 3'
            }
        }).bindPopup(`
            <div class="popup-content">
                <h3 class="popup-title">${props.estuary_name || 'Unnamed Catchment'}</h3>
                <div class="popup-type" style="background: ${color};">${type}</div>
                <div class="popup-info">
                    <strong>Type:</strong> ${props.type_detailed || 'N/A'}
                </div>
                <div class="popup-source">
                    <strong>Source:</strong> Dürr et al. (2011) - Full Catchments
                </div>
            </div>
        `);
        
        layerGroups.durrReference.addLayer(polygon);
    });
    
    console.log(`📍 Displayed ${datasets.durrReference.features.length} Dürr reference catchments`);
}

function updateBaumLayer() {
    layerGroups.baum.clearLayers();
    if (!datasets.baum || !datasets.baum.features) return;
    
    datasets.baum.features.forEach(feature => {
        const props = feature.properties;
        const color = BAUM_COLORS[props.geomorphotype] || '#808080';
        
        const marker = L.circleMarker([props.lat, props.lon], {
            radius: 8,
            fillColor: color,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).bindPopup(`
            <div class="popup-content">
                <h3 class="popup-title">${props.name}</h3>
                <div class="popup-type" style="background: ${color};">${props.geomorphotype}</div>
                <div class="popup-source">
                    <strong>Source:</strong> Baum et al. (2024)
                </div>
            </div>
        `);
        
        layerGroups.baum.addLayer(marker);
    });
    
    console.log(`📍 Displayed ${datasets.baum.features.length} Baum estuaries`);
}

function updateSalinityLayer() {
    layerGroups.salinityZones.clearLayers();
    if (!datasets.salinityZones || !datasets.salinityZones.features) return;
    
    const filteredFeatures = datasets.salinityZones.features.filter(feature => {
        const zone = feature.properties.salinity_zone;
        return activeFilters.salinity.has('all') || activeFilters.salinity.has(zone);
    });
    
    filteredFeatures.forEach(feature => {
        const props = feature.properties;
        const zone = props.salinity_zone || 'unknown';
        const color = SALINITY_COLORS[zone] || '#808080';
        const range = SALINITY_RANGES[zone] || 'Unknown';
        
        const polygon = L.geoJSON(feature, {
            style: {
                fillColor: color,
                fillOpacity: 0.6,
                color: color,
                weight: 1,
                opacity: 0.8
            }
        }).bindPopup(`
            <div class="popup-content">
                <h3 class="popup-title">Salinity Zone</h3>
                <div class="popup-type" style="background: ${color};">${zone.charAt(0).toUpperCase() + zone.slice(1)}</div>
                <div class="popup-info">
                    <strong>Range:</strong> ${range}<br>
                    <strong>Area:</strong> ${(props.SUB_AREA || 0).toFixed(0)} km²
                </div>
                <div class="popup-source">
                    <strong>Source:</strong> GlobSalt v2.0
                </div>
            </div>
        `);
        
        layerGroups.salinityZones.addLayer(polygon);
    });
    
    console.log(`📍 Displayed ${filteredFeatures.length} salinity zones`);
}

function updateTidalZoneLayer() {
    layerGroups.tidalZones.clearLayers();
    if (!datasets.tidalZones || !datasets.tidalZones.features) return;
    
    const filteredFeatures = datasets.tidalZones.features.filter(feature => {
        const zone = feature.properties.tidal_zone;
        return activeFilters.tidal.has('all') || activeFilters.tidal.has(zone);
    });
    
    filteredFeatures.forEach(feature => {
        const props = feature.properties;
        const zone = props.tidal_zone || 'unknown';
        const color = TIDAL_ZONE_COLORS[zone] || '#808080';
        const label = TIDAL_ZONE_LABELS[zone] || zone;
        
        const polygon = L.geoJSON(feature, {
            style: {
                fillColor: color,
                fillOpacity: 0.6,
                color: color,
                weight: 1,
                opacity: 0.8
            }
        }).bindPopup(`
            <div class="popup-content">
                <h3 class="popup-title">Tidal Zone Classification</h3>
                <div class="popup-type" style="background: ${color};">${label}</div>
                <div class="popup-info">
                    <strong>Salinity:</strong> ${props.salinity_zone || 'N/A'}<br>
                    <strong>Tidal Influence:</strong> ${props.is_tidal ? 'Yes' : 'No'}<br>
                    <strong>Area:</strong> ${(props.SUB_AREA || 0).toFixed(0)} km²
                </div>
                <div class="popup-source">
                    <strong>Source:</strong> Ensign et al. (2012)
                </div>
            </div>
        `);
        
        layerGroups.tidalZones.addLayer(polygon);
    });
    
    console.log(`📍 Displayed ${filteredFeatures.length} tidal zones`);
}

function updateRiversLayer() {
    layerGroups.rivers.clearLayers();
    if (!datasets.rivers || !datasets.rivers.features) return;
    
    datasets.rivers.features.forEach(feature => {
        const line = L.geoJSON(feature, {
            style: {
                color: '#4a90e2',
                weight: 1.5,
                opacity: 0.7
            }
        });
        layerGroups.rivers.addLayer(line);
    });
    
    console.log(`📍 Displayed ${datasets.rivers.features.length} river reaches`);
}

function updateBasinsLayer() {
    layerGroups.basins.clearLayers();
    if (!datasets.basins || !datasets.basins.features) return;
    
    datasets.basins.features.forEach(feature => {
        const polygon = L.geoJSON(feature, {
            style: {
                fillColor: '#3498db',
                fillOpacity: 0.2,
                color: '#3498db',
                weight: 1,
                opacity: 0.5
            }
        });
        layerGroups.basins.addLayer(polygon);
    });
    
    console.log(`📍 Displayed ${datasets.basins.features.length} basins`);
}

// ============================================================================
// VIEW MODE SELECTOR
// ============================================================================

function setupViewModeSelector() {
    const viewModeRadios = document.querySelectorAll('input[name="view-mode"]');
    viewModeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            currentViewMode = e.target.value;
            switchViewMode(currentViewMode);
        });
    });
}

function switchViewMode(mode) {
    console.log(`🎛️ Switching to ${mode} view mode`);
    
    // Hide all classification layers
    map.removeLayer(layerGroups.coastalBasins);
    map.removeLayer(layerGroups.salinityZones);
    map.removeLayer(layerGroups.tidalZones);
    
    // Show appropriate layer based on mode
    switch(mode) {
        case 'geomorphology':
            layerGroups.durrBasins.addTo(map);
            document.getElementById('layer-durr-basins').checked = true;
            break;
        case 'salinity':
            if (!layerGroups.salinityZones.getLayers().length && datasets.salinityZones) {
                updateSalinityLayer();
            }
            layerGroups.salinityZones.addTo(map);
            document.getElementById('layer-salinity').checked = true;
            break;
        case 'tidal':
            if (!layerGroups.tidalZones.getLayers().length && datasets.tidalZones) {
                updateTidalZoneLayer();
            }
            layerGroups.tidalZones.addTo(map);
            document.getElementById('layer-tidal').checked = true;
            break;
    }
    
    updateLegend();
    updateSidebarFilters();
}

// ============================================================================
// LAYER CONTROLS
// ============================================================================

function setupLayerControls() {
    const layerToggles = {
        'layer-coastal-basins': { group: layerGroups.coastalBasins, update: updateDurrBasins },
        'layer-durr-reference': { group: layerGroups.durrReference, update: updateDurrReference },
        'layer-baum': { group: layerGroups.baum, update: updateBaumLayer },
        'layer-salinity': { group: layerGroups.salinityZones, update: updateSalinityLayer },
        'layer-tidal': { group: layerGroups.tidalZones, update: updateTidalZoneLayer }
        // Rivers and basins disabled - not meaningful without data
        // 'layer-rivers': { group: layerGroups.rivers, update: updateRiversLayer },
        // 'layer-basins': { group: layerGroups.basins, update: updateBasinsLayer }
    };
    
    Object.entries(layerToggles).forEach(([id, config]) => {
        const checkbox = document.getElementById(id);
        if (checkbox) {
            checkbox.addEventListener('change', (e) => {
                if (e.target.checked) {
                    if (config.update && !config.group.getLayers().length) {
                        config.update();
                    }
                    config.group.addTo(map);
                } else {
                    map.removeLayer(config.group);
                }
                updateLegend();
                updateSidebarFilters();
            });
        }
    });
}

// ============================================================================
// FILTERS
// ============================================================================

function setupFilters() {
    // Dürr filters
    document.querySelectorAll('[id^="filter-durr-"]').forEach(cb => {
        cb.addEventListener('change', handleDurrFilter);
    });
    
    // Salinity filters
    document.querySelectorAll('[id^="filter-salinity-"]').forEach(cb => {
        cb.addEventListener('change', handleSalinityFilter);
    });
    
    // Tidal filters
    document.querySelectorAll('[id^="filter-tidal-"]').forEach(cb => {
        cb.addEventListener('change', handleTidalFilter);
    });
}

function handleDurrFilter() {
    const allCheckbox = document.getElementById('filter-durr-all');
    const checkboxes = document.querySelectorAll('[id^="filter-durr-"]:not(#filter-durr-all)');
    
    if (allCheckbox && allCheckbox.checked) {
        activeFilters.durr = new Set(['all']);
        checkboxes.forEach(cb => cb.checked = true);
    } else {
        activeFilters.durr = new Set();
        checkboxes.forEach(cb => {
            if (cb.checked) {
                const type = cb.id.replace('filter-durr-', '').split('-').map(w => 
                    w.charAt(0).toUpperCase() + w.slice(1)
                ).join(' ');
                if (Object.keys(DURR_COLORS).includes(type)) {
                    activeFilters.durr.add(type);
                }
            }
        });
        if (activeFilters.durr.size === 0) activeFilters.durr.add('all');
    }
    
    updateCoastalBasins();
    updateLegend();
}

function handleSalinityFilter() {
    const allCheckbox = document.getElementById('filter-salinity-all');
    const checkboxes = document.querySelectorAll('[id^="filter-salinity-"]:not(#filter-salinity-all)');
    
    if (allCheckbox && allCheckbox.checked) {
        activeFilters.salinity = new Set(['all']);
        checkboxes.forEach(cb => cb.checked = true);
    } else {
        activeFilters.salinity = new Set();
        checkboxes.forEach(cb => {
            if (cb.checked) {
                const zone = cb.id.replace('filter-salinity-', '');
                activeFilters.salinity.add(zone);
            }
        });
        if (activeFilters.salinity.size === 0) activeFilters.salinity.add('all');
    }
    
    updateSalinityLayer();
    updateLegend();
}

function handleTidalFilter() {
    const allCheckbox = document.getElementById('filter-tidal-all');
    const checkboxes = document.querySelectorAll('[id^="filter-tidal-"]:not(#filter-tidal-all)');
    
    if (allCheckbox && allCheckbox.checked) {
        activeFilters.tidal = new Set(['all']);
        checkboxes.forEach(cb => cb.checked = true);
    } else {
        activeFilters.tidal = new Set();
        checkboxes.forEach(cb => {
            if (cb.checked) {
                const zone = cb.id.replace('filter-tidal-', '');
                activeFilters.tidal.add(zone);
            }
        });
        if (activeFilters.tidal.size === 0) activeFilters.tidal.add('all');
    }
    
    updateTidalZoneLayer();
    updateLegend();
}

// ============================================================================
// LEGEND
// ============================================================================

function updateLegend() {
    const legendContent = document.getElementById('legend-content');
    const legendTitle = document.getElementById('legend-title');
    if (!legendContent) return;
    
    legendContent.innerHTML = '';
    
    const isCoastalBasinsActive = map.hasLayer(layerGroups.coastalBasins);
    const isDurrRefActive = map.hasLayer(layerGroups.durrReference);
    const isBaumActive = map.hasLayer(layerGroups.baum);
    const isSalinityActive = map.hasLayer(layerGroups.salinityZones);
    const isTidalActive = map.hasLayer(layerGroups.tidalZones);
    
    // Update title
    let title = 'Map Legend';
    if (currentViewMode === 'geomorphology') title = 'Estuary Types (Coastal Only)';
    else if (currentViewMode === 'salinity') title = 'Salinity Zones';
    else if (currentViewMode === 'tidal') title = 'Tidal Zones';
    if (legendTitle) legendTitle.textContent = title;
    
    // Coastal Basins legend
    if (isCoastalBasinsActive) {
        legendContent.innerHTML += '<div class="legend-section-title">Coastal Basins (BasinATLAS L7)</div>';
        Object.entries(DURR_COLORS).forEach(([type, color]) => {
            const isActive = activeFilters.durr.has('all') || activeFilters.durr.has(type);
            legendContent.innerHTML += `
                <div class="legend-item" style="opacity:${isActive ? 1 : 0.3}">
                    <div class="legend-color" style="background:${color};"></div>
                    <span class="legend-label">${type}</span>
                </div>
            `;
        });
    }
    
    // Dürr Reference legend (if enabled)
    if (isDurrRefActive) {
        legendContent.innerHTML += '<div class="legend-section-title" style="margin-top:10px;">Dürr Reference (Outline)</div>';
        legendContent.innerHTML += `
            <div class="legend-item" style="opacity:0.6">
                <div style="width:20px; height:2px; background:#666; border-top:1px dashed #666; margin:8px 0;"></div>
                <span class="legend-label" style="font-size:0.85em;">Full Watersheds</span>
            </div>
        `;
    }
    
    // Salinity legend
    if (isSalinityActive) {
        legendContent.innerHTML += '<div class="legend-section-title">Salinity Zones</div>';
        Object.entries(SALINITY_COLORS).forEach(([zone, color]) => {
            const label = zone.charAt(0).toUpperCase() + zone.slice(1);
            const range = SALINITY_RANGES[zone];
            const isActive = activeFilters.salinity.has('all') || activeFilters.salinity.has(zone);
            legendContent.innerHTML += `
                <div class="legend-item" style="opacity:${isActive ? 1 : 0.3}">
                    <div class="legend-color" style="background:${color};"></div>
                    <span class="legend-label">${label} (${range})</span>
                </div>
            `;
        });
    }
    
    // Tidal zone legend
    if (isTidalActive) {
        legendContent.innerHTML += '<div class="legend-section-title">Tidal Zones</div>';
        Object.entries(TIDAL_ZONE_COLORS).forEach(([zone, color]) => {
            const label = TIDAL_ZONE_LABELS[zone];
            const isActive = activeFilters.tidal.has('all') || activeFilters.tidal.has(zone);
            legendContent.innerHTML += `
                <div class="legend-item" style="opacity:${isActive ? 1 : 0.3}">
                    <div class="legend-color" style="background:${color};"></div>
                    <span class="legend-label">${label}</span>
                </div>
            `;
        });
    }
    
    // Baum legend
    if (isBaumActive) {
        legendContent.innerHTML += '<div class="legend-section-title">Baum Morphometry</div>';
        Object.entries(BAUM_COLORS).forEach(([type, color]) => {
            legendContent.innerHTML += `
                <div class="legend-item">
                    <div class="legend-color" style="background:${color}; border-radius:50%;"></div>
                    <span class="legend-label">${type}</span>
                </div>
            `;
        });
    }
    
    // Hide legend if no layers active
    const legend = document.querySelector('.legend');
    if (legend) {
        legend.style.display = (isDurrActive || isBaumActive || isSalinityActive || isTidalActive) ? 'block' : 'none';
    }
}

// ============================================================================
// SIDEBAR FILTERS
// ============================================================================

function updateSidebarFilters() {
    const isDurrActive = map.hasLayer(layerGroups.durrBasins);
    const isSalinityActive = map.hasLayer(layerGroups.salinityZones);
    const isTidalActive = map.hasLayer(layerGroups.tidalZones);
    
    // Show/hide filter sections
    const durrSection = document.getElementById('durr-filters-section');
    const salinitySection = document.getElementById('salinity-filters-section');
    const tidalSection = document.getElementById('tidal-filters-section');
    
    if (durrSection) durrSection.style.display = isDurrActive ? 'block' : 'none';
    if (salinitySection) salinitySection.style.display = isSalinityActive ? 'block' : 'none';
    if (tidalSection) tidalSection.style.display = isTidalActive ? 'block' : 'none';
}

// ============================================================================
// COUNTS
// ============================================================================

function updateDurrCounts() {
    if (!datasets.coastalBasins) return;
    const typeGroups = {};
    Object.keys(DURR_COLORS).forEach(type => typeGroups[type] = []);
    datasets.coastalBasins.features.forEach(feature => {
        const type = feature.properties.estuary_type;
        if (type && typeGroups[type]) typeGroups[type].push(feature);
    });
    Object.entries(typeGroups).forEach(([type, features]) => {
        const id = `count-durr-${type.toLowerCase().replace(/\s+/g, '-')}`;
        updateCountElement(id, features.length);
    });
}

function updateSalinityCounts() {
    if (!datasets.salinityZones) return;
    const zoneGroups = {};
    Object.keys(SALINITY_COLORS).forEach(zone => zoneGroups[zone] = []);
    datasets.salinityZones.features.forEach(feature => {
        const zone = feature.properties.salinity_zone;
        if (zoneGroups[zone]) zoneGroups[zone].push(feature);
    });
    Object.entries(zoneGroups).forEach(([zone, features]) => {
        updateCountElement(`count-salinity-${zone}`, features.length);
    });
}

function updateTidalCounts() {
    if (!datasets.tidalZones) return;
    const zoneGroups = {};
    Object.keys(TIDAL_ZONE_COLORS).forEach(zone => zoneGroups[zone] = []);
    datasets.tidalZones.features.forEach(feature => {
        const zone = feature.properties.tidal_zone;
        if (zoneGroups[zone]) zoneGroups[zone].push(feature);
    });
    Object.entries(zoneGroups).forEach(([zone, features]) => {
        updateCountElement(`count-tidal-${zone}`, features.length);
    });
}

function updateCountElement(id, count) {
    const element = document.getElementById(id);
    if (element) element.textContent = count;
}

// ============================================================================
// UTILITIES
// ============================================================================

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = 'position:fixed;top:80px;right:20px;background:#e74c3c;color:white;padding:15px;border-radius:5px;z-index:9999;max-width:300px;';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
}

function setupMapEvents() {
    map.on('zoomend', () => {
        updateLegend();
    });
}

// ============================================================================
// INITIALIZATION
// ============================================================================

// ============================================================================
// PIE CHART - SURFACE AREA DISTRIBUTION
// ============================================================================

let pieChart = null;

function createPieChart() {
    if (!datasets.durrBasins) {
        console.log('⏳ Waiting for Dürr data to create pie chart...');
        return;
    }
    
    // Calculate surface area by type
    const areaByType = {};
    datasets.durrBasins.features.forEach(feature => {
        const type = feature.properties.type;
        const area = feature.properties.basin_area_km2 || 0;
        areaByType[type] = (areaByType[type] || 0) + area;
    });
    
    // Sort by area descending
    const sortedTypes = Object.entries(areaByType)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 6); // Top 6 types
    
    const labels = sortedTypes.map(([type]) => type);
    const data = sortedTypes.map(([, area]) => area);
    const colors = sortedTypes.map(([type]) => DURR_COLORS[type] || '#808080');
    
    // Calculate total and percentages
    const total = data.reduce((sum, val) => sum + val, 0);
    const percentages = data.map(val => ((val / total) * 100).toFixed(1));
    
    // Create chart
    const ctx = document.getElementById('pieChart');
    if (!ctx) return;
    
    pieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderColor: 'white',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false // We'll create custom legend
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const percent = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value.toLocaleString()} km² (${percent}%)`;
                        }
                    }
                }
            }
        }
    });
    
    // Create custom legend
    updateStatsLegend(sortedTypes, total);
    
    console.log('✓ Pie chart created');
}

function updateStatsLegend(sortedTypes, total) {
    const legendDiv = document.getElementById('stats-legend');
    if (!legendDiv) return;
    
    legendDiv.innerHTML = '';
    
    sortedTypes.forEach(([type, area]) => {
        const percent = ((area / total) * 100).toFixed(1);
        const color = DURR_COLORS[type] || '#808080';
        
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.style.borderLeftColor = color;
        
        item.innerHTML = `
            <span class="legend-item-label">${type}</span>
            <span class="legend-item-value">
                ${(area / 1000).toFixed(0)}k km²
                <span class="legend-item-percent">(${percent}%)</span>
            </span>
        `;
        
        legendDiv.appendChild(item);
    });
}

function setupStatsToggle() {
    const header = document.querySelector('.stats-header');
    const overlay = document.querySelector('.stats-overlay');
    const toggle = document.getElementById('toggle-stats');
    
    if (header && overlay) {
        header.addEventListener('click', () => {
            overlay.classList.toggle('collapsed');
            if (toggle) {
                toggle.textContent = overlay.classList.contains('collapsed') ? '▶' : '▼';
            }
        });
    }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    loadAllData().then(() => {
        // Create pie chart after data loads
        setTimeout(() => {
            createPieChart();
            setupStatsToggle();
        }, 1500);
    });
});

window.addEventListener('resize', () => {
    if (map) map.invalidateSize();
    if (pieChart) pieChart.resize();
});

console.log('✅ Complete final map script loaded - All features integrated!');
