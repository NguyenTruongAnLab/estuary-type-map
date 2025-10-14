#!/usr/bin/env python3
"""
Clean Git History - Remove Large Files
======================================

PURPOSE: Remove large files from git history to enable GitHub push

USAGE: python clean_git_history.py

Author: Global Water Body Surface Area Atlas Project
Date: October 14, 2025
"""

import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def run_command(command):
    """Run shell command"""
    try:
        result = subprocess.run(command, shell=True, cwd=BASE_DIR, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def main():
    print("🧹 Cleaning Git History - Removing Large Files")
    print("=" * 60)
    
    # Files to remove from history
    large_files = [
        "diagnostics_html/tidal_basins_with_rivers.html",
        "data/web/basins_coastal_lev08_z7-10.geojson"
    ]
    
    print(f"Files to remove from git history:")
    for file in large_files:
        print(f"  - {file}")
    
    print(f"\n⚠️ This will rewrite git history. Continue? (y/N): ", end="")
    response = input().lower().strip()
    
    if response != 'y':
        print("❌ Aborted")
        return False
    
    # Check if git-filter-repo is available
    success, _, _ = run_command("git filter-repo --version")
    if success:
        print("✅ Using git-filter-repo (recommended)")
        
        for file in large_files:
            print(f"🗑️ Removing {file} from history...")
            cmd = f'git filter-repo --path "{file}" --invert-paths --force'
            success, output, error = run_command(cmd)
            
            if success:
                print(f"   ✅ Removed {file}")
            else:
                print(f"   ❌ Failed: {error}")
    else:
        print("⚠️ git-filter-repo not found, using git filter-branch")
        
        # Set environment variable to suppress warning
        import os
        os.environ['FILTER_BRANCH_SQUELCH_WARNING'] = '1'
        
        for file in large_files:
            print(f"🗑️ Removing {file} from history...")
            cmd = f'git filter-branch --force --index-filter "git rm --cached --ignore-unmatch \\"{file}\\"" --prune-empty --tag-name-filter cat -- --all'
            success, output, error = run_command(cmd)
            
            if success:
                print(f"   ✅ Removed {file}")
            else:
                print(f"   ❌ Failed: {error}")
    
    # Force push to update remote
    print(f"\n🚀 Force pushing clean history to GitHub...")
    success, output, error = run_command("git push origin main --force")
    
    if success:
        print("✅ Successfully pushed clean history!")
        print("\n🎉 Git history cleaned! You can now:")
        print("   1. Run: python automated_github_release.py")
        print("   2. Or manually create release at: https://github.com/NguyenTruongAnLab/estuary-type-map/releases/new")
    else:
        print(f"❌ Failed to push: {error}")
        print("\n📋 Manual steps:")
        print("   1. git push origin main --force")
        print("   2. If still fails, contact GitHub support or use Git LFS")
    
    return success

if __name__ == "__main__":
    main()