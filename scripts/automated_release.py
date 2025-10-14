#!/usr/bin/env python3
"""
Complete GitHub Release Automation System
=========================================

PURPOSE: Complete automation for GitHub releases with large file management
- Scans for files >30MB and manages them automatically
- Creates release file list (Markdown)
- Generates complete release documentation
- Automates GitHub release creation with file attachments

USAGE:
    python scripts/automated_release.py [--tag TAG] [--dry-run]

Author: Global Water Body Surface Area Atlas Project
Date: October 14, 2025
"""

import os
import subprocess
import argparse
from pathlib import Path
import json
from datetime import datetime
import shutil

# Configuration
MAX_FILE_SIZE_MB = 30
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
BASE_DIR = Path(__file__).resolve().parent.parent

# Release configuration
DEFAULT_TAG = "v1.0.0"
DEFAULT_TITLE = "v1.0.0 - High-Resolution Global Tidal Basin Atlas"
RELEASE_NOTES_FILE = "docs/RELEASE_NOTES_v1.0.0.md"
RELEASE_DATASET_FILE = "release_dataset.md"

def get_file_size_mb(file_path):
    """Get file size in MB"""
    try:
        return os.path.getsize(file_path) / (1024 * 1024)
    except (OSError, FileNotFoundError):
        return 0

