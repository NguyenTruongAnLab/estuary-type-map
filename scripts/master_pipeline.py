
"""
MASTER PIPELINE: Complete Project Aquarius Processing
======================================================

Orchestrates the entire global water body atlas creation pipeline from
raw data to web-ready outputs.

This is the ONE script to run the complete analysis.

Pipeline Stages:
1. Data Preprocessing: GRIT, GlobSalt, Dürr, Baum (60-90 min)
2. Machine Learning: Feature extraction, training, prediction (2-3 hours)
3. Web Optimization: Generate GeoJSON for interactive atlas (30 min)

Total Duration: 3-4.5 hours (run overnight recommended)

Usage:
    # Complete pipeline (recommended)
    python scripts/master_pipeline.py --all
    
    # Individual stages
    python scripts/master_pipeline.py --stage preprocessing
    python scripts/master_pipeline.py --stage ml
    python scripts/master_pipeline.py --stage web
    
    # Skip specific steps
    python scripts/master_pipeline.py --all --skip-grit --skip-ml
"""

import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
import argparse

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / 'scripts'

# Script folder organization
RAW_DATA_DIR = SCRIPTS_DIR / 'raw_data_processing'
ML_DIR = SCRIPTS_DIR / 'ml_salinity'
WEB_DIR = SCRIPTS_DIR / 'web_optimization'

def print_header():
    """Print pipeline header"""
    print("\n" + "="*80)
    print("="*80)
    print("  🌊 PROJECT AQUARIUS - MASTER PIPELINE")
    print("  Global Water Body Surface Area Atlas")
    print("="*80)
    print("="*80)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Expected duration: 3-4.5 hours (all stages)")
    print(f"\nProject: Direct polygon-based measurement of global aquatic systems")
    print(f"Objective: Enable precise biogeochemical modeling (GHG, carbon, nutrients)\n")


def print_section(title: str, stage: int, total: int):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"{'='*80}")
    print(f"  STAGE {stage}/{total}: {title}")
    print(f"{'='*80}")
    print(f"{'='*80}\n")


def run_script(script_name: str, args: list, description: str) -> int:
    """Run a Python script with arguments"""
    print(f"\n▶️  {description}")
    print(f"   Command: python {script_name} {' '.join(args)}")
    
    cmd = [sys.executable, str(SCRIPTS_DIR / script_name)] + args
    start_time = time.time()
    
    result = subprocess.run(cmd)
    
    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    
    if result.returncode == 0:
        print(f"   ✅ Completed in {minutes}m {seconds}s")
    else:
        print(f"   ❌ Failed with exit code {result.returncode}")
    
    return result.returncode


def check_file_exists(filepath: Path) -> bool:
    """Check if file exists"""
    return filepath.exists()


