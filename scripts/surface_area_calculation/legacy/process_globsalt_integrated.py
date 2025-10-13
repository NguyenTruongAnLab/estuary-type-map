"""
⚠️ LEGACY SCRIPT - OBSOLETE FOR CURRENT WORKFLOW
================================================

ORIGINAL PURPOSE: GlobSalt + GRIT + OSM Integration Pipeline

This script was designed to integrate salinity data (GlobSalt v2.0) with GRIT river
network and OSM water polygons to create salinity-classified water body surface areas.

❌ WHY THIS IS OBSOLETE:
-----------------------
1. Uses RAW GlobSalt data (only 0.7-25% coverage!)
2. Does NOT use ML salinity predictions (which provide 100% coverage!)
3. Superseded by new workflow: ml_salinity/ → surface_area_calculation/

✅ CORRECT WORKFLOW (Phase 2):
-------------------------------
1. Use ML-classified segments (100% coverage with salinity predictions)
2. Join to GRIT reaches (inherit classification + get width data)
3. Intersect with OSM water polygons (get actual water bodies)
4. Calculate surface areas by classification

See: scripts/surface_area_calculation/README.md for current approach

ORIGINAL WORKFLOW (OUTDATED):
------------------------------
1. Load GlobSalt data with salinity measurements
2. Load GRIT reaches (all regions) with width data and classifications
3. Spatial join: GRIT reaches → GlobSalt stations
4. Aggregate salinity by reach (mean/median over time)
5. Classify reaches by salinity zone
6. Intersect with OSM water polygons for actual surface areas
7. Calculate surface areas by salinity zone and system type

CRITICAL LIMITATION:
--------------------
GlobSalt provides measurements for only 0.7-25% of global river segments (region-dependent).
This means 75-99.3% of segments would be unclassified!

This is why we developed the ML salinity prediction pipeline (scripts/ml_salinity/)
which fills these gaps using:
- DynQual physics-based features
- Topological features (stream order, distance to coast)
- Spatial context (Dürr catchments)
- Hydrological context (drainage area)

RESULT: 100% coverage instead of 0.7-25%!

SALINITY CLASSIFICATION (O'Connor et al. 2022 + Venice System):
- Non-Tidal Riverine: <0.5 ppt (freshwater upstream)
- Tidal Freshwater Zone (TFZ): 0.5-5.0 ppt (oligohaline)
- Lower Estuary: >5.0 ppt (mesohaline to euhaline)

ACTUAL COLUMNS IN GLOBSALT CSV:
- HYBAS_ID: HydroBASINS level 06 ID
- x, y: Longitude, Latitude
- Station_ID: Unique station identifier
- Conductivity: Electrical conductivity (µS/cm)
- year, month: Temporal info
- Country, Continent: Location info
- Water_type: River, estuary, etc.
- Quality_data_flag: QC flag

ORIGINAL INTEGRATION STRATEGY (OBSOLETE):
- Use GRIT reaches (20.5M globally) as base geometry
- Spatial join with GlobSalt stations (270K stations, 15M records) ← Only 0.7-25%!
- Calculate salinity per reach (temporal average)
- Classify reaches into salinity zones
- Use GRIT width data for estimated areas
- Validate/refine with OSM water polygons

RECOMMENDATION:
---------------
DO NOT USE THIS SCRIPT!
Use: scripts/surface_area_calculation/calculate_surface_areas_master.py (Phase 2)

Author: Global Water Body Surface Area Atlas Project
Date: October 12, 2025 (Marked obsolete: October 13, 2025)
"""

import sys
import warnings
import time
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import geopandas as gpd
import numpy as np
from tqdm import tqdm
from shapely.geometry import Point

warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
GLOBSALT_DIR = BASE_DIR / 'data' / 'raw' / 'GlobSalt'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
OUTPUT_DIR = BASE_DIR / 'data' / 'processed'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Input files
GLOBSALT_FILE = GLOBSALT_DIR / 'GlobSalt_v2.0.csv'
OSM_WATER_FILE = BASE_DIR / 'data' / 'raw' / 'OSM-Water-Layer-Yamazaki_2021' / 'OSM_WaterLayer_POLYGONS.gpkg'

