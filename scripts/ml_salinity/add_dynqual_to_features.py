
"""
Add DynQual Features to ML Pipeline
====================================

Extracts DynQual salinity, discharge, and temperature at GRIT segment centroids
and adds as ensemble features for ML classification.

This implements stacking/ensemble learning:
- Training labels: GlobSalt measurements (ground truth)
- Features: DynQual predictions + topology + Dürr
- NOT circular reasoning: DynQual is independent information source

Usage:
    python scripts/add_dynqual_to_features.py --region SP
    python scripts/add_dynqual_to_features.py --all-regions
"""

import sys
import warnings
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import xarray as xr

warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DYNQUAL_DIR = BASE_DIR / 'data' / 'raw' / 'DynQual-Jones_2023'
ML_DIR = BASE_DIR / 'data' / 'processed' / 'ml_features'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'

GRIT_REGIONS = ['AF', 'AS', 'EU', 'NA', 'SA', 'SI', 'SP']

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")


def load_dynqual_datasets():
    """
    Load DynQual NetCDF files
    """
    print(f"\n📂 Loading DynQual datasets...")
    
    files = {
        'salinity': DYNQUAL_DIR / 'salinity_annualAvg_1980_2019.nc',
        'discharge': DYNQUAL_DIR / 'discharge_annualAvg_1980_2019.nc',
        'temperature': DYNQUAL_DIR / 'waterTemperature_annualAvg_1980_2019.nc',
    }
    
    # Check existence
    for name, path in files.items():
        if not path.exists():
            print(f"❌ Missing: {path.name}")
            return None
    
    try:
        ds_sal = xr.open_dataset(files['salinity'])
        ds_dis = xr.open_dataset(files['discharge'])
        ds_temp = xr.open_dataset(files['temperature'])
        
        print(f"✓ Loaded DynQual datasets:")
        print(f"   Salinity: {list(ds_sal.data_vars)[0]}")
        print(f"   Discharge: {list(ds_dis.data_vars)[0]}")
        print(f"   Temperature: {list(ds_temp.data_vars)[0]}")
        
        return {
            'salinity': ds_sal,
            'discharge': ds_dis,
            'temperature': ds_temp
        }
    except Exception as e:
        print(f"❌ Error loading DynQual: {e}")
        return None


