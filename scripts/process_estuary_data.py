#!/usr/bin/env python3
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
            "type": DURR_TYPE_MAP.get(row['FIN_TYP'], "Unknown"),
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

def main():
    """Main function to process estuary data and generate GeoJSON output."""
    print("=" * 60)
    print("Processing Real Estuary Data")
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
    
    # Sample a reasonable number of estuaries for the map
    # (Too many points would clutter the visualization)
    print("\nSelecting representative estuaries...")
    
    # Prioritize larger basins and diverse types
    durr_sample = durr_gdf.sort_values('BASINAREA', ascending=False).head(100)
    
    print(f"Selected {len(durr_sample)} estuaries for visualization")
    
    # Create GeoJSON features
    print("\nCreating GeoJSON features...")
    features = create_estuary_features(durr_sample, baum_df)
    
    # Create GeoJSON structure
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
            "note": "Laruelle et al. (2025) used only for validation and statistics, not as raw data source",
            "gcc_note": "GCC (Athanasiou et al. 2024) geophysical data can be added by downloading from https://zenodo.org/records/11072020",
            "generated_date": pd.Timestamp.now().isoformat()
        },
        "features": features
    }
    
    # Output to data directory
    output_path = data_dir / 'estuaries.geojson'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(estuary_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Generated {len(features)} estuaries")
    print(f"✓ Output saved to: {output_path}")
    
    # Print summary statistics
    types = {}
    for feature in features:
        estuary_type = feature['properties']['type']
        types[estuary_type] = types.get(estuary_type, 0) + 1
    
    print("\nEstuary types distribution:")
    for estuary_type, count in sorted(types.items()):
        print(f"  {estuary_type}: {count}")
    
    print("\n" + "=" * 60)
    print("Data processing complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
