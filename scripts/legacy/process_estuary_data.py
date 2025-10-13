
"""
Process estuary data from open-access scientific datasets.

Data sources:
- Dürr et al. (2011): Worldwide typology of nearshore coastal systems
  DOI: 10.1007/s12237-011-9381-y
- Baum et al. (2024): Large structural estuaries (supplementary data)
- Athanasiou et al. (2024): Global Coastal Characteristics (GCC) - optional enrichment
  DOI: 10.5281/zenodo.8200199

This script processes real estuary datasets and generates a GeoJSON file
with estuary locations and their classifications.

Note: Laruelle et al. (2025) is used only for validation and global area
statistics. No shape, polygon, or direct attribute data is used from that study.
"""

import json
import sys
import os
from pathlib import Path

try:
    import geopandas as gpd
    import pandas as pd
except ImportError as e:
    print(f"Error: Required packages not installed: {e}", file=sys.stderr)
    print("Please install: pip install geopandas pandas pyproj", file=sys.stderr)
    sys.exit(1)


# Type mapping from Dürr et al. (2011) FIN_TYP codes to descriptive names
DURR_TYPE_MAP = {
    -9999: "Unknown",
    0: "Endorheic/Glaciated",
    1: "Small Delta (Type I)",
    2: "Tidal System (Type II)",
    3: "Lagoon (Type III)",
    4: "Fjord/Fjaerd (Type IV)",
    5: "Large River (Type Va)",
    51: "Large River with Tidal Delta (Type Vb)",
    6: "Karst (Type VI)",
    7: "Arheic (Type VII)"
}

# Simplified type mapping for web display (matches frontend filters)
SIMPLE_TYPE_MAP = {
    1: "Delta",
    2: "Coastal Plain",  # Tidal systems are often coastal plain
    3: "Lagoon",
    4: "Fjord",
    5: "Delta",  # Large rivers with deltas
    51: "Delta",  # Large rivers with tidal deltas
    6: "Coastal Plain",  # Karst systems
    7: "Coastal Plain"
}


def load_durr_data(shapefile_path):
    """
    Load estuary data from Dürr et al. (2011) shapefile.
    
    Args:
        shapefile_path: Path to the typology_catchments.shp file
    
    Returns:
        GeoDataFrame with estuary catchment data
    """
    print(f"Loading Dürr et al. (2011) shapefile: {shapefile_path}")
    gdf = gpd.read_file(shapefile_path)
    
    # Filter to meaningful estuaries (exclude endorheic, glaciated, arheic, unknown)
    # Focus on types 1-6, 51 (actual coastal systems)
    valid_types = [1, 2, 3, 4, 5, 6, 51]
    gdf = gdf[gdf['FIN_TYP'].isin(valid_types)].copy()
    
    # Filter to named basins with reasonable area
    gdf = gdf[
        (gdf['RECORDNAME'].notna()) & 
        (gdf['RECORDNAME'] != 'None') &
        (gdf['BASINAREA'] > 100)  # Filter small unnamed catchments
    ].copy()
    
    print(f"Found {len(gdf)} valid estuary catchments")
    return gdf


def load_baum_data(csv_path):
    """
    Load large estuary data from Baum et al. (2024).
    
    Args:
        csv_path: Path to the Baum_2024_Geomorphology.csv file
    
    Returns:
        DataFrame with large estuary morphometry data
    """
    print(f"Loading Baum et al. (2024) CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Found {len(df)} large structural estuaries")
    return df


def create_estuary_features(durr_gdf, baum_df=None):
    """
    Create GeoJSON features from Dürr data, enriched with Baum data where available.
    
    Args:
        durr_gdf: GeoDataFrame from Dürr et al. (2011)
        baum_df: Optional DataFrame from Baum et al. (2024)
    
    Returns:
        List of GeoJSON features
    """
    features = []
    
    # Group by basin and aggregate
    for idx, row in durr_gdf.iterrows():
        # Get centroid for point representation
        centroid = row.geometry.centroid
        
        # Extract properties
        properties = {
            "name": row['RECORDNAME'],
            "type": SIMPLE_TYPE_MAP.get(row['FIN_TYP'], "Unknown"),  # Simple type for frontend
            "type_detailed": DURR_TYPE_MAP.get(row['FIN_TYP'], "Unknown"),  # Detailed type
            "type_code": int(row['FIN_TYP']),
            "basin_area_km2": round(row['BASINAREA'], 2) if pd.notna(row['BASINAREA']) else None,
            "sea_name": row['SEANAME'] if pd.notna(row['SEANAME']) else None,
            "ocean_name": row['OCEANNAME'] if pd.notna(row['OCEANNAME']) else None,
            "data_source": "Dürr et al. (2011)",
            "data_source_doi": "10.1007/s12237-011-9381-y"
        }
        
        # Try to match with Baum data if available
        if baum_df is not None:
            # Simple name matching (could be improved with fuzzy matching)
            baum_match = baum_df[
                baum_df['Embayment'].str.lower().str.contains(
                    row['RECORDNAME'].lower(), na=False
                )
            ]
            if len(baum_match) > 0:
                baum_row = baum_match.iloc[0]
                properties.update({
                    "baum_embayment_name": baum_row['Embayment'],
                    "baum_mouth_width_m": baum_row['Lm'],
                    "baum_length_m": baum_row['Lb'],
                    "baum_geomorphotype": baum_row['Geomorphotype'],
                    "baum_data_source": "Baum et al. (2024)"
                })
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [round(centroid.x, 4), round(centroid.y, 4)]
            },
            "properties": properties
        }
        
        features.append(feature)
    
    return features


