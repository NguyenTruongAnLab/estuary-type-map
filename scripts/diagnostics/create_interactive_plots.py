#!/usr/bin/env python3
"""
Create Interactive HTML Diagnostic Plots for All Datasets
==========================================================

PURPOSE: Generate Plotly HTML visualizations for data quality checking

Creates interactive plots for:
1. GlobSalt stations (salinity map)
2. DynQual rivers (discharge, TDS, temperature)
3. GCC coastal segments
4. Baum morphometry
5. Coastal basins

Features:
- Parameter selection dropdown
- Color by concentration/value
- Hover tooltips with all attributes
- Zoom/pan/download
- Optimized for large datasets (sampling/aggregation)

Author: Global Water Body Surface Area Atlas Project
Date: October 13, 2025
"""

import geopandas as gpd
import pandas as pd
import xarray as xr
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'diagnostics_html'
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_POINTS_PLOT = 10000  # Maximum points per plot (for performance)

# ==============================================================================
# PLOTTING FUNCTIONS
# ==============================================================================

def plot_globsalt_stations():
    """Create interactive plot for ALL GlobSalt stations - NO SAMPLING!"""
    print("\n📊 Creating GlobSalt stations plot (ALL STATIONS)...")
    
    file_path = DATA_DIR / 'processed' / 'globsalt_stations.gpkg'
    if not file_path.exists():
        print(f"   ⚠️  File not found: {file_path}")
        return
    
    gdf = gpd.read_file(file_path)
    print(f"   Loaded {len(gdf):,} stations")
    
    # NO SAMPLING - Keep ALL stations!
    print(f"   Keeping ALL {len(gdf):,} stations (no sampling)")
    
    # Extract coordinates
    gdf['lon'] = gdf.geometry.x
    gdf['lat'] = gdf.geometry.y
    
    # Create clear hover text with meaningful names
    hover_text = []
    for idx, row in gdf.iterrows():
        text = f"<b>Station ID:</b> {row.get('Station_ID', 'N/A')}<br>"
        text += f"<b>Mean Salinity:</b> {row.get('salinity_mean_psu', 0):.2f} PSU<br>"
        text += f"<b>Water Type:</b> {row.get('Water_type', 'N/A')}<br>"
        text += f"<b>Salinity Zone:</b> {row.get('salinity_zone', 'N/A')}<br>"
        text += f"<b>Measurements:</b> {row.get('n_measurements', 0):,.0f}<br>"
        text += f"<b>Country:</b> {row.get('Country', 'N/A')}"
        hover_text.append(text)
    
    # Create plot - Color by MEAN SALINITY only!
    fig = go.Figure(go.Scattermapbox(
        lon=gdf['lon'],
        lat=gdf['lat'],
        mode='markers',
        marker=dict(
            size=5,
            color=gdf['salinity_mean_psu'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title='Mean Salinity<br>(PSU)',
                x=1.02
            ),
            cmin=0,
            cmax=35,
            opacity=0.7
        ),
        text=hover_text,
        hoverinfo='text',
        name='GlobSalt Stations'
    ))
    
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(
            center=dict(lat=20, lon=0),
            zoom=1
        ),
        height=900,
        title=f'GlobSalt Salinity Monitoring Stations - {len(gdf):,} Complete Sites',
        title_font_size=18,
        margin=dict(l=0, r=0, t=50, b=0),
        dragmode='pan'
    )
    
    output_file = OUTPUT_DIR / 'globsalt_stations.html'
    fig.write_html(output_file, config={'scrollZoom': True})
    
    file_size = output_file.stat().st_size / (1024**2)
    print(f"   ✅ Saved: {output_file}")
    print(f"   File size: {file_size:.2f} MB")
    print(f"   Stations: {len(gdf):,} (complete!)")

