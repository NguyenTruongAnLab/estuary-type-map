"""
Complete GRIT Processing Pipeline - All Steps in One Script
============================================================

Process GRIT v0.6 data end-to-end: segments → reaches → surface areas.
Handles all Asia (AS) files in the GRIT folder.

Processing Steps:
1. Load & classify segments (topology + basin/salinity classification)
2. Load & classify reaches (inherit from segments + add width data)
3. Calculate surface areas (buffer by width + intersect with OSM water)

Usage:
    python scripts/process_grit_complete.py --region asia
    python scripts/process_grit_complete.py --region asia --skip-reaches
    python scripts/process_grit_complete.py --region asia --skip-surface-areas
"""

import sys
import time
import warnings
from pathlib import Path
from typing import Optional, Dict

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import LineString
from tqdm import tqdm

warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

tqdm.pandas()

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
GRIT_DIR = BASE_DIR / 'data' / 'raw' / 'GRIT-Michel_2025'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
OUTPUT_DIR = BASE_DIR / 'data' / 'processed'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# GRIT regions available (all regions!)
GRIT_REGIONS = {
    'AF': 'Africa',
    'AS': 'Asia (excl. Siberia)',
    'EU': 'Europe',
    'NA': 'North America',
    'SA': 'South America',
    'SI': 'Siberia',
    'SP': 'South Pacific/Australia'
}

def get_grit_files(region_code: str) -> Dict[str, Path]:
    """Get GRIT file paths for a specific region"""
    return {
        'segments': GRIT_DIR / f'GRITv06_segments_{region_code}_EPSG4326.gpkg',
        'reaches': GRIT_DIR / f'GRITv06_reaches_{region_code}_EPSG4326.gpkg',
        'catchments': GRIT_DIR / f'GRITv06_component_catchments_{region_code}_EPSG4326.gpkg'
    }

# GlobSalt salinity zones (if available)
SALINITY_FILE = PROCESSED_DIR / 'salinity_zones.gpkg'

# OSM water polygons (if available)
OSM_WATER_FILE = PROCESSED_DIR / 'osm_water_polygons_asia.gpkg'
# Alternative: use raw converted file directly
OSM_WATER_RAW = BASE_DIR / 'data' / 'raw' / 'OSM-Water-Layer-Yamazaki_2021' / 'OSM_WaterLayer_POLYGONS.gpkg'

# Processing parameters
MIN_STRAHLER_ORDER = None  # None = include all orders
SIMPLIFY_TOLERANCE = 0.0001  # degrees (~11m at equator)

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================
def print_section(title: str, step_num: Optional[int] = None):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    if step_num:
        print(f"STEP {step_num}: {title}")
    else:
        print(f"{title}")
    print(f"{'='*80}")

def has_valid_coordinates(geom) -> bool:
    """Check if geometry has valid coordinates (NaN/Inf check)"""
    if geom is None or geom.is_empty:
        return False
    try:
        from shapely import get_coordinates
        coords = get_coordinates(geom)
        if coords.size == 0:
            return False
        return np.all(np.isfinite(coords))
    except Exception:
        return False

