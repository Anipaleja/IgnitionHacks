#!/usr/bin/env python3
"""
Fix wire visibility issues by using simpler routing and standard colors
"""

import json

def fix_wire_visibility(input_file, output_file):
    """Fix wire visibility issues"""
    
    with open(input_file, 'r') as f:
        diagram = json.loads(f.read())
    
    # Standard Wokwi colors that are clearly visible
    color_map = {
        'black': 'black',
        'red': 'red', 
        'gold': 'yellow',  # Gold might not show well, use yellow
        'cyan': 'blue',    # Cyan might not show well, use blue
        'blue': 'green',   # Change blue to green to avoid conflicts
        'purple': 'purple',
        'orange': 'orange',
        'violet': 'violet'
    }
    
    # Fix connections with better routing and colors
    fixed_connections = []
    
    for conn in diagram['connections']:
        source, target, color, path = conn
        
        # Use standard color
        new_color = color_map.get(color, color)
        
        # Simplify wire routing - use more visible paths
        if len(path) > 1:
            # Create simpler, more visible paths
            new_path = ["h20", "v20", "*", "v-10", "h-10"]
        else:
            new_path = ["*"]  # Direct connection
        
        fixed_connections.append([source, target, new_color, new_path])
    
    # Update the diagram
    diagram['connections'] = fixed_connections
    diagram['author'] = "Fixed Wire Visibility"
    
    # Save the fixed version
    with open(output_file, 'w') as f:
        json.dump(diagram, f, indent=2)
    
    return diagram

def show_wire_analysis(filename):
    """Analyze wire connections for visibility issues"""
    
    with open(filename, 'r') as f:
        diagram = json.loads(f.read())
    
    print(f"🔍 WIRE ANALYSIS FOR {filename}")
    print("=" * 50)
    
    connections = diagram.get('connections', [])
    
    if not connections:
        print("❌ No connections found!")
        return
    
    # Count colors
    color_count = {}
    for conn in connections:
        color = conn[2]
        color_count[color] = color_count.get(color, 0) + 1
    
    print(f"📊 Total connections: {len(connections)}")
    print(f"🎨 Wire colors used:")
    
    for color, count in color_count.items():
        print(f"   • {color}: {count} wire(s)")
    
    print("\n🔗 All connections:")
    for i, conn in enumerate(connections, 1):
        source, target, color, path = conn
        path_str = " → ".join(path) if len(path) > 1 else "direct"
        print(f"   {i:2d}. {source:15} → {target:15} ({color:8}) [{path_str}]")

# Fix the step 3 circuit
if __name__ == "__main__":
    print("🔧 FIXING WIRE VISIBILITY ISSUES")
    print("=" * 50)
    
    # Analyze original
    show_wire_analysis("step_3_circuit.json")
    
    print("\n" + "=" * 50)
    print("🛠️ CREATING FIXED VERSION")
    print("=" * 50)
    
    # Create fixed version
    fixed_diagram = fix_wire_visibility("step_3_circuit.json", "step_3_fixed.json")
    
    print("✅ Created fixed version: step_3_fixed.json")
    
    # Analyze fixed version
    print()
    show_wire_analysis("step_3_fixed.json")
    
    print("\n🎯 Try loading 'step_3_fixed.json' in Wokwi - wires should be more visible!")
