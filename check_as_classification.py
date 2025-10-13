import geopandas as gpd
import pandas as pd

print("="*80)
print("CHECKING AS (ASIA) CLASSIFICATION RESULTS")
print("="*80)

# Load classified segments
gdf = gpd.read_file('data/processed/ml_classified/rivers_grit_ml_classified_as.gpkg')

print(f"\n📊 BASIC STATS:")
print(f"Total segments: {len(gdf):,}")

# Check columns
print(f"\n📋 COLUMNS ({len(gdf.columns)}):")
print(gdf.columns.tolist())

# Check classification distribution
print(f"\n🌊 SALINITY CLASS DISTRIBUTION:")
if 'salinity_class_final' in gdf.columns:
    print(gdf['salinity_class_final'].value_counts())
    print(f"\nPercentages:")
    print((gdf['salinity_class_final'].value_counts() / len(gdf) * 100).round(2))

# Check confidence levels
print(f"\n🎯 CONFIDENCE LEVELS:")
if 'confidence_level' in gdf.columns:
    print(gdf['confidence_level'].value_counts())
    print(f"\nPercentages:")
    print((gdf['confidence_level'].value_counts() / len(gdf) * 100).round(2))

# Check classification methods
print(f"\n📊 CLASSIFICATION METHOD:")
if 'classification_method' in gdf.columns:
    print(gdf['classification_method'].value_counts())
    
# Check distance distribution for estuarine segments
print(f"\n📏 ESTUARINE SEGMENTS BY DISTANCE FROM COAST:")
if 'salinity_class_final' in gdf.columns and 'dist_to_coast_km' in gdf.columns:
    estuarine = gdf[gdf['salinity_class_final'].isin(['Oligohaline', 'Mesohaline', 'Polyhaline'])]
    
    # Distance bins
    bins = [0, 20, 50, 100, 200, 500, 1000, 10000]
    labels = ['0-20km', '20-50km', '50-100km', '100-200km', '200-500km', '500-1000km', '>1000km']
    
    gdf['distance_bin'] = pd.cut(gdf['dist_to_coast_km'], bins=bins, labels=labels, include_lowest=True)
    
    for bin_label in labels:
        bin_data = gdf[gdf['distance_bin'] == bin_label]
        if len(bin_data) > 0:
            estuarine_count = bin_data[bin_data['salinity_class_final'].isin(['Oligohaline', 'Mesohaline', 'Polyhaline'])].shape[0]
            estuarine_pct = (estuarine_count / len(bin_data) * 100)
            print(f"   {bin_label:12s}: {estuarine_count:6,} / {len(bin_data):7,} ({estuarine_pct:5.1f}%)")

# Check GlobSalt coverage
print(f"\n🔬 GLOBSALT COVERAGE:")
if 'classification_method' in gdf.columns:
    globsalt = gdf[gdf['classification_method'] == 'GlobSalt_Validated']
    print(f"Total segments with GlobSalt: {len(globsalt):,} ({len(globsalt)/len(gdf)*100:.2f}%)")
    
    if len(globsalt) > 0:
        print(f"\nGlobSalt class distribution:")
        print(globsalt['salinity_class_final'].value_counts())

# Check suspicious patterns
print(f"\n⚠️  QUALITY CHECKS:")

# 1. Estuarine segments far from coast
if 'dist_to_coast_km' in gdf.columns:
    far_estuarine = gdf[
        (gdf['salinity_class_final'].isin(['Oligohaline', 'Mesohaline', 'Polyhaline'])) &
        (gdf['dist_to_coast_km'] > 100)
    ]
    print(f"1. Estuarine segments >100km from coast: {len(far_estuarine):,} ({len(far_estuarine)/len(gdf)*100:.2f}%)")
    
    very_far = gdf[
        (gdf['salinity_class_final'].isin(['Oligohaline', 'Mesohaline', 'Polyhaline'])) &
        (gdf['dist_to_coast_km'] > 500)
    ]
    print(f"   - Estuarine segments >500km from coast: {len(very_far):,} ({len(very_far)/len(gdf)*100:.2f}%)")

# 2. Confidence distribution for estuarine predictions
if 'confidence_level' in gdf.columns:
    estuarine_pred = gdf[
        (gdf['salinity_class_final'].isin(['Oligohaline', 'Mesohaline', 'Polyhaline'])) &
        (gdf['classification_method'] == 'ML_Predicted')
    ]
    print(f"\n2. ML-predicted estuarine segments: {len(estuarine_pred):,}")
    if len(estuarine_pred) > 0:
        print(f"   Confidence distribution:")
        print(estuarine_pred['confidence_level'].value_counts())

print(f"\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
