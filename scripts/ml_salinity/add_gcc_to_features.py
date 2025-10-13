"""
Add GCC (Global Coastal Characteristics) Features to ML Dataset
================================================================

Integrates Athanasiou et al. (2024) coastal indicators with GRIT river segments.

GCC provides 80 high-resolution (1 km) coastal indicators:
- Geophysical: Elevation, slopes, land cover, vegetation
- Hydrometeorological: Waves, tides, storm surge, temperature, precipitation  
- Socioeconomic: Population, GDP, infrastructure

Reference:
Athanasiou, P., van Dongeren, A., Pronk, M., Giardino, A., Vousdoukas, M., & 
Ranasinghe, R. (2024). Global Coastal Characteristics (GCC): a global dataset 
of geophysical, hydrodynamic, and socioeconomic coastal indicators. 
Earth System Science Data, 16, 3847–3894.
DOI: 10.5194/essd-16-3847-2024

Usage:
    python scripts/ml_salinity/add_gcc_to_features.py --region AS
    python scripts/ml_salinity/add_gcc_to_features.py --all-regions
"""

import sys
import argparse
import pandas as pd
import geopandas as gpd
from pathlib import Path
from scipy.spatial import cKDTree
import numpy as np
import time
import warnings

warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw' / 'GCC-Panagiotis-Athanasiou_2024'
ML_DIR = BASE_DIR / 'data' / 'processed' / 'ml_features'

GRIT_REGIONS = ['AF', 'AS', 'EU', 'NA', 'SA', 'SI', 'SP']

# GCC files
GCC_GEOPHYSICAL = RAW_DIR / 'GCC_geophysical.csv'
GCC_HYDROMETEOROLOGICAL = RAW_DIR / 'GCC_hydrometeorological.csv'

# Matching distance threshold (degrees, ~5 km at equator)
MATCH_DISTANCE_DEGREES = 0.05

# ==============================================================================
# FEATURE SELECTION
# ==============================================================================

# Select most relevant GCC features for estuarine classification
GCC_GEOPHYSICAL_FEATURES = [
    # Elevation features (important for tidal influence)
    'z_peak_max_1km_copdem',     # Max elevation within 1km
    'he',                         # Mean hinterland elevation
    'ev',                         # Variance of hinterland elevation
    
    # Slope features (control mixing and stratification)
    'ns',                         # Nearshore slope
    'bs_copdem',                  # Backshore slope
    'cs_copdem',                  # Coastal slope
    
    # Morphology features
    'x_shoreline',                # Distance to shoreline
    'doc',                        # Depth of closure
    'tr_zone_width',              # Transition zone width
    
    # Land cover (indicates sediment input, anthropogenic influence)
    'lu_trees',                   # % Trees
    'lu_crop',                    # % Cropland
    'lu_built',                   # % Built-up
    'lu_water',                   # % Open water
    'lu_wet',                     # % Wetland
    'lu_mangr',                   # % Mangroves
    
    # Coastal type flags
    'coast_type_flag',            # Sandy, Muddy, Rocky, Vegetated
    'veg_type',                   # Mangrove, Saltmarsh
]

GCC_HYDROMETEOROLOGICAL_FEATURES = [
    # Wave conditions (affect mixing)
    'swh_p50',                    # Median significant wave height
    'swh_p95',                    # 95th percentile wave height
    'pp1d_p50',                   # Median wave period
    
    # Tidal range (PRIMARY indicator of estuarine extent!)
    'mhhw',                       # Mean Higher High Water
    'mllw',                       # Mean Lower Low Water
    
    # Storm surge (affects saltwater intrusion)
    'ssl_p95',                    # 95th percentile storm surge
    'wl_rp10_mean',               # 10-year return period water level
    
    # Climate (affects discharge and evaporation)
    't2m_p50',                    # Median temperature
    't2m_p95',                    # 95th percentile temperature
    'tp_p50',                     # Median precipitation
    'tp_p95',                     # 95th percentile precipitation
]

ALL_GCC_FEATURES = GCC_GEOPHYSICAL_FEATURES + GCC_HYDROMETEOROLOGICAL_FEATURES

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")


def calculate_tidal_range(row):
    """Calculate tidal range from MHHW and MLLW"""
    if pd.notna(row['mhhw']) and pd.notna(row['mllw']):
        return row['mhhw'] - row['mllw']
    return np.nan


