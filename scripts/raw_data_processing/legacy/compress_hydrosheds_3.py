
"""
Comprehensive HydroSHEDS Data Processing for Global River System Classification
with Regional Visualization Validation

This script represents the optimal synthesis of performance and academic rigor for
processing the complete global HydroSHEDS datasets. It produces two primary,
fully classified, and geometrically valid global outputs: one for basins (Level 08)
and one for rivers.

Each feature is classified into one of three system types:
1.  'Estuarine': Coastal basins and their immediate upstream neighbors.
2.  'Non-Tidal Riverine': Basins part of a river system that reaches the ocean.
3.  'Endorheic': Basins in closed, inland drainage systems.

As a final validation step, the script generates interactive HTML maps of the
processed global data, focused on the Mekong and Saigon-Dong Nai systems in
Southern Vietnam.

Data Source: HydroSHEDS RiverATLAS & BasinATLAS v1.0
DOI: 10.5067/9SQ1S6VFQQ20
"""

import os
import sys
import time
from pathlib import Path
import warnings
from typing import Dict, Optional

warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import MultiPolygon
from shapely import get_coordinates
from tqdm import tqdm

tqdm.pandas()

try:
    import pyogrio
    PYOGRIO_AVAILABLE = True
    print("✓ Pyogrio engine available (optimized performance)")
except ImportError:
    PYOGRIO_AVAILABLE = False
    print("⚠️  Pyogrio not installed. Falling back to Fiona\n")

# --- Plotly for visualization validation ---
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
    print("✓ Plotly available, will generate interactive validation maps.")
except ImportError:
    PLOTLY_AVAILABLE = False
    print("⚠️  Plotly not installed. Skipping map generation. To install: pip install plotly")


# ==============================================================================
# CONFIGURATION
# ==============================================================================

CPU_CORES = max(1, os.cpu_count() - 1)
UPSTREAM_SEARCH_DEPTH = 1  # How many steps to trace upstream from the coast for 'Estuarine' classification.

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data' / 'raw' / 'hydrosheds'
OUTPUT_DIR = BASE_DIR / 'data' / 'processed'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Use comprehensive attributes for global datasets
BASIN_ATTRIBUTES_FULL = [
    'HYBAS_ID', 'NEXT_DOWN', 'NEXT_SINK', 'MAIN_BAS', 'DIST_SINK', 'DIST_MAIN',
    'SUB_AREA', 'UP_AREA', 'PFAF_ID', 'ENDO', 'COAST', 'ORDER_'
]
RIVER_ATTRIBUTES_FULL = [
    'HYRIV_ID', 'NEXT_DOWN', 'MAIN_RIV', 'LENGTH_KM', 'DIST_DN_KM', 'DIST_UP_KM',
    'CATCH_SKM', 'UPLAND_SKM', 'ENDORHEIC', 'DIS_AV_CMS', 'ORD_STRA', 'ORD_CLAS',
    'ORD_FLOW', 'HYBAS_L12'
]

# Bounding box for Southern Vietnam visualization
VIETNAM_AOI = {
    "lon_min": 103.5, "lon_max": 109.5,
    "lat_min": 8.0, "lat_max": 12.5
}
MAP_CENTER = {"lat": 10.0, "lon": 106.5}
MAP_ZOOM = 6


# ==============================================================================
# UTILITY AND VALIDATION FUNCTIONS
# ==============================================================================

def has_valid_coordinates(geom) -> bool:
    """Robustly check if a geometry contains any NaN or Inf coordinates."""
    if geom is None or geom.is_empty:
        return False
    try:
        return np.all(np.isfinite(get_coordinates(geom)))
    except Exception:
        return False

def get_file_size_mb(filepath: Path) -> float:
    return filepath.stat().st_size / (1024 * 1024)

