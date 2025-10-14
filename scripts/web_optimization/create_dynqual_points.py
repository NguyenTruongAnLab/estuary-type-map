#!/usr/bin/env python3
"""
Create DynQual River Characteristics Points for Web Visualization
==================================================================

PURPOSE: Generate web-optimized GeoJSON from DynQual NetCDF grids (Jones et al. 2023)

INPUT:
- data/raw/DynQual-Jones_2023/discharge_annualAvg_1980_2019.nc
- data/raw/DynQual-Jones_2023/salinity_annualAvg_1980_2019.nc
- data/raw/DynQual-Jones_2023/waterTemperature_annualAvg_1980_2019.nc

OUTPUT:
- data/web/dynqual_river_characteristics.geojson (<5MB)

STRATEGY:
- Extract 10km grid cells near coastlines only (estuarine focus)
- Convert to point features with discharge and salinity attributes
- Aggressive spatial sampling to meet file size limits

Author: Global Water Body Surface Area Atlas Project
Date: October 13, 2025
"""

import xarray as xr
import geopandas as gpd
import pandas as pd
import numpy as np
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
RAW_DIR = DATA_DIR / 'raw' / 'DynQual-Jones_2023'
WEB_DIR = DATA_DIR / 'web'

# Input files
DISCHARGE_FILE = RAW_DIR / 'discharge_annualAvg_1980_2019.nc'
SALINITY_FILE = RAW_DIR / 'salinity_annualAvg_1980_2019.nc'
TEMPERATURE_FILE = RAW_DIR / 'waterTemperature_annualAvg_1980_2019.nc'

# Output file
OUTPUT_FILE = WEB_DIR / 'dynqual_river_characteristics.geojson'

# Processing parameters
MAX_SIZE_MB = 5.0
MIN_DISCHARGE = 1.0  # Minimum discharge to include (m³/s) - GLOBAL COVERAGE!
MAX_DISCHARGE = 100000  # Maximum plausible discharge (m³/s)
MAX_SALINITY = 45  # Maximum plausible salinity (PSU)
TARGET_POINTS = 5000  # Target number of points for web (up from 1660)

# ==============================================================================
# MAIN PROCESSING
# ==============================================================================