def create_basin_polygon_features(durr_gdf, baum_df=None):
    """
    Create GeoJSON features with basin polygons from Dürr data.
    
    Args:
        durr_gdf: GeoDataFrame from Dürr et al. (2011) with Polygon geometries
        baum_df: Optional DataFrame from Baum et al. (2024)
    
    Returns:
        List of GeoJSON features with Polygon/MultiPolygon geometries
    """
    features = []
    
    for idx, row in durr_gdf.iterrows():
        # Extract properties (same as point features)
        properties = {
            "name": row['RECORDNAME'],
            "type": SIMPLE_TYPE_MAP.get(row['FIN_TYP'], "Unknown"),
            "type_detailed": DURR_TYPE_MAP.get(row['FIN_TYP'], "Unknown"),
            "type_code": int(row['FIN_TYP']),
            "basin_area_km2": round(row['BASINAREA'], 2) if pd.notna(row['BASINAREA']) else None,
            "sea_name": row['SEANAME'] if pd.notna(row['SEANAME']) else None,
            "ocean_name": row['OCEANNAME'] if pd.notna(row['OCEANNAME']) else None,
            "data_source": "Dürr et al. (2011)",
            "data_source_doi": "10.1007/s12237-011-9381-y"
        }
        
        # Try to match with Baum data if available
        if baum_df is not None:
            baum_match = baum_df[
                baum_df['Embayment'].str.lower().str.contains(
                    row['RECORDNAME'].lower(), na=False
                )
            ]
            if len(baum_match) > 0:
                baum_row = baum_match.iloc[0]
                properties.update({
                    "baum_embayment_name": baum_row['Embayment'],
                    "baum_mouth_width_m": baum_row['Lm'],
                    "baum_length_m": baum_row['Lb'],
                    "baum_geomorphotype": baum_row['Geomorphotype'],
                    "baum_data_source": "Baum et al. (2024)"
                })
        
        # Use the actual basin polygon geometry
        # Convert to GeoJSON format (preserves Polygon or MultiPolygon)
        geometry = row.geometry.__geo_interface__
        
        # Round coordinates to 4 decimal places for file size optimization
        def round_coords(coords):
            if isinstance(coords[0], (list, tuple)):
                return [round_coords(c) for c in coords]
            else:
                return [round(coords[0], 4), round(coords[1], 4)]
        
        if geometry['type'] == 'Polygon':
            geometry['coordinates'] = [round_coords(ring) for ring in geometry['coordinates']]
        elif geometry['type'] == 'MultiPolygon':
            geometry['coordinates'] = [[round_coords(ring) for ring in polygon] for polygon in geometry['coordinates']]
        
        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }
        
        features.append(feature)
    
    return features


def create_coastline_features(coastline_gdf):
    """
    Create GeoJSON features from Dürr coastline data for coastal segmentation view.
    
    Args:
        coastline_gdf: GeoDataFrame from typology_coastline.shp
    
    Returns:
        List of GeoJSON features with LineString geometries
    """
    features = []
    
    for idx, row in coastline_gdf.iterrows():
        # Extract properties
        properties = {
            "type": SIMPLE_TYPE_MAP.get(row['FIN_TYP'], "Unknown"),
            "type_detailed": DURR_TYPE_MAP.get(row['FIN_TYP'], "Unknown"),
            "type_code": int(row['FIN_TYP']),
            "length_km": round(row['LENGTH'], 2) if pd.notna(row['LENGTH']) else None,
            "coastline_id": idx,
            "data_source": "Dürr et al. (2011) - Coastal Typology",
            "data_source_doi": "10.1007/s12237-011-9381-y"
        }
        
        # Convert geometry to GeoJSON format
        coords = [[round(x, 4), round(y, 4)] for x, y in row.geometry.coords]
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            },
            "properties": properties
        }
        
        features.append(feature)
    
    return features

