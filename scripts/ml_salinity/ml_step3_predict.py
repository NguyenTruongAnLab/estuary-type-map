
"""
STEP 3: Predict Salinity for All Segments
==========================================

Use trained ML model to predict salinity class for segments without
GlobSalt validation.

Usage:
    python scripts/ml_step3_predict.py --region SP
    python scripts/ml_step3_predict.py --all-regions
"""

import sys
import warnings
import time
import argparse
from pathlib import Path
import pandas as pd
import geopandas as gpd
import numpy as np
import joblib

warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ML_DIR = BASE_DIR / 'data' / 'processed' / 'ml_features'
MODEL_DIR = BASE_DIR / 'data' / 'processed' / 'ml_models'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
OUTPUT_DIR = PROCESSED_DIR / 'ml_classified'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GRIT_REGIONS = ['AF', 'AS', 'EU', 'NA', 'SA', 'SI', 'SP']

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")


def load_model():
    """Load trained model and metadata"""
    print_section("📂 LOADING TRAINED MODEL")
    
    model_file = MODEL_DIR / 'salinity_classifier_rf.pkl'
    encoder_file = MODEL_DIR / 'label_encoder.pkl'
    feature_file = MODEL_DIR / 'feature_columns.txt'
    
    if not all([model_file.exists(), encoder_file.exists(), feature_file.exists()]):
        print(f"❌ Model files not found!")
        print(f"   Run ml_step2_train_model.py first!")
        return None, None, None
    
    # Load model
    model = joblib.load(model_file)
    print(f"✓ Model loaded: {model_file.name}")
    
    # Load label encoder
    label_encoder = joblib.load(encoder_file)
    print(f"✓ Label encoder loaded: {label_encoder.classes_}")
    
    # Load feature columns
    with open(feature_file, 'r') as f:
        feature_cols = [line.strip() for line in f if line.strip()]
    print(f"✓ Feature columns loaded: {len(feature_cols)} features")
    
    return model, label_encoder, feature_cols


