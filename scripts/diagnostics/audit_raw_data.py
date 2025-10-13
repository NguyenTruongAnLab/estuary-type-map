
"""
Data Audit & README Generator for Raw Datasets
===============================================

Systematically inspect all datasets in data/raw/, extract actual schemas,
and generate clear READMEs with real column names and data types.

This prevents coding mistakes from fake/assumed variable names!

Usage:
    python scripts/audit_raw_data.py
    python scripts/audit_raw_data.py --dataset durr
    python scripts/audit_raw_data.py --convert-pbf  # Convert OSM PBF to GPKG
"""

import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import shutil

import geopandas as gpd
import pandas as pd
import numpy as np

warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'
TEMP_DIR = BASE_DIR / 'data' / 'temp'
TEMP_DIR.mkdir(exist_ok=True)

# ==============================================================================
# DATASET AUDITORS
# ==============================================================================

def audit_durr_2011():
    """Audit Dürr et al. (2011) Worldwide Estuary Typology"""
    print("\n" + "="*80)
    print("AUDITING: Dürr et al. (2011) - Worldwide Estuary Typology")
    print("="*80)
    
    durr_dir = RAW_DIR / 'Worldwide-typology-Shapefile-Durr_2011'
    
    if not durr_dir.exists():
        print(f"❌ Directory not found: {durr_dir}")
        return None
    
    print(f"📂 Directory: {durr_dir}")
    
    # List all files
    print(f"\n📁 Files in directory:")
    for file in sorted(durr_dir.iterdir()):
        size_mb = file.stat().st_size / (1024**2) if file.is_file() else 0
        print(f"    {'📄' if file.is_file() else '📁'} {file.name} ({size_mb:.2f} MB)")
    
    # Find shapefile
    shapefiles = list(durr_dir.glob('*.shp'))
    
    if not shapefiles:
        print(f"\n⚠️  No shapefiles found!")
        return None
    
    shapefile = shapefiles[0]
    print(f"\n📊 Inspecting: {shapefile.name}")
    
    try:
        gdf = gpd.read_file(shapefile)
        
        print(f"\n✅ Successfully loaded!")
        print(f"    Features: {len(gdf):,}")
        print(f"    CRS: {gdf.crs}")
        print(f"    Geometry type: {gdf.geometry.type.unique().tolist()}")
        
        print(f"\n📋 ACTUAL COLUMNS ({len(gdf.columns)} total):")
        for col in gdf.columns:
            dtype = gdf[col].dtype
            non_null = gdf[col].notna().sum()
            unique = gdf[col].nunique() if col != 'geometry' else 'N/A'
            print(f"    • {col:20s} | {str(dtype):15s} | {non_null:6,} non-null | {unique} unique")
        
        # Sample values for key columns
        print(f"\n🔍 SAMPLE VALUES:")
        
        # Estuary names
        if 'NAME' in gdf.columns or 'Est_Name' in gdf.columns or 'name' in gdf.columns:
            name_col = next((c for c in ['NAME', 'Est_Name', 'name'] if c in gdf.columns), None)
            if name_col:
                print(f"    {name_col}: {gdf[name_col].dropna().head(5).tolist()}")
        
        # Estuary types
        type_cols = [c for c in gdf.columns if 'type' in c.lower() or 'class' in c.lower()]
        for col in type_cols[:3]:
            print(f"    {col}: {gdf[col].value_counts().head(5).to_dict()}")
        
        # Geographic coordinates
        if 'LAT' in gdf.columns or 'lat' in gdf.columns:
            lat_col = next((c for c in ['LAT', 'lat', 'Lat'] if c in gdf.columns), None)
            if lat_col:
                print(f"    {lat_col} range: {gdf[lat_col].min():.2f} to {gdf[lat_col].max():.2f}")
        
        # Generate README
        readme_content = f"""# Dürr et al. (2011) - Worldwide Estuary Typology Dataset

**Citation**: Dürr, H. H., Laruelle, G. G., van Kempen, C. M., Slomp, C. P., Meybeck, M., & Middelkoop, H. (2011).  
Worldwide Typology of Nearshore Coastal Systems: Defining the Estuarine Filter of River Inputs to the Oceans.  
*Estuaries and Coasts*, 34(3), 441-458.  
DOI: [10.1007/s12237-011-9381-y](https://doi.org/10.1007/s12237-011-9381-y)

---

## 📊 Dataset Summary

- **Total estuaries**: {len(gdf):,}
- **File format**: ESRI Shapefile
- **Coordinate system**: {gdf.crs}
- **Geometry type**: {gdf.geometry.type.unique()[0]}
- **Last audited**: {pd.Timestamp.now().strftime('%Y-%m-%d')}

---

## 📋 Actual Column Names & Data Types

"""
        
        for col in gdf.columns:
            if col != 'geometry':
                dtype = gdf[col].dtype
                non_null = gdf[col].notna().sum()
                pct = non_null / len(gdf) * 100
                unique = gdf[col].nunique()
                
                readme_content += f"### `{col}` ({dtype})\n"
                readme_content += f"- **Completeness**: {non_null:,} / {len(gdf):,} ({pct:.1f}%)\n"
                readme_content += f"- **Unique values**: {unique:,}\n"
                
                # Add value distribution for categorical columns
                if unique < 50 and col != 'geometry':
                    readme_content += f"- **Distribution**:\n"
                    for val, count in gdf[col].value_counts().head(10).items():
                        readme_content += f"  - `{val}`: {count:,} ({count/len(gdf)*100:.1f}%)\n"
                
                readme_content += "\n"
        
        readme_content += f"""---

## 🎯 How to Use in This Project

### Load Data
```python
import geopandas as gpd
durr = gpd.read_file('data/raw/Worldwide-typology-Shapefile-Durr_2011/{shapefile.name}')
```

### Classification Columns
- **Geomorphology**: [Add correct column name after inspection]
- **Catchment area**: [Add correct column name]
- **River discharge**: [Add correct column name]

---

## ⚠️ Known Issues & Limitations

1. [Add any data quality issues found]
2. [Add any missing values or inconsistencies]
3. [Add any coordinate system issues]

---

**Generated by**: `scripts/audit_raw_data.py`  
**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Save README
        readme_file = durr_dir / 'README_ACTUAL.md'
        readme_file.write_text(readme_content)
        print(f"\n✅ README saved: {readme_file}")
        
        return {
            'dataset': 'Durr_2011',
            'features': len(gdf),
            'columns': list(gdf.columns),
            'crs': str(gdf.crs),
            'readme': readme_file
        }
        
    except Exception as e:
        print(f"❌ Error loading shapefile: {e}")
        return None


def audit_baum_2024():
    """Audit Baum et al. (2024) Large Estuaries"""
    print("\n" + "="*80)
    print("AUDITING: Baum et al. (2024) - Large Estuaries Morphometry")
    print("="*80)
    
    baum_dir = RAW_DIR / 'Large-estuaries-Baum_2024'
    
    if not baum_dir.exists():
        print(f"❌ Directory not found: {baum_dir}")
        return None
    
    print(f"📂 Directory: {baum_dir}")
    
    # List all files
    print(f"\n📁 Files in directory:")
    for file in sorted(baum_dir.iterdir()):
        size_mb = file.stat().st_size / (1024**2) if file.is_file() else 0
        print(f"    {'📄' if file.is_file() else '📁'} {file.name} ({size_mb:.2f} MB)")
    
    # Find data files (could be CSV, Excel, GeoJSON, etc.)
    data_files = []
    for ext in ['*.csv', '*.xlsx', '*.geojson', '*.gpkg', '*.shp']:
        data_files.extend(list(baum_dir.glob(ext)))
    
    if not data_files:
        print(f"\n⚠️  No data files found!")
        return None
    
    results = []
    
    for data_file in data_files:
        print(f"\n📊 Inspecting: {data_file.name}")
        
        try:
            # Try reading as geodata first
            if data_file.suffix in ['.geojson', '.gpkg', '.shp']:
                df = gpd.read_file(data_file)
                is_geo = True
            else:
                df = pd.read_csv(data_file) if data_file.suffix == '.csv' else pd.read_excel(data_file)
                is_geo = False
            
            print(f"✅ Successfully loaded!")
            print(f"    Rows: {len(df):,}")
            print(f"    Columns: {len(df.columns)}")
            if is_geo:
                print(f"    CRS: {df.crs}")
                print(f"    Geometry type: {df.geometry.type.unique().tolist()}")
            
            print(f"\n📋 ACTUAL COLUMNS:")
            for col in df.columns:
                dtype = df[col].dtype
                non_null = df[col].notna().sum()
                print(f"    • {col:30s} | {str(dtype):15s} | {non_null:6,} non-null")
            
            # Sample first few rows
            print(f"\n🔍 SAMPLE DATA (first 3 rows):")
            print(df.head(3).to_string())
            
            results.append({
                'file': data_file.name,
                'rows': len(df),
                'columns': list(df.columns),
                'is_geo': is_geo
            })
            
        except Exception as e:
            print(f"❌ Error loading {data_file.name}: {e}")
    
    return {'dataset': 'Baum_2024', 'files': results}


def audit_gcc_2024():
    """Audit GCC (Athanasiou et al. 2024) - Global Coastal Characteristics"""
    print("\n" + "="*80)
    print("AUDITING: Athanasiou et al. (2024) - Global Coastal Characteristics")
    print("="*80)
    
    gcc_dir = RAW_DIR / 'GCC-Panagiotis-Athanasiou_2024'
    
    if not gcc_dir.exists():
        print(f"❌ Directory not found: {gcc_dir}")
        return None
    
    print(f"📂 Directory: {gcc_dir}")
    
    # List all files
    print(f"\n📁 Files in directory:")
    for file in sorted(gcc_dir.iterdir()):
        size_mb = file.stat().st_size / (1024**2) if file.is_file() else 0
        print(f"    {'📄' if file.is_file() else '📁'} {file.name} ({size_mb:.2f} MB)")
    
    # Find CSV files
    csv_files = list(gcc_dir.glob('*.csv'))
    
    if not csv_files:
        print(f"\n⚠️  No CSV files found!")
        return None
    
    results = []
    
    for csv_file in csv_files:
        print(f"\n📊 Inspecting: {csv_file.name}")
        
        try:
            df = pd.read_csv(csv_file)
            
            print(f"✅ Successfully loaded!")
            print(f"    Rows: {len(df):,}")
            print(f"    Columns: {len(df.columns)}")
            
            print(f"\n📋 ACTUAL COLUMNS ({len(df.columns)} total):")
            for col in df.columns:
                dtype = df[col].dtype
                non_null = df[col].notna().sum()
                unique = df[col].nunique()
                print(f"    • {col:40s} | {str(dtype):15s} | {non_null:8,} non-null | {unique:8,} unique")
            
            results.append({
                'file': csv_file.name,
                'rows': len(df),
                'columns': list(df.columns)
            })
            
        except Exception as e:
            print(f"❌ Error loading {csv_file.name}: {e}")
    
    return {'dataset': 'GCC_2024', 'files': results}


def audit_hydrosheds():
    """Audit HydroSHEDS BasinATLAS & RiverATLAS"""
    print("\n" + "="*80)
    print("AUDITING: HydroSHEDS - BasinATLAS & RiverATLAS v1.0")
    print("="*80)
    
    hydro_dir = RAW_DIR / 'hydrosheds'
    
    if not hydro_dir.exists():
        print(f"❌ Directory not found: {hydro_dir}")
        return None
    
    print(f"📂 Directory: {hydro_dir}")
    
    # List all subdirectories
    print(f"\n📁 Subdirectories:")
    for subdir in sorted([d for d in hydro_dir.iterdir() if d.is_dir()]):
        print(f"    📁 {subdir.name}/")
        
        # List GDB files
        gdb_files = list(subdir.glob('*.gdb'))
        for gdb in gdb_files:
            print(f"        🗄️  {gdb.name}")
            
            # Try to list layers
            try:
                import fiona
                layers = fiona.listlayers(str(gdb))
                print(f"            Layers: {', '.join(layers[:5])}{'...' if len(layers) > 5 else ''}")
            except:
                pass
    
    return {'dataset': 'HydroSHEDS', 'status': 'Complex GDB structure - needs manual inspection'}


def audit_osm_water():
    """Audit OSM Water Layer (Yamazaki 2021)"""
    print("\n" + "="*80)
    print("AUDITING: OSM Water Layer (Yamazaki et al. 2021)")
    print("="*80)
    
    osm_dir = RAW_DIR / 'OSM-Water-Layer-Yamazaki_2021'
    
    if not osm_dir.exists():
        print(f"❌ Directory not found: {osm_dir}")
        return None
    
    print(f"📂 Directory: {osm_dir}")
    
    # List all files
    print(f"\n📁 Files in directory:")
    for file in sorted(osm_dir.iterdir()):
        size_mb = file.stat().st_size / (1024**2) if file.is_file() else 0
        size_gb = size_mb / 1024
        print(f"    {'📄' if file.is_file() else '📁'} {file.name} ({size_gb:.2f} GB)")
    
    # Find PBF file
    pbf_files = list(osm_dir.glob('*.pbf'))
    
    if not pbf_files:
        print(f"\n⚠️  No PBF files found!")
        return None
    
    pbf_file = pbf_files[0]
    size_gb = pbf_file.stat().st_size / (1024**3)
    
    print(f"\n📊 PBF File: {pbf_file.name}")
    print(f"    Size: {size_gb:.2f} GB")
    print(f"\n💡 To inspect PBF contents, use osmium:")
    print(f"    osmium fileinfo {pbf_file.name}")
    print(f"\n💡 To convert to GPKG (will take 15-30 min):")
    print(f"    python scripts/audit_raw_data.py --convert-pbf")
    
    return {'dataset': 'OSM_Water', 'file': pbf_file.name, 'size_gb': size_gb}


def audit_grit():
    """Audit GRIT v0.6 (Michel et al. 2025)"""
    print("\n" + "="*80)
    print("AUDITING: GRIT v0.6 (Wortmann/Michel et al. 2024)")
    print("="*80)
    
    grit_dir = RAW_DIR / 'GRIT-Michel_2025'
    
    if not grit_dir.exists():
        print(f"❌ Directory not found: {grit_dir}")
        return None
    
    print(f"📂 Directory: {grit_dir}")
    
    # List all GPKG files
    print(f"\n📁 GPKG files in directory:")
    gpkg_files = list(grit_dir.glob('*.gpkg'))
    
    for gpkg_file in sorted(gpkg_files):
        size_mb = gpkg_file.stat().st_size / (1024**2)
        print(f"    🗄️  {gpkg_file.name} ({size_mb:.1f} MB)")
        
        # List layers
        try:
            import fiona
            layers = fiona.listlayers(str(gpkg_file))
            print(f"        Layers: {', '.join(layers)}")
            
            # Sample first layer
            if layers:
                with fiona.open(str(gpkg_file), layer=layers[0]) as src:
                    print(f"        Features in '{layers[0]}': {len(src):,}")
                    print(f"        Schema fields: {', '.join(src.schema['properties'].keys())[:100]}...")
        except Exception as e:
            print(f"        Error reading: {e}")
    
    # Detailed inspection of Asia files
    asia_files = {
        'segments': grit_dir / 'GRITv06_segments_AS_EPSG4326.gpkg',
        'reaches': grit_dir / 'GRITv06_reaches_AS_EPSG4326.gpkg',
        'catchments': grit_dir / 'GRITv06_component_catchments_AS_EPSG4326.gpkg'
    }
    
    results = {}
    
    for name, file in asia_files.items():
        if not file.exists():
            print(f"\n⚠️  {name} file not found!")
            continue
        
        print(f"\n📊 Detailed inspection: {file.name}")
        
        try:
            # Load with geopandas
            gdf = gpd.read_file(file, layer='lines' if name != 'catchments' else None, rows=1000)
            
            print(f"✅ Successfully loaded (sample: 1000 rows)")
            print(f"    Total features: ~{len(gdf):,} (sampled)")
            print(f"    CRS: {gdf.crs}")
            print(f"    Geometry type: {gdf.geometry.type.unique().tolist()}")
            
            print(f"\n📋 ACTUAL COLUMNS ({len(gdf.columns)} total):")
            for col in gdf.columns:
                dtype = gdf[col].dtype
                non_null = gdf[col].notna().sum()
                print(f"    • {col:30s} | {str(dtype):15s} | {non_null:5,} non-null (in sample)")
            
            results[name] = {
                'file': file.name,
                'columns': list(gdf.columns),
                'crs': str(gdf.crs)
            }
            
        except Exception as e:
            print(f"❌ Error loading: {e}")
    
    return {'dataset': 'GRIT_v06', 'files': results}


def convert_pbf_to_gpkg():
    """Convert OSM PBF to GPKG for easier processing"""
    print("\n" + "="*80)
    print("CONVERTING: OSM Water Layer PBF → GPKG")
    print("="*80)
    
    osm_dir = RAW_DIR / 'OSM-Water-Layer-Yamazaki_2021'
    pbf_file = osm_dir / 'OSM_WaterLayer.pbf'
    output_gpkg = osm_dir / 'OSM_WaterLayer.gpkg'
    
    if not pbf_file.exists():
        print(f"❌ PBF file not found: {pbf_file}")
        return None
    
    if output_gpkg.exists():
        print(f"⚠️  Output already exists: {output_gpkg}")
        response = input("    Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("    Cancelled.")
            return None
    
    # Check if ogr2ogr is available
    if not shutil.which('ogr2ogr'):
        print(f"❌ ogr2ogr not found! Install GDAL/OGR first.")
        print(f"    Windows: https://gdal.org/download.html")
        return None
    
    print(f"📂 Input: {pbf_file.name} ({pbf_file.stat().st_size / (1024**3):.2f} GB)")
    print(f"📂 Output: {output_gpkg.name}")
    print(f"\n⏳ Converting... (this will take 15-30 minutes)")
    print(f"    Processing water polygons only...")
    
    # Run ogr2ogr
    cmd = [
        'ogr2ogr',
        '-f', 'GPKG',
        str(output_gpkg),
        str(pbf_file),
        '-sql', "SELECT * FROM multipolygons WHERE natural='water' OR water IS NOT NULL",
        '-progress'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        output_size = output_gpkg.stat().st_size / (1024**3)
        print(f"\n✅ Conversion complete!")
        print(f"    Output size: {output_size:.2f} GB")
        print(f"    File: {output_gpkg}")
        
        return output_gpkg
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Conversion failed: {e}")
        print(f"    stderr: {e.stderr}")
        return None


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    """Run all audits"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Audit raw datasets and generate READMEs')
    parser.add_argument('--dataset', type=str, help='Audit specific dataset (durr, baum, gcc, hydrosheds, osm, grit)')
    parser.add_argument('--convert-pbf', action='store_true', help='Convert OSM PBF to GPKG')
    parser.add_argument('--all', action='store_true', help='Audit all datasets')
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("RAW DATA AUDIT & README GENERATOR")
    print("="*80)
    print(f"Base directory: {RAW_DIR}")
    
    if args.convert_pbf:
        convert_pbf_to_gpkg()
        return
    
    results = {}
    
    if args.dataset == 'durr' or args.all:
        results['durr'] = audit_durr_2011()
    
    if args.dataset == 'baum' or args.all:
        results['baum'] = audit_baum_2024()
    
    if args.dataset == 'gcc' or args.all:
        results['gcc'] = audit_gcc_2024()
    
    if args.dataset == 'hydrosheds' or args.all:
        results['hydrosheds'] = audit_hydrosheds()
    
    if args.dataset == 'osm' or args.all:
        results['osm'] = audit_osm_water()
    
    if args.dataset == 'grit' or args.all:
        results['grit'] = audit_grit()
    
    # If no specific dataset, audit all
    if not any([args.dataset, args.all, args.convert_pbf]):
        print("\n💡 Usage:")
        print("    python scripts/audit_raw_data.py --all")
        print("    python scripts/audit_raw_data.py --dataset durr")
        print("    python scripts/audit_raw_data.py --convert-pbf")
        return
    
    # Summary
    print("\n" + "="*80)
    print("AUDIT SUMMARY")
    print("="*80)
    for dataset, result in results.items():
        if result:
            print(f"✅ {dataset:15s}: {result.get('dataset', 'OK')}")
        else:
            print(f"❌ {dataset:15s}: Failed or not found")
    
    print("\n✅ Audit complete! Check generated README_ACTUAL.md files in each dataset folder.")


if __name__ == '__main__':
    main()
