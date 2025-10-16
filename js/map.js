// ============================================================================
// Global Water Body Surface Area Atlas - Interactive Map  
// Simplified High-Performance Implementation
// ============================================================================

// Make color schemes globally accessible
window.DURR_COLORS = {
    'Small deltas': '#8B4513',
    'Tidal System': '#FF8C00',
    'Tidal systems': '#FF8C00',
    'Lagoons': '#50C878',
    'Lagoon': '#3498DB',
    'Fjords and fjaerds': '#4169E1',
    'Fjord/Fjaerd': '#4169E1',
    'Fjord': '#4169E1',
    'Large Rivers': '#27AE60',
    'Large Rivers with tidal deltas': '#16A085',
    'Karst': '#9370DB',
    'Karst system': '#9370DB',
    'Arheic': '#E74C3C',
    'Arheic system': '#E74C3C',
    'Atheic': '#E74C3C',
    'Atheic system': '#E74C3C',
    'Endorheic or Glaciated': '#95A5A6',
    'Unclassified': '#34495E',
    'Delta': '#E67E22',
    'Coastal Plain': '#F39C12',
    'Small Delta': '#8B4513',
    'Archeic': '#E74C3C',
    'Archeic system': '#E74C3C'
};

window.SALINITY_COLORS = {
    'freshwater': '#2166ac',
    'oligohaline': '#67a9cf',
    'mesohaline': '#d1e5f0',
    'polyhaline': '#fddbc7',
    'euhaline': '#ef8a62',
    'hyperhaline': '#b2182b'
};

let map;
let layerGroups = {};
let datasets = {};
let currentBasemap = null;
let currentLabels = null;

// Define available basemaps
const basemaps = {
    'natgeo': {
        name: 'ESRI National Geographic',
        layer: 'https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}',
        attribution: 'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC',
        maxZoom: 16,
        labels: null
    },
    'imagery-hybrid': {
        name: 'ESRI Imagery Hybrid',
        layer: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
        maxZoom: 18,
        labels: 'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}'
    },
    'imagery': {
        name: 'ESRI World Imagery',
        layer: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
        maxZoom: 18,
        labels: null
    },
    'ocean': {
        name: 'ESRI Ocean Basemap',
        layer: 'https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}',
        attribution: 'Tiles &copy; Esri &mdash; Sources: GEBCO, NOAA, CHS, OSU, UNH, CSUMB, National Geographic, DeLorme, NAVTEQ, and Esri',
        maxZoom: 13,
        labels: 'https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Reference/MapServer/tile/{z}/{y}/{x}'
    },
    'topo': {
        name: 'ESRI World Topo',
        layer: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
        attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community',
        maxZoom: 18,
        labels: null
    },
    'osm': {
        name: 'OpenStreetMap',
        layer: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
        labels: null
    },
    'cartodb-light': {
        name: 'CartoDB Positron',
        layer: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        maxZoom: 19,
        labels: null
    }
};

function initMap() {
    console.log('🗺️ Initializing map...');
    map = L.map('map', {
        center: [20, 0],
        zoom: 3,
        zoomControl: true,
        preferCanvas: true
    });

    // Initialize with ESRI National Geographic (default)
    switchBasemap('natgeo');

    console.log('✅ Map initialized with ESRI National Geographic');
}

function switchBasemap(basemapId) {
    const basemapConfig = basemaps[basemapId];
    if (!basemapConfig) {
        console.error(`❌ Unknown basemap: ${basemapId}`);
        return;
    }
    
    // Remove existing basemap and labels
    if (currentBasemap) {
        map.removeLayer(currentBasemap);
    }
    if (currentLabels) {
        map.removeLayer(currentLabels);
    }
    
    // Add new basemap
    currentBasemap = L.tileLayer(basemapConfig.layer, {
        attribution: basemapConfig.attribution,
        maxZoom: basemapConfig.maxZoom
    }).addTo(map);
    
    // Add labels if specified
    if (basemapConfig.labels) {
        currentLabels = L.tileLayer(basemapConfig.labels, {
            attribution: '',
            maxZoom: basemapConfig.maxZoom
        }).addTo(map);
    }
    
    console.log(`✅ Switched to basemap: ${basemapConfig.name}`);
}

