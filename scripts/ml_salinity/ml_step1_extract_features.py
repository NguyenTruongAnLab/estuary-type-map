
"""
STEP 1: Feature Extraction for ML Classification
=================================================

Extract comprehensive features from GRIT, HydroSHEDS, Dürr, and GCC datasets
for machine learning-based salinity classification.

This creates a feature matrix that will be used for:
1. Training ML model on GlobSalt-validated segments
2. Predicting salinity for all other segments

Usage:
    python scripts/ml_step1_extract_features.py --region SP
    python scripts/ml_step1_extract_features.py --all-regions
"""

import sys
import warnings
import time
import argparse
from pathlib import Path
from typing import Optional, Dict
import pandas as pd
import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
GRIT_DIR = BASE_DIR / 'data' / 'raw' / 'GRIT-Michel_2025'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
RAW_DIR = BASE_DIR / 'data' / 'raw'
ML_DIR = PROCESSED_DIR / 'ml_features'
ML_DIR.mkdir(parents=True, exist_ok=True)

GRIT_REGIONS = ['AF', 'AS', 'EU', 'NA', 'SA', 'SI', 'SP']

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")


def calculate_distance_to_coast(segments: gpd.GeoDataFrame, 
                                 region_code: str) -> pd.Series:
    """
    Calculate Euclidean distance from segment centroids to nearest coastal outlet
    
    Uses GRIT nodes with node_type='coastal_outlet'
    Returns distance in kilometers
    """
    print(f"\n📏 Calculating distance to coast...")
    
    # Load GRIT nodes (from 'nodes' layer in segments file)
    nodes_file = GRIT_DIR / f'GRITv06_segments_{region_code}_EPSG4326.gpkg'
    
    if not nodes_file.exists():
        print(f"   ⚠️  Segments file not found: {nodes_file.name}")
        print(f"   Using segment geometry as fallback (coastline intersection)")
        # Fallback: assume segments near lat extremes are coastal
        return segments.geometry.centroid.y.abs().apply(lambda y: min(90 - y, y) * 111)
    
    try:
        nodes = gpd.read_file(nodes_file, layer='nodes', engine='pyogrio')
        
        # Filter for coastal outlets
        if 'node_type' not in nodes.columns:
            print(f"   ⚠️  'node_type' column not found in nodes")
            print(f"   Available columns: {nodes.columns.tolist()}")
            print(f"   Using all outlet nodes as coastal")
            # Fallback: use nodes at basin outlets
            coastal_outlets = nodes[nodes['outlet_flag'] == 1] if 'outlet_flag' in nodes.columns else nodes
        else:
            coastal_outlets = nodes[nodes['node_type'] == 'coastal_outlet']
        
        if len(coastal_outlets) == 0:
            print(f"   ⚠️  No coastal outlets found, using all outlet nodes")
            coastal_outlets = nodes[nodes['outlet_flag'] == 1] if 'outlet_flag' in nodes.columns else nodes[:1000]
        
        print(f"   ✓ Found {len(coastal_outlets):,} coastal outlet nodes")
        
        # Extract coordinates
        seg_coords = np.column_stack([
            segments.geometry.centroid.x,
            segments.geometry.centroid.y
        ])
        
        coast_coords = np.column_stack([
            coastal_outlets.geometry.x,
            coastal_outlets.geometry.y
        ])
        
        # Build KD-tree for efficient nearest neighbor search
        tree = cKDTree(coast_coords)
        distances, indices = tree.query(seg_coords, k=1)
        
        # Convert degrees to kilometers (rough approximation)
        # More accurate would use haversine, but this is faster
        distances_km = distances * 111  # 1 degree ≈ 111 km
        
        print(f"   ✓ Distance range: {distances_km.min():.1f} - {distances_km.max():.1f} km")
        print(f"   ✓ Mean distance: {distances_km.mean():.1f} km")
        
        return pd.Series(distances_km, index=segments.index)
        
    except Exception as e:
        print(f"   ❌ Error loading nodes: {e}")
        print(f"   Using fallback distance calculation")
        return segments.geometry.centroid.y.abs().apply(lambda y: min(90 - y, y) * 111)


