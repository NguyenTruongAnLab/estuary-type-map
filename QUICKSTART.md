# Quick Start Guide

Get the Global Estuary Type Map up and running in minutes!

## 🚀 For Users (View the Map)

### Visit the Live Site

Simply go to: **[https://nguyentruonganlab.github.io/estuary-type-map/](https://nguyentruonganlab.github.io/estuary-type-map/)**

That's it! The map is ready to use.

## 🔍 How to Use the Map

### Explore Estuaries

1. **Pan**: Click and drag the map to move around
2. **Zoom**: Use mouse wheel or +/- buttons
3. **Click markers**: View detailed information about each estuary

### Filter by Type

Use the sidebar checkboxes to filter estuaries:
- ✅ **All Types**: Show/hide all estuaries
- Individual types: Delta, Fjord, Lagoon, Ria, etc.

### Learn About Types

Scroll down in the sidebar to read:
- Scientific definitions for each estuary type
- Formation processes and characteristics
- Academic references

## 💻 For Developers (Run Locally)

### Prerequisites

- Python 3.x
- Modern web browser
- Git (optional)

### Quick Setup

1. **Clone or download the repository**:
   ```bash
   git clone https://github.com/NguyenTruongAnLab/estuary-type-map.git
   cd estuary-type-map
   ```

2. **Start a local web server**:
   ```bash
   python3 -m http.server 8000
   ```

3. **Open your browser**:
   ```
   http://localhost:8000
   ```

### Alternative Servers

**Node.js**:
```bash
npx http-server
```

**PHP**:
```bash
php -S localhost:8000
```

**VS Code**:
Install "Live Server" extension and right-click `index.html`

## 🔧 For Contributors (Modify & Add Data)

### Add New Estuaries

The data is now sourced from real scientific datasets. To contribute:

1. **Option A: Add to source data**
   - Add to `data/Worldwide-typology-Shapefile-Durr_2011/` (shapefile format)
   - Or contribute to Baum et al. (2024) dataset for large estuaries

2. **Option B: Modify filtering/sampling**
   ```bash
   nano scripts/process_estuary_data.py
   ```
   
   Adjust the filtering criteria in `load_durr_data()` or sampling logic in `main()` to include more/different estuaries.

3. **Install dependencies**:
   ```bash
   pip install geopandas pandas pyproj
   ```

4. **Run the processing script**:
   ```bash
   python3 scripts/process_estuary_data.py
   ```

5. **Test the data**:
   ```bash
   python3 scripts/test_data.py
   ```

6. **View your changes**:
   Start local server and check the map

7. **Submit your contribution**:
   ```bash
   git add data/estuaries.geojson scripts/process_estuary_data.py
   git commit -m "Update estuary data filtering"
   git push
   ```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 🌐 Deploy Your Own Copy

### To GitHub Pages

1. **Fork the repository** on GitHub
2. Go to **Settings** → **Pages**
3. Enable Pages from `main` branch
4. Your map will be at: `https://[your-username].github.io/estuary-type-map/`

### To Other Platforms

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for:
- Netlify deployment
- Vercel deployment
- CloudFlare Pages
- Custom domain setup

## 📚 Learn More

- **README.md**: Full documentation and citations
- **docs/TECHNICAL.md**: Technical details and API reference
- **docs/DEPLOYMENT.md**: Deployment options and troubleshooting
- **CONTRIBUTING.md**: How to contribute

## 🎯 Common Tasks

### View All Estuaries in Console

Open browser developer tools and run:
```javascript
console.table(
    estuaryData.features.map(f => ({
        name: f.properties.name,
        type: f.properties.type,
        country: f.properties.country
    }))
);
```

### Export Filtered Data

1. Filter to your desired types
2. Open console
3. Run:
   ```javascript
   console.log(JSON.stringify(estuaryData, null, 2));
   ```
4. Copy the output

### Check Data Statistics

Run the test script:
```bash
python3 scripts/test_data.py
```

## 🐛 Troubleshooting

### Map Not Loading?

- Check browser console (F12) for errors
- Ensure you're using a web server (not `file://`)
- Verify `data/estuaries.geojson` exists

### Markers Missing?

- Check GeoJSON file is valid
- Verify coordinates are [longitude, latitude]
- Check browser console for JavaScript errors

### Filters Not Working?

- Clear browser cache (Ctrl+F5)
- Check JavaScript console for errors
- Try a different browser

## 💡 Tips

- **Best View**: Use zoom level 3-8 for global overview
- **Mobile**: Works best in landscape orientation
- **Sharing**: Share specific locations by copying the URL after navigating
- **Printing**: Use browser print to create a static map

## 🆘 Get Help

- **Issues**: Report bugs at [GitHub Issues](https://github.com/NguyenTruongAnLab/estuary-type-map/issues)
- **Questions**: Open a [Discussion](https://github.com/NguyenTruongAnLab/estuary-type-map/discussions)
- **Documentation**: Check all `.md` files in the repo

## 🌟 Quick Examples

### Filter to Only Deltas

1. Uncheck "All Types"
2. Check only "Delta"
3. See 8 major river deltas worldwide

### Compare Fjords

1. Filter to "Fjord"
2. Click each marker to compare depths
3. Note geographic distribution (high latitudes)

### Find Nearest Estuary

1. Zoom to your region
2. Look for nearest marker
3. Click for details

---

**Ready to explore? Visit the [live map](https://nguyentruonganlab.github.io/estuary-type-map/) now! 🌊**
