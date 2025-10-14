#!/usr/bin/env python3
"""
Create GCC (Global Coastal Characteristics) Points for Web Visualization
=========================================================================

PURPOSE: Generate web-optimized GeoJSON from GCC dataset (Athanasiou et al. 2024)

INPUT:
- data/raw/GCC-Panagiotis-Athanasiou_2024/GCC_geophysical.csv
- data/raw/GCC-Panagiotis-Athanasiou_2024/GCC_hydrometeorological.csv
- data/raw/GCC-Panagiotis-Athanasiou_2024/GCC_socioeconomic.csv

OUTPUT:
- data/web/gcc_coastal_characteristics.geojson (<5MB)

FEATURES:
- Coastal segment characteristics (100km resolution)
- Wave height, tidal range, sediment supply
- Population density, coastal erosion risk

Author: Global Water Body Surface Area Atlas Project
Date: October 13, 2025
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
import json
from shapely.geometry import Point
import warnings
warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
RAW_DIR = DATA_DIR / 'raw' / 'GCC-Panagiotis-Athanasiou_2024'
WEB_DIR = DATA_DIR / 'web'

# Input files
GEOPHYSICAL_FILE = RAW_DIR / 'GCC_geophysical.csv'
HYDROMETEO_FILE = RAW_DIR / 'GCC_hydrometeorological.csv'
SOCIOECONOMIC_FILE = RAW_DIR / 'GCC_socioeconomic.csv'

# Output file
OUTPUT_FILE = WEB_DIR / 'gcc_coastal_characteristics.geojson'

# Maximum file size target
MAX_SIZE_MB = 5.0

# ==============================================================================
# MAIN PROCESSING
# ==============================================================================

def main():
    """Create web-optimized GCC coastal characteristics points"""
    
    print("\n" + "="*80)
    print("CREATE GCC COASTAL CHARACTERISTICS FOR WEB")
    print("="*80)
    
    # Step 1: Load GCC datasets
    print("\n📂 STEP 1: Loading GCC datasets...")
    
    if not GEOPHYSICAL_FILE.exists():
        print(f"   ❌ ERROR: {GEOPHYSICAL_FILE} not found!")
        return
    
    df_geo = pd.read_csv(GEOPHYSICAL_FILE)
    print(f"   ✓ Loaded geophysical: {len(df_geo):,} segments")
    print(f"     Columns: {list(df_geo.columns[:10])}...")
    
    df_hydro = None
    if HYDROMETEO_FILE.exists():
        df_hydro = pd.read_csv(HYDROMETEO_FILE)
        print(f"   ✓ Loaded hydrometeorological: {len(df_hydro):,} segments")
    
    df_socio = None
    if SOCIOECONOMIC_FILE.exists():
        df_socio = pd.read_csv(SOCIOECONOMIC_FILE)
        print(f"   ✓ Loaded socioeconomic: {len(df_socio):,} segments")
    
    # Step 2: Merge datasets
    print("\n🔗 STEP 2: Merging datasets...")
    
    # Identify ID column (usually 'id', 'ID', 'segment_id', or similar)
    id_col = None
    for col in ['id', 'ID', 'segment_id', 'SEGMENT_ID', 'tr_id', 'TR_ID']:
        if col in df_geo.columns:
            id_col = col
            break
    
    if id_col is None:
        print("   ⚠️  No ID column found, using index")
        id_col = 'index'
        df_geo[id_col] = df_geo.index
    
    print(f"   Using ID column: '{id_col}'")
    
    # Merge datasets
    df = df_geo.copy()
    if df_hydro is not None and id_col in df_hydro.columns:
        df = df.merge(df_hydro, on=id_col, how='left', suffixes=('', '_hydro'))
    if df_socio is not None and id_col in df_socio.columns:
        df = df.merge(df_socio, on=id_col, how='left', suffixes=('', '_socio'))
    
    print(f"   ✓ Merged dataset: {len(df):,} segments with {len(df.columns)} columns")
    
    # Step 3: Identify coordinate columns
    print("\n🗺️ STEP 3: Extracting coordinates...")
    
    # Try common coordinate column names
    lon_col = None
    lat_col = None
    
    for lon_name in ['lon', 'longitude', 'Longitude', 'LON', 'x', 'X']:
        if lon_name in df.columns:
            lon_col = lon_name
            break
    
    for lat_name in ['lat', 'latitude', 'Latitude', 'LAT', 'y', 'Y']:
        if lat_name in df.columns:
            lat_col = lat_name
            break
    
    if lon_col is None or lat_col is None:
        print(f"   ❌ ERROR: Cannot find coordinate columns!")
        print(f"   Available columns: {list(df.columns[:20])}...")
        return
    
    print(f"   ✓ Using coordinates: {lon_col}, {lat_col}")
    
    # Remove rows with missing coordinates
    df = df.dropna(subset=[lon_col, lat_col])
    print(f"   ✓ Valid coordinates: {len(df):,} segments")
    
    # Step 4: Select essential attributes
    print("\n🎯 STEP 4: Selecting essential attributes...")
    
    # Define important attributes (adjust based on actual columns)
    important_attrs = [
        id_col, lon_col, lat_col,
        # Geophysical
        'wave_height', 'tidal_range', 'sediment_supply', 'slope',
        # Hydrometeorological
        'river_discharge', 'precipitation', 'temperature',
        # Socioeconomic
        'population', 'gdp', 'erosion_risk'
    ]
    
    # Filter to existing columns (remove duplicates)
    available_attrs = []
    seen = set()
    for col in important_attrs:
        if col in df.columns and col not in seen:
            available_attrs.append(col)
            seen.add(col)
    
    # If not enough columns, take first 10-15 most relevant
    if len(available_attrs) < 5:
        # Exclude text/object columns, keep numeric
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        for col in numeric_cols[:12]:
            if col not in seen:
                available_attrs.append(col)
                seen.add(col)
    
    df_web = df[available_attrs].copy()
    
    # Round numeric values to reduce file size
    for col in df_web.select_dtypes(include=['number']).columns:
        if col not in [id_col, lon_col, lat_col]:
            df_web[col] = df_web[col].round(2)
    
    print(f"   ✓ Selected {len(available_attrs)} attributes")
    print(f"   Attributes: {available_attrs}")
    
    # Step 5: Spatial sampling if needed
    print("\n📉 STEP 5: Checking file size...")
    
    estimated_size_mb = len(df_web) * 0.004  # ~4KB per point with multiple attributes
    
    if estimated_size_mb > MAX_SIZE_MB:
        print(f"   ⚠️  Estimated size: {estimated_size_mb:.1f} MB (exceeds {MAX_SIZE_MB} MB)")
        
        # Systematic spatial sampling (every Nth point)
        sample_rate = int(len(df_web) / (MAX_SIZE_MB / 0.004))
        df_web = df_web.iloc[::sample_rate].copy()
        
        print(f"   ✓ Sampled to {len(df_web):,} points (every {sample_rate}th segment)")
    else:
        print(f"   ✓ Estimated size: {estimated_size_mb:.1f} MB (within limit)")
    
    # Step 6: Convert to GeoDataFrame
    print("\n🌍 STEP 6: Creating GeoDataFrame...")
    
    geometry = [Point(lon, lat) for lon, lat in zip(df_web[lon_col], df_web[lat_col])]
    gdf = gpd.GeoDataFrame(df_web, geometry=geometry, crs='EPSG:4326')
    
    # Drop coordinate columns (redundant with geometry)
    gdf = gdf.drop(columns=[lon_col, lat_col])
    
    print(f"   ✓ Created GeoDataFrame with {len(gdf):,} features")
    
    # Step 7: Export to GeoJSON
    print("\n💾 STEP 7: Exporting to GeoJSON...")
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    
    gdf.to_file(OUTPUT_FILE, driver='GeoJSON')
    
    file_size_mb = OUTPUT_FILE.stat().st_size / 1024**2
    print(f"   ✓ Exported: {OUTPUT_FILE}")
    print(f"   File size: {file_size_mb:.2f} MB")
    print(f"   Features: {len(gdf):,}")
    
    # Step 8: Create metadata
    metadata = {
        'title': 'GCC - Global Coastal Characteristics',
        'description': 'Comprehensive coastal segment database (100km resolution)',
        'source': 'Athanasiou et al. (2024) - Global Coastal Characteristics',
        'spatial_resolution': '100 km coastal segments',
        'features_count': len(gdf),
        'file_size_mb': round(file_size_mb, 2),
        'attributes': {col: f'Coastal characteristic: {col}' for col in gdf.columns if col != 'geometry'},
        'reference': 'Athanasiou, P., et al. (2024). doi:10.5281/zenodo.8200199',
        'generated': pd.Timestamp.now().isoformat()
    }
    
    metadata_file = OUTPUT_FILE.with_suffix('.json')
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"   ✓ Metadata: {metadata_file}")
    
    print("\n" + "="*80)
    print("✅ COMPLETE!")
    print("="*80)

if __name__ == '__main__':
    main()
