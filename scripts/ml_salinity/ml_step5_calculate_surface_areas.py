"""
STEP 5: Calculate Water Body Surface Areas by Salinity Class
==============================================================

GOAL: Connect ML salinity predictions to actual water surface areas for 
      biogeochemical budgeting (GHG emissions, carbon fluxes, nutrient cycles)

WORKFLOW:
1. Load ML-classified river segments (all regions)
2. Join with OSM water polygons OR GRIT surface areas
3. Calculate surface area by salinity class
4. Generate global summary statistics
5. Export results for biogeochemical models

INPUTS:
- ML predictions: data/processed/ml_classified_hybrid/segments_classified_*.gpkg
- Water polygons: OSM Water Layer (Yamazaki 2018) OR GRIT surface_area attribute

OUTPUTS:
- Global surface area by salinity class (CSV)
- Regional breakdown (GeoPackage)
- Summary statistics for publications

SCIENTIFIC RATIONALE:
- GHG emissions scale with surface area (Cole et al. 2007)
- Different salinity zones have different biogeochemistry
- Direct polygon measurement > statistical extrapolation

Usage:
    python scripts/ml_salinity/ml_step5_calculate_surface_areas.py --all-regions
    python scripts/ml_salinity/ml_step5_calculate_surface_areas.py --region AS --use-osm
"""

import sys
import argparse
import warnings
import pandas as pd
import geopandas as gpd
from pathlib import Path
import numpy as np
from datetime import datetime

warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
ML_DIR = PROCESSED_DIR / 'ml_classified_hybrid'
OSM_DIR = BASE_DIR / 'data' / 'raw' / 'OSM-Water-Layer-Yamazaki_2021'
OUTPUT_DIR = PROCESSED_DIR / 'surface_areas_by_salinity'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GRIT_REGIONS = ['AF', 'AS', 'EU', 'NA', 'SA', 'SI', 'SP']

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")

# ==============================================================================
# APPROACH 1: Use GRIT Surface Area Attribute (FAST!)
# ==============================================================================

def calculate_areas_from_grit(region_code: str) -> pd.DataFrame:
    """
    Calculate surface areas using GRIT's pre-calculated surface_area attribute
    
    ADVANTAGE: Fast, no need to load/process OSM polygons
    LIMITATION: GRIT surface areas are estimates, not actual water polygons
    """
    print_section(f"APPROACH 1: GRIT Surface Areas - {region_code}")
    
    # Load ML-classified segments
    classified_file = ML_DIR / f'segments_classified_{region_code.lower()}.gpkg'
    
    if not classified_file.exists():
        print(f"❌ No classified segments found: {classified_file.name}")
        return None
    
    print(f"\n📂 Loading classified segments...")
    segments = gpd.read_file(classified_file)
    print(f"✅ Loaded {len(segments):,} segments")
    
    # Check if surface_area exists
    if 'surface_area' not in segments.columns:
        print(f"⚠️  No surface_area attribute in GRIT data!")
        print(f"   Attempting to load from original GRIT segments...")
        
        # Try to load surface_area from original GRIT
        grit_file = PROCESSED_DIR / f'rivers_grit_segments_classified_{region_code.lower()}.gpkg'
        if grit_file.exists():
            grit_orig = gpd.read_file(grit_file, columns=['global_id', 'surface_area'])
            segments = segments.merge(grit_orig[['global_id', 'surface_area']], 
                                     on='global_id', how='left')
        else:
            print(f"❌ Cannot find surface_area data!")
            return None
    
    # Calculate areas by salinity class
    print(f"\n📊 Calculating surface areas by salinity class...")
    
    # Get ML prediction column
    pred_col = 'ml_predicted_class'
    if pred_col not in segments.columns:
        print(f"❌ No ML predictions found!")
        return None
    
    # Group by salinity class
    area_summary = segments.groupby(pred_col).agg({
        'global_id': 'count',
        'surface_area': ['sum', 'mean', 'std', 'min', 'max']
    }).round(2)
    
    area_summary.columns = ['_'.join(col).strip() for col in area_summary.columns.values]
    area_summary = area_summary.reset_index()
    area_summary['region'] = region_code
    
    print(f"\n✅ Surface Area Summary:")
    print(area_summary.to_string())
    
    return area_summary

# ==============================================================================
# APPROACH 2: Join with OSM Water Polygons (PRECISE!)
# ==============================================================================

