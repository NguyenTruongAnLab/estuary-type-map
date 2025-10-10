#!/usr/bin/env python3
"""
Test script to validate estuary GeoJSON data structure and content.
"""

import json
import sys
from pathlib import Path

def test_geojson_structure():
    """Test that GeoJSON file has valid structure."""
    print("Testing GeoJSON structure...")
    
    data_file = Path(__file__).parent.parent / 'data' / 'estuaries.geojson'
    
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ FAIL: estuaries.geojson not found")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ FAIL: Invalid JSON - {e}")
        return False
    
    # Check top-level structure
    if data.get('type') != 'FeatureCollection':
        print("❌ FAIL: Top-level type must be 'FeatureCollection'")
        return False
    
    if 'features' not in data:
        print("❌ FAIL: Missing 'features' array")
        return False
    
    print("✓ Valid GeoJSON FeatureCollection structure")
    return True

def test_basin_geojson_structure():
    """Test that basin polygon GeoJSON file has valid structure."""
    print("\nTesting Basin Polygon GeoJSON structure...")
    
    data_file = Path(__file__).parent.parent / 'data' / 'basins_simplified.geojson'
    
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ FAIL: basins_simplified.geojson not found")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ FAIL: Invalid JSON - {e}")
        return False
    
    # Check top-level structure
    if data.get('type') != 'FeatureCollection':
        print("❌ FAIL: Top-level type must be 'FeatureCollection'")
        return False
    
    if 'features' not in data:
        print("❌ FAIL: Missing 'features' array")
        return False
    
    print("✓ Valid Basin Polygon GeoJSON FeatureCollection structure")
    return True

def test_features():
    """Test that all features have required properties."""
    print("\nTesting features...")
    
    data_file = Path(__file__).parent.parent / 'data' / 'estuaries.geojson'
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    features = data['features']
    total = len(features)
    print(f"Found {total} estuaries")
    
    required_properties = ['name', 'type', 'type_detailed', 'type_code']
    valid_types = ['Delta', 'Fjord', 'Lagoon', 'Ria', 'Coastal Plain', 'Bar-Built', 'Tectonic', 'Unknown']
    
    errors = []
    
    for i, feature in enumerate(features, 1):
        # Check feature structure
        if feature.get('type') != 'Feature':
            errors.append(f"Feature {i}: Invalid type '{feature.get('type')}'")
        
        if 'geometry' not in feature:
            errors.append(f"Feature {i}: Missing geometry")
            continue
        
        geometry = feature['geometry']
        if geometry.get('type') != 'Point':
            errors.append(f"Feature {i}: Geometry must be 'Point', got '{geometry.get('type')}'")
        
        if 'coordinates' not in geometry:
            errors.append(f"Feature {i}: Missing coordinates")
        elif len(geometry['coordinates']) != 2:
            errors.append(f"Feature {i}: Coordinates must be [lng, lat]")
        else:
            lng, lat = geometry['coordinates']
            if not (-180 <= lng <= 180):
                errors.append(f"Feature {i}: Invalid longitude {lng}")
            if not (-90 <= lat <= 90):
                errors.append(f"Feature {i}: Invalid latitude {lat}")
        
        # Check properties
        if 'properties' not in feature:
            errors.append(f"Feature {i}: Missing properties")
            continue
        
        props = feature['properties']
        
        # Check required properties
        for prop in required_properties:
            if prop not in props:
                errors.append(f"Feature {i} ({props.get('name', 'Unknown')}): Missing '{prop}'")
        
        # Validate estuary type
        if 'type' in props and props['type'] not in valid_types:
            errors.append(f"Feature {i} ({props.get('name', 'Unknown')}): Invalid type '{props['type']}'")
    
    if errors:
        print("\n❌ FAILURES:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print(f"✓ All {total} features are valid")
    return True

def test_statistics():
    """Display statistics about the dataset."""
    print("\nDataset Statistics:")
    
    data_file = Path(__file__).parent.parent / 'data' / 'estuaries.geojson'
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    features = data['features']
    
    # Count by type
    type_counts = {}
    for feature in features:
        estuary_type = feature['properties'].get('type', 'Unknown')
        type_counts[estuary_type] = type_counts.get(estuary_type, 0) + 1
    
    print(f"\nTotal estuaries: {len(features)}")
    print("\nBy type:")
    for estuary_type in sorted(type_counts.keys()):
        count = type_counts[estuary_type]
        print(f"  {estuary_type}: {count}")
    
    # Count by continent (rough approximation by longitude)
    continents = {
        'Americas': 0,
        'Europe/Africa': 0,
        'Asia/Oceania': 0
    }
    
    for feature in features:
        lng = feature['geometry']['coordinates'][0]
        if -170 <= lng <= -30:
            continents['Americas'] += 1
        elif -30 < lng <= 60:
            continents['Europe/Africa'] += 1
        else:
            continents['Asia/Oceania'] += 1
    
    print("\nBy region (approximate):")
    for continent, count in continents.items():
        print(f"  {continent}: {count}")
    
    return True

def test_basin_features():
    """Test that all basin polygon features have required properties."""
    print("\nTesting basin polygon features...")
    
    data_file = Path(__file__).parent.parent / 'data' / 'basins_simplified.geojson'
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    features = data['features']
    total = len(features)
    print(f"Found {total} basin polygons")
    
    required_properties = ['name', 'type', 'type_detailed', 'type_code']
    valid_types = ['Delta', 'Fjord', 'Lagoon', 'Ria', 'Coastal Plain', 'Bar-Built', 'Tectonic', 'Unknown']
    valid_geometry_types = ['Polygon', 'MultiPolygon']
    
    errors = []
    
    for i, feature in enumerate(features, 1):
        # Check feature structure
        if feature.get('type') != 'Feature':
            errors.append(f"Basin {i}: Invalid type '{feature.get('type')}'")
        
        if 'geometry' not in feature:
            errors.append(f"Basin {i}: Missing geometry")
            continue
        
        geometry = feature['geometry']
        if geometry.get('type') not in valid_geometry_types:
            errors.append(f"Basin {i}: Geometry must be 'Polygon' or 'MultiPolygon', got '{geometry.get('type')}'")
        
        # Check properties
        if 'properties' not in feature:
            errors.append(f"Basin {i}: Missing properties")
            continue
        
        props = feature['properties']
        
        # Check required properties
        for prop in required_properties:
            if prop not in props:
                errors.append(f"Basin {i} ({props.get('name', 'Unknown')}): Missing '{prop}'")
        
        # Validate estuary type
        if 'type' in props and props['type'] not in valid_types:
            errors.append(f"Basin {i} ({props.get('name', 'Unknown')}): Invalid type '{props['type']}'")
    
    if errors:
        print("\n❌ FAILURES:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
        return False
    
    print(f"✓ All {total} basin polygon features are valid")
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Estuary GeoJSON Data Validation")
    print("=" * 60)
    
    all_passed = True
    
    # Run tests
    all_passed &= test_geojson_structure()
    all_passed &= test_features()
    all_passed &= test_statistics()
    all_passed &= test_basin_geojson_structure()
    all_passed &= test_basin_features()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