def run_command(command, capture_output=True):
    """Run shell command"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=BASE_DIR,
            capture_output=capture_output, 
            text=True
        )
        return result.returncode == 0, result.stdout.strip() if capture_output else "", result.stderr.strip() if capture_output else ""
    except Exception as e:
        return False, "", str(e)

def find_large_files():
    """Find all files larger than MAX_FILE_SIZE_MB"""
    print(f"\n🔍 Scanning repository for files larger than {MAX_FILE_SIZE_MB} MB...")
    
    large_files = []
    
    # Walk through all files in the repository
    for root, dirs, files in os.walk(BASE_DIR):
        # Skip .git directory
        if '.git' in dirs:
            dirs.remove('.git')
        
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(BASE_DIR)
            
            size_mb = get_file_size_mb(file_path)
            if size_mb > MAX_FILE_SIZE_MB:
                file_info = {
                    'path': str(relative_path),
                    'absolute_path': str(file_path),
                    'size_mb': round(size_mb, 1),
                    'size_bytes': file_path.stat().st_size,
                    'extension': file_path.suffix.lower(),
                    'category': categorize_file(file_path)
                }
                
                large_files.append(file_info)
    
    # Sort by size (largest first)
    large_files.sort(key=lambda x: x['size_mb'], reverse=True)
    
    print(f"   Found {len(large_files)} files > {MAX_FILE_SIZE_MB} MB")
    
    return large_files, []

def categorize_file(file_path):
    """Categorize files for release organization"""
    path_str = str(file_path).lower()
    
    if 'tidal_basins' in path_str and file_path.suffix == '.gpkg':
        return 'primary_dataset'
    elif 'diagnostics_html' in path_str and file_path.suffix == '.html':
        return 'interactive_map'
    elif file_path.suffix == '.gpkg':
        return 'dataset'
    elif file_path.suffix == '.geojson':
        return 'web_data'
    elif file_path.suffix == '.html':
        return 'visualization'
    elif file_path.suffix in ['.nc', '.csv']:
        return 'raw_data'
    else:
        return 'other'

def parse_release_dataset_file():
    """Parse release_dataset.md to get file list for release"""
    dataset_file = BASE_DIR / RELEASE_DATASET_FILE
    if not dataset_file.exists():
        print(f"❌ Release dataset file not found: {RELEASE_DATASET_FILE}")
        return []
    
    release_files = []
    with open(dataset_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse markdown to extract file paths
    import re
    # Find all **Path**: `filepath` patterns
    path_pattern = r'\*\*Path\*\*: `([^`]+)`'
    size_pattern = r'\*\*Size\*\*: ([^\n]+)'
    desc_pattern = r'\*\*Description\*\*: ([^\n]+)'
    
    lines = content.split('\n')
    current_file = None
    
    for i, line in enumerate(lines):
        # Look for file headers (### filename)
        if line.startswith('### ') and not line.startswith('### ') or 'Path' in line:
            if '**Path**' in line:
                path_match = re.search(path_pattern, line)
                if path_match:
                    file_path = path_match.group(1)
                    full_path = BASE_DIR / file_path
                    
                    if full_path.exists():
                        # Get size and description from nearby lines
                        size_str = "Unknown"
                        desc_str = "No description"
                        
                        # Look for size and description in next few lines
                        for j in range(i+1, min(i+5, len(lines))):
                            if '**Size**' in lines[j]:
                                size_match = re.search(size_pattern, lines[j])
                                if size_match:
                                    size_str = size_match.group(1).strip()
                            elif '**Description**' in lines[j]:
                                desc_match = re.search(desc_pattern, lines[j])
                                if desc_match:
                                    desc_str = desc_match.group(1).strip()
                        
                        release_files.append({
                            'path': file_path,
                            'absolute_path': str(full_path),
                            'size_mb': get_file_size_mb(full_path),
                            'name': full_path.name,
                            'description': desc_str,
                            'size_str': size_str
                        })
    
    return release_files

def update_gitignore(large_files):
    """Update .gitignore with large files"""
    print(f"\n📝 Updating .gitignore...")
    
    gitignore_path = BASE_DIR / '.gitignore'
    
    # Read existing .gitignore
    existing_lines = []
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            existing_lines = [line.rstrip() for line in f.readlines()]
    
    # Prepare new lines to add
    new_lines = []
    
    # Add header if not exists
    header = f"# Large files >30MB (auto-generated {datetime.now().strftime('%Y-%m-%d %H:%M')})"
    if not any('auto-generated' in line for line in existing_lines):
        new_lines.extend([
            "",
            header,
            "# Files larger than 30MB are excluded from git and included in GitHub releases"
        ])
    
    # Add specific large files
    files_added = 0
    for file_info in large_files:
        file_path = file_info['path'].replace('\\', '/')  # Use forward slashes
        if file_path not in existing_lines and not any(file_path in line for line in existing_lines):
            new_lines.append(file_path)
            files_added += 1
    
    # Write updated .gitignore
    if new_lines:
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            f.write('\n'.join(new_lines) + '\n')
        print(f"   Added {files_added} large files to .gitignore")
    else:
        print("   .gitignore is already up to date")

def create_release_file_list(important_files):
    """Create markdown file with release file list"""
    print(f"\n📋 Creating release file list...")
    
    # Group files by category
    categories = {}
    for file_info in important_files:
        cat = file_info['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(file_info)
    
    # Create markdown content
    content = f"""# 📦 GitHub Release Files - v1.0.0

## 🎯 Large Files for Release Attachment

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Files**: {len(important_files)}  
**Total Size**: {sum(f['size_mb'] for f in important_files):.1f} MB

---

"""
    
    # Add files by category
    category_names = {
        'primary_dataset': '🌊 Primary Datasets',
        'interactive_map': '🗺️ Interactive Maps',
        'dataset': '📊 Datasets',
        'web_data': '🌐 Web Data',
        'visualization': '📈 Visualizations',
        'raw_data': '📁 Raw Data',
        'other': '📄 Other Files'
    }
    
    for cat, files in categories.items():
        if not files:
            continue
            
        content += f"## {category_names.get(cat, cat.title())}\n\n"
        
        for file_info in sorted(files, key=lambda x: x['size_mb'], reverse=True):
            content += f"- **{Path(file_info['path']).name}** ({file_info['size_mb']} MB)\n"
            content += f"  - Path: `{file_info['path']}`\n"
            content += f"  - Size: {file_info['size_mb']} MB\n\n"
    
    content += f"""---