def optimize_memory(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Optimize GeoDataFrame memory usage"""
    original_mem = gdf.memory_usage(deep=True).sum() / 1024**2
    
    for col in gdf.select_dtypes(include=['int64']).columns:
        gdf[col] = pd.to_numeric(gdf[col], downcast='integer')
    
    for col in gdf.select_dtypes(include=['float64']).columns:
        gdf[col] = pd.to_numeric(gdf[col], downcast='float')
    
    new_mem = gdf.memory_usage(deep=True).sum() / 1024**2
    reduction = (1 - new_mem / original_mem) * 100 if original_mem > 0 else 0
    print(f"    Memory optimized: {original_mem:.1f} MB → {new_mem:.1f} MB ({reduction:.1f}% reduction)")
    
    return gdf

def save_metadata(data: Dict, filename: Path):
    """Save metadata to JSON file"""
    import json
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Metadata saved: {filename.name}")

# ==============================================================================
# STEP 1: PROCESS SEGMENTS (Classification)
# ==============================================================================
def process_segments() -> Optional[gpd.GeoDataFrame]:
    """
    Load and classify GRIT segments using native catchments.
    This is the foundation - all classification happens here.
    """
    print_section("LOAD & CLASSIFY SEGMENTS", 1)
    
    # Load segments
    segments_file = GRIT_FILES['segments']
    
    if not segments_file.exists():
        print(f"❌ Error: Segments file not found: {segments_file}")
        return None
    
    print(f"📂 Loading: {segments_file.name}")
    start_time = time.time()
    
    segments = gpd.read_file(segments_file, layer='lines', engine='pyogrio')
    elapsed = time.time() - start_time
    
    print(f"✓ Loaded {len(segments):,} segments in {elapsed:.1f} seconds")
    print(f"    Total length: {segments['length'].sum()/1e6:.0f},000 km")
    print(f"    Strahler orders: {segments['strahler_order'].min()}-{segments['strahler_order'].max()}")
    
    # Validate geometries
    print(f"\n🔍 Validating geometries...")
    segments = segments[segments.geometry.notnull()].copy()
    
    print(f"    Checking coordinates...")
    valid_mask = segments.geometry.progress_apply(has_valid_coordinates)
    removed = (~valid_mask).sum()
    if removed > 0:
        print(f"    ⚠️  Removed {removed} segments with invalid coordinates")
    segments = segments[valid_mask].copy()
    
    print(f"✓ Valid segments: {len(segments):,}")
    
    # Filter by stream order (optional)
    if MIN_STRAHLER_ORDER:
        original = len(segments)
        segments = segments[segments['strahler_order'] >= MIN_STRAHLER_ORDER].copy()
        print(f"    Filtered to order >={MIN_STRAHLER_ORDER}: {len(segments):,} ({len(segments)/original*100:.1f}%)")
    
    # Classify by catchment type
    print(f"\n🏔️  Classifying by catchment type...")
    catchments_file = GRIT_FILES['catchments']
    
    if not catchments_file.exists():
        print(f"⚠️  Catchments file not found: {catchments_file}")
        print(f"    All segments classified as 'Unclassified'")
        segments['system_type'] = 'Unclassified'
        segments['is_coastal'] = 0
    else:
        print(f"📂 Loading: {catchments_file.name}")
        catchments = gpd.read_file(catchments_file, engine='pyogrio')
        print(f"✓ Loaded {len(catchments):,} catchments")
        
        # Classify catchments
        def classify_catchment(row):
            return 'Estuarine' if row.get('is_coastal', 0) == 1 else 'Non-Tidal Riverine'
        
        catchments['system_type'] = catchments.apply(classify_catchment, axis=1)
        
        print(f"    Catchment types:")
        for sys_type, count in catchments['system_type'].value_counts().items():
            print(f"        {sys_type}: {count:,}")
        
        # Join with segments (attribute join - fast!)
        print(f"\n    Joining via catchment_id (attribute join)...")
        print(f"    DEBUG: Checking catchment_id values...")
        print(f"        Segments have catchment_id: {segments['catchment_id'].notna().sum():,} / {len(segments):,}")
        print(f"        Sample segment catchment_ids: {segments['catchment_id'].dropna().head(10).tolist()}")
        print(f"        Sample catchment global_ids: {catchments['global_id'].head(10).tolist()}")
        
        start_time = time.time()
        
        segments_before = len(segments)
        segments = segments.merge(
            catchments[['global_id', 'system_type', 'is_coastal', 'area']],
            left_on='catchment_id',
            right_on='global_id',
            how='left',
            suffixes=('', '_catchment')
        )
        
        elapsed = time.time() - start_time
        print(f"✓ Join complete in {elapsed:.1f} seconds")
        
        # Check join success
        matched = segments['system_type'].notna().sum()
        print(f"    Matched: {matched:,} / {segments_before:,} ({matched/segments_before*100:.1f}%)")
        
        # Fill missing
        segments['system_type'] = segments['system_type'].fillna('Unclassified')
        segments['is_coastal'] = segments['is_coastal'].fillna(0)
        
        # Clean up
        if 'global_id_catchment' in segments.columns:
            segments = segments.drop(columns=['global_id_catchment'])
    
    # Classify by salinity zone
    print(f"\n💧 Classifying by salinity zone...")
    
    if not SALINITY_FILE.exists():
        print(f"⚠️  Salinity file not found: {SALINITY_FILE}")
        print(f"    All segments classified as 'Unknown'")
        segments['salinity_zone'] = 'Unknown'
    else:
        print(f"📂 Loading: {SALINITY_FILE.name}")
        salinity = gpd.read_file(SALINITY_FILE, engine='pyogrio')
        print(f"✓ Loaded {len(salinity):,} salinity zones")
        
        # Spatial join
        print(f"    Performing spatial join...")
        start_time = time.time()
        
        segments = gpd.sjoin(
            segments,
            salinity[['zone_type', 'salinity_mean_psu', 'geometry']],
            how='left',
            predicate='intersects'
        )
        
        elapsed = time.time() - start_time
        print(f"✓ Join complete in {elapsed:.1f} seconds")
        
        # Classify
        def classify_salinity(row):
            sal = row.get('salinity_mean_psu', np.nan)
            if pd.isna(sal):
                return 'Non-Tidal'
            elif sal < 0.5:
                return 'TFZ'
            else:
                return 'Saline'
        
        segments['salinity_zone'] = segments.apply(classify_salinity, axis=1)
        segments = segments.drop_duplicates(subset=['global_id'])
    
    # Summary statistics
    print(f"\n📊 Classification Summary:")
    print(f"    By system type:")
    for sys_type, count in segments['system_type'].value_counts().items():
        length_km = segments[segments['system_type'] == sys_type]['length'].sum() / 1000
        print(f"        {sys_type}: {count:,} segments ({length_km:,.0f} km)")
    
    if 'salinity_zone' in segments.columns:
        print(f"    By salinity zone:")
        for zone, count in segments['salinity_zone'].value_counts().items():
            length_km = segments[segments['salinity_zone'] == zone]['length'].sum() / 1000
            print(f"        {zone}: {count:,} segments ({length_km:,.0f} km)")
    
    # Export
    print(f"\n💾 Exporting segments...")
    output_file = OUTPUT_DIR / 'rivers_grit_segments_classified_asia.gpkg'
    
    segments = optimize_memory(segments)
    segments.to_file(output_file, driver='GPKG', layer='rivers', engine='pyogrio')
    
    file_size = output_file.stat().st_size / (1024**2)
    print(f"✓ Exported: {output_file.name} ({file_size:.1f} MB)")
    
    return segments

# ==============================================================================
# STEP 2: PROCESS REACHES (Inherit Classification + Width Data)
# ==============================================================================
def process_reaches(segments: gpd.GeoDataFrame) -> Optional[gpd.GeoDataFrame]:
    """
    Load GRIT reaches and inherit classification from segments.
    Reaches have actual width data (grwl_width_median) for surface area calculations.
    """
    print_section("LOAD & CLASSIFY REACHES (with Width Data)", 2)
    
    reaches_file = GRIT_FILES['reaches']
    
    if not reaches_file.exists():
        print(f"❌ Error: Reaches file not found: {reaches_file}")
        print(f"    Expected: {reaches_file}")
        return None
    
    print(f"📂 Loading: {reaches_file.name}")
    print(f"    ⚠️  This may take 5-10 minutes (large dataset!)...")
    start_time = time.time()
    
    reaches = gpd.read_file(reaches_file, layer='lines', engine='pyogrio')
    elapsed = time.time() - start_time
    
    print(f"✓ Loaded {len(reaches):,} reaches in {elapsed:.1f} seconds")
    print(f"    Total length: {reaches['length'].sum()/1e6:.0f},000 km")
    
    # Check for width data
    if 'grwl_width_median' in reaches.columns:
        has_width = reaches['grwl_width_median'].notna().sum()
        print(f"    Width data: {has_width:,} reaches ({has_width/len(reaches)*100:.1f}%)")
        print(f"    Width range: {reaches['grwl_width_median'].min():.1f} - {reaches['grwl_width_median'].max():.1f} m")
    else:
        print(f"    ⚠️  No width data found in reaches!")
    
    # Inherit classification from segments
    print(f"\n🔗 Inheriting classification from segments...")
    print(f"    Joining via segment_id...")
    
    # Prepare segment classification
    segment_classification = segments[[
        'global_id', 'system_type', 'salinity_zone', 'is_coastal', 'name', 'domain'
    ]].copy()
    
    segment_classification = segment_classification.drop_duplicates(subset=['global_id'])
    
    # Join
    start_time = time.time()
    reaches = reaches.merge(
        segment_classification,
        left_on='segment_id',
        right_on='global_id',
        how='left',
        suffixes=('', '_segment')
    )
    elapsed = time.time() - start_time
    
    print(f"✓ Join complete in {elapsed:.1f} seconds")
    
    # Fill missing
    reaches['system_type'] = reaches['system_type'].fillna('Unclassified')
    reaches['salinity_zone'] = reaches['salinity_zone'].fillna('Unknown')
    
    # Clean up
    if 'global_id_segment' in reaches.columns:
        reaches = reaches.drop(columns=['global_id_segment'])
    
    # Summary
    print(f"\n📊 Reaches Classification Summary:")
    print(f"    Total reaches: {len(reaches):,}")
    classified = reaches[reaches['system_type'] != 'Unclassified']
    print(f"    Classified: {len(classified):,} ({len(classified)/len(reaches)*100:.1f}%)")
    
    print(f"    By system type:")
    for sys_type, count in reaches['system_type'].value_counts().items():
        print(f"        {sys_type}: {count:,}")
    
    # Export
    print(f"\n💾 Exporting reaches...")
    output_file = OUTPUT_DIR / 'rivers_grit_reaches_classified_asia.gpkg'
    
    reaches = optimize_memory(reaches)
    reaches.to_file(output_file, driver='GPKG', layer='rivers', engine='pyogrio')
    
    file_size = output_file.stat().st_size / (1024**2)
    print(f"✓ Exported: {output_file.name} ({file_size:.1f} MB)")
    
    return reaches

# ==============================================================================
# STEP 3: INTERSECT WITH OSM WATER POLYGONS (Correct Approach!)
# ==============================================================================
def intersect_with_osm_water(reaches: gpd.GeoDataFrame) -> Optional[pd.DataFrame]:
    """
    Calculate water surface areas by intersecting GRIT reaches with 
    ACTUAL OSM water body polygons (not buffering!).
    
    This is the correct approach for polygon-based surface area calculation.
    """
    print_section("INTERSECT WITH OSM WATER POLYGONS", 3)
    
    # Check if OSM water polygons exist
    osm_file = None
    if OSM_WATER_FILE.exists():
        osm_file = OSM_WATER_FILE
        print(f"\ud83d\udcc2 Found processed OSM water: {OSM_WATER_FILE.name}")
    elif OSM_WATER_RAW.exists():
        osm_file = OSM_WATER_RAW
        print(f"\ud83d\udcc2 Found raw converted OSM water: {OSM_WATER_RAW.name}")
    else:
        print(f"\u274c Error: OSM water polygons not found!")
        print(f"    Tried:")
        print(f"      1. {OSM_WATER_FILE}")
        print(f"      2. {OSM_WATER_RAW}")
        print(f"\n\ud83d\udca1 You need to convert OSM PBF first:")
        print(f"    python scripts/convert_pbf_2.py")
        print(f"\n\u26a0\ufe0f  Skipping surface area calculation.")
        print(f"    However, you can still use the classified reaches for analysis.")
        return None
    
    print(f"\ud83d\udcc2 Loading OSM water polygons from {osm_file.name}...")
    start_time = time.time()
    
    try:
        osm_water = gpd.read_file(osm_file, engine='pyogrio')
        elapsed = time.time() - start_time
        print(f"\u2713 Loaded {len(osm_water):,} water polygons in {elapsed:.1f} seconds")
        
        # Validate geometries
        valid_geom = osm_water[osm_water.geometry.notna() & osm_water.geometry.is_valid]
        if len(valid_geom) == 0:
            print(f"\u274c Error: No valid geometries in OSM water!")
            return None
        elif len(valid_geom) < len(osm_water):
            print(f"\u26a0\ufe0f  Warning: {len(osm_water) - len(valid_geom):,} invalid geometries removed")
            osm_water = valid_geom
        
        print(f"\u2713 Valid geometries: {len(osm_water):,}")
        
    except Exception as e:
        print(f"\u274c Error loading OSM water: {e}")
        return None
    
    # Ensure same CRS
    if reaches.crs != osm_water.crs:
        print(f"    Converting OSM water to match GRIT CRS...")
        osm_water = osm_water.to_crs(reaches.crs)
    
    # Spatial intersection
    print(f"\n� Intersecting GRIT reaches with OSM water polygons...")
    print(f"    This may take 10-20 minutes for large datasets...")
    
    start_time = time.time()
    
    # Convert to equal-area projection for accurate area calculation
    reaches_ea = reaches.to_crs('EPSG:6933')
    osm_water_ea = osm_water.to_crs('EPSG:6933')
    
    # Intersection
    water_reaches = gpd.overlay(
        reaches_ea,
        osm_water_ea,
        how='intersection',
        keep_geom_type=False
    )
    
    elapsed = time.time() - start_time
    print(f"✓ Intersection complete in {elapsed:.1f} seconds")
    print(f"    Result: {len(water_reaches):,} water polygons matched to reaches")
    
    # Calculate surface areas
    print(f"\n📐 Calculating surface areas...")
    water_reaches['area_km2'] = water_reaches.geometry.area / 1e6
    
    # Summary by classification
    print(f"\n📊 Surface Area Summary (from OSM water polygons):")
    
    total_area = water_reaches['area_km2'].sum()
    print(f"    Total water surface area: {total_area:,.1f} km²")
    
    # By system type
    print(f"\n    By system type:")
    for sys_type in water_reaches['system_type'].unique():
        subset = water_reaches[water_reaches['system_type'] == sys_type]
        area = subset['area_km2'].sum()
        print(f"        {sys_type}: {area:,.1f} km² ({area/total_area*100:.1f}%)")
    
    # By salinity zone
    if 'salinity_zone' in water_reaches.columns:
        print(f"\n    By salinity zone:")
        for zone in water_reaches['salinity_zone'].unique():
            subset = water_reaches[water_reaches['salinity_zone'] == zone]
            area = subset['area_km2'].sum()
            print(f"        {zone}: {area:,.1f} km² ({area/total_area*100:.1f}%)")
    
    # Export results
    print(f"\n💾 Exporting results...")
    
    # Convert back to WGS84 for export
    water_reaches_wgs84 = water_reaches.to_crs('EPSG:4326')
    
    output_file = OUTPUT_DIR / 'rivers_grit_water_polygons_asia.gpkg'
    water_reaches_wgs84 = optimize_memory(water_reaches_wgs84)
    water_reaches_wgs84.to_file(output_file, driver='GPKG', layer='water', engine='pyogrio')
    
    file_size = output_file.stat().st_size / (1024**2)
    print(f"✓ Exported: {output_file.name} ({file_size:.1f} MB)")
    
    # Create summary statistics
    summary_stats = []
    
    for sys_type in water_reaches['system_type'].unique():
        for zone in water_reaches.get('salinity_zone', pd.Series(['Unknown'])).unique():
            subset = water_reaches[
                (water_reaches['system_type'] == sys_type) & 
                (water_reaches.get('salinity_zone', 'Unknown') == zone)
            ]
            
            if len(subset) > 0:
                summary_stats.append({
                    'system_type': sys_type,
                    'salinity_zone': zone,
                    'n_polygons': len(subset),
                    'total_area_km2': subset['area_km2'].sum(),
                    'mean_area_km2': subset['area_km2'].mean(),
                    'median_area_km2': subset['area_km2'].median()
                })
    
    summary_df = pd.DataFrame(summary_stats)
    
    # Export summary
    summary_file = OUTPUT_DIR / 'rivers_grit_surface_area_summary_asia.csv'
    summary_df.to_csv(summary_file, index=False)
    print(f"✓ Summary exported: {summary_file.name}")
    
    return summary_df

# ==============================================================================
# MAIN PROCESSING PIPELINE
# ==============================================================================
def main(skip_reaches: bool = False, skip_surface_areas: bool = False):
    """
    Complete GRIT processing pipeline for Asia.
    
    Args:
        skip_reaches: Skip reaches processing
        skip_surface_areas: Skip surface area calculations
    """
    script_start = time.time()
    
    print("\n" + "="*80)
    print("COMPLETE GRIT PROCESSING PIPELINE - ASIA")
    print("="*80)
    print(f"Region: Asia (AS files)")
    print(f"Started: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📁 Input files:")
    for name, path in GRIT_FILES.items():
        status = "✓" if path.exists() else "✗"
        print(f"    {status} {name}: {path.name}")
    
    # Step 1: Process segments
    segments = process_segments()
    if segments is None:
        print(f"\n❌ Failed to process segments. Exiting.")
        return 1
    
    # Step 2: Process reaches (optional)
    if not skip_reaches:
        reaches = process_reaches(segments)
        if reaches is None:
            print(f"\n⚠️  Failed to process reaches. Continuing without reach data.")
            reaches = None
    else:
        print(f"\n⏭️  Skipping reaches processing (--skip-reaches flag)")
        reaches = None
    
    # Step 3: Calculate surface areas (optional)
    if not skip_surface_areas and reaches is not None:
        summary = intersect_with_osm_water(reaches)
        if summary is None:
            print(f"\n⚠️  Failed to calculate surface areas (OSM water polygons not available).")
    elif skip_surface_areas:
        print(f"\n⏭️  Skipping surface area calculations (--skip-surface-areas flag)")
    elif reaches is None:
        print(f"\n⏭️  Skipping surface areas (no reaches data)")
    
    # Final summary
    total_time = time.time() - script_start
    
    print("\n" + "="*80)
    print("✅ PROCESSING COMPLETE")
    print("="*80)
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"\n📂 Output files:")
    print(f"    ✓ rivers_grit_segments_classified_asia.gpkg")
    if not skip_reaches and reaches is not None:
        print(f"    ✓ rivers_grit_reaches_classified_asia.gpkg")
    if not skip_surface_areas and reaches is not None:
        print(f"    ✓ rivers_grit_water_polygons_asia.gpkg (intersected with OSM)")
        print(f"    ✓ rivers_grit_surface_area_summary_asia.csv")
    
    print(f"\n💡 Next steps:")
    print(f"   1. Review output files in: {OUTPUT_DIR}")
    print(f"   2. Open buffered reaches in QGIS to visualize")
    print(f"   3. Use summary CSV for statistics and validation")
    print(f"   4. Run for other regions (when ready)")
    
    return 0

# ==============================================================================
# COMMAND LINE INTERFACE
# ==============================================================================
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Complete GRIT processing pipeline for Asia',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process everything (segments + reaches + surface areas)
  python scripts/process_grit_complete.py
  
  # Process only segments
  python scripts/process_grit_complete.py --skip-reaches --skip-surface-areas
  
  # Process segments and reaches only
  python scripts/process_grit_complete.py --skip-surface-areas
        """
    )
    
    parser.add_argument(
        '--skip-reaches',
        action='store_true',
        help='Skip reaches processing (only process segments)'
    )
    
    parser.add_argument(
        '--skip-surface-areas',
        action='store_true',
        help='Skip surface area calculations'
    )
    
    args = parser.parse_args()
    
    sys.exit(main(
        skip_reaches=args.skip_reaches,
        skip_surface_areas=args.skip_surface_areas
    ))
