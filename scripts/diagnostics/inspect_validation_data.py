
"""
Complete Data Inspection for Validation Debugging
==================================================

Inspect both Dürr shapefile and ML predictions to understand
exact data structures and fix validation code properly.

Usage:
    python scripts/inspect_validation_data.py --region SP
"""

import sys
from pathlib import Path
import geopandas as gpd
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'
ML_DIR = BASE_DIR / 'data' / 'processed' / 'ml_features'
OUTPUT_DIR = BASE_DIR / 'data' / 'processed' / 'ml_classified'

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', default='SP', choices=['AF', 'AS', 'EU', 'NA', 'SA', 'SI', 'SP'])
    args = parser.parse_args()
    
    region = args.region
    
    print("\n" + "="*80)
    print("COMPLETE VALIDATION DATA INSPECTION")
    print("="*80)
    print(f"Region: {region}")
    
    # =========================================================================
    # 1. Inspect Dürr Shapefile
    # =========================================================================
    print("\n" + "="*80)
    print("1. DÜRR SHAPEFILE")
    print("="*80)
    
    durr_dir = RAW_DIR / 'Worldwide-typology-Shapefile-Durr_2011'
    durr_file = durr_dir / 'typology_catchments.shp'
    
    if durr_file.exists():
        durr = gpd.read_file(durr_file)
        print(f"✓ Loaded: {len(durr):,} catchments")
        
        print(f"\n📋 Columns:")
        for col in durr.columns:
            if col != 'geometry':
                print(f"   - {col:20s} ({durr[col].dtype})")
        
        if 'FIN_TYP' in durr.columns:
            print(f"\n🔍 FIN_TYP Analysis:")
            print(f"   dtype: {durr['FIN_TYP'].dtype}")
            print(f"   unique: {durr['FIN_TYP'].nunique()} values")
            
            print(f"\n   Distribution:")
            for val, count in durr['FIN_TYP'].value_counts(dropna=False).head(20).items():
                val_str = str(val) if pd.notna(val) else "NaN"
                val_type = type(val).__name__
                print(f"      {val_str:30s} ({val_type:10s}): {count:,}")
    else:
        print(f"❌ Not found: {durr_file}")
    
    # =========================================================================
    # 2. Inspect ML Predictions
    # =========================================================================
    print("\n" + "="*80)
    print("2. ML PREDICTIONS")
    print("="*80)
    
    predictions_file = OUTPUT_DIR / f'rivers_grit_ml_classified_{region.lower()}.gpkg'
    
    if predictions_file.exists():
        predictions = gpd.read_file(predictions_file)
        print(f"✓ Loaded: {len(predictions):,} segments")
        
        print(f"\n📋 Columns ({len(predictions.columns)}):")
        for col in predictions.columns:
            print(f"   - {col:30s} ({predictions[col].dtype})")
        
        print(f"\n🔍 Key columns check:")
        key_cols = ['global_id', 'salinity_class_final', 'confidence_level', 'dist_to_coast_km']
        for col in key_cols:
            if col in predictions.columns:
                print(f"   ✓ {col}")
            else:
                print(f"   ❌ {col} NOT FOUND")
        
        if 'index_right' in predictions.columns:
            print(f"\n   ⚠️  WARNING: 'index_right' exists! (will cause spatial join conflict)")
        else:
            print(f"\n   ✅ No 'index_right' column")
        
        if 'salinity_class_final' in predictions.columns:
            print(f"\n   Salinity classes:")
            for val, count in predictions['salinity_class_final'].value_counts().items():
                print(f"      {val:15s}: {count:,}")
    else:
        print(f"❌ Not found: {predictions_file}")
    
    # =========================================================================
    # 3. Inspect ML Features
    # =========================================================================
    print("\n" + "="*80)
    print("3. ML FEATURES")
    print("="*80)
    
    features_file = ML_DIR / f'features_{region.lower()}.parquet'
    
    if features_file.exists():
        features = pd.read_parquet(features_file)
        print(f"✓ Loaded: {len(features):,} segments")
        
        print(f"\n📋 Columns ({len(features.columns)}):")
        for col in features.columns:
            print(f"   - {col:30s} ({features[col].dtype})")
        
        if 'dist_to_coast_km' in features.columns:
            print(f"\n   Distance stats:")
            print(f"      min: {features['dist_to_coast_km'].min():.1f} km")
            print(f"      max: {features['dist_to_coast_km'].max():.1f} km")
            print(f"      mean: {features['dist_to_coast_km'].mean():.1f} km")
    else:
        print(f"❌ Not found: {features_file}")
    
    # =========================================================================
    # 4. Test Spatial Join (Simulation)
    # =========================================================================
    print("\n" + "="*80)
    print("4. SPATIAL JOIN TEST")
    print("="*80)
    
    if durr_file.exists() and predictions_file.exists():
        print("Testing spatial join logic...")
        
        # Reset indexes
        predictions_test = predictions.reset_index(drop=True)
        durr_test = durr.reset_index(drop=True)
        
        # Remove index_right if exists
        if 'index_right' in predictions_test.columns:
            predictions_test = predictions_test.drop(columns=['index_right'])
            print("   ✓ Removed 'index_right' from predictions")
        
        if 'index_right' in durr_test.columns:
            durr_test = durr_test.drop(columns=['index_right'])
            print("   ✓ Removed 'index_right' from Dürr")
        
        print(f"\n   Ready for spatial join:")
        print(f"      Predictions: {len(predictions_test):,} features")
        print(f"      Dürr: {len(durr_test):,} features")
        print(f"      Predictions CRS: {predictions_test.crs}")
        print(f"      Dürr CRS: {durr_test.crs}")
        
        if predictions_test.crs != durr_test.crs:
            print(f"   ⚠️  CRS mismatch! Will need reprojection")
        else:
            print(f"   ✅ CRS match!")
    
    print("\n" + "="*80)
    print("✅ INSPECTION COMPLETE")
    print("="*80)
    print("\nRecommendations:")
    print("1. Check FIN_TYP data types above")
    print("2. Verify all expected columns exist")
    print("3. Confirm spatial join will work")
    print("4. Update validation code based on actual data structure")


if __name__ == '__main__':
    main()