def stage_preprocessing(args):
    """
    STAGE 1: Data Preprocessing (60-90 minutes)
    
    Converts raw datasets to standardized GPKG format:
    - GRIT v0.6: 20.5M river reaches (7 regions)
    - GlobSalt: 270K salinity stations
    - Dürr 2011: 7,057 estuary catchments
    - Baum 2024: Large estuary morphometry
    """
    print_section("DATA PREPROCESSING", 1, 3)
    
    failed = []
    
    # 1.1: Process GRIT (all 7 regions)
    if not args.skip_grit:
        print("\n📍 1.1: Processing GRIT River Network (7 regions)")
        print("    Duration: 40-60 minutes")
        print("    Output: rivers_grit_segments_classified_*.gpkg (7 files)")
        
        ret = run_script(
            'raw_data_processing/process_grit_all_regions.py',
            [],
            'Process GRIT v0.6 for all regions (AF, AS, EU, NA, SA, SI, SP)'
        )
        if ret != 0:
            failed.append('GRIT processing')
    else:
        print("\n⏭️  Skipping GRIT processing (--skip-grit)")
    
    # 1.2: Process Dürr estuary database
    if not args.skip_durr:
        print("\n📍 1.2: Processing Dürr 2011 Estuary Database")
        print("    Duration: 5-10 minutes")
        print("    Output: durr_estuaries.geojson + metadata")
        
        ret = run_script(
            'raw_data_processing/process_durr.py',
            [],
            'Process Dürr 2011 estuary typology (7,057 catchments)'
        )
        if ret != 0:
            failed.append('Dürr processing')
    else:
        print("\n⏭️  Skipping Dürr processing (--skip-durr)")
    
    # 1.3: Process Baum morphometry
    if not args.skip_baum:
        print("\n📍 1.3: Processing Baum 2024 Morphometry")
        print("    Duration: 5-10 minutes")
        print("    Output: baum_morphometry.geojson + metadata")
        
        ret = run_script(
            'raw_data_processing/process_baum.py',
            [],
            'Process Baum 2024 large estuary morphometry'
        )
        if ret != 0:
            failed.append('Baum processing')
    else:
        print("\n⏭️  Skipping Baum processing (--skip-baum)")
    
    # Summary
    print(f"\n{'='*80}")
    print("STAGE 1 SUMMARY")
    print(f"{'='*80}")
    if failed:
        print(f"❌ Failed steps: {', '.join(failed)}")
        return False
    else:
        print("✅ All preprocessing steps completed successfully!")
        print("\n📊 Generated Files:")
        print("   - data/processed/rivers_grit_segments_classified_*.gpkg (7 regions)")
        print("   - data/processed/durr_estuaries.geojson")
        print("   - data/processed/baum_morphometry.geojson")
        return True


def stage_ml(args):
    """
    STAGE 2: Machine Learning Pipeline (2-3 hours)
    
    ML-based salinity prediction for segments without GlobSalt:
    - Extract features (GRIT topology + Dürr + DynQual)
    - Train Random Forest (spatial holdout validation)
    - Predict for all segments
    - Multi-method validation
    """
    print_section("MACHINE LEARNING CLASSIFICATION", 2, 3)
    
    print("\n🤖 Running complete ML pipeline with DynQual integration")
    print("    This uses ml_dynqual_master_pipeline.py orchestrator")
    print("    Duration: 2-3 hours")
    print("    Steps: Feature extraction → Training → Prediction → Validation")
    
    ml_args = ['--all-regions']
    
    if args.skip_baseline:
        ml_args.append('--skip-baseline')
    if args.skip_dynqual:
        ml_args.append('--skip-dynqual')
    if args.skip_training:
        ml_args.append('--skip-training')
    if args.skip_prediction:
        ml_args.append('--skip-prediction')
    if args.skip_validation:
        ml_args.append('--skip-validation')
    
    ret = run_script(
        'ml_salinity/ml_dynqual_master_pipeline.py',
        ml_args,
        'Complete ML pipeline (5 steps)'
    )
    
    if ret != 0:
        print("\n❌ ML pipeline failed!")
        return False
    else:
        print("\n✅ ML pipeline completed successfully!")
        print("\n📊 Generated Files:")
        print("   - data/processed/ml_features/features_*.parquet (7 regions)")
        print("   - data/processed/ml_models/salinity_classifier_rf.pkl")
        print("   - data/processed/ml_classified/rivers_grit_ml_classified_*.gpkg")
        print("   - data/processed/validation_improved/*.csv (validation results)")
        return True


