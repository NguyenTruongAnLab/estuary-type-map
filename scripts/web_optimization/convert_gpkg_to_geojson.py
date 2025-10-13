
"""
Smart GPKG to GeoJSON Converter with Zoom-Based Multi-Resolution
==================================================================

Converts GPKG files to web-optimized GeoJSON with intelligent strategies:
1. Small files (<5MB) → Direct conversion
2. Medium files (5-20MB) → Simplified geometry + attribute selection
3. Large files (>20MB) → Multi-resolution pyramid (zoom-based loading)

This ensures fast web performance while maintaining data quality at appropriate scales.

Author: Global Estuary Type Map Project
Date: October 10, 2025
"""

import geopandas as gpd
import json
from pathlib import Path
from shapely import wkb, wkt
from shapely.geometry import shape, mapping
import warnings
warnings.filterwarnings('ignore')

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
OUTPUT_DIR = BASE_DIR / 'data' / 'web'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# File size thresholds (MB)
DIRECT_THRESHOLD = 5.0  # Files <5MB: direct conversion
SIMPLIFY_THRESHOLD = 20.0  # Files 5-20MB: simplify geometry
PYRAMID_THRESHOLD = 20.0  # Files >20MB: multi-resolution

# Geometry simplification tolerances (degrees, ~km at equator)
TOLERANCE_LOW = 0.1  # ~10km - for zoom 2-4 (global view)
TOLERANCE_MED = 0.01  # ~1km - for zoom 5-8 (regional view)
TOLERANCE_HIGH = 0.001  # ~100m - for zoom 9+ (local view)

# Files to process with their configurations
FILES_CONFIG = {
    # Small files - direct conversion
    'baum_morphometry.gpkg': {
        'output': 'baum_morphometry.geojson',
        'strategy': 'direct',
        'description': '271 point features, already converted'
    },
    'durr_estuaries.gpkg': {
        'output': 'durr_estuaries.geojson',
        'strategy': 'direct',
        'description': '6,226 polygon features with attributes, already converted'
    },
    'salinity_zones.gpkg': {
        'output': 'salinity_zones.geojson',
        'strategy': 'direct',
        'description': '8,104 basins with salinity data, already converted'
    },
    
    # Medium files - simplify geometry
    'basins_coastal_lev06.gpkg': {
        'output': 'basins_coastal_lev06_simplified.geojson',
        'strategy': 'simplify',
        'tolerance': TOLERANCE_MED,
        'attributes': ['HYBAS_ID', 'MAIN_BAS', 'DIST_MAIN', 'DIST_SINK', 'SUB_AREA', 'COAST'],
        'description': '5,149 coastal basins (level 6) - simplified for web'
    },
    
    # Large files - multi-resolution pyramid
    'rivers_estuaries_global.gpkg': {
        'output_base': 'rivers_estuaries',
        'strategy': 'pyramid',
        'zoom_levels': {
            'low': {'zoom': '2-4', 'tolerance': TOLERANCE_LOW, 'file': 'rivers_estuaries_z2-4.geojson'},
            'med': {'zoom': '5-8', 'tolerance': TOLERANCE_MED, 'file': 'rivers_estuaries_z5-8.geojson'},
            'high': {'zoom': '9+', 'tolerance': TOLERANCE_HIGH, 'file': 'rivers_estuaries_z9plus.geojson'}
        },
        'attributes': ['HYRIV_ID', 'MAIN_RIV', 'LENGTH_KM', 'ORD_STRA', 'DIS_AV_CMS'],
        'description': '73,410 river reaches - multi-resolution for zoom-based loading'
    },
    'basins_coastal_lev08.gpkg': {
        'output_base': 'basins_coastal_lev08',
        'strategy': 'pyramid',
        'zoom_levels': {
            'low': {'zoom': '2-6', 'tolerance': TOLERANCE_LOW, 'file': 'basins_coastal_lev08_z2-6.geojson'},
            'med': {'zoom': '7-10', 'tolerance': TOLERANCE_MED, 'file': 'basins_coastal_lev08_z7-10.geojson'},
            'high': {'zoom': '11+', 'tolerance': TOLERANCE_HIGH, 'file': 'basins_coastal_lev08_z11plus.geojson'}
        },
        'attributes': ['HYBAS_ID', 'MAIN_BAS', 'DIST_MAIN', 'DIST_SINK', 'SUB_AREA', 'COAST'],
        'description': '23,996 coastal basins (level 8) - multi-resolution for zoom-based loading'
    }
}


