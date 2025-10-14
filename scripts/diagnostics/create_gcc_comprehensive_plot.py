#!/usr/bin/env python3
"""
Create Comprehensive GCC Interactive Plot
==========================================

PURPOSE: Generate interactive Plotly visualization for GCC coastal characteristics
         with meaningful parameter selection for water body surface area research

INPUT:
- data/raw/GCC-Panagiotis-Athanasiou_2024/GCC_geophysical.csv
- data/raw/GCC-Panagiotis-Athanasiou_2024/GCC_hydrometeorological.csv
- data/raw/GCC-Panagiotis-Athanasiou_2024/GCC_socioeconomic.csv
- data/raw/GCC-Panagiotis-Athanasiou_2024/meta_data.yml (for parameter descriptions)

OUTPUT:
- diagnostics_html/gcc_comprehensive.html (interactive multi-parameter plot)

FEATURES:
- Dropdown parameter selection (project-relevant only)
- Mouse scroll zoom enabled
- Color-coded by selected parameter
- Optimized sampling (10K points max)
- Hover tooltips with key attributes

Author: Global Water Body Surface Area Atlas Project
Date: October 13, 2025
"""

import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
from pathlib import Path
import yaml
import numpy as np
from shapely.geometry import Point

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / 'data' / 'raw' / 'GCC-Panagiotis-Athanasiou_2024'
OUTPUT_DIR = BASE_DIR / 'diagnostics_html'
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_POINTS = 10000

# Project-relevant parameters with MEANINGFUL NAMES
# Based on ACTUAL column names in GCC CSVs
RELEVANT_PARAMS = {
    'Geophysical': [
        'z_peak_first_copdem',      # Coastal elevation
        'z_peak_max_1km_copdem',    # Maximum elevation (1km)
    ],
    'Hydrometeorological': [
        'swh_p50',                  # Wave height
        'mhhw',                     # High tide level
        'mllw',                     # Low tide level
        'tr',                       # Tidal range (CRITICAL for salinity!)
        't2m_p50',                  # Air temperature
        'tp_p50',                   # Precipitation
    ],
    'Socioeconomic': [
        'country',                  # Country name
    ]
}

# Meaningful display names for parameters
PARAM_DISPLAY_NAMES = {
    'z_peak_first_copdem': 'Coastal Elevation (m)',
    'z_peak_max_1km_copdem': 'Maximum Elevation 1km (m)',
    'swh_p50': 'Wave Height (m)',
    'mhhw': 'Mean Higher High Water (m)',
    'mllw': 'Mean Lower Low Water (m)',
    'tr': 'Tidal Range (m)',
    't2m_p50': 'Air Temperature (°C)',
    'tp_p50': 'Total Precipitation (mm)',
    'country': 'Country'
}

# ==============================================================================
# MAIN PROCESSING
# ==============================================================================

def load_gcc_data():
    """Load and merge all three GCC CSV files"""
    print("\n📂 Loading GCC datasets...")
    
    # Load geophysical
    geo_file = DATA_DIR / 'GCC_geophysical.csv'
    df_geo = pd.read_csv(geo_file)
    print(f"   ✓ Geophysical: {len(df_geo):,} segments")
    
    # Load hydrometeorological
    hydro_file = DATA_DIR / 'GCC_hydrometeorological.csv'
    df_hydro = pd.read_csv(hydro_file)
    print(f"   ✓ Hydrometeorological: {len(df_hydro):,} segments")
    
    # Load socioeconomic
    socio_file = DATA_DIR / 'GCC_socioeconomic.csv'
    df_socio = pd.read_csv(socio_file)
    print(f"   ✓ Socioeconomic: {len(df_socio):,} segments")
    
    # Merge on 'id' column
    df = df_geo.merge(df_hydro, on='id', how='outer', suffixes=('', '_hydro'))
    df = df.merge(df_socio, on='id', how='outer', suffixes=('', '_socio'))
    
    # Keep only one lat/lon (they should be identical)
    if 'lat_hydro' in df.columns:
        df = df.drop(columns=['lat_hydro', 'lon_hydro'])
    if 'lat_socio' in df.columns:
        df = df.drop(columns=['lat_socio', 'lon_socio'])
    
    print(f"   ✓ Merged: {len(df):,} total segments")
    
    return df

def filter_relevant_params(df):
    """Filter to only project-relevant parameters"""
    print("\n🎯 Filtering to project-relevant parameters...")
    
    # Flatten all relevant params
    all_params = []
    for category, params in RELEVANT_PARAMS.items():
        all_params.extend(params)
    
    # Always keep id, lat, lon, angle
    keep_cols = ['id', 'lat', 'lon', 'angle']
    
    # Add relevant params that exist
    for param in all_params:
        if param in df.columns:
            keep_cols.append(param)
    
    df_filtered = df[keep_cols].copy()
    
    # Calculate tidal range if not present (MHHW - MLLW)
    if 'tr' not in df_filtered.columns and 'mhhw' in df_filtered.columns and 'mllw' in df_filtered.columns:
        print(f"   Calculating tidal range from MHHW - MLLW...")
        df_filtered['tr'] = df_filtered['mhhw'] - df_filtered['mllw']
        print(f"   ✓ Tidal range calculated")
    
    print(f"   ✓ Kept {len(df_filtered.columns)} columns (from {len(df.columns)})")
    print(f"   Parameters: {[c for c in df_filtered.columns if c not in ['id', 'lat', 'lon', 'angle']]}")
    
    return df_filtered

