
"""
STEP 2: Train ML Model on GlobSalt Data
========================================

Train Random Forest classifier on global GlobSalt-validated segments
to predict salinity class for unvalidated segments.

Usage:
    python scripts/ml_step2_train_model.py
"""

import sys
import warnings
import time
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ML_DIR = BASE_DIR / 'data' / 'processed' / 'ml_features'
MODEL_DIR = BASE_DIR / 'data' / 'processed' / 'ml_models'
MODEL_DIR.mkdir(parents=True, exist_ok=True)

GRIT_REGIONS = ['AF', 'AS', 'EU', 'NA', 'SA', 'SI', 'SP']

# Spatial holdout strategy: hold out one region for validation
# This prevents data leakage - the holdout region is NEVER seen during training!
HOLDOUT_REGION = 'SP'  # South Pacific held out completely
TRAIN_REGIONS = [r for r in GRIT_REGIONS if r != HOLDOUT_REGION]

print(f"\n🔒 SPATIAL HOLDOUT CONFIGURATION:")
print(f"   Training regions: {TRAIN_REGIONS}")
print(f"   Holdout region: {HOLDOUT_REGION} (NEVER used in training!)")
print(f"   This ensures TRUE independent validation\n")

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")


def load_global_training_data():
    """
    Load features from TRAINING regions only (excludes spatial holdout)
    Only include segments with GlobSalt salinity measurements
    
    CRITICAL: Uses TRAIN_REGIONS (not GRIT_REGIONS) to prevent data leakage!
    """
    print_section("📊 LOADING GLOBAL TRAINING DATA")
    
    print(f"\n🔒 SPATIAL HOLDOUT STRATEGY:")
    print(f"   Training on: {TRAIN_REGIONS}")
    print(f"   Held out: {HOLDOUT_REGION} (for independent validation)")
    print(f"   This prevents data leakage!\n")
    
    all_features = []
    
    for region_code in TRAIN_REGIONS:  # CRITICAL FIX: was GRIT_REGIONS
        feature_file = ML_DIR / f'features_{region_code.lower()}.parquet'
        
        if not feature_file.exists():
            print(f"⚠️  {region_code}: Feature file not found, skipping")
            continue
        
        features = pd.read_parquet(feature_file)
        
        # Filter for segments WITH salinity data (training set)
        with_salinity = features[features['has_salinity'] == 1].copy()
        
        if len(with_salinity) > 0:
            with_salinity['region'] = region_code
            all_features.append(with_salinity)
            print(f"✓ {region_code}: {len(with_salinity):,} segments with salinity")
        else:
            print(f"⚠️  {region_code}: 0 segments with salinity")
    
    if len(all_features) == 0:
        print(f"\n❌ No training data found!")
        print(f"   Make sure to run ml_step1_extract_features.py first")
        return None
    
    # Concatenate all regions
    global_data = pd.concat(all_features, ignore_index=True)
    
    print(f"\n📊 Global Training Data Summary:")
    print(f"   Total segments: {len(global_data):,}")
    print(f"   Regions: {global_data['region'].nunique()}")
    print(f"   Regional breakdown:")
    for region, count in global_data['region'].value_counts().items():
        print(f"      {region}: {count:,} ({count/len(global_data)*100:.1f}%)")
    
    return global_data


def classify_salinity(salinity_psu):
    """
    Classify salinity using Venice System thresholds
    """
    if pd.isna(salinity_psu):
        return 'Unknown'
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


def prepare_training_data(global_data):
    """
    Prepare X (features) and y (target) for ML training
    """
    print_section("🔧 PREPARING TRAINING DATA")
    
    # Create target variable (salinity class)
    global_data['salinity_class'] = global_data['salinity_mean_psu'].apply(classify_salinity)
    
    # Remove 'Unknown' (should be none)
    global_data = global_data[global_data['salinity_class'] != 'Unknown']
    
    print(f"\n📊 Target Distribution (Venice System):")
    class_counts = global_data['salinity_class'].value_counts()
    for cls, count in class_counts.items():
        print(f"   {cls:15s}: {count:>7,} ({count/len(global_data)*100:>5.1f}%)")
    
    # Check for class imbalance
    minority_class_pct = class_counts.min() / class_counts.max() * 100
    if minority_class_pct < 5:
        print(f"\n⚠️  WARNING: Severe class imbalance detected!")
        print(f"   Minority class: {minority_class_pct:.1f}% of majority")
        print(f"   Using balanced class weights in Random Forest")
    
    # Feature columns (exclude metadata)
    exclude_cols = ['global_id', 'salinity_mean_psu', 'has_salinity', 
                    'salinity_class', 'region', 'latitude', 'longitude']
    
    feature_cols = [col for col in global_data.columns if col not in exclude_cols]
    
    print(f"\n📊 Feature Set:")
    print(f"   Total features: {len(feature_cols)}")
    print(f"   Features: {feature_cols}")
    
    # Prepare X and y
    X = global_data[feature_cols].copy()
    y = global_data['salinity_class'].copy()
    
    # Handle missing values (fill with median)
    for col in X.columns:
        if X[col].isna().any():
            median_val = X[col].median()
            X[col].fillna(median_val, inplace=True)
            print(f"   ✓ Filled {X[col].isna().sum()} NaN in {col} with median {median_val:.2f}")
    
    # Encode target labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    print(f"\n✓ Training data prepared:")
    print(f"   X shape: {X.shape}")
    print(f"   y classes: {le.classes_}")
    
    return X, y_encoded, le, feature_cols


