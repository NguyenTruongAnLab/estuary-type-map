🌊 Milestone Release v1.0.0: High-Resolution Global Tidal Basin Atlas

BREAKING CHANGES:
- Corrected Dürr et al. (2011) type mapping based on official documentation
- New primary dataset: tidal_basins_river_based_lev07.gpkg (16,189 basins)
- Classification priority: coastline > catchment for ocean basins

FEATURES:
✨ First global tidal basin database using BasinATLAS Level 7 (direct polygon measurement)
✨ Corrected Dürr 2011 typology implementation (8 types: Tidal systems, Small deltas, Lagoons, Fjords, Large Rivers, Large Rivers + tidal deltas, Karst, Arheic)
✨ Dual-layer web maps with interactive pie charts (Chart.js)
✨ GRIT river integration (148,824 large rivers in tidal zones)
✨ 36.6 million km² catchment area, 0-300km from coast

FIXES:
🐛 Fixed Dürr type codes (Type I=Small deltas, Type II=Tidal systems, etc.)
🐛 Fixed Mekong Delta classification (now "Large Rivers with tidal deltas")
🐛 Fixed Dürr area calculation (117.2 million km² using equal-area projection)
🐛 Fixed pie chart visualization (now shows real circular charts with percentages)

DATA:
📦 data/processed/tidal_basins_river_based_lev07.gpkg (380 MB)
📦 data/web/tidal_basins_precise.geojson (28.5 MB)
📦 diagnostics_html/tidal_basins_web.html (interactive map with charts)

SCRIPTS:
🔧 scripts/diagnostics/create_tidal_basins_river_based.py (main processing)
🔧 scripts/web_optimization/create_web_tidal_basins.py (web generation)

DOCUMENTATION:
📚 RELEASE_NOTES_v1.0.0.md (comprehensive release notes)
📚 Updated README.md with corrected type mapping
📚 Copilot instructions updated with correct Dürr framework

See RELEASE_NOTES_v1.0.0.md for full details.
