#!/usr/bin/env python3
"""
Create Tidal Basins from Coastal Rivers - Bottom-Up Approach
=============================================================

PURPOSE: Build tidal basin network from actual coastal rivers, NOT Dürr catchments

NEW PHILOSOPHY:
- Start with coastal basins (DIST_SINK=0, COAST=1) - ALL of them!
- Find GRIT rivers in coastal basins
- Trace upstream via GRIT river network connectivity
- Include all basins containing connected rivers
- Classify using Dürr AFTER (not before!)
- Result: More complete, river-verified tidal networks

ADVANTAGES:
✅ No dependency on Dürr spatial extent (which goes far inland)
✅ Uses actual river connectivity (GRIT) as primary criterion
✅ May discover estuaries not in Dürr 2011 dataset
✅ Based on modern data (HydroSHEDS 2018, GRIT 2022)
✅ No isolated inland basins (100% river-connected by design)

Author: Global Water Body Surface Area Atlas Project
Date: October 14, 2025
Version: 5.0 (BOTTOM-UP FROM RIVERS)
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import folium
from folium import plugins
import time
import warnings
warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_HYDROSHEDS = BASE_DIR / 'data' / 'raw' / 'hydrosheds'
RAW_GRIT = BASE_DIR / 'data' / 'raw' / 'GRIT-Michel_2025'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
OUTPUT_DIR = BASE_DIR / 'diagnostics_html'
OUTPUT_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

# Input files
BASINATLAS_FILE = RAW_HYDROSHEDS / 'BasinATLAS_v10_lev07_QGIS.gpkg'
GRIT_SEGMENTS_FILE = RAW_GRIT / 'GRITv06_segments_simple_GLOBAL_EPSG4326.gpkg'
DURR_CATCHMENT_FILE = BASE_DIR / 'data' / 'raw' / 'Worldwide-typology-Shapefile-Durr_2011' / 'typology_catchments.shp'
DURR_COASTLINE_FILE = BASE_DIR / 'data' / 'raw' / 'Worldwide-typology-Shapefile-Durr_2011' / 'typology_coastline.shp'

# Output files
TIDAL_BASINS_FULL = PROCESSED_DIR / 'tidal_basins_river_based_lev07.gpkg'
TIDAL_BASINS_WEB = PROCESSED_DIR / 'tidal_basins_river_based_lev07_web.geojson'
OUTPUT_MAP_NO_RIVERS = OUTPUT_DIR / 'tidal_basins_web.html'  # For web hosting
OUTPUT_MAP_WITH_RIVERS = OUTPUT_DIR / 'tidal_basins_with_rivers.html'  # Full version

# Parameters
MAX_DISTANCE_KM = 300  # Maximum distance from coast
MIN_ORDER = 1          # Minimum stream order
SIMPLIFY_WEB = 0.02    # Simplification for web (2.2 km)

# ==============================================================================
# STEP 1: FIND ALL COASTAL BASINS (NO DÜRR FILTER!)
# ==============================================================================

def find_all_coastal_basins(basins):
    """Get ALL basins draining to ocean within tidal distance"""
    print("\n" + "="*80)
    print("STEP 1: Finding ALL Tidal Basins (DISTANCE-BASED)")
    print("="*80)
    
    print(f"\n🎯 CORRECT Strategy:")
    print(f"   1. Find ALL basins draining to ocean (ENDO=0)")
    print(f"   2. Within tidal distance (DIST_SINK <= {MAX_DISTANCE_KM} km)")
    print(f"   3. NO COAST=1 filter (that's only 4,536 outlets!)")
    print(f"   4. This captures ALL upstream tidal basins!")
    
    # Get ALL basins draining to ocean within tidal distance
    tidal = basins[
        (basins['ENDO'] == 0) &                      # Drains to ocean (not inland lake)
        (basins['DIST_SINK'] <= MAX_DISTANCE_KM)     # Within tidal distance
    ].copy()
    
    print(f"\n✅ Found {len(tidal):,} tidal basins")
    print(f"   Distance range: {tidal['DIST_SINK'].min():.0f}-{tidal['DIST_SINK'].max():.0f} km")
    print(f"   Ocean outlets (DIST_SINK=0): {len(tidal[tidal['DIST_SINK']==0]):,}")
    print(f"   Upstream basins: {len(tidal[tidal['DIST_SINK']>0]):,}")
    
    return tidal

# ==============================================================================
# STEP 2: FIND GRIT RIVERS IN COASTAL BASINS
# ==============================================================================

def find_coastal_rivers(coastal_basins, grit_file, all_basins):
    """Find GRIT river segments in ALL coastal basins (not just DIST_SINK=0!)"""
    print("\n" + "="*80)
    print("STEP 2: Finding GRIT Rivers in ALL Coastal Basins")
    print("="*80)
    
    print(f"\n🌊 Loading GRIT river segments...")
    start_time = time.time()
    grit = gpd.read_file(grit_file, layer='lines')
    print(f"   Loaded {len(grit):,} river segments in {time.time()-start_time:.1f}s")
    
    # Ensure same CRS
    if grit.crs != coastal_basins.crs:
        grit = grit.to_crs(coastal_basins.crs)
    
    # CRITICAL: Find rivers in ALL coastal basins (not just DIST_SINK=0!)
    print(f"\n   Finding rivers in ALL coastal basins (within {MAX_DISTANCE_KM} km)...")
    grit_points = grit.copy()
    grit_points['geometry'] = grit_points.geometry.centroid
    
    # Spatial join with ALL coastal basins
    grit_in_coastal = gpd.sjoin(
        grit_points[['global_id', 'catchment_id', 'strahler_order', 'is_mainstem', 'domain', 'geometry']],
        coastal_basins[['HYBAS_ID', 'DIST_SINK', 'geometry']],
        how='inner',
        predicate='within'
    )
    
    # Find which basins at OCEAN (DIST_SINK=0) have rivers
    ocean_basins_with_rivers = grit_in_coastal[grit_in_coastal['DIST_SINK'] == 0]['HYBAS_ID'].unique()
    
    print(f"\n✅ Found {len(grit_in_coastal):,} river segments in coastal basins")
    print(f"   Unique GRIT catchments: {grit_in_coastal['catchment_id'].nunique():,}")
    print(f"   Coastal basins with rivers: {grit_in_coastal['HYBAS_ID'].nunique():,}")
    print(f"   Ocean basins (DIST_SINK=0) with rivers: {len(ocean_basins_with_rivers):,}")
    
    return grit, grit_in_coastal, ocean_basins_with_rivers

# ==============================================================================
# STEP 3: TRACE UPSTREAM VIA GRIT CONNECTIVITY
# ==============================================================================

def filter_and_clean(tidal_basins):
    """Apply final filters and mark seeds"""
    print("\n" + "="*80)
    print("STEP 2: Filtering and Cleaning")
    print("="*80)
    
    print(f"\n   Input basins: {len(tidal_basins):,}")
    
    # Mark seeds (ocean outlets)
    tidal_basins['is_seed'] = tidal_basins['DIST_SINK'] == 0
    
    # Apply size filter
    print(f"\n   Applying filter: Size >= 5 km²")
    tidal_clean = tidal_basins[tidal_basins['SUB_AREA'] >= 5].copy()
    
    print(f"\n✅ Final: {len(tidal_clean):,} basins")
    print(f"   Ocean outlets: {tidal_clean['is_seed'].sum():,}")
    print(f"   Upstream: {(~tidal_clean['is_seed']).sum():,}")
    print(f"   Total area: {tidal_clean['SUB_AREA'].sum():,.0f} km²")
    print(f"   Distance range: {tidal_clean['DIST_SINK'].min():.0f}-{tidal_clean['DIST_SINK'].max():.0f} km")
    
    return tidal_clean

# ==============================================================================
# STEP 4: CLASSIFY USING DÜRR (OPTIONAL)
# ==============================================================================

def classify_with_durr(tidal_basins, durr_catchment_file, durr_coastline_file):
    """Classify basins using BOTH Dürr catchments AND coastline"""
    print("\n" + "="*80)
    print("STEP 3: Classifying with Dürr (CATCHMENTS + COASTLINE)")
    print("="*80)
    
    # Remove any existing classification columns to avoid duplicates
    cols_to_drop = ['estuary_type', 'estuary_name', 'type_catchment', 'type_coastline', 'name_catchment']
    tidal_basins = tidal_basins.drop(columns=[c for c in cols_to_drop if c in tidal_basins.columns])
    
    # Load BOTH sources
    print(f"\n📊 Loading Dürr catchments...")
    durr_catchments = gpd.read_file(durr_catchment_file)
    print(f"   Catchments: {len(durr_catchments):,}")
    
    print(f"\n📊 Loading Dürr coastline...")
    durr_coastline = gpd.read_file(durr_coastline_file)
    print(f"   Coastline segments: {len(durr_coastline):,}")
    
    # Map FIN_TYP codes to estuary type names - CORRECT MAPPING FROM DÜRR DOCUMENTATION!
    # Source: Dürr et al. (2011) README file
    type_map = {
        0: 'Endorheic or Glaciated',
        1: 'Small deltas',              # Type I
        2: 'Tidal systems',             # Type II
        3: 'Lagoons',                   # Type III
        4: 'Fjords and fjaerds',        # Type IV
        5: 'Large Rivers',              # Type Va (Non-filter)
        51: 'Large Rivers with tidal deltas',  # Type Vb (Non-filter)
        6: 'Karst',                     # Type VI (Non-filter)
        7: 'Arheic',                    # Type VII (Non-filter)
        -9999: 'Unclassified'           # Missing data
    }
    
    # Apply to coastline
    durr_coastline['estuary_type'] = durr_coastline['FIN_TYP'].map(type_map)
    durr_coastline = durr_coastline[
        (durr_coastline['estuary_type'] != 'Unclassified') & 
        (durr_coastline['estuary_type'] != 'Endorheic or Glaciated')
    ].copy()
    
    # Apply to catchments
    durr_catchments['estuary_type'] = durr_catchments['FIN_TYP'].map(type_map)
    durr_catchments = durr_catchments[
        (durr_catchments['estuary_type'] != 'Unclassified') &
        (durr_catchments['estuary_type'] != 'Endorheic or Glaciated')
    ].copy()
    print(f"   Valid catchments (after filter): {len(durr_catchments):,}")
    print(f"   Valid coastline (after filter): {len(durr_coastline):,}")
    
    # Ensure same CRS
    if durr_catchments.crs != tidal_basins.crs:
        durr_catchments = durr_catchments.to_crs(tidal_basins.crs)
    if durr_coastline.crs != tidal_basins.crs:
        durr_coastline = durr_coastline.to_crs(tidal_basins.crs)
    
    # METHOD 1: Classify via CATCHMENTS (interior basins)
    print(f"\n   Method 1: Intersecting with Dürr catchments...")
    
    # Rename columns in durr_catchments BEFORE join to avoid duplicates
    durr_catch_cols = durr_catchments[['RECORDNAME', 'estuary_type', 'geometry']].copy()
    durr_catch_cols = durr_catch_cols.rename(columns={'estuary_type': 'type_catchment', 'RECORDNAME': 'name_catchment'})
    
    tidal_with_catchments = gpd.sjoin(
        tidal_basins,
        durr_catch_cols,
        how='left',
        predicate='intersects'
    )
    tidal_with_catchments = tidal_with_catchments.drop_duplicates(subset='HYBAS_ID', keep='first')
    if 'index_right' in tidal_with_catchments.columns:
        tidal_with_catchments = tidal_with_catchments.drop(columns=['index_right'])
    
    # METHOD 2: Classify via COASTLINE (nearest for ocean basins)
    print(f"\n   Method 2: Finding nearest coastline for ocean basins...")
    ocean_basins = tidal_with_catchments[tidal_with_catchments['DIST_SINK'] == 0].copy()
    
    # Create a separate GeoDataFrame with centroids
    ocean_centroids = gpd.GeoDataFrame(
        ocean_basins[['HYBAS_ID']],
        geometry=ocean_basins.geometry.centroid,
        crs=ocean_basins.crs
    )
    
    # Rename coastline column BEFORE join to avoid duplicates
    durr_coast_cols = durr_coastline[['estuary_type', 'geometry']].copy()
    durr_coast_cols = durr_coast_cols.rename(columns={'estuary_type': 'type_coastline'})
    
    ocean_with_coastline = gpd.sjoin_nearest(
        ocean_centroids,
        durr_coast_cols,
        how='left',
        max_distance=0.5  # 0.5 degrees ~ 55km
    )
    ocean_with_coastline = ocean_with_coastline.drop_duplicates(subset='HYBAS_ID', keep='first')
    if 'index_right' in ocean_with_coastline.columns:
        ocean_with_coastline = ocean_with_coastline.drop(columns=['index_right'])
    
    # MERGE: Coastline takes priority for ocean basins, then catchment
    type_map = ocean_with_coastline.set_index('HYBAS_ID')['type_coastline'].to_dict()
    tidal_with_catchments['type_coastline'] = tidal_with_catchments['HYBAS_ID'].map(type_map)
    
    # Final classification: STRICT PRIORITY - coastline MUST win for ocean basins!
    # For ocean basins (DIST_SINK=0): coastline ONLY (ignore catchment)
    # For upstream basins: use catchment
    is_ocean = tidal_with_catchments['DIST_SINK'] == 0
    
    tidal_with_catchments['estuary_type'] = 'Unclassified'
    
    # Step 1: Assign coastline types to ocean basins (absolute priority!)
    tidal_with_catchments.loc[is_ocean & (~tidal_with_catchments['type_coastline'].isna()), 'estuary_type'] = \
        tidal_with_catchments.loc[is_ocean & (~tidal_with_catchments['type_coastline'].isna()), 'type_coastline']
    
    # Step 2: For upstream basins WITHOUT coastline, use catchment
    tidal_with_catchments.loc[~is_ocean & (~tidal_with_catchments['type_catchment'].isna()), 'estuary_type'] = \
        tidal_with_catchments.loc[~is_ocean & (~tidal_with_catchments['type_catchment'].isna()), 'type_catchment']
    
    # Step 3: For ocean basins WITHOUT coastline match, use catchment as fallback
    tidal_with_catchments.loc[is_ocean & (tidal_with_catchments['estuary_type']=='Unclassified') & (~tidal_with_catchments['type_catchment'].isna()), 'estuary_type'] = \
        tidal_with_catchments.loc[is_ocean & (tidal_with_catchments['estuary_type']=='Unclassified') & (~tidal_with_catchments['type_catchment'].isna()), 'type_catchment']
    
    tidal_with_catchments['estuary_name'] = tidal_with_catchments['name_catchment'].fillna('Unnamed')
    tidal_with_catchments['is_seed'] = (tidal_with_catchments['DIST_SINK'] == 0)
    
    # Keep tidal_with_catchments for stats before dropping columns
    tidal_clean = tidal_with_catchments.copy()
    
    print(f"\n✅ Classification complete:")
    catchment_count = (~tidal_with_catchments['type_catchment'].isna()).sum() if 'type_catchment' in tidal_with_catchments.columns else 0
    print(f"   Via catchments: {catchment_count:,}")
    print(f"   Via coastline: {len(type_map):,}")
    print(f"   Classified: {len(tidal_clean[tidal_clean['estuary_type']!='Unclassified']):,}")
    print(f"   Unclassified: {len(tidal_clean[tidal_clean['estuary_type']=='Unclassified']):,}")
    
    print(f"\n   By estuary type:")
    for etype, count in tidal_clean['estuary_type'].value_counts().items():
        area = tidal_clean[tidal_clean['estuary_type']==etype]['SUB_AREA'].sum()
        print(f"     {etype}: {count:,} basins ({area:,.0f} km²)")
    
    return tidal_clean, durr_coastline

# ==============================================================================
# HELPER: CLEAN SMALL ISLANDS FROM MULTIPOLYGONS
# ==============================================================================

def clean_small_islands(geometry, min_area_km2=5):
    """Remove small island polygons from MultiPolygon geometries"""
    from shapely.geometry import MultiPolygon, Polygon
    
    if geometry is None or geometry.is_empty:
        return geometry
    
    if geometry.geom_type == 'Polygon':
        # Single polygon - keep as is if large enough
        area_km2 = geometry.area * 111 * 111  # rough degrees to km2
        return geometry if area_km2 >= min_area_km2 else None
    
    elif geometry.geom_type == 'MultiPolygon':
        # Keep only large polygons from MultiPolygon
        large_polygons = []
        total_small_area = 0
        for poly in geometry.geoms:
            area_km2 = poly.area * 111 * 111  # rough degrees to km2
            if area_km2 >= min_area_km2:
                large_polygons.append(poly)
            else:
                total_small_area += area_km2
        
        if len(large_polygons) == 0:
            return None
        elif len(large_polygons) == 1:
            return large_polygons[0]
        else:
            return MultiPolygon(large_polygons)
    
    return geometry

# ==============================================================================
# STEP 5: CREATE OUTPUT FILES
# ==============================================================================

def create_output_files(tidal_basins):
    """Save analysis and web versions"""
    print("\n" + "="*80)
    print("STEP 5: Creating Output Files & Cleaning Geometries")
    print("="*80)
    
    # CRITICAL: Clean small islands from MultiPolygons!
    print(f"\n   Cleaning small island polygons from geometries...")
    print(f"     Before: {len(tidal_basins):,} basins")
    
    # Count MultiPolygons before
    multi_before = len(tidal_basins[tidal_basins.geometry.geom_type == 'MultiPolygon'])
    print(f"     MultiPolygons before: {multi_before:,}")
    
    # Clean geometries
    tidal_basins = tidal_basins.copy()
    tidal_basins['geometry'] = tidal_basins['geometry'].apply(
        lambda g: clean_small_islands(g, min_area_km2=5)
    )
    
    # Remove basins with no geometry left
    tidal_basins = tidal_basins[tidal_basins['geometry'].notna()].copy()
    tidal_basins = tidal_basins[~tidal_basins.geometry.is_empty].copy()
    
    # Count MultiPolygons after
    multi_after = len(tidal_basins[tidal_basins.geometry.geom_type == 'MultiPolygon'])
    print(f"     MultiPolygons after: {multi_after:,}")
    print(f"     Cleaned: {multi_before - multi_after:,} converted to Polygon")
    
    # Also remove tiny basins
    tidal_filtered = tidal_basins[tidal_basins['SUB_AREA'] >= 5].copy()
    removed = len(tidal_basins) - len(tidal_filtered)
    
    print(f"     After all filtering: {len(tidal_filtered):,} basins")
    print(f"     Removed: {removed:,} tiny basins total")
    
    # Keep essential columns
    output_cols = [
        'HYBAS_ID', 'MAIN_BAS', 'SUB_AREA', 'UP_AREA', 'DIST_SINK', 'ORDER_',
        'COAST', 'estuary_name', 'estuary_type', 'estuary_type_detailed', 
        'is_seed', 'geometry'
    ]
    output_cols = [col for col in output_cols if col in tidal_filtered.columns]
    tidal_clean = tidal_filtered[output_cols].copy()
    
    # Rename for clarity
    tidal_clean = tidal_clean.rename(columns={
        'SUB_AREA': 'basin_area_km2',
        'UP_AREA': 'upstream_area_km2',
        'DIST_SINK': 'distance_to_coast_km',
        'ORDER_': 'stream_order',
        'COAST': 'coastal_flag'
    })
    
    # Save full resolution
    print(f"\n💾 Saving full resolution...")
    tidal_clean.to_file(TIDAL_BASINS_FULL, driver='GPKG')
    size_mb = TIDAL_BASINS_FULL.stat().st_size / (1024*1024)
    print(f"✅ Full: {size_mb:.1f} MB")
    
    # Save web version (MINIMAL columns only!)
    print(f"\n💾 Creating web version (minimal)...")
    tidal_web = tidal_clean[['estuary_type', 'basin_area_km2', 'geometry']].copy()
    tidal_web['geometry'] = tidal_web.geometry.simplify(SIMPLIFY_WEB)
    tidal_web.to_file(TIDAL_BASINS_WEB, driver='GeoJSON')
    size_mb = TIDAL_BASINS_WEB.stat().st_size / (1024*1024)
    print(f"✅ Web: {size_mb:.1f} MB (minimal columns)")
    
    return tidal_clean

# ==============================================================================
# STEP 6: CREATE VISUALIZATION
# ==============================================================================

def create_visualization(tidal_basins, grit_rivers=None, durr_coastline=None):
    """Create TWO versions: with/without rivers + Dürr reference layers"""
    print("\n" + "="*80)
    print("STEP 6: Creating Visualizations")
    print("="*80)
    
    # Load Dürr catchments for reference
    durr_catchments = None
    if DURR_CATCHMENT_FILE.exists():
        print(f"\n   Loading Dürr catchments for reference...")
        durr_catchments = gpd.read_file(DURR_CATCHMENT_FILE)
        
        # Map types - CORRECT MAPPING FROM DÜRR DOCUMENTATION!
        type_map = {
            0: 'Endorheic or Glaciated',
            1: 'Small deltas',              # Type I
            2: 'Tidal systems',             # Type II
            3: 'Lagoons',                   # Type III
            4: 'Fjords and fjaerds',        # Type IV
            5: 'Large Rivers',              # Type Va
            51: 'Large Rivers with tidal deltas',  # Type Vb
            6: 'Karst',                     # Type VI
            7: 'Arheic',                    # Type VII
            -9999: 'Unclassified'
        }
        durr_catchments['estuary_type'] = durr_catchments['FIN_TYP'].map(type_map)
        durr_catchments = durr_catchments[
            (durr_catchments['estuary_type'] != 'Unclassified') &
            (durr_catchments['estuary_type'] != 'Endorheic or Glaciated')
        ].copy()
        
        # Calculate area for pie chart - MUST reproject to equal area projection!
        print(f"     Calculating areas in equal-area projection...")
        durr_catchments_aea = durr_catchments.to_crs('ESRI:54009')  # World Mollweide equal area
        durr_catchments['area_km2'] = durr_catchments_aea.geometry.area / 1e6
        
        durr_catchments = durr_catchments[['RECORDNAME', 'estuary_type', 'area_km2', 'geometry']].copy()
        print(f"     Total Dürr area: {durr_catchments['area_km2'].sum():,.0f} km²")
        
        if durr_catchments.crs != tidal_basins.crs:
            durr_catchments = durr_catchments.to_crs(tidal_basins.crs)
        durr_catchments['geometry'] = durr_catchments.geometry.simplify(0.05)
        print(f"     Dürr catchments: {len(durr_catchments):,}")
        print(f"     Types: {durr_catchments['estuary_type'].value_counts().to_dict()}")
    
    # Color scheme - CORRECTED to match Dürr types
    color_map = {
        'Small deltas': '#9D4EDD',                    # Type I - Purple
        'Tidal systems': '#F72585',                   # Type II - Pink
        'Lagoons': '#FFA500',                         # Type III - Orange
        'Fjords and fjaerds': '#3A86FF',             # Type IV - Blue
        'Large Rivers': '#C77DFF',                    # Type Va - Light purple
        'Large Rivers with tidal deltas': '#7209B7', # Type Vb - Dark purple
        'Karst': '#FFD60A',                          # Type VI - Yellow
        'Arheic': '#00BBF9',                         # Type VII - Cyan
        'Endorheic or Glaciated': '#808080',         # Grey
        'Unclassified': '#CCCCCC'                    # Light grey
    }
    
    # Simplify basins for web
    print(f"\n   Simplifying geometries for web...")
    tidal_simple = tidal_basins.copy()
    tidal_simple['geometry'] = tidal_simple.geometry.simplify(0.05)
    
    # Prepare Dürr coastline (already loaded and classified in classify_with_durr)
    if durr_coastline is not None:
        print(f"\n   Preparing Dürr coastline for visualization...")
        
        # CRITICAL: Keep only unique columns to avoid duplicates error
        durr_coastline = durr_coastline[['estuary_type', 'geometry']].copy()
        
        if durr_coastline.crs != tidal_simple.crs:
            durr_coastline = durr_coastline.to_crs(tidal_simple.crs)
        durr_coastline['geometry'] = durr_coastline.geometry.simplify(0.02)
        print(f"     Dürr coastline segments: {len(durr_coastline):,}")
        print(f"     Types: {durr_coastline['estuary_type'].value_counts().to_dict()}")
    
    # =========================================================================
    # CALCULATE STATISTICS FOR PIE CHARTS
    # =========================================================================
    print(f"\n   Calculating statistics for pie charts...")
    
    # Our basins statistics
    our_stats = tidal_simple.groupby('estuary_type')['basin_area_km2'].sum().to_dict()
    our_total = sum(our_stats.values())
    
    # Dürr catchments statistics
    durr_stats = {}
    if durr_catchments is not None:
        durr_stats = durr_catchments.groupby('estuary_type')['area_km2'].sum().to_dict()
    durr_total = sum(durr_stats.values()) if durr_stats else 0
    
    # =========================================================================
    # VERSION 1: WITH PIE CHARTS AND CHECKBOX CONTROL (FOR WEB HOSTING)
    # =========================================================================
    print(f"\n   Creating VERSION 1: With pie charts and layer control...")
    m1 = folium.Map(location=[10, 0], zoom_start=2, tiles='Esri WorldImagery')
    
    # Create feature groups for checkbox control
    durr_catchments_group = folium.FeatureGroup(name='📊 Dürr Catchments (Original 2011)', show=False)
    our_basins_group = folium.FeatureGroup(name='🌊 Our Tidal Basins (High-Resolution)', show=True)
    durr_coastline_group = folium.FeatureGroup(name='📍 Dürr Coastline (Reference)', show=True)
    
    # Layer 1: Dürr catchments (in feature group)
    if durr_catchments is not None:
        for etype in sorted(durr_catchments['estuary_type'].unique()):
            if pd.isna(etype):
                continue
            catchment_type = durr_catchments[durr_catchments['estuary_type'] == etype].copy()
            color = color_map.get(etype, '#808080')
            
            folium.GeoJson(
                catchment_type.__geo_interface__,
                name=f'{etype}',
                style_function=lambda x, c=color: {
                    'fillColor': c,
                    'color': c,
                    'weight': 2,
                    'fillOpacity': 0.25,
                    'opacity': 0.7,
                    'dashArray': '5, 5'
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['RECORDNAME', 'estuary_type', 'area_km2'],
                    aliases=['Name', 'Dürr Type', 'Area (km²)']
                )
            ).add_to(durr_catchments_group)
    
    # Layer 2: Dürr coastline (in feature group)
    if durr_coastline is not None:
        for etype in sorted(durr_coastline['estuary_type'].unique()):
            if pd.isna(etype):
                continue
            coastline_type = durr_coastline[durr_coastline['estuary_type'] == etype].copy()
            color = color_map.get(etype, '#808080')
            
            folium.GeoJson(
                coastline_type.__geo_interface__,
                name=f'{etype}',
                style_function=lambda x, c=color: {
                    'color': c,
                    'weight': 3,
                    'opacity': 0.9
                }
            ).add_to(durr_coastline_group)
    
    # Layer 3: Our tidal basins (in feature group)
    for etype in sorted(tidal_simple['estuary_type'].unique()):
        if pd.isna(etype):
            continue
        
        type_data = tidal_simple[tidal_simple['estuary_type'] == etype]
        color = color_map.get(etype, '#808080')
        
        folium.GeoJson(
            type_data.__geo_interface__,
            name=f'{etype}',
            style_function=lambda x, c=color: {
                'fillColor': c,
                'color': 'none',
                'fillOpacity': 0.4
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['estuary_name', 'estuary_type', 'basin_area_km2'],
                aliases=['Estuary', 'Type', 'Area (km²)']
            )
        ).add_to(our_basins_group)
    
    # Add feature groups to map
    durr_catchments_group.add_to(m1)
    durr_coastline_group.add_to(m1)
    our_basins_group.add_to(m1)
    
    # Add layer control with checkbox
    folium.LayerControl(collapsed=False).add_to(m1)
    plugins.Fullscreen().add_to(m1)
    
    # Prepare data for pie charts
    our_labels = [t for t in sorted(our_stats.keys(), key=lambda x: our_stats[x], reverse=True)]
    our_values = [our_stats[t] for t in our_labels]
    our_colors = [color_map.get(t, '#ccc') for t in our_labels]
    our_percentages = [f"{(v/our_total*100):.1f}%" for v in our_values]
    
    durr_labels = [t for t in sorted(durr_stats.keys(), key=lambda x: durr_stats[x], reverse=True)] if durr_stats else []
    durr_values = [durr_stats[t] for t in durr_labels] if durr_stats else []
    durr_colors = [color_map.get(t, '#ccc') for t in durr_labels] if durr_stats else []
    durr_percentages = [f"{(v/durr_total*100):.1f}%" for v in durr_values] if durr_total > 0 else []
    
    # Add pie charts as HTML overlay - BOTTOM RIGHT with Chart.js
    pie_html = f"""
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <div style="position: fixed; bottom: 10px; right: 10px; display: flex; gap: 15px; z-index: 9999;">
        
        <!-- Our Basins Pie Chart -->
        <div style="background: white; border: 2px solid #333; border-radius: 8px; padding: 15px; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.3); width: 320px;">
            <h4 style="margin: 0 0 5px 0; font-size: 13px; color: #2c3e50; text-align: center;">
                🌊 HydroSheds Basins (Lv 07)
            </h4>
            <div style="font-size: 11px; color: #666; margin-bottom: 10px; text-align: center; font-weight: bold;">
                Total: {our_total:,.0f} km²
            </div>
            <canvas id="ourPieChart" width="200" height="200"></canvas>
        </div>
        
        <!-- Durr Catchments Pie Chart -->
        <div style="background: white; border: 2px solid #333; border-radius: 8px; padding: 15px; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.3); width: 320px;">
            <h4 style="margin: 0 0 5px 0; font-size: 13px; color: #2c3e50; text-align: center;">
                📊 Dürr 2011 Catchments
            </h4>
            <div style="font-size: 11px; color: #666; margin-bottom: 10px; text-align: center; font-weight: bold;">
                Total: {durr_total:,.0f} km²
            </div>
            <canvas id="durrPieChart" width="200" height="200"></canvas>
        </div>
    </div>
    
    <script>
    // Our Basins Pie Chart
    new Chart(document.getElementById('ourPieChart'), {{
        type: 'pie',
        data: {{
            labels: {our_labels},
            datasets: [{{
                data: {our_values},
                backgroundColor: {our_colors},
                borderWidth: 1,
                borderColor: '#fff'
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: true,
            plugins: {{
                legend: {{
                    display: true,
                    position: 'bottom',
                    labels: {{
                        font: {{ size: 9 }},
                        padding: 5,
                        boxWidth: 12,
                        generateLabels: function(chart) {{
                            const data = chart.data;
                            return data.labels.map((label, i) => ({{
                                text: label + ' (' + {our_percentages}[i] + ')',
                                fillStyle: data.datasets[0].backgroundColor[i],
                                hidden: false,
                                index: i
                            }}));
                        }}
                    }}
                }},
                tooltip: {{
                    callbacks: {{
                        label: function(context) {{
                            return context.label + ': ' + context.parsed.toLocaleString() + ' km² (' + {our_percentages}[context.dataIndex] + ')';
                        }}
                    }}
                }}
            }}
        }}
    }});
    
    // Durr Catchments Pie Chart
    new Chart(document.getElementById('durrPieChart'), {{
        type: 'pie',
        data: {{
            labels: {durr_labels if durr_labels else "[]"},
            datasets: [{{
                data: {durr_values if durr_values else "[]"},
                backgroundColor: {durr_colors if durr_colors else "[]"},
                borderWidth: 1,
                borderColor: '#fff'
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: true,
            plugins: {{
                legend: {{
                    display: true,
                    position: 'bottom',
                    labels: {{
                        font: {{ size: 9 }},
                        padding: 5,
                        boxWidth: 12,
                        generateLabels: function(chart) {{
                            const data = chart.data;
                            return data.labels.map((label, i) => ({{
                                text: label + ' (' + {durr_percentages if durr_percentages else "[]"}[i] + ')',
                                fillStyle: data.datasets[0].backgroundColor[i],
                                hidden: false,
                                index: i
                            }}));
                        }}
                    }}
                }},
                tooltip: {{
                    callbacks: {{
                        label: function(context) {{
                            return context.label + ': ' + context.parsed.toLocaleString() + ' km² (' + {durr_percentages if durr_percentages else "[]"}[context.dataIndex] + ')';
                        }}
                    }}
                }}
            }}
        }}
    }});
    </script>
    """
    m1.get_root().html.add_child(folium.Element(pie_html))
    
    m1.save(str(OUTPUT_MAP_NO_RIVERS))
    size_mb = OUTPUT_MAP_NO_RIVERS.stat().st_size / (1024*1024)
    print(f"   ✅ Saved: {OUTPUT_MAP_NO_RIVERS.name} ({size_mb:.1f} MB)")
    
    # =========================================================================
    # VERSION 2: WITH RIVERS (DIAGNOSTIC VERSION)
    # =========================================================================
    print(f"\n   Creating VERSION 2: With large rivers...")
    
    # Load and filter GRIT rivers
    grit_rivers_filtered = None
    if GRIT_SEGMENTS_FILE.exists():
        print(f"   Loading GRIT rivers...")
        grit = gpd.read_file(GRIT_SEGMENTS_FILE, layer='lines')
        
        # Filter to large rivers only (Strahler order >= 6 OR mainstems)
        grit_large = grit[
            (grit['strahler_order'] >= 6) | 
            (grit['is_mainstem'] == 1)
        ].copy()
        
        print(f"   Filtered to {len(grit_large):,} large rivers (order >= 6 or mainstem)")
        
        # Spatial join to keep only rivers within tidal basins
        if grit.crs != tidal_simple.crs:
            grit_large = grit_large.to_crs(tidal_simple.crs)
        
        grit_points = grit_large.copy()
        grit_points['geometry'] = grit_points.geometry.centroid
        
        grit_in_basins = gpd.sjoin(
            grit_points[['global_id', 'strahler_order', 'is_mainstem', 'geometry']],
            tidal_simple[['HYBAS_ID', 'geometry']],
            how='inner',
            predicate='within'
        )
        
        # Get full river segments for matched IDs
        river_ids = grit_in_basins['global_id'].unique()
        grit_rivers_filtered = grit_large[grit_large['global_id'].isin(river_ids)].copy()
        grit_rivers_filtered['geometry'] = grit_rivers_filtered.geometry.simplify(0.01)
        
        print(f"   Rivers within tidal basins: {len(grit_rivers_filtered):,}")
    
    m2 = folium.Map(location=[10, 0], zoom_start=2, tiles='Esri WorldImagery')
    
    # Create feature groups
    durr_catchments_group2 = folium.FeatureGroup(name='📊 Dürr Catchments (Original 2011)', show=False)
    our_basins_group2 = folium.FeatureGroup(name='🌊 Our Tidal Basins (High-Resolution)', show=True)
    durr_coastline_group2 = folium.FeatureGroup(name='📍 Dürr Coastline (Reference)', show=True)
    
    # Add layers to groups
    if durr_catchments is not None:
        for etype in sorted(durr_catchments['estuary_type'].unique()):
            if pd.isna(etype):
                continue
            catchment_type = durr_catchments[durr_catchments['estuary_type'] == etype].copy()
            color = color_map.get(etype, '#808080')
            folium.GeoJson(
                catchment_type.__geo_interface__,
                style_function=lambda x, c=color: {
                    'fillColor': c, 'color': c, 'weight': 2,
                    'fillOpacity': 0.25, 'opacity': 0.7, 'dashArray': '5, 5'
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['RECORDNAME', 'estuary_type', 'area_km2'],
                    aliases=['Name', 'Dürr Type', 'Area (km²)']
                )
            ).add_to(durr_catchments_group2)
    
    if durr_coastline is not None:
        for etype in sorted(durr_coastline['estuary_type'].unique()):
            if pd.isna(etype):
                continue
            coastline_type = durr_coastline[durr_coastline['estuary_type'] == etype].copy()
            color = color_map.get(etype, '#808080')
            folium.GeoJson(
                coastline_type.__geo_interface__,
                style_function=lambda x, c=color: {'color': c, 'weight': 3, 'opacity': 0.9}
            ).add_to(durr_coastline_group2)
    
    for etype in sorted(tidal_simple['estuary_type'].unique()):
        if pd.isna(etype):
            continue
        type_data = tidal_simple[tidal_simple['estuary_type'] == etype]
        color = color_map.get(etype, '#808080')
        folium.GeoJson(
            type_data.__geo_interface__,
            style_function=lambda x, c=color: {'fillColor': c, 'color': 'none', 'fillOpacity': 0.4},
            tooltip=folium.GeoJsonTooltip(
                fields=['estuary_name', 'estuary_type', 'basin_area_km2'],
                aliases=['Estuary', 'Type', 'Area (km²)']
            )
        ).add_to(our_basins_group2)
    
    durr_catchments_group2.add_to(m2)
    durr_coastline_group2.add_to(m2)
    our_basins_group2.add_to(m2)
    
    # Add rivers layer
    if grit_rivers_filtered is not None and len(grit_rivers_filtered) > 0:
        rivers_group = folium.FeatureGroup(name='🌊 Large Rivers (GRIT)', show=True)
        
        folium.GeoJson(
            grit_rivers_filtered.__geo_interface__,
            style_function=lambda x: {
                'color': '#00CED1',  # Dark turquoise
                'weight': 2,
                'opacity': 0.8
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['strahler_order', 'is_mainstem'],
                aliases=['Stream Order', 'Is Mainstem']
            )
        ).add_to(rivers_group)
        
        rivers_group.add_to(m2)
    
    folium.LayerControl(collapsed=False).add_to(m2)
    plugins.Fullscreen().add_to(m2)
    m2.get_root().html.add_child(folium.Element(pie_html))
    
    m2.save(str(OUTPUT_MAP_WITH_RIVERS))
    size_mb2 = OUTPUT_MAP_WITH_RIVERS.stat().st_size / (1024*1024)
    print(f"   ✅ Saved: {OUTPUT_MAP_WITH_RIVERS.name} ({size_mb2:.1f} MB)")
    
    print(f"\n   📊 Summary:")
    print(f"      Web version (no rivers): {size_mb:.1f} MB")
    print(f"      Full version (with rivers): {size_mb2:.1f} MB")

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    """Generate river-based tidal basins (bottom-up approach)"""
    
    print("\n" + "="*80)
    print("River-Based Tidal Basin Network (Bottom-Up Approach)")
    print("="*80)
    print(f"\nNEW Philosophy:")
    print(f"  1. Start with ALL coastal basins (no Dürr filter!)")
    print(f"  2. Find GRIT rivers in coastal basins")
    print(f"  3. Trace upstream via GRIT catchment connectivity")
    print(f"  4. Include all basins with connected rivers")
    print(f"  5. Classify with Dürr AFTER (optional)")
    print(f"  6. Result: River-verified, no inland isolation!")
    
    try:
        # Load BasinATLAS
        print(f"\n📂 Loading BasinATLAS Level 7...")
        start_time = time.time()
        basins = gpd.read_file(BASINATLAS_FILE)
        print(f"   Loaded {len(basins):,} basins in {time.time()-start_time:.1f}s")
        
        # Step 1: Find ALL tidal basins (distance-based)
        tidal_basins = find_all_coastal_basins(basins)
        
        # Step 2: Filter and clean
        tidal_filtered = filter_and_clean(tidal_basins)
        
        # Step 3: Classify with Dürr (catchments + coastline)
        tidal_classified, durr_coastline = classify_with_durr(tidal_filtered, DURR_CATCHMENT_FILE, DURR_COASTLINE_FILE)
        
        # Step 5: Create outputs
        tidal_final = create_output_files(tidal_classified)
        
        # Step 6: Visualization (with Dürr coastline)
        create_visualization(tidal_final, None, durr_coastline)
        
        # Summary
        print("\n" + "="*80)
        print("✅ RIVER-BASED TIDAL BASIN NETWORK COMPLETE!")
        print("="*80)
        
        print(f"\n📊 Final Statistics:")
        print(f"   Total basins: {len(tidal_final):,}")
        print(f"   Total area: {tidal_final['basin_area_km2'].sum():,.0f} km²")
        print(f"   Coastal (seeds): {len(tidal_final[tidal_final['is_seed']==True]):,}")
        print(f"   Upstream: {len(tidal_final[tidal_final['is_seed']==False]):,}")
        
        print(f"\n   Classification:")
        classified = len(tidal_final[tidal_final['estuary_type']!='Unclassified'])
        unclassified = len(tidal_final[tidal_final['estuary_type']=='Unclassified'])
        print(f"     Dürr-classified: {classified:,}")
        print(f"     Unclassified (NEW discoveries!): {unclassified:,}")
        
        print(f"\n📁 Output Files:")
        print(f"   Full: {TIDAL_BASINS_FULL.name}")
        print(f"   Web: {TIDAL_BASINS_WEB.name}")
        print(f"   Map (web): {OUTPUT_MAP_NO_RIVERS.name}")
        print(f"   Map (diagnostic): {OUTPUT_MAP_WITH_RIVERS.name}")
        
        print(f"\n✅ Advantages of River-Based Approach:")
        print(f"   - NO dependency on Dürr spatial extent")
        print(f"   - Based on actual river connectivity (GRIT)")
        print(f"   - More complete global coverage")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
