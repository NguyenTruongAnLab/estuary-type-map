// ============================================================================
// Global Water Body Surface Area Atlas - Interactive Map
// ============================================================================
// Complete implementation with all data layers:
// - Dürr Estuary Types (geomorphology) - 2 versions
// - Baum Morphometry (large estuaries)
// - GlobSalt Stations (salinity monitoring)
// - DynQual River Characteristics (discharge/salinity)
// - GCC Coastal Characteristics
// - Salinity Zones & Tidal Zones
// ============================================================================

// ============================================================================
// COLOR SCHEMES
// ============================================================================

// Corrected Dürr et al. (2011) color scheme
const DURR_COLORS = {
    'Small deltas': '#8b4513',
    'Tidal systems': '#ff8c00',
    'Lagoons': '#50c878',
    'Fjords and fjaerds': '#4a90e2',
    'Large Rivers': '#27ae60',
    'Large Rivers with tidal deltas': '#16a085',
    'Karst': '#9370db',
    'Arheic': '#e74c3c',
    'Endorheic or Glaciated': '#95a5a6',
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
    'freshwater': '<0.5 PSU',
    'oligohaline': '0.5-5 PSU',
    'mesohaline': '5-18 PSU',
    'polyhaline': '18-25 PSU',
    'euhaline': '25-35 PSU',
    'hyperhaline': '>35 PSU'
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
    coastalBasins: L.layerGroup(),    // Coastal basins with Dürr types
    durrReference: L.layerGroup(),    // Original Dürr full catchments
    baum: L.layerGroup(),             // Baum morphometry points
    globsalt: L.layerGroup(),         // GlobSalt monitoring stations
    dynqual: L.layerGroup(),          // DynQual river characteristics
    gcc: L.layerGroup()               // GCC coastal characteristics
};

let datasets = {};
let activeFilters = {
    durr: new Set(['all'])
};

let currentViewMode = 'coastal'; // 'coastal' or 'reference'
let loadingIndicator;
let pieChart = null;

// ============================================================================
// INITIALIZATION
// ============================================================================

function initMap() {
    console.log('🗺️ Initializing Global Water Body Surface Area Atlas...');
    
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

    setupLayerControls();
    setupFilters();
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
        
        // Load data in parallel for faster loading
        await Promise.all([
            loadCoastalBasins(),
            loadDurrReference(),
            loadBaumData(),
            loadGlobSaltStations(),
            loadDynQualData(),
            loadGCCData()
        ]);
        
        console.log('✅ All data loaded successfully!');
        
        // Initialize visualization
        updateCoastalBasins();
        updateDurrReference();
        updateBaumLayer();
        updateLegend();
        
        // Create pie chart
        setTimeout(() => {
            createPieChart();
            setupStatsToggle();
        }, 500);
        
    } catch (error) {
        console.error('❌ Error loading data:', error);
        showError('Failed to load data: ' + error.message);
    } finally {
        setLoading(false);
    }
}

async function loadCoastalBasins() {
    console.log('📂 Loading tidal basins (precise Dürr classification)...');
    const response = await fetch('data/web/tidal_basins_precise.geojson');
    if (!response.ok) throw new Error('Failed to load tidal basins');
    datasets.coastalBasins = await response.json();
    console.log(`✓ Loaded ${datasets.coastalBasins.features.length} tidal basins (HydroSHEDS Level 7 + GRIT network)`);
}

async function loadDurrReference() {
    console.log('📂 Loading Dürr reference catchments...');
    const response = await fetch('data/web/durr_estuaries.geojson');
    if (!response.ok) throw new Error('Failed to load Dürr reference');
    datasets.durrReference = await response.json();
    console.log(`✓ Loaded ${datasets.durrReference.features.length} Dürr catchments`);
}

async function loadBaumData() {
    console.log('📂 Loading Baum morphometry...');
    const response = await fetch('data/web/baum_morphometry.geojson');
    if (!response.ok) throw new Error('Failed to load Baum data');
    datasets.baum = await response.json();
    console.log(`✓ Loaded ${datasets.baum.features.length} Baum estuaries`);
}