# All GRIT regions
GRIT_REGIONS = ['af', 'as', 'eu', 'na', 'sa', 'si', 'sp']

# Salinity classification (ppt - parts per thousand)
# Based on O'Connor et al. (2022) + Venice System (1958)
SALINITY_ZONES = {
    'Non-Tidal Riverine': (0, 0.5),       # <0.5 ppt: Freshwater upstream
    'Tidal Freshwater Zone': (0.5, 5.0),  # 0.5-5 ppt: TFZ (O'Connor 2022)
    'Lower Estuary': (5.0, 999.0),        # >5 ppt: Saline estuary
}

# Processing config
CHUNK_SIZE = 500000  # Process 500k rows at a time
BUFFER_DISTANCE_KM = 5  # Buffer around stations for spatial join (5km)

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")

def conductivity_to_salinity(conductivity_us_cm, temp_c=25):
    """
    Convert electrical conductivity (µS/cm) to salinity (ppt).
    Uses empirical formula from GlobSalt documentation.
    
    Args:
        conductivity_us_cm: Conductivity in µS/cm
        temp_c: Temperature in Celsius (default 25°C)
    
    Returns:
        Salinity in ppt (parts per thousand)
    """
    if pd.isna(conductivity_us_cm) or conductivity_us_cm <= 0:
        return np.nan
    
    # Convert µS/cm to mS/cm
    conductivity_ms_cm = conductivity_us_cm / 1000
    
    # Empirical formula (Schemel 2001, modified)
    # S (ppt) ≈ 0.0120 - 0.2174 × C + 25.3283 × C² + 13.7714 × C³ - 6.4788 × C⁴ + 2.5842 × C⁵
    # where C = conductivity in mS/cm
    
    # Simplified linear approximation for freshwater-brackish range
    # S ≈ C × 0.47 - 0.13 (valid for 0-50 mS/cm)
    
    if conductivity_ms_cm < 50:
        salinity = conductivity_ms_cm * 0.47 - 0.13
    else:
        # For higher conductivity, use polynomial
        C = conductivity_ms_cm
        salinity = (0.0120 - 0.2174*C + 25.3283*C**2 + 
                    13.7714*C**3 - 6.4788*C**4 + 2.5842*C**5)
    
    return max(0, salinity)  # Salinity can't be negative

def classify_salinity(salinity_ppt):
    """Classify salinity into zones"""
    if pd.isna(salinity_ppt):
        return 'Unknown'
    
    for zone_name, (min_val, max_val) in SALINITY_ZONES.items():
        if min_val <= salinity_ppt < max_val:
            return zone_name
    
    return 'Hypersaline'  # >35 ppt (rare)

# ==============================================================================
# PROCESSING FUNCTIONS
# ==============================================================================

