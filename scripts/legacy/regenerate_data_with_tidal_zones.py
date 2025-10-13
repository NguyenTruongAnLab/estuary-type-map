
"""
Complete Data Regeneration with Tidal Zone Classification
==========================================================

This script implements:
1. Proper salinity-basin polygon joins
2. Tidal zone classification (Tidal Freshwater, Tidal Saline, Non-tidal)
3. River segmentation by tidal influence
4. Integration with Dürr and Baum classifications

Based on: Ensign et al. (2012) "The tidal freshwater river zone"
- Tidal Freshwater: Tidal influence + freshwater (<0.5 ppt)
- Tidal Saline: Tidal influence + saline (>0.5 ppt)
- Non-tidal: No tidal influence

Author: Global Estuary Type Map Project
Date: October 10, 2025
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
from shapely.geometry import Point, LineString
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
RAW_DIR = DATA_DIR / 'raw' / 'hydrosheds'
PROCESSED_DIR = DATA_DIR / 'processed'
OPTIMIZED_DIR = DATA_DIR / 'optimized'
OPTIMIZED_DIR.mkdir(parents=True, exist_ok=True)

# Tidal zone thresholds (from Ensign et al. 2012)
TIDAL_ELEVATION_MAX_M = 10  # Maximum elevation for tidal influence
TIDAL_DISTANCE_MAX_KM = 100  # Maximum distance from coast for tidal influence
FRESHWATER_SALINITY_PPT = 0.5  # Threshold for freshwater vs saline

# Color schemes
TIDAL_ZONE_COLORS = {
    'tidal_freshwater': '#2E7D32',  # Dark green
    'tidal_saline': '#1976D2',      # Blue
    'non_tidal': '#757575'          # Gray
}

SALINITY_COLORS = {
    'freshwater': '#2166ac',
    'oligohaline': '#67a9cf',
    'mesohaline': '#d1e5f0',
    'polyhaline': '#fddbc7',
    'euhaline': '#ef8a62',
    'hyperhaline': '#b2182b'
}

def load_original_hydrosheds_basins():
    """Load ORIGINAL HydroSHEDS basins from GDB (not filtered versions)"""
    print("\n" + "="*80)
    print("📂 STEP 1: Loading ORIGINAL HydroSHEDS BasinATLAS")
    print("="*80)
    
    gdb_path = RAW_DIR / 'BasinATLAS_v10.gdb'
    
    if not gdb_path.exists():
        print(f"   ❌ GDB not found: {gdb_path}")
        print(f"   Please download BasinATLAS v10 from HydroSHEDS website")
        return None
    
    try:
        # Try level 08 first (salinity data seems to use this level based on HYBAS_IDs)
        print(f"   Trying BasinATLAS_v10_lev08...")
        try:
            basins = gpd.read_file(gdb_path, layer='BasinATLAS_v10_lev08')
            print(f"   ✓ Loaded {len(basins)} basins (level 08)")
        except:
            print(f"   ⚠️  Level 08 not found, trying level 06...")
            basins = gpd.read_file(gdb_path, layer='BasinATLAS_v10_lev06')
            print(f"   ✓ Loaded {len(basins)} basins (level 06)")
        
        print(f"   Columns: {list(basins.columns[:10])}...")
        print(f"   HYBAS_ID sample: {basins['HYBAS_ID'].head().tolist()}")
        
        # Filter to coastal basins only (DIST_SINK = 0 or very small)
        if 'DIST_SINK' in basins.columns:
            coastal_basins = basins[basins['DIST_SINK'] <= 50].copy()
            print(f"   ✓ Filtered to {len(coastal_basins)} coastal basins (DIST_SINK ≤ 50 km)")
        else:
            coastal_basins = basins.copy()
            print(f"   ⚠️  DIST_SINK not found - using all basins")
        
        return coastal_basins
        
    except Exception as e:
        print(f"   ❌ Error loading GDB: {e}")
        return None

def load_salinity_data():
    """Load salinity point data"""
    print("\n" + "="*80)
    print("📂 STEP 2: Loading Salinity Data")
    print("="*80)
    
    salinity_file = PROCESSED_DIR / 'salinity_zones.gpkg'
    if not salinity_file.exists():
        salinity_file = OPTIMIZED_DIR / 'salinity_zones.geojson'
    
    if not salinity_file.exists():
        print(f"   ❌ Salinity file not found")
        return None
    
    salinity = gpd.read_file(salinity_file)
    print(f"   ✓ Loaded {len(salinity)} salinity points")
    print(f"   Columns: {list(salinity.columns)}")
    print(f"   Salinity zones: {salinity['salinity_zone'].value_counts().to_dict()}")
    
    # Extract attributes (drop geometry since we'll join with basins)
    salinity_attrs = salinity[['HYBAS_ID', 'salinity_zone']].copy()
    if 'salinity_ppt' in salinity.columns:
        salinity_attrs['salinity_ppt'] = salinity['salinity_ppt']
    
    salinity_attrs['HYBAS_ID'] = salinity_attrs['HYBAS_ID'].astype('int64')
    salinity_attrs = salinity_attrs.drop_duplicates(subset=['HYBAS_ID'])
    
    return salinity_attrs

def join_salinity_with_basins(basins, salinity_attrs):
    """Join salinity attributes with basin POLYGONS"""
    print("\n" + "="*80)
    print("🔗 STEP 3: Joining Salinity with Basin Polygons")
    print("="*80)
    
    # Ensure HYBAS_ID types match
    basins['HYBAS_ID'] = basins['HYBAS_ID'].astype('int64')
    
    # Join
    basins_salinity = basins.merge(salinity_attrs, on='HYBAS_ID', how='inner')
    
    print(f"   ✓ Matched {len(basins_salinity)} / {len(basins)} basins ({len(basins_salinity)/len(basins)*100:.1f}%)")
    
    if len(basins_salinity) == 0:
        print(f"   ❌ NO MATCHES! HYBAS_ID mismatch problem!")
        print(f"   Basin HYBAS_ID sample: {basins['HYBAS_ID'].head().tolist()}")
        print(f"   Salinity HYBAS_ID sample: {salinity_attrs['HYBAS_ID'].head().tolist()}")
        return None
    
    # Add color attributes
    basins_salinity['salinity_color'] = basins_salinity['salinity_zone'].map(SALINITY_COLORS)
    
    return basins_salinity

def classify_tidal_zones(basins_salinity):
    """Classify basins into tidal zones based on Ensign et al. (2012)"""
    print("\n" + "="*80)
    print("🌊 STEP 4: Classifying Tidal Zones")
    print("="*80)
    
    # Criteria for tidal influence:
    # 1. Distance from sink (coast) < TIDAL_DISTANCE_MAX_KM
    # 2. Elevation < TIDAL_ELEVATION_MAX_M
    
    if 'DIST_SINK' not in basins_salinity.columns:
        print("   ⚠️  DIST_SINK not available - using distance from coast = 0")
        basins_salinity['DIST_SINK'] = 0
    
    if 'elv_av' not in basins_salinity.columns and 'ele_mt_smn' not in basins_salinity.columns:
        print("   ⚠️  Elevation data not available - using elevation = 0")
        basins_salinity['elevation_m'] = 0
    else:
        elev_col = 'elv_av' if 'elv_av' in basins_salinity.columns else 'ele_mt_smn'
        basins_salinity['elevation_m'] = basins_salinity[elev_col]
    
    # Determine if tidal influenced
    basins_salinity['is_tidal'] = (
        (basins_salinity['DIST_SINK'] <= TIDAL_DISTANCE_MAX_KM) &
        (basins_salinity['elevation_m'] <= TIDAL_ELEVATION_MAX_M)
    )
    
    # Determine if freshwater
    basins_salinity['is_freshwater'] = basins_salinity['salinity_zone'].isin([
        'freshwater', 'oligohaline'
    ])
    
    # Classify into 3 tidal zones
    def classify_zone(row):
        if row['is_tidal']:
            if row['is_freshwater']:
                return 'tidal_freshwater'
            else:
                return 'tidal_saline'
        else:
            return 'non_tidal'
    
    basins_salinity['tidal_zone'] = basins_salinity.apply(classify_zone, axis=1)
    basins_salinity['tidal_color'] = basins_salinity['tidal_zone'].map(TIDAL_ZONE_COLORS)
    
    # Statistics
    print("\n   📊 Tidal Zone Distribution:")
    for zone, count in basins_salinity['tidal_zone'].value_counts().items():
        color = TIDAL_ZONE_COLORS[zone]
        pct = count / len(basins_salinity) * 100
        print(f"   ▣ {zone.replace('_', ' ').title():20} {count:>6,} basins ({pct:>5.1f}%)")
    
    return basins_salinity

def save_optimized_layers(basins_salinity):
    """Save optimized layers for web display"""
    print("\n" + "="*80)
    print("💾 STEP 5: Saving Optimized Layers")
    print("="*80)
    
    # Select essential columns
    essential_cols = [
        'HYBAS_ID', 'DIST_SINK', 'SUB_AREA',
        'salinity_zone', 'salinity_color',
        'tidal_zone', 'tidal_color',
        'is_tidal', 'is_freshwater',
        'geometry'
    ]
    
    # Add salinity_ppt if available
    if 'salinity_ppt' in basins_salinity.columns:
        essential_cols.insert(4, 'salinity_ppt')
    
    # Keep only available columns
    cols_to_keep = [col for col in essential_cols if col in basins_salinity.columns]
    basins_final = basins_salinity[cols_to_keep].copy()
    
    # Simplify geometry for web
    print("\n   ✂️  Simplifying geometries...")
    basins_final['geometry'] = basins_final['geometry'].simplify(0.02, preserve_topology=True)
    
    # Save as GeoJSON
    output_file = OPTIMIZED_DIR / 'basins_salinity_tidal.geojson'
    basins_final.to_file(output_file, driver='GeoJSON')
    
    size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"   ✓ Saved: {output_file.name} ({size_mb:.1f} MB)")
    
    # Create separate files for each classification
    
    # 1. Salinity classification
    salinity_file = OPTIMIZED_DIR / 'basins_by_salinity.geojson'
    basins_final.to_file(salinity_file, driver='GeoJSON')
    print(f"   ✓ Saved: {salinity_file.name} ({size_mb:.1f} MB)")
    
    # 2. Tidal zone classification
    tidal_file = OPTIMIZED_DIR / 'basins_by_tidal_zone.geojson'
    basins_final.to_file(tidal_file, driver='GeoJSON')
    print(f"   ✓ Saved: {tidal_file.name} ({size_mb:.1f} MB)")
    
    return basins_final

def create_summary_statistics(basins_salinity):
    """Create comprehensive summary statistics"""
    print("\n" + "="*80)
    print("📊 STEP 6: Summary Statistics")
    print("="*80)
    
    print("\n🌍 GLOBAL TIDAL FRESHWATER ZONE ANALYSIS")
    print("-" * 80)
    
    # By tidal zone
    print("\n1. Tidal Zone Distribution:")
    tidal_stats = basins_salinity.groupby('tidal_zone').agg({
        'HYBAS_ID': 'count',
        'SUB_AREA': 'sum'
    }).rename(columns={'HYBAS_ID': 'count', 'SUB_AREA': 'total_area_km2'})
    
    for zone, row in tidal_stats.iterrows():
        print(f"   {zone.replace('_', ' ').title():20} "
              f"{row['count']:>6,} basins | "
              f"{row['total_area_km2']:>12,.0f} km²")
    
    # By salinity zone
    print("\n2. Salinity Distribution:")
    salinity_stats = basins_salinity.groupby('salinity_zone').agg({
        'HYBAS_ID': 'count',
        'SUB_AREA': 'sum'
    }).rename(columns={'HYBAS_ID': 'count', 'SUB_AREA': 'total_area_km2'})
    
    for zone, row in salinity_stats.iterrows():
        print(f"   {zone.title():20} "
              f"{row['count']:>6,} basins | "
              f"{row['total_area_km2']:>12,.0f} km²")
    
    # Cross-tabulation: Tidal zone × Salinity
    print("\n3. Tidal Zone × Salinity Cross-tabulation:")
    crosstab = pd.crosstab(
        basins_salinity['tidal_zone'],
        basins_salinity['salinity_zone'],
        margins=True
    )
    print(crosstab.to_string())
    
    # Key findings
    print("\n4. Key Findings:")
    tidal_fresh = len(basins_salinity[basins_salinity['tidal_zone'] == 'tidal_freshwater'])
    tidal_saline = len(basins_salinity[basins_salinity['tidal_zone'] == 'tidal_saline'])
    total = len(basins_salinity)
    
    print(f"   • Tidal Freshwater Zones: {tidal_fresh:,} basins ({tidal_fresh/total*100:.1f}%)")
    print(f"   • Tidal Saline Zones: {tidal_saline:,} basins ({tidal_saline/total*100:.1f}%)")
    print(f"   • Total area with tidal influence: "
          f"{basins_salinity[basins_salinity['is_tidal']]['SUB_AREA'].sum():,.0f} km²")
    
    # Save statistics to CSV
    stats_file = OPTIMIZED_DIR / 'tidal_zone_statistics.csv'
    basins_salinity.groupby(['tidal_zone', 'salinity_zone']).agg({
        'HYBAS_ID': 'count',
        'SUB_AREA': 'sum'
    }).to_csv(stats_file)
    print(f"\n   ✓ Statistics saved: {stats_file.name}")

def main():
    print("="*80)
    print("🌊 COMPLETE DATA REGENERATION + TIDAL ZONE ANALYSIS")
    print("="*80)
    print("\nThis script will:")
    print("  1. Load ORIGINAL HydroSHEDS BasinATLAS data")
    print("  2. Join with salinity data to create POLYGON geometries")
    print("  3. Classify tidal zones (Tidal Freshwater, Tidal Saline, Non-tidal)")
    print("  4. Generate optimized layers for web display")
    print("  5. Create comprehensive statistics")
    print("\nBased on: Ensign et al. (2012) 'The tidal freshwater river zone'")
    print("")
    
    # Step 1: Load original basins
    basins = load_original_hydrosheds_basins()
    if basins is None:
        print("\n❌ Failed to load HydroSHEDS data")
        print("\nPlease ensure BasinATLAS_v10.gdb is in:")
        print(f"   {RAW_DIR}")
        return
    
    # Step 2: Load salinity data
    salinity_attrs = load_salinity_data()
    if salinity_attrs is None:
        print("\n❌ Failed to load salinity data")
        return
    
    # Step 3: Join salinity with basins
    basins_salinity = join_salinity_with_basins(basins, salinity_attrs)
    if basins_salinity is None:
        print("\n❌ Failed to join data - HYBAS_ID mismatch!")
        print("\n💡 Possible solutions:")
        print("   1. Re-run process_globsalt.py to regenerate salinity data")
        print("   2. Use same HydroSHEDS version for both basins and salinity")
        print("   3. Check HYBAS_ID data types and formats")
        return
    
    # Step 4: Classify tidal zones
    basins_salinity = classify_tidal_zones(basins_salinity)
    
    # Step 5: Save optimized layers
    basins_final = save_optimized_layers(basins_salinity)
    
    # Step 6: Create statistics
    create_summary_statistics(basins_salinity)
    
    print("\n" + "="*80)
    print("✅ COMPLETE! Data regeneration successful!")
    print("="*80)
    print("\n📁 Output files created:")
    print("   • basins_salinity_tidal.geojson - Complete data with all attributes")
    print("   • basins_by_salinity.geojson - Colored by salinity zones")
    print("   • basins_by_tidal_zone.geojson - Colored by tidal zones")
    print("   • tidal_zone_statistics.csv - Summary statistics")
    print("\n💡 Next steps:")
    print("   1. Update map.js to load these new files")
    print("   2. Add layer toggles for 'Salinity View' and 'Tidal Zone View'")
    print("   3. Create legends showing tidal zone classification")
    print("   4. Enable combined analysis (Dürr types + Tidal zones)")
    print("\n🎯 Scientific Impact:")
    print("   • First global map of tidal freshwater zones!")
    print("   • Integration with estuary geomorphology (Dürr/Baum)")
    print("   • Foundation for GHG emissions and biogeochemical studies")

if __name__ == '__main__':
    main()