async function loadAllData() {
    console.log('�� Loading data...');
    if (!window.sidebarConfig) {
        console.error('❌ Sidebar config not available');
        return;
    }
    try {
        const loadPromises = [];
        window.sidebarConfig.forEach(category => {
            category.layers.forEach(layer => {
                loadPromises.push(loadLayerData(layer));
            });
        });
        await Promise.all(loadPromises);
        console.log('✅ All data loaded');
        setupLayerControls();
    } catch (error) {
        console.error('❌ Error loading data:', error);
    }
}

async function loadLayerData(layerConfig) {
    try {
        console.log(`📂 Loading ${layerConfig.name}...`);
        const response = await fetch(layerConfig.dataPath);
        const data = await response.json();
        datasets[layerConfig.id] = data;
        console.log(`✓ Loaded ${data.features.length} features for ${layerConfig.name}`);
        return data;
    } catch (error) {
        console.error(`❌ Error loading ${layerConfig.name}:`, error);
        return null;
    }
}

function setupLayerControls() {
    console.log('🎛️ Setting up layer controls...');
    if (!window.sidebarConfig) {
        setTimeout(setupLayerControls, 100);
        return;
    }
    window.sidebarConfig.forEach(category => {
        category.layers.forEach(layer => {
            if (!layerGroups[layer.id]) {
                layerGroups[layer.id] = L.layerGroup();
            }
            const checkbox = document.getElementById(layer.layerId);
            if (checkbox) {
                checkbox.addEventListener('change', (e) => {
                    handleLayerToggle(layer, e.target.checked);
                });
                console.log(`✓ Registered ${layer.name}`);
            }
        });
    });
}

function handleLayerToggle(layerConfig, isVisible) {
    const layerGroup = layerGroups[layerConfig.id];
    if (isVisible) {
        console.log(`👁️ Showing ${layerConfig.name}`);
        if (datasets[layerConfig.id]) {
            renderLayer(layerConfig);
            if (!map.hasLayer(layerGroup)) {
                map.addLayer(layerGroup);
            }
        }
    } else {
        console.log(`🙈 Hiding ${layerConfig.name}`);
        if (map.hasLayer(layerGroup)) {
            map.removeLayer(layerGroup);
        }
    }
    updateLegend();
}

function renderLayer(layerConfig) {
    const layerGroup = layerGroups[layerConfig.id];
    const dataset = datasets[layerConfig.id];
    if (!dataset) {
        console.warn(`⚠️ No data for ${layerConfig.id}`);
        return;
    }
    layerGroup.clearLayers();
    console.log(`🎨 Rendering ${dataset.features.length} features for ${layerConfig.name}`);
    console.log(`   Style Property: ${layerConfig.styleProperty}`);
    console.log(`   Color Scheme: ${layerConfig.colorScheme}`);
    
    const colorScheme = layerConfig.colorScheme ? window[layerConfig.colorScheme] : null;
    const defaultColor = layerConfig.layerColor || '#3498db';
    
    console.log(`   Color Scheme Object:`, colorScheme);
    
    // Track unique colors used
    const colorsUsed = new Set();
    
    dataset.features.forEach(feature => {
        let color = defaultColor;
        if (layerConfig.styleProperty && colorScheme) {
            const styleValue = feature.properties[layerConfig.styleProperty];
            if (styleValue && colorScheme[styleValue]) {
                color = colorScheme[styleValue];
                colorsUsed.add(`${styleValue}: ${color}`);
            }
        }
        if (layerConfig.geometryType === 'polygon') {
            const layer = L.geoJSON(feature, {
                style: {
                    fillColor: color,
                    weight: 1,
                    opacity: 0.8,
                    color: '#333',
                    fillOpacity: 0.6
                },
                onEachFeature: (feature, layer) => {
                    layer.bindPopup(createPopup(feature, layerConfig));
                }
            });
            layerGroup.addLayer(layer);
        } else if (layerConfig.geometryType === 'point') {
            const coords = feature.geometry.coordinates;
            const marker = L.circleMarker([coords[1], coords[0]], {
                radius: 4,
                fillColor: color,
                color: '#fff',
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
            }).bindPopup(createPopup(feature, layerConfig));
            layerGroup.addLayer(marker);
        }
    });
    
    console.log(`✓ Rendered ${layerConfig.name}`);
    console.log(`   Colors used:`, Array.from(colorsUsed));
}

