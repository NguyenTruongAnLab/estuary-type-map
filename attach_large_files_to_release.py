#!/usr/bin/env python3
"""
GitHub Release with Large Files Attachment
=========================================

Auto-generated script to create GitHub release v1.0.0 with large file attachments

Usage: python attach_large_files_to_release.py
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RELEASE_TAG = "v1.0.0"
RELEASE_TITLE = "v1.0.0 - High-Resolution Global Tidal Basin Atlas"

# Large files to attach (generated 2025-10-14 15:19)
LARGE_FILES = [
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\hydrosheds\RiverATLAS_v10_QGIS.gpkg",
        'name': "RiverATLAS_v10_QGIS.gpkg",
        'size_mb': 7678.9
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\OSM-Water-Layer-Yamazaki_2021\OSM_WaterLayer.pbf",
        'name': "OSM_WaterLayer.pbf",
        'size_mb': 6677.5
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_reaches_AF_EPSG4326.gpkg",
        'name': "GRITv06_reaches_AF_EPSG4326.gpkg",
        'size_mb': 2782.8
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_reaches_AS_EPSG4326.gpkg",
        'name': "GRITv06_reaches_AS_EPSG4326.gpkg",
        'size_mb': 2537.5
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\hydrosheds\LakeATLAS_v10_QGIS.gpkg",
        'name': "LakeATLAS_v10_QGIS.gpkg",
        'size_mb': 2503.6
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\rivers_grit_reaches_classified_af.gpkg",
        'name': "rivers_grit_reaches_classified_af.gpkg",
        'size_mb': 2371.4
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\rivers_grit_reaches_classified_as.gpkg",
        'name': "rivers_grit_reaches_classified_as.gpkg",
        'size_mb': 2172.0
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_reaches_NA_EPSG4326.gpkg",
        'name': "GRITv06_reaches_NA_EPSG4326.gpkg",
        'size_mb': 2075.3
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\rivers_grit_reaches_classified_na.gpkg",
        'name': "rivers_grit_reaches_classified_na.gpkg",
        'size_mb': 1773.9
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_reaches_SA_EPSG4326.gpkg",
        'name': "GRITv06_reaches_SA_EPSG4326.gpkg",
        'size_mb': 1694.1
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\rivers_grit_reaches_classified_sa.gpkg",
        'name': "rivers_grit_reaches_classified_sa.gpkg",
        'size_mb': 1455.8
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_reaches_SI_EPSG4326.gpkg",
        'name': "GRITv06_reaches_SI_EPSG4326.gpkg",
        'size_mb': 1365.4
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GlobSalt\GlobSalt_v2.0.csv",
        'name': "GlobSalt_v2.0.csv",
        'size_mb': 1238.3
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_segments_AF_EPSG4326.gpkg",
        'name': "GRITv06_segments_AF_EPSG4326.gpkg",
        'size_mb': 1205.7
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_reaches_EU_EPSG4326.gpkg",
        'name': "GRITv06_reaches_EU_EPSG4326.gpkg",
        'size_mb': 1204.9
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\rivers_grit_reaches_classified_si.gpkg",
        'name': "rivers_grit_reaches_classified_si.gpkg",
        'size_mb': 1163.5
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\rivers_grit_segments_classified_af.gpkg",
        'name': "rivers_grit_segments_classified_af.gpkg",
        'size_mb': 1160.9
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_segments_AS_EPSG4326.gpkg",
        'name': "GRITv06_segments_AS_EPSG4326.gpkg",
        'size_mb': 1156.5
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\rivers_grit_segments_classified_as.gpkg",
        'name': "rivers_grit_segments_classified_as.gpkg",
        'size_mb': 1112.7
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_component_catchments_NA_EPSG4326.gpkg",
        'name': "GRITv06_component_catchments_NA_EPSG4326.gpkg",
        'size_mb': 1061.9
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\rivers_grit_reaches_classified_eu.gpkg",
        'name': "rivers_grit_reaches_classified_eu.gpkg",
        'size_mb': 1031.9
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_reaches_SP_EPSG4326.gpkg",
        'name': "GRITv06_reaches_SP_EPSG4326.gpkg",
        'size_mb': 1028.7
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_segments_NA_EPSG4326.gpkg",
        'name': "GRITv06_segments_NA_EPSG4326.gpkg",
        'size_mb': 965.2
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\rivers_grit_segments_classified_na.gpkg",
        'name': "rivers_grit_segments_classified_na.gpkg",
        'size_mb': 926.7
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_component_catchments_AS_EPSG4326.gpkg",
        'name': "GRITv06_component_catchments_AS_EPSG4326.gpkg",
        'size_mb': 915.1
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\rivers_grit_reaches_classified_sp.gpkg",
        'name': "rivers_grit_reaches_classified_sp.gpkg",
        'size_mb': 871.0
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\hydrosheds\BasinATLAS_v10_lev08_QGIS.gpkg",
        'name': "BasinATLAS_v10_lev08_QGIS.gpkg",
        'size_mb': 825.7
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_segments_SA_EPSG4326.gpkg",
        'name': "GRITv06_segments_SA_EPSG4326.gpkg",
        'size_mb': 777.5
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\rivers_grit_segments_classified_sa.gpkg",
        'name': "rivers_grit_segments_classified_sa.gpkg",
        'size_mb': 749.2
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_component_catchments_EU_EPSG4326.gpkg",
        'name': "GRITv06_component_catchments_EU_EPSG4326.gpkg",
        'size_mb': 667.7
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_segments_SI_EPSG4326.gpkg",
        'name': "GRITv06_segments_SI_EPSG4326.gpkg",
        'size_mb': 654.7
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_component_catchments_SP_EPSG4326.gpkg",
        'name': "GRITv06_component_catchments_SP_EPSG4326.gpkg",
        'size_mb': 637.0
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_component_catchments_AF_EPSG4326.gpkg",
        'name': "GRITv06_component_catchments_AF_EPSG4326.gpkg",
        'size_mb': 633.7
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\rivers_grit_segments_classified_si.gpkg",
        'name': "rivers_grit_segments_classified_si.gpkg",
        'size_mb': 626.6
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\esri_water_bodies\World_Water_Bodies.lpk",
        'name': "World_Water_Bodies.lpk",
        'size_mb': 600.4
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\OSM-Water-Layer-Yamazaki_2021\OSM_WaterLayer_POLYGONS.gpkg",
        'name': "OSM_WaterLayer_POLYGONS.gpkg",
        'size_mb': 574.9
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_segments_EU_EPSG4326.gpkg",
        'name': "GRITv06_segments_EU_EPSG4326.gpkg",
        'size_mb': 537.1
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\rivers_grit_segments_classified_eu.gpkg",
        'name': "rivers_grit_segments_classified_eu.gpkg",
        'size_mb': 517.3
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\tidal_basins_distance_based.gpkg",
        'name': "tidal_basins_distance_based.gpkg",
        'size_mb': 495.9
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_segments_SP_EPSG4326.gpkg",
        'name': "GRITv06_segments_SP_EPSG4326.gpkg",
        'size_mb': 456.0
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\rivers_grit_segments_classified_sp.gpkg",
        'name': "rivers_grit_segments_classified_sp.gpkg",
        'size_mb': 438.3
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\hydrosheds\BasinATLAS_v10_lev07_QGIS.gpkg",
        'name': "BasinATLAS_v10_lev07_QGIS.gpkg",
        'size_mb': 401.8
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_component_catchments_SA_EPSG4326.gpkg",
        'name': "GRITv06_component_catchments_SA_EPSG4326.gpkg",
        'size_mb': 394.0
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\DynQual-Jones_2023\channelStorage_annualAvg_1980_2019.nc",
        'name': "channelStorage_annualAvg_1980_2019.nc",
        'size_mb': 297.3
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\DynQual-Jones_2023\discharge_annualAvg_1980_2019.nc",
        'name': "discharge_annualAvg_1980_2019.nc",
        'size_mb': 292.9
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_component_catchments_SI_EPSG4326.gpkg",
        'name': "GRITv06_component_catchments_SI_EPSG4326.gpkg",
        'size_mb': 275.4
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_segments_simple_GLOBAL_EPSG4326.gpkg",
        'name': "GRITv06_segments_simple_GLOBAL_EPSG4326.gpkg",
        'size_mb': 226.9
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\DynQual-Jones_2023\salinity_annualAvg_1980_2019.nc",
        'name': "salinity_annualAvg_1980_2019.nc",
        'size_mb': 209.3
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GCC-Panagiotis-Athanasiou_2024\GCC_geophysical.csv",
        'name': "GCC_geophysical.csv",
        'size_mb': 203.5
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\DynQual-Jones_2023\waterTemperature_annualAvg_1980_2019.nc",
        'name': "waterTemperature_annualAvg_1980_2019.nc",
        'size_mb': 198.1
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\tidal_basins_basinatlas_durr_analysis.gpkg",
        'name': "tidal_basins_basinatlas_durr_analysis.gpkg",
        'size_mb': 170.6
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GCC-Panagiotis-Athanasiou_2024\GCC_hydrometeorological.csv",
        'name': "GCC_hydrometeorological.csv",
        'size_mb': 141.0
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\tidal_basins_topology_traced_full.gpkg",
        'name': "tidal_basins_topology_traced_full.gpkg",
        'size_mb': 135.2
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\tidal_basins_connected_lev07.gpkg",
        'name': "tidal_basins_connected_lev07.gpkg",
        'size_mb': 122.1
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GRIT-Michel_2025\GRITv06_sinks_GLOBAL_EPSG4326.gpkg",
        'name': "GRITv06_sinks_GLOBAL_EPSG4326.gpkg",
        'size_mb': 112.7
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\tidal_basins_river_based_lev07.gpkg",
        'name': "tidal_basins_river_based_lev07.gpkg",
        'size_mb': 111.4
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\tidal_basins_grit_validated.gpkg",
        'name': "tidal_basins_grit_validated.gpkg",
        'size_mb': 96.8
    },
    {
        'path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\raw\GCC-Panagiotis-Athanasiou_2024\GCC_socioeconomic.csv",
        'name': "GCC_socioeconomic.csv",
        'size_mb': 72.8
    },
]

def run_command(command):
    """Run shell command"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def main():
    print("🚀 Creating GitHub release with large files...")
    
    # Check if gh CLI is available
    success, _, _ = run_command("gh --version")
    if not success:
        print("❌ GitHub CLI (gh) not found. Please install it:")
        print("   https://cli.github.com/")
        return False
    
    # Create release
    release_notes_file = BASE_DIR / "docs" / "RELEASE_NOTES_v1.0.0.md"
    
    print(f"📝 Creating release {RELEASE_TAG}...")
    cmd = f'gh release create {RELEASE_TAG} --title "{RELEASE_TITLE}" --notes-file "{release_notes_file}"'
    success, output, error = run_command(cmd)
    
    if not success:
        print(f"❌ Failed to create release: {error}")
        return False
    
    print("✅ Release created successfully")
    
    # Attach large files
    for file_info in LARGE_FILES:
        file_path = Path(file_info['path'])
        if file_path.exists():
            print(f"📎 Attaching {file_info['name']} ({file_info['size_mb']} MB)...")
            cmd = f'gh release upload {RELEASE_TAG} "{file_path}"'
            success, output, error = run_command(cmd)
            
            if success:
                print(f"   ✅ Uploaded {file_info['name']}")
            else:
                print(f"   ❌ Failed to upload {file_info['name']}: {error}")
        else:
            print(f"   ⚠️ File not found: {file_path}")
    
    print("\n🎉 Release with large files complete!")
    print(f"   🌐 View release: https://github.com/NguyenTruongAnLab/estuary-type-map/releases/tag/{RELEASE_TAG}")
    
    return True

if __name__ == "__main__":
    main()
