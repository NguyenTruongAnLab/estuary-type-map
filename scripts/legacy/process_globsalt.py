
"""
GlobSalt Data Processing Pipeline for Estuary Salinity Mapping
================================================================

Processes global river salinity data (GlobSalt v2.0) and integrates with 
HydroSHEDS river network for interactive estuary visualization.

SCIENTIFIC CLASSIFICATION:
- River (Freshwater): <0.5 ppt salinity
- Head of Tide (Oligohaline): 0.5-5.0 ppt
- Upper Estuary (Mesohaline): 5.0-18.0 ppt
- Middle Estuary (Polyhaline): 18.0-25.0 ppt
- Lower Estuary/Mouth (Marine): 25.0-35.0 ppt

PROCESSING STEPS:
1. Read GlobSalt CSV in chunks (memory-efficient)
2. Convert electrical conductivity (EC) to salinity (ppt)
3. Aggregate by HydroBASINS ID (HYBAS_ID) - spatial aggregation
4. Calculate mean/median salinity per basin
5. Classify into salinity zones
6. Join with HydroSHEDS river network geometry
7. Export to web-compatible GeoJSON (<5MB)

Data Sources:
- GlobSalt v2.0: 15M records, 270k stations, 1980-2023
- HydroSHEDS RiverATLAS v1.0: 8.5M river reaches
- HydroATLAS BasinATLAS: Watershed polygons

References:
- Moyano Salcedo et al. (2025): GlobSalt database
- Venice System (1958): Salinity classification
- Bulger et al. (1993): Estuarine classification

Author: Global Estuary Type Map Project
Date: October 10, 2025
License: MIT
"""
import pandas as pd
import geopandas as gpd
import numpy as np
from pathlib import Path
import json
import time
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
GLOBSALT_DIR = BASE_DIR / 'data' / 'raw' / 'GlobSalt'
HYDROSHEDS_DIR = BASE_DIR / 'data' / 'hydrosheds' / 'processed'
OUTPUT_DIR = BASE_DIR / 'data' / 'processed'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Input files
GLOBSALT_FILE = GLOBSALT_DIR / 'GlobSalt_v2.0.csv'
RIVERS_FILE = HYDROSHEDS_DIR / 'rivers_estuaries_global.gpkg'  # From compress_hydrosheds.py
BASINS_FILE = HYDROSHEDS_DIR / 'basins_coastal_lev06.gpkg'

# Salinity classification thresholds (ppt - parts per thousand)
# Based on Venice System (1958) modified for estuaries
SALINITY_CLASSES = {
    'freshwater': (0, 0.5),           # <0.5 ppt: Freshwater rivers
    'oligohaline': (0.5, 5.0),        # 0.5-5 ppt: Head of tide
    'mesohaline': (5.0, 18.0),        # 5-18 ppt: Upper estuary
    'polyhaline': (18.0, 25.0),       # 18-25 ppt: Middle estuary
    'euhaline': (25.0, 35.0),         # 25-35 ppt: Lower estuary/marine
    'hyperhaline': (35.0, 999.0),     # >35 ppt: Hypersaline (rare in estuaries)
}

# Processing configuration
CHUNK_SIZE = 100000  # Process 100k rows at a time (memory-efficient)
MIN_RECORDS_PER_BASIN = 5  # Minimum observations for reliable estimate

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def ec_to_salinity(ec_us_cm, temp_c=25):
    """
    Convert electrical conductivity (EC) to salinity (ppt).
    
    Uses empirical relationship from UNESCO (1981) and Schemel (2001)
    for estuarine waters.
    
    Args:
        ec_us_cm: Electrical conductivity in μS/cm
        temp_c: Water temperature in °C (default 25°C)
        
    Returns:
        Salinity in parts per thousand (ppt)
        
    Reference:
    - Schemel, L.E. (2001). Simplified conversions between specific conductance 
      and salinity units for use with data from monitoring stations.
    - UNESCO (1981). The practical salinity scale 1978
    """
    if pd.isna(ec_us_cm) or ec_us_cm < 0:
        return np.nan
    
    # Convert μS/cm to mS/cm
    ec_ms_cm = ec_us_cm / 1000.0
    
    # Empirical relationship for estuarine waters (Schemel 2001)
    # salinity (ppt) ≈ EC (mS/cm) * 0.64
    # More accurate for EC < 5000 μS/cm (salinity < 3.2 ppt)
    
    if ec_us_cm < 5000:
        # Low salinity: Linear relationship
        salinity = ec_ms_cm * 0.64
    else:
        # Higher salinity: Polynomial relationship (UNESCO 1981)
        # Simplified for computational efficiency
        salinity = 0.0080 - 0.1692 * np.sqrt(ec_ms_cm) + 25.3851 * ec_ms_cm + 14.0941 * (ec_ms_cm ** 1.5) - 7.0261 * (ec_ms_cm ** 2) + 2.7081 * (ec_ms_cm ** 2.5)
        
        # Clamp to realistic range
        salinity = max(0, min(salinity, 50))
    
    return salinity


