
"""Check which feature files exist and if they have DynQual"""
import pandas as pd
from pathlib import Path

ml_dir = Path('data/processed/ml_features')
files = sorted(ml_dir.glob('features_*.parquet'))

print("=" * 80)
print("📁 FEATURE FILES CHECK")
print("=" * 80)

for f in files:
    df = pd.read_parquet(f)
    has_dynqual = 'dynqual_salinity_psu' in df.columns
    region = f.stem.split('_')[-1].upper()
    
    status = "✅ HAS DynQual" if has_dynqual else "❌ NO DynQual (OLD)"
    
    print(f"\n{region:2s}: {f.name:30s}")
    print(f"    Rows: {len(df):>7,} | Columns: {len(df.columns):>2} | {status}")

print("\n" + "=" * 80)
print("RECOMMENDATION:")
print("=" * 80)

all_have_dynqual = all('dynqual_salinity_psu' in pd.read_parquet(f).columns for f in files)
all_regions = len(files) == 7

if all_have_dynqual and all_regions:
    print("✅ All 7 regions with DynQual - Ready for production!")
elif all_have_dynqual:
    print(f"⚠️  Only {len(files)}/7 regions extracted (but all have DynQual)")
    print("   → Run: python scripts/ml_dynqual_master_pipeline.py --all-regions")
else:
    print("❌ Some regions missing DynQual features (created before integration)")
    print("   → MUST re-run: python scripts/ml_dynqual_master_pipeline.py --all-regions")
    print("   → This will recreate ALL features with DynQual included")