def get_file_size_mb(filepath):
    """Get file size in MB"""
    if not filepath.exists():
        return 0
    return filepath.stat().st_size / (1024 * 1024)


def simplify_geometry(gdf, tolerance):
    """Simplify geometry while preserving topology"""
    print(f"   Simplifying geometry (tolerance={tolerance}°)...")
    gdf = gdf.copy()
    gdf['geometry'] = gdf['geometry'].simplify(tolerance, preserve_topology=True)
    return gdf


def select_attributes(gdf, attributes):
    """Keep only specified attributes plus geometry"""
    cols_to_keep = [col for col in attributes if col in gdf.columns]
    cols_to_keep.append('geometry')
    return gdf[cols_to_keep]


def convert_direct(input_file, output_file, description):
    """Direct conversion for small files"""
    print(f"\n📄 Processing: {input_file.name}")
    print(f"   Strategy: Direct conversion")
    print(f"   Description: {description}")
    
    if not input_file.exists():
        print(f"   ⚠️  File not found: {input_file}")
        return False
    
    try:
        gdf = gpd.read_file(input_file)
        print(f"   ✓ Loaded {len(gdf)} features")
        
        # Save as GeoJSON
        gdf.to_file(output_file, driver='GeoJSON')
        output_size = get_file_size_mb(output_file)
        print(f"   ✓ Saved: {output_file.name} ({output_size:.2f} MB)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def convert_simplify(input_file, output_file, tolerance, attributes, description):
    """Conversion with geometry simplification and attribute selection"""
    print(f"\n📄 Processing: {input_file.name}")
    print(f"   Strategy: Simplify + Attribute selection")
    print(f"   Description: {description}")
    
    if not input_file.exists():
        print(f"   ⚠️  File not found: {input_file}")
        return False
    
    try:
        gdf = gpd.read_file(input_file)
        original_count = len(gdf)
        original_size = get_file_size_mb(input_file)
        print(f"   ✓ Loaded {original_count} features ({original_size:.2f} MB)")
        
        # Select attributes
        gdf = select_attributes(gdf, attributes)
        print(f"   ✓ Kept {len([c for c in gdf.columns if c != 'geometry'])} attributes")
        
        # Simplify geometry
        gdf = simplify_geometry(gdf, tolerance)
        
        # Save as GeoJSON
        gdf.to_file(output_file, driver='GeoJSON')
        output_size = get_file_size_mb(output_file)
        reduction = ((original_size - output_size) / original_size * 100) if original_size > 0 else 0
        print(f"   ✓ Saved: {output_file.name} ({output_size:.2f} MB, {reduction:.1f}% reduction)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def convert_pyramid(input_file, output_base, zoom_levels, attributes, description):
    """Create multi-resolution pyramid for zoom-based loading"""
    print(f"\n📄 Processing: {input_file.name}")
    print(f"   Strategy: Multi-resolution pyramid")
    print(f"   Description: {description}")
    
    if not input_file.exists():
        print(f"   ⚠️  File not found: {input_file}")
        return False
    
    try:
        gdf = gpd.read_file(input_file)
        original_count = len(gdf)
        original_size = get_file_size_mb(input_file)
        print(f"   ✓ Loaded {original_count} features ({original_size:.2f} MB)")
        
        # Select attributes
        gdf = select_attributes(gdf, attributes)
        print(f"   ✓ Kept {len([c for c in gdf.columns if c != 'geometry'])} attributes")
        
        # Create pyramid levels
        results = {}
        for level, config in zoom_levels.items():
            print(f"\n   📊 Creating {level} resolution (zoom {config['zoom']})...")
            
            gdf_level = simplify_geometry(gdf.copy(), config['tolerance'])
            output_file = OUTPUT_DIR / config['file']
            gdf_level.to_file(output_file, driver='GeoJSON')
            
            output_size = get_file_size_mb(output_file)
            print(f"      ✓ Saved: {config['file']} ({output_size:.2f} MB)")
            results[level] = {
                'file': config['file'],
                'zoom': config['zoom'],
                'size_mb': output_size,
                'features': len(gdf_level)
            }
        
        # Create metadata JSON for JavaScript loader
        metadata_file = OUTPUT_DIR / f"{output_base}_metadata.json"
        metadata = {
            'source_file': input_file.name,
            'total_features': original_count,
            'strategy': 'multi-resolution',
            'zoom_levels': results,
            'description': description,
            'usage': 'Load appropriate resolution based on map zoom level',
            'loader_example': {
                'zoom_2_4': results['low']['file'],
                'zoom_5_8': results['med']['file'],
                'zoom_9plus': results['high']['file']
            }
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n   ✓ Metadata saved: {metadata_file.name}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def create_conversion_report():
    """Create a report of all converted files"""
    print("\n" + "="*80)
    print("📊 CONVERSION REPORT")
    print("="*80)
    
    report = []
    web_files = list(OUTPUT_DIR.glob('*.geojson')) + list(OUTPUT_DIR.glob('*.json'))
    
    for file in sorted(web_files):
        size_mb = get_file_size_mb(file)
        report.append({
            'file': file.name,
            'size_mb': size_mb,
            'type': 'metadata' if file.suffix == '.json' else 'data'
        })
    
    # Group by type
    data_files = [r for r in report if r['type'] == 'data']
    meta_files = [r for r in report if r['type'] == 'metadata']
    
    print("\n✅ GeoJSON Data Files:")
    for r in data_files:
        print(f"   {r['file']:<50} {r['size_mb']:>8.2f} MB")
    
    if meta_files:
        print("\n📋 Metadata Files:")
        for r in meta_files:
            print(f"   {r['file']}")
    
    total_size = sum(r['size_mb'] for r in report)
    print(f"\n📦 Total size: {total_size:.2f} MB")
    print(f"📁 Output directory: {OUTPUT_DIR}")


def main():
    print("="*80)
    print("🌊 Global Estuary Type Map - Smart GPKG to GeoJSON Converter")
    print("="*80)
    print(f"\nInput directory: {PROCESSED_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    
    # Process each file according to its strategy
    for gpkg_file, config in FILES_CONFIG.items():
        input_file = PROCESSED_DIR / gpkg_file
        
        if config['strategy'] == 'direct':
            output_file = OUTPUT_DIR / config['output']
            convert_direct(input_file, output_file, config['description'])
            
        elif config['strategy'] == 'simplify':
            output_file = OUTPUT_DIR / config['output']
            convert_simplify(
                input_file, 
                output_file, 
                config['tolerance'], 
                config['attributes'], 
                config['description']
            )
            
        elif config['strategy'] == 'pyramid':
            convert_pyramid(
                input_file,
                config['output_base'],
                config['zoom_levels'],
                config['attributes'],
                config['description']
            )
    
    # Create conversion report
    create_conversion_report()
    
    print("\n" + "="*80)
    print("✅ CONVERSION COMPLETE!")
    print("="*80)
    print("\n💡 Next Steps:")
    print("   1. Review converted files in data/web/")
    print("   2. Update map.js to use zoom-based loading for large files")
    print("   3. Test performance in browser at different zoom levels")
    print("   4. Adjust tolerances if needed")


if __name__ == '__main__':
    main()
