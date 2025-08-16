#!/usr/bin/env python3
"""
Demo script showing Gemini API integration setup and usage
"""

import os
import sys
from pathlib import Path

def show_setup_instructions():
    """Show step-by-step setup instructions"""
    print("GEMINI API SETUP GUIDE")
    print("=" * 50)
    print()
    print("1. Get your Gemini API key:")
    print("   Visit: https://aistudio.google.com/app/apikey")
    print("   Create a new API key (starts with 'AIza...')")
    print()
    print("2. Set up the API key (choose one method):")
    print()
    print("   METHOD A - Environment Variable:")
    print("   export GEMINI_API_KEY='your_api_key_here'")
    print()
    print("   METHOD B - .env file:")
    print("   echo 'GEMINI_API_KEY=your_api_key_here' > .env")
    print()
    print("3. Test the integration:")
    print("   python test_gemini_integration.py")
    print()
    print("4. Use in your code:")
    print("   from main import generate_circuit_diagram_json")
    print("   diagram = generate_circuit_diagram_json(parts)")
    print()

def demo_with_api_key():
    """Demo the system with an API key"""
    print("GEMINI-ENHANCED CIRCUIT GENERATION DEMO")
    print("=" * 50)
    
    # Import our main module
    sys.path.insert(0, str(Path(__file__).parent))
    from main import generate_circuit_diagram_json
    
    # Example: Smart home sensor hub
    smart_home_parts = [
        {
            "type": "wokwi-esp32-devkit-v1",
            "id": "esp32",
            "top": 200,
            "left": 100,
            "attrs": {}
        },
        {
            "type": "wokwi-ssd1306",
            "id": "oled",
            "top": 50,
            "left": 300,
            "attrs": {}
        },
        {
            "type": "wokwi-dht22", 
            "id": "temp_sensor",
            "top": 150,
            "left": 400,
            "attrs": {}
        },
        {
            "type": "wokwi-pushbutton",
            "id": "mode_btn",
            "top": 300,
            "left": 300,
            "attrs": {}
        },
        {
            "type": "wokwi-led",
            "id": "status_led",
            "top": 350,
            "left": 400,
            "attrs": {"color": "green"}
        }
    ]
    
    print("Creating smart home sensor hub with:")
    for part in smart_home_parts:
        component_name = part['type'].replace('wokwi-', '').replace('-', ' ').title()
        print(f"   • {component_name} ({part['id']})")
    
    print("\nProcessing with RAG AI + Gemini double-check...")
    
    try:
        result = generate_circuit_diagram_json(smart_home_parts, "smart_home_demo.json")
        
        import json
        diagram = json.loads(result)
        
        print("Circuit generated successfully!")
        print(f"Created {len(diagram['connections'])} electrical connections")
        print("Saved as: smart_home_demo.json")
        
        # Show key connections
        print("\nKey connections generated:")
        connection_types = {}
        for conn in diagram['connections']:
            wire_color = conn[2]
            if wire_color not in connection_types:
                connection_types[wire_color] = []
            connection_types[wire_color].append(f"{conn[0]} → {conn[1]}")
        
        for color, connections in list(connection_types.items())[:3]:  # Show first 3 colors
            print(f"   {color.upper()} wires: {len(connections)} connections")
            for conn in connections[:2]:  # Show first 2 of each color
                print(f"     • {conn}")
            if len(connections) > 2:
                print(f"     • ... and {len(connections) - 2} more")
        
        # Check if Gemini was used
        if diagram.get('author') == 'Gemini Enhanced Circuit Generator':
            print("\nEnhanced by Gemini API for maximum accuracy!")
        else:
            print("\nGenerated with pattern-based system (add Gemini API for enhancement)")
            
        print("\nDemo completed! Check smart_home_demo.json for the full circuit.")
        
    except Exception as e:
        print(f"Demo failed: {e}")
        return False
    
    return True

def main():
    """Main demo function"""
    print("Welcome to the Enhanced Circuit Generator!")
    print()
    
    # Load .env file manually for this demo
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")
    
    # Check if API key is available
    if os.getenv('GEMINI_API_KEY'):
        print("Gemini API key detected - running enhanced demo")
        print()
        demo_with_api_key()
    else:
        print("No Gemini API key found")
        print()
        show_setup_instructions()
        print("After setting up your API key, run this demo again to see the enhanced features!")

if __name__ == "__main__":
    main()
