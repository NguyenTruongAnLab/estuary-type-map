"""
HYBRID MODEL TRAINING: Separate Coastal and Inland Models
==========================================================

Trains TWO Random Forest models:
1. INLAND MODEL (>50km): DynQual-only features (19 features)
2. COASTAL MODEL (<50km): DynQual + GCC features (50+ features)

Scientific Rationale:
- GCC has 80-90% coverage in coastal zones (<50km)
- GCC has <10% coverage inland (sparse data hurts performance)
- Tidal range is CRITICAL for estuarine extent (Savenije 2012)
- Separate models optimize for each zone's data characteristics

Usage:
    python scripts/ml_salinity/ml_step2_train_model_hybrid.py
"""

import sys
import time
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
import joblib
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ML_DIR = BASE_DIR / 'data' / 'processed' / 'ml_features'
MODEL_DIR = BASE_DIR / 'data' / 'processed' / 'ml_models'
MODEL_DIR.mkdir(parents=True, exist_ok=True)

GRIT_REGIONS = ['AF', 'AS', 'EU', 'NA', 'SA', 'SI', 'SP']

# Spatial holdout
HOLDOUT_REGION = 'SP'
TRAIN_REGIONS = [r for r in GRIT_REGIONS if r != HOLDOUT_REGION]

# CRITICAL: Distance threshold
COASTAL_THRESHOLD_KM = 50

print(f"\n🔒 HYBRID MODEL CONFIGURATION:")
print(f"   Training regions: {TRAIN_REGIONS}")
print(f"   Holdout region: {HOLDOUT_REGION}")
print(f"   Coastal threshold: {COASTAL_THRESHOLD_KM} km")
print(f"   This trains TWO models for optimal performance!\n")

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")


def load_training_data():
    """Load features from all training regions"""
    print_section("📊 LOADING TRAINING DATA")
    
    all_features = []
    
    for region_code in TRAIN_REGIONS:
        feature_file = ML_DIR / f'features_{region_code.lower()}.parquet'
        if not feature_file.exists():
            print(f"⚠️  {region_code}: Features not found")
            continue
        
        df = pd.read_parquet(feature_file)
        has_salinity = df[df['has_salinity'] == 1].copy()
        
        if len(has_salinity) > 0:
            has_salinity['region'] = region_code
            all_features.append(has_salinity)
            print(f"✓ {region_code}: {len(has_salinity):,} segments with salinity")
        else:
            print(f"⚠️  {region_code}: 0 segments with salinity")
    
    global_data = pd.concat(all_features, ignore_index=True)
    
    print(f"\n📊 Global Training Data:")
    print(f"   Total segments: {len(global_data):,}")
    print(f"   Regions: {global_data['region'].nunique()}")
    
    return global_data


def classify_salinity(salinity_psu):
    """Venice System classification"""
    if pd.isna(salinity_psu):
        return None
    elif salinity_psu < 0.5:
        return 'Freshwater'
    elif salinity_psu < 5.0:
        return 'Oligohaline'
    elif salinity_psu < 18.0:
        return 'Mesohaline'
    elif salinity_psu < 30.0:
        return 'Polyhaline'
    else:
        return 'Euhaline'


