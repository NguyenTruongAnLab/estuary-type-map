#!/usr/bin/env python3
"""
Create Web-Optimized Tidal Basin GeoJSON
=========================================

PURPOSE: Convert high-resolution tidal basins GPKG to web-ready GeoJSON

Author: Global Water Body Surface Area Atlas Project
Date: October 14, 2025
"""

import geopandas as gpd
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
WEB_DIR = BASE_DIR / 'data' / 'web'
WEB_DIR.mkdir(exist_ok=True)

# Input
INPUT_FILE = PROCESSED_DIR / 'tidal_basins_river_based_lev07.gpkg'

# Outputs
OUTPUT_FULL = WEB_DIR / 'tidal_basins_precise.geojson'
OUTPUT_STATS = WEB_DIR / 'tidal_basins_stats.json'

print(f"\n{'='*80}")
print("Creating Web-Optimized Tidal Basin GeoJSON")
print(f"{'='*80}\n")

# Load data
print(f"📂 Loading: {INPUT_FILE.name}")
gdf = gpd.read_file(INPUT_FILE)
print(f"   Loaded {len(gdf):,} basins")

# Simplify geometries for web
print(f"\n🔧 Simplifying geometries...")
gdf['geometry'] = gdf.geometry.simplify(0.02)  # ~2.2 km tolerance

# Keep only essential columns for web
essential_cols = [
    'HYBAS_ID', 'basin_area_km2', 'distance_to_coast_km', 
    'stream_order', 'estuary_name', 'estuary_type', 'is_seed', 'geometry'
]
web_gdf = gdf[[col for col in essential_cols if col in gdf.columns]].copy()

# Calculate statistics
print(f"\n📊 Calculating statistics...")
stats = {
    'total_basins': len(web_gdf),
    'total_area_km2': float(web_gdf['basin_area_km2'].sum()),
    'by_type': {}
}

for etype, group in web_gdf.groupby('estuary_type'):
    stats['by_type'][etype] = {
        'count': len(group),
        'area_km2': float(group['basin_area_km2'].sum()),
        'percentage': float(len(group) / len(web_gdf) * 100)
    }

print(f"   Total basins: {stats['total_basins']:,}")
print(f"   Total area: {stats['total_area_km2']:,.0f} km²")
print(f"\n   By estuary type:")
for etype, data in sorted(stats['by_type'].items(), key=lambda x: x[1]['area_km2'], reverse=True):
    print(f"     {etype}: {data['count']:,} basins ({data['percentage']:.1f}%)")

# Save GeoJSON
print(f"\n💾 Saving web GeoJSON...")
web_gdf.to_file(OUTPUT_FULL, driver='GeoJSON')
size_mb = OUTPUT_FULL.stat().st_size / (1024*1024)
print(f"✅ Saved: {OUTPUT_FULL.name} ({size_mb:.1f} MB)")

# Save statistics
with open(OUTPUT_STATS, 'w') as f:
    json.dump(stats, f, indent=2)
print(f"✅ Saved: {OUTPUT_STATS.name}")

print(f"\n{'='*80}")
print("✅ WEB OPTIMIZATION COMPLETE!")
print(f"{'='*80}\n")
