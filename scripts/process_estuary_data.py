#!/usr/bin/env python3
"""
Process estuary data and classify by geomorphological shape types.
Data source: Laruelle et al. (2024, Estuaries and Coasts)

This script processes global estuary datasets and generates a GeoJSON file
with estuary locations and their classifications.
"""

import json
import sys

def create_sample_estuary_data():
    """
    Creates sample estuary data classified by geomorphological types.
    
    In a production environment, this would fetch and process actual data from:
    Laruelle, G.G., et al. (2024). A global classification of estuaries based on 
    their geomorphological characteristics. Estuaries and Coasts.
    
    Types based on geomorphological classification:
    - Delta: River-dominated, sediment-rich formations
    - Fjord: Glacially carved, deep narrow inlets
    - Lagoon: Coastal water bodies separated by barrier islands
    - Ria: Drowned river valley
    - Coastal Plain: Wide, shallow estuaries on flat coastal areas
    - Bar-Built: Formed behind barrier islands or spits
    - Tectonic: Formed by geological faulting or subsidence
    """
    
    estuaries = {
        "type": "FeatureCollection",
        "features": [
            # Deltas
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [90.3563, 22.5726]},
                "properties": {
                    "name": "Ganges-Brahmaputra Delta",
                    "type": "Delta",
                    "country": "Bangladesh/India",
                    "description": "World's largest river delta, highly sediment-laden",
                    "area_km2": 105000,
                    "river": "Ganges, Brahmaputra"
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [29.7167, 45.2167]},
                "properties": {
                    "name": "Danube Delta",
                    "type": "Delta",
                    "country": "Romania/Ukraine",
                    "description": "Major European delta with extensive wetlands",
                    "area_km2": 5800,
                    "river": "Danube"
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [31.1656, 30.4167]},
                "properties": {
                    "name": "Nile Delta",
                    "type": "Delta",
                    "country": "Egypt",
                    "description": "Historic delta, one of the world's most productive agricultural regions",
                    "area_km2": 24000,
                    "river": "Nile"
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-91.1767, 29.1550]},
                "properties": {
                    "name": "Mississippi Delta",
                    "type": "Delta",
                    "country": "USA",
                    "description": "Bird's-foot delta, heavily engineered system",
                    "area_km2": 12000,
                    "river": "Mississippi"
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [106.7000, 10.5000]},
                "properties": {
                    "name": "Mekong Delta",
                    "type": "Delta",
                    "country": "Vietnam",
                    "description": "Rice bowl of Vietnam, extensive distributary network",
                    "area_km2": 40000,
                    "river": "Mekong"
                }
            },
            
            # Fjords
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [7.0667, 60.8667]},
                "properties": {
                    "name": "Sognefjord",
                    "type": "Fjord",
                    "country": "Norway",
                    "description": "Longest and deepest fjord in Norway, glacially carved",
                    "area_km2": 350,
                    "depth_m": 1308
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [8.5000, 61.6000]},
                "properties": {
                    "name": "Geirangerfjord",
                    "type": "Fjord",
                    "country": "Norway",
                    "description": "UNESCO World Heritage Site, steep mountains and waterfalls",
                    "area_km2": 15,
                    "depth_m": 260
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-72.9167, -45.4500]},
                "properties": {
                    "name": "Baker Channel",
                    "type": "Fjord",
                    "country": "Chile",
                    "description": "Part of Chilean fjord system, pristine glacial estuary",
                    "area_km2": 280,
                    "depth_m": 450
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [166.5500, -45.3833]},
                "properties": {
                    "name": "Milford Sound",
                    "type": "Fjord",
                    "country": "New Zealand",
                    "description": "Fiordland fjord, surrounded by peaks and rainforest",
                    "area_km2": 16,
                    "depth_m": 290
                }
            },
            
            # Lagoons
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [12.3500, 45.4333]},
                "properties": {
                    "name": "Venetian Lagoon",
                    "type": "Lagoon",
                    "country": "Italy",
                    "description": "Large shallow lagoon, separated from Adriatic by barrier islands",
                    "area_km2": 550,
                    "depth_m": 2
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-80.8500, 35.2333]},
                "properties": {
                    "name": "Pamlico Sound",
                    "type": "Lagoon",
                    "country": "USA",
                    "description": "Largest lagoon along US Atlantic coast, protected by Outer Banks",
                    "area_km2": 5180,
                    "depth_m": 6
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-97.3000, 27.8000]},
                "properties": {
                    "name": "Laguna Madre",
                    "type": "Lagoon",
                    "country": "USA/Mexico",
                    "description": "Hypersaline lagoon system, important seagrass habitat",
                    "area_km2": 2000,
                    "depth_m": 1
                }
            },
            
            # Rias
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-8.7833, 42.5833]},
                "properties": {
                    "name": "Ria de Vigo",
                    "type": "Ria",
                    "country": "Spain",
                    "description": "Drowned river valley, major fishing and aquaculture area",
                    "area_km2": 176,
                    "depth_m": 60
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-9.0000, 42.3333]},
                "properties": {
                    "name": "Ria de Arousa",
                    "type": "Ria",
                    "country": "Spain",
                    "description": "Largest of the Galician rias, extensive mussel farming",
                    "area_km2": 230,
                    "depth_m": 67
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-4.1667, 50.2500]},
                "properties": {
                    "name": "Plymouth Sound",
                    "type": "Ria",
                    "country": "UK",
                    "description": "Natural harbor formed by drowned river valleys",
                    "area_km2": 9,
                    "depth_m": 15
                }
            },
            
            # Coastal Plain Estuaries
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-76.5000, 37.0000]},
                "properties": {
                    "name": "Chesapeake Bay",
                    "type": "Coastal Plain",
                    "country": "USA",
                    "description": "Largest estuary in USA, drowned river valley in coastal plain",
                    "area_km2": 11600,
                    "depth_m": 21
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [0.8833, 51.4833]},
                "properties": {
                    "name": "Thames Estuary",
                    "type": "Coastal Plain",
                    "country": "UK",
                    "description": "Major shipping route, wide funnel-shaped estuary",
                    "area_km2": 285,
                    "depth_m": 10
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [151.2500, -33.8500]},
                "properties": {
                    "name": "Sydney Harbour",
                    "type": "Ria",
                    "country": "Australia",
                    "description": "Drowned river valley, deep water harbor",
                    "area_km2": 55,
                    "depth_m": 45
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-122.4167, 37.8000]},
                "properties": {
                    "name": "San Francisco Bay",
                    "type": "Tectonic",
                    "country": "USA",
                    "description": "Tectonic estuary formed by faulting, highly productive",
                    "area_km2": 4160,
                    "depth_m": 12
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-3.0000, 51.3667]},
                "properties": {
                    "name": "Severn Estuary",
                    "type": "Coastal Plain",
                    "country": "UK",
                    "description": "Funnel-shaped estuary with second highest tidal range in world",
                    "area_km2": 557,
                    "depth_m": 15
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [114.1833, 22.2833]},
                "properties": {
                    "name": "Pearl River Estuary",
                    "type": "Delta",
                    "country": "China",
                    "description": "Highly urbanized delta system, major shipping hub",
                    "area_km2": 2700,
                    "river": "Pearl River"
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [121.8667, 31.2333]},
                "properties": {
                    "name": "Yangtze Estuary",
                    "type": "Delta",
                    "country": "China",
                    "description": "One of world's largest river estuaries by discharge",
                    "area_km2": 6600,
                    "river": "Yangtze"
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [103.8333, 1.2667]},
                "properties": {
                    "name": "Singapore Strait",
                    "type": "Bar-Built",
                    "country": "Singapore/Malaysia/Indonesia",
                    "description": "Major shipping route, bar-built estuary system",
                    "area_km2": 1030,
                    "depth_m": 23
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [138.5833, -34.9167]},
                "properties": {
                    "name": "Murray Mouth",
                    "type": "Bar-Built",
                    "country": "Australia",
                    "description": "Bar-built estuary, mouth of Murray-Darling system",
                    "area_km2": 200,
                    "river": "Murray"
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [18.4333, -33.9167]},
                "properties": {
                    "name": "Table Bay",
                    "type": "Coastal Plain",
                    "country": "South Africa",
                    "description": "Natural harbor, open coastal embayment",
                    "area_km2": 88,
                    "depth_m": 20
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-43.1833, -22.9167]},
                "properties": {
                    "name": "Guanabara Bay",
                    "type": "Ria",
                    "country": "Brazil",
                    "description": "Drowned river valley, major urban harbor",
                    "area_km2": 412,
                    "depth_m": 30
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-57.9500, -34.8667]},
                "properties": {
                    "name": "Rio de la Plata",
                    "type": "Coastal Plain",
                    "country": "Argentina/Uruguay",
                    "description": "Widest estuary in the world, funnel-shaped",
                    "area_km2": 35000,
                    "depth_m": 5
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [139.7500, 35.6833]},
                "properties": {
                    "name": "Tokyo Bay",
                    "type": "Coastal Plain",
                    "country": "Japan",
                    "description": "Highly urbanized bay estuary, major port system",
                    "area_km2": 922,
                    "depth_m": 40
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [4.4167, 51.9167]},
                "properties": {
                    "name": "Rhine-Meuse-Scheldt Delta",
                    "type": "Delta",
                    "country": "Netherlands",
                    "description": "Complex delta system, highly engineered",
                    "area_km2": 4000,
                    "river": "Rhine, Meuse, Scheldt"
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-6.2000, 53.3500]},
                "properties": {
                    "name": "Dublin Bay",
                    "type": "Coastal Plain",
                    "country": "Ireland",
                    "description": "Shallow coastal embayment with extensive intertidal areas",
                    "area_km2": 125,
                    "depth_m": 10
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [144.9500, -37.8333]},
                "properties": {
                    "name": "Port Phillip Bay",
                    "type": "Ria",
                    "country": "Australia",
                    "description": "Large bay with narrow entrance, drowned valley",
                    "area_km2": 1930,
                    "depth_m": 24
                }
            }
        ]
    }
    
    return estuaries

def main():
    """Main function to process estuary data and generate GeoJSON output."""
    print("Processing estuary data...")
    
    # Create sample data (in production, would fetch from actual sources)
    estuary_data = create_sample_estuary_data()
    
    # Output to data directory
    output_path = '/home/runner/work/estuary-type-map/estuary-type-map/data/estuaries.geojson'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(estuary_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Generated {len(estuary_data['features'])} estuaries")
    print(f"✓ Output saved to: {output_path}")
    
    # Print summary statistics
    types = {}
    for feature in estuary_data['features']:
        estuary_type = feature['properties']['type']
        types[estuary_type] = types.get(estuary_type, 0) + 1
    
    print("\nEstuary types distribution:")
    for estuary_type, count in sorted(types.items()):
        print(f"  {estuary_type}: {count}")

if __name__ == '__main__':
    main()