def calculate_areas_from_osm(region_code: str) -> pd.DataFrame:
    """
    Calculate surface areas by joining ML predictions with OSM water polygons
    
    ADVANTAGE: Actual water polygon areas (most accurate!)
    LIMITATION: Requires OSM data processing, slower
    """
    print_section(f"APPROACH 2: OSM Water Polygons - {region_code}")
    
    # Load ML-classified segments
    classified_file = ML_DIR / f'segments_classified_{region_code.lower()}.gpkg'
    
    if not classified_file.exists():
        print(f"❌ No classified segments found: {classified_file.name}")
        return None
    
    print(f"\n📂 Loading classified segments...")
    segments = gpd.read_file(classified_file)
    print(f"✅ Loaded {len(segments):,} segments")
    
    # Look for OSM water polygons
    print(f"\n📂 Looking for OSM water polygons...")
    
    # Check if OSM data exists for this region
    osm_file = PROCESSED_DIR / f'osm_water_{region_code.lower()}.gpkg'
    
    if not osm_file.exists():
        print(f"⚠️  OSM water polygons not yet processed for {region_code}")
        print(f"   Use Approach 1 (GRIT surface areas) instead")
        print(f"   Or run: python scripts/process_osm_water.py --region {region_code}")
        return None
    
    print(f"✅ Found OSM water polygons: {osm_file.name}")
    osm_water = gpd.read_file(osm_file)
    print(f"   {len(osm_water):,} water polygons")
    
    # Spatial join: OSM polygons → river segments
    print(f"\n🔗 Spatial join: OSM polygons → classified segments...")
    print(f"   This may take several minutes...")
    
    osm_with_class = gpd.sjoin(
        osm_water,
        segments[['global_id', 'ml_predicted_class', 'geometry']],
        how='left',
        predicate='intersects'
    )
    
    # Calculate actual polygon areas
    print(f"\n📏 Calculating actual polygon areas...")
    
    # Project to equal-area CRS for accurate area calculation
    osm_with_class_proj = osm_with_class.to_crs('EPSG:6933')  # Equidistant Cylindrical
    osm_with_class['area_km2'] = osm_with_class_proj.geometry.area / 1e6
    
    # Group by salinity class
    area_summary = osm_with_class.groupby('ml_predicted_class').agg({
        'area_km2': ['sum', 'mean', 'count']
    }).round(2)
    
    area_summary.columns = ['_'.join(col).strip() for col in area_summary.columns.values]
    area_summary = area_summary.reset_index()
    area_summary['region'] = region_code
    
    print(f"\n✅ OSM Polygon Area Summary:")
    print(area_summary.to_string())
    
    return area_summary

# ==============================================================================
# GLOBAL AGGREGATION
# ==============================================================================

def aggregate_global_results(all_results: list) -> pd.DataFrame:
    """Aggregate all regional results into global summary"""
    print_section("GLOBAL AGGREGATION")
    
    # Combine all regions
    global_summary = pd.concat(all_results, ignore_index=True)
    
    # Calculate global totals by salinity class
    print(f"\n📊 Calculating global totals...")
    
    # Get column names (depends on approach used)
    if 'surface_area_sum' in global_summary.columns:
        area_col = 'surface_area_sum'
        count_col = 'global_id_count'
    elif 'area_km2_sum' in global_summary.columns:
        area_col = 'area_km2_sum'
        count_col = 'area_km2_count'
    else:
        print(f"❌ Cannot identify area column!")
        return None
    
    # Group by salinity class
    global_totals = global_summary.groupby('ml_predicted_class').agg({
        area_col: 'sum',
        count_col: 'sum'
    }).round(2)
    
    global_totals = global_totals.reset_index()
    global_totals.columns = ['salinity_class', 'total_area_km2', 'n_features']
    
    # Calculate percentages
    total_area = global_totals['total_area_km2'].sum()
    global_totals['percent_of_total'] = (
        global_totals['total_area_km2'] / total_area * 100
    ).round(2)
    
    # Sort by Venice System order
    venice_order = ['freshwater', 'oligohaline', 'mesohaline', 'polyhaline', 'euhaline']
    global_totals['salinity_class'] = pd.Categorical(
        global_totals['salinity_class'],
        categories=venice_order,
        ordered=True
    )
    global_totals = global_totals.sort_values('salinity_class')
    
    print(f"\n" + "="*80)
    print("🌍 GLOBAL WATER BODY SURFACE AREAS BY SALINITY CLASS")
    print("="*80)
    print(global_totals.to_string(index=False))
    print(f"\nTotal Global Surface Area: {total_area:,.0f} km²")
    
    # Calculate tidal/estuarine total (everything except freshwater)
    tidal_classes = ['oligohaline', 'mesohaline', 'polyhaline', 'euhaline']
    tidal_area = global_totals[
        global_totals['salinity_class'].isin(tidal_classes)
    ]['total_area_km2'].sum()
    
    print(f"\n📊 Key Metrics:")
    print(f"   Total Freshwater: {global_totals[global_totals['salinity_class']=='freshwater']['total_area_km2'].sum():,.0f} km²")
    print(f"   Total Tidal/Estuarine: {tidal_area:,.0f} km²")
    print(f"   Tidal % of Total: {tidal_area/total_area*100:.1f}%")
    
    return global_totals

