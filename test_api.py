#!/usr/bin/env python3
"""
Test script for the Flask API
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5001"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_parse():
    """Test component parsing"""
    print("\nTesting component parsing...")
    try:
        data = {
            "description": "arduino uno, led, buzzer, oled display"
        }
        response = requests.post(f"{BASE_URL}/api/parse", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Components detected: {result.get('components_detected', 0)}")
        for comp in result.get('components', []):
            print(f"  - {comp['name']} ({comp['type']})")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_generate():
    """Test circuit generation"""
    print("\nTesting circuit generation...")
    try:
        data = {
            "description": "arduino uno with led and buzzer",
            "filename": "test_circuit.json"
        }
        response = requests.post(f"{BASE_URL}/api/generate", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        if response.status_code == 200:
            print(f"Components detected: {result.get('components_detected', 0)}")
            print(f"Total parts: {result.get('total_parts', 0)}")
            print(f"Connections: {result.get('connections', 0)}")
            
            # Save the generated circuit to a file
            with open('test_api_output.json', 'w') as f:
                json.dump(result['circuit_json'], f, indent=2)
            print("Circuit saved to test_api_output.json")
        else:
            print(f"Error: {result}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_components():
    """Test generation from explicit components"""
    print("\nTesting generation from components...")
    try:
        data = {
            "components": [
                {"type": "wokwi-arduino-uno", "id": "mcu"},
                {"type": "wokwi-led", "id": "led1"},
                {"type": "wokwi-buzzer", "id": "buzzer1"}
            ]
        }
        response = requests.post(f"{BASE_URL}/api/components", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        if response.status_code == 200:
            print(f"Total parts: {result.get('total_parts', 0)}")
            print(f"Connections: {result.get('connections', 0)}")
        else:
            print(f"Error: {result}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def run_tests():
    """Run all API tests"""
    print("=== Flask API Test Suite ===")
    
    # Wait a moment for server to start
    print("Waiting for server to start...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health),
        ("Component Parsing", test_parse),
        ("Circuit Generation", test_generate),
        ("Component-based Generation", test_components)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        success = test_func()
        results.append((test_name, success))
        print(f"Result: {'PASS' if success else 'FAIL'}")
    
    print(f"\n{'='*50}")
    print("TEST SUMMARY:")
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  {test_name}: {status}")
    
    total_passed = sum(1 for _, success in results if success)
    print(f"\nPassed: {total_passed}/{len(results)}")

if __name__ == "__main__":
    run_tests()