async function loadGlobSaltStations() {
    console.log('📂 Loading GlobSalt stations...');
    try {
        const response = await fetch('data/web/globsalt_stations.geojson');
        if (!response.ok) throw new Error('GlobSalt file not found');
        datasets.globsalt = await response.json();
        console.log(`✓ Loaded ${datasets.globsalt.features.length} GlobSalt stations`);
    } catch (error) {
        console.warn('⚠️ GlobSalt data not available:', error.message);
        datasets.globsalt = null;
    }
}

async function loadDynQualData() {
    console.log('📂 Loading DynQual river characteristics...');
    try {
        const response = await fetch('data/web/dynqual_river_characteristics.geojson');
        if (!response.ok) throw new Error('DynQual file not found');
        datasets.dynqual = await response.json();
        console.log(`✓ Loaded ${datasets.dynqual.features.length} DynQual points`);
    } catch (error) {
        console.warn('⚠️ DynQual data not available:', error.message);
        datasets.dynqual = null;
    }
}

async function loadGCCData() {
    console.log('📂 Loading GCC coastal characteristics...');
    try {
        const response = await fetch('data/web/gcc_coastal_characteristics.geojson');
        if (!response.ok) throw new Error('GCC file not found');
        datasets.gcc = await response.json();
        console.log(`✓ Loaded ${datasets.gcc.features.length} GCC segments`);
    } catch (error) {
        console.warn('⚠️ GCC data not available:', error.message);
        datasets.gcc = null;
    }
}

// ============================================================================
// LAYER RENDERING
// ============================================================================

function updateCoastalBasins() {
    layerGroups.coastalBasins.clearLayers();
    if (!datasets.coastalBasins) return;
    
    console.log('📊 Updating coastal basins...');
    
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
                fillOpacity: 0.6,
                color: color,
                weight: 1,
                opacity: 0.8
            }
        }).bindPopup(`
            <div class="popup-content">
                <h3 class="popup-title">${props.estuary_name || 'Tidal Basin'}</h3>
                <div class="popup-type" style="background: ${color};">${props.estuary_type}</div>
                <div class="popup-info">
                    <strong>Basin ID:</strong> ${props.HYBAS_ID}<br>
                    <strong>Area:</strong> ${(props.basin_area_km2 || 0).toLocaleString()} km²<br>
                    <strong>Distance to Coast:</strong> ${(props.distance_to_coast_km || 0).toFixed(1)} km<br>
                    <strong>Stream Order:</strong> ${props.stream_order || 'N/A'}<br>
                    <strong>Seed Basin:</strong> ${props.is_seed ? 'Yes (Ocean Outlet)' : 'No (Upstream)'}
                </div>
                <div class="popup-source">
                    <strong>Method:</strong> HydroSHEDS Level 7 + GRIT river connectivity<br>
                    <strong>Classification:</strong> Corrected Dürr et al. (2011)
                </div>
            </div>
        `);
        
        layerGroups.coastalBasins.addLayer(polygon);
    });
    
    console.log(`📍 Displayed ${filteredFeatures.length} coastal basins`);
}

function updateDurrReference() {
    layerGroups.durrReference.clearLayers();
    if (!datasets.durrReference) return;
    
    console.log('📂 Updating Dürr reference catchments...');
    
    datasets.durrReference.features.forEach(feature => {
        const props = feature.properties;
        const type = props.type || 'Unclassified';
        const color = DURR_COLORS[type] || '#808080';
        
        const polygon = L.geoJSON(feature, {
            style: {
                fillColor: color,
                fillOpacity: 0.2,
                color: '#666',
                weight: 1,
                opacity: 0.6,
                dashArray: '5, 5'
            }
        }).bindPopup(`
            <div class="popup-content">
                <h3 class="popup-title">${props.name || 'Unnamed'}</h3>
                <div class="popup-type" style="background: ${color};">${type}</div>
                <div class="popup-info">
                    <strong>Detailed Type:</strong> ${props.type_detailed || 'N/A'}<br>
                    <strong>Basin Area:</strong> ${(props.basin_area_km2 || 0).toLocaleString()} km²
                </div>
                <div class="popup-source">
                    <strong>Source:</strong> Dürr et al. (2011) - Full Watershed
                </div>
            </div>
        `);
        
        layerGroups.durrReference.addLayer(polygon);
    });
    
    console.log(`📍 Displayed ${datasets.durrReference.features.length} Dürr catchments`);
}