# ==============================================================================
# EXPORT RESULTS
# ==============================================================================

def export_results(global_totals: pd.DataFrame, regional_results: list, approach: str):
    """Export results in multiple formats"""
    print_section("EXPORTING RESULTS")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. Global summary CSV
    global_file = OUTPUT_DIR / f'global_surface_areas_{approach}_{timestamp}.csv'
    global_totals.to_csv(global_file, index=False)
    print(f"✅ Global summary: {global_file.name}")
    
    # 2. Regional breakdown CSV
    regional_df = pd.concat(regional_results, ignore_index=True)
    regional_file = OUTPUT_DIR / f'regional_surface_areas_{approach}_{timestamp}.csv'
    regional_df.to_csv(regional_file, index=False)
    print(f"✅ Regional breakdown: {regional_file.name}")
    
    # 3. Summary for README/publication
    summary_file = OUTPUT_DIR / f'SUMMARY_{approach}_{timestamp}.txt'
    with open(summary_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("GLOBAL WATER BODY SURFACE AREAS BY SALINITY CLASS\n")
        f.write("="*80 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Method: {approach.upper()}\n")
        f.write(f"Regions: {', '.join(GRIT_REGIONS)}\n\n")
        f.write(global_totals.to_string(index=False))
        f.write("\n\n")
        f.write("="*80 + "\n")
        f.write("REFERENCE\n")
        f.write("="*80 + "\n")
        f.write("Salinity Classification: Venice System (1958)\n")
        f.write("  - Freshwater: <0.5 PSU\n")
        f.write("  - Oligohaline: 0.5-5 PSU (Tidal Freshwater Zone)\n")
        f.write("  - Mesohaline: 5-18 PSU\n")
        f.write("  - Polyhaline: 18-30 PSU\n")
        f.write("  - Euhaline: >30 PSU\n\n")
        f.write("Data Sources:\n")
        f.write("  - ML Model: Random Forest trained on GlobSalt data\n")
        f.write("  - River Network: GRIT v0.6 (Wortmann et al. 2025)\n")
        f.write("  - Surface Areas: " + ("OSM Water Layer (Yamazaki 2018)" if approach == 'osm' else "GRIT attributes") + "\n")
    
    print(f"✅ Summary report: {summary_file.name}")
    
    print(f"\n💡 Files saved to: {OUTPUT_DIR}")

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Calculate water body surface areas by salinity class'
    )
    parser.add_argument('--region', type=str, choices=GRIT_REGIONS,
                        help='Process single region')
    parser.add_argument('--all-regions', action='store_true',
                        help='Process all regions (recommended)')
    parser.add_argument('--use-osm', action='store_true',
                        help='Use OSM water polygons (more accurate but slower)')
    parser.add_argument('--use-grit', action='store_true', default=True,
                        help='Use GRIT surface areas (faster, default)')
    args = parser.parse_args()
    
    if not args.region and not args.all_regions:
        print("❌ Specify --region REGION or --all-regions")
        return
    
    # Determine approach
    approach = 'osm' if args.use_osm else 'grit'
    calc_func = calculate_areas_from_osm if args.use_osm else calculate_areas_from_grit
    
    print("\n" + "="*80)
    print("STEP 5: CALCULATE WATER BODY SURFACE AREAS BY SALINITY CLASS")
    print("="*80)
    print(f"\n🎯 Goal: Connect ML predictions to actual surface areas")
    print(f"📊 Approach: {approach.upper()}")
    print(f"🌍 Coverage: {'All regions' if args.all_regions else args.region}")
    
    # Determine regions
    regions = GRIT_REGIONS if args.all_regions else [args.region]
    
    # Process each region
    all_results = []
    
    for region in regions:
        result = calc_func(region)
        if result is not None:
            all_results.append(result)
    
    if len(all_results) == 0:
        print("\n❌ No results generated!")
        return
    
    # Aggregate global results
    global_totals = aggregate_global_results(all_results)
    
    if global_totals is not None:
        # Export results
        export_results(global_totals, all_results, approach)
        
        print("\n" + "="*80)
        print("✅ SUCCESS - SURFACE AREA CALCULATION COMPLETE!")
        print("="*80)
        
        print(f"\n📊 Next Steps:")
        print(f"   1. Review results in: {OUTPUT_DIR}")
        print(f"   2. Compare with literature (Dürr 2011, Laruelle 2025)")
        print(f"   3. Use for biogeochemical budgets (GHG, carbon, nutrients)")
        print(f"   4. Update README.md with final surface areas")
        print(f"   5. Publish results! 📄")

if __name__ == '__main__':
    main()
