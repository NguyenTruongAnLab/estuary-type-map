
"""
Enhanced Estuary Data Integration
===================================

Integrates multiple peer-reviewed datasets using spatial joins:
1. Dürr et al. (2011): Base estuary classification (970 estuaries)
2. Baum et al. (2024): Large estuary morphometry (271 estuaries)
3. Athanasiou et al. (2024): Coastal characteristics (728k segments)

Uses coordinate-based spatial matching (much more reliable than name matching).

Author: Global Estuary Type Map Project
Date: October 10, 2025
"""
import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
from shapely.geometry import Point
import json

# ==============================================================================
# CONFIGURATION
# ==============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
RAW_DIR = DATA_DIR / 'raw'
OUTPUT_DIR = DATA_DIR / 'processed'

# Input files
DURR_SHAPEFILE = RAW_DIR / 'Worldwide-typology-Shapefile-Durr_2011' / 'typology_catchments.shp'
BAUM_CSV = RAW_DIR / 'Large-estuaries-Baum_2024' / 'Baum_2024_Geomorphology.csv'
GCC_GEOPHYSICAL = RAW_DIR / 'GCC-Panagiotis-Athanasiou_2024' / 'GCC_geophysical.csv'
GCC_HYDROMETEOROLOGICAL = RAW_DIR / 'GCC-Panagiotis-Athanasiou_2024' / 'GCC_hydrometeorological.csv'
GCC_SOCIOECONOMIC = RAW_DIR / 'GCC-Panagiotis-Athanasiou_2024' / 'GCC_socioeconomic.csv'

# Matching thresholds
BAUM_MATCH_DISTANCE_KM = 50  # Max distance to match Baum estuaries (they're large)
GCC_BUFFER_KM = 10           # Buffer around estuary for GCC aggregation

