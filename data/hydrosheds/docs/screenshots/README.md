# Screenshot Placeholders

This directory contains screenshot placeholders for the HydroSHEDS documentation.

## Required Screenshots

### 01_download.png
**Purpose**: Show HydroSHEDS RiverATLAS download page  
**URL**: https://www.hydrosheds.org/products/riveratlas  
**What to capture**:
- Full webpage showing download section
- Highlight "RiverATLAS v1.0 Shapefile" download link
- File size information visible

### 01_download_basin.png
**Purpose**: Show HydroSHEDS BasinATLAS download page  
**URL**: https://www.hydrosheds.org/products/basinatlas  
**What to capture**:
- Full webpage showing download section
- Highlight "BasinATLAS v1.0 Geodatabase" download link
- File size information visible

### 02_extract.png
**Purpose**: Show file extraction process  
**What to capture**:
- File explorer showing extracted directory structure
- RiverATLAS_v10_shp/ folder with .shp, .dbf, .shx files
- File sizes visible

### 03_processing.png
**Purpose**: Show compression script output  
**Command**: `python scripts/compress_hydrosheds.py`  
**What to capture**:
- Terminal/console output showing:
  - Progress bars
  - Compression statistics
  - File size reductions
  - Success messages

### 04_validation.png
**Purpose**: Show validation script output  
**Command**: `python scripts/validate_hydrosheds.py`  
**What to capture**:
- Terminal output showing:
  - Validation checks (✅ marks)
  - Attribute completeness
  - File sizes
  - Summary table

### 05_browser_rivers.png (Optional)
**Purpose**: Show rivers visualization in web map  
**URL**: http://localhost:8000  
**What to capture**:
- Web map with "Rivers" mode active
- Rivers colored by classification (tidal vs freshwater)
- Popup showing river attributes

## How to Add Screenshots

1. Take screenshots following the descriptions above
2. Save as PNG files with exact filenames
3. Place in this directory: `data/hydrosheds/docs/screenshots/`
4. Screenshots will automatically appear in README.md

## Image Specifications

- **Format**: PNG (preferred) or JPG
- **Resolution**: At least 1280x720 pixels
- **File size**: Compress to <500KB each
- **Content**: Clear, readable text and UI elements

## Optional: Automated Screenshot Tool

For terminal output screenshots, you can use:
```bash
# Linux/Mac
script -q -c "python scripts/compress_hydrosheds.py" /dev/null | ansi2html > output.html
# Then screenshot the HTML

# Windows PowerShell
Start-Transcript -Path output.txt
python scripts/compress_hydrosheds.py
Stop-Transcript
```

---

**Note**: Screenshots are optional but highly recommended for user-friendly documentation.