def load_globsalt_stations():
    """Load GlobSalt data and convert to GeoDataFrame of stations"""
    print_section("STEP 1: Loading GlobSalt Salinity Data")
    
    if not GLOBSALT_FILE.exists():
        print(f"❌ GlobSalt file not found: {GLOBSALT_FILE}")
        return None
    
    print(f"📂 Loading: {GLOBSALT_FILE.name} (1.2 GB)")
    print(f"    Reading in chunks of {CHUNK_SIZE:,} rows...")
    print(f"    Note: Using Latin-1 encoding due to special characters in station names")
    
    # Read in chunks and aggregate by station
    station_salinity = {}
    station_coords = {}
    station_info = {}
    
    chunk_count = 0
    total_records = 0
    
    # Use Latin-1 encoding to handle special characters in country/station names
    csv_reader = pd.read_csv(GLOBSALT_FILE, chunksize=CHUNK_SIZE, encoding='latin-1')
    
    for chunk in csv_reader:
        chunk_count += 1
        total_records += len(chunk)
        
        print(f"    Processing chunk {chunk_count} ({total_records:,} records)...", end='\r')
        
        # Calculate salinity from conductivity (vectorized - much faster!)
        chunk['salinity_ppt'] = chunk['Conductivity'].apply(conductivity_to_salinity)
        
        # Filter valid salinity values
        valid_chunk = chunk[chunk['salinity_ppt'].notna()].copy()
        
        # Group by station and aggregate (vectorized approach)
        for station_id in valid_chunk['Station_ID'].unique():
            station_data = valid_chunk[valid_chunk['Station_ID'] == station_id]
            
            if station_id not in station_salinity:
                first_row = station_data.iloc[0]
                station_salinity[station_id] = []
                station_coords[station_id] = (first_row['x'], first_row['y'])
                station_info[station_id] = {
                    'HYBAS_ID': first_row['HYBAS_ID'],
                    'Country': first_row['Country'],
                    'Continent': first_row['Continent'],
                    'Water_type': first_row['Water_type']
                }
            
            station_salinity[station_id].extend(station_data['salinity_ppt'].tolist())
    
    print()  # New line after progress updates
    
    print(f"\n✓ Loaded {total_records:,} records from {len(station_salinity):,} stations")
    
    # Create GeoDataFrame
    print(f"\n📊 Creating station GeoDataFrame...")
    
    records = []
    for station_id, salinity_list in station_salinity.items():
        if len(salinity_list) > 0:
            lon, lat = station_coords[station_id]
            records.append({
                'Station_ID': station_id,
                'longitude': lon,
                'latitude': lat,
                'salinity_mean': np.mean(salinity_list),
                'salinity_median': np.median(salinity_list),
                'salinity_std': np.std(salinity_list),
                'n_measurements': len(salinity_list),
                'HYBAS_ID': station_info[station_id]['HYBAS_ID'],
                'Country': station_info[station_id]['Country'],
                'Continent': station_info[station_id]['Continent'],
                'Water_type': station_info[station_id]['Water_type'],
                'salinity_zone': classify_salinity(np.median(salinity_list))
            })
    
    stations_df = pd.DataFrame(records)
    
    # Convert to GeoDataFrame
    geometry = [Point(row['longitude'], row['latitude']) for _, row in stations_df.iterrows()]
    stations_gdf = gpd.GeoDataFrame(stations_df, geometry=geometry, crs='EPSG:4326')
    
    print(f"✓ Created GeoDataFrame: {len(stations_gdf):,} stations")
    print(f"\n📊 Salinity zone distribution:")
    for zone, count in stations_gdf['salinity_zone'].value_counts().items():
        print(f"    {zone}: {count:,} stations ({count/len(stations_gdf)*100:.1f}%)")
    
    # Save stations
    stations_file = OUTPUT_DIR / 'globsalt_stations.gpkg'
    print(f"\n💾 Saving stations: {stations_file.name}")
    stations_gdf.to_file(stations_file, driver='GPKG')
    print(f"✓ Saved: {stations_file}")
    
    return stations_gdf