def join_durr_features(segments: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Spatial join with Dürr 2011 estuary database
    Returns binary indicator and estuary type
    """
    print(f"\n🗺️  Joining with Dürr 2011 estuary database...")
    
    durr_dir = RAW_DIR / 'Worldwide-typology-Shapefile-Durr_2011'
    
    # Try different possible filenames
    possible_files = [
        durr_dir / 'typology_catchments.shp',  # Actual filename
        durr_dir / 'Catch_WW.shp',
        durr_dir / 'Dürr_catchments.shp',
        durr_dir / 'duerr_catchments.shp',
        durr_dir / 'catchments.shp'
    ]
    
    durr_file = None
    for f in possible_files:
        if f.exists():
            durr_file = f
            break
    
    if durr_file is None:
        print(f"   ⚠️  Dürr data not found in: {durr_dir}")
        print(f"   Creating dummy features (in_durr_estuary=0)")
        return pd.DataFrame({
            'in_durr_estuary': 0,
            'durr_type_encoded': 0
        }, index=segments.index)
    
    try:
        durr = gpd.read_file(durr_file)
        print(f"   ✓ Loaded {len(durr):,} Dürr estuary catchments")
        
        # Ensure CRS match
        if segments.crs != durr.crs:
            durr = durr.to_crs(segments.crs)
        
        # Spatial join
        seg_with_durr = gpd.sjoin(
            segments[['global_id', 'geometry']],
            durr[['BASINID', 'FIN_TYP', 'geometry']],
            how='left',
            predicate='intersects'
        )
        
        # Handle duplicates (keep first)
        seg_with_durr = seg_with_durr.drop_duplicates(subset=['global_id'], keep='first')
        
        # Binary indicator
        features = pd.DataFrame({
            'in_durr_estuary': seg_with_durr['BASINID'].notna().astype(int),
        }, index=segments.index)
        
        # Encode estuary type (for ML)
        durr_types = seg_with_durr['FIN_TYP'].fillna('Not_Estuary')
        type_mapping = {
            'Delta': 1,
            'Tidal': 2,
            'Lagoon': 3,
            'Fjord': 4,
            'Coastal Plain': 5,
            'Not_Estuary': 0
        }
        features['durr_type_encoded'] = durr_types.map(
            lambda x: type_mapping.get(x, 0)
        )
        
        matched = features['in_durr_estuary'].sum()
        print(f"   ✓ Matched: {matched:,} segments in Dürr estuaries ({matched/len(segments)*100:.1f}%)")
        
        return features
        
    except Exception as e:
        print(f"   ❌ Error processing Dürr data: {e}")
        return pd.DataFrame({
            'in_durr_estuary': 0,
            'durr_type_encoded': 0
        }, index=segments.index)


def extract_features_for_region(region_code: str) -> Optional[pd.DataFrame]:
    """
    Extract comprehensive feature set for a single region
    """
    print_section(f"🔬 FEATURE EXTRACTION: {region_code}")
    
    # Load GlobSalt-classified segments
    segments_file = PROCESSED_DIR / f'rivers_grit_segments_classified_{region_code.lower()}.gpkg'
    
    if not segments_file.exists():
        print(f"❌ Segments file not found: {segments_file}")
        print(f"   Run process_grit_all_regions.py first!")
        return None
    
    print(f"\n📂 Loading segments...")
    segments = gpd.read_file(segments_file)
    print(f"✓ Loaded {len(segments):,} segments")
    
    # Initialize feature dataframe
    features = pd.DataFrame({'global_id': segments['global_id']})
    
    # ===== FEATURE 1: Distance to coast (CRITICAL!) =====
    features['dist_to_coast_km'] = calculate_distance_to_coast(segments, region_code)
    features['log_dist_to_coast'] = np.log1p(features['dist_to_coast_km'])
    
    # ===== FEATURE 2: GRIT network attributes =====
    print(f"\n🌊 Extracting GRIT network features...")
    # Map GRIT actual column names
    grit_feature_map = {
        'strahler_order': 'strahler_order',
        'length': 'length',
        'upstream_area': 'drainage_area_out',  # GRIT uses this name
        'sinuosity': 'sinuousity',  # Note: GRIT spells it 'sinuousity'
        'azimuth': 'azimuth',
        'is_mainstem': 'is_mainstem'
    }
    grit_features = list(grit_feature_map.keys())
    
    for feat_name, grit_col in grit_feature_map.items():
        if grit_col in segments.columns:
            features[feat_name] = segments[grit_col]
            print(f"   ✓ {feat_name} (from {grit_col})")
        else:
            print(f"   ⚠️  {feat_name} not found (expected: {grit_col}), setting to 0")
            features[feat_name] = 0
    
    # Derived features
    features['log_upstream_area'] = np.log1p(features['upstream_area'])
    features['length_km'] = features['length'] / 1000
    
    # ===== FEATURE 3: Dürr estuary context =====
    durr_features = join_durr_features(segments)
    features = features.join(durr_features)
    
    # ===== FEATURE 4: Salinity (TARGET for training, NaN for prediction) =====
    if 'salinity_mean_psu' in segments.columns:
        features['salinity_mean_psu'] = segments['salinity_mean_psu']
        features['has_salinity'] = segments['salinity_mean_psu'].notna().astype(int)
    else:
        features['salinity_mean_psu'] = np.nan
        features['has_salinity'] = 0
    
    # ===== FEATURE 5: Geographic coordinates =====
    features['latitude'] = segments.geometry.centroid.y
    features['longitude'] = segments.geometry.centroid.x
    features['abs_latitude'] = features['latitude'].abs()  # Distance from equator
    
    # ===== FEATURE 6: Interaction features =====
    features['dist_x_strahler'] = features['dist_to_coast_km'] * features['strahler_order']
    features['area_per_length'] = features['upstream_area'] / (features['length_km'] + 1)
    
    # Summary
    print(f"\n📊 Feature Summary:")
    print(f"   Total features: {len(features.columns)}")
    print(f"   Segments with salinity: {features['has_salinity'].sum():,} ({features['has_salinity'].mean()*100:.1f}%)")
    print(f"   Distance range: {features['dist_to_coast_km'].min():.0f} - {features['dist_to_coast_km'].max():.0f} km")
    print(f"   In Dürr estuaries: {features['in_durr_estuary'].sum():,}")
    
    # Save
    output_file = ML_DIR / f'features_{region_code.lower()}.parquet'
    features.to_parquet(output_file)
    print(f"\n💾 Saved: {output_file}")
    
    return features


def main():
    parser = argparse.ArgumentParser(description='Extract features for ML classification')
    parser.add_argument('--region', type=str, choices=GRIT_REGIONS,
                        help='Process single region')
    parser.add_argument('--all-regions', action='store_true',
                        help='Process all regions')
    args = parser.parse_args()
    
    print_section("🔬 ML FEATURE EXTRACTION PIPELINE")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if args.all_regions:
        regions = GRIT_REGIONS
    elif args.region:
        regions = [args.region]
    else:
        print("❌ Must specify --region or --all-regions")
        return 1
    
    print(f"\n📋 Regions to process: {', '.join(regions)}")
    
    # Process each region
    for region_code in regions:
        features = extract_features_for_region(region_code)
        if features is None:
            print(f"⚠️  Skipping {region_code}")
    
    print_section("✅ FEATURE EXTRACTION COMPLETE")
    print(f"\n💾 Features saved to: {ML_DIR}")
    print(f"\nNext step: python scripts/ml_step2_train_model.py")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

