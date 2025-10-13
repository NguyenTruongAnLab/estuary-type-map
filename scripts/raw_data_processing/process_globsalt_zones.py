
"""
GlobSalt Salinity Zones Generator
==================================

Creates spatial salinity zones from GlobSalt v2.0 station data for use in 
GRIT river classification. This is the FIRST STEP in the processing pipeline.

WORKFLOW:
1. Load GlobSalt v2.0 CSV (270K stations, 15M measurements)
2. Calculate salinity from conductivity
3. Aggregate by station (temporal average)
4. Create spatial zones using Voronoi tessellation or grid
5. Save as globsalt_salinity_zones.gpkg for use by process_grit_all_regions.py

SALINITY CLASSIFICATION (Venice System 1958 + O'Connor 2022):
- <0.5 PSU: Freshwater
- 0.5-5.0 PSU: Oligohaline (Tidal Freshwater Zone)
- 5.0-18.0 PSU: Mesohaline (Upper Estuary)
- 18.0-30.0 PSU: Polyhaline (Lower Estuary)
- >30.0 PSU: Euhaline (Marine)

OUTPUT:
- globsalt_salinity_zones.gpkg: Polygon layer with salinity_mean_psu attribute
- globsalt_stations.gpkg: Point layer of all stations

Author: Global Water Body Surface Area Atlas Project
Date: October 12, 2025
"""

import sys
import warnings
import time
from pathlib import Path
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, Polygon
from scipy.spatial import Voronoi
from tqdm import tqdm

warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
GLOBSALT_DIR = BASE_DIR / 'data' / 'raw' / 'GlobSalt'
OUTPUT_DIR = BASE_DIR / 'data' / 'processed'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Input files
GLOBSALT_FILE = GLOBSALT_DIR / 'GlobSalt_v2.0.csv'

# Processing config
CHUNK_SIZE = 500000  # Process 500k rows at a time

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")

def conductivity_to_salinity(conductivity_us_cm):
    """
    Convert electrical conductivity (µS/cm) to salinity (ppt/PSU).
    Uses simplified empirical formula for freshwater-brackish range.
    
    Args:
        conductivity_us_cm: Conductivity in µS/cm
    
    Returns:
        Salinity in ppt (parts per thousand = PSU)
    """
    if pd.isna(conductivity_us_cm) or conductivity_us_cm <= 0:
        return np.nan
    
    # Convert µS/cm to mS/cm
    conductivity_ms_cm = conductivity_us_cm / 1000
    
    # Simplified linear approximation for freshwater-brackish range (0-50 mS/cm)
    # S (PSU) ≈ C × 0.47 - 0.13
    if conductivity_ms_cm < 50:
        salinity = conductivity_ms_cm * 0.47 - 0.13
    else:
        # For seawater range (>50 mS/cm), use polynomial
        C = conductivity_ms_cm
        salinity = (0.0120 - 0.2174*C + 25.3283*C**2 + 
                    13.7714*C**3 - 6.4788*C**4 + 2.5842*C**5)
    
    return max(0, salinity)  # Salinity can't be negative

def classify_salinity_zone(salinity_psu):
    """Classify salinity into biogeochemical zones (Venice System + O'Connor 2022)"""
    if pd.isna(salinity_psu):
        return 'Unknown'
    elif salinity_psu < 0.5:
        return 'Freshwater'
    elif salinity_psu < 5.0:
        return 'Oligohaline (TFZ)'  # Tidal Freshwater Zone
    elif salinity_psu < 18.0:
        return 'Mesohaline'
    elif salinity_psu < 30.0:
        return 'Polyhaline'
    else:
        return 'Euhaline'

# ==============================================================================
# PROCESSING FUNCTIONS
# ==============================================================================