def integrate_with_grit_reaches(stations_gdf):
    """Spatially join GlobSalt stations with GRIT reaches"""
    print_section("STEP 2: Integrating with GRIT River Reaches")
    
    print(f"📊 Loading GRIT reaches for all regions...")
    
    all_reaches = []
    
    for region in GRIT_REGIONS:
        reaches_file = PROCESSED_DIR / f'rivers_grit_reaches_classified_{region}.gpkg'
        
        if not reaches_file.exists():
            print(f"  ⚠️  Skipping {region.upper()}: file not found")
            continue
        
        # Check for journal files (indicates locked database)
        journal_file = Path(str(reaches_file) + '-journal')
        if journal_file.exists():
            print(f"  ⚠️  Removing journal file for {region.upper()} (indicates previous lock)")
            journal_file.unlink()
        
        print(f"  📂 Loading {region.upper()}: {reaches_file.name}")
        try:
            reaches = gpd.read_file(reaches_file)
            if len(reaches) == 0:
                print(f"      ⚠️  File is empty, skipping...")
                continue
            reaches['region'] = region.upper()
            all_reaches.append(reaches)
            print(f"      ✓ {len(reaches):,} reaches")
        except Exception as e:
            print(f"      ❌ Error loading {region.upper()}: {e}")
            print(f"      Skipping this region...")
    
    if not all_reaches:
        print(f"\n❌ No GRIT reaches found!")
        return None
    
    # Combine all regions
    print(f"\n🔗 Combining all regions...")
    global_reaches = pd.concat(all_reaches, ignore_index=True)
    global_reaches = gpd.GeoDataFrame(global_reaches, crs='EPSG:4326')
    
    print(f"✓ Combined: {len(global_reaches):,} reaches globally")
    
    # Spatial join
    print(f"\n🗺️  Performing spatial join...")
    print(f"    Strategy: Buffer stations by {BUFFER_DISTANCE_KM} km, intersect with reaches")
    
    # Buffer stations (in meters, using equal-area projection)
    stations_proj = stations_gdf.to_crs('EPSG:6933')  # Equal-area
    buffer_m = BUFFER_DISTANCE_KM * 1000
    stations_buffered = stations_proj.copy()
    stations_buffered['geometry'] = stations_proj.buffer(buffer_m)
    stations_buffered = stations_buffered.to_crs('EPSG:4326')
    
    # Spatial join
    print(f"    Joining {len(global_reaches):,} reaches with {len(stations_buffered):,} buffered stations...")
    
    reaches_with_salinity = gpd.sjoin(
        global_reaches,
        stations_buffered[['Station_ID', 'salinity_median', 'salinity_zone', 'n_measurements', 'geometry']],
        how='left',
        predicate='intersects'
    )
    
    # Aggregate multiple stations per reach (take median)
    print(f"\n📊 Aggregating salinity by reach...")
    
    reaches_salinity = reaches_with_salinity.groupby('global_id').agg({
        'salinity_median': 'median',
        'salinity_zone': lambda x: x.mode()[0] if len(x) > 0 else 'Unknown',
        'n_measurements': 'sum',
        'system_type': 'first',
        'region': 'first',
        'length': 'first',
        'grwl_width_median': 'first',
        'segment_id': 'first',
        'geometry': 'first'
    }).reset_index()
    
    reaches_salinity = gpd.GeoDataFrame(reaches_salinity, crs='EPSG:4326')
    
    # Classify reaches without salinity data using system_type
    no_salinity = reaches_salinity['salinity_median'].isna()
    print(f"\n    Reaches with salinity data: {(~no_salinity).sum():,} ({(~no_salinity).sum()/len(reaches_salinity)*100:.1f}%)")
    print(f"    Reaches without salinity: {no_salinity.sum():,}")
    
    # For reaches without salinity, use system_type as proxy
    print(f"\n    Using system_type as proxy for reaches without salinity...")
    reaches_salinity.loc[no_salinity & (reaches_salinity['system_type'] == 'Estuarine'), 'salinity_zone'] = 'Lower Estuary'
    reaches_salinity.loc[no_salinity & (reaches_salinity['system_type'] == 'Non-Tidal Riverine'), 'salinity_zone'] = 'Non-Tidal Riverine'
    
    # Final classification summary
    print(f"\n📊 Final salinity zone classification:")
    for zone, count in reaches_salinity['salinity_zone'].value_counts().items():
        print(f"    {zone}: {count:,} reaches ({count/len(reaches_salinity)*100:.1f}%)")
    
    # Save
    output_file = OUTPUT_DIR / 'rivers_grit_reaches_with_salinity_GLOBAL.gpkg'
    print(f"\n💾 Saving: {output_file.name}")
    reaches_salinity.to_file(output_file, driver='GPKG')
    print(f"✓ Saved: {output_file}")
    
    return reaches_salinity