def main():
    """Create web-optimized DynQual river characteristics points"""
    
    print("\n" + "="*80)
    print("CREATE DYNQUAL RIVER CHARACTERISTICS FOR WEB")
    print("="*80)
    
    # Step 1: Load NetCDF datasets
    print("\n📂 STEP 1: Loading DynQual NetCDF files...")
    
    if not DISCHARGE_FILE.exists():
        print(f"   ❌ ERROR: {DISCHARGE_FILE} not found!")
        return
    
    ds_discharge = xr.open_dataset(DISCHARGE_FILE)
    print(f"   ✓ Loaded discharge: {DISCHARGE_FILE.name}")
    print(f"     Shape: {ds_discharge.dims}")
    
    ds_salinity = None
    if SALINITY_FILE.exists():
        ds_salinity = xr.open_dataset(SALINITY_FILE)
        print(f"   ✓ Loaded salinity: {SALINITY_FILE.name}")
    else:
        print(f"   ⚠️  Salinity file not found (optional)")
    
    ds_temperature = None
    if TEMPERATURE_FILE.exists():
        ds_temperature = xr.open_dataset(TEMPERATURE_FILE)
        print(f"   ✓ Loaded temperature: {TEMPERATURE_FILE.name}")
    else:
        print(f"   ⚠️  Temperature file not found (optional)")
    
    # Step 2: Extract data to DataFrame
    print("\n🗺️ STEP 2: Converting NetCDF to point features...")
    
    # Get discharge data (first time step if multiple)
    discharge_var = list(ds_discharge.data_vars)[0]  # Usually 'discharge' or similar
    discharge = ds_discharge[discharge_var]
    
    # If time dimension exists, take mean or first timestep
    if 'time' in discharge.dims:
        discharge = discharge.mean(dim='time')
    
    # Convert to DataFrame
    df = discharge.to_dataframe().reset_index()
    df = df.rename(columns={discharge_var: 'discharge'})
    
    print(f"   ✓ Extracted {len(df):,} grid cells")
    
    # Add TDS (Total Dissolved Solids) if available
    if ds_salinity is not None:
        tds_var = list(ds_salinity.data_vars)[0]  # This is actually 'tds', not salinity!
        tds = ds_salinity[tds_var]
        if 'time' in tds.dims:
            tds = tds.mean(dim='time')
        df_tds = tds.to_dataframe().reset_index()
        df = df.merge(df_tds, on=['lat', 'lon'], how='left')
        df = df.rename(columns={tds_var: 'tds'})
    
    # Add temperature if available (convert Kelvin to Celsius!)
    if ds_temperature is not None:
        temp_var = list(ds_temperature.data_vars)[0]
        temperature = ds_temperature[temp_var]
        if 'time' in temperature.dims:
            temperature = temperature.mean(dim='time')
        df_temp = temperature.to_dataframe().reset_index()
        df = df.merge(df_temp, on=['lat', 'lon'], how='left')
        df = df.rename(columns={temp_var: 'temperature'})
        # Convert Kelvin to Celsius
        df['temperature'] = df['temperature'] - 273.15
    
    # Step 3: Filter and clean data
    print("\n🧹 STEP 3: Filtering and cleaning...")
    
    # Remove invalid/fill values
    df = df[df['discharge'] > MIN_DISCHARGE]  # Global rivers with discharge > 1 m³/s
    df = df[df['discharge'] < MAX_DISCHARGE]
    
    if 'tds' in df.columns:
        # Remove extreme outliers using 2nd-98th percentile
        p2 = df['tds'].quantile(0.02)
        p98 = df['tds'].quantile(0.98)
        print(f"   TDS range (2nd-98th percentile): {p2:.1f} - {p98:.1f} mg/L")
        df = df[(df['tds'] >= p2) & (df['tds'] <= p98)]
        
        # Calculate salinity from TDS (PSU ≈ TDS mg/L / 640)
        df['salinity_psu'] = df['tds'] / 640.0
        
        # Additional salinity filter: rivers should be <40 PSU (max seawater!)
        df = df[df['salinity_psu'] < 40.0]
        print(f"   ✓ Calculated salinity from TDS (conversion factor: 640)")
        print(f"   Salinity range: {df['salinity_psu'].min():.2f} - {df['salinity_psu'].max():.2f} PSU")
    
    # Temperature outlier removal (2nd-98th percentile)
    if 'temperature' in df.columns:
        p2_temp = df['temperature'].quantile(0.02)
        p98_temp = df['temperature'].quantile(0.98)
        print(f"   Temperature range (2nd-98th percentile): {p2_temp:.1f} - {p98_temp:.1f}°C")
        df = df[(df['temperature'] >= p2_temp) & (df['temperature'] <= p98_temp)]
    
    # GLOBAL COVERAGE - No coastal filter!
    # DynQual is global surface water quality, not just estuarine
    print(f"   ✓ Filtered to {len(df):,} global river cells (discharge > {MIN_DISCHARGE} m³/s, outliers removed)")
    df_global = df.copy()
    
    # Step 4: Spatial sampling if needed
    print("\n📉 STEP 4: Spatial sampling...")
    
    estimated_size_mb = len(df_global) * 0.003  # ~3KB per point with attributes
    
    if estimated_size_mb > MAX_SIZE_MB or len(df_global) > TARGET_POINTS:
        print(f"   ⚠️  Need sampling: {len(df_global):,} points (target: {TARGET_POINTS})")
        
        # Stratified sampling by discharge magnitude
        df_global['discharge_log'] = np.log10(df_global['discharge'] + 1)
        df_global['discharge_bin'] = pd.qcut(df_global['discharge_log'], q=10, labels=False, duplicates='drop')
        
        # Sample proportionally from each bin
        df_global = df_global.groupby('discharge_bin', group_keys=False).apply(
            lambda x: x.sample(n=min(len(x), TARGET_POINTS // 10), random_state=42)
        )
        df_global = df_global.drop(columns=['discharge_log', 'discharge_bin'])
        
        print(f"   ✓ Sampled to {len(df_global):,} points")
    else:
        print(f"   ✓ Size OK: {estimated_size_mb:.1f} MB ({len(df_global):,} points)")
    
    # Step 5: Convert to GeoDataFrame
    print("\n🌍 STEP 5: Creating GeoDataFrame...")
    
    geometry = [Point(lon, lat) for lon, lat in zip(df_global['lon'], df_global['lat'])]
    gdf = gpd.GeoDataFrame(df_global, geometry=geometry, crs='EPSG:4326')
    
    # Clean up columns
    keep_cols = ['discharge', 'geometry']
    
    # Add TDS
    if 'tds' in gdf.columns:
        keep_cols.insert(1, 'tds')
        gdf['tds'] = gdf['tds'].round(0)
    
    # Add calculated salinity from TDS
    if 'salinity_psu' in gdf.columns:
        keep_cols.insert(2, 'salinity_psu')
        gdf['salinity_psu'] = gdf['salinity_psu'].round(3)
        gdf['salinity_class'] = gdf['salinity_psu'].apply(classify_salinity)
        keep_cols.append('salinity_class')
    
    # Add temperature
    if 'temperature' in gdf.columns:
        keep_cols.insert(3, 'temperature')
        gdf['temperature'] = gdf['temperature'].round(1)
    
    gdf['discharge'] = gdf['discharge'].round(1)
    gdf = gdf[keep_cols]
    
    print(f"   ✓ Created GeoDataFrame with {len(gdf):,} features")
    
    # Step 6: Export to GeoJSON
    print("\n💾 STEP 6: Exporting to GeoJSON...")
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    
    gdf.to_file(OUTPUT_FILE, driver='GeoJSON')
    
    file_size_mb = OUTPUT_FILE.stat().st_size / 1024**2
    print(f"   ✓ Exported: {OUTPUT_FILE}")
    print(f"   File size: {file_size_mb:.2f} MB")
    print(f"   Features: {len(gdf):,}")
    
    # Step 7: Create metadata
    metadata = {
        'title': 'DynQual River Characteristics (Jones et al. 2023)',
        'description': 'Global 10km resolution river discharge, TDS, temperature, and calculated salinity',
        'source': 'Jones et al. (2023) - Global hydrology and water quality',
        'temporal_coverage': '1980-2019 (annual average)',
        'spatial_resolution': '10 km',
        'features_count': len(gdf),
        'file_size_mb': round(file_size_mb, 2),
        'data_quality': 'Outliers removed using 2nd-98th percentile filter for TDS and temperature',
        'attributes': {
            'discharge': 'Annual average discharge (m³/s)',
            'tds': 'Total Dissolved Solids (mg/L)',
            'salinity_psu': 'Calculated salinity (PSU) = TDS / 640',
            'temperature': 'Annual average water temperature (°C)',
            'salinity_class': 'Venice System classification based on calculated salinity'
        },
        'reference': 'Jones, E.R., et al. (2023). doi:10.5194/essd-15-5287-2023',
        'generated': pd.Timestamp.now().isoformat()
    }
    
    metadata_file = OUTPUT_FILE.with_suffix('.json')
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"   ✓ Metadata: {metadata_file}")
    
    # Close datasets
    ds_discharge.close()
    if ds_salinity is not None:
        ds_salinity.close()
    if ds_temperature is not None:
        ds_temperature.close()
    
    print("\n" + "="*80)
    print("✅ COMPLETE!")
    print("="*80)

def classify_salinity(salinity_psu):
    """Classify salinity using Venice System"""
    if pd.isna(salinity_psu):
        return 'unknown'
    elif salinity_psu < 0.5:
        return 'freshwater'
    elif salinity_psu < 5:
        return 'oligohaline'
    elif salinity_psu < 18:
        return 'mesohaline'
    elif salinity_psu < 25:
        return 'polyhaline'
    elif salinity_psu < 35:
        return 'euhaline'
    else:
        return 'hyperhaline'

if __name__ == '__main__':
    main()
