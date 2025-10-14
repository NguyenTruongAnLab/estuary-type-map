"""
VERIFY FEATURE CONSISTENCY ACROSS ALL DATASETS
===============================================

This script checks that all required features exist in all datasets
and that column names are consistent across the pipeline.

Usage:
    python scripts/ml_salinity/verify_feature_consistency.py
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ML_DIR = BASE_DIR / 'data' / 'processed' / 'ml_features'
MODEL_DIR = BASE_DIR / 'data' / 'processed' / 'ml_models'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'

GRIT_REGIONS = ['AF', 'AS', 'EU', 'NA', 'SA', 'SI', 'SP']

def print_section(title: str):
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")

def verify_models():
    """Check what features the trained models expect"""
    print_section("TRAINED MODELS - EXPECTED FEATURES")
    
    # Inland model
    inland_features_file = MODEL_DIR / 'feature_columns_inland.txt'
    if inland_features_file.exists():
        with open(inland_features_file, 'r') as f:
            inland_features = [line.strip() for line in f if line.strip()]
        print(f"\n🏞️  INLAND MODEL ({len(inland_features)} features):")
        for i, feat in enumerate(inland_features, 1):
            print(f"   {i:2d}. {feat}")
    else:
        print(f"\n❌ Inland model not trained yet")
    
    # Coastal model
    coastal_features_file = MODEL_DIR / 'feature_columns_coastal.txt'
    if coastal_features_file.exists():
        with open(coastal_features_file, 'r') as f:
            coastal_features = [line.strip() for line in f if line.strip()]
        print(f"\n🌊 COASTAL MODEL ({len(coastal_features)} features):")
        for i, feat in enumerate(coastal_features, 1):
            print(f"   {i:2d}. {feat}")
    else:
        print(f"\n❌ Coastal model not trained yet")
    
    return inland_features if inland_features_file.exists() else None, \
           coastal_features if coastal_features_file.exists() else None

def verify_features_file(region_code: str, expected_inland: list, expected_coastal: list):
    """Verify a single region's feature file"""
    
    feature_file = ML_DIR / f'features_{region_code.lower()}.parquet'
    
    if not feature_file.exists():
        print(f"\n❌ {region_code}: Feature file not found")
        return False
    
    features = pd.read_parquet(feature_file)
    
    print(f"\n✅ {region_code}: {len(features):,} segments, {len(features.columns)} columns")
    
    # Check for required base features
    required_base = [
        'global_id', 'dist_to_coast_km', 'log_dist_to_coast', 
        'strahler_order', 'length', 'upstream_area', 'sinuosity', 
        'azimuth', 'is_mainstem', 'salinity_mean_psu', 'has_salinity'
    ]
    
    missing_base = [f for f in required_base if f not in features.columns]
    if missing_base:
        print(f"   ⚠️  Missing base features: {missing_base}")
    
    # Check for DynQual temperature
    if 'dynqual_temperature_C' in features.columns:
        valid_temp = features['dynqual_temperature_C'].notna().sum()
        print(f"   ✅ DynQual temperature: {valid_temp:,} / {len(features):,} valid ({valid_temp/len(features)*100:.1f}%)")
    else:
        print(f"   ❌ DynQual temperature: MISSING")
    
    # Check for GCC features (optional, only for coastal)
    gcc_features = [col for col in features.columns if col.startswith('gcc_')]
    if gcc_features:
        print(f"   ✅ GCC features: {len(gcc_features)} features")
        # Check coverage
        gcc_coverage = features[gcc_features].notna().all(axis=1).sum()
        print(f"      Coverage: {gcc_coverage:,} / {len(features):,} segments ({gcc_coverage/len(features)*100:.1f}%)")
    else:
        print(f"   ⚠️  GCC features: None (may need to run add_gcc_to_features.py)")
    
    # Check against expected model features
    if expected_inland:
        missing_inland = [f for f in expected_inland if f not in features.columns]
        if missing_inland:
            print(f"   ⚠️  Missing for INLAND model: {missing_inland}")
        else:
            print(f"   ✅ All INLAND model features present")
    
    if expected_coastal:
        missing_coastal = [f for f in expected_coastal if f not in features.columns]
        if missing_coastal:
            print(f"   ⚠️  Missing for COASTAL model ({len(missing_coastal)} features)")
            print(f"      (This is OK if GCC not processed for this region yet)")
        else:
            print(f"   ✅ All COASTAL model features present")
    
    return True

def verify_segments_file(region_code: str):
    """Verify what's in the original GRIT segments file"""
    
    segments_file = PROCESSED_DIR / f'rivers_grit_segments_classified_{region_code.lower()}.gpkg'
    
    if not segments_file.exists():
        print(f"\n❌ {region_code}: Segments file not found")
        return False
    
    segments = gpd.read_file(segments_file)
    
    print(f"\n📊 {region_code} GRIT Segments: {len(segments):,} segments")
    print(f"   Columns: {list(segments.columns)[:15]}...")
    
    # Check critical columns
    if 'dist_to_coast_km' in segments.columns:
        print(f"   ✅ Has dist_to_coast_km in segments (unusual!)")
    else:
        print(f"   ℹ️  No dist_to_coast_km in segments (expected - calculated in Step 1)")
    
    return True

def main():
    print("\n" + "="*80)
    print("FEATURE CONSISTENCY VERIFICATION")
    print("="*80)
    print("\nThis script checks that all features are consistent across:")
    print("  1. Trained models (expected features)")
    print("  2. Feature files (ml_features/*.parquet)")
    print("  3. Original GRIT segments")
    
    # Check models
    expected_inland, expected_coastal = verify_models()
    
    # Check each region
    print_section("FEATURE FILES BY REGION")
    
    all_ok = True
    for region in GRIT_REGIONS:
        if not verify_features_file(region, expected_inland, expected_coastal):
            all_ok = False
    
    # Sample check of segments file
    print_section("SAMPLE: GRIT SEGMENTS FILE (SP)")
    verify_segments_file('SP')
    
    # Summary
    print("\n" + "="*80)
    if all_ok:
        print("✅ ALL FEATURE FILES OK")
    else:
        print("⚠️  SOME ISSUES FOUND - Check output above")
    print("="*80)
    
    print("\n📊 KEY FINDINGS:")
    print("   • dist_to_coast_km is calculated in Step 1 (NOT in original GRIT)")
    print("   • DynQual temperature should be added in Step 2")
    print("   • GCC features should be added in Step 3 (optional)")
    print("   • Models expect specific feature names (see above)")
    
    print("\n💡 IF MISSING FEATURES:")
    print("   1. Re-run Step 1: python scripts/ml_salinity/ml_step1_extract_features.py --all-regions")
    print("   2. Re-run Step 2: python scripts/ml_salinity/add_dynqual_to_features.py --all-regions")
    print("   3. Re-run Step 3: python scripts/ml_salinity/add_gcc_to_features.py --all-regions")
    print("   4. Re-train model: python scripts/ml_salinity/ml_step2_train_model_hybrid.py")

if __name__ == '__main__':
    main()