function createPopup(feature, layerConfig) {
    const props = feature.properties;
    let html = `<div class="popup-content"><h3 class="popup-title">${layerConfig.name}</h3><div class="popup-info">`;
    const importantKeys = ['name', 'estuary_name', 'estuary_type', 'type_detailed', 'typology', 'salinity_class', 'basin_area_km2', 'distance_to_coast_km', 'discharge', 'salinity'];
    importantKeys.forEach(key => {
        if (props[key] !== undefined && props[key] !== null) {
            const value = typeof props[key] === 'number' ? props[key].toFixed(2) : props[key];
            html += `<strong>${key}:</strong> ${value}<br>`;
        }
    });
    html += `</div></div>`;
    return html;
}

function updateLegend() {
    console.log('🔄 Updating legend...');
    const legendContent = document.getElementById('legend-content');
    const legendTitle = document.getElementById('legend-title');
    if (!legendContent || !window.sidebarConfig) return;
    
    legendContent.innerHTML = '';
    if (legendTitle) legendTitle.textContent = 'Map Legend';
    let anyLayerActive = false;
    
    window.sidebarConfig.forEach(category => {
        category.layers.forEach(layerConfig => {
            const layerGroup = layerGroups[layerConfig.id];
            if (!layerGroup || !map.hasLayer(layerGroup)) return;
            
            anyLayerActive = true;
            console.log(`📋 Adding legend for ${layerConfig.name}`);
            console.log(`   Has styleProperty: ${!!layerConfig.styleProperty}`);
            console.log(`   Has colorScheme: ${!!layerConfig.colorScheme}`);
            
            legendContent.innerHTML += `<div class="legend-section-title" style="margin-top:${legendContent.innerHTML ? '10px' : '0'};">${layerConfig.legendTitle}</div>`;
            
            if (layerConfig.styleProperty && layerConfig.colorScheme) {
                const colorScheme = window[layerConfig.colorScheme];
                console.log(`   Color Scheme Found:`, !!colorScheme);
                
                if (colorScheme) {
                    const uniqueValues = new Set();
                    const dataset = datasets[layerConfig.id];
                    
                    if (dataset && dataset.features) {
                        dataset.features.forEach(feature => {
                            const value = feature.properties[layerConfig.styleProperty];
                            if (value) uniqueValues.add(value);
                        });
                    }
                    
                    console.log(`   Unique values found: ${uniqueValues.size}`);
                    console.log(`   Values:`, Array.from(uniqueValues));
                    
                    Array.from(uniqueValues).sort().forEach(value => {
                        const color = colorScheme[value] || '#3498db';
                        const shape = layerConfig.geometryType === 'point' ? 'border-radius:50%;' : '';
                        console.log(`   Legend item: ${value} -> ${color}`);
                        legendContent.innerHTML += `<div class="legend-item"><div class="legend-color" style="background:${color}; ${shape}"></div><span class="legend-label">${value}</span></div>`;
                    });
                }
            } else {
                const shape = layerConfig.geometryType === 'point' ? 'border-radius:50%; width:8px; height:8px;' : '';
                const color = layerConfig.layerColor || '#3498db';
                legendContent.innerHTML += `<div class="legend-item"><div class="legend-color" style="background:${color}; ${shape}"></div><span class="legend-label" style="font-size:0.85em;">${layerConfig.description || layerConfig.name}</span></div>`;
            }
        });
    });
    const legend = document.querySelector('.legend');
    if (legend) {
        legend.style.display = anyLayerActive ? 'block' : 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Map script ready - waiting for sidebar initialization...');
    // Map initialization is handled by index.html after sidebar is ready
});

window.addEventListener('resize', () => {
    if (map) map.invalidateSize();
});

console.log('✅ Map script loaded');