def load_globsalt_stations():
    """Load GlobSalt data and create station GeoDataFrame"""
    print_section("STEP 1: Loading GlobSalt Salinity Data")
    
    if not GLOBSALT_FILE.exists():
        print(f"❌ GlobSalt file not found: {GLOBSALT_FILE}")
        print(f"   Expected location: {GLOBSALT_DIR}")
        print(f"   Please download GlobSalt v2.0 from Linked Earth Data Portal")
        return None
    
    print(f"📂 Loading: {GLOBSALT_FILE.name} (1.2 GB)")
    print(f"   Reading in chunks of {CHUNK_SIZE:,} rows...")
    
    # Dictionary to store aggregated data by station
    station_data = {}
    
    chunk_count = 0
    total_records = 0
    
    try:
        # Read CSV in chunks (handles large file efficiently)
        csv_reader = pd.read_csv(GLOBSALT_FILE, chunksize=CHUNK_SIZE, encoding='latin-1')
        
        for chunk in csv_reader:
            chunk_count += 1
            total_records += len(chunk)
            
            print(f"   Processing chunk {chunk_count} ({total_records:,} records)...", end='\r')
            
            # Calculate salinity from conductivity (vectorized operation)
            chunk['salinity_psu'] = chunk['Conductivity'].apply(conductivity_to_salinity)
            
            # Filter valid salinity values
            valid = chunk[chunk['salinity_psu'].notna()]
            
            # Group by station
            for station_id in valid['Station_ID'].unique():
                station_rows = valid[valid['Station_ID'] == station_id]
                
                if station_id not in station_data:
                    first_row = station_rows.iloc[0]
                    station_data[station_id] = {
                        'longitude': first_row['x'],
                        'latitude': first_row['y'],
                        'salinity_values': [],
                        'HYBAS_ID': first_row['HYBAS_ID'],
                        'Country': first_row['Country'],
                        'Continent': first_row['Continent'],
                        'Water_type': first_row['Water_type']
                    }
                
                station_data[station_id]['salinity_values'].extend(
                    station_rows['salinity_psu'].tolist()
                )
        
        print()  # New line after progress
        
    except Exception as e:
        print(f"\n❌ Error reading GlobSalt file: {e}")
        return None
    
    print(f"✓ Loaded {total_records:,} records from {len(station_data):,} stations")
    
    # Create station summary DataFrame
    print(f"\n📊 Aggregating salinity by station...")
    
    records = []
    for station_id, data in station_data.items():
        salinity_values = data['salinity_values']
        if len(salinity_values) > 0:
            records.append({
                'Station_ID': station_id,
                'longitude': data['longitude'],
                'latitude': data['latitude'],
                'salinity_mean_psu': np.mean(salinity_values),
                'salinity_median_psu': np.median(salinity_values),
                'salinity_std_psu': np.std(salinity_values),
                'n_measurements': len(salinity_values),
                'HYBAS_ID': data['HYBAS_ID'],
                'Country': data['Country'],
                'Continent': data['Continent'],
                'Water_type': data['Water_type']
            })
    
    stations_df = pd.DataFrame(records)
    
    # Classify into salinity zones
    stations_df['salinity_zone'] = stations_df['salinity_mean_psu'].apply(classify_salinity_zone)
    
    # Convert to GeoDataFrame
    geometry = [Point(row['longitude'], row['latitude']) for _, row in stations_df.iterrows()]
    stations_gdf = gpd.GeoDataFrame(stations_df, geometry=geometry, crs='EPSG:4326')
    
    print(f"✓ Created {len(stations_gdf):,} stations")
    print(f"\n📊 Salinity zone distribution:")
    for zone, count in stations_gdf['salinity_zone'].value_counts().items():
        pct = count / len(stations_gdf) * 100
        print(f"   {zone:25s}: {count:>6,} stations ({pct:>5.1f}%)")
    
    # Save stations
    stations_file = OUTPUT_DIR / 'globsalt_stations.gpkg'
    print(f"\n💾 Saving stations: {stations_file.name}")
    stations_gdf.to_file(stations_file, driver='GPKG')
    print(f"✓ Saved: {stations_file}")
    
    return stations_gdf


def create_salinity_zones(stations_gdf):
    """
    Create spatial salinity zones from station points.
    Uses buffered points (simpler than Voronoi for global dataset).
    """
    print_section("STEP 2: Creating Salinity Zones")
    
    print(f"🗺️  Creating spatial zones from {len(stations_gdf):,} stations...")
    print(f"   Method: Buffer stations by 10 km (representative zone)")
    
    # Project to equal-area CRS for buffering
    print(f"   Projecting to equal-area CRS (EPSG:6933)...")
    stations_proj = stations_gdf.to_crs('EPSG:6933')
    
    # Buffer by 10 km
    buffer_m = 10000  # 10 km
    print(f"   Buffering stations by {buffer_m/1000:.0f} km...")
    stations_buffered = stations_proj.copy()
    stations_buffered['geometry'] = stations_proj.buffer(buffer_m)
    
    # Convert back to WGS84
    print(f"   Reprojecting to WGS84...")
    salinity_zones = stations_buffered.to_crs('EPSG:4326')
    
    # Keep only necessary columns
    salinity_zones = salinity_zones[[
        'Station_ID',
        'salinity_mean_psu',
        'salinity_median_psu',
        'salinity_zone',
        'n_measurements',
        'Country',
        'Continent',
        'geometry'
    ]]
    
    print(f"✓ Created {len(salinity_zones):,} salinity zones")
    
    # Statistics
    print(f"\n📊 Zone Statistics:")
    print(f"   Mean salinity: {salinity_zones['salinity_mean_psu'].mean():.2f} PSU")
    print(f"   Median salinity: {salinity_zones['salinity_median_psu'].median():.2f} PSU")
    print(f"   Max salinity: {salinity_zones['salinity_mean_psu'].max():.2f} PSU")
    
    print(f"\n   Zones by classification:")
    for zone, count in salinity_zones['salinity_zone'].value_counts().items():
        pct = count / len(salinity_zones) * 100
        print(f"      {zone:25s}: {count:>6,} zones ({pct:>5.1f}%)")
    
    # Save zones
    zones_file = OUTPUT_DIR / 'globsalt_salinity_zones.gpkg'
    print(f"\n💾 Saving salinity zones: {zones_file.name}")
    salinity_zones.to_file(zones_file, driver='GPKG')
    print(f"✓ Saved: {zones_file}")
    
    print(f"\n🎯 This file is now ready for use by process_grit_all_regions.py!")
    
    return salinity_zones


# ==============================================================================
# MAIN PIPELINE
# ==============================================================================

def main():
    """Main processing pipeline"""
    print_section("🌊 GLOBSALT SALINITY ZONES GENERATOR")
    print(f"Creates spatial salinity zones for GRIT river classification")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    # Step 1: Load stations
    stations_gdf = load_globsalt_stations()
    if stations_gdf is None:
        print(f"\n❌ Failed to load GlobSalt data")
        return 1
    
    # Step 2: Create zones
    salinity_zones = create_salinity_zones(stations_gdf)
    
    # Summary
    elapsed = time.time() - start_time
    
    print_section("✅ PROCESSING COMPLETE")
    print(f"Total time: {elapsed/60:.1f} minutes")
    
    print(f"\n📁 Output files created:")
    print(f"   ✓ globsalt_stations.gpkg - {len(stations_gdf):,} point stations")
    print(f"   ✓ globsalt_salinity_zones.gpkg - {len(salinity_zones):,} buffered zones")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. ✅ Salinity zones ready!")
    print(f"   2. Run: python scripts/process_grit_all_regions.py")
    print(f"   3. GRIT script will use globsalt_salinity_zones.gpkg for classification")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