def encode_categorical(df, feature_name):
    """
    Encode categorical features as dummy variables
    
    CRITICAL: Use fixed categories to ensure ALL regions get SAME columns!
    This prevents KeyError when predicting (e.g., 'Salt-marshes' missing in EU).
    """
    if feature_name not in df.columns:
        return df, []
    
    # Define ALL possible categories (from GCC documentation)
    if 'coast_type_flag' in feature_name:
        # GCC coast types: Other, Rocky, Sandy, Vegetated
        categories = ['Other', 'Rocky', 'Sandy', 'Vegetated']
    elif 'veg_type' in feature_name:
        # GCC vegetation types: Mangroves, Salt-marshes
        categories = ['Mangroves', 'Salt-marshes']
    else:
        # Unknown categorical - use actual values
        categories = df[feature_name].dropna().unique().tolist()
    
    # Create dummy variables with FIXED categories
    # This ensures all regions get the same columns (even if category not present)
    dummies = pd.get_dummies(df[feature_name], prefix=feature_name)
    
    # Ensure ALL expected columns exist (fill missing with 0)
    expected_cols = [f"{feature_name}_{cat}" for cat in categories]
    for col in expected_cols:
        if col not in dummies.columns:
            dummies[col] = 0  # Missing category = all zeros
    
    # Keep only expected columns (drop any unexpected ones)
    dummies = dummies[expected_cols]
    
    # Add to dataframe
    df = pd.concat([df.drop(columns=[feature_name]), dummies], axis=1)
    
    return df, expected_cols


# ==============================================================================
# MAIN PROCESSING
# ==============================================================================

def load_gcc_data():
    """Load GCC datasets"""
    print_section("📂 LOADING GCC DATA")
    
    print(f"📂 Loading geophysical features...")
    if not GCC_GEOPHYSICAL.exists():
        print(f"❌ File not found: {GCC_GEOPHYSICAL}")
        return None, None
    
    geo_df = pd.read_csv(GCC_GEOPHYSICAL, usecols=['lon', 'lat'] + GCC_GEOPHYSICAL_FEATURES)
    print(f"   ✓ Loaded {len(geo_df):,} transects with {len(GCC_GEOPHYSICAL_FEATURES)} features")
    
    print(f"\n📂 Loading hydrometeorological features...")
    if not GCC_HYDROMETEOROLOGICAL.exists():
        print(f"❌ File not found: {GCC_HYDROMETEOROLOGICAL}")
        return None, None
    
    hydro_df = pd.read_csv(GCC_HYDROMETEOROLOGICAL, usecols=['lon', 'lat'] + GCC_HYDROMETEOROLOGICAL_FEATURES)
    print(f"   ✓ Loaded {len(hydro_df):,} transects with {len(GCC_HYDROMETEOROLOGICAL_FEATURES)} features")
    
    # Merge geophysical and hydrometeorological
    print(f"\n🔗 Merging GCC datasets...")
    gcc_df = pd.merge(geo_df, hydro_df, on=['lon', 'lat'], how='inner')
    print(f"   ✓ Merged: {len(gcc_df):,} transects with {len(ALL_GCC_FEATURES)} features")
    
    # Calculate derived features
    print(f"\n🧮 Calculating derived features...")
    gcc_df['tidal_range'] = gcc_df.apply(calculate_tidal_range, axis=1)
    print(f"   ✓ Added tidal_range (mhhw - mllw)")
    
    # Add tidal_range to feature list
    ALL_GCC_FEATURES.append('tidal_range')
    
    return gcc_df, ALL_GCC_FEATURES


def match_gcc_to_segments(features_df, gcc_df, region_code):
    """Match GCC transects to GRIT segments using nearest neighbor"""
    print_section(f"🔗 MATCHING GCC TO GRIT SEGMENTS - {region_code}")
    
    # Filter to coastal segments only (within 100 km)
    coastal_segments = features_df[features_df['dist_to_coast_km'] <= 100].copy()
    print(f"📍 Coastal segments (<100 km): {len(coastal_segments):,} / {len(features_df):,}")
    
    if len(coastal_segments) == 0:
        print(f"⚠️  No coastal segments in {region_code}")
        return features_df
    
    # Build spatial index for GCC transects
    print(f"\n🗺️  Building spatial index...")
    gcc_coords = gcc_df[['lon', 'lat']].values
    gcc_tree = cKDTree(gcc_coords)
    
    # Find nearest GCC transect for each segment
    # Note: Features file uses 'longitude' and 'latitude', not 'lon' and 'lat'
    print(f"🔍 Finding nearest GCC transect for each segment...")
    segment_coords = coastal_segments[['longitude', 'latitude']].values
    distances, indices = gcc_tree.query(segment_coords, k=1)
    
    # Filter by distance threshold
    valid_matches = distances <= MATCH_DISTANCE_DEGREES
    n_matched = valid_matches.sum()
    print(f"   ✓ Matched: {n_matched:,} / {len(coastal_segments):,} segments ({n_matched/len(coastal_segments)*100:.1f}%)")
    print(f"   Distance threshold: {MATCH_DISTANCE_DEGREES:.4f}° (~{MATCH_DISTANCE_DEGREES*111:.1f} km)")
    print(f"   Mean distance: {distances[valid_matches].mean():.4f}° (~{distances[valid_matches].mean()*111:.1f} km)")
    
    # Add GCC features to matched segments
    print(f"\n📥 Adding GCC features...")
    for feature in ALL_GCC_FEATURES:
        coastal_segments[f'gcc_{feature}'] = np.nan
        coastal_segments.loc[valid_matches, f'gcc_{feature}'] = gcc_df.iloc[indices[valid_matches]][feature].values
    
    # Merge back to full dataset
    features_df = features_df.drop(columns=[f'gcc_{f}' for f in ALL_GCC_FEATURES if f'gcc_{f}' in features_df.columns], errors='ignore')
    for feature in ALL_GCC_FEATURES:
        features_df[f'gcc_{feature}'] = np.nan
        features_df.loc[coastal_segments.index, f'gcc_{feature}'] = coastal_segments[f'gcc_{feature}']
    
    # Encode categorical features
    print(f"\n🏷️  Encoding categorical features...")
    new_features = []
    for feature in ['coast_type_flag', 'veg_type']:
        gcc_feature = f'gcc_{feature}'
        if gcc_feature in features_df.columns:
            features_df, dummies = encode_categorical(features_df, gcc_feature)
            new_features.extend(dummies)
            print(f"   ✓ {gcc_feature} → {len(dummies)} dummy variables")
    
    # Summary
    print(f"\n📊 GCC Feature Coverage:")
    for feature in ALL_GCC_FEATURES:
        gcc_feature = f'gcc_{feature}'
        if gcc_feature in features_df.columns:
            coverage = features_df[gcc_feature].notna().sum()
            print(f"   {feature:30s}: {coverage:7,d} segments ({coverage/len(features_df)*100:5.1f}%)")
    
    return features_df