def sample_data(df, max_points=MAX_POINTS):
    """Sample data spatially if too large"""
    if len(df) <= max_points:
        return df
    
    print(f"\n📉 Sampling data: {len(df):,} → {max_points:,} points")
    
    # Stratified sampling by latitude (ensure global coverage)
    df['lat_bin'] = pd.cut(df['lat'], bins=20, labels=False)
    df_sampled = df.groupby('lat_bin', group_keys=False).apply(
        lambda x: x.sample(n=min(len(x), max_points // 20), random_state=42)
    )
    df_sampled = df_sampled.drop(columns=['lat_bin'])
    
    print(f"   ✓ Sampled to {len(df_sampled):,} points")
    
    return df_sampled

def create_interactive_plot(df):
    """Create multi-parameter interactive plot with dropdown"""
    print("\n🎨 Creating interactive plot...")
    
    # Get numeric parameters
    numeric_params = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_params = [p for p in numeric_params if p not in ['id', 'lat', 'lon', 'angle']]
    
    if len(numeric_params) == 0:
        print("   ⚠️  No numeric parameters found!")
        return None
    
    # Create figure with traces for each parameter
    fig = go.Figure()
    
    # Prepare parameter info
    param_info = {}
    for param in numeric_params:
        # Get basic stats
        valid_data = df[param].dropna()
        if len(valid_data) == 0:
            continue
        
        param_info[param] = {
            'min': valid_data.min(),
            'max': valid_data.max(),
            'mean': valid_data.mean(),
            'count': len(valid_data)
        }
        
        # Determine colorscale based on parameter name
        if 'temp' in param.lower():
            colorscale = 'RdYlBu_r'
        elif 'pop' in param.lower() or 'light' in param.lower():
            colorscale = 'Reds'
        elif 'tide' in param.lower() or 'surge' in param.lower():
            colorscale = 'Blues'
        elif 'wave' in param.lower() or 'swh' in param.lower():
            colorscale = 'Viridis'
        else:
            colorscale = 'Plasma'
        
        # Get meaningful display name
        display_name = PARAM_DISPLAY_NAMES.get(param, param)
        
        # Create hover text with meaningful names
        hover_text = []
        for idx, row in df.iterrows():
            text = f"<b>Coastal Segment</b><br>"
            text += f"<b>Location:</b> {row['lat']:.2f}°N, {row['lon']:.2f}°E<br>"
            text += f"<b>{display_name}:</b> {row[param]:.2f}"
            hover_text.append(text)
        
        # Add trace
        fig.add_trace(go.Scattermapbox(
            lon=df['lon'],
            lat=df['lat'],
            mode='markers',
            marker=dict(
                size=6,
                color=df[param],
                colorscale=colorscale,
                showscale=True,
                colorbar=dict(
                    title=display_name,
                    x=1.02
                ),
                opacity=0.7
            ),
            text=hover_text,
            hoverinfo='text',
            name=param,
            visible=(numeric_params.index(param) == 0)  # Only first visible
        ))
    
    # Create dropdown menu with meaningful names
    buttons = []
    for i, param in enumerate(numeric_params):
        visibility = [False] * len(numeric_params)
        visibility[i] = True
        
        # Get meaningful display name
        display_name = PARAM_DISPLAY_NAMES.get(param, param)
        
        # Format button label with stats
        if param in param_info:
            info = param_info[param]
            label = f"{display_name}<br>(Range: {info['min']:.1f} - {info['max']:.1f})"
        else:
            label = display_name
        
        buttons.append(
            dict(
                label=label,
                method="update",
                args=[
                    {"visible": visibility},
                    {"title": f"GCC Coastal Characteristics - {display_name}"}
                ]
            )
        )
    
    # Update layout
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=buttons,
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.02,
                xanchor="left",
                y=0.98,
                yanchor="top",
                bgcolor="white",
                bordercolor="#333",
                borderwidth=1
            )
        ],
        mapbox_style="open-street-map",
        mapbox=dict(
            center=dict(lat=20, lon=0),
            zoom=1
        ),
        height=900,
        title=f"GCC Coastal Characteristics - {PARAM_DISPLAY_NAMES.get(numeric_params[0], numeric_params[0])}",
        title_font_size=18,
        dragmode='pan',
        margin=dict(l=0, r=0, t=60, b=0)
    )
    
    print(f"   ✓ Created plot with {len(numeric_params)} parameters")
    
    return fig

def main():
    """Main processing pipeline"""
    print("\n" + "="*80)
    print("CREATE GCC COMPREHENSIVE INTERACTIVE PLOT")
    print("="*80)
    
    # Load data
    df = load_gcc_data()
    
    # Filter to relevant parameters
    df = filter_relevant_params(df)
    
    # Remove rows with missing coordinates
    df = df.dropna(subset=['lat', 'lon'])
    print(f"\n✓ Valid coordinates: {len(df):,} segments")
    
    # Sample if needed
    df = sample_data(df)
    
    # Create plot
    fig = create_interactive_plot(df)
    
    if fig is None:
        print("\n❌ Failed to create plot")
        return
    
    # Save with scroll zoom enabled
    output_file = OUTPUT_DIR / 'gcc_comprehensive.html'
    fig.write_html(output_file, config={'scrollZoom': True})
    
    file_size_mb = output_file.stat().st_size / (1024**2)
    
    print("\n" + "="*80)
    print("✅ SUCCESS!")
    print("="*80)
    print(f"\n📂 Output: {output_file}")
    print(f"📊 File size: {file_size_mb:.2f} MB")
    print(f"📍 Data points: {len(df):,}")
    print(f"🎛️  Parameters: {len([p for p in df.columns if p not in ['id', 'lat', 'lon', 'angle']])}")
    print("\n✨ Features:")
    print("   • Dropdown menu to switch between parameters")
    print("   • Mouse scroll zoom enabled")
    print("   • Color-coded by parameter value")
    print("   • Hover tooltips with details")
    print("\n💡 Open in browser to explore!")

if __name__ == '__main__':
    main()
