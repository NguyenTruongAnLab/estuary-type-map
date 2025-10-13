
"""
Process Baum et al. (2024) Large Estuary Morphometry Data
===========================================================

Processes morphometric measurements for 271 large structural estuaries from:
Baum, M.J., Schüttrumpf, H., & Siemes, R.W. (2024). 
Large structural estuaries: Their global distribution and morphology.
Geomorphology, supplementary data.

Creates web-compatible outputs:
- baum_morphometry.geojson - Point features with morphometric attributes
- baum_morphometry.gpkg - GeoPackage for GIS analysis
- baum_morphometry_metadata.json - Data provenance

Author: Global Estuary Type Map Project
Date: October 10, 2025
"""
import geopandas as gpd
import pandas as pd
import json
from pathlib import Path
from shapely.geometry import Point
from datetime import datetime

# ==============================================================================
# CONFIGURATION
# ==============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
INPUT_DIR = DATA_DIR / 'raw' / 'Large-estuaries-Baum_2024'
OUTPUT_DIR = DATA_DIR / 'processed'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_CSV = INPUT_DIR / 'Baum_2024_Geomorphology.csv'

# ==============================================================================
# PROCESSING FUNCTIONS
# ==============================================================================

def load_and_process_data():
    """Load Baum CSV and create GeoDataFrame"""
    print("="*80)
    print("BAUM ET AL. (2024) MORPHOMETRY PROCESSING")
    print("="*80)
    
    print(f"\n📂 Loading CSV: {INPUT_CSV.name}")
    
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"File not found: {INPUT_CSV}")
    
    df = pd.read_csv(INPUT_CSV)
    print(f"   Total records: {len(df):,}")
    
    # Create point geometries from coordinates
    geometry = [Point(xy) for xy in zip(df['Long'], df['Lat'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
    
    print(f"\n📊 Data Overview:")
    print(f"   Geomorphotypes:")
    for geotype, count in gdf['Geomorphotype'].value_counts().items():
        print(f"     {geotype:20s}: {count:3d} estuaries")
    
    print(f"\n   Tectonic Settings:")
    for tectonic, count in gdf['Tectonic Coast Classification'].value_counts().items():
        print(f"     {tectonic:20s}: {count:3d} estuaries")
    
    return gdf


def prepare_attributes(gdf):
    """Prepare and clean attributes for output"""
    print(f"\n⚙️  Preparing attributes...")
    
    # Rename columns for clarity
    gdf_output = gdf.rename(columns={
        'Embayment': 'name',
        'Lm': 'mouth_length_m',
        'Lb': 'bay_length_m',
        'Lat': 'lat',
        'Long': 'lon',
        'C': 'complexity_index',
        'Tectonic Coast Classification': 'tectonic_setting',
        'Geomorphotype': 'geomorphotype',
        'Cluster Weight (ω)': 'confidence'
    }).copy()
    
    # Convert meters to kilometers for better readability
    gdf_output['mouth_length_km'] = (gdf_output['mouth_length_m'] / 1000).round(2)
    gdf_output['bay_length_km'] = (gdf_output['bay_length_m'] / 1000).round(2)
    
    # Round other numerical values
    gdf_output['complexity_index'] = gdf_output['complexity_index'].round(3)
    gdf_output['confidence'] = gdf_output['confidence'].round(3)
    gdf_output['lat'] = gdf_output['lat'].round(4)
    gdf_output['lon'] = gdf_output['lon'].round(4)
    
    # Calculate estuary size category
    def categorize_size(mouth_km):
        if mouth_km < 5:
            return 'Medium'
        elif mouth_km < 20:
            return 'Large'
        elif mouth_km < 50:
            return 'Very Large'
        else:
            return 'Mega'
    
    gdf_output['size_category'] = gdf_output['mouth_length_km'].apply(categorize_size)
    
    # Add metadata
    gdf_output['data_source'] = 'Baum et al. (2024)'
    gdf_output['data_source_info'] = 'Large structural estuaries'
    
    # Select final columns
    final_cols = [
        'name', 'lat', 'lon',
        'geomorphotype', 'tectonic_setting',
        'mouth_length_km', 'bay_length_km', 'complexity_index',
        'size_category', 'confidence',
        'data_source', 'data_source_info',
        'geometry'
    ]
    
    gdf_output = gdf_output[final_cols]
    
    print(f"   ✓ Prepared {len(gdf_output.columns)} attributes")
    
    return gdf_output


def export_outputs(gdf):
    """Export to multiple formats"""
    print(f"\n💾 Exporting outputs...")
    
    # GeoPackage
    gpkg_file = OUTPUT_DIR / 'baum_morphometry.gpkg'
    print(f"   Writing: {gpkg_file.name}")
    gdf.to_file(gpkg_file, driver='GPKG')
    gpkg_size_kb = gpkg_file.stat().st_size / 1024
    print(f"   ✓ Size: {gpkg_size_kb:.1f} KB")
    
    # GeoJSON
    geojson_file = OUTPUT_DIR / 'baum_morphometry.geojson'
    print(f"   Writing: {geojson_file.name}")
    gdf.to_file(geojson_file, driver='GeoJSON')
    geojson_size_kb = geojson_file.stat().st_size / 1024
    print(f"   ✓ Size: {geojson_size_kb:.1f} KB")
    
    # Metadata
    metadata = {
        'dataset': 'Baum et al. (2024) Large Estuary Morphometry',
        'data_source': 'Baum, M.J., Schüttrumpf, H., & Siemes, R.W. (2024)',
        'publication': 'Large structural estuaries: Their global distribution and morphology',
        'journal': 'Geomorphology',
        'processed_date': datetime.now().isoformat(),
        'n_features': len(gdf),
        'geometry_type': 'Point',
        'crs': str(gdf.crs),
        'geomorphotypes': {
            'LSE': 'Large Shallow Estuary',
            'Rocky Bay': 'Rocky embayment',
            'Barrier Estuary': 'Protected by barrier',
            'Sandy Bay': 'Sandy embayment',
            'Funnelled': 'Funnel-shaped'
        },
        'tectonic_settings': {
            'collision': 'Active plate collision zones',
            'trailing': 'Passive continental margins',
            'marginal': 'Back-arc and marginal basins'
        },
        'attributes': {
            'name': 'Embayment name',
            'geomorphotype': 'Morphological classification (5 types)',
            'tectonic_setting': 'Tectonic coast type',
            'mouth_length_km': 'Width at mouth (km)',
            'bay_length_km': 'Length of embayment (km)',
            'complexity_index': 'Coastline complexity ratio (Lm/Lb)',
            'size_category': 'Size classification',
            'confidence': 'Classification confidence (0-1)',
            'lat': 'Latitude',
            'lon': 'Longitude'
        },
        'statistics': {
            'mouth_width_range_km': [
                float(gdf['mouth_length_km'].min()),
                float(gdf['mouth_length_km'].max())
            ],
            'bay_length_range_km': [
                float(gdf['bay_length_km'].min()),
                float(gdf['bay_length_km'].max())
            ],
            'complexity_range': [
                float(gdf['complexity_index'].min()),
                float(gdf['complexity_index'].max())
            ]
        }
    }
    
    metadata_file = OUTPUT_DIR / 'baum_morphometry_metadata.json'
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
    print(f"   Geographic coverage: Global")
    
    print(f"\n🏔️  Geomorphotype Distribution:")
    for geotype, count in gdf['geomorphotype'].value_counts().items():
        pct = (count / len(gdf)) * 100
        print(f"   {geotype:20s}: {count:3d} ({pct:5.1f}%)")
    
    print(f"\n📐 Morphometric Statistics:")
    print(f"   Mouth width:  {gdf['mouth_length_km'].min():.1f} - {gdf['mouth_length_km'].max():.1f} km")
    print(f"   Bay length:   {gdf['bay_length_km'].min():.1f} - {gdf['bay_length_km'].max():.1f} km")
    print(f"   Complexity:   {gdf['complexity_index'].min():.2f} - {gdf['complexity_index'].max():.2f}")
    
    print(f"\n🌍 Size Distribution:")
    for size, count in gdf['size_category'].value_counts().items():
        pct = (count / len(gdf)) * 100
        print(f"   {size:15s}: {count:3d} ({pct:5.1f}%)")
    
    print(f"\n📁 Output Files:")
    print(f"   - baum_morphometry.gpkg (~{gpkg_file.stat().st_size/1024:.0f} KB)")
    print(f"   - baum_morphometry.geojson (~{geojson_file.stat().st_size/1024:.0f} KB)")
    print(f"   - baum_morphometry_metadata.json")
    
    print(f"\n🎯 Usage:")
    print(f"   - Independent layer in web map")
    print(f"   - Spatial join with Dürr estuaries for enrichment")
    print(f"   - Morphometric analysis and classification")


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    """Main processing pipeline"""
    global gpkg_file, geojson_file  # For summary
    
    # Load data
    gdf = load_and_process_data()
    
    # Prepare attributes
    gdf = prepare_attributes(gdf)
    
    # Export
    gpkg_file, geojson_file, metadata_file = export_outputs(gdf)
    
    # Summary
    print_summary(gdf)


if __name__ == '__main__':
    main()