## 🚀 Release Instructions

### Manual Upload Steps:
1. Go to: https://github.com/NguyenTruongAnLab/estuary-type-map/releases/new
2. Choose tag: `v1.0.0`
3. Title: `v1.0.0 - High-Resolution Global Tidal Basin Atlas`
4. Description: Copy from `{RELEASE_NOTES_FILE}`
5. Attach all files listed above
6. Publish release

### Automated Upload (if GitHub CLI available):
```bash
python scripts/automated_release.py --tag v1.0.0
```

---

## 📊 File Statistics

"""
    
    # Add statistics
    total_size = sum(f['size_mb'] for f in important_files)
    for cat, files in categories.items():
        if files:
            cat_size = sum(f['size_mb'] for f in files)
            content += f"- {category_names.get(cat, cat.title())}: {len(files)} files, {cat_size:.1f} MB\n"
    
    content += f"\n**Total**: {len(important_files)} files, {total_size:.1f} MB\n"
    
    # Save file
    release_list_path = BASE_DIR / 'RELEASE_FILES_v1.0.0.md'
    with open(release_list_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"   ✅ Created: {release_list_path.name}")
    return release_list_path

def create_automated_release_script(important_files, tag, title):
    """Create automated GitHub release script"""
    print(f"\n🤖 Creating automated release script...")
    
    script_content = f'''#!/usr/bin/env python3
"""
Automated GitHub Release v1.0.0
===============================

Auto-generated script to create GitHub release with all large file attachments

Usage: python automated_github_release.py
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
RELEASE_TAG = "{tag}"
RELEASE_TITLE = "{title}"
RELEASE_NOTES_FILE = BASE_DIR / "{RELEASE_NOTES_FILE}"

# Files to attach (generated {datetime.now().strftime('%Y-%m-%d %H:%M')})
RELEASE_FILES = [
'''
    
    for file_info in important_files:
        script_content += f"""    {{
        'local_path': r"{file_info['absolute_path']}",
        'name': "{Path(file_info['path']).name}",
        'size_mb': {file_info['size_mb']},
        'category': "{file_info['category']}"
    }},
"""
    
    script_content += f''']

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
        print("\\n📋 Manual release instructions:")
        print("1. Go to: https://github.com/NguyenTruongAnLab/estuary-type-map/releases/new")
        print(f"2. Tag: {{RELEASE_TAG}}")
        print(f"3. Title: {{RELEASE_TITLE}}")
        print(f"4. Description: Copy from {{RELEASE_NOTES_FILE}}")
        print("5. Attach these files:")
        for file_info in RELEASE_FILES:
            print(f"   - {{file_info['name']}} ({{file_info['size_mb']}} MB)")
        return False
    
    # Check if release notes exist
    if not RELEASE_NOTES_FILE.exists():
        print(f"❌ Release notes file not found: {{RELEASE_NOTES_FILE}}")
        return False
    
    # Create release
    print(f"📝 Creating release {{RELEASE_TAG}}...")
    cmd = f'gh release create {{RELEASE_TAG}} --title "{{RELEASE_TITLE}}" --notes-file "{{RELEASE_NOTES_FILE}}"'
    success, output, error = run_command(cmd)
    
    if not success:
        if "already exists" in error.lower():
            print("⚠️ Release already exists. Uploading files to existing release...")
        else:
            print(f"❌ Failed to create release: {{error}}")
            return False
    else:
        print("✅ Release created successfully")
    
    # Attach files
    print(f"\\n📎 Uploading {{len(RELEASE_FILES)}} large files...")
    uploaded = 0
    
    for i, file_info in enumerate(RELEASE_FILES, 1):
        file_path = Path(file_info['local_path'])
        if file_path.exists():
            print(f"   [{{i}}/{{len(RELEASE_FILES)}}] {{file_info['name']}} ({{file_info['size_mb']}} MB)...")
            cmd = f'gh release upload {{RELEASE_TAG}} "{{file_path}}"'
            success, output, error = run_command(cmd)
            
            if success:
                uploaded += 1
                print(f"   ✅ Uploaded {{file_info['name']}}")
            else:
                if "already exists" in error.lower():
                    uploaded += 1
                    print(f"   ⚠️ {{file_info['name']}} already exists in release")
                else:
                    print(f"   ❌ Failed: {{error}}")
        else:
            print(f"   ❌ File not found: {{file_path}}")
    
    print(f"\\n🎉 Release complete!")
    print(f"   📊 Uploaded: {{uploaded}}/{{len(RELEASE_FILES)}} files")
    print(f"   🌐 View: https://github.com/NguyenTruongAnLab/estuary-type-map/releases/tag/{{RELEASE_TAG}}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'''
    
    script_path = BASE_DIR / 'automated_github_release.py'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"   ✅ Created: {script_path.name}")
    return script_path

