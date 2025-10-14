#!/usr/bin/env python3
"""
Create GlobSalt Station Points for Web Visualization
=====================================================

PURPOSE: Generate web-optimized GeoJSON of GlobSalt salinity monitoring stations

INPUT:
- data/processed/globsalt_stations.gpkg (from process_globsalt_integrated.py)

OUTPUT:
- data/web/globsalt_stations.geojson (<5MB, optimized for web)

FEATURES:
- Station locations (points)
- Average salinity measurements
- Temporal coverage (years)
- Data quality indicators

Author: Global Water Body Surface Area Atlas Project
Date: October 13, 2025
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
WEB_DIR = DATA_DIR / 'web'

# Input/Output files
INPUT_FILE = PROCESSED_DIR / 'globsalt_stations.gpkg'
OUTPUT_FILE = WEB_DIR / 'globsalt_stations.geojson'

# Maximum file size target
MAX_SIZE_MB = 5.0

# ==============================================================================
# MAIN PROCESSING
# ==============================================================================

def main():
    """Create web-optimized GlobSalt station points"""
    
    print("\n" + "="*80)
    print("CREATE GLOBSALT STATION POINTS FOR WEB")
    print("="*80)
    
    # Step 1: Load GlobSalt stations
    print("\n📂 STEP 1: Loading GlobSalt stations...")
    print(f"   File: {INPUT_FILE}")
    
    if not INPUT_FILE.exists():
        print(f"   ❌ ERROR: Input file not found!")
        print(f"   Run: python scripts/raw_data_processing/process_globsalt_integrated.py")
        return
    
    stations = gpd.read_file(INPUT_FILE)
    print(f"   ✓ Loaded {len(stations):,} stations")
    print(f"   Columns: {list(stations.columns)}")
    
    # Step 2: Select and optimize attributes
    print("\n🎯 STEP 2: Optimizing attributes for web...")
    
    # Keep only essential columns (use actual column names from GPKG)
    keep_columns = [
        'Station_ID',           # Station identifier
        'salinity_mean_psu',    # Average salinity (ACTUAL NAME!)
        'salinity_median_psu',  # Median salinity
        'salinity_std_psu',     # Standard deviation
        'n_measurements',       # Number of measurements
        'Water_type',           # Water type classification
        'salinity_zone',        # Salinity zone
        'geometry'
    ]
    
    # Filter to columns that exist
    available_columns = [col for col in keep_columns if col in stations.columns]
    stations_web = stations[available_columns].copy()
    
    # Round numerical values to reduce file size
    if 'salinity_mean_psu' in stations_web.columns:
        stations_web['salinity_mean_psu'] = stations_web['salinity_mean_psu'].round(2)
    if 'salinity_median_psu' in stations_web.columns:
        stations_web['salinity_median_psu'] = stations_web['salinity_median_psu'].round(2)
    if 'salinity_std_psu' in stations_web.columns:
        stations_web['salinity_std_psu'] = stations_web['salinity_std_psu'].round(2)
    
    # Use existing salinity_zone if available, otherwise classify
    if 'salinity_zone' not in stations_web.columns and 'salinity_mean_psu' in stations_web.columns:
        stations_web['salinity_zone'] = stations_web['salinity_mean_psu'].apply(classify_salinity)
    elif 'salinity_zone' in stations_web.columns:
        # Rename to match expected name
        stations_web['salinity_class'] = stations_web['salinity_zone']
    
    print(f"   ✓ Kept {len(available_columns)} attributes")
    print(f"   Features: {len(stations_web):,}")
    
    # Step 3: Spatial sampling if too large
    print("\n🗺️ STEP 3: Checking file size...")
    
    # Estimate file size (rough approximation)
    estimated_size_mb = len(stations_web) * 0.002  # ~2KB per point
    
    # NO SAMPLING - Keep ALL stations for complete data verification!
    print(f"   ✓ Estimated size: {estimated_size_mb:.1f} MB")
    print(f"   ✓ Keeping ALL {len(stations_web):,} stations (no sampling!)")
    print(f"   Reason: Complete sampling sites needed for data verification")
    
    # Step 4: Export to GeoJSON
    print("\n💾 STEP 4: Exporting to GeoJSON...")
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    
    stations_web.to_file(OUTPUT_FILE, driver='GeoJSON')
    
    file_size_mb = OUTPUT_FILE.stat().st_size / 1024**2
    print(f"   ✓ Exported: {OUTPUT_FILE}")
    print(f"   File size: {file_size_mb:.2f} MB")
    print(f"   Features: {len(stations_web):,}")
    
    # Step 5: Create metadata
    metadata = {
        'title': 'GlobSalt Salinity Monitoring Stations',
        'description': 'Global network of salinity monitoring stations',
        'source': 'GlobSalt v2.0 (GEMS/Water, GRDC, national agencies)',
        'temporal_coverage': '1980-2023',
        'features_count': len(stations_web),
        'file_size_mb': round(file_size_mb, 2),
        'attributes': {
            'Station_ID': 'Unique station identifier',
            'salinity_mean_psu': 'Mean salinity (PSU)',
            'salinity_median_psu': 'Median salinity (PSU)',
            'salinity_std_psu': 'Standard deviation (PSU)',
            'salinity_zone': 'Venice System classification',
            'n_measurements': 'Number of measurements',
            'Water_type': 'Water body type'
        },
        'generated': pd.Timestamp.now().isoformat()
    }
    
    metadata_file = OUTPUT_FILE.with_suffix('.json')
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"   ✓ Metadata: {metadata_file}")
    
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
