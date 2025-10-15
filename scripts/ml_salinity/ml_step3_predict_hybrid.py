"""
HYBRID ML PREDICTION: Two-Stage Coastal/Inland Model
====================================================

Implements smart two-stage prediction strategy:
1. INLAND (>50km): Use DynQual-only model (19 features)
2. COASTAL (<50km): Use DynQual+GCC model (50+ features)

This leverages GCC's coastal strength while avoiding sparse data issues inland!

Scientific Justification:
- GCC designed for coastal processes (Athanasiou 2024)
- 80-90% coverage in coastal zones (<50km)
- <10% coverage inland (not useful there)
- Tidal range is PRIMARY control on salinity intrusion (Savenije 2012)

Usage:
    python scripts/ml_salinity/ml_step3_predict_hybrid.py --region SP
    python scripts/ml_salinity/ml_step3_predict_hybrid.py --all-regions
"""

import sys
import time
import argparse
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
import joblib

warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ML_DIR = BASE_DIR / 'data' / 'processed' / 'ml_features'
MODEL_DIR = BASE_DIR / 'data' / 'processed' / 'ml_models'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
OUTPUT_DIR = PROCESSED_DIR / 'ml_classified_hybrid'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GRIT_REGIONS = ['AF', 'AS', 'EU', 'NA', 'SA', 'SI', 'SP']

# CRITICAL: Distance threshold for coastal vs inland
COASTAL_THRESHOLD_KM = 50  # GCC coverage drops sharply beyond 50km

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")


def load_models():
    """Load both inland and coastal models"""
    print_section("📂 LOADING HYBRID MODELS")
    
    # Inland model (DynQual only)
    inland_model_file = MODEL_DIR / 'salinity_classifier_rf_inland.pkl'
    inland_encoder_file = MODEL_DIR / 'label_encoder_inland.pkl'
    inland_features_file = MODEL_DIR / 'feature_columns_inland.txt'
    
    # Coastal model (DynQual + GCC)
    coastal_model_file = MODEL_DIR / 'salinity_classifier_rf_coastal.pkl'
    coastal_encoder_file = MODEL_DIR / 'label_encoder_coastal.pkl'
    coastal_features_file = MODEL_DIR / 'feature_columns_coastal.txt'
    
    # Check if hybrid models exist
    if not inland_model_file.exists():
        print(f"⚠️  Hybrid models not trained yet!")
        print(f"\n🔧 Run training script first:")
        print(f"   python scripts/ml_salinity/ml_step2_train_model_hybrid.py")
        return None
    
    # Load inland model
    inland_model = joblib.load(inland_model_file)
    inland_encoder = joblib.load(inland_encoder_file)
    with open(inland_features_file, 'r') as f:
        inland_features = [line.strip() for line in f.readlines()]
    
    print(f"✓ Inland model loaded: {len(inland_features)} features")
    print(f"   For segments >50 km from coast")
    
    # Load coastal model
    coastal_model = joblib.load(coastal_model_file)
    coastal_encoder = joblib.load(coastal_encoder_file)
    with open(coastal_features_file, 'r') as f:
        coastal_features = [line.strip() for line in f.readlines()]
    
    print(f"✓ Coastal model loaded: {len(coastal_features)} features")
    print(f"   For segments <50 km from coast (with GCC!)")
    
    return {
        'inland': {'model': inland_model, 'encoder': inland_encoder, 'features': inland_features},
        'coastal': {'model': coastal_model, 'encoder': coastal_encoder, 'features': coastal_features}
    }


