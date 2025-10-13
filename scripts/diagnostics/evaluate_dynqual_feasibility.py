
"""
DynQual Feasibility Test
========================

Test whether DynQual data should be integrated into ML pipeline.

Tests:
1. Correlation with existing features (independence)
2. Validation against GlobSalt measurements (accuracy)
3. Spatial resolution effects (10 km vs segment-level)

Usage:
    python scripts/evaluate_dynqual_feasibility.py --region SP
    python scripts/evaluate_dynqual_feasibility.py --all-regions
"""

import sys
import warnings
import argparse
from pathlib import Path
import pandas as pd
import geopandas as gpd
import numpy as np
import xarray as xr
from scipy.stats import spearmanr, pearsonr
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DYNQUAL_DIR = BASE_DIR / 'data' / 'raw' / 'DynQual-Jones_2023'
ML_DIR = BASE_DIR / 'data' / 'processed' / 'ml_features'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
EVAL_DIR = BASE_DIR / 'data' / 'processed' / 'dynqual_evaluation'
EVAL_DIR.mkdir(parents=True, exist_ok=True)

GRIT_REGIONS = ['AF', 'AS', 'EU', 'NA', 'SA', 'SI', 'SP']

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")


def extract_dynqual_at_centroids(segments: gpd.GeoDataFrame, 
                                  region_code: str) -> pd.DataFrame:
    """
    Extract DynQual values at GRIT segment centroids
    """
    print(f"\n📊 Extracting DynQual data for {region_code}...")
    
    # Check if DynQual files exist
    dynqual_files = {
        'salinity': DYNQUAL_DIR / 'salinity_annualAvg_1980_2019.nc',
        'discharge': DYNQUAL_DIR / 'discharge_annualAvg_1980_2019.nc',
        'temperature': DYNQUAL_DIR / 'waterTemperature_annualAvg_1980_2019.nc',
    }
    
    for name, path in dynqual_files.items():
        if not path.exists():
            print(f"   ⚠️  {name} file not found: {path.name}")
            return None
    
    # Load DynQual datasets
    print(f"   📂 Loading DynQual NetCDF files...")
    try:
        ds_sal = xr.open_dataset(dynqual_files['salinity'])
        ds_dis = xr.open_dataset(dynqual_files['discharge'])
        ds_temp = xr.open_dataset(dynqual_files['temperature'])
        print(f"   ✓ Loaded 3 DynQual datasets")
    except Exception as e:
        print(f"   ❌ Error loading DynQual: {e}")
        return None
    
    # Get variable names (they might differ)
    sal_var = list(ds_sal.data_vars)[0]
    dis_var = list(ds_dis.data_vars)[0]
    temp_var = list(ds_temp.data_vars)[0]
    
    print(f"   Variables: {sal_var}, {dis_var}, {temp_var}")
    
    # Extract centroids
    centroids_lon = segments.geometry.centroid.x.values
    centroids_lat = segments.geometry.centroid.y.values
    
    print(f"   Extracting values for {len(segments):,} segments...")
    
    # Extract using nearest neighbor (fast)
    dynqual_data = pd.DataFrame({
        'global_id': segments['global_id'].values,
    })
    
    try:
        # Extract salinity (TDS in mg/L)
        sal_values = []
        for lon, lat in zip(centroids_lon, centroids_lat):
            val = ds_sal[sal_var].sel(lon=lon, lat=lat, method='nearest').values
            sal_values.append(float(val))
        dynqual_data['dynqual_tds_mgL'] = sal_values
        
        # Extract discharge (m³/s)
        dis_values = []
        for lon, lat in zip(centroids_lon, centroids_lat):
            val = ds_dis[dis_var].sel(lon=lon, lat=lat, method='nearest').values
            dis_values.append(float(val))
        dynqual_data['dynqual_discharge_m3s'] = dis_values
        
        # Extract temperature (°C)
        temp_values = []
        for lon, lat in zip(centroids_lon, centroids_lat):
            val = ds_temp[temp_var].sel(lon=lon, lat=lat, method='nearest').values
            temp_values.append(float(val))
        dynqual_data['dynqual_temperature_C'] = temp_values
        
        print(f"   ✓ Extracted DynQual data")
        
    except Exception as e:
        print(f"   ❌ Extraction error: {e}")
        return None
    
    # Convert TDS (mg/L) to approximate salinity (PSU)
    # Rough conversion: TDS (mg/L) / 640 ≈ Salinity (PSU)
    dynqual_data['dynqual_salinity_psu'] = dynqual_data['dynqual_tds_mgL'] / 640
    
    # Summary statistics
    print(f"\n   📊 DynQual Summary:")
    print(f"      TDS range: {dynqual_data['dynqual_tds_mgL'].min():.1f} - {dynqual_data['dynqual_tds_mgL'].max():.1f} mg/L")
    print(f"      Salinity range: {dynqual_data['dynqual_salinity_psu'].min():.2f} - {dynqual_data['dynqual_salinity_psu'].max():.2f} PSU")
    print(f"      Discharge range: {dynqual_data['dynqual_discharge_m3s'].min():.1f} - {dynqual_data['dynqual_discharge_m3s'].max():.1f} m³/s")
    print(f"      Temperature range: {dynqual_data['dynqual_temperature_C'].min():.1f} - {dynqual_data['dynqual_temperature_C'].max():.1f} °C")
    
    return dynqual_data


