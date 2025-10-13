
"""
Join Salinity Data with Basin/River Geometries
===============================================

Fixes the critical issue: salinity data is POINTS, not polygons!

This script:
1. Reads salinity points (HYBAS_ID + salinity_zone)
2. Joins with HydroSHEDS basins to get POLYGON geometries
3. Joins with HydroSHEDS rivers to get LINE geometries
4. Creates properly colored layers for web display

Result: Basins and rivers colored by salinity zones!

Author: Global Estuary Type Map Project
Date: October 10, 2025
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
OPTIMIZED_DIR = DATA_DIR / 'optimized'
PROCESSED_DIR = DATA_DIR / 'processed'

# Salinity color mapping
SALINITY_COLORS = {
    'freshwater': '#2166ac',
    'oligohaline': '#67a9cf',
    'mesohaline': '#d1e5f0',
    'polyhaline': '#fddbc7',
    'euhaline': '#ef8a62',
    'hyperhaline': '#b2182b'
}

SALINITY_RANGES = {
    'freshwater': '<0.5 ppt',
    'oligohaline': '0.5-5 ppt',
    'mesohaline': '5-18 ppt',
    'polyhaline': '18-25 ppt',
    'euhaline': '25-35 ppt',
    'hyperhaline': '>35 ppt'
}

def load_salinity_points():
    """Load salinity data (currently points with HYBAS_ID)"""
    print("📂 Loading salinity points...")
    
    salinity_file = OPTIMIZED_DIR / 'salinity_zones.geojson'
    if not salinity_file.exists():
        salinity_file = PROCESSED_DIR / 'salinity_zones.gpkg'
    
    gdf = gpd.read_file(salinity_file)
    print(f"   ✓ Loaded {len(gdf)} salinity points")
    print(f"   Geometry type: {gdf.geometry.geom_type.unique()}")
    
    # Extract salinity attributes
    salinity_data = gdf[['HYBAS_ID', 'salinity_zone']].drop_duplicates()
    
    if 'salinity_ppt' in gdf.columns:
        salinity_data['salinity_ppt'] = gdf.groupby('HYBAS_ID')['salinity_ppt'].mean().values
    
    print(f"   ✓ Extracted {len(salinity_data)} unique HYBAS_ID with salinity data")
    print(f"   Salinity zones: {salinity_data['salinity_zone'].value_counts().to_dict()}")
    
    return salinity_data

def join_salinity_with_basins(salinity_data):
    """Join salinity data with basin polygons"""
    print("\n📂 Loading HydroSHEDS basins...")
    
    basins_file = OPTIMIZED_DIR / 'basins_lev06.geojson'
    if not basins_file.exists():
        basins_file = PROCESSED_DIR / 'basins_coastal_lev06.gpkg'
    
    if not basins_file.exists():
        print("   ❌ Basins file not found!")
        return None
    
    basins = gpd.read_file(basins_file)
    print(f"   ✓ Loaded {len(basins)} basin polygons")
    
    # Fix type mismatch: convert both to int64
    basins['HYBAS_ID'] = basins['HYBAS_ID'].astype('int64')
    salinity_data['HYBAS_ID'] = salinity_data['HYBAS_ID'].astype('int64')
    
    # Join with salinity data
    print("\n🔗 Joining salinity data with basins...")
    basins_salinity = basins.merge(salinity_data, on='HYBAS_ID', how='inner')
    
    print(f"   ✓ Matched {len(basins_salinity)} basins with salinity data")
    print(f"   Geometry type: {basins_salinity.geometry.geom_type.unique()}")
    
    # Add color attribute
    basins_salinity['color'] = basins_salinity['salinity_zone'].map(SALINITY_COLORS)
    basins_salinity['salinity_range'] = basins_salinity['salinity_zone'].map(SALINITY_RANGES)
    
    # Simplify for web
    print("\n   ✂️  Simplifying geometries for web...")
    basins_salinity['geometry'] = basins_salinity['geometry'].simplify(0.02, preserve_topology=True)
    
    # Keep only essential attributes
    columns_to_keep = ['HYBAS_ID', 'salinity_zone', 'salinity_range', 'color', 'geometry']
    if 'salinity_ppt' in basins_salinity.columns:
        columns_to_keep.insert(2, 'salinity_ppt')
    
    basins_salinity = basins_salinity[[col for col in columns_to_keep if col in basins_salinity.columns]]
    
    # Save
    output_file = OPTIMIZED_DIR / 'salinity_basins.geojson'
    basins_salinity.to_file(output_file, driver='GeoJSON')
    
    output_size = output_file.stat().st_size / (1024 * 1024)
    print(f"   ✓ Saved: {output_file.name} ({output_size:.1f} MB)")
    
    return basins_salinity

def join_salinity_with_rivers(salinity_data):
    """Join salinity data with river lines"""
    print("\n📂 Loading HydroSHEDS rivers...")
    
    rivers_file = OPTIMIZED_DIR / 'rivers_estuaries.geojson'
    if not rivers_file.exists():
        rivers_file = PROCESSED_DIR / 'rivers_estuaries_global.gpkg'
    
    if not rivers_file.exists():
        print("   ❌ Rivers file not found!")
        return None
    
    # Rivers are large - read in chunks or use pyogrio
    try:
        import pyogrio
        rivers = gpd.read_file(rivers_file, engine='pyogrio')
    except:
        rivers = gpd.read_file(rivers_file)
    
    print(f"   ✓ Loaded {len(rivers)} river segments")
    
    # Rivers don't have HYBAS_ID, need to join by spatial intersection or MAIN_BAS
    # For now, if rivers have basin ID in attributes
    if 'HYBAS_ID' in rivers.columns or 'MAIN_BAS' in rivers.columns:
        basin_col = 'HYBAS_ID' if 'HYBAS_ID' in rivers.columns else 'MAIN_BAS'
        
        print(f"\n🔗 Joining salinity data with rivers (by {basin_col})...")
        rivers_salinity = rivers.merge(
            salinity_data, 
            left_on=basin_col, 
            right_on='HYBAS_ID', 
            how='inner'
        )
        
        print(f"   ✓ Matched {len(rivers_salinity)} rivers with salinity data")
        
        # Add color attribute
        rivers_salinity['color'] = rivers_salinity['salinity_zone'].map(SALINITY_COLORS)
        rivers_salinity['salinity_range'] = rivers_salinity['salinity_zone'].map(SALINITY_RANGES)
        
        # Keep only essential attributes
        columns_to_keep = ['HYRIV_ID', 'salinity_zone', 'salinity_range', 'color', 'geometry']
        if 'LENGTH_KM' in rivers_salinity.columns:
            columns_to_keep.insert(1, 'LENGTH_KM')
        if 'salinity_ppt' in rivers_salinity.columns:
            columns_to_keep.insert(2, 'salinity_ppt')
        
        rivers_salinity = rivers_salinity[[col for col in columns_to_keep if col in rivers_salinity.columns]]
        
        # Save
        output_file = OPTIMIZED_DIR / 'salinity_rivers.geojson'
        rivers_salinity.to_file(output_file, driver='GeoJSON')
        
        output_size = output_file.stat().st_size / (1024 * 1024)
        print(f"   ✓ Saved: {output_file.name} ({output_size:.1f} MB)")
        
        return rivers_salinity
    else:
        print("   ⚠️ Rivers don't have basin ID - spatial join needed (slow)")
        return None

def create_summary():
    """Create summary of salinity distribution"""
    print("\n" + "="*80)
    print("📊 SALINITY DATA SUMMARY")
    print("="*80)
    
    # Check created files
    basins_file = OPTIMIZED_DIR / 'salinity_basins.geojson'
    rivers_file = OPTIMIZED_DIR / 'salinity_rivers.geojson'
    
    if basins_file.exists():
        basins = gpd.read_file(basins_file)
        print(f"\n✅ Salinity Basins: {len(basins)} polygons")
        print("\n   Distribution:")
        for zone, count in basins['salinity_zone'].value_counts().items():
            color = SALINITY_COLORS[zone]
            range_str = SALINITY_RANGES[zone]
            print(f"   ▣ {zone.capitalize():12} ({range_str:12}) {count:>6,} basins")
        
        size_mb = basins_file.stat().st_size / (1024 * 1024)
        print(f"\n   📦 File size: {size_mb:.1f} MB")
    
    if rivers_file.exists():
        rivers = gpd.read_file(rivers_file)
        print(f"\n✅ Salinity Rivers: {len(rivers)} lines")
        print("\n   Distribution:")
        for zone, count in rivers['salinity_zone'].value_counts().items():
            color = SALINITY_COLORS[zone]
            range_str = SALINITY_RANGES[zone]
            print(f"   ▣ {zone.capitalize():12} ({range_str:12}) {count:>6,} rivers")
        
        size_mb = rivers_file.stat().st_size / (1024 * 1024)
        print(f"\n   📦 File size: {size_mb:.1f} MB")
    
    print("\n" + "="*80)
    print("✅ SALINITY GEOMETRIES CREATED!")
    print("="*80)
    print("\n💡 Next:")
    print("   1. Update map.js to load salinity_basins.geojson and salinity_rivers.geojson")
    print("   2. Color polygons/lines by 'color' attribute")
    print("   3. Show 'salinity_range' in legend")
    print("   4. Make layers toggleable")

def main():
    print("="*80)
    print("🔧 JOIN SALINITY DATA WITH GEOMETRIES")
    print("="*80)
    print("\nThis script fixes the critical issue:")
    print("   Salinity data is POINTS → Need POLYGONS & LINES!")
    print("")
    
    # Load salinity data
    salinity_data = load_salinity_points()
    
    # Join with basins
    basins_salinity = join_salinity_with_basins(salinity_data)
    
    # Join with rivers
    rivers_salinity = join_salinity_with_rivers(salinity_data)
    
    # Create summary
    create_summary()
    
    print("\n✨ Now your map can show:")
    print("   • Basins colored by salinity (polygons)")
    print("   • Rivers colored by salinity (lines)")
    print("   • Salinity ranges in legend")
    print("   • Combined analysis: estuary type + water chemistry!")

if __name__ == '__main__':
    main()
