"""
Generate Gallery Index from diagnostics_html Folder
====================================================

Automatically creates a JSON index of all HTML visualizations for the gallery page.
Categorizes files based on filename patterns.

Usage:
    python scripts/generate_gallery_index.py
"""

import json
from pathlib import Path
from datetime import datetime
import os

BASE_DIR = Path(__file__).resolve().parent.parent
HTML_DIR = BASE_DIR / 'diagnostics_html'
OUTPUT_DIR = BASE_DIR / 'data'
OUTPUT_FILE = OUTPUT_DIR / 'gallery_index.json'

def categorize_file(filename):
    """Auto-categorize based on filename patterns"""
    filename_lower = filename.lower()
    
    # Category patterns (order matters - more specific first)
    patterns = [
        (['tidal', 'basin'], 'Tidal Basin Analysis'),
        (['river', 'grit', 'stream'], 'River Network Analysis'),
        (['coastal', 'coast'], 'Coastal Analysis'),
        (['salinity', 'globsalt'], 'Salinity Classification'),
        (['morphometry', 'baum'], 'Morphometry'),
        (['durr', 'estuary', 'estuarine'], 'Estuary Typology'),
        (['dynqual'], 'DynQual Hydrology'),
        (['gcc'], 'Coastal Characteristics (GCC)'),
        (['map', 'web'], 'Interactive Maps'),
        (['notebook', 'analysis'], 'Jupyter Notebooks'),
        (['validation', 'verify'], 'Validation & QA'),
    ]
    
    for keywords, category in patterns:
        if any(keyword in filename_lower for keyword in keywords):
            return category
    
    return 'General Visualizations'

def generate_title(filename):
    """Generate human-readable title from filename"""
    # Remove extension
    name = Path(filename).stem
    
    # Replace underscores and hyphens with spaces
    name = name.replace('_', ' ').replace('-', ' ')
    
    # Capitalize words
    return ' '.join(word.capitalize() for word in name.split())

def get_file_info(html_file):
    """Get metadata for a single HTML file"""
    relative_path = html_file.relative_to(BASE_DIR).as_posix()
    filename = html_file.name
    
    # Get file size
    size_bytes = html_file.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    
    # Get modification time
    mtime = html_file.stat().st_mtime
    modified = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
    
    return {
        'title': generate_title(filename),
        'path': '/' + relative_path,  # Add leading slash for absolute path
        'filename': filename,
        'size_mb': round(size_mb, 2),
        'modified': modified
    }

def generate_gallery_index():
    """Generate JSON index of all HTML files in diagnostics_html/"""
    print(f"\n{'='*80}")
    print(f"GENERATING GALLERY INDEX")
    print(f"{'='*80}\n")
    
    if not HTML_DIR.exists():
        print(f"❌ Error: diagnostics_html folder not found: {HTML_DIR}")
        return
    
    print(f"📂 Scanning: {HTML_DIR}")
    
    gallery_items = []
    
    # Find all HTML files
    html_files = list(HTML_DIR.rglob('*.html'))
    
    print(f"   Found {len(html_files)} HTML files\n")
    
    # Process each file
    for html_file in html_files:
        try:
            item = get_file_info(html_file)
            gallery_items.append(item)
            print(f"   ✓ {item['filename']}")
        except Exception as e:
            print(f"   ⚠️  Error processing {html_file.name}: {e}")
    
    # Sort by title
    gallery_items.sort(key=lambda x: x['title'])
    
    # Create output directory if needed
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Write JSON file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(gallery_items, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"✅ SUCCESS")
    print(f"{'='*80}")
    print(f"\n📊 Gallery Index Generated:")
    print(f"   Total visualizations: {len(gallery_items)}")
    print(f"   Output file: {OUTPUT_FILE}")
    print(f"   File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
    
    print(f"\n🎉 Gallery page is ready to use!\n")

if __name__ == '__main__':
    generate_gallery_index()