def train_inland_model(global_data):
    """Train model for INLAND segments (>50km from coast)"""
    print_section("🏞️  TRAINING INLAND MODEL (DynQual-only)")
    
    # Filter to inland segments only
    inland_data = global_data[global_data['dist_to_coast_km'] > COASTAL_THRESHOLD_KM].copy()
    
    print(f"\n📊 Inland Training Data:")
    print(f"   Total segments: {len(inland_data):,} (>{COASTAL_THRESHOLD_KM}km from coast)")
    
    # Classify
    inland_data['class'] = inland_data['salinity_mean_psu'].apply(classify_salinity)
    inland_data = inland_data.dropna(subset=['class'])
    
    print(f"\n📊 Class Distribution:")
    for cls, count in inland_data['class'].value_counts().items():
        print(f"   {cls:15s}: {count:>7,} ({count/len(inland_data)*100:>5.1f}%)")
    
    # Select GRIT + Dürr + Temperature features (NO GCC for inland!)
    feature_cols = [
        # GRIT network features (EXCELLENT predictors!)
        'dist_to_coast_km', 'log_dist_to_coast', 'strahler_order',
        'length', 'upstream_area', 'sinuosity', 'azimuth', 'is_mainstem',
        'log_upstream_area', 'length_km', 'abs_latitude', 
        'dist_x_strahler', 'area_per_length',
        # Dürr estuary features
        'in_durr_estuary', 'durr_type_encoded',
        # DynQual temperature ONLY (climate proxy)
        'dynqual_temperature_C'
        # REMOVED: dynqual_salinity_psu (circular reasoning!)
        # REMOVED: dynqual_tds_mgL (poor quality, 10km resolution)
        # REMOVED: dynqual_discharge_m3s (use upstream_area instead!)
    ]
    
    # Check available features
    available_features = [f for f in feature_cols if f in inland_data.columns]
    print(f"\n📊 Feature Set: {len(available_features)} features")
    
    X = inland_data[available_features].copy()
    y = inland_data['class'].values
    
    # Fill NaN
    for col in X.columns:
        if X[col].isna().any():
            median_val = X[col].median()
            if pd.isna(median_val):
                median_val = 0
            X[col].fillna(median_val, inplace=True)
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"\n📊 Train/Test Split:")
    print(f"   Training: {len(X_train):,} segments")
    print(f"   Testing: {len(X_test):,} segments")
    
    # Train model
    print(f"\n🌲 Training Random Forest...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=30,
        min_samples_leaf=10,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n🎯 Inland Model Performance:")
    print(f"   Test Accuracy: {accuracy:.3f}")
    
    print(f"\n📊 Classification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=label_encoder.classes_,
        zero_division=0
    ))
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': available_features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n📊 Top 10 Features:")
    print(feature_importance.head(10).to_string(index=False))
    
    # Save model
    joblib.dump(model, MODEL_DIR / 'salinity_classifier_rf_inland.pkl')
    joblib.dump(label_encoder, MODEL_DIR / 'label_encoder_inland.pkl')
    with open(MODEL_DIR / 'feature_columns_inland.txt', 'w') as f:
        f.write('\n'.join(available_features))
    feature_importance.to_csv(MODEL_DIR / 'feature_importance_inland.csv', index=False)
    
    print(f"\n✅ Inland model saved")
    
    return model, label_encoder, available_features