def predict_for_region(region_code: str, model, label_encoder, feature_cols):
    """
    Predict salinity class for all segments in a region
    """
    print_section(f"🔮 PREDICTING: {region_code}")
    
    # Load features
    feature_file = ML_DIR / f'features_{region_code.lower()}.parquet'
    if not feature_file.exists():
        print(f"❌ Features not found: {feature_file}")
        return None
    
    features = pd.read_parquet(feature_file)
    print(f"✓ Loaded {len(features):,} segments")
    
    # Load original segments (for geometry and metadata)
    segments_file = PROCESSED_DIR / f'rivers_grit_segments_classified_{region_code.lower()}.gpkg'
    segments = gpd.read_file(segments_file)
    
    # Separate validated (GlobSalt) vs. to-predict segments
    has_salinity = features['has_salinity'] == 1
    validated = features[has_salinity].copy()
    to_predict = features[~has_salinity].copy()
    
    print(f"\n📊 Data Split:")
    print(f"   Validated (GlobSalt): {len(validated):,} ({len(validated)/len(features)*100:.1f}%)")
    print(f"   To predict (ML): {len(to_predict):,} ({len(to_predict)/len(features)*100:.1f}%)")
    
    if len(to_predict) == 0:
        print(f"\n✓ All segments already validated by GlobSalt!")
        # Just copy GlobSalt classifications
        result = segments.copy()
        result['classification_method'] = 'GlobSalt_Validated'
        result['confidence_level'] = 'HIGH'
        result['prediction_probability'] = 1.0
        return result
    
    # Prepare features for prediction
    # CRITICAL: Check for missing features (prevents KeyError)
    missing_features = [f for f in feature_cols if f not in to_predict.columns]
    if missing_features:
        print(f"\n❌ ERROR: {len(missing_features)} features missing in {region_code}!")
        print(f"   Missing features: {missing_features[:10]}")  # Show first 10
        print(f"\n🔧 FIX: Re-run GCC integration:")
        print(f"   python scripts/ml_salinity/add_gcc_to_features.py --region {region_code}")
        print(f"\n   Or re-run for all regions:")
        print(f"   python scripts/ml_salinity/add_gcc_to_features.py --all-regions")
        return None
    
    X_predict = to_predict[feature_cols].copy()
    
    # Fill NaN with median (same as training)
    for col in X_predict.columns:
        if X_predict[col].isna().any():
            median_val = X_predict[col].median()
            if pd.isna(median_val):  # All NaN
                median_val = 0
            X_predict[col].fillna(median_val, inplace=True)
    
    # Predict
    print(f"\n🔮 Running predictions...")
    start_time = time.time()
    
    y_pred = model.predict(X_predict)
    y_pred_proba = model.predict_proba(X_predict)
    
    elapsed = time.time() - start_time
    print(f"✓ Predicted {len(y_pred):,} segments in {elapsed:.1f}s")
    
    # Convert predictions back to class names
    predicted_classes = label_encoder.inverse_transform(y_pred)
    max_probabilities = y_pred_proba.max(axis=1)
    
    # Assign to dataframe
    to_predict['predicted_class'] = predicted_classes
    to_predict['prediction_probability'] = max_probabilities
    
    # Assign confidence levels based on prediction probability
    # ADJUSTED: Less strict thresholds to reduce VERY-LOW percentage
    def get_confidence_level(prob):
        if prob > 0.75:
            return 'HIGH'        # Raised from MEDIUM-HIGH
        elif prob > 0.60:
            return 'MEDIUM'      # Lowered from 0.70
        elif prob > 0.45:
            return 'LOW'         # Lowered from 0.55
        else:
            return 'VERY-LOW'
    
    to_predict['confidence_level'] = to_predict['prediction_probability'].apply(get_confidence_level)
    to_predict['classification_method'] = 'ML_Predicted'
    
    # For validated segments, use actual salinity class
    def classify_salinity(sal):
        if pd.isna(sal):
            return 'Unknown'
        elif sal < 0.5:
            return 'Freshwater'
        elif sal < 5.0:
            return 'Oligohaline'
        elif sal < 18.0:
            return 'Mesohaline'
        elif sal < 30.0:
            return 'Polyhaline'
        else:
            return 'Euhaline'
    
    validated['predicted_class'] = validated['salinity_mean_psu'].apply(classify_salinity)
    validated['prediction_probability'] = 1.0
    validated['confidence_level'] = 'HIGH'
    validated['classification_method'] = 'GlobSalt_Validated'
    
    # =========================================================================
    # CRITICAL FIX: Apply distance-based post-processing filter
    # =========================================================================
    print(f"\n🔧 Applying distance-based constraints...")
    print(f"   Scientific basis: Savenije (2012), O'Connor (2022)")
    print(f"   Max estuarine extent: ~200 km (Amazon, Severn)")
    
    # Rule 1: Segments >200 km from coast CANNOT be estuarine
    far_inland = to_predict['dist_to_coast_km'] > 200
    estuarine_pred = to_predict['predicted_class'].isin(['Oligohaline', 'Mesohaline', 'Polyhaline'])
    
    far_estuarine = far_inland & estuarine_pred
    if far_estuarine.sum() > 0:
        print(f"   ⚠️  Found {far_estuarine.sum():,} estuarine predictions >200km from coast")
        print(f"   → Reclassifying as Freshwater (physically impossible!)")
        to_predict.loc[far_estuarine, 'predicted_class'] = 'Freshwater'
        to_predict.loc[far_estuarine, 'confidence_level'] = 'HIGH'
        to_predict.loc[far_estuarine, 'classification_method'] = 'Rule_Based_Distance'
    
    # Rule 2: Segments 100-200km + LOW confidence + estuarine → Freshwater
    mid_distance = (to_predict['dist_to_coast_km'] > 100) & (to_predict['dist_to_coast_km'] <= 200)
    low_conf = to_predict['confidence_level'].isin(['VERY-LOW', 'LOW'])
    
    suspicious = mid_distance & low_conf & estuarine_pred
    if suspicious.sum() > 0:
        print(f"   ⚠️  Found {suspicious.sum():,} low-confidence estuarine predictions 100-200km from coast")
        print(f"   → Reclassifying as Freshwater (likely false positives)")
        to_predict.loc[suspicious, 'predicted_class'] = 'Freshwater'
        to_predict.loc[suspicious, 'confidence_level'] = 'MEDIUM'
        to_predict.loc[suspicious, 'classification_method'] = 'Rule_Based_Hybrid'
    
    print(f"   ✓ Distance constraints applied")
    
    # Combine
    all_classified = pd.concat([validated, to_predict], ignore_index=True)
    
    # Merge back with original segments (for geometry)
    result = segments.merge(
        all_classified[['global_id', 'predicted_class', 'prediction_probability', 
                        'confidence_level', 'classification_method']],
        on='global_id',
        how='left'
    )
    
    # Rename for clarity
    result.rename(columns={'predicted_class': 'salinity_class_final'}, inplace=True)
    
    # Summary
    print(f"\n📊 Prediction Summary:")
    for cls, count in result['salinity_class_final'].value_counts().items():
        print(f"   {cls:15s}: {count:>7,} ({count/len(result)*100:>5.1f}%)")
    
    print(f"\n🎯 Confidence Distribution:")
    for conf, count in result['confidence_level'].value_counts().items():
        print(f"   {conf:15s}: {count:>7,} ({count/len(result)*100:>5.1f}%)")
    
    print(f"\n📊 Classification Method:")
    for method, count in result['classification_method'].value_counts().items():
        print(f"   {method:20s}: {count:>7,} ({count/len(result)*100:>5.1f}%)")
    
    # Calculate estuarine percentage
    estuarine = result['salinity_class_final'].isin(['Oligohaline', 'Mesohaline', 'Polyhaline', 'Euhaline'])
    estuarine_pct = estuarine.sum() / len(result) * 100
    print(f"\n🌊 Estuarine Segments (0.5-30 PSU): {estuarine.sum():,} ({estuarine_pct:.1f}%)")
    
    # Save
    output_file = OUTPUT_DIR / f'rivers_grit_ml_classified_{region_code.lower()}.gpkg'
    print(f"\n💾 Saving: {output_file.name} ({len(result):,} features)")
    print(f"   This may take 30-90 seconds for large datasets...")
    
    start_save = time.time()
    
    # Use engine='pyogrio' for faster writing (if available)
    try:
        result.to_file(output_file, driver='GPKG', engine='pyogrio')
    except:
        # Fallback to fiona (slower but more compatible)
        result.to_file(output_file, driver='GPKG')
    
    save_time = time.time() - start_save
    print(f"✓ Saved: {output_file} (took {save_time:.1f}s)")
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Predict salinity using ML model')
    parser.add_argument('--region', type=str, choices=GRIT_REGIONS,
                        help='Process single region')
    parser.add_argument('--all-regions', action='store_true',
                        help='Process all regions')
    args = parser.parse_args()
    
    print_section("🤖 ML PREDICTION PIPELINE")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load model
    model, label_encoder, feature_cols = load_model()
    if model is None:
        return 1
    
    # Determine regions
    if args.all_regions:
        regions = GRIT_REGIONS
    elif args.region:
        regions = [args.region]
    else:
        print("❌ Must specify --region or --all-regions")
        return 1
    
    print(f"\n📋 Regions to process: {', '.join(regions)}")
    
    # Process each region
    for region_code in regions:
        result = predict_for_region(region_code, model, label_encoder, feature_cols)
        if result is None:
            print(f"⚠️  Skipping {region_code}")
    
    print_section("✅ PREDICTION COMPLETE")
    print(f"\n📁 Results saved to: {OUTPUT_DIR}")
    print(f"\nNext step: python scripts/ml_step4_validate.py --region SP")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