def process_region(region_code: str, gcc_df):
    """Add GCC features to a single region"""
    print_section(f"🌍 PROCESSING REGION: {region_code}")
    
    features_file = ML_DIR / f'features_{region_code.lower()}.parquet'
    
    if not features_file.exists():
        print(f"❌ Features file not found: {features_file}")
        return False
    
    # Load existing features
    print(f"📂 Loading features: {features_file.name}")
    features_df = pd.read_parquet(features_file)
    print(f"   ✓ Loaded {len(features_df):,} segments with {len(features_df.columns)} features")
    
    # Check if GCC features already exist
    gcc_feature_cols = [c for c in features_df.columns if c.startswith('gcc_')]
    if len(gcc_feature_cols) > 0:
        print(f"\n⚠️  GCC features already exist ({len(gcc_feature_cols)} features)")
        print(f"   Removing existing GCC features before re-processing...")
        features_df = features_df.drop(columns=gcc_feature_cols)
        print(f"   ✓ Cleaned: {len(features_df.columns)} features remaining")
    
    # Match and add GCC features
    features_df = match_gcc_to_segments(features_df, gcc_df, region_code)
    
    # Save updated features
    output_file = ML_DIR / f'features_{region_code.lower()}.parquet'
    print(f"\n💾 Saving updated features: {output_file.name}")
    features_df.to_parquet(output_file, index=False)
    print(f"   ✓ Saved {len(features_df):,} segments with {len(features_df.columns)} features")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Add GCC coastal characteristics to ML features'
    )
    parser.add_argument('--region', type=str, choices=GRIT_REGIONS,
                        help='Process single region')
    parser.add_argument('--all-regions', action='store_true',
                        help='Process all regions')
    args = parser.parse_args()
    
    # Determine regions
    if args.all_regions:
        regions = GRIT_REGIONS
    elif args.region:
        regions = [args.region]
    else:
        print("❌ Must specify --region or --all-regions")
        sys.exit(1)
    
    print_section("🌊 ADD GCC FEATURES TO ML DATASET")
    print(f"\n📋 Configuration:")
    print(f"   Regions: {', '.join(regions)}")
    print(f"   Match distance: {MATCH_DISTANCE_DEGREES:.4f}° (~{MATCH_DISTANCE_DEGREES*111:.1f} km)")
    print(f"   Features: {len(ALL_GCC_FEATURES)} GCC indicators")
    
    # Load GCC data once (used for all regions)
    gcc_df, gcc_features = load_gcc_data()
    
    if gcc_df is None:
        print("\n❌ Failed to load GCC data")
        sys.exit(1)
    
    # Process each region
    start_time = time.time()
    success_count = 0
    
    for region_code in regions:
        if process_region(region_code, gcc_df):
            success_count += 1
    
    # Summary
    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    
    print_section("✅ COMPLETE")
    print(f"\n📊 Summary:")
    print(f"   Processed: {success_count} / {len(regions)} regions")
    print(f"   Time: {minutes}m {seconds}s")
    print(f"   Features added: {len(ALL_GCC_FEATURES)} GCC indicators")
    
    if success_count == len(regions):
        print(f"\n🎉 All regions updated successfully!")
        return 0
    else:
        print(f"\n⚠️  Some regions failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
