"""
FIX: Re-integrate GCC Features with Consistent Categories
==========================================================

Problem: Different regions have different categorical dummy variables
Solution: Re-run GCC integration with fixed categories

This ensures ALL regions get the SAME feature columns!
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = BASE_DIR / 'scripts'

print("="*80)
print("FIXING GCC FEATURE CONSISTENCY")
print("="*80)

print("\n🔧 Problem:")
print("   - Different regions have different GCC categorical columns")
print("   - Example: EU missing 'gcc_veg_type_Salt-marshes'")
print("   - Causes KeyError when predicting")

print("\n✅ Solution:")
print("   - Re-run GCC integration with FIXED categories")
print("   - All regions will get SAME columns (missing categories = 0)")

print("\n📊 Regions to process:")
REGIONS = ['AF', 'AS', 'EU', 'NA', 'SA', 'SI', 'SP']
for region in REGIONS:
    print(f"   - {region}")

print("\n⏰ Expected time: ~1 minute total")

input("\nPress Enter to continue (or Ctrl+C to cancel)...")

# Run GCC integration for all regions
cmd = [sys.executable, str(SCRIPTS_DIR / 'ml_salinity' / 'add_gcc_to_features.py'), '--all-regions']

print(f"\n▶️  Running: python scripts/ml_salinity/add_gcc_to_features.py --all-regions")
print("="*80)

result = subprocess.run(cmd)

print("\n" + "="*80)
if result.returncode == 0:
    print("✅ GCC INTEGRATION COMPLETE!")
    print("\n📊 Now ALL regions have consistent features:")
    print("   - gcc_coast_type_flag_Other")
    print("   - gcc_coast_type_flag_Rocky")
    print("   - gcc_coast_type_flag_Sandy")
    print("   - gcc_coast_type_flag_Vegetated")
    print("   - gcc_veg_type_Mangroves")
    print("   - gcc_veg_type_Salt-marshes  ← NOW PRESENT IN ALL REGIONS!")
    
    print("\n🎯 Next step:")
    print("   python scripts/ml_salinity/ml_step3_predict.py --all-regions")
else:
    print("❌ GCC INTEGRATION FAILED!")
    print(f"   Exit code: {result.returncode}")
    sys.exit(1)