def main():
    """Main function to process estuary data and generate GeoJSON output."""
    print("=" * 60)
    print("Processing Real Estuary Data - ALL GLOBAL ESTUARIES")
    print("=" * 60)
    
    # Determine base path
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent
    data_dir = base_dir / 'data'
    
    # Load Dürr et al. (2011) shapefile
    durr_shapefile = data_dir / 'Worldwide-typology-Shapefile-Durr_2011' / 'typology_catchments.shp'
    if not durr_shapefile.exists():
        print(f"Error: Dürr shapefile not found at {durr_shapefile}", file=sys.stderr)
        sys.exit(1)
    
    durr_gdf = load_durr_data(str(durr_shapefile))
    
    # Load Baum et al. (2024) CSV (optional)
    baum_csv = data_dir / 'Large-estuaries-Baum_2024' / 'Baum_2024_Geomorphology.csv'
    baum_df = None
    if baum_csv.exists():
        baum_df = load_baum_data(str(baum_csv))
    else:
        print(f"Warning: Baum CSV not found at {baum_csv}, skipping enrichment")
    
    # Process ALL estuaries (no sampling limit)
    print(f"\nProcessing ALL {len(durr_gdf)} estuaries for full global coverage...")
    
    # Create GeoJSON features for point view (estuary catchments)
    print("\nCreating GeoJSON features for estuary points...")
    features = create_estuary_features(durr_gdf, baum_df)
    
    # Create GeoJSON structure for points
    estuary_data = {
        "type": "FeatureCollection",
        "metadata": {
            "data_sources": [
                {
                    "name": "Dürr et al. (2011)",
                    "title": "Worldwide typology of nearshore coastal systems",
                    "doi": "10.1007/s12237-011-9381-y",
                    "description": "Primary typology and geometry source"
                },
                {
                    "name": "Baum et al. (2024)",
                    "title": "Large structural estuaries",
                    "description": "Supplementary morphometry data"
                }
            ],
            "note": "Full global dataset - all ~6,200+ estuaries from Dürr et al. (2011)",
            "gcc_note": "GCC (Athanasiou et al. 2024) geophysical data can be added by downloading from https://zenodo.org/records/11072020",
            "generated_date": pd.Timestamp.now().isoformat()
        },
        "features": features
    }
    
    # Output estuaries to data directory
    output_path = data_dir / 'estuaries.geojson'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(estuary_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Generated {len(features)} estuary points")
    print(f"✓ Output saved to: {output_path}")
    
    # Create basin polygon features
    print("\n" + "=" * 60)
    print("Processing Basin Polygon Data")
    print("=" * 60)
    print("\nCreating GeoJSON features for basin polygons...")
    
    basin_features = create_basin_polygon_features(durr_gdf, baum_df)
    
    # Create GeoJSON structure for basins
    basin_data = {
        "type": "FeatureCollection",
        "metadata": {
            "data_sources": [
                {
                    "name": "Dürr et al. (2011)",
                    "title": "Worldwide typology of nearshore coastal systems",
                    "doi": "10.1007/s12237-011-9381-y",
                    "description": "Primary typology and basin geometry source"
                },
                {
                    "name": "Baum et al. (2024)",
                    "title": "Large structural estuaries",
                    "description": "Supplementary morphometry data"
                }
            ],
            "note": "Full global dataset - all ~6,200+ estuary basin polygons from Dürr et al. (2011)",
            "visualization_note": "Basin polygons show complete drainage basins for each estuary",
            "generated_date": pd.Timestamp.now().isoformat()
        },
        "features": basin_features
    }
    
    # Output basin polygons to data directory
    basin_output_path = data_dir / 'basins.geojson'
    
    with open(basin_output_path, 'w', encoding='utf-8') as f:
        json.dump(basin_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Generated {len(basin_features)} basin polygons")
    print(f"✓ Output saved to: {basin_output_path}")
    
    # Also save as GeoPackage for efficient storage
    print("\nSaving basin polygons as GeoPackage...")
    durr_gdf_with_properties = durr_gdf.copy()
    
    # Remove duplicate columns before saving
    durr_gdf_with_properties = durr_gdf_with_properties.loc[:, ~durr_gdf_with_properties.columns.duplicated()]
    
    durr_gdf_with_properties['type'] = durr_gdf_with_properties['FIN_TYP'].map(SIMPLE_TYPE_MAP).fillna('Unknown')
    durr_gdf_with_properties['type_detailed'] = durr_gdf_with_properties['FIN_TYP'].map(DURR_TYPE_MAP).fillna('Unknown')
    
    gpkg_output_path = data_dir / 'basins.gpkg'
    durr_gdf_with_properties.to_file(str(gpkg_output_path), driver='GPKG', layer='estuary_basins')
    
    print(f"✓ GeoPackage saved to: {gpkg_output_path}")
    
    # Create simplified version for web display
    print("\nCreating simplified basin polygons for web display...")
    durr_gdf_simplified = durr_gdf.copy()
    durr_gdf_simplified['geometry'] = durr_gdf_simplified.geometry.simplify(tolerance=0.05, preserve_topology=True)
    
    basin_features_simplified = create_basin_polygon_features(durr_gdf_simplified, baum_df)
    
    # Create GeoJSON structure for simplified basins
    basin_data_simplified = {
        "type": "FeatureCollection",
        "metadata": {
            "data_sources": [
                {
                    "name": "Dürr et al. (2011)",
                    "title": "Worldwide typology of nearshore coastal systems",
                    "doi": "10.1007/s12237-011-9381-y",
                    "description": "Primary typology and basin geometry source"
                },
                {
                    "name": "Baum et al. (2024)",
                    "title": "Large structural estuaries",
                    "description": "Supplementary morphometry data"
                }
            ],
            "note": "Simplified basin polygons (tolerance=0.05) optimized for web display",
            "full_resolution_note": "Full resolution data available in basins.geojson and basins.gpkg",
            "visualization_note": "Basin polygons show complete drainage basins for each estuary",
            "generated_date": pd.Timestamp.now().isoformat()
        },
        "features": basin_features_simplified
    }
    
    # Output simplified basin polygons (no indent for smaller file size)
    basin_simplified_output_path = data_dir / 'basins_simplified.geojson'
    
    with open(basin_simplified_output_path, 'w', encoding='utf-8') as f:
        json.dump(basin_data_simplified, f, ensure_ascii=False)
    
    print(f"✓ Generated {len(basin_features_simplified)} simplified basin polygons")
    print(f"✓ Output saved to: {basin_simplified_output_path}")
    
    # Process coastline data for coastal segmentation mode
    print("\n" + "=" * 60)
    print("Processing Coastal Segmentation Data")
    print("=" * 60)
    
    coastline_shapefile = data_dir / 'Worldwide-typology-Shapefile-Durr_2011' / 'typology_coastline.shp'
    if coastline_shapefile.exists():
        print(f"Loading coastline shapefile: {coastline_shapefile}")
        coastline_gdf = gpd.read_file(str(coastline_shapefile))
        
        # Filter to meaningful coastal types (same as catchments)
        valid_types = [1, 2, 3, 4, 5, 6]
        coastline_gdf = coastline_gdf[coastline_gdf['FIN_TYP'].isin(valid_types)].copy()
        
        print(f"Found {len(coastline_gdf)} valid coastline segments")
        
        # Create GeoJSON features for coastline view
        print("\nCreating GeoJSON features for coastal segments...")
        coastline_features = create_coastline_features(coastline_gdf)
        
        # Create GeoJSON structure for coastline
        coastline_data = {
            "type": "FeatureCollection",
            "metadata": {
                "data_sources": [
                    {
                        "name": "Dürr et al. (2011)",
                        "title": "Worldwide typology of nearshore coastal systems - Coastline",
                        "doi": "10.1007/s12237-011-9381-y",
                        "description": "Global coastal segmentation by estuary type"
                    }
                ],
                "note": "Coastal segments colored by estuary type for global visualization",
                "generated_date": pd.Timestamp.now().isoformat()
            },
            "features": coastline_features
        }
        
        # Output coastline to data directory
        coastline_output_path = data_dir / 'coastline.geojson'
        
        with open(coastline_output_path, 'w', encoding='utf-8') as f:
            json.dump(coastline_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Generated {len(coastline_features)} coastline segments")
        print(f"✓ Output saved to: {coastline_output_path}")
    else:
        print(f"Warning: Coastline shapefile not found at {coastline_shapefile}, skipping coastal mode")
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("Summary Statistics")
    print("=" * 60)
    
    types = {}
    for feature in features:
        estuary_type = feature['properties']['type']
        types[estuary_type] = types.get(estuary_type, 0) + 1
    
    print(f"\nTotal estuaries: {len(features)}")
    print("\nEstuary types distribution:")
    for estuary_type, count in sorted(types.items()):
        print(f"  {estuary_type}: {count}")
    
    print("\n" + "=" * 60)
    print("Data processing complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
