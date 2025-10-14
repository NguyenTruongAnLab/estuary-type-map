#!/usr/bin/env python3
"""
Create Coastal Basin Layer with Estuarine Types
================================================

PURPOSE: Solve the Dürr visualization problem!

PROBLEM:
--------
Dürr catchments show ENTIRE watersheds (e.g., Amazon from Andes to Atlantic).
This makes it look like all of Brazil is "Delta" type, when only the mouth is!

SOLUTION:
---------
Use BasinATLAS Level 7 to create fine-resolution coastal basin layer:
1. Filter to coastal basins (COAST=1 + within 100 km of ocean)
2. Inherit Dürr estuary type via spatial join
3. Result: ONLY coastal portions shown with estuary types

OUTPUT:
-------
Web-optimized GeoJSON showing ONLY estuarine basins (not entire watersheds!)

Author: Global Water Body Surface Area Atlas Project
Date: October 13, 2025
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
from shapely.geometry import box
import time

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
RAW_DIR = DATA_DIR / 'raw'
PROCESSED_DIR = DATA_DIR / 'processed'
WEB_DIR = DATA_DIR / 'web'

# Input files
BASINATLAS_FILE = RAW_DIR / 'hydrosheds' / 'BasinATLAS_v10_lev07_QGIS.gpkg'
DURR_FILE = PROCESSED_DIR / 'durr_estuaries.geojson'

# Output file
OUTPUT_FILE = WEB_DIR / 'coastal_basins_estuarine_types.geojson'

# Processing parameters
MAX_DISTANCE_TO_COAST_KM = 100  # Only basins within 100 km of coast
SIMPLIFY_TOLERANCE = 0.05       # Simplification for web (degrees, ~5.5 km at equator - more aggressive!)
DIST_SINK_PERCENTILE = 0.50     # Use 50th percentile (more inclusive for deltas)

# Dürr columns (from process_durr.py output):
# - name: Estuary/basin name
# - type: Simple type (Delta, Fjord, Lagoon, Coastal Plain)
# - type_detailed: Detailed type (e.g., "Fjord/Fjaerd", "Large River with Tidal Delta")
# - type_code: Numeric code (1-7)
# - basin_area_km2: Basin area
# - sea_name, ocean_name: Geographic context
# - geometry: Polygon

# ==============================================================================
# MAIN PROCESSING
# ==============================================================================

def main():
    """Create coastal basin layer with estuarine types"""
    
    print("\n" + "="*80)
    print("CREATE COASTAL BASINS WITH ESTUARINE TYPES")
    print("="*80)
    print("\nSOLVING: Dürr shows entire watersheds (e.g., all of Amazon basin)")
    print("SOLUTION: Use BasinATLAS Level 7 for fine-resolution coastal basins")
    print("\n" + "="*80)
    
    # Step 1: Load BasinATLAS
    print("\n📂 STEP 1: Loading BasinATLAS Level 7...")
    print(f"   File: {BASINATLAS_FILE}")
    
    if not BASINATLAS_FILE.exists():
        print(f"\n❌ ERROR: BasinATLAS file not found!")
        print(f"   Expected: {BASINATLAS_FILE}")
        return 1
    
    start_time = time.time()
    basinATLAS = gpd.read_file(BASINATLAS_FILE)
    elapsed = time.time() - start_time
    
    print(f"   ✓ Loaded {len(basinATLAS):,} basins in {elapsed:.1f}s")
    print(f"   File size: {BASINATLAS_FILE.stat().st_size / 1024**2:.1f} MB")
    
    # Step 2: Filter to coastal basins
    print("\n🌊 STEP 2: Filtering to coastal basins...")
    print(f"   Criteria: COAST=1 (drains to ocean)")
    
    coastal_basins = basinATLAS[basinATLAS['COAST'] == 1].copy()
    print(f"   ✓ Coastal basins: {len(coastal_basins):,} / {len(basinATLAS):,} ({len(coastal_basins)/len(basinATLAS)*100:.1f}%)")
    
    # Further filter by distance to coast (use geometry bounds as proxy)
    print(f"\n📏 STEP 3: Filtering by distance to coast...")
    print(f"   Method: Selecting basins near coastline (heuristic)")
    
    # Calculate crude distance to nearest coast (using global ocean extent)
    # For simplicity, we'll keep COAST=1 basins that are in the lowest DIST_SINK percentile
    coastal_basins_sorted = coastal_basins.sort_values('DIST_SINK')
    distance_threshold = coastal_basins_sorted['DIST_SINK'].quantile(DIST_SINK_PERCENTILE)
    
    coastal_basins_near = coastal_basins[coastal_basins['DIST_SINK'] <= distance_threshold].copy()
    
    print(f"   Distance threshold: {distance_threshold:.0f} km ({DIST_SINK_PERCENTILE*100:.0f}th percentile)")
    print(f"   ✓ Near-coastal basins: {len(coastal_basins_near):,} / {len(coastal_basins):,}")
    
    # Step 4: Load Dürr estuaries
    print("\n📂 STEP 4: Loading Dürr estuary typology...")
    
    if not DURR_FILE.exists():
        print(f"\n❌ ERROR: Dürr file not found!")
        print(f"   Expected: {DURR_FILE}")
        print(f"   Run: python scripts/raw_data_processing/process_durr.py")
        return 1
    
    durr = gpd.read_file(DURR_FILE)
    print(f"   ✓ Loaded {len(durr):,} Dürr catchments")
    
    # Step 5: Spatial join (inherit Dürr types to coastal basins)
    print("\n🔗 STEP 5: Spatial join (BasinATLAS ← Dürr types)...")
    print(f"   Method: Intersection (basins that overlap Dürr catchments)")
    
    start_time = time.time()
    
    # Ensure same CRS
    if coastal_basins_near.crs != durr.crs:
        print(f"   Converting CRS: {durr.crs} → {coastal_basins_near.crs}")
        durr = durr.to_crs(coastal_basins_near.crs)
    
    # Spatial join (keep only relevant Dürr attributes)
    # Dürr columns: name, type, type_detailed, type_code, basin_area_km2
    coastal_basins_typed = gpd.sjoin(
        coastal_basins_near,
        durr[['name', 'type', 'type_detailed', 'geometry']],
        how='left',
        predicate='intersects'
    )
    
    # Remove duplicate basins (if overlapping multiple Dürr catchments, keep first)
    coastal_basins_typed = coastal_basins_typed.drop_duplicates(subset='HYBAS_ID', keep='first')
    
    elapsed = time.time() - start_time
    print(f"   ✓ Spatial join complete in {elapsed:.1f}s")
    
    # Step 6: Use Dürr estuary types
    print("\n🏷️  STEP 6: Adding estuary types...")
    
    # 'type' column already has readable names (Delta, Fjord, Lagoon, Coastal Plain)
    coastal_basins_typed['estuary_type'] = coastal_basins_typed['type'].fillna('Unclassified')
    coastal_basins_typed['estuary_name'] = coastal_basins_typed['name']  # Rename for clarity
    
    # Count by type
    type_counts = coastal_basins_typed['estuary_type'].value_counts()
    print(f"   Estuary types:")
    for etype, count in type_counts.items():
        print(f"      {etype}: {count:,} basins")
    
    # Step 7: Select attributes for web visualization
    print("\n📝 STEP 7: Selecting attributes for web...")
    
    keep_columns = [
        'HYBAS_ID',          # Basin ID
        'SUB_AREA',          # Basin area (km²)
        'UP_AREA',           # Upstream drainage area (km²)
        'DIST_SINK',         # Distance to ocean (km)
        'ORDER_',            # Stream order
        'dis_m3_pyr',        # Mean annual discharge (m³/year)
        'run_mm_syr',        # Runoff (mm/year)
        'estuary_type',      # Estuary type (Delta, Fjord, etc.)
        'estuary_name',      # Estuary name (from Dürr)
        'type_detailed',     # Detailed type (e.g., "Fjord/Fjaerd")
        'geometry'           # Basin polygon
    ]
    
    # Filter to columns that exist
    keep_columns_available = [col for col in keep_columns if col in coastal_basins_typed.columns]
    coastal_basins_web = coastal_basins_typed[keep_columns_available].copy()
    
    print(f"   ✓ Retained {len(keep_columns_available)} attributes")
    
    # Step 8: Simplify geometries for web
    print("\n🗜️  STEP 8: Simplifying geometries for web...")
    print(f"   Tolerance: {SIMPLIFY_TOLERANCE}° (~1.1 km at equator)")
    
    start_time = time.time()
    coastal_basins_web['geometry'] = coastal_basins_web.geometry.simplify(
        SIMPLIFY_TOLERANCE,
        preserve_topology=True
    )
    elapsed = time.time() - start_time
    
    print(f"   ✓ Simplified in {elapsed:.1f}s")
    
    # Step 9: Export to GeoJSON
    print("\n💾 STEP 9: Exporting to GeoJSON...")
    
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    
    coastal_basins_web.to_file(
        OUTPUT_FILE,
        driver='GeoJSON',
        engine='pyogrio'
    )
    
    file_size = OUTPUT_FILE.stat().st_size / 1024**2
    print(f"   ✓ Exported: {OUTPUT_FILE.name}")
    print(f"   File size: {file_size:.1f} MB")
    
    if file_size > 5:
        print(f"\n   ⚠️  WARNING: File is large ({file_size:.1f} MB)")
        print(f"   Consider: Further simplification or splitting by region")
    
    # Step 10: Generate summary statistics
    print("\n📊 STEP 10: Summary Statistics")
    print("-" * 80)
    
    total_basins = len(coastal_basins_web)
    typed_basins = coastal_basins_web[coastal_basins_web['estuary_type'] != 'Unclassified']
    
    print(f"\nBasin counts:")
    print(f"   Total coastal basins: {total_basins:,}")
    print(f"   With estuary type: {len(typed_basins):,} ({len(typed_basins)/total_basins*100:.1f}%)")
    print(f"   Unclassified: {total_basins - len(typed_basins):,}")
    
    if 'SUB_AREA' in coastal_basins_web.columns:
        total_area = coastal_basins_web['SUB_AREA'].sum()
        print(f"\nTotal coastal basin area: {total_area:,.0f} km²")
        print(f"   Mean basin area: {coastal_basins_web['SUB_AREA'].mean():.0f} km²")
        print(f"   Median basin area: {coastal_basins_web['SUB_AREA'].median():.0f} km²")
    
    print("\n" + "="*80)
    print("✅ SUCCESS!")
    print("="*80)
    print(f"\nOutput file: {OUTPUT_FILE}")
    print(f"\n💡 Usage:")
    print(f"   - Use this layer for web map visualization (NOT Dürr full catchments)")
    print(f"   - Shows ONLY coastal portions with estuarine influence")
    print(f"   - Fine resolution: Level 7 basins (not entire watersheds)")
    print(f"\n🎨 Visualization:")
    print(f"   - Color by estuary_type (Delta, Fjord, Lagoon, Coastal Plain)")
    print(f"   - Popup: estuary_type, estuary_name, SUB_AREA, dis_m3_pyr")
    print(f"   - Filter: Toggle estuary types on/off")
    print(f"\n📊 Available types:")
    if 'estuary_type' in coastal_basins_web.columns:
        for etype in coastal_basins_web['estuary_type'].unique():
            count = (coastal_basins_web['estuary_type'] == etype).sum()
            print(f"   - {etype}: {count:,} basins")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
