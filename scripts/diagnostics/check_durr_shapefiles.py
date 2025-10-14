import geopandas as gpd

# Check coastline shapefile
coastline = gpd.read_file('data/raw/Worldwide-typology-Shapefile-Durr_2011/typology_coastline.shp')
print('=== COASTLINE SHAPEFILE ===')
print(f'Features: {len(coastline):,}')
print(f'\nColumns: {coastline.columns.tolist()}')
print(f'\nSample data:')
print(coastline.head())
print(f'\nEstuary types (FIN_TYP):')
print(coastline['FIN_TYP'].value_counts())
print(f'\nType mapping:')
type_map = {1: 'Delta', 2: 'Lagoon', 3: 'Fjord', 4: 'Coastal Plain', 5: 'Karst', 6: 'Tidal system', 7: 'Archipelagic', 8: 'Small deltas'}
for code, name in type_map.items():
    count = len(coastline[coastline['FIN_TYP'] == code])
    print(f'  {code} = {name}: {count:,}')

# Check catchment shapefile
print('\n' + '='*80)
print('=== CATCHMENT SHAPEFILE ===')
catchment = gpd.read_file('data/processed/durr_estuaries.geojson')
print(f'Features: {len(catchment):,}')
print(f'\nColumns: {catchment.columns.tolist()}')
print(f'\nEstuary types:')
if 'type' in catchment.columns:
    print(catchment['type'].value_counts())
elif 'estuary_type' in catchment.columns:
    print(catchment['estuary_type'].value_counts())
