
"""
Inspect Dürr Shapefile Data Types
==================================

Check actual column names, data types, and sample values
to ensure validation code handles them correctly.
"""

import sys
from pathlib import Path
import geopandas as gpd
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'

def inspect_durr_shapefile():
    """Inspect Dürr 2011 shapefile structure"""
    print("="*80)
    print("INSPECTING DÜRR 2011 SHAPEFILE")
    print("="*80)
    
    durr_dir = RAW_DIR / 'Worldwide-typology-Shapefile-Durr_2011'
    durr_file = durr_dir / 'typology_catchments.shp'
    
    if not durr_file.exists():
        print(f"❌ File not found: {durr_file}")
        return
    
    print(f"\n📂 Loading: {durr_file.name}")
    durr = gpd.read_file(durr_file)
    
    print(f"\n📊 Basic Info:")
    print(f"   Total features: {len(durr):,}")
    print(f"   CRS: {durr.crs}")
    
    print(f"\n📋 All Columns ({len(durr.columns)}):")
    for col in durr.columns:
        print(f"   - {col}")
    
    print(f"\n🔍 Column Data Types:")
    print(durr.dtypes)
    
    print(f"\n🔍 FIN_TYP Column Details:")
    if 'FIN_TYP' in durr.columns:
        print(f"   Data type: {durr['FIN_TYP'].dtype}")
        print(f"   Non-null count: {durr['FIN_TYP'].notna().sum():,} / {len(durr):,}")
        print(f"   Null count: {durr['FIN_TYP'].isna().sum():,}")
        print(f"   Unique values: {durr['FIN_TYP'].nunique()}")
        
        print(f"\n   📊 Value Distribution:")
        value_counts = durr['FIN_TYP'].value_counts(dropna=False)
        for val, count in value_counts.items():
            val_repr = repr(val) if pd.notna(val) else "NaN"
            val_type = type(val).__name__
            print(f"      {val_repr:30s} ({val_type:10s}): {count:,} ({count/len(durr)*100:.1f}%)")
        
        print(f"\n   🔬 Sample Values (first 20):")
        for i, val in enumerate(durr['FIN_TYP'].head(20)):
            val_repr = repr(val) if pd.notna(val) else "NaN"
            val_type = type(val).__name__
            print(f"      [{i}] {val_repr:30s} (type: {val_type})")
    else:
        print(f"   ❌ FIN_TYP column not found!")
        print(f"   Available columns: {durr.columns.tolist()}")
    
    print(f"\n🔍 BASINID Column Details:")
    if 'BASINID' in durr.columns:
        print(f"   Data type: {durr['BASINID'].dtype}")
        print(f"   Non-null count: {durr['BASINID'].notna().sum():,}")
        print(f"   Sample values: {durr['BASINID'].head(10).tolist()}")
    
    print(f"\n💾 Saving sample to CSV for inspection...")
    sample_file = BASE_DIR / 'data' / 'processed' / 'durr_sample_inspection.csv'
    durr[['BASINID', 'FIN_TYP']].head(100).to_csv(sample_file, index=False)
    print(f"   ✓ Saved: {sample_file}")
    
    print(f"\n✅ Inspection complete!")
    print(f"\n📋 Summary:")
    print(f"   - FIN_TYP dtype: {durr['FIN_TYP'].dtype if 'FIN_TYP' in durr.columns else 'NOT FOUND'}")
    print(f"   - Contains strings: {durr['FIN_TYP'].apply(lambda x: isinstance(x, str)).any() if 'FIN_TYP' in durr.columns else 'N/A'}")
    print(f"   - Contains floats: {durr['FIN_TYP'].apply(lambda x: isinstance(x, float)).any() if 'FIN_TYP' in durr.columns else 'N/A'}")
    print(f"   - Contains ints: {durr['FIN_TYP'].apply(lambda x: isinstance(x, int)).any() if 'FIN_TYP' in durr.columns else 'N/A'}")


if __name__ == '__main__':
    inspect_durr_shapefile()