def classify_salinity(salinity_ppt):
    """
    Classify salinity into ecological zones.
    
    Args:
        salinity_ppt: Salinity in parts per thousand
        
    Returns:
        Classification string
    """
    if pd.isna(salinity_ppt):
        return 'unknown'
    
    for zone_name, (min_sal, max_sal) in SALINITY_CLASSES.items():
        if min_sal <= salinity_ppt < max_sal:
            return zone_name
    
    return 'hyperhaline'


def get_zone_color(zone):
    """Get color code for salinity zone (for visualization)"""
    colors = {
        'freshwater': '#2166ac',    # Dark blue
        'oligohaline': '#67a9cf',   # Light blue
        'mesohaline': '#d1e5f0',    # Very light blue
        'polyhaline': '#fddbc7',    # Light orange
        'euhaline': '#ef8a62',      # Orange
        'hyperhaline': '#b2182b',   # Red
        'unknown': '#999999'        # Gray
    }
    return colors.get(zone, '#999999')


# ==============================================================================
# MAIN PROCESSING FUNCTIONS
# ==============================================================================

def process_globsalt_data():
    """
    Process GlobSalt CSV in chunks and aggregate by basin.
    
    Returns:
        DataFrame with basin-level salinity statistics
    """
    print("\n" + "="*80)
    print("GLOBSALT DATA PROCESSING")
    print("="*80)
    
    if not GLOBSALT_FILE.exists():
        print(f"\n❌ GlobSalt file not found: {GLOBSALT_FILE}")
        print("   Please download from: https://zenodo.org/record/8200199")
        return None
    
    file_size_mb = GLOBSALT_FILE.stat().st_size / (1024**2)
    print(f"\n📊 Input: {GLOBSALT_FILE.name}")
    print(f"   Size: {file_size_mb:,.1f} MB")
    
    # Skip exact row counting (too slow with encoding issues)
    # Estimate based on file size
    print(f"\n⚙️  Estimating from file size (~80 bytes/row average)...")
    estimated_rows = int((file_size_mb * 1024 * 1024) / 80)
    print(f"   Estimated records: ~{estimated_rows:,}")
    
    # Auto-detect encoding by trying to read first chunk
    print(f"\n🔍 Detecting file encoding...")
    encoding = 'latin-1'  # Most permissive, works for most CSV files
    try:
        test_chunk = pd.read_csv(GLOBSALT_FILE, nrows=100, encoding='utf-8')
        encoding = 'utf-8'
        print(f"   Detected encoding: UTF-8")
    except UnicodeDecodeError:
        print(f"   Detected encoding: Latin-1 (fallback)")
    
    # Process in chunks
    print(f"\n⚙️  Processing in chunks of {CHUNK_SIZE:,} rows...")
    
    basin_data = {}
    chunk_count = 0
    processed_rows = 0
    
    start_time = time.time()
    
    # Use detected encoding for reading CSV
    for chunk in tqdm(pd.read_csv(GLOBSALT_FILE, chunksize=CHUNK_SIZE, encoding=encoding, 
                                  encoding_errors='ignore'),  # Skip problematic characters
                      desc="Processing chunks"):
        
        chunk_count += 1
        processed_rows += len(chunk)
        
        # Filter: Only keep conductivity data (required for salinity calculation)
        chunk = chunk[chunk['Conductivity'].notna()].copy()
        
        if len(chunk) == 0:
            continue
        
        # Convert conductivity to salinity
        chunk['salinity_ppt'] = chunk['Conductivity'].apply(ec_to_salinity)
        
        # Classify salinity zones
        chunk['salinity_zone'] = chunk['salinity_ppt'].apply(classify_salinity)
        
        # Aggregate by HYBAS_ID
        for hybas_id, group in chunk.groupby('HYBAS_ID'):
            if hybas_id not in basin_data:
                basin_data[hybas_id] = {
                    'salinity_values': [],
                    'conductivity_values': [],
                    'lon': group['x'].mean(),
                    'lat': group['y'].mean(),
                    'n_records': 0
                }
            
            basin_data[hybas_id]['salinity_values'].extend(group['salinity_ppt'].dropna().tolist())
            basin_data[hybas_id]['conductivity_values'].extend(group['Conductivity'].dropna().tolist())
            basin_data[hybas_id]['n_records'] += len(group)
    
    elapsed = time.time() - start_time
    
    print(f"\n✓ Processed {processed_rows:,} rows in {elapsed:.1f}s")
    print(f"   Unique basins: {len(basin_data):,}")
    
    # Aggregate statistics per basin
    print(f"\n📊 Calculating basin-level statistics...")
    
    results = []
    for hybas_id, data in tqdm(basin_data.items(), desc="Aggregating"):
        if len(data['salinity_values']) < MIN_RECORDS_PER_BASIN:
            continue  # Skip basins with insufficient data
        
        sal_values = np.array(data['salinity_values'])
        
        result = {
            'HYBAS_ID': hybas_id,
            'lon': data['lon'],
            'lat': data['lat'],
            'n_records': data['n_records'],
            'salinity_mean': np.mean(sal_values),
            'salinity_median': np.median(sal_values),
            'salinity_std': np.std(sal_values),
            'salinity_min': np.min(sal_values),
            'salinity_max': np.max(sal_values),
            'conductivity_mean': np.mean(data['conductivity_values']),
        }
        
        # Classify based on median salinity (most robust)
        result['salinity_zone'] = classify_salinity(result['salinity_median'])
        result['zone_color'] = get_zone_color(result['salinity_zone'])
        
        results.append(result)
    
    df_result = pd.DataFrame(results)
    
    print(f"\n✓ Aggregated to {len(df_result):,} basins with sufficient data")
    print(f"\n📈 Salinity Zone Distribution:")
    zone_counts = df_result['salinity_zone'].value_counts()
    for zone, count in zone_counts.items():
        pct = (count / len(df_result)) * 100
        print(f"   {zone:15s}: {count:6,} basins ({pct:5.1f}%)")
    
    return df_result