def test_correlation_with_features(region_code: str):
    """
    TEST 1: Check correlation between DynQual and existing features
    """
    print_section(f"TEST 1: INDEPENDENCE CHECK ({region_code})")
    
    # Load existing features
    feature_file = ML_DIR / f'features_{region_code.lower()}.parquet'
    if not feature_file.exists():
        print(f"❌ Feature file not found: {feature_file}")
        print(f"   Run ml_step1_extract_features.py first!")
        return None
    
    features = pd.read_parquet(feature_file)
    print(f"✓ Loaded {len(features):,} features")
    
    # Load GRIT segments (for centroids)
    segments_file = PROCESSED_DIR / f'rivers_grit_segments_classified_{region_code.lower()}.gpkg'
    segments = gpd.read_file(segments_file)
    
    # Extract DynQual data
    dynqual = extract_dynqual_at_centroids(segments, region_code)
    if dynqual is None:
        return None
    
    # Merge with features
    data = features.merge(dynqual, on='global_id', how='left')
    
    # Calculate correlations
    print(f"\n📊 Correlation Analysis:")
    
    correlations = {}
    
    # DynQual salinity vs existing features
    if data['dynqual_salinity_psu'].notna().sum() > 100:
        corr_pairs = {
            'DynQual_salinity vs dist_to_coast': 
                ('dynqual_salinity_psu', 'dist_to_coast_km'),
            'DynQual_salinity vs in_durr_estuary': 
                ('dynqual_salinity_psu', 'in_durr_estuary'),
            'DynQual_salinity vs GlobSalt_salinity': 
                ('dynqual_salinity_psu', 'salinity_mean_psu'),
            'DynQual_discharge vs upstream_area': 
                ('dynqual_discharge_m3s', 'upstream_area'),
            'DynQual_discharge vs strahler_order': 
                ('dynqual_discharge_m3s', 'strahler_order'),
        }
        
        for name, (col1, col2) in corr_pairs.items():
            if col1 in data.columns and col2 in data.columns:
                valid = data[[col1, col2]].dropna()
                if len(valid) > 100:
                    r_spearman, p_spearman = spearmanr(valid[col1], valid[col2])
                    r_pearson, p_pearson = pearsonr(valid[col1], valid[col2])
                    correlations[name] = {
                        'spearman_r': r_spearman,
                        'spearman_p': p_spearman,
                        'pearson_r': r_pearson,
                        'pearson_p': p_pearson,
                        'n': len(valid)
                    }
                    
                    # Interpretation
                    if abs(r_spearman) > 0.9:
                        flag = "❌ REDUNDANT"
                    elif abs(r_spearman) > 0.7:
                        flag = "⚠️  HIGH OVERLAP"
                    elif abs(r_spearman) > 0.5:
                        flag = "⚠️  MODERATE"
                    else:
                        flag = "✅ INDEPENDENT"
                    
                    print(f"\n   {name}:")
                    print(f"      Spearman r = {r_spearman:.3f} (p = {p_spearman:.4f}) {flag}")
                    print(f"      Pearson r = {r_pearson:.3f} (n = {len(valid):,})")
    
    # Save correlation report
    corr_df = pd.DataFrame(correlations).T
    report_file = EVAL_DIR / f'correlation_report_{region_code.lower()}.csv'
    corr_df.to_csv(report_file)
    print(f"\n💾 Correlation report saved: {report_file}")
    
    return corr_df