function updateBaumLayer() {
    layerGroups.baum.clearLayers();
    if (!datasets.baum) return;
    
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
                <div class="popup-info">
                    <strong>Country:</strong> ${props.country || 'N/A'}<br>
                    <strong>Coordinates:</strong> ${props.lat.toFixed(2)}, ${props.lon.toFixed(2)}
                </div>
                <div class="popup-source">
                    <strong>Source:</strong> Baum et al. (2024)
                </div>
            </div>
        `);
        
        layerGroups.baum.addLayer(marker);
    });
    
    console.log(`📍 Displayed ${datasets.baum.features.length} Baum estuaries`);
}

function updateGlobSaltLayer() {
    layerGroups.globsalt.clearLayers();
    if (!datasets.globsalt) return;
    
    datasets.globsalt.features.forEach(feature => {
        const props = feature.properties;
        const salinity = props.salinity_mean_psu || props.salinity_median_psu || 0;
        const salinityClass = props.salinity_zone || props.salinity_class || 'freshwater';
        const color = SALINITY_COLORS[salinityClass] || '#808080';
        
        const coords = feature.geometry.coordinates;
        const marker = L.circleMarker([coords[1], coords[0]], {
            radius: 4,
            fillColor: color,
            color: '#fff',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.7
        }).bindPopup(`
            <div class="popup-content">
                <h3 class="popup-title">GlobSalt Station</h3>
                <div class="popup-type" style="background: ${color};">${salinityClass}</div>
                <div class="popup-info">
                    <strong>Mean Salinity:</strong> ${salinity.toFixed(2)} PSU<br>
                    <strong>Std Dev:</strong> ${(props.salinity_std_psu || 0).toFixed(2)} PSU<br>
                    <strong>Measurements:</strong> ${props.n_measurements || 'N/A'}<br>
                    <strong>Water Type:</strong> ${props.Water_type || 'N/A'}
                </div>
                <div class="popup-source">
                    <strong>Source:</strong> GlobSalt v2.0
                </div>
            </div>
        `);
        
        layerGroups.globsalt.addLayer(marker);
    });
    
    console.log(`📍 Displayed ${datasets.globsalt.features.length} GlobSalt stations`);
}

function updateDynQualLayer() {
    layerGroups.dynqual.clearLayers();
    if (!datasets.dynqual) return;
    
    datasets.dynqual.features.forEach(feature => {
        const props = feature.properties;
        const discharge = props.discharge || 0;
        const salinity = props.salinity || 0;
        const salinityClass = props.salinity_class || 'freshwater';
        const color = SALINITY_COLORS[salinityClass] || '#4a90e2';
        
        const coords = feature.geometry.coordinates;
        const marker = L.circleMarker([coords[1], coords[0]], {
            radius: 5,
            fillColor: color,
            color: '#fff',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.7
        }).bindPopup(`
            <div class="popup-content">
                <h3 class="popup-title">DynQual River Point</h3>
                <div class="popup-info">
                    <strong>Discharge:</strong> ${discharge.toFixed(1)} m³/s<br>
                    <strong>Salinity:</strong> ${salinity.toFixed(2)} PSU<br>
                    <strong>Classification:</strong> ${salinityClass}
                    ${props.temperature ? `<br><strong>Temperature:</strong> ${props.temperature.toFixed(1)}°C` : ''}
                </div>
                <div class="popup-source">
                    <strong>Source:</strong> Jones et al. (2023) - DynQual 10km
                </div>
            </div>
        `);
        
        layerGroups.dynqual.addLayer(marker);
    });
    
    console.log(`📍 Displayed ${datasets.dynqual.features.length} DynQual points`);
}

function updateGCCLayer() {
    layerGroups.gcc.clearLayers();
    if (!datasets.gcc) return;
    
    datasets.gcc.features.forEach(feature => {
        const props = feature.properties;
        const coords = feature.geometry.coordinates;
        
        const marker = L.circleMarker([coords[1], coords[0]], {
            radius: 4,
            fillColor: '#3498db',
            color: '#fff',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.6
        }).bindPopup(`
            <div class="popup-content">
                <h3 class="popup-title">GCC Coastal Segment</h3>
                <div class="popup-info">
                    <strong>ID:</strong> ${props.id || 'N/A'}<br>
                    ${Object.entries(props).slice(0, 5).map(([key, val]) => 
                        key !== 'id' ? `<strong>${key}:</strong> ${typeof val === 'number' ? val.toFixed(2) : val}<br>` : ''
                    ).join('')}
                </div>
                <div class="popup-source">
                    <strong>Source:</strong> Athanasiou et al. (2024) - GCC
                </div>
            </div>
        `);
        
        layerGroups.gcc.addLayer(marker);
    });
    
    console.log(`📍 Displayed ${datasets.gcc.features.length} GCC segments`);
}

// ============================================================================
// LAYER CONTROLS
// ============================================================================

function setupLayerControls() {
    const layerToggles = {
        'layer-coastal-basins': { group: layerGroups.coastalBasins, update: updateCoastalBasins },
        'layer-durr-reference': { group: layerGroups.durrReference, update: updateDurrReference },
        'layer-baum': { group: layerGroups.baum, update: updateBaumLayer },
        'layer-globsalt': { group: layerGroups.globsalt, update: updateGlobSaltLayer },
        'layer-dynqual': { group: layerGroups.dynqual, update: updateDynQualLayer },
        'layer-gcc': { group: layerGroups.gcc, update: updateGCCLayer }
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

// ============================================================================
// LEGEND
// ============================================================================

function updateLegend() {
    const legendContent = document.getElementById('legend-content');
    const legendTitle = document.getElementById('legend-title');
    if (!legendContent) return;
    
    legendContent.innerHTML = '';
    
    const isCoastalActive = map.hasLayer(layerGroups.coastalBasins);
    const isDurrRefActive = map.hasLayer(layerGroups.durrReference);
    const isBaumActive = map.hasLayer(layerGroups.baum);
    const isGlobSaltActive = map.hasLayer(layerGroups.globsalt);
    const isDynQualActive = map.hasLayer(layerGroups.dynqual);
    const isGCCActive = map.hasLayer(layerGroups.gcc);
    
    // Update title
    if (legendTitle) legendTitle.textContent = 'Map Legend';
    
    // Coastal Basins
    if (isCoastalActive) {
        legendContent.innerHTML += '<div class="legend-section-title">Estuarine Types (Basins)</div>';
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
    
    // Dürr Reference
    if (isDurrRefActive) {
        legendContent.innerHTML += '<div class="legend-section-title" style="margin-top:10px;">Full Dürr Watersheds</div>';
        legendContent.innerHTML += `
            <div class="legend-item">
                <div style="width:20px; height:2px; border-top:2px dashed #666;"></div>
                <span class="legend-label" style="font-size:0.85em;">Original Catchments</span>
            </div>
        `;
    }
    
    // Baum
    if (isBaumActive) {
        legendContent.innerHTML += '<div class="legend-section-title" style="margin-top:10px;">Baum Morphometry</div>';
        Object.entries(BAUM_COLORS).forEach(([type, color]) => {
            legendContent.innerHTML += `
                <div class="legend-item">
                    <div class="legend-color" style="background:${color}; border-radius:50%;"></div>
                    <span class="legend-label">${type}</span>
                </div>
            `;
        });
    }
    
    // GlobSalt
    if (isGlobSaltActive) {
        legendContent.innerHTML += '<div class="legend-section-title" style="margin-top:10px;">GlobSalt Stations</div>';
        legendContent.innerHTML += `
            <div class="legend-item">
                <div class="legend-color" style="background:#3498db; border-radius:50%; width:8px; height:8px;"></div>
                <span class="legend-label" style="font-size:0.85em;">Monitoring Stations</span>
            </div>
        `;
    }
    
    // DynQual
    if (isDynQualActive) {
        legendContent.innerHTML += '<div class="legend-section-title" style="margin-top:10px;">DynQual River Data</div>';
        legendContent.innerHTML += `
            <div class="legend-item">
                <div class="legend-color" style="background:#4a90e2; border-radius:50%; width:10px; height:10px;"></div>
                <span class="legend-label" style="font-size:0.85em;">Discharge & Salinity (10km)</span>
            </div>
        `;
    }
    
    // GCC
    if (isGCCActive) {
        legendContent.innerHTML += '<div class="legend-section-title" style="margin-top:10px;">GCC Coastal Segments</div>';
        legendContent.innerHTML += `
            <div class="legend-item">
                <div class="legend-color" style="background:#3498db; border-radius:50%; width:8px; height:8px;"></div>
                <span class="legend-label" style="font-size:0.85em;">100km Coastal Segments</span>
            </div>
        `;
    }
    
    // Hide legend if no layers active
    const legend = document.querySelector('.legend');
    if (legend) {
        const anyActive = isCoastalActive || isDurrRefActive || isBaumActive || isGlobSaltActive || isDynQualActive || isGCCActive;
        legend.style.display = anyActive ? 'block' : 'none';
    }
}

// ============================================================================
// PIE CHART - SURFACE AREA DISTRIBUTION
// ============================================================================

function createPieChart() {
    if (!datasets.coastalBasins) {
        console.log('⏳ Waiting for tidal basins data to create pie chart...');
        return;
    }
    
    // Calculate counts and surface area by type from TIDAL BASINS (not Dürr reference)
    const statsByType = {};
    
    datasets.coastalBasins.features.forEach(feature => {
        const type = feature.properties.estuary_type || 'Unclassified';
        const area = feature.properties.basin_area_km2 || 0;
        
        if (!statsByType[type]) {
            statsByType[type] = { count: 0, area: 0 };
        }
        statsByType[type].count++;
        statsByType[type].area += area;
    });
    
    // Sort by area descending
    const sortedTypes = Object.entries(statsByType)
        .sort((a, b) => b[1].area - a[1].area);
    
    // Show all types (not just top 6)
    
    const labels = sortedTypes.map(([type]) => type);
    const data = sortedTypes.map(([, stats]) => stats.area);
    const colors = sortedTypes.map(([type]) => DURR_COLORS[type] || '#808080');
    
    // Calculate total
    const totalArea = data.reduce((sum, val) => sum + val, 0);
    const totalCount = Object.values(statsByType).reduce((sum, stats) => sum + stats.count, 0);
    
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
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const type = labels[context.dataIndex];
                            const area = data[context.dataIndex];
                            const count = statsByType[type].count;
                            const percent = ((area / totalArea) * 100).toFixed(1);
                            return [
                                `${type}`,
                                `Area: ${area.toLocaleString()} km²`,
                                `Count: ${count} estuaries`,
                                `${percent}% of total`
                            ];
                        }
                    }
                }
            }
        }
    });
    
    // Create custom legend
    updateStatsLegend(sortedTypes, totalArea, totalCount, statsByType);
    
    console.log('✓ Pie chart created');
}

function updateStatsLegend(sortedTypes, totalArea, totalCount, statsByType) {
    const legendDiv = document.getElementById('stats-legend');
    if (!legendDiv) return;
    
    legendDiv.innerHTML = `
        <div style="text-align:center; margin-bottom:10px; padding:10px; background:#f8f9fa; border-radius:5px;">
            <strong>Total: ${totalCount.toLocaleString()} tidal basins</strong><br>
            <span style="font-size:0.9em;">${(totalArea / 1000000).toFixed(2)} million km²</span>
        </div>
    `;
    
    sortedTypes.forEach(([type, stats]) => {
        const percent = ((stats.area / totalArea) * 100).toFixed(1);
        const color = DURR_COLORS[type] || '#808080';
        
        const item = document.createElement('div');
        item.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            margin: 5px 0;
            border-left: 4px solid ${color};
            background: #f8f9fa;
            border-radius: 3px;
        `;
        
        item.innerHTML = `
            <span style="font-weight:500; font-size:0.9em;">${type}</span>
            <div style="text-align:right;">
                <div style="font-size:0.85em;">${stats.count} estuaries</div>
                <div style="font-size:0.85em; color:#666;">${(stats.area / 1000).toFixed(0)}k km² (${percent}%)</div>
            </div>
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

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    loadAllData();
});

window.addEventListener('resize', () => {
    if (map) map.invalidateSize();
    if (pieChart) pieChart.resize();
});

console.log('✅ Global Water Body Surface Area Atlas - Map Script Loaded!');