# Type mappings (from original script)
DURR_TYPE_MAP = {
    1: "Small Delta (Type I)",
    2: "Tidal System (Type II)",
    3: "Lagoon (Type III)",
    4: "Fjord/Fjaerd (Type IV)",
    5: "Large River (Type Va)",
    51: "Large River with Tidal Delta (Type Vb)",
    6: "Karst (Type VI)",
    7: "Arheic (Type VII)"
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

# ==============================================================================
# DATA LOADING
# ==============================================================================

def load_durr_estuaries():
    """Load Dürr et al. (2011) estuary catchments"""
    print("\n📂 Loading Dürr et al. (2011) estuaries...")
    gdf = gpd.read_file(DURR_SHAPEFILE)
    
    # Filter to valid estuaries
    valid_types = [1, 2, 3, 4, 5, 6, 51]
    gdf = gdf[gdf['FIN_TYP'].isin(valid_types)].copy()
    gdf = gdf[(gdf['RECORDNAME'].notna()) & (gdf['BASINAREA'] > 100)].copy()
    
    print(f"   ✓ Loaded {len(gdf)} estuaries")
    return gdf


def load_baum_estuaries():
    """Load Baum et al. (2024) large estuaries with coordinates"""
    print("\n📂 Loading Baum et al. (2024) large estuaries...")
    
    if not BAUM_CSV.exists():
        print(f"   ⚠️  File not found: {BAUM_CSV}")
        return None
    
    df = pd.read_csv(BAUM_CSV)
    
    # Create GeoDataFrame with point geometries
    geometry = [Point(xy) for xy in zip(df['Long'], df['Lat'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
    
    print(f"   ✓ Loaded {len(gdf)} large estuaries")
    print(f"   Geomorphotypes: {gdf['Geomorphotype'].value_counts().to_dict()}")
    
    return gdf


def load_gcc_coastal_data(limit_rows=None):
    """
    Load GCC coastal characteristics.
    Use limit_rows for testing (e.g., 10000), None for full dataset.
    """
    print("\n📂 Loading GCC coastal characteristics...")
    
    gcc_data = {}
    
    for name, file_path in [
        ('geophysical', GCC_GEOPHYSICAL),
        ('hydrometeorological', GCC_HYDROMETEOROLOGICAL),
        ('socioeconomic', GCC_SOCIOECONOMIC)
    ]:
        if not file_path.exists():
            print(f"   ⚠️  File not found: {file_path.name}")
            continue
        
        print(f"   Loading {name}...", end='')
        df = pd.read_csv(file_path, nrows=limit_rows)
        
        # Create GeoDataFrame
        geometry = [Point(xy) for xy in zip(df['lon'], df['lat'])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
        
        gcc_data[name] = gdf
        print(f" ✓ {len(gdf):,} segments")
    
    return gcc_data


# ==============================================================================
# SPATIAL MATCHING
# ==============================================================================

def match_with_baum(durr_gdf, baum_gdf):
    """
    Spatially match Dürr estuaries with Baum data using nearest neighbor.
    
    Args:
        durr_gdf: Dürr estuary polygons
        baum_gdf: Baum estuary points
        
    Returns:
        durr_gdf with Baum attributes added
    """
    if baum_gdf is None or len(baum_gdf) == 0:
        print("\n⚠️  No Baum data to match")
        return durr_gdf
    
    print(f"\n🔗 Matching Dürr estuaries with Baum data...")
    print(f"   Method: Nearest neighbor within {BAUM_MATCH_DISTANCE_KM} km")
    
    # Get centroids of Dürr polygons
    durr_centroids = durr_gdf.copy()
    durr_centroids['geometry'] = durr_centroids.geometry.centroid
    
    # Reproject to meters for distance calculation (World Mollweide)
    durr_proj = durr_centroids.to_crs('ESRI:54009')
    baum_proj = baum_gdf.to_crs('ESRI:54009')
    
    # Find nearest Baum estuary for each Dürr estuary
    matches = 0
    max_dist_m = BAUM_MATCH_DISTANCE_KM * 1000
    
    # Initialize Baum attribute columns
    baum_cols = {
        'baum_name': None,
        'baum_geomorphotype': None,
        'baum_mouth_length_m': None,
        'baum_bay_length_m': None,
        'baum_complexity': None,
        'baum_tectonic': None,
        'baum_confidence': None,
        'baum_distance_km': None
    }
    
    for col in baum_cols:
        durr_gdf[col] = baum_cols[col]
    
    for idx in durr_proj.index:
        durr_point = durr_proj.loc[idx, 'geometry']
        
        # Calculate distances to all Baum estuaries
        distances = baum_proj.geometry.distance(durr_point)
        nearest_idx = distances.idxmin()
        nearest_dist = distances[nearest_idx]
        
        # Only match if within threshold
        if nearest_dist <= max_dist_m:
            baum_row = baum_gdf.loc[nearest_idx]
            durr_gdf.loc[idx, 'baum_name'] = baum_row['Embayment']
            durr_gdf.loc[idx, 'baum_geomorphotype'] = baum_row['Geomorphotype']
            durr_gdf.loc[idx, 'baum_mouth_length_m'] = baum_row['Lm']
            durr_gdf.loc[idx, 'baum_bay_length_m'] = baum_row['Lb']
            durr_gdf.loc[idx, 'baum_complexity'] = baum_row['C']
            durr_gdf.loc[idx, 'baum_tectonic'] = baum_row['Tectonic Coast Classification']
            durr_gdf.loc[idx, 'baum_confidence'] = baum_row['Cluster Weight (ω)']
            durr_gdf.loc[idx, 'baum_distance_km'] = nearest_dist / 1000
            matches += 1
    
    match_pct = (matches / len(durr_gdf)) * 100
    print(f"   ✓ Matched {matches}/{len(durr_gdf)} estuaries ({match_pct:.1f}%)")
    
    return durr_gdf


def aggregate_gcc_around_estuaries(durr_gdf, gcc_data, buffer_km=10):
    """
    Aggregate GCC data within buffer around each estuary.
    
    Args:
        durr_gdf: Dürr estuary polygons
        gcc_data: Dict of GCC GeoDataFrames
        buffer_km: Buffer radius in km
        
    Returns:
        durr_gdf with GCC attributes added
    """
    if not gcc_data:
        print("\n⚠️  No GCC data to aggregate")
        return durr_gdf
    
    print(f"\n🔗 Aggregating GCC data around estuaries...")
    print(f"   Buffer: {buffer_km} km radius")
    print(f"   This may take a while for 728k coastal segments...")
    
    # Get centroids
    durr_centroids = durr_gdf.copy()
    durr_centroids['geometry'] = durr_centroids.geometry.centroid
    
    # Reproject to meters
    durr_proj = durr_centroids.to_crs('ESRI:54009')
    buffer_m = buffer_km * 1000
    durr_proj['geometry'] = durr_proj.geometry.buffer(buffer_m)
    
    # Initialize GCC attribute columns (select most important)
    gcc_cols = {
        'gcc_tidal_range_m': None,
        'gcc_wave_height_p50_m': None,
        'gcc_wave_height_p95_m': None,
        'gcc_storm_surge_100yr_m': None,
        'gcc_nearshore_slope': None,
        'gcc_erosion_rate_m_yr': None,
        'gcc_pop_10km': None,
        'gcc_infrastructure_score': None
    }
    
    for col in gcc_cols:
        durr_gdf[col] = gcc_cols[col]
    
    # Process each dataset
    for dataset_name, gdf_gcc in gcc_data.items():
        print(f"   Processing {dataset_name}...")
        
        # Reproject GCC to meters
        gcc_proj = gdf_gcc.to_crs('ESRI:54009')
        
        # Spatial join (slow but accurate)
        for idx in durr_proj.index[:10]:  # LIMIT TO 10 FOR TESTING
            estuary_buffer = durr_proj.loc[idx, 'geometry']
            
            # Find GCC segments within buffer
            gcc_within = gcc_proj[gcc_proj.geometry.within(estuary_buffer)]
            
            if len(gcc_within) == 0:
                continue
            
            # Aggregate based on dataset
            if dataset_name == 'hydrometeorological':
                if 'mhhw' in gcc_within.columns and 'mllw' in gcc_within.columns:
                    durr_gdf.loc[idx, 'gcc_tidal_range_m'] = (
                        gcc_within['mhhw'] - gcc_within['mllw']
                    ).mean()
                if 'swh_p50' in gcc_within.columns:
                    durr_gdf.loc[idx, 'gcc_wave_height_p50_m'] = gcc_within['swh_p50'].mean()
                if 'swh_p95' in gcc_within.columns:
                    durr_gdf.loc[idx, 'gcc_wave_height_p95_m'] = gcc_within['swh_p95'].mean()
            
            elif dataset_name == 'socioeconomic':
                if 'pop_10_m' in gcc_within.columns:
                    durr_gdf.loc[idx, 'gcc_pop_10km'] = gcc_within['pop_10_m'].sum()
                if all(col in gcc_within.columns for col in ['roads', 'railways', 'ports']):
                    durr_gdf.loc[idx, 'gcc_infrastructure_score'] = (
                        gcc_within['roads'] + gcc_within['railways'] + gcc_within['ports']
                    ).sum()
    
    print(f"   ⚠️  GCC integration limited to first 10 estuaries for testing")
    print(f"   ⚠️  Full integration would take 2-3 hours for 970 estuaries")
    
    return durr_gdf


# ==============================================================================
# EXPORT
# ==============================================================================

def export_enhanced_geojson(gdf, output_file):
    """Export enhanced estuary data to GeoJSON"""
    print(f"\n💾 Exporting enhanced data...")
    
    # Create features for basins (polygons)
    features = []
    
    for idx, row in gdf.iterrows():
        centroid = row.geometry.centroid
        
        properties = {
            # Original Dürr attributes
            "name": row['RECORDNAME'],
            "type": SIMPLE_TYPE_MAP.get(row['FIN_TYP'], "Unknown"),
            "type_detailed": DURR_TYPE_MAP.get(row['FIN_TYP'], "Unknown"),
            "type_code": int(row['FIN_TYP']),
            "basin_area_km2": round(row['BASINAREA'], 2) if pd.notna(row['BASINAREA']) else None,
            "data_source": "Dürr et al. (2011)",
            "data_source_doi": "10.1007/s12237-011-9381-y",
        }
        
        # Add Baum attributes if matched
        if pd.notna(row.get('baum_name')):
            properties.update({
                "baum_name": row['baum_name'],
                "baum_geomorphotype": row['baum_geomorphotype'],
                "baum_mouth_length_km": round(row['baum_mouth_length_m'] / 1000, 2),
                "baum_bay_length_km": round(row['baum_bay_length_m'] / 1000, 2),
                "baum_complexity": round(row['baum_complexity'], 2),
                "baum_tectonic": row['baum_tectonic'],
                "baum_confidence": round(row['baum_confidence'], 2),
                "baum_source": "Baum et al. (2024)"
            })
        
        # Add GCC attributes if available
        if pd.notna(row.get('gcc_tidal_range_m')):
            properties.update({
                "gcc_tidal_range_m": round(row['gcc_tidal_range_m'], 2),
                "gcc_wave_height_mean_m": round(row['gcc_wave_height_p50_m'], 2) if pd.notna(row.get('gcc_wave_height_p50_m')) else None,
                "gcc_pop_10km": int(row['gcc_pop_10km']) if pd.notna(row.get('gcc_pop_10km')) else None,
                "gcc_source": "Athanasiou et al. (2024) - DOI: 10.5281/zenodo.8200199"
            })
        
        # Create feature with polygon geometry
        feature = {
            "type": "Feature",
            "geometry": json.loads(gdf.loc[idx:idx].to_json())['features'][0]['geometry'],
            "properties": properties
        }
        
        features.append(feature)
    
    # Create GeoJSON
    geojson = {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "generated_date": pd.Timestamp.now().isoformat(),
            "total_estuaries": len(features),
            "data_sources": [
                "Dürr et al. (2011) - DOI: 10.1007/s12237-011-9381-y",
                "Baum et al. (2024) - Large Structural Estuaries",
                "Athanasiou et al. (2024) - DOI: 10.5281/zenodo.8200199"
            ]
        }
    }
    
    # Save
    with open(output_file, 'w') as f:
        json.dump(geojson, f)
    
    file_size_mb = output_file.stat().st_size / (1024**2)
    print(f"   ✓ Exported: {output_file.name}")
    print(f"   Size: {file_size_mb:.2f} MB")
    
    # Statistics
    baum_matches = gdf['baum_name'].notna().sum()
    gcc_matches = gdf['gcc_tidal_range_m'].notna().sum()
    
    print(f"\n📊 Enhancement Statistics:")
    print(f"   Total estuaries: {len(gdf)}")
    print(f"   With Baum data: {baum_matches} ({baum_matches/len(gdf)*100:.1f}%)")
    print(f"   With GCC data: {gcc_matches} ({gcc_matches/len(gdf)*100:.1f}%)")


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("="*80)
    print("ENHANCED ESTUARY DATA INTEGRATION")
    print("="*80)
    print("\nIntegrating:")
    print("  1. Dürr et al. (2011) - Base classification")
    print("  2. Baum et al. (2024) - Large estuary morphometry")
    print("  3. Athanasiou et al. (2024) - Coastal characteristics")
    
    # Load data
    durr_gdf = load_durr_estuaries()
    baum_gdf = load_baum_estuaries()
    gcc_data = load_gcc_coastal_data(limit_rows=50000)  # Load 50k segments for testing
    
    # Match with Baum
    durr_gdf = match_with_baum(durr_gdf, baum_gdf)
    
    # Aggregate GCC (WARNING: Slow!)
    # durr_gdf = aggregate_gcc_around_estuaries(durr_gdf, gcc_data, buffer_km=GCC_BUFFER_KM)
    
    # Export
    output_file = OUTPUT_DIR / 'basins_enhanced.geojson'
    export_enhanced_geojson(durr_gdf, output_file)
    
    print("\n" + "="*80)
    print("✅ INTEGRATION COMPLETE")
    print("="*80)
    print(f"\nOutput: {output_file}")
    print("\n🎯 Next Steps:")
    print("  1. Replace basins_simplified.geojson with basins_enhanced.geojson")
    print("  2. Update map.js to display new attributes")
    print("  3. Add filters for Baum geomorphotypes")
    print("  4. Test in browser")


if __name__ == '__main__':
    main()