def test_validation_vs_globsalt(region_code: str):
    """
    TEST 2: Validate DynQual salinity against GlobSalt measurements
    """
    print_section(f"TEST 2: GLOBSALT VALIDATION ({region_code})")
    
    # Load classified segments (has GlobSalt data)
    segments_file = PROCESSED_DIR / f'rivers_grit_segments_classified_{region_code.lower()}.gpkg'
    segments = gpd.read_file(segments_file)
    
    # Filter for segments WITH GlobSalt data
    has_globsalt = segments['salinity_mean_psu'].notna()
    validated = segments[has_globsalt].copy()
    
    if len(validated) == 0:
        print(f"❌ No GlobSalt data in {region_code}")
        return None
    
    print(f"✓ {len(validated):,} segments with GlobSalt measurements")
    
    # Extract DynQual for these segments
    dynqual = extract_dynqual_at_centroids(validated, region_code)
    if dynqual is None:
        return None
    
    # Merge
    comparison = validated[['global_id', 'salinity_mean_psu']].merge(
        dynqual[['global_id', 'dynqual_salinity_psu']], 
        on='global_id', 
        how='left'
    )
    
    # Remove NaN
    comparison = comparison.dropna()
    
    if len(comparison) < 50:
        print(f"⚠️  Only {len(comparison)} valid comparisons, results may be unreliable")
    
    # Calculate metrics
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
    
    globsalt = comparison['salinity_mean_psu'].values
    dynqual_sal = comparison['dynqual_salinity_psu'].values
    
    r2 = r2_score(globsalt, dynqual_sal)
    mae = mean_absolute_error(globsalt, dynqual_sal)
    rmse = np.sqrt(mean_squared_error(globsalt, dynqual_sal))
    r_pearson, p_pearson = pearsonr(globsalt, dynqual_sal)
    
    print(f"\n📊 DynQual vs GlobSalt Performance:")
    print(f"   R² = {r2:.3f}")
    print(f"   MAE = {mae:.2f} PSU")
    print(f"   RMSE = {rmse:.2f} PSU")
    print(f"   Pearson r = {r_pearson:.3f} (p = {p_pearson:.4f})")
    print(f"   n = {len(comparison):,} segments")
    
    # Interpretation
    print(f"\n💡 Interpretation:")
    if r2 > 0.7:
        print(f"   ✅ EXCELLENT: DynQual captures real salinity patterns")
    elif r2 > 0.5:
        print(f"   ✓ GOOD: DynQual shows reasonable agreement")
    elif r2 > 0.3:
        print(f"   ⚠️  MODERATE: DynQual has weak predictive power")
    else:
        print(f"   ❌ POOR: DynQual does not match field measurements")
    
    # Save scatter plot
    try:
        plt.figure(figsize=(8, 8))
        plt.scatter(globsalt, dynqual_sal, alpha=0.5, s=10)
        plt.plot([0, 30], [0, 30], 'r--', label='1:1 line')
        plt.xlabel('GlobSalt Measured Salinity (PSU)')
        plt.ylabel('DynQual Model Salinity (PSU)')
        plt.title(f'DynQual vs GlobSalt Validation ({region_code})\nR² = {r2:.3f}, n = {len(comparison):,}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plot_file = EVAL_DIR / f'dynqual_validation_{region_code.lower()}.png'
        plt.savefig(plot_file, dpi=150)
        print(f"\n📊 Validation plot saved: {plot_file}")
    except:
        print(f"⚠️  Could not save plot")
    
    # Save comparison data
    comparison_file = EVAL_DIR / f'dynqual_globsalt_comparison_{region_code.lower()}.csv'
    comparison.to_csv(comparison_file, index=False)
    print(f"💾 Comparison data saved: {comparison_file}")
    
    return {
        'r2': r2,
        'mae': mae,
        'rmse': rmse,
        'pearson_r': r_pearson,
        'n': len(comparison)
    }


def main():
    parser = argparse.ArgumentParser(description='Evaluate DynQual feasibility for ML pipeline')
    parser.add_argument('--region', type=str, choices=GRIT_REGIONS,
                        help='Test single region')
    parser.add_argument('--all-regions', action='store_true',
                        help='Test all regions')
    args = parser.parse_args()
    
    print_section("🔬 DYNQUAL FEASIBILITY EVALUATION")
    print(f"Testing whether DynQual should be integrated into ML pipeline")
    
    # Determine regions
    if args.all_regions:
        regions = GRIT_REGIONS
    elif args.region:
        regions = [args.region]
    else:
        print("❌ Must specify --region or --all-regions")
        return 1
    
    print(f"\n📋 Regions to test: {', '.join(regions)}")
    
    # Run tests
    all_correlations = []
    all_validations = []
    
    for region_code in regions:
        # Test 1: Correlation
        corr_results = test_correlation_with_features(region_code)
        if corr_results is not None:
            corr_results['region'] = region_code
            all_correlations.append(corr_results)
        
        # Test 2: Validation
        val_results = test_validation_vs_globsalt(region_code)
        if val_results is not None:
            val_results['region'] = region_code
            all_validations.append(val_results)
    
    # Generate summary report
    print_section("📊 FINAL RECOMMENDATION")
    
    if len(all_correlations) > 0:
        print(f"\n✅ Correlation Analysis Complete ({len(all_correlations)} regions)")
        print(f"   See: {EVAL_DIR}/correlation_report_*.csv")
    
    if len(all_validations) > 0:
        print(f"\n✅ Validation Analysis Complete ({len(all_validations)} regions)")
        val_df = pd.DataFrame(all_validations)
        mean_r2 = val_df['r2'].mean()
        mean_mae = val_df['mae'].mean()
        
        print(f"\n   Global averages:")
        print(f"   Mean R² = {mean_r2:.3f}")
        print(f"   Mean MAE = {mean_mae:.2f} PSU")
        
        # Overall recommendation
        print(f"\n💡 RECOMMENDATION:")
        if mean_r2 > 0.6:
            print(f"   ✅ PROCEED: DynQual shows good agreement with field data")
            print(f"   Next step: Run Phase 3 ML ablation study")
        elif mean_r2 > 0.4:
            print(f"   ⚠️  CAUTION: DynQual shows moderate agreement")
            print(f"   Consider using DISCHARGE only (not salinity)")
        else:
            print(f"   ❌ DON'T USE: DynQual does not match field measurements")
            print(f"   Not recommended for ML pipeline")
    
    print(f"\n📁 All results saved to: {EVAL_DIR}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