def predict_hybrid(region_code: str, models: dict):
    """
    Hybrid prediction: Coastal model for <50km, Inland model for >50km
    """
    print_section(f"🔮 HYBRID PREDICTION: {region_code}")
    
    # Load features
    feature_file = ML_DIR / f'features_{region_code.lower()}.parquet'
    if not feature_file.exists():
        print(f"❌ Features not found: {feature_file}")
        return None
    
    features = pd.read_parquet(feature_file)
    print(f"✓ Loaded {len(features):,} segments")
    
    # Load original segments (for geometry)
    segments_file = PROCESSED_DIR / f'rivers_grit_segments_classified_{region_code.lower()}.gpkg'
    segments = gpd.read_file(segments_file)
    
    # Separate validated vs to-predict
    has_salinity = features['has_salinity'] == 1
    validated = features[has_salinity].copy()
    to_predict = features[~has_salinity].copy()
    
    print(f"\n📊 Data Split:")
    print(f"   Validated (GlobSalt): {len(validated):,} ({len(validated)/len(features)*100:.1f}%)")
    print(f"   To predict (ML): {len(to_predict):,} ({len(to_predict)/len(features)*100:.1f}%)")
    
    if len(to_predict) == 0:
        print(f"\n⚠️  All segments have GlobSalt data - nothing to predict!")
        result = segments.copy()
        result['classification_method'] = 'GlobSalt_Validated'
        result['confidence_level'] = 'HIGH'
        result['prediction_probability'] = 1.0
        return result
    
    # =========================================================================
    # CRITICAL: Split by distance for hybrid modeling
    # =========================================================================
    print(f"\n🌊 Splitting by distance threshold ({COASTAL_THRESHOLD_KM} km)...")
    
    coastal_mask = to_predict['dist_to_coast_km'] <= COASTAL_THRESHOLD_KM
    inland_mask = to_predict['dist_to_coast_km'] > COASTAL_THRESHOLD_KM
    
    coastal_segments = to_predict[coastal_mask].copy()
    inland_segments = to_predict[inland_mask].copy()
    
    print(f"   Coastal (<{COASTAL_THRESHOLD_KM}km): {len(coastal_segments):,} ({len(coastal_segments)/len(to_predict)*100:.1f}%)")
    print(f"   Inland (>{COASTAL_THRESHOLD_KM}km): {len(inland_segments):,} ({len(inland_segments)/len(to_predict)*100:.1f}%)")
    
    # =========================================================================
    # PREDICT COASTAL SEGMENTS (with GCC features!)
    # =========================================================================
    if len(coastal_segments) > 0:
        print(f"\n🌊 Predicting COASTAL segments (DynQual + GCC model)...")
        
        coastal_model = models['coastal']['model']
        coastal_encoder = models['coastal']['encoder']
        coastal_features = models['coastal']['features']
        
        # Check for missing features
        missing = [f for f in coastal_features if f not in coastal_segments.columns]
        if missing:
            print(f"   ⚠️  Missing {len(missing)} GCC features (expected for some regions)")
            print(f"   Filling with median values...")
            for feat in missing:
                coastal_segments[feat] = 0  # Fill missing GCC with 0
        
        X_coastal = coastal_segments[coastal_features].copy()
        
        # Fill NaN
        for col in X_coastal.columns:
            if X_coastal[col].isna().any():
                median_val = X_coastal[col].median()
                if pd.isna(median_val):
                    median_val = 0
                X_coastal[col].fillna(median_val, inplace=True)
        
        # Predict
        y_pred_coastal = coastal_model.predict(X_coastal)
        y_prob_coastal = coastal_model.predict_proba(X_coastal)
        
        coastal_segments['predicted_class'] = coastal_encoder.inverse_transform(y_pred_coastal)
        coastal_segments['prediction_probability'] = y_prob_coastal.max(axis=1)
        coastal_segments['classification_method'] = 'ML_Coastal'
        
        print(f"   ✓ Predicted {len(coastal_segments):,} coastal segments")
    
    # =========================================================================
    # PREDICT INLAND SEGMENTS (DynQual only)
    # =========================================================================
    if len(inland_segments) > 0:
        print(f"\n🏞️  Predicting INLAND segments (DynQual-only model)...")
        
        inland_model = models['inland']['model']
        inland_encoder = models['inland']['encoder']
        inland_features = models['inland']['features']
        
        X_inland = inland_segments[inland_features].copy()
        
        # Fill NaN
        for col in X_inland.columns:
            if X_inland[col].isna().any():
                median_val = X_inland[col].median()
                if pd.isna(median_val):
                    median_val = 0
                X_inland[col].fillna(median_val, inplace=True)
        
        # Predict
        y_pred_inland = inland_model.predict(X_inland)
        y_prob_inland = inland_model.predict_proba(X_inland)
        
        inland_segments['predicted_class'] = inland_encoder.inverse_transform(y_pred_inland)
        inland_segments['prediction_probability'] = y_prob_inland.max(axis=1)
        inland_segments['classification_method'] = 'ML_Inland'
        
        print(f"   ✓ Predicted {len(inland_segments):,} inland segments")
    
    # =========================================================================
    # COMBINE PREDICTIONS
    # =========================================================================
    # Combine coastal and inland predictions
    predicted_dfs = []
    if len(coastal_segments) > 0:
        predicted_dfs.append(coastal_segments)
    if len(inland_segments) > 0:
        predicted_dfs.append(inland_segments)
    
    if len(predicted_dfs) == 0:
        all_predicted = pd.DataFrame()
    else:
        all_predicted = pd.concat(predicted_dfs, ignore_index=True)
    
    # Assign confidence levels
    def get_confidence_level(prob):
        if prob > 0.75:
            return 'HIGH'
        elif prob > 0.60:
            return 'MEDIUM'
        elif prob > 0.45:
            return 'LOW'
        else:
            return 'VERY-LOW'
    
    all_predicted['confidence_level'] = all_predicted['prediction_probability'].apply(get_confidence_level)
    
    # =========================================================================
    # DISTANCE-BASED CONSTRAINTS (still apply!)
    # =========================================================================
    print(f"\n🔧 Applying distance-based constraints...")
    
    # Rule: >200 km = freshwater (physically impossible)
    far_inland = all_predicted['dist_to_coast_km'] > 200
    estuarine_pred = all_predicted['predicted_class'].isin(['Oligohaline', 'Mesohaline', 'Polyhaline'])
    
    far_estuarine = far_inland & estuarine_pred
    if far_estuarine.sum() > 0:
        print(f"   ⚠️  Reclassifying {far_estuarine.sum():,} estuarine predictions >200km as Freshwater")
        all_predicted.loc[far_estuarine, 'predicted_class'] = 'Freshwater'
        all_predicted.loc[far_estuarine, 'confidence_level'] = 'HIGH'
        all_predicted.loc[far_estuarine, 'classification_method'] = 'Rule_Based_Distance'
    
    # =========================================================================
    # ADD VALIDATED SEGMENTS
    # =========================================================================
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
    
    # Combine all (make sure we have dist_to_coast_km from both sources)
    # Validated segments already have it from features df
    # Predicted segments have it from to_predict df (which came from features)
    all_classified = pd.concat([validated, all_predicted], ignore_index=True)
    
    # Ensure dist_to_coast_km is present (should already be there, but double-check)
    if 'dist_to_coast_km' not in all_classified.columns:
        all_classified = all_classified.merge(
            features[['global_id', 'dist_to_coast_km']],
            on='global_id',
            how='left'
        )
    
    # Merge with geometries
    result = segments.merge(
        all_classified[['global_id', 'predicted_class', 'prediction_probability',
                        'confidence_level', 'classification_method', 'dist_to_coast_km']],
        on='global_id',
        how='left'
    )
    
    result.rename(columns={'predicted_class': 'salinity_class_final'}, inplace=True)
    
    # =========================================================================
    # SUMMARY STATISTICS
    # =========================================================================
    print(f"\n📊 Prediction Summary:")
    for cls, count in result['salinity_class_final'].value_counts().items():
        print(f"   {cls:15s}: {count:>7,} ({count/len(result)*100:>5.1f}%)")
    
    print(f"\n🎯 Confidence Distribution:")
    for conf, count in result['confidence_level'].value_counts().items():
        print(f"   {conf:15s}: {count:>7,} ({count/len(result)*100:>5.1f}%)")
    
    print(f"\n📊 Classification Method:")
    for method, count in result['classification_method'].value_counts().items():
        print(f"   {method:25s}: {count:>7,} ({count/len(result)*100:>5.1f}%)")
    
    # Estuarine percentage
    estuarine = result['salinity_class_final'].isin(['Oligohaline', 'Mesohaline', 'Polyhaline', 'Euhaline'])
    estuarine_pct = estuarine.sum() / len(result) * 100
    print(f"\n🌊 Estuarine Segments (0.5-30 PSU): {estuarine.sum():,} ({estuarine_pct:.1f}%)")
    
    # Breakdown by zone
    if len(coastal_segments) > 0:
        coastal_est = result[
            (result['dist_to_coast_km'] <= COASTAL_THRESHOLD_KM) &
            (result['salinity_class_final'].isin(['Oligohaline', 'Mesohaline', 'Polyhaline']))
        ]
        print(f"   Coastal zone (<{COASTAL_THRESHOLD_KM}km): {len(coastal_est):,} estuarine")
    
    if len(inland_segments) > 0:
        inland_est = result[
            (result['dist_to_coast_km'] > COASTAL_THRESHOLD_KM) &
            (result['salinity_class_final'].isin(['Oligohaline', 'Mesohaline', 'Polyhaline']))
        ]
        print(f"   Inland zone (>{COASTAL_THRESHOLD_KM}km): {len(inland_est):,} estuarine")
    
    # Save
    output_file = OUTPUT_DIR / f'rivers_grit_ml_classified_hybrid_{region_code.lower()}.gpkg'
    print(f"\n💾 Saving: {output_file.name}")
    
    start_save = time.time()
    result.to_file(output_file, driver='GPKG', engine='pyogrio')
    elapsed_save = time.time() - start_save
    
    print(f"✓ Saved: {output_file} (took {elapsed_save:.1f}s)")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description='Hybrid ML prediction with coastal/inland models'
    )
    parser.add_argument('--region', type=str, choices=GRIT_REGIONS,
                        help='Process single region')
    parser.add_argument('--all-regions', action='store_true',
                        help='Process all regions')
    args = parser.parse_args()
    
    print("="*80)
    print("🤖 HYBRID ML PREDICTION PIPELINE")
    print("="*80)
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n🔬 Two-Stage Approach:")
    print(f"   Coastal (<{COASTAL_THRESHOLD_KM}km): DynQual + GCC (50+ features)")
    print(f"   Inland (>{COASTAL_THRESHOLD_KM}km): DynQual only (19 features)")
    
    # Load models
    models = load_models()
    if models is None:
        sys.exit(1)
    
    # Determine regions
    if args.all_regions:
        regions = GRIT_REGIONS
    elif args.region:
        regions = [args.region]
    else:
        print("\n❌ Error: Specify --region or --all-regions")
        sys.exit(1)
    
    print(f"\n📋 Regions to process: {', '.join(regions)}")
    
    # Process each region
    for region_code in regions:
        try:
            result = predict_hybrid(region_code, models)
            if result is None:
                print(f"\n⚠️  Skipping {region_code}")
                continue
        except Exception as e:
            print(f"\n❌ Error processing {region_code}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "="*80)
    print("✅ HYBRID PREDICTION COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