def stage_web(args):
    """
    STAGE 3: Web Optimization (30 minutes)
    
    Generate web-ready GeoJSON files (<5MB each):
    - Simplify geometries for fast loading
    - Create zoom-level optimized versions
    - Generate summary statistics
    """
    print_section("WEB OPTIMIZATION", 3, 3)
    
    failed = []
    
    # 3.1: Optimize data
    print("\n📍 3.1: Optimizing for Web Display")
    print("    Duration: 20-30 minutes")
    print("    Output: data/web/*.geojson (<5MB each)")
    
    ret = run_script(
        'web_optimization/optimize_data_final.py',
        [],
        'Generate web-ready GeoJSON with geometry simplification'
    )
    if ret != 0:
        failed.append('Data optimization')
    
    # 3.2: Convert formats
    print("\n📍 3.2: Converting GPKG to GeoJSON")
    print("    Duration: 5-10 minutes")
    
    ret = run_script(
        'web_optimization/convert_gpkg_to_geojson.py',
        [],
        'Convert all GPKG files to GeoJSON format'
    )
    if ret != 0:
        failed.append('Format conversion')
    
    # Summary
    print(f"\n{'='*80}")
    print("STAGE 3 SUMMARY")
    print(f"{'='*80}")
    if failed:
        print(f"❌ Failed steps: {', '.join(failed)}")
        return False
    else:
        print("✅ All web optimization steps completed successfully!")
        print("\n📊 Generated Files:")
        print("   - data/web/*.geojson (web-ready, <5MB each)")
        print("\n🌐 Ready for deployment to GitHub Pages!")
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Master pipeline for Project Aquarius',
        epilog='Example: python scripts/master_pipeline.py --all'
    )
    
    # Main options
    parser.add_argument('--all', action='store_true',
                        help='Run complete pipeline (all 3 stages)')
    parser.add_argument('--stage', type=str, choices=['preprocessing', 'ml', 'web'],
                        help='Run specific stage only')
    
    # Skip options for Stage 1
    parser.add_argument('--skip-grit', action='store_true',
                        help='Skip GRIT processing (Stage 1)')
    parser.add_argument('--skip-durr', action='store_true',
                        help='Skip Dürr processing (Stage 1)')
    parser.add_argument('--skip-baum', action='store_true',
                        help='Skip Baum processing (Stage 1)')
    
    # Skip options for Stage 2 (passed to ml_dynqual_master_pipeline.py)
    parser.add_argument('--skip-baseline', action='store_true',
                        help='Skip baseline feature extraction (Stage 2)')
    parser.add_argument('--skip-dynqual', action='store_true',
                        help='Skip DynQual feature addition (Stage 2)')
    parser.add_argument('--skip-training', action='store_true',
                        help='Skip model training (Stage 2)')
    parser.add_argument('--skip-prediction', action='store_true',
                        help='Skip prediction (Stage 2)')
    parser.add_argument('--skip-validation', action='store_true',
                        help='Skip validation (Stage 2)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.all and not args.stage:
        parser.error("Must specify --all or --stage")
    
    print_header()
    
    start_time = time.time()
    all_success = True
    
    # Run stages
    if args.all:
        # Run all 3 stages
        success_1 = stage_preprocessing(args)
        success_2 = stage_ml(args) if success_1 else False
        success_3 = stage_web(args) if success_2 else False
        all_success = success_1 and success_2 and success_3
    else:
        # Run specific stage
        if args.stage == 'preprocessing':
            all_success = stage_preprocessing(args)
        elif args.stage == 'ml':
            all_success = stage_ml(args)
        elif args.stage == 'web':
            all_success = stage_web(args)
    
    # Final summary
    elapsed = time.time() - start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    
    print(f"\n{'='*80}")
    print(f"{'='*80}")
    print(f"  MASTER PIPELINE {'COMPLETED' if all_success else 'FAILED'}")
    print(f"{'='*80}")
    print(f"{'='*80}")
    print(f"\nTotal time: {hours}h {minutes}m")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if all_success:
        print("✅ SUCCESS! All stages completed successfully!")
        print("\n📊 Next Steps:")
        print("   1. Review validation results: data/processed/validation_improved/")
        print("   2. Check web files: data/web/")
        print("   3. Deploy to GitHub Pages")
        print("   4. Update README.md with latest statistics")
    else:
        print("❌ PIPELINE FAILED! Check error messages above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