def add_dynqual_to_region(region_code: str, dynqual_datasets: dict):
    """
    Add DynQual features to existing ML feature file
    """
    print_section(f"🔬 ADDING DYNQUAL FEATURES: {region_code}")
    
    # Load existing features
    feature_file = ML_DIR / f'features_{region_code.lower()}.parquet'
    
    if not feature_file.exists():
        print(f"❌ Feature file not found: {feature_file}")
        print(f"   Run ml_step1_extract_features.py first!")
        return False
    
    features = pd.read_parquet(feature_file)
    print(f"✓ Loaded {len(features):,} features")
    
    # Check if DynQual already added
    if 'dynqual_salinity_psu' in features.columns:
        print(f"⚠️  DynQual features already exist, skipping")
        return True
    
    # Load GRIT segments for geometries
    segments_file = PROCESSED_DIR / f'rivers_grit_segments_classified_{region_code.lower()}.gpkg'
    if not segments_file.exists():
        print(f"❌ Segments file not found: {segments_file}")
        return False
    
    import geopandas as gpd
    segments = gpd.read_file(segments_file)
    
    # Merge to get geometries
    data = features.merge(segments[['global_id', 'geometry']], on='global_id', how='left')
    data = gpd.GeoDataFrame(data, geometry='geometry', crs=segments.crs)
    
    # Extract centroids
    centroids_lon = data.geometry.centroid.x.values
    centroids_lat = data.geometry.centroid.y.values
    
    print(f"\n📊 Extracting DynQual values at {len(data):,} centroids...")
    
    # Get variable names
    ds_sal = dynqual_datasets['salinity']
    ds_dis = dynqual_datasets['discharge']
    ds_temp = dynqual_datasets['temperature']
    
    sal_var = list(ds_sal.data_vars)[0]
    dis_var = list(ds_dis.data_vars)[0]
    temp_var = list(ds_temp.data_vars)[0]
    
    # Use most recent decade (2010-2019) for contemporary conditions
    # Time dimension: 0=1980, 39=2019, so indices 30-39 = 2010-2019
    print(f"   Computing recent decade average (2010-2019)...")
    ds_sal_recent = ds_sal[sal_var].isel(time=slice(30, 40)).mean(dim='time')
    ds_dis_recent = ds_dis[dis_var].isel(time=slice(30, 40)).mean(dim='time')
    ds_temp_recent = ds_temp[temp_var].isel(time=slice(30, 40)).mean(dim='time')
    
    # Extract values (nearest neighbor)
    try:
        sal_values = []
        dis_values = []
        temp_values = []
        
        for lon, lat in zip(centroids_lon, centroids_lat):
            # Salinity (TDS in mg/L) - recent decade average
            sal = ds_sal_recent.sel(lon=lon, lat=lat, method='nearest').values
            sal_values.append(float(sal) if not np.isnan(sal) else np.nan)
            
            # Discharge (m³/s) - recent decade average
            dis = ds_dis_recent.sel(lon=lon, lat=lat, method='nearest').values
            dis_values.append(float(dis) if not np.isnan(dis) else np.nan)
            
            # Temperature (°C) - recent decade average
            temp = ds_temp_recent.sel(lon=lon, lat=lat, method='nearest').values
            temp_values.append(float(temp) if not np.isnan(temp) else np.nan)
        
        # Add to features
        features['dynqual_tds_mgL'] = sal_values
        features['dynqual_discharge_m3s'] = dis_values
        features['dynqual_temperature_C'] = temp_values
        
        # Convert TDS to salinity (rough: TDS mg/L / 640 ≈ PSU)
        features['dynqual_salinity_psu'] = features['dynqual_tds_mgL'] / 640
        
        # CRITICAL FIX: Sanitize DynQual data - remove impossible values from NetCDF fill values
        # These are land/no-data cells that have extreme values (e.g., 21,606 PSU!)
        MAX_SALINITY_PSU = 45.0   # Safe upper limit for estuaries/coastal zones
        MAX_TDS_MGL = 60000.0     # Approximate equivalent (~94 PSU)
        MAX_DISCHARGE_M3S = 300000.0  # Amazon peak is ~200,000 m³/s
        MAX_TEMP_C = 50.0  # Natural waters <45°C
        MIN_TEMP_C = -2.0  # Seawater freezes at ~-2°C
        
        print(f"\n🧹 Sanitizing DynQual data (removing impossible values)...")
        
        # Count outliers before removal
        outliers_sal = (features['dynqual_salinity_psu'] > MAX_SALINITY_PSU).sum()
        outliers_tds = (features['dynqual_tds_mgL'] > MAX_TDS_MGL).sum()
        outliers_dis = (features['dynqual_discharge_m3s'] > MAX_DISCHARGE_M3S).sum()
        outliers_temp = ((features['dynqual_temperature_C'] > MAX_TEMP_C) | 
                         (features['dynqual_temperature_C'] < MIN_TEMP_C)).sum()
        
        if outliers_sal + outliers_tds + outliers_dis + outliers_temp > 0:
            print(f"   Found {outliers_sal:,} impossible salinity values (>{MAX_SALINITY_PSU} PSU)")
            print(f"   Found {outliers_tds:,} impossible TDS values (>{MAX_TDS_MGL} mg/L)")
            print(f"   Found {outliers_dis:,} impossible discharge values (>{MAX_DISCHARGE_M3S} m³/s)")
            print(f"   Found {outliers_temp:,} impossible temperature values")
            print(f"   Replacing with NaN (will be median-filled during training)")
        
        # Replace impossible values with NaN
        features['dynqual_salinity_psu'] = features['dynqual_salinity_psu'].where(
            features['dynqual_salinity_psu'] <= MAX_SALINITY_PSU
        )
        features['dynqual_tds_mgL'] = features['dynqual_tds_mgL'].where(
            features['dynqual_tds_mgL'] <= MAX_TDS_MGL
        )
        features['dynqual_discharge_m3s'] = features['dynqual_discharge_m3s'].where(
            features['dynqual_discharge_m3s'] <= MAX_DISCHARGE_M3S
        )
        features['dynqual_temperature_C'] = features['dynqual_temperature_C'].where(
            (features['dynqual_temperature_C'] >= MIN_TEMP_C) & 
            (features['dynqual_temperature_C'] <= MAX_TEMP_C)
        )
        
        # Add derived features
        features['log_dynqual_salinity'] = np.log1p(features['dynqual_salinity_psu'])
        features['log_dynqual_discharge'] = np.log1p(features['dynqual_discharge_m3s'])
        
        # Interaction features
        if 'dist_to_coast_km' in features.columns:
            features['salinity_x_distance'] = features['dynqual_salinity_psu'] * features['dist_to_coast_km']
            features['discharge_x_distance'] = features['dynqual_discharge_m3s'] * features['dist_to_coast_km']
        
        print(f"✓ Extracted and sanitized DynQual values")
        
        # Summary statistics (now sanitized)
        print(f"\n📊 DynQual Summary (Sanitized):")
        print(f"   TDS range: {features['dynqual_tds_mgL'].min():.1f} - {features['dynqual_tds_mgL'].max():.1f} mg/L")
        print(f"   Salinity range: {features['dynqual_salinity_psu'].min():.2f} - {features['dynqual_salinity_psu'].max():.2f} PSU")
        print(f"   Discharge range: {features['dynqual_discharge_m3s'].min():.1f} - {features['dynqual_discharge_m3s'].max():.1f} m³/s")
        print(f"   Temperature range: {features['dynqual_temperature_C'].min():.1f} - {features['dynqual_temperature_C'].max():.1f} °C")
        
        # Count non-NaN values
        n_valid = features['dynqual_salinity_psu'].notna().sum()
        print(f"   Valid values: {n_valid:,} / {len(features):,} ({n_valid/len(features)*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ Extraction error: {e}")
        return False
    
    # Save updated features
    features.to_parquet(feature_file)
    print(f"\n💾 Updated: {feature_file.name}")
    print(f"   New columns: dynqual_salinity_psu, dynqual_discharge_m3s, dynqual_temperature_C")
    print(f"   Derived: log_dynqual_salinity, log_dynqual_discharge")
    print(f"   Interactions: salinity_x_distance, discharge_x_distance")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Add DynQual features to ML pipeline')
    parser.add_argument('--region', type=str, choices=GRIT_REGIONS,
                        help='Process single region')
    parser.add_argument('--all-regions', action='store_true',
                        help='Process all regions')
    args = parser.parse_args()
    
    print_section("🔬 DYNQUAL FEATURE INTEGRATION")
    print(f"Adding DynQual ensemble features to ML pipeline")
    print(f"Approach: Stacking (DynQual predictions as features, GlobSalt as labels)")
    
    # Determine regions
    if args.all_regions:
        regions = GRIT_REGIONS
    elif args.region:
        regions = [args.region]
    else:
        print("❌ Must specify --region or --all-regions")
        return 1
    
    print(f"\n📋 Regions to process: {', '.join(regions)}")
    
    # Load DynQual datasets (once)
    dynqual_datasets = load_dynqual_datasets()
    if dynqual_datasets is None:
        return 1
    
    # Process each region
    success_count = 0
    for region_code in regions:
        if add_dynqual_to_region(region_code, dynqual_datasets):
            success_count += 1
    
    # Summary
    print_section("✅ DYNQUAL INTEGRATION COMPLETE")
    print(f"✓ Successfully updated {success_count}/{len(regions)} regions")
    
    if success_count > 0:
        print(f"\n📊 Next Steps:")
        print(f"   1. Retrain model: python scripts/ml_step2_train_model.py")
        print(f"   2. Compare baseline vs enhanced performance")
        print(f"   3. Check feature importance (DynQual should rank in top 5)")
        print(f"   4. If improvement >3% and p<0.05 → Keep DynQual ✅")
        print(f"   5. If no improvement → Remove DynQual features ❌")
    
    return 0 if success_count == len(regions) else 1


if __name__ == '__main__':
    sys.exit(main())

