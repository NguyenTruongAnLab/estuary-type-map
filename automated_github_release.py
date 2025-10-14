#!/usr/bin/env python3
"""
Automated GitHub Release with Markdown File List
===============================================

Creates GitHub release v1.0.0 reading file list from release_dataset.md

Usage: python automated_github_release.py
"""

import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
RELEASE_TAG = "v1.0.0"
RELEASE_TITLE = "v1.0.0 - High-Resolution Global Tidal Basin Atlas"
RELEASE_NOTES_FILE = BASE_DIR / "docs" / "RELEASE_NOTES_v1.0.0.md"
RELEASE_DATASET_FILE = BASE_DIR / "release_dataset.md"

# Files to attach (generated 2025-10-14 15:39)
RELEASE_FILES = [
    {
        'local_path': r"H:\My Drive\Project\TROPECOS\Github\estuary-type-map\data\processed\tidal_basins_river_based_lev07.gpkg",
        'name': "tidal_basins_river_based_lev07.gpkg",
        'size_mb': 111.4,
        'category': "primary_dataset"
    },
]

def run_command(command):
    """Run shell command"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def main():
    print("🚀 Creating GitHub release v1.0.0 with large file attachments...")
    
    # Check if gh CLI is available
    success, _, _ = run_command("gh --version")
    if not success:
        print("❌ GitHub CLI (gh) not found.")
        print("\n📋 Manual release instructions:")
        print("1. Go to: https://github.com/NguyenTruongAnLab/estuary-type-map/releases/new")
        print(f"2. Tag: {RELEASE_TAG}")
        print(f"3. Title: {RELEASE_TITLE}")
        print(f"4. Description: Copy from {RELEASE_NOTES_FILE}")
        print("5. Attach these files:")
        for file_info in RELEASE_FILES:
            print(f"   - {file_info['name']} ({file_info['size_mb']} MB)")
        return False
    
    # Check if release notes exist
    if not RELEASE_NOTES_FILE.exists():
        print(f"❌ Release notes file not found: {RELEASE_NOTES_FILE}")
        return False
    
    # Create release
    print(f"📝 Creating release {RELEASE_TAG}...")
    cmd = f'gh release create {RELEASE_TAG} --title "{RELEASE_TITLE}" --notes-file "{RELEASE_NOTES_FILE}"'
    success, output, error = run_command(cmd)
    
    if not success:
        if "already exists" in error.lower():
            print("⚠️ Release already exists. Uploading files to existing release...")
        else:
            print(f"❌ Failed to create release: {error}")
            return False
    else:
        print("✅ Release created successfully")
    
    # Attach files
    print(f"\n📎 Uploading {len(RELEASE_FILES)} large files...")
    uploaded = 0
    
    for i, file_info in enumerate(RELEASE_FILES, 1):
        file_path = Path(file_info['local_path'])
        if file_path.exists():
            print(f"   [{i}/{len(RELEASE_FILES)}] {file_info['name']} ({file_info['size_mb']} MB)...")
            cmd = f'gh release upload {RELEASE_TAG} "{file_path}"'
            success, output, error = run_command(cmd)
            
            if success:
                uploaded += 1
                print(f"   ✅ Uploaded {file_info['name']}")
            else:
                if "already exists" in error.lower():
                    uploaded += 1
                    print(f"   ⚠️ {file_info['name']} already exists in release")
                else:
                    print(f"   ❌ Failed: {error}")
        else:
            print(f"   ❌ File not found: {file_path}")
    
    print(f"\n🎉 Release complete!")
    print(f"   📊 Uploaded: {uploaded}/{len(RELEASE_FILES)} files")
    print(f"   🌐 View: https://github.com/NguyenTruongAnLab/estuary-type-map/releases/tag/{RELEASE_TAG}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
