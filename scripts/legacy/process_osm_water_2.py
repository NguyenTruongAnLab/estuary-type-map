
"""Process Yamazaki OSM Water Layer with Interactive Visualization
===================================================================

Extract water body polygons with basin level comparison and 
interactive Plotly visualizations.

Features:
- Processes both basin level 06 and level 08

Usage:
  python scripts/process_osm_water_2.py --process-both-levels
  
  # Then open in browser:
  data/processed/comparison_map.html
  data/processed/comparison_stats.html
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence, Dict, List

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely import set_precision

# Plotly imports
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("⚠️  Plotly not installed. Install for visualizations:")
    print("   pip install plotly kaleido")

LOG = logging.getLogger("process_osm_water")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw" / "OSM-Water-Layer-Yamazaki_2021"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OPTIMIZED_DIR = BASE_DIR / "data" / "optimized"
WEB_DIR = BASE_DIR / "data" / "web"
TEMP_DIR = BASE_DIR / "data" / "temp"

DEFAULT_PBF = RAW_DIR / "OSM_WaterLayer.pbf"

CRS_SOURCE = "EPSG:4326"
CRS_EQUAL_AREA = "EPSG:6933"

SIMPLIFY_LOW_ZOOM = 0.05
SIMPLIFY_HIGH_ZOOM = 0.01
COORD_PRECISION = 4


@dataclass
class OutputConfig:
    """Export targets."""
    gpkg: Path
    metadata_json: Path
    optimized_geojson: Path
    web_low_zoom: Path
    web_high_zoom: Path
    overwrite: bool = False


@dataclass
class ProcessingConfig:
    """Runtime configuration."""
    pbf_path: Path = DEFAULT_PBF
    hydrosheds_basins: Path = None
    basin_level: int = 8
    process_both_levels: bool = False
    coastal_buffer_km: float = 50.0
    include_lakes: bool = False
    min_area_km2: float = 0.05
    outputs: OutputConfig = None
    create_visualizations: bool = True


def check_ogr2ogr():
    """Verify ogr2ogr is available."""
    if not shutil.which("ogr2ogr"):
        LOG.error("="*80)
        LOG.error("ERROR: ogr2ogr not found!")
        LOG.error("="*80)
        LOG.error("Install GDAL: conda install -c conda-forge gdal")
        LOG.error("="*80)
        raise RuntimeError("ogr2ogr not found in PATH")
    
    result = subprocess.run(
        ["ogr2ogr", "--version"],
        capture_output=True,
        text=True
    )
    version = result.stdout.strip() if result.stdout else "unknown"
    LOG.info(f"✓ Found ogr2ogr: {version}")


def find_basin_file(level: int) -> Optional[Path]:
    """Find basin file for specified level."""
    candidates = [
        PROCESSED_DIR / f"basins_coastal_lev{level:02d}.gpkg",
        BASE_DIR / "data" / "hydrosheds" / "processed" / f"basins_coastal_lev{level:02d}.gpkg",
    ]
    
    for path in candidates:
        if path.exists():
            LOG.info(f"✓ Found basin level {level} at: {path}")
            return path
    
    return None


def is_geometry_valid_coordinates(geom) -> bool:
    """Check if geometry has valid coordinates."""
    if geom is None or geom.is_empty:
        return False
    
    try:
        coords = np.array(geom.coords if hasattr(geom, 'coords') else 
                         list(geom.exterior.coords) if hasattr(geom, 'exterior') else [])
        
        if len(coords) == 0:
            return False
        
        return not (np.isnan(coords).any() or np.isinf(coords).any())
    
    except Exception:
        return False


def load_and_prepare_coastal_basins(
    basin_file: Path,
    basin_level: int,
    buffer_km: float
) -> Path:
    """Load basins with corrupt geometry filtering."""
    LOG.info("="*80)
    LOG.info(f"STEP 1: Preparing clipping polygon (Level {basin_level})")
    LOG.info("="*80)
    
    LOG.info(f"Loading: {basin_file.name}")
    basins = gpd.read_file(basin_file)
    
    if basins.empty:
        raise ValueError("HydroSHEDS basins file is empty")
    
    LOG.info(f"✓ Loaded {len(basins)} coastal basins")
    
    # Filter corrupt geometries
    LOG.info("Filtering corrupt geometries...")
    basins = basins[basins.geometry.notnull()].copy()
    valid_mask = basins.geometry.apply(is_geometry_valid_coordinates)
    removed = (~valid_mask).sum()
    basins = basins[valid_mask].copy()
    
    LOG.info(f"✓ Removed {removed} corrupt geometries")
    LOG.info(f"✓ Remaining: {len(basins)} valid basins")
    
    if basins.empty:
        raise ValueError("No valid basins after filtering!")
    
    basins["geometry"] = basins.geometry.buffer(0)
    
    # Buffer
    LOG.info(f"Buffering by {buffer_km} km...")
    basins_proj = basins.to_crs(CRS_EQUAL_AREA)
    buffer_m = buffer_km * 1000
    
    buffered = []
    failed = 0
    
    for geom in basins_proj.geometry:
        try:
            if is_geometry_valid_coordinates(geom):
                buf = geom.buffer(buffer_m)
                if buf and is_geometry_valid_coordinates(buf):
                    buffered.append(buf)
                else:
                    failed += 1
            else:
                failed += 1
        except:
            failed += 1
    
    LOG.info(f"✓ Buffered {len(buffered)} basins ({failed} failed)")
    
    basins_buffered = gpd.GeoDataFrame(
        geometry=buffered, crs=CRS_EQUAL_AREA
    ).to_crs(CRS_SOURCE)
    
    # Chunked union
    LOG.info("Merging basins (chunked)...")
    chunk_size = 100
    chunks = []
    
    for i in range(0, len(basins_buffered), chunk_size):
        try:
            from shapely.ops import unary_union
            chunk_union = unary_union(basins_buffered.iloc[i:i+chunk_size].geometry.tolist())
            if chunk_union and is_geometry_valid_coordinates(chunk_union):
                chunks.append(chunk_union)
        except:
            pass
    
    from shapely.ops import unary_union
    basins_union = unary_union(chunks).buffer(0)
    
    clip_file = TEMP_DIR / f"coastal_clip_lev{basin_level:02d}.geojson"
    gpd.GeoDataFrame(geometry=[basins_union], crs=CRS_SOURCE).to_file(clip_file, driver="GeoJSON")
    
    LOG.info(f"✓ Saved: {clip_file.name}")
    LOG.info("")
    return clip_file


def extract_with_ogr2ogr(
    pbf_path: Path,
    clip_file: Path,
    include_lakes: bool,
    output_gpkg: Path,
    basin_level: int
) -> None:
    """Extract water polygons using ogr2ogr."""
    LOG.info("="*80)
    LOG.info(f"STEP 2: Extracting water (Level {basin_level})")
    LOG.info("="*80)
    LOG.info(f"Expected time: 5-15 minutes")
    LOG.info("")
    
    start = time.time()
    
    sql = (
        "SELECT osm_id as id, name, "
        "CASE "
        "  WHEN waterway='riverbank' THEN 'riverbank' "
        "  WHEN waterway='river' THEN 'river' "
        "  WHEN natural='water' THEN 'water' "
        "  WHEN landuse='reservoir' THEN 'reservoir' "
        "  ELSE 'other' "
        "END as water_type "
        "FROM multipolygons "
        "WHERE (natural='water' OR waterway IS NOT NULL OR landuse='reservoir')"
    )
    
    if not include_lakes:
        sql += " AND (water IS NULL OR water NOT IN ('lake', 'pond'))"
    
    cmd = [
        "ogr2ogr", "-f", "GPKG", str(output_gpkg), str(pbf_path),
        "-clipsrc", str(clip_file), "-sql", sql, "-nln", "water_polygons",
        "-progress", "--config", "OGR_INTERLEAVED_READING", "YES",
        "--config", "OSM_MAX_TMPFILE_SIZE", "2000"
    ]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True, bufsize=1)
    
    for line in process.stdout:
        if "%" in line or "ERROR" in line:
            LOG.info(f"   {line.strip()}")
    
    process.wait()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd)
    
    LOG.info(f"✓ Complete! ({(time.time()-start)/60:.1f} minutes)")
    LOG.info("")


def post_process_water_polygons(
    input_gpkg: Path,
    min_area_km2: float,
    basin_level: int
) -> gpd.GeoDataFrame:
    """Post-process extracted polygons."""
    LOG.info("="*80)
    LOG.info(f"STEP 3: Post-processing (Level {basin_level})")
    LOG.info("="*80)
    
    water = gpd.read_file(input_gpkg)
    LOG.info(f"✓ Loaded {len(water)} polygons")
    
    if water.crs is None:
        water = water.set_crs(CRS_SOURCE)
    
    water["geometry"] = water.geometry.buffer(0)
    water = water[water.geometry.notnull()]
    water = water.explode(index_parts=False).reset_index(drop=True)
    
    water_proj = water.to_crs(CRS_EQUAL_AREA)
    water["area_km2"] = water_proj.geometry.area / 1e6
    
    water = water[water["area_km2"] >= min_area_km2]
    LOG.info(f"✓ Final: {len(water)} polygons, {water['area_km2'].sum():,.0f} km²")
    
    if "id" not in water.columns:
        water["id"] = water.index.astype(str)
    if "name" not in water.columns:
        water["name"] = ""
    
    water["geometry_type"] = water.geometry.geom_type
    water["data_source"] = "Yamazaki et al. 2017 OSM Water Layer v2.0"
    water["basin_level"] = basin_level
    water["generated_date"] = pd.Timestamp.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    LOG.info("")
    return water[[
        "id", "name", "water_type", "geometry_type", "area_km2",
        "data_source", "basin_level", "generated_date", "geometry"
    ]]


def export_outputs(gdf: gpd.GeoDataFrame, cfg: OutputConfig, level: int) -> None:
    """Export all outputs."""
    LOG.info("="*80)
    LOG.info(f"STEP 4: Exporting (Level {level})")
    LOG.info("="*80)
    
    if not cfg.gpkg.exists() or cfg.overwrite:
        gdf.to_file(cfg.gpkg, driver="GPKG")
        LOG.info(f"✓ Saved: {cfg.gpkg.name}")
    
    metadata = {
        "dataset_name": f"OSM Water (Level {level})",
        "basin_level": level,
        "records": int(len(gdf)),
        "total_area_km2": float(gdf["area_km2"].sum()),
        "generated_date": pd.Timestamp.utcnow().isoformat(),
    }
    
    cfg.metadata_json.write_text(json.dumps(metadata, indent=2))
    LOG.info(f"✓ Saved: {cfg.metadata_json.name}")
    LOG.info("")


def create_comparison_visualizations(stats_list: List[Dict], output_dir: Path) -> None:
    """Create interactive Plotly visualizations comparing basin levels."""
    
    if not PLOTLY_AVAILABLE or len(stats_list) < 2:
        return
    
    LOG.info("="*80)
    LOG.info("📊 Creating Interactive Visualizations")
    LOG.info("="*80)
    
    df = pd.DataFrame(stats_list)
    
    # === CHART 1: Comparison Bar Charts ===
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Number of Polygons',
            'Total Surface Area (km²)',
            'Processing Time (minutes)',
            'Average Polygon Size (km²)'
        ),
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    colors = ['#3498db', '#e74c3c']
    
    # Polygons
    fig.add_trace(
        go.Bar(
            x=[f"Level {int(l):02d}" for l in df['level']],
            y=df['polygons'],
            marker_color=colors,
            text=df['polygons'].apply(lambda x: f"{x:,}"),
            textposition='outside',
            name='Polygons'
        ),
        row=1, col=1
    )
    
    # Area
    fig.add_trace(
        go.Bar(
            x=[f"Level {int(l):02d}" for l in df['level']],
            y=df['total_area_km2'],
            marker_color=colors,
            text=df['total_area_km2'].apply(lambda x: f"{x:,.0f}"),
            textposition='outside',
            name='Area'
        ),
        row=1, col=2
    )
    
    # Processing time
    fig.add_trace(
        go.Bar(
            x=[f"Level {int(l):02d}" for l in df['level']],
            y=df['processing_time_min'],
            marker_color=colors,
            text=df['processing_time_min'].apply(lambda x: f"{x:.1f}"),
            textposition='outside',
            name='Time'
        ),
        row=2, col=1
    )
    
    # Average size
    avg_size = df['total_area_km2'] / df['polygons']
    fig.add_trace(
        go.Bar(
            x=[f"Level {int(l):02d}" for l in df['level']],
            y=avg_size,
            marker_color=colors,
            text=avg_size.apply(lambda x: f"{x:.3f}"),
            textposition='outside',
            name='Avg Size'
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        title_text="<b>Basin Level Comparison: Level 06 vs Level 08</b>",
        showlegend=False,
        height=800,
        font=dict(size=12)
    )
    
    # Save chart
    chart_file = output_dir / "comparison_stats.html"
    fig.write_html(str(chart_file))
    LOG.info(f"✓ Saved interactive chart: {chart_file.name}")
    
    # === CHART 2: Difference Analysis ===
    if len(df) == 2:
        diff_polygons = df.iloc[1]['polygons'] - df.iloc[0]['polygons']
        diff_area = df.iloc[1]['total_area_km2'] - df.iloc[0]['total_area_km2']
        diff_time = df.iloc[1]['processing_time_min'] - df.iloc[0]['processing_time_min']
        
        diff_pct_polygons = (diff_polygons / df.iloc[0]['polygons']) * 100
        diff_pct_area = (diff_area / df.iloc[0]['total_area_km2']) * 100
        diff_pct_time = (diff_time / df.iloc[0]['processing_time_min']) * 100
        
        fig_diff = go.Figure()
        
        metrics = ['Polygons', 'Area (km²)', 'Time (min)']
        absolute = [diff_polygons, diff_area, diff_time]
        percentage = [diff_pct_polygons, diff_pct_area, diff_pct_time]
        
        fig_diff.add_trace(go.Bar(
            x=metrics,
            y=absolute,
            name='Absolute Difference',
            marker_color=['#2ecc71' if v > 0 else '#e74c3c' for v in absolute],
            text=[f"{v:+,.0f}<br>({p:+.1f}%)" for v, p in zip(absolute, percentage)],
            textposition='outside'
        ))
        
        fig_diff.update_layout(
            title="<b>Level 08 vs Level 06: Differences</b>",
            yaxis_title="Difference (Level 08 - Level 06)",
            height=500,
            showlegend=False
        )
        
        diff_file = output_dir / "comparison_differences.html"
        fig_diff.write_html(str(diff_file))
        LOG.info(f"✓ Saved difference chart: {diff_file.name}")
    
    # === CHART 3: Sample Map (if data available) ===
    try:
        # Load a sample of data for visualization
        sample_files = []
        for stats in stats_list:
            gpkg_path = Path(stats['output_file'])
            if gpkg_path.exists():
                sample_files.append((stats['level'], gpkg_path))
        
        if len(sample_files) >= 2:
            LOG.info("Creating sample map comparison...")
            
            fig_map = make_subplots(
                rows=1, cols=2,
                subplot_titles=(
                    f"Level {int(sample_files[0][0]):02d}",
                    f"Level {int(sample_files[1][0]):02d}"
                ),
                specs=[[{'type': 'scattergeo'}, {'type': 'scattergeo'}]]
            )
            
            for idx, (level, gpkg) in enumerate(sample_files[:2]):
                # Load small sample
                water_sample = gpd.read_file(gpkg).sample(min(500, len(gpd.read_file(gpkg))))
                
                # Get centroids for plotting
                centroids = water_sample.geometry.centroid
                
                fig_map.add_trace(
                    go.Scattergeo(
                        lon=centroids.x,
                        lat=centroids.y,
                        mode='markers',
                        marker=dict(
                            size=water_sample['area_km2'].apply(lambda x: min(10, max(2, x/10))),
                            color=water_sample['area_km2'],
                            colorscale='Blues',
                            showscale=(idx == 0),
                            colorbar=dict(title="Area (km²)") if idx == 0 else None
                        ),
                        text=water_sample.apply(lambda r: f"{r['name']}<br>Area: {r['area_km2']:.2f} km²", axis=1),
                        hoverinfo='text',
                        name=f"Level {int(level):02d}"
                    ),
                    row=1, col=idx+1
                )
            
            fig_map.update_geos(
                projection_type="natural earth",
                showcoastlines=True,
                coastlinecolor="gray",
                showland=True,
                landcolor="lightgray",
                showcountries=True
            )
            
            fig_map.update_layout(
                title="<b>Spatial Distribution Comparison (500 samples each)</b>",
                height=600
            )
            
            map_file = output_dir / "comparison_map.html"
            fig_map.write_html(str(map_file))
            LOG.info(f"✓ Saved interactive map: {map_file.name}")
    
    except Exception as e:
        LOG.warning(f"Could not create map visualization: {e}")
    
    LOG.info("")
    LOG.info("="*80)
    LOG.info("📂 Open visualizations in your browser:")
    LOG.info(f"   {(output_dir / 'comparison_stats.html').resolve()}")
    LOG.info(f"   {(output_dir / 'comparison_differences.html').resolve()}")
    if (output_dir / 'comparison_map.html').exists():
        LOG.info(f"   {(output_dir / 'comparison_map.html').resolve()}")
    LOG.info("="*80)


def process_basin_level(cfg: ProcessingConfig, level: int) -> Optional[Dict]:
    """Process a single basin level."""
    
    LOG.info("")
    LOG.info("="*80)
    LOG.info(f"PROCESSING BASIN LEVEL {level}")
    LOG.info("="*80)
    
    start = time.time()
    
    basin_file = find_basin_file(level)
    if not basin_file:
        LOG.warning(f"Basin level {level} not found, skipping")
        return None
    
    suffix = f"_lev{level:02d}"
    outputs = OutputConfig(
        gpkg=PROCESSED_DIR / f"osm_water_polygons{suffix}.gpkg",
        metadata_json=PROCESSED_DIR / f"osm_water_polygons{suffix}_metadata.json",
        optimized_geojson=OPTIMIZED_DIR / f"osm_water_polygons{suffix}.geojson",
        web_low_zoom=WEB_DIR / f"osm_water_polygons{suffix}_z2-6.geojson",
        web_high_zoom=WEB_DIR / f"osm_water_polygons{suffix}_z7-10.geojson",
        overwrite=cfg.outputs.overwrite
    )
    
    try:
        clip_file = load_and_prepare_coastal_basins(basin_file, level, cfg.coastal_buffer_km)
        
        temp_gpkg = TEMP_DIR / f"osm_water_raw_lev{level:02d}.gpkg"
        
        if not temp_gpkg.exists() or outputs.overwrite:
            extract_with_ogr2ogr(cfg.pbf_path, clip_file, cfg.include_lakes, temp_gpkg, level)
        
        water = post_process_water_polygons(temp_gpkg, cfg.min_area_km2, level)
        export_outputs(water, outputs, level)
        
        elapsed = (time.time() - start) / 60
        
        return {
            'level': level,
            'polygons': len(water),
            'total_area_km2': float(water['area_km2'].sum()),
            'processing_time_min': elapsed,
            'output_file': str(outputs.gpkg)
        }
    
    except Exception as e:
        LOG.error(f"❌ Level {level} failed: {e}")
        return None


def run(cfg: ProcessingConfig) -> None:
    """Execute full workflow."""
    
    LOG.info("="*80)
    LOG.info("YAMAZAKI OSM WATER PROCESSOR WITH VISUALIZATION")
    LOG.info("="*80)
    LOG.info(f"Mode: {'BOTH levels (06 & 08)' if cfg.process_both_levels else f'Level {cfg.basin_level} only'}")
    LOG.info("="*80)
    LOG.info("")
    
    overall_start = time.time()
    
    check_ogr2ogr()
    
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    OPTIMIZED_DIR.mkdir(parents=True, exist_ok=True)
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    stats_list = []
    
    if cfg.process_both_levels:
        for level in [8, 6]:
            stats = process_basin_level(cfg, level)
            if stats:
                stats_list.append(stats)
    else:
        stats = process_basin_level(cfg, cfg.basin_level)
        if stats:
            stats_list.append(stats)
    
    elapsed = (time.time() - overall_start) / 60
    
    LOG.info("")
    LOG.info("="*80)
    LOG.info("✅ PROCESSING COMPLETE!")
    LOG.info("="*80)
    LOG.info(f"Total runtime: {elapsed:.1f} minutes")
    LOG.info(f"Levels processed: {len(stats_list)}")
    
    if len(stats_list) >= 2 and cfg.create_visualizations:
        create_comparison_visualizations(stats_list, PROCESSED_DIR)
    
    LOG.info("")


def parse_args(argv: Optional[Sequence[str]] = None) -> ProcessingConfig:
    """Parse arguments."""
    
    parser = argparse.ArgumentParser(
        description="Process OSM Water Layer with visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--pbf", type=Path, default=DEFAULT_PBF)
    parser.add_argument("--basin-level", type=int, default=8, choices=[6,7,8,9,10])
    parser.add_argument("--process-both-levels", action="store_true",
                       help="Process both level 06 and 08 (enables comparison)")
    parser.add_argument("--no-visualizations", action="store_true",
                       help="Skip creating Plotly visualizations")
    parser.add_argument("--include-lakes", action="store_true")
    parser.add_argument("--coastal-buffer-km", type=float, default=50.0)
    parser.add_argument("--min-area-km2", type=float, default=0.05)
    parser.add_argument("--overwrite", action="store_true")
    
    args = parser.parse_args(argv)
    
    return ProcessingConfig(
        pbf_path=args.pbf,
        basin_level=args.basin_level,
        process_both_levels=args.process_both_levels,
        coastal_buffer_km=args.coastal_buffer_km,
        include_lakes=args.include_lakes,
        min_area_km2=args.min_area_km2,
        create_visualizations=not args.no_visualizations,
        outputs=OutputConfig(
            gpkg=PROCESSED_DIR / "osm_water_polygons.gpkg",
            metadata_json=PROCESSED_DIR / "osm_water_polygons_metadata.json",
            optimized_geojson=OPTIMIZED_DIR / "osm_water_polygons.geojson",
            web_low_zoom=WEB_DIR / "osm_water_polygons_z2-6.geojson",
            web_high_zoom=WEB_DIR / "osm_water_polygons_z7-10.geojson",
            overwrite=args.overwrite
        )
    )


def main(argv: Optional[Sequence[str]] = None) -> None:
    cfg = parse_args(argv)
    try:
        run(cfg)
    except KeyboardInterrupt:
        LOG.warning("\nInterrupted by user")
        sys.exit(1)
    except Exception as exc:
        LOG.error(f"\nFailed: {exc}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