def main():
    parser = argparse.ArgumentParser(description='Automated GitHub release system')
    parser.add_argument('--tag', default=DEFAULT_TAG, help='Release tag')
    parser.add_argument('--title', default=DEFAULT_TITLE, help='Release title')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    print("="*80)
    print("🚀 AUTOMATED GITHUB RELEASE SYSTEM")
    print("="*80)
    print(f"Repository: {BASE_DIR}")
    print(f"Max file size: {MAX_FILE_SIZE_MB} MB")
    print(f"Release tag: {args.tag}")
    print(f"Dry run: {args.dry_run}")
    
    if args.dry_run:
        print("\\n⚠️ DRY RUN MODE - No changes will be made")
    
    # Step 1: Find large files
    large_files, _ = find_large_files()
    
    # Step 2: Parse release dataset file
    important_files = parse_release_dataset_file()
    
    if not large_files:
        print(f"\\n✅ No files larger than {MAX_FILE_SIZE_MB} MB found!")
        return
    
    print(f"\\n📊 Summary:")
    print(f"   • Large files: {len(large_files)} ({sum(f['size_mb'] for f in large_files):.1f} MB)")
    print(f"   • Important for release: {len(important_files)} ({sum(f['size_mb'] for f in important_files):.1f} MB)")
    
    if args.dry_run:
        print(f"\\n📋 Would update .gitignore with {len(large_files)} files")
        print(f"📋 Would create release file list with {len(important_files)} files")
        print(f"📋 Would create automated release script")
        return
    
    # Step 2: Update .gitignore
    update_gitignore(large_files)
    
    # Step 3: Create release file list
    release_list_path = create_release_file_list(important_files)
    
    # Step 4: Create automated release script
    release_script_path = create_automated_release_script(important_files, args.tag, args.title)
    
    # Step 5: Summary and next steps
    total_size = sum(f['size_mb'] for f in important_files)
    print(f"\\n{'='*80}")
    print("✅ AUTOMATED RELEASE SYSTEM READY!")
    print(f"{'='*80}")
    print(f"📊 Release Summary:")
    print(f"   • Files for release: {len(important_files)}")
    print(f"   • Total release size: {total_size:.1f} MB")
    print(f"   • Files excluded from git: {len(large_files)}")
    
    print(f"\\n📁 Generated Files:")
    print(f"   • {release_list_path.name} - Release file manifest")
    print(f"   • {release_script_path.name} - Automated release script")
    
    print(f"\\n🚀 Next Steps:")
    print(f"   1. Review changes: git diff .gitignore")
    print(f"   2. Commit changes: git add . && git commit -m 'Prepare v1.0.0 release'")
    print(f"   3. Push changes: git push origin main")
    print(f"   4. Create release: python {release_script_path.name}")
    
    print(f"\\n📦 Release Files:")
    for file_info in important_files:
        print(f"   • {Path(file_info['path']).name} ({file_info['size_mb']} MB)")

if __name__ == "__main__":
    main()