def train_random_forest(X, y, label_encoder):
    """
    Train Random Forest classifier with hyperparameter tuning
    """
    print_section("🌲 TRAINING RANDOM FOREST MODEL")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n📊 Train/Test Split:")
    print(f"   Training set: {len(X_train):,} samples")
    print(f"   Test set: {len(X_test):,} samples")
    
    # Initial model (baseline)
    print(f"\n🌲 Training baseline model...")
    rf_baseline = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=50,
        min_samples_leaf=20,
        class_weight='balanced',  # Handle imbalanced classes
        random_state=42,
        n_jobs=-1,
        verbose=0
    )
    
    rf_baseline.fit(X_train, y_train)
    baseline_score = rf_baseline.score(X_test, y_test)
    
    print(f"✓ Baseline test accuracy: {baseline_score:.3f}")
    
    # Hyperparameter tuning (if time allows)
    print(f"\n🔧 Hyperparameter tuning (this may take 10-20 minutes)...")
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [10, 15, 20],
        'min_samples_split': [30, 50],
        'min_samples_leaf': [10, 20]
    }
    
    grid_search = GridSearchCV(
        RandomForestClassifier(class_weight='balanced', random_state=42, n_jobs=-1),
        param_grid,
        cv=3,  # 3-fold cross-validation
        scoring='accuracy',
        verbose=1,
        n_jobs=1  # GridSearch parallelizes internally
    )
    
    try:
        grid_search.fit(X_train, y_train)
        best_model = grid_search.best_estimator_
        best_score = grid_search.best_score_
        
        print(f"\n✓ Best parameters: {grid_search.best_params_}")
        print(f"✓ Best CV score: {best_score:.3f}")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Hyperparameter tuning interrupted, using baseline model")
        best_model = rf_baseline
        best_score = baseline_score
    
    # Final evaluation
    print_section("📊 MODEL EVALUATION")
    
    y_pred = best_model.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n🎯 Test Set Performance:")
    print(f"   Accuracy: {test_accuracy:.3f}")
    
    # Classification report
    print(f"\n📊 Detailed Classification Report:")
    class_names = label_encoder.classes_
    print(classification_report(y_test, y_pred, 
                                 target_names=class_names,
                                 digits=3))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\n📊 Confusion Matrix:")
    cm_df = pd.DataFrame(cm, index=class_names, columns=class_names)
    print(cm_df)
    
    # Feature importance
    print(f"\n📊 Top 10 Most Important Features:")
    feature_imp = pd.DataFrame({
        'feature': X.columns,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(feature_imp.head(10).to_string(index=False))
    
    # Save feature importance plot
    try:
        plt.figure(figsize=(10, 6))
        feature_imp.head(15).plot(x='feature', y='importance', kind='barh')
        plt.xlabel('Feature Importance')
        plt.title('Random Forest Feature Importance (Top 15)')
        plt.tight_layout()
        plt.savefig(MODEL_DIR / 'feature_importance.png', dpi=150)
        print(f"\n✓ Feature importance plot saved: feature_importance.png")
    except:
        print(f"\n⚠️  Could not save feature importance plot")
    
    # Cross-validation
    print(f"\n🔄 5-Fold Cross-Validation:")
    cv_scores = cross_val_score(best_model, X, y, cv=5, scoring='accuracy', n_jobs=-1)
    print(f"   Scores: {cv_scores}")
    print(f"   Mean: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    
    return best_model, feature_imp


def save_model(model, label_encoder, feature_cols, feature_importance):
    """
    Save trained model and metadata
    """
    print_section("💾 SAVING MODEL")
    
    # Save model
    model_file = MODEL_DIR / 'salinity_classifier_rf.pkl'
    joblib.dump(model, model_file)
    print(f"✓ Model saved: {model_file}")
    
    # Save label encoder
    encoder_file = MODEL_DIR / 'label_encoder.pkl'
    joblib.dump(label_encoder, encoder_file)
    print(f"✓ Label encoder saved: {encoder_file}")
    
    # Save feature list
    feature_file = MODEL_DIR / 'feature_columns.txt'
    with open(feature_file, 'w') as f:
        for feat in feature_cols:
            f.write(f"{feat}\n")
    print(f"✓ Feature columns saved: {feature_file}")
    
    # Save feature importance
    importance_file = MODEL_DIR / 'feature_importance.csv'
    feature_importance.to_csv(importance_file, index=False)
    print(f"✓ Feature importance saved: {importance_file}")
    
    # Save metadata
    metadata = {
        'model_type': 'RandomForestClassifier',
        'n_features': len(feature_cols),
        'classes': label_encoder.classes_.tolist(),
        'trained_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'sklearn_version': '1.3+',
    }
    
    metadata_file = MODEL_DIR / 'model_metadata.txt'
    with open(metadata_file, 'w') as f:
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")
    print(f"✓ Metadata saved: {metadata_file}")
    
    # Save holdout region info for validation
    holdout_file = MODEL_DIR / 'holdout_region.txt'
    with open(holdout_file, 'w') as f:
        f.write(HOLDOUT_REGION)
    print(f"✓ Holdout region saved: {holdout_file}")
    print(f"   Only {HOLDOUT_REGION} provides TRUE independent validation!")


def main():
    print_section("🤖 ML MODEL TRAINING PIPELINE")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load data
    global_data = load_global_training_data()
    if global_data is None:
        return 1
    
    # Prepare training data
    X, y, label_encoder, feature_cols = prepare_training_data(global_data)
    
    # Train model
    model, feature_importance = train_random_forest(X, y, label_encoder)
    
    # Save model
    save_model(model, label_encoder, feature_cols, feature_importance)
    
    print_section("✅ MODEL TRAINING COMPLETE")
    print(f"\n📁 Model files saved to: {MODEL_DIR}")
    print(f"\nNext step: python scripts/ml_step3_predict.py --region SP")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