def calculate_surface_areas(reaches_salinity):
    """Calculate surface areas using GRIT width data"""
    print_section("STEP 3: Calculating Surface Areas")
    
    print(f"📐 Calculating surface areas from GRIT width data...")
    
    # Filter reaches with width data
    with_width = reaches_salinity[reaches_salinity['grwl_width_median'].notna()].copy()
    print(f"    Reaches with width data: {len(with_width):,} ({len(with_width)/len(reaches_salinity)*100:.1f}%)")
    
    # Calculate area = length × width
    with_width['area_m2'] = with_width['length'] * with_width['grwl_width_median']
    with_width['area_km2'] = with_width['area_m2'] / 1e6
    
    # Summary statistics
    print(f"\n📊 Surface Area Statistics:")
    
    total_area = with_width['area_km2'].sum()
    print(f"\n    Total global river surface area: {total_area:,.0f} km²")
    
    # By salinity zone
    print(f"\n    By salinity zone:")
    for zone in SALINITY_ZONES.keys():
        zone_data = with_width[with_width['salinity_zone'] == zone]
        if len(zone_data) > 0:
            zone_area = zone_data['area_km2'].sum()
            print(f"      {zone:30s}: {zone_area:>10,.0f} km² ({zone_area/total_area*100:>5.1f}%)")
    
    # By region
    print(f"\n    By region:")
    for region in sorted(with_width['region'].unique()):
        region_data = with_width[with_width['region'] == region]
        region_area = region_data['area_km2'].sum()
        print(f"      {region}: {region_area:>10,.0f} km²")
    
    # By system type
    print(f"\n    By system type:")
    for sys_type in sorted(with_width['system_type'].unique()):
        type_data = with_width[with_width['system_type'] == sys_type]
        type_area = type_data['area_km2'].sum()
        print(f"      {sys_type:30s}: {type_area:>10,.0f} km²")
    
    # Cross-tabulation: system type × salinity zone
    print(f"\n    Cross-tabulation (System Type × Salinity Zone):")
    crosstab = pd.crosstab(
        with_width['system_type'],
        with_width['salinity_zone'],
        with_width['area_km2'],
        aggfunc='sum',
        margins=True
    ).fillna(0)
    print(crosstab.to_string())
    
    # Save summary
    summary_file = OUTPUT_DIR / 'surface_areas_by_salinity_zone_GLOBAL.csv'
    print(f"\n💾 Saving summary: {summary_file.name}")
    crosstab.to_csv(summary_file)
    print(f"✓ Saved: {summary_file}")
    
    return with_width


# ==============================================================================
# MAIN PIPELINE
# ==============================================================================

def main():
    """Main processing pipeline"""
    print_section("🌊 GLOBSALT + GRIT + OSM INTEGRATION PIPELINE")
    print(f"Integrating salinity data with precise river network")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    # Step 1: Load GlobSalt stations
    stations_gdf = load_globsalt_stations()
    if stations_gdf is None:
        return 1
    
    # Step 2: Integrate with GRIT reaches
    reaches_salinity = integrate_with_grit_reaches(stations_gdf)
    if reaches_salinity is None:
        return 1
    
    # Step 3: Calculate surface areas
    reaches_with_areas = calculate_surface_areas(reaches_salinity)
    
    # Summary
    elapsed = time.time() - start_time
    
    print_section("✅ PROCESSING COMPLETE")
    print(f"Total time: {elapsed/60:.1f} minutes")
    print(f"\n📁 Output files:")
    print(f"    • globsalt_stations.gpkg - Station locations with salinity")
    print(f"    • rivers_grit_reaches_with_salinity_GLOBAL.gpkg - Classified reaches")
    print(f"    • surface_areas_by_salinity_zone_GLOBAL.csv - Summary statistics")
    
    print(f"\n🎯 Key Results:")
    if reaches_with_areas is not None:
        total_area = reaches_with_areas['area_km2'].sum()
        estuarine = reaches_with_areas[reaches_with_areas['system_type'] == 'Estuarine']['area_km2'].sum()
        tfz = reaches_with_areas[reaches_with_areas['salinity_zone'] == 'Tidal Freshwater Zone']['area_km2'].sum()
        print(f"    • Total river surface area: {total_area:,.0f} km²")
        print(f"    • Estuarine systems: {estuarine:,.0f} km²")
        print(f"    • Tidal Freshwater Zone: {tfz:,.0f} km² (O'Connor et al. 2022)")
    
    print(f"\n✅ Ready for validation and visualization!")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
