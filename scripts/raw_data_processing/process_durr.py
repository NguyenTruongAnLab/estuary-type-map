
"""
Process Dürr et al. (2011) Estuary Classification Data
======================================================

Processes the base global estuary classification from:
Dürr, H.H., Laruelle, G.G., van Kempen, C.M., Slomp, C.P., Meybeck, M., & 
Middelkoop, H. (2011). Worldwide Typology of Nearshore Coastal Systems: 
Defining the Estuarine Filter of River Inputs to the Oceans. 
Estuaries and Coasts, 34(3), 441-458.
DOI: 10.1007/s12237-011-9381-y

Creates web-compatible outputs:
- durr_estuaries.geojson - Estuary polygons with classification
- durr_estuaries.gpkg - GeoPackage for GIS analysis
- durr_estuaries_metadata.json - Data provenance

Author: Global Estuary Type Map Project
Date: October 10, 2025
"""
import geopandas as gpd
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# ==============================================================================
# CONFIGURATION
# ==============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
INPUT_DIR = DATA_DIR / 'raw' / 'Worldwide-typology-Shapefile-Durr_2011'
OUTPUT_DIR = DATA_DIR / 'processed'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_SHAPEFILE = INPUT_DIR / 'typology_catchments.shp'

# Type mappings
DURR_TYPE_MAP = {
    1: "Small Delta",
    2: "Tidal System",
    3: "Lagoon",
    4: "Fjord/Fjaerd",
    5: "Large River",
    51: "Large River with Tidal Delta",
    6: "Karst",
    7: "Arheic"
}

SIMPLE_TYPE_MAP = {
    1: "Delta",
    2: "Coastal Plain",
    3: "Lagoon",
    4: "Fjord",
    5: "Delta",
    51: "Delta",
    6: "Coastal Plain",
    7: "Coastal Plain"
}

# Simplification tolerance (degrees, ~1km at equator)
SIMPLIFY_TOLERANCE = 0.01

# ==============================================================================
# PROCESSING FUNCTIONS
# ==============================================================================

def load_and_filter_data():
    """Load Dürr shapefile and filter to valid estuaries"""
    print("="*80)
    print("DÜRR ET AL. (2011) ESTUARY CLASSIFICATION PROCESSING")
    print("="*80)
    
    print(f"\n📂 Loading shapefile: {INPUT_SHAPEFILE.name}")
    gdf = gpd.read_file(INPUT_SHAPEFILE)
    
    print(f"   Total features: {len(gdf):,}")
    
    # Filter to valid coastal estuaries
    valid_types = [1, 2, 3, 4, 5, 6, 51]
    gdf_filtered = gdf[gdf['FIN_TYP'].isin(valid_types)].copy()
    
    # Filter to named basins with reasonable area
    gdf_filtered = gdf_filtered[
        (gdf_filtered['RECORDNAME'].notna()) & 
        (gdf_filtered['RECORDNAME'] != 'None') &
        (gdf_filtered['BASINAREA'] > 100)  # km²
    ].copy()
    
    print(f"   Filtered to: {len(gdf_filtered):,} valid estuaries")
    print(f"\n📊 Type Distribution:")
    type_counts = gdf_filtered['FIN_TYP'].value_counts().sort_index()
    for type_code, count in type_counts.items():
        type_name = DURR_TYPE_MAP.get(type_code, "Unknown")
        print(f"   {type_code:2d} - {type_name:30s}: {count:4d} estuaries")
    
    return gdf_filtered


def prepare_attributes(gdf):
    """Prepare and clean attributes for output"""
    print(f"\n⚙️  Preparing attributes...")
    
    # Add derived fields
    gdf['type_code'] = gdf['FIN_TYP'].astype(int)
    gdf['type_detailed'] = gdf['FIN_TYP'].map(DURR_TYPE_MAP)
    gdf['type_simple'] = gdf['FIN_TYP'].map(SIMPLE_TYPE_MAP)
    
    # Calculate centroid coordinates
    centroids = gdf.geometry.centroid
    gdf['centroid_lon'] = centroids.x.round(4)
    gdf['centroid_lat'] = centroids.y.round(4)
    
    # Select and rename columns for output
    output_cols = {
        'RECORDNAME': 'name',
        'type_simple': 'type',
        'type_detailed': 'type_detailed',
        'type_code': 'type_code',
        'BASINAREA': 'basin_area_km2',
        'SEANAME': 'sea_name',
        'OCEANNAME': 'ocean_name',
        'centroid_lon': 'lon',
        'centroid_lat': 'lat',
        'geometry': 'geometry'
    }
    
    gdf_output = gdf[list(output_cols.keys())].copy()
    gdf_output = gdf_output.rename(columns=output_cols)
    
    # Round numerical values
    gdf_output['basin_area_km2'] = gdf_output['basin_area_km2'].round(2)
    
    # Add metadata fields
    gdf_output['data_source'] = 'Dürr et al. (2011)'
    gdf_output['data_source_doi'] = '10.1007/s12237-011-9381-y'
    
    print(f"   ✓ Prepared {len(gdf_output.columns)} attributes")
    
    return gdf_output


