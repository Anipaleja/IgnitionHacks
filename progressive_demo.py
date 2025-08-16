#!/usr/bin/env python3
"""
Progressive Circuit Generation Demo
Shows how circuit diagrams build up component by component
"""

import json
import sys
from pathlib import Path

# Add the main directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import generate_circuit_diagram_json

def progressive_circuit_demo():
    """Generate circuit diagrams progressively, one component at a time"""
    
    print("🔧 PROGRESSIVE CIRCUIT GENERATION DEMO")
    print("=" * 60)
    print("Building circuit step by step, component by component...")
    print()
    
    # Define all components
    all_components = [
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
    
    # Generate circuit for each progressive step
    for step in range(1, len(all_components) + 1):
        current_parts = all_components[:step]
        
        print(f"📡 STEP {step}: Adding component {step}")
        print("-" * 40)
        
        # Show current components
        for i, part in enumerate(current_parts, 1):
            component_name = part['type'].replace('wokwi-', '').replace('-', ' ').title()
            marker = "🆕" if i == step else "✅"
            print(f"   {marker} {component_name} ({part['id']})")
        
        print()
        
        # Generate the circuit
        filename = f"step_{step}_circuit.json"
        try:
            diagram_json = generate_circuit_diagram_json(current_parts, filename)
            diagram = json.loads(diagram_json)
            
            connections = diagram.get('connections', [])
            
            print(f"📊 Generated {len(connections)} connections:")
            
            if len(connections) == 0:
                print("   (No connections - only MCU)")
            else:
                # Group connections by target component
                component_connections = {}
                for conn in connections:
                    target_comp = conn[1].split(':')[0]
                    if target_comp not in component_connections:
                        component_connections[target_comp] = []
                    component_connections[target_comp].append(conn)
                
                for comp_name, conns in component_connections.items():
                    if comp_name != all_components[0]['id']:  # Don't show MCU as target
                        comp_type = next((p['type'] for p in current_parts if p['id'] == comp_name), comp_name)
                        clean_name = comp_type.replace('wokwi-', '').replace('-', ' ').title()
                        print(f"   🔗 {clean_name} ({comp_name}):")
                        
                        for conn in conns:
                            source_pin = conn[0].split(':')[1]
                            target_pin = conn[1].split(':')[1]
                            wire_color = conn[2]
                            print(f"      • Pin {source_pin} → {target_pin} ({wire_color} wire)")
            
            print(f"   💾 Saved as: {filename}")
            
        except Exception as e:
            print(f"   ❌ Error generating step {step}: {e}")
        
        print()
        print("=" * 60)
        print()

def show_final_summary():
    """Show a summary of all generated files"""
    print("📋 GENERATED FILES SUMMARY:")
    print("=" * 40)
    
    for step in range(1, 6):
        filename = f"step_{step}_circuit.json"
        try:
            with open(filename, 'r') as f:
                diagram = json.loads(f.read())
            
            parts_count = len(diagram.get('parts', []))
            connections_count = len(diagram.get('connections', []))
            
            print(f"Step {step}: {filename}")
            print(f"   Components: {parts_count}, Connections: {connections_count}")
        except FileNotFoundError:
            print(f"Step {step}: {filename} (not found)")
        except Exception as e:
            print(f"Step {step}: {filename} (error: {e})")
    
    print()
    print("🎯 You can now open each file to see how the circuit builds up!")

if __name__ == "__main__":
    progressive_circuit_demo()
    show_final_summary()
