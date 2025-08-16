#!/usr/bin/env python3
"""
Example: Integrating Flask API with the Demo System
===================================================

This example shows how to use the Flask API alongside your existing demo system.
"""

import requests
import json
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:5001"

def api_generate_circuit(description, filename=None):
    """Generate circuit using the Flask API"""
    try:
        data = {"description": description}
        if filename:
            data["filename"] = filename
        
        response = requests.post(f"{API_BASE_URL}/api/generate", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Circuit generated successfully!")
            print(f"   Components detected: {result['components_detected']}")
            print(f"   Total parts: {result['total_parts']}")
            print(f"   Connections: {result['connections']}")
            
            return result['circuit_json']
        else:
            error = response.json()
            print(f"❌ Error: {error['error']}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ API server not running. Start it with: python start_api.py --port 5001")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def api_generate_progressive(description):
    """Generate progressive circuits using the Flask API"""
    try:
        data = {"description": description}
        
        response = requests.post(f"{API_BASE_URL}/api/progressive", json=data)
        
        if response.status_code == 200:
            # Save the ZIP file
            timestamp = int(time.time())
            filename = f"api_progressive_circuits_{timestamp}.zip"
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Progressive circuits generated and saved to {filename}")
            return filename
        else:
            error = response.json()
            print(f"❌ Error: {error['error']}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ API server not running. Start it with: python start_api.py --port 5001")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def api_parse_components(description):
    """Parse components from text using the Flask API"""
    try:
        data = {"description": description}
        
        response = requests.post(f"{API_BASE_URL}/api/parse", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Components parsed successfully!")
            print(f"   Components detected: {result['components_detected']}")
            
            for comp in result['components']:
                print(f"   - {comp['name']} ({comp['category']})")
            
            return result['components']
        else:
            error = response.json()
            print(f"❌ Error: {error['error']}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ API server not running. Start it with: python start_api.py --port 5001")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def demo_api_integration():
    """Demo showing API integration"""
    print("🔧 RAG AI Circuit Generator - API Integration Demo")
    print("=" * 60)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        if response.status_code == 200:
            print("API server is running")
        else:
            print("❌ API server is not responding")
            return
    except:
        print("❌ API server is not running. Start it with: python start_api.py --port 5001")
        return
    
    # Test descriptions
    test_cases = [
        "arduino uno with led and buzzer",
        "esp32 with oled display, button, and ultrasonic sensor",
        "arduino mega with rgb led, servo motor, and temperature sensor"
    ]
    
    for i, description in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {description}")
        print("-" * 40)
        
        # Parse components first
        print("📋 Parsing components...")
        components = api_parse_components(description)
        
        if components:
            # Generate single circuit
            print("\n🔌 Generating circuit...")
            circuit = api_generate_circuit(description, f"api_test_{i}.json")
            
            if circuit:
                # Save the circuit
                output_file = f"api_generated_circuit_{i}.json"
                with open(output_file, 'w') as f:
                    json.dump(circuit, f, indent=2)
                print(f"   💾 Circuit saved to {output_file}")
                
                # You can now use this circuit_json with your existing systems
                # For example, load it into Wokwi or use with your AutoGUI automation
                print(f"   🎯 Circuit ready for Wokwi or AutoGUI automation")
    
    # Generate progressive circuits for the first test case
    print(f"\n📚 Generating progressive circuits for: {test_cases[0]}")
    print("-" * 40)
    zip_file = api_generate_progressive(test_cases[0])
    
    if zip_file:
        print(f"   📦 Progressive circuits available in {zip_file}")
        print("   🎓 Extract and use individual step files for tutorials")

def compare_api_vs_direct():
    """Compare API vs direct function calls"""
    print("\n🔄 Comparing API vs Direct Function Calls")
    print("=" * 60)
    
    description = "arduino uno with led, buzzer, and oled display"
    
    # Direct method (existing)
    print("🔧 Using direct function calls...")
    try:
        from demo import parse_text_input
        from main import generate_circuit_diagram_json
        
        start_time = time.time()
        components = parse_text_input(description)
        circuit_json = generate_circuit_diagram_json(parts=components, save_to_file=None)
        direct_time = time.time() - start_time
        
        print(f"   ✅ Direct method completed in {direct_time:.2f}s")
        print(f"   📊 Generated circuit with {len(json.loads(circuit_json)['parts'])} parts")
        
    except Exception as e:
        print(f"   ❌ Direct method failed: {e}")
        direct_time = None
    
    # API method
    print("\n🌐 Using API calls...")
    start_time = time.time()
    circuit = api_generate_circuit(description)
    api_time = time.time() - start_time
    
    if circuit:
        print(f"   ✅ API method completed in {api_time:.2f}s")
        print(f"   📊 Generated circuit with {len(circuit['parts'])} parts")
        
        if direct_time:
            overhead = ((api_time - direct_time) / direct_time) * 100
            print(f"   📈 API overhead: {overhead:.1f}%")
    else:
        print("   ❌ API method failed")

def main():
    """Main demo function"""
    demo_api_integration()
    compare_api_vs_direct()
    
    print("\n🎉 Demo completed!")
    print("\nNext steps:")
    print("1. Open web_interface.html in your browser for interactive testing")
    print("2. Use the API endpoints in your own applications")
    print("3. Integrate with your AutoGUI automation scripts")
    print("4. Build web applications using the REST API")

if __name__ == "__main__":
    main()