def simplify_geometries(gdf):
    """Simplify geometries for web performance"""
    print(f"\n🔧 Simplifying geometries...")
    print(f"   Tolerance: {SIMPLIFY_TOLERANCE}° (~1 km)")
    
    # Calculate original size
    original_vertices = sum(len(geom.exterior.coords) if hasattr(geom, 'exterior') 
                           else 0 for geom in gdf.geometry)
    
    # Simplify
    gdf['geometry'] = gdf.geometry.simplify(SIMPLIFY_TOLERANCE, preserve_topology=True)
    
    # Calculate new size
    simplified_vertices = sum(len(geom.exterior.coords) if hasattr(geom, 'exterior') 
                             else 0 for geom in gdf.geometry)
    
    reduction = (1 - simplified_vertices / original_vertices) * 100
    print(f"   Original vertices: {original_vertices:,}")
    print(f"   Simplified vertices: {simplified_vertices:,}")
    print(f"   Reduction: {reduction:.1f}%")
    
    return gdf


def export_outputs(gdf):
    """Export to multiple formats"""
    print(f"\n💾 Exporting outputs...")
    
    # GeoPackage (full precision, for analysis)
    gpkg_file = OUTPUT_DIR / 'durr_estuaries.gpkg'
    print(f"   Writing: {gpkg_file.name}")
    gdf.to_file(gpkg_file, driver='GPKG')
    gpkg_size_mb = gpkg_file.stat().st_size / (1024**2)
    print(f"   ✓ Size: {gpkg_size_mb:.2f} MB")
    
    # GeoJSON (web-compatible)
    geojson_file = OUTPUT_DIR / 'durr_estuaries.geojson'
    print(f"   Writing: {geojson_file.name}")
    gdf.to_file(geojson_file, driver='GeoJSON')
    geojson_size_mb = geojson_file.stat().st_size / (1024**2)
    print(f"   ✓ Size: {geojson_size_mb:.2f} MB")
    
    if geojson_size_mb > 5:
        print(f"   ⚠️  Warning: File exceeds 5MB target")
        print(f"   Consider increasing simplification or splitting by region")
    
    # Metadata JSON
    metadata = {
        'dataset': 'Dürr et al. (2011) Estuary Classification',
        'data_source_doi': '10.1007/s12237-011-9381-y',
        'processed_date': datetime.now().isoformat(),
        'n_features': len(gdf),
        'geometry_type': 'Polygon',
        'crs': str(gdf.crs),
        'simplification_tolerance_degrees': SIMPLIFY_TOLERANCE,
        'type_classification': {
            'system': '7-class geomorphological typology',
            'classes': DURR_TYPE_MAP
        },
        'attributes': {
            'name': 'Estuary/basin name',
            'type': 'Simplified type (5 classes)',
            'type_detailed': 'Detailed Dürr type (7 classes)',
            'type_code': 'Original FIN_TYP code',
            'basin_area_km2': 'Watershed area (km²)',
            'sea_name': 'Adjacent sea',
            'ocean_name': 'Ocean basin',
            'lon': 'Centroid longitude',
            'lat': 'Centroid latitude'
        },
        'citation': (
            'Dürr, H.H., Laruelle, G.G., van Kempen, C.M., Slomp, C.P., '
            'Meybeck, M., & Middelkoop, H. (2011). Worldwide Typology of '
            'Nearshore Coastal Systems: Defining the Estuarine Filter of '
            'River Inputs to the Oceans. Estuaries and Coasts, 34(3), 441-458.'
        )
    }
    
    metadata_file = OUTPUT_DIR / 'durr_estuaries_metadata.json'
    print(f"   Writing: {metadata_file.name}")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"   ✓ Metadata saved")
    
    return gpkg_file, geojson_file, metadata_file


def print_summary(gdf):
    """Print processing summary"""
    print(f"\n" + "="*80)
    print("✅ PROCESSING COMPLETE")
    print("="*80)
    
    print(f"\n📊 Summary:")
    print(f"   Total estuaries: {len(gdf):,}")
    print(f"   Geographic extent: {gdf.total_bounds}")
    print(f"\n🗂️  Type Distribution:")
    for type_name in gdf['type'].value_counts().sort_index().items():
        print(f"   {type_name[0]:15s}: {type_name[1]:4d} estuaries")
    
    print(f"\n🌍 Regional Distribution:")
    ocean_counts = gdf['ocean_name'].value_counts().head(5)
    for ocean, count in ocean_counts.items():
        print(f"   {ocean:30s}: {count:4d} estuaries")
    
    print(f"\n📁 Output Files:")
    print(f"   - durr_estuaries.gpkg (GeoPackage)")
    print(f"   - durr_estuaries.geojson (GeoJSON)")
    print(f"   - durr_estuaries_metadata.json (Metadata)")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Process other datasets (Baum, GCC, GlobSalt, HydroSHEDS)")
    print(f"   2. Create layer loader in map.js")
    print(f"   3. Test in browser: http://localhost:8000")


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    """Main processing pipeline"""
    
    # Load and filter
    gdf = load_and_filter_data()
    
    # Prepare attributes
    gdf = prepare_attributes(gdf)
    
    # Simplify geometries
    gdf = simplify_geometries(gdf)
    
    # Export
    export_outputs(gdf)
    
    # Summary
    print_summary(gdf)


if __name__ == '__main__':
    main()