def plot_dynqual_rivers():
    """Create interactive plot for DynQual river data"""
    print("\n📊 Creating DynQual rivers plot...")
    
    # Load NetCDF files
    discharge_file = DATA_DIR / 'raw' / 'DynQual-Jones_2023' / 'discharge_annualAvg_1980_2019.nc'
    tds_file = DATA_DIR / 'raw' / 'DynQual-Jones_2023' / 'salinity_annualAvg_1980_2019.nc'
    temp_file = DATA_DIR / 'raw' / 'DynQual-Jones_2023' / 'waterTemperature_annualAvg_1980_2019.nc'
    
    if not discharge_file.exists():
        print(f"   ⚠️  File not found: {discharge_file}")
        return
    
    # Load and process
    ds_dis = xr.open_dataset(discharge_file)
    ds_tds = xr.open_dataset(tds_file)
    ds_temp = xr.open_dataset(temp_file)
    
    # Average over time
    discharge = ds_dis['dis'].mean(dim='time').values
    tds = ds_tds['tds'].mean(dim='time').values
    temp = ds_temp['triver'].mean(dim='time').values - 273.15  # Kelvin to Celsius
    
    # Create coordinate grids
    lons, lats = np.meshgrid(ds_dis.lon.values, ds_dis.lat.values)
    
    # Flatten and filter
    df = pd.DataFrame({
        'lon': lons.ravel(),
        'lat': lats.ravel(),
        'discharge': discharge.ravel(),
        'tds': tds.ravel(),
        'temperature': temp.ravel()
    })
    
    # Remove NaN and filter to rivers
    df = df.dropna()
    df = df[df['discharge'] > 1.0]  # Rivers with discharge > 1 m³/s
    
    print(f"   Loaded {len(df):,} river cells")
    
    # Sample if too large
    if len(df) > MAX_POINTS_PLOT:
        df = df.sample(n=MAX_POINTS_PLOT, random_state=42)
        print(f"   Sampled to {len(df):,} points")
    
    # Calculate salinity from TDS if not present
    if 'salinity_psu' not in df.columns and 'tds' in df.columns:
        df['salinity_psu'] = df['tds'] / 640.0  # TDS to salinity conversion
        # Remove impossible salinity values (>40 PSU is unrealistic for rivers)
        df = df[df['salinity_psu'] < 40.0]
    
    # Apply reasonable discharge filter (remove extreme outliers for better visualization)
    if 'discharge' in df.columns:
        # Keep only 1st-99th percentile for discharge (better visualization)
        p1 = df['discharge'].quantile(0.01)
        p99 = df['discharge'].quantile(0.99)
        df = df[(df['discharge'] >= p1) & (df['discharge'] <= p99)]
        print(f"   Discharge filtered to: {p1:.1f} - {p99:.1f} m³/s (1st-99th percentile)")
    
    # Create interactive plot with dropdown selector
    fig = go.Figure()
    
    # Add trace for each parameter
    parameters = {
        'discharge': {'label': 'Discharge (m³/s)', 'colorscale': 'Blues'},
        'tds': {'label': 'TDS (mg/L)', 'colorscale': 'Oranges'},
        'salinity_psu': {'label': 'Salinity (PSU)', 'colorscale': 'Viridis'},
        'temperature': {'label': 'Temperature (°C)', 'colorscale': 'RdYlBu_r'}
    }
    
    for i, (param, config) in enumerate(parameters.items()):
        fig.add_trace(go.Scattermapbox(
            lon=df['lon'],
            lat=df['lat'],
            mode='markers',
            marker=dict(
                size=5,
                color=df[param],
                colorscale=config['colorscale'],
                showscale=True,
                colorbar=dict(title=config['label'])
            ),
            text=[f"Discharge: {d:.1f} m³/s<br>TDS: {t:.0f} mg/L<br>Salinity: {s:.2f} PSU<br>Temp: {temp:.1f}°C"
                  for d, t, s, temp in zip(df['discharge'], df['tds'], df.get('salinity_psu', [0]*len(df)), df['temperature'])],
            hoverinfo='text',
            name=param,
            visible=(i == 0)  # Only first trace visible initially
        ))
    
    # Create dropdown menu
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=list([
                    dict(
                        args=[{"visible": [True, False, False, False]}],
                        label="Discharge (m³/s)",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False, True, False, False]}],
                        label="TDS (mg/L)",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False, False, True, False]}],
                        label="Salinity (PSU)",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False, False, False, True]}],
                        label="Temperature (°C)",
                        method="update"
                    )
                ]),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.15,
                yanchor="top"
            ),
        ],
        mapbox_style="open-street-map",
        mapbox=dict(center=dict(lat=20, lon=0), zoom=1),
        height=800,
        title="DynQual Global Rivers - Select Parameter",
        dragmode='pan'
    )
    
    output_file = OUTPUT_DIR / 'dynqual_rivers.html'
    fig.write_html(output_file, config={'scrollZoom': True})
    print(f"   ✅ Saved: {output_file}")
    
    ds_dis.close()
    ds_tds.close()
    ds_temp.close()

def plot_gcc_coastal():
    """Create interactive plot for GCC coastal characteristics"""
    print("\n📊 Creating GCC coastal plot...")
    
    file_path = DATA_DIR / 'raw' / 'GCC-Panagiotis-Athanasiou_2024' / 'GCC_geophysical.csv'
    if not file_path.exists():
        print(f"   ⚠️  File not found: {file_path}")
        return
    
    df = pd.read_csv(file_path)
    print(f"   Loaded {len(df):,} segments")
    
    # Sample if too large
    if len(df) > MAX_POINTS_PLOT:
        df = df.sample(n=MAX_POINTS_PLOT, random_state=42)
        print(f"   Sampled to {len(df):,} segments")
    
    # Get numeric columns for selection
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if 'id' in numeric_cols:
        numeric_cols.remove('id')
    if 'lon' in numeric_cols and 'lat' in numeric_cols:
        numeric_cols.remove('lon')
        numeric_cols.remove('lat')
    
    # Create plot
    fig = px.scatter_mapbox(
        df,
        lat='lat',
        lon='lon',
        color=numeric_cols[0] if numeric_cols else None,
        hover_data=numeric_cols[:10],  # First 10 columns
        color_continuous_scale='Viridis',
        title='GCC - Global Coastal Characteristics (100km segments)',
        zoom=1
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        height=800,
        dragmode='pan'
    )
    
    output_file = OUTPUT_DIR / 'gcc_coastal.html'
    fig.write_html(output_file, config={'scrollZoom': True})
    print(f"   ✅ Saved: {output_file}")