def train_coastal_model(global_data):
    """Train model for COASTAL segments (<50km from coast) with GCC features"""
    print_section("🌊 TRAINING COASTAL MODEL (DynQual + GCC)")
    
    # Filter to coastal segments only
    coastal_data = global_data[global_data['dist_to_coast_km'] <= COASTAL_THRESHOLD_KM].copy()
    
    print(f"\n📊 Coastal Training Data:")
    print(f"   Total segments: {len(coastal_data):,} (<{COASTAL_THRESHOLD_KM}km from coast)")
    
    # Classify
    coastal_data['class'] = coastal_data['salinity_mean_psu'].apply(classify_salinity)
    coastal_data = coastal_data.dropna(subset=['class'])
    
    print(f"\n📊 Class Distribution:")
    for cls, count in coastal_data['class'].value_counts().items():
        print(f"   {cls:15s}: {count:>7,} ({count/len(coastal_data)*100:>5.1f}%)")
    
    # Select ALL features (DynQual + GCC)
    base_features = [
        'dist_to_coast_km', 'log_dist_to_coast', 'strahler_order',
        'length', 'upstream_area', 'sinuosity', 'azimuth', 'is_mainstem',
        'log_upstream_area', 'length_km', 'in_durr_estuary', 'durr_type_encoded',
        'abs_latitude', 'dist_x_strahler', 'area_per_length',
        'dynqual_tds_mgL', 'dynqual_discharge_m3s', 'dynqual_temperature_C', 'dynqual_salinity_psu'
    ]
    
    # Add GCC features if available
    gcc_features = [c for c in coastal_data.columns if c.startswith('gcc_')]
    
    feature_cols = base_features + gcc_features
    available_features = [f for f in feature_cols if f in coastal_data.columns]
    
    print(f"\n📊 Feature Set:")
    print(f"   Base features: {len(base_features)}")
    print(f"   GCC features: {len(gcc_features)}")
    print(f"   Total: {len(available_features)} features")
    
    # Check GCC coverage
    if len(gcc_features) > 0:
        gcc_coverage = coastal_data[gcc_features].notna().mean().mean() * 100
        print(f"   GCC coverage: {gcc_coverage:.1f}% (coastal zone)")
    
    X = coastal_data[available_features].copy()
    y = coastal_data['class'].values
    
    # Fill NaN
    for col in X.columns:
        if X[col].isna().any():
            median_val = X[col].median()
            if pd.isna(median_val):
                median_val = 0
            X[col].fillna(median_val, inplace=True)
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"\n📊 Train/Test Split:")
    print(f"   Training: {len(X_train):,} segments")
    print(f"   Testing: {len(X_test):,} segments")
    
    # Train model
    print(f"\n🌲 Training Random Forest...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=30,
        min_samples_leaf=10,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n🎯 Coastal Model Performance:")
    print(f"   Test Accuracy: {accuracy:.3f}")
    
    print(f"\n📊 Classification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=label_encoder.classes_,
        zero_division=0
    ))
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': available_features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n📊 Top 10 Features:")
    print(feature_importance.head(10).to_string(index=False))
    
    # Check if GCC features are in top 10
    gcc_in_top10 = feature_importance.head(10)['feature'].str.startswith('gcc_').sum()
    if gcc_in_top10 > 0:
        print(f"\n✅ {gcc_in_top10} GCC features in top 10! (Coastal model benefits from GCC)")
    
    # Save model
    joblib.dump(model, MODEL_DIR / 'salinity_classifier_rf_coastal.pkl')
    joblib.dump(label_encoder, MODEL_DIR / 'label_encoder_coastal.pkl')
    with open(MODEL_DIR / 'feature_columns_coastal.txt', 'w') as f:
        f.write('\n'.join(available_features))
    feature_importance.to_csv(MODEL_DIR / 'feature_importance_coastal.csv', index=False)
    
    print(f"\n✅ Coastal model saved")
    
    return model, label_encoder, available_features


def main():
    print("="*80)
    print("🤖 HYBRID ML MODEL TRAINING")
    print("="*80)
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n🔬 Training Strategy:")
    print(f"   1. Inland model (>{COASTAL_THRESHOLD_KM}km): DynQual-only (19 features)")
    print(f"   2. Coastal model (<{COASTAL_THRESHOLD_KM}km): DynQual + GCC (50+ features)")
    print(f"\n💡 This leverages GCC's coastal strength while avoiding sparse data issues!")
    
    # Load data
    global_data = load_training_data()
    
    # Check if GCC features exist
    gcc_features = [c for c in global_data.columns if c.startswith('gcc_')]
    
    if len(gcc_features) == 0:
        print(f"\n⚠️  WARNING: No GCC features found!")
        print(f"   Run GCC integration first:")
        print(f"   python scripts/ml_salinity/add_gcc_to_features.py --all-regions")
        print(f"\n   Training will proceed with DynQual-only for BOTH models.")
    else:
        print(f"\n✅ Found {len(gcc_features)} GCC features")
    
    # Train both models
    print_section("PHASE 1: INLAND MODEL")
    inland_model, inland_encoder, inland_features = train_inland_model(global_data)
    
    print_section("PHASE 2: COASTAL MODEL")
    coastal_model, coastal_encoder, coastal_features = train_coastal_model(global_data)
    
    # Summary
    print_section("✅ TRAINING COMPLETE")
    print(f"\n📁 Models saved to: {MODEL_DIR}")
    print(f"\n📊 Model Summary:")
    print(f"   Inland model: {len(inland_features)} features")
    print(f"   Coastal model: {len(coastal_features)} features")
    print(f"   Difference: +{len(coastal_features) - len(inland_features)} GCC features for coastal!")
    
    print(f"\n🎯 Next step:")
    print(f"   python scripts/ml_salinity/ml_step3_predict_hybrid.py --all-regions")


if __name__ == '__main__':
    main()