def optimize_geodataframe_memory(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    original_mem = gdf.memory_usage(deep=True).sum() / 1024**2
    for col in gdf.select_dtypes(include=['int64']).columns:
        gdf[col] = pd.to_numeric(gdf[col], downcast='integer')
    for col in gdf.select_dtypes(include=['float64']).columns:
        gdf[col] = pd.to_numeric(gdf[col], downcast='float')
    new_mem = gdf.memory_usage(deep=True).sum() / 1024**2
    reduction = (1 - new_mem / original_mem) * 100 if original_mem > 0 else 0
    print(f"    Memory: {original_mem:.1f} MB → {new_mem:.1f} MB ({reduction:.1f}% reduction)")
    return gdf

def select_largest_polygon(geometry):
    if isinstance(geometry, MultiPolygon):
        if geometry.geoms:
            return max(geometry.geoms, key=lambda p: p.area)
    return geometry

# ==============================================================================
# CORE DATA PROCESSING
# ==============================================================================

def load_and_validate_geodatabase(gdb_path: str, layer_name: str, attributes: list) -> Optional[gpd.GeoDataFrame]:
    """Loads a full GDB layer, validates geometries, and optimizes memory."""
    print(f"\n{'='*90}")
    print(f"LOADING & VALIDATING: {layer_name}")
    print(f"{'='*90}")

    try:
        engine = "pyogrio" if PYOGRIO_AVAILABLE else "fiona"
        print(f"    Loading full dataset with {engine} engine...")
        gdf = gpd.read_file(gdb_path, layer=layer_name, engine=engine)
        print(f"    ✓ Loaded {len(gdf):,} raw features.")

        available_cols = [col for col in attributes if col in gdf.columns]
        gdf = gdf[available_cols + ['geometry']].copy()
        gdf = optimize_geodataframe_memory(gdf)

        print(f"\n    🔧 Geometry Validation & Cleaning...")
        gdf = gdf[gdf.geometry.notnull()].copy()

        print(f"        Applying buffer(0) to fix structural invalidities...")
        gdf['geometry'] = gdf.geometry.progress_apply(lambda g: g.buffer(0))
        gdf = gdf[~gdf.geometry.is_empty].copy()

        print(f"        Validating coordinates (NaN/Inf check)...")
        valid_mask = gdf.geometry.progress_apply(has_valid_coordinates)
        removed_count = (~valid_mask).sum()

        if removed_count > 0:
            print(f"        ⚠️  Removed {removed_count} geometries with invalid coordinates")

        gdf = gdf[valid_mask].copy()
        print(f"        ✅ Final: {len(gdf):,} fully valid features.")

        if gdf.empty:
            print(f"    ❌ No valid features remained after cleaning!")
            return None

        return gdf
    except Exception as e:
        print(f"    ❌ ERROR loading/validating {layer_name}: {e}")
        return None

def save_output(gdf: gpd.GeoDataFrame, filename_prefix: str) -> None:
    """Simplifies and saves a final GeoDataFrame."""
    if gdf is None: return

    output_path = OUTPUT_DIR / f'{filename_prefix}.gpkg'
    print(f"\n    💾 Finalizing and Saving Global Dataset: {output_path.name}")

    gdf['geometry'] = gdf['geometry'].progress_apply(select_largest_polygon)

    print("        Simplifying geometries for manageable file size...")
    tolerance = 0.005 if 'basins' in filename_prefix else 0.01
    gdf['geometry'] = gdf.geometry.simplify(tolerance, preserve_topology=True)

    gdf['processing_date'] = pd.Timestamp.now().strftime('%Y-%m-%d')

    engine = "pyogrio" if PYOGRIO_AVAILABLE else "fiona"
    gdf.to_file(output_path, driver='GPKG', layer=filename_prefix, engine=engine)

    size_mb = get_file_size_mb(output_path)
    print(f"        ✓ Output: {size_mb:.1f} MB ({len(gdf):,} features)")

# ==============================================================================
# VISUALIZATION VALIDATION FUNCTION
# ==============================================================================

def create_regional_maps(classified_basins, classified_rivers):
    """Generates focused Plotly maps for Southern Vietnam from global data."""
    if not PLOTLY_AVAILABLE:
        print("\nPlotly not available, skipping map generation.")
        return

    print(f"\n{'='*90}")
    print("GENERATING REGIONAL VALIDATION MAPS (SOUTHERN VIETNAM)")
    print(f"{'='*90}")

    color_map = {
        'Estuarine': '#e41a1c',          # Red
        'Non-Tidal Riverine': '#377eb8',  # Blue
        'Endorheic': '#999999',          # Grey
        'Unclassified': '#ffff33'        # Yellow
    }

    datasets = {
        "basins": classified_basins,
        "rivers": classified_rivers
    }

    for name, gdf in datasets.items():
        if gdf is None: continue

        print(f"    Creating map for: {name}...")

        # Crop the global GDF to the Area of Interest
        gdf_aoi = gdf.cx[VIETNAM_AOI['lon_min']:VIETNAM_AOI['lon_max'],
                         VIETNAM_AOI['lat_min']:VIETNAM_AOI['lat_max']]

        if gdf_aoi.empty:
            print(f"        - No data found in the specified AOI for {name}.")
            continue

        hover_id = "HYBAS_ID" if name == "basins" else "HYRIV_ID"

        fig = px.choropleth_mapbox(
            gdf_aoi,
            geojson=gdf_aoi.geometry,
            locations=gdf_aoi.index,
            color="system_type",
            color_discrete_map=color_map,
            mapbox_style="carto-positron",
            center=MAP_CENTER,
            zoom=MAP_ZOOM,
            opacity=0.7,
            hover_data={hover_id: True, "system_type": True},
            title=f"Global Classification ({name.title()}) - Southern Vietnam Validation"
        )
        fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

        output_path = OUTPUT_DIR / f"validation_map_{name}_vietnam.html"
        fig.write_html(str(output_path))
        print(f"        ✓ Saved map: {output_path.name}")


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    """Main execution."""
    print(f"\n{'='*90}")
    print("COMPREHENSIVE HYDROSHEDS GLOBAL DATA PROCESSING AND CLASSIFICATION")
    print(f"{'='*90}")

    basinatlas_gdb = DATA_DIR / 'BasinATLAS_v10.gdb'
    riveratlas_gdb = DATA_DIR / 'RiverATLAS_v10.gdb'

    if not basinatlas_gdb.exists() or not riveratlas_gdb.exists():
        print(f"\n❌ ERROR: BasinATLAS_v10.gdb and/or RiverATLAS_v10.gdb not found at {DATA_DIR}")
        sys.exit(1)

    # 1. Process Basins
    master_basins = load_and_validate_geodatabase(str(basinatlas_gdb), 'BasinATLAS_v10_lev08', BASIN_ATTRIBUTES_FULL)
    if master_basins is None:
        sys.exit("Basin processing failed. Aborting.")

    # 2. Classify Basins
    print(f"\n{'='*90}")
    print("CLASSIFYING ALL GLOBAL BASINS BY SYSTEM TYPE")
    print(f"{'='*90}")

    # A. Identify Estuarine system
    coastal_basins = master_basins[master_basins['NEXT_DOWN'] == 0].copy()
    estuarine_ids = set(coastal_basins['HYBAS_ID'])
    # Trace upstream for 'Estuarine' classification
    current_selection = coastal_basins
    for i in range(UPSTREAM_SEARCH_DEPTH):
        downstream_ids = current_selection['HYBAS_ID'].unique()
        upstream_neighbors = master_basins[master_basins['NEXT_DOWN'].isin(downstream_ids)]
        if upstream_neighbors.empty: break
        estuarine_ids.update(upstream_neighbors['HYBAS_ID'])
        current_selection = upstream_neighbors

    # B. Apply classification
    def classify_basin(row):
        if row['HYBAS_ID'] in estuarine_ids:
            return 'Estuarine'
        if row['ENDO'] == 0:
            return 'Non-Tidal Riverine'
        return 'Endorheic'

    print("\n    Applying classification to all basins...")
    master_basins['system_type'] = master_basins.progress_apply(classify_basin, axis=1)

    print("\n    Global Basin Classification Summary:")
    print(master_basins['system_type'].value_counts().to_string())

    # 3. Process Rivers
    master_rivers = load_and_validate_geodatabase(str(riveratlas_gdb), 'RiverATLAS_v10', RIVER_ATTRIBUTES_FULL)
    if master_rivers is None:
        sys.exit("River processing failed. Aborting.")

    # 4. Classify Rivers by joining with classified basins
    print(f"\n{'='*90}")
    print("CLASSIFYING ALL GLOBAL RIVERS BY SPATIAL JOIN")
    print(f"{'='*90}")

    print("    Spatially joining rivers to classified basins...")
    basins_for_join = master_basins[['HYBAS_ID', 'system_type', 'geometry']]
    classified_rivers = gpd.sjoin(master_rivers, basins_for_join, how="left", predicate="within")
    classified_rivers['system_type'] = classified_rivers['system_type'].fillna('Unclassified')
    classified_rivers = classified_rivers.drop_duplicates(subset=['HYRIV_ID'])

    print("\n    Global River Classification Summary:")
    print(classified_rivers['system_type'].value_counts().to_string())

    # 5. Save final global outputs
    save_output(master_basins, "basins_classified_global_lev08")
    save_output(classified_rivers, "rivers_classified_global")

    # 6. Generate regional validation maps
    create_regional_maps(master_basins, classified_rivers)

    print(f"\n{'='*90}")
    print(" "*30 + "✅ PROCESSING COMPLETE")
    print(f"{'='*90}")

    print(f"\n📁 Output directory: {OUTPUT_DIR.resolve()}")
    print(f"\n📄 Generated Files:")
    for file in sorted(OUTPUT_DIR.glob('*_classified_*.gpkg')):
        print(f"    - {file.name} (Global Dataset)")
    for file in sorted(OUTPUT_DIR.glob('validation_map_*.html')):
        print(f"    - {file.name} (Regional Validation Map)")

    print(f"\n💡 Next step: Open the generated .html files in your browser to view the validation maps.")

    return 0


if __name__ == '__main__':
    print("Deleting old processed files to ensure a clean run...")
    for f in OUTPUT_DIR.glob('*_classified_*.gpkg'):
        f.unlink()
    for f in OUTPUT_DIR.glob('validation_map_*.html'):
        f.unlink()

    sys.exit(main())