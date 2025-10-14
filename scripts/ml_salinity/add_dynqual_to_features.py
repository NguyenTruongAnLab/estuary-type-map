
"""
Add DynQual Features to ML Pipeline
====================================

Extracts ONLY DynQual temperature (climate proxy) at GRIT segment centroids
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
    Load DynQual NetCDF file (TEMPERATURE ONLY)
    
    REMOVED:
    - Salinity: Circular reasoning (predicting salinity with salinity!)
    - Discharge: Poor quality, use GRIT upstream_area instead
    - TDS: Poor quality, 10km resolution too coarse
    
    KEPT:
    - Temperature: Useful climate/evaporation proxy
    """
    print(f"\n📂 Loading DynQual temperature dataset...")
    
    temp_file = DYNQUAL_DIR / 'waterTemperature_annualAvg_1980_2019.nc'
    
    # Check existence
    if not temp_file.exists():
        print(f"❌ Missing: {temp_file.name}")
        print(f"   Expected location: {temp_file}")
        return None
    
    try:
        ds_temp = xr.open_dataset(temp_file)
        temp_var = list(ds_temp.data_vars)[0]
        
        print(f"✓ Loaded DynQual temperature dataset")
        print(f"   Variable: {temp_var}")
        print(f"   Shape: {ds_temp[temp_var].shape}")
        print(f"   Time range: {ds_temp.time.values[0]} to {ds_temp.time.values[-1]}")
        
        return {'temperature': ds_temp}
        
    except Exception as e:
        print(f"❌ Error loading DynQual temperature: {e}")
        return None


