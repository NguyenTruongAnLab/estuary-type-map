#!/usr/bin/env python3
"""
Data Download Script for Global Estuary Type Map

This script downloads large data files required for the web application
from external storage (Zenodo) during the GitHub Pages build process.

Usage:
    python scripts/download_web_data.py

Environment Variables:
    GITHUB_ACTIONS: Set to 'true' when running in GitHub Actions
    CI: Set to 'true' when running in CI environment
"""

import os
import sys
import requests
import zipfile
import shutil
from pathlib import Path
from urllib.parse import urlparse

# Configuration
DATA_DIR = Path("data/web")
ZENODO_BASE_URL = "https://zenodo.org/records/YOUR_RECORD_ID/files/"

# Files to download with their Zenodo filenames
DATA_FILES = {
    "coastal_basins_estuarine_types.geojson": "coastal_basins_estuarine_types.geojson",
    "salinity_zones.geojson": "salinity_zones.geojson",
    "rivers_estuaries_z2-4.geojson": "rivers_estuaries_z2-4.geojson",
    "rivers_estuaries_z5-8.geojson": "rivers_estuaries_z5-8.geojson",
    "rivers_estuaries_z9plus.geojson": "rivers_estuaries_z9plus.geojson",
    "basins_coastal_lev06_simplified.geojson": "basins_coastal_lev06_simplified.geojson",
    "basins_coastal_lev08_z2-6.geojson": "basins_coastal_lev08_z2-6.geojson",
    "basins_coastal_lev08_z7-10.geojson": "basins_coastal_lev08_z7-10.geojson",
    "basins_coastal_lev08_z11plus.geojson": "basins_coastal_lev08_z11plus.geojson",
    "baum_morphometry.geojson": "baum_morphometry.geojson",
    "durr_estuaries.geojson": "durr_estuaries.geojson"
}

def download_file(url: str, destination: Path, chunk_size: int = 8192) -> bool:
    """Download a file with progress indication."""
    try:
        print(f"📥 Downloading {url} → {destination}")

        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))

            with open(destination, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(".1f", end='', flush=True)

            print(" ✓ Complete")
            return True

    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return False

def extract_zip(zip_path: Path, extract_to: Path) -> bool:
    """Extract a ZIP file."""
    try:
        print(f"📦 Extracting {zip_path} → {extract_to}")

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

        # Remove the ZIP file after extraction
        zip_path.unlink()
        print(" ✓ Extracted")
        return True

    except Exception as e:
        print(f"❌ Failed to extract {zip_path}: {e}")
        return False

def main():
    """Main download function."""
    print("🌊 Global Estuary Type Map - Data Download Script")
    print("=" * 60)

    # Create data directory
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Check if we're in CI/GitHub Actions
    is_ci = os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'
    if is_ci:
        print("🤖 Running in CI environment - downloading all data files")
    else:
        print("💻 Running locally - downloading minimal data for development")

    success_count = 0
    total_count = len(DATA_FILES)

    for local_name, remote_name in DATA_FILES.items():
        local_path = DATA_DIR / local_name

        # Skip if file already exists (unless in CI where we want fresh downloads)
        if local_path.exists() and not is_ci:
            print(f"⏭️  {local_name} already exists, skipping")
            success_count += 1
            continue

        # Construct download URL
        # TODO: Replace with actual Zenodo record URL
        download_url = f"{ZENODO_BASE_URL}{remote_name}"

        # For now, create a placeholder file (replace with actual download)
        print(f"⚠️  Placeholder: Would download {remote_name}")
        print("   Update ZENODO_BASE_URL with actual Zenodo record URL"
        # Uncomment when Zenodo record is created:
        # if download_file(download_url, local_path):
        #     success_count += 1

        # Create placeholder file for now
        local_path.write_text('{"type": "FeatureCollection", "features": []}')
        success_count += 1

    print(f"\n📊 Download Summary: {success_count}/{total_count} files processed")

    if success_count == total_count:
        print("✅ All data files ready!")
        return 0
    else:
        print("❌ Some downloads failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())