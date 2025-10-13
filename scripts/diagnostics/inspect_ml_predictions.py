
"""
Inspect ML Classified Predictions Data
=======================================

Check what columns exist in the ML classified GPKG files
to ensure validation code uses correct column names.
"""

import sys
from pathlib import Path
import geopandas as gpd
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / 'data' / 'processed' / 'ml_classified'

def inspect_ml_predictions(region_code='SP'):
    """Inspect ML classified predictions structure"""
    print("="*80)
    print(f"INSPECTING ML PREDICTIONS: {region_code}")
    print("="*80)
    
    predictions_file = OUTPUT_DIR / f'rivers_grit_ml_classified_{region_code.lower()}.gpkg'
    
    if not predictions_file.exists():
        print(f"❌ File not found: {predictions_file}")
        return
    
    print(f"\n📂 Loading: {predictions_file.name}")
    predictions = gpd.read_file(predictions_file)
    
    print(f"\n📊 Basic Info:")
    print(f"   Total features: {len(predictions):,}")
    print(f"   CRS: {predictions.crs}")
    
    print(f"\n📋 All Columns ({len(predictions.columns)}):")
    for i, col in enumerate(predictions.columns, 1):
        dtype = predictions[col].dtype
        print(f"   {i:2d}. {col:30s} ({dtype})")
    
    print(f"\n🔍 Key Column Data Types:")
    key_cols = ['global_id', 'salinity_class_final', 'confidence_level', 
                'dist_to_coast_km', 'classification_method']
    for col in key_cols:
        if col in predictions.columns:
            print(f"   {col:30s}: {predictions[col].dtype}")
        else:
            print(f"   {col:30s}: ❌ NOT FOUND")
    
    print(f"\n🔍 salinity_class_final Column:")
    if 'salinity_class_final' in predictions.columns:
        print(f"   Data type: {predictions['salinity_class_final'].dtype}")
        print(f"   Unique values: {predictions['salinity_class_final'].nunique()}")
        print(f"   Value counts:")
        for val, count in predictions['salinity_class_final'].value_counts().items():
            print(f"      {val:20s}: {count:,} ({count/len(predictions)*100:.1f}%)")
    
    print(f"\n🔍 Checking for 'index_right' column:")
    if 'index_right' in predictions.columns:
        print(f"   ⚠️  WARNING: 'index_right' column EXISTS!")
        print(f"      This will cause spatial join conflicts")
        print(f"      Data type: {predictions['index_right'].dtype}")
        print(f"      Sample values: {predictions['index_right'].head(10).tolist()}")
    else:
        print(f"   ✅ No 'index_right' column (good!)")
    
    print(f"\n💾 Saving column list for reference...")
    col_file = BASE_DIR / 'data' / 'processed' / f'ml_predictions_columns_{region_code.lower()}.txt'
    with open(col_file, 'w') as f:
        f.write(f"ML Predictions Columns for {region_code}\n")
        f.write("="*50 + "\n\n")
        for i, col in enumerate(predictions.columns, 1):
            f.write(f"{i:2d}. {col:30s} ({predictions[col].dtype})\n")
    print(f"   ✓ Saved: {col_file}")
    
    print(f"\n✅ Inspection complete!")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', default='SP', choices=['AF', 'AS', 'EU', 'NA', 'SA', 'SI', 'SP'])
    args = parser.parse_args()
    
    inspect_ml_predictions(args.region)