def join_with_hydrosheds(df_salinity):
    """
    Join salinity data with HydroSHEDS river geometries.
    
    Args:
        df_salinity: DataFrame with basin-level salinity data
        
    Returns:
        GeoDataFrame with river geometries and salinity attributes
    """
    print(f"\n" + "="*80)
    print("JOINING WITH HYDROSHEDS RIVER NETWORK")
    print("="*80)
    
    # Try basins first (polygons)
    if BASINS_FILE.exists():
        print(f"\n📂 Loading HydroSHEDS basins: {BASINS_FILE.name}")
        gdf_basins = gpd.read_file(BASINS_FILE)
        print(f"   Basins loaded: {len(gdf_basins):,}")
        
        # Join salinity data
        print(f"\n🔗 Joining salinity data with basins...")
        gdf_result = gdf_basins.merge(df_salinity, on='HYBAS_ID', how='inner')
        
        print(f"   Matched: {len(gdf_result):,} basins with salinity data")
        
        return gdf_result
    
    else:
        print(f"\n⚠️  Basin file not found: {BASINS_FILE}")
        print(f"   Creating point geometries from coordinates...")
        
        # Create point geometries from lon/lat
        gdf_result = gpd.GeoDataFrame(
            df_salinity,
            geometry=gpd.points_from_xy(df_salinity['lon'], df_salinity['lat']),
            crs='EPSG:4326'
        )
        
        return gdf_result