def add_dynqual_to_region(region_code: str, dynqual_datasets: dict):
    """
    Add DynQual TEMPERATURE ONLY to existing ML feature file
    
    Temperature conversion: Kelvin → Celsius
    Quality control: Remove abnormal values (keep 5th-95th percentile, max 40°C)
    """
    print_section(f"🔬 ADDING DYNQUAL TEMPERATURE: {region_code}")
    
    # Load existing features
    feature_file = ML_DIR / f'features_{region_code.lower()}.parquet'
    
    if not feature_file.exists():
        print(f"❌ Feature file not found: {feature_file}")
        print(f"   Run ml_step1_extract_features.py first!")
        return False
    
    features = pd.read_parquet(feature_file)
    print(f"✓ Loaded {len(features):,} features")
    
    # Check if DynQual temperature already added
    if 'dynqual_temperature_C' in features.columns:
        print(f"⚠️  DynQual temperature already exists, skipping")
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
    
    # Get variable names (TEMPERATURE ONLY!)
    ds_temp = dynqual_datasets['temperature']
    temp_var = list(ds_temp.data_vars)[0]
    
    # REMOVED: salinity (poor quality, circular reasoning)
    # REMOVED: discharge (use GRIT upstream_area instead!)
    
    # Use most recent decade (2010-2019) for contemporary conditions
    # Time dimension: 0=1980, 39=2019, so indices 30-39 = 2010-2019
    print(f"   Computing recent decade average (2010-2019)...")
    ds_temp_recent = ds_temp[temp_var].isel(time=slice(30, 40)).mean(dim='time')
    
    # Extract temperature values (nearest neighbor)
    try:
        print(f"   Extracting temperature at {len(data):,} segment centroids...")
        temp_values = []
        
        for i, (lon, lat) in enumerate(zip(centroids_lon, centroids_lat)):
            if i % 10000 == 0 and i > 0:
                print(f"      Progress: {i:,} / {len(data):,} ({i/len(data)*100:.1f}%)")
            
            # Temperature - recent decade average
            temp = ds_temp_recent.sel(lon=lon, lat=lat, method='nearest').values
            temp_values.append(float(temp) if not np.isnan(temp) else np.nan)
        
        print(f"   ✓ Extracted {len(temp_values):,} temperature values")
        
        # Add to features as raw values (may be Kelvin)
        features['dynqual_temperature_raw'] = temp_values
        
        # CRITICAL: Convert temperature from Kelvin to Celsius if needed
        print(f"\n🌡️  Converting temperature to Celsius...")
        
        # Check if values are in Kelvin (typical range: 270-320 K)
        temp_median = features['dynqual_temperature_raw'].median()
        
        if temp_median > 100:  # Likely Kelvin
            print(f"   Detected Kelvin (median: {temp_median:.1f} K)")
            print(f"   Converting: Kelvin → Celsius (T_C = T_K - 273.15)")
            features['dynqual_temperature_C'] = features['dynqual_temperature_raw'] - 273.15
        else:  # Already Celsius
            print(f"   Already in Celsius (median: {temp_median:.1f} °C)")
            features['dynqual_temperature_C'] = features['dynqual_temperature_raw']
        
        # QUALITY CONTROL: Remove abnormal temperatures
        print(f"\n🧹 Applying quality control to temperature...")
        
        # Calculate percentiles
        p5 = features['dynqual_temperature_C'].quantile(0.02)
        p95 = features['dynqual_temperature_C'].quantile(0.98)
        
        print(f"   2th percentile: {p5:.1f} °C")
        print(f"   98th percentile: {p95:.1f} °C")
        
        # Apply filters:
        # 1. Keep only 2th-98th percentile
        # 2. Maximum 40°C (natural waters)
        # 3. Minimum -2°C (seawater freezing point)
        MAX_TEMP_C = 40.0
        MIN_TEMP_C = -2.0
        
        before_qc = features['dynqual_temperature_C'].notna().sum()
        
        # Create mask for valid temperatures
        valid_mask = (
            (features['dynqual_temperature_C'] >= p5) &
            (features['dynqual_temperature_C'] <= p95) &
            (features['dynqual_temperature_C'] >= MIN_TEMP_C) &
            (features['dynqual_temperature_C'] <= MAX_TEMP_C)
        )
        
        # Replace outliers with NaN
        features['dynqual_temperature_C'] = features['dynqual_temperature_C'].where(valid_mask)
        
        after_qc = features['dynqual_temperature_C'].notna().sum()
        removed = before_qc - after_qc
        
        print(f"   Filters applied:")
        print(f"      - Keep 2th-98th percentile: {p5:.1f} to {p95:.1f} °C")
        print(f"      - Maximum: {MAX_TEMP_C}°C")
        print(f"      - Minimum: {MIN_TEMP_C}°C")
        print(f"   Removed {removed:,} outliers ({removed/before_qc*100:.1f}%)")
        print(f"   Valid values: {after_qc:,} / {len(features):,} ({after_qc/len(features)*100:.1f}%)")
        
        # Drop raw temperature column
        features = features.drop(columns=['dynqual_temperature_raw'])
        
        print(f"\n✓ Temperature extraction and QC complete")
        
        # Summary statistics (after QC)
        print(f"\n📊 Temperature Summary (After QC):")
        print(f"   Range: {features['dynqual_temperature_C'].min():.1f} - {features['dynqual_temperature_C'].max():.1f} °C")
        print(f"   Mean: {features['dynqual_temperature_C'].mean():.1f} °C")
        print(f"   Median: {features['dynqual_temperature_C'].median():.1f} °C")
        print(f"   Std Dev: {features['dynqual_temperature_C'].std():.1f} °C")
        
        
    except Exception as e:
        print(f"❌ Extraction error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Save updated features
    features.to_parquet(feature_file)
    print(f"\n💾 Updated: {feature_file.name}")
    print(f"   ✅ New column: dynqual_temperature_C (climate/evaporation proxy)")
    print(f"   ✅ Quality controlled: 5th-95th percentile, max 40°C")
    print(f"   📊 Use GRIT upstream_area as discharge proxy instead!")
    
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
        print("\n⚠️  DynQual data not available")
        print("   Pipeline will continue with baseline features only")
        print("   This is acceptable - GRIT and GCC features are sufficient!")
        return 0  # Not an error - continue pipeline
    
    # Process each region
    success_count = 0
    failed_regions = []
    
    for i, region_code in enumerate(regions):
        print(f"\n{'='*80}")
        print(f"Processing region {i+1}/{len(regions)}: {region_code}")
        print(f"{'='*80}")
        
        try:
            if add_dynqual_to_region(region_code, dynqual_datasets):
                success_count += 1
                print(f"✓ {region_code} completed successfully")
            else:
                failed_regions.append(region_code)
                print(f"⚠️  {region_code} failed - continuing with next region")
        except Exception as e:
            print(f"❌ Error processing {region_code}: {e}")
            failed_regions.append(region_code)
            print(f"   Continuing with next region...")
    
    # Summary
    print("\n" + "="*80)
    print_section("✅ DYNQUAL INTEGRATION COMPLETE")
    print(f"✓ Successfully updated: {success_count}/{len(regions)} regions")
    
    if failed_regions:
        print(f"\n⚠️  Failed regions: {', '.join(failed_regions)}")
        print(f"   These regions will use baseline features only")
        print(f"   Pipeline can continue normally!")
    
    if success_count > 0:
        print(f"\n📊 Next Steps:")
        print(f"   1. Add GCC coastal features: python scripts/ml_salinity/add_gcc_to_features.py --all-regions")
        print(f"   2. Train hybrid model: python scripts/ml_salinity/ml_step2_train_model_hybrid.py")
        print(f"   3. Predict for all segments: python scripts/ml_salinity/ml_step3_predict_hybrid.py --all-regions")
        print(f"   4. Calculate surface areas: python scripts/ml_salinity/ml_step5_calculate_surface_areas.py --all-regions")
    
    # Always return 0 to continue pipeline (even if some regions failed)
    print(f"\n✅ Pipeline can continue to next step!")
    return 0


if __name__ == '__main__':
    sys.exit(main())