def plot_coastal_basins():
    """Create interactive plot for coastal basins with estuary types"""
    print("\n📊 Creating coastal basins plot...")
    
    file_path = DATA_DIR / 'web' / 'coastal_basins_estuarine_types.geojson'
    if not file_path.exists():
        print(f"   ⚠️  File not found: {file_path}")
        return
    
    gdf = gpd.read_file(file_path)
    print(f"   Loaded {len(gdf):,} basins")
    
    # Sample if too large
    if len(gdf) > MAX_POINTS_PLOT:
        gdf = gdf.sample(n=MAX_POINTS_PLOT, random_state=42)
        print(f"   Sampled to {len(gdf):,} basins")
    
    # Get centroids for point plot
    gdf['lon'] = gdf.geometry.centroid.x
    gdf['lat'] = gdf.geometry.centroid.y
    
    # Create plot
    fig = px.scatter_mapbox(
        gdf,
        lat='lat',
        lon='lon',
        color='estuary_type',
        hover_data=['estuary_name', 'estuary_type', 'HYBAS_ID', 'SUB_AREA'],
        title='Coastal Basins with Estuarine Types',
        zoom=1,
        color_discrete_map={
            'Delta': '#8b4513',
            'Coastal Plain': '#ff8c00',
            'Lagoon': '#50c878',
            'Fjord': '#4a90e2',
            'Karst': '#9370db',
            'Unclassified': '#808080'
        }
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        height=800,
        dragmode='pan'
    )
    
    output_file = OUTPUT_DIR / 'coastal_basins.html'
    fig.write_html(output_file, config={'scrollZoom': True})
    print(f"   ✅ Saved: {output_file}")

def plot_baum_morphometry():
    """Create interactive plot for Baum morphometry"""
    print("\n📊 Creating Baum morphometry plot...")
    
    file_path = DATA_DIR / 'web' / 'baum_morphometry.geojson'
    if not file_path.exists():
        print(f"   ⚠️  File not found: {file_path}")
        return
    
    gdf = gpd.read_file(file_path)
    print(f"   Loaded {len(gdf):,} estuaries")
    
    # Create plot
    hover_cols = [col for col in ['name', 'geomorphotype', 'tectonic_setting', 'size_category'] 
                  if col in gdf.columns]
    
    fig = px.scatter_mapbox(
        gdf,
        lat='lat',
        lon='lon',
        color='geomorphotype',
        hover_data=hover_cols,
        title='Baum et al. (2024) - Large Estuary Morphometry',
        zoom=1,
        color_discrete_map={
            'LSE': '#e74c3c',
            'Rocky Bay': '#95a5a6',
            'Barrier Estuary': '#3498db',
            'Sandy Bay': '#f39c12',
            'Funnelled': '#9b59b6'
        }
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        height=800,
        dragmode='pan'
    )
    
    output_file = OUTPUT_DIR / 'baum_morphometry.html'
    fig.write_html(output_file, config={'scrollZoom': True})
    print(f"   ✅ Saved: {output_file}")

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    """Generate all diagnostic plots"""
    print("\n" + "="*80)
    print("CREATING INTERACTIVE DIAGNOSTIC PLOTS")
    print("="*80)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"Max points per plot: {MAX_POINTS_PLOT:,}")
    
    # Generate plots
    plot_globsalt_stations()
    plot_dynqual_rivers()
    plot_gcc_coastal()
    plot_coastal_basins()
    plot_baum_morphometry()
    
    print("\n" + "="*80)
    print("✅ ALL PLOTS GENERATED!")
    print("="*80)
    print(f"\n📂 Open HTML files in: {OUTPUT_DIR}")
    print("\n📊 Available plots:")
    for f in sorted(OUTPUT_DIR.glob('*.html')):
        file_size = f.stat().st_size / (1024**2)
        print(f"   - {f.name:<40} ({file_size:.1f} MB)")
    
    print("\n💡 Additional comprehensive plots available:")
    print("   - Run: python scripts/diagnostics/create_gcc_comprehensive_plot.py")
    print("   - Run: python scripts/diagnostics/create_basinatlas_plot.py")

if __name__ == '__main__':
    main()