def export_for_web(gdf, output_name='salinity_zones'):
    """
    Export to web-compatible format.
    
    Args:
        gdf: GeoDataFrame with salinity data
        output_name: Base filename for output
    """
    print(f"\n" + "="*80)
    print("EXPORTING WEB-COMPATIBLE FILES")
    print("="*80)
    
    # Optimize columns for web
    columns_to_keep = [
        'HYBAS_ID', 'salinity_mean', 'salinity_median', 'salinity_zone',
        'zone_color', 'n_records', 'geometry'
    ]
    
    gdf_web = gdf[columns_to_keep].copy()
    
    # Round numerical values
    gdf_web['salinity_mean'] = gdf_web['salinity_mean'].round(2)
    gdf_web['salinity_median'] = gdf_web['salinity_median'].round(2)
    
    # Export GeoJSON
    geojson_file = OUTPUT_DIR / f'{output_name}.geojson'
    print(f"\n💾 Exporting GeoJSON: {geojson_file.name}")
    gdf_web.to_file(geojson_file, driver='GeoJSON')
    
    file_size_mb = geojson_file.stat().st_size / (1024**2)
    print(f"   Size: {file_size_mb:.1f} MB")
    
    if file_size_mb > 5:
        print(f"   ⚠️  File exceeds 5MB - consider splitting by region")
    
    # Export GeoPackage (more efficient)
    gpkg_file = OUTPUT_DIR / f'{output_name}.gpkg'
    print(f"\n💾 Exporting GeoPackage: {gpkg_file.name}")
    gdf_web.to_file(gpkg_file, driver='GPKG')
    
    file_size_mb = gpkg_file.stat().st_size / (1024**2)
    print(f"   Size: {file_size_mb:.1f} MB")
    
    # Export metadata
    metadata = {
        'data_source': 'GlobSalt v2.0',
        'data_source_doi': '10.5281/zenodo.8200199',
        'processed_date': time.strftime('%Y-%m-%d'),
        'n_features': len(gdf_web),
        'salinity_zones': SALINITY_CLASSES,
        'classification': 'Venice System (1958) modified for estuaries',
        'attributes': {
            'HYBAS_ID': 'HydroATLAS basin identifier',
            'salinity_mean': 'Mean salinity (ppt)',
            'salinity_median': 'Median salinity (ppt)',
            'salinity_zone': 'Classified salinity zone',
            'zone_color': 'Hex color for visualization',
            'n_records': 'Number of observations'
        }
    }
    
    metadata_file = OUTPUT_DIR / f'{output_name}_metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✓ Metadata: {metadata_file.name}")
    
    return geojson_file, gpkg_file


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    """Main processing pipeline"""
    
    print("\n" + "="*80)
    print("GLOBSALT ESTUARY SALINITY PROCESSING PIPELINE")
    print("="*80)
    print(f"\n📚 Data Sources:")
    print(f"   - GlobSalt v2.0: Global river salinity (15M records)")
    print(f"   - HydroSHEDS: Global river network (8.5M reaches)")
    print(f"\n🎯 Objective:")
    print(f"   Process and classify river salinity for estuary mapping")
    
    # Step 1: Process GlobSalt data
    df_salinity = process_globsalt_data()
    
    if df_salinity is None or len(df_salinity) == 0:
        print("\n❌ No salinity data processed. Exiting.")
        return
    
    # Step 2: Join with HydroSHEDS geometry
    gdf_salinity = join_with_hydrosheds(df_salinity)
    
    # Step 3: Export for web
    geojson_file, gpkg_file = export_for_web(gdf_salinity)
    
    print("\n" + "="*80)
    print("✅ PROCESSING COMPLETE")
    print("="*80)
    print(f"\n📊 Summary:")
    print(f"   Processed basins: {len(gdf_salinity):,}")
    print(f"   Output files:")
    print(f"   - GeoJSON: {geojson_file}")
    print(f"   - GeoPackage: {gpkg_file}")
    print(f"\n🎯 Next Steps:")
    print(f"   1. Integrate with map.js for interactive visualization")
    print(f"   2. Add salinity zone layer toggle")
    print(f"   3. Create popup info with salinity statistics")
    print(f"   4. Test in browser: http://localhost:8000")
    print("\n" + "="*80)


if __name__ == '__main__':
    main()
