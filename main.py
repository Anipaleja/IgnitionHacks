#!/usr/bin/env python3
"""
Simple RAG AI Circuit Diagram Generator
User inputs parts → RAG AI model outputs diagram.json

Usage:
    parts = [{"type": "wokwi-arduino-uno", "id": "uno", ...}, ...]
    diagram_json = generate_circuit_diagram_json(parts)
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class RAGCircuitGenerator:
    """Simple RAG AI circuit diagram generator"""
    
    def __init__(self):
        self.model_trainer = None
        self.load_rag_model()
    
    def load_rag_model(self):
        """Load the trained RAG AI model"""
        try:
            from comprehensive_model_trainer import ComprehensiveHardwareModelTrainer
            self.model_trainer = ComprehensiveHardwareModelTrainer()
            print("RAG AI model loaded")
        except:
            print("RAG model not available - using patterns")
            self.model_trainer = None
    
    def generate_diagram(self, parts: List[Dict[str, Any]]) -> str:
        """Generate complete diagram.json from parts"""
        
        if self.model_trainer:
            # Use Code Llama RAG AI model with enhanced prompt
            parts_list = []
            for p in parts:
                parts_list.append(f"- {p['id']}: {p['type']} at position (top: {p.get('top', 0)}, left: {p.get('left', 0)})")
            
            parts_text = "\n".join(parts_list)
            
            prompt = f"""Create a complete Wokwi circuit diagram JSON for these components:

{parts_text}

Requirements:
1. Include the provided parts array exactly as given
2. Generate proper electrical connections between components
3. Use realistic wire colors (red=power, black=ground, other colors for signals)
4. Include wire routing paths using format: ["v10", "h20", "*", "v-5"] for clean layout
5. Follow standard electronic wiring conventions
6. Ensure all components are properly connected and functional

Return ONLY the complete JSON with this exact structure:
{{
  "version": 1,
  "author": "Code Llama Circuit Generator",
  "editor": "wokwi",
  "parts": [the exact parts array provided],
  "connections": [
    ["source_pin", "target_pin", "wire_color", ["wire_routing_path"]],
    ...
  ],
  "dependencies": {{}}
}}"""

            response = self.model_trainer.generate_response(prompt)
            
            # Try to extract JSON from response
            try:
                if "{" in response and "}" in response:
                    start = response.find("{")
                    end = response.rfind("}") + 1
                    json_text = response[start:end]
                    # Validate JSON
                    parsed = json.loads(json_text)
                    return json.dumps(parsed, indent=2)
            except:
                pass
        
        # Fallback: use simple patterns
        return self.generate_with_patterns(parts)
    
    def generate_with_patterns(self, parts: List[Dict[str, Any]]) -> str:
        """Fallback pattern-based generation with proper wire routing"""
        
        # Find MCU
        mcu = None
        for part in parts:
            if any(x in part['type'].lower() for x in ['arduino', 'esp32', 'mega', 'nano']):
                mcu = part
                break
        
        if not mcu:
            return json.dumps({"error": "No MCU found"}, indent=2)
        
        connections = []
        pin_idx = 2  # Start from pin 2
        
        for part in parts:
            if part == mcu:
                continue
                
            part_type = part['type'].lower()
            part_id = part['id']
            mcu_id = mcu['id']
            
            # Calculate wire paths based on component positions
            wire_paths = self.calculate_wire_paths(mcu, part)
            
            # Pattern matching with proper wire routing
            if 'ssd1306' in part_type or 'oled' in part_type:
                connections.extend([
                    [f"{mcu_id}:GND.1", f"{part_id}:GND", "black", wire_paths['power']],
                    [f"{mcu_id}:3.3V", f"{part_id}:VCC", "red", wire_paths['power_alt']],
                    [f"{mcu_id}:A4", f"{part_id}:SDA", "gold", wire_paths['analog1']],
                    [f"{mcu_id}:A5", f"{part_id}:SCL", "cyan", wire_paths['analog2']]
                ])
            elif 'ili9341' in part_type or 'tft' in part_type:
                if 'esp32' in mcu['type'].lower():
                    # ESP32 pins for ILI9341
                    connections.extend([
                        [f"{mcu_id}:GND.2", f"{part_id}:GND", "black", ["h-19.2", "v91.54"]],
                        [f"{mcu_id}:5V", f"{part_id}:VCC", "red", ["h-21.83", "v-206.3", "h201.6", "v48.5"]],
                        [f"{mcu_id}:15", f"{part_id}:CS", "violet", ["h-57.6", "v105.6"]],
                        [f"{mcu_id}:4", f"{part_id}:RST", "purple", ["h-48", "v67.2"]],
                        [f"{mcu_id}:2", f"{part_id}:D/C", "#8f4814", ["h-28.8", "v44.14"]],
                        [f"{mcu_id}:18", f"{part_id}:SCK", "gray", ["v-0.01", "h-48", "v-19.2"]],
                        [f"{mcu_id}:19", f"{part_id}:MISO", "orange", ["h-67.2", "v-9.61", "h0", "v-19.2"]],
                        [f"{mcu_id}:23", f"{part_id}:MOSI", "green", ["h-38.4", "v-67.31"]]
                    ])
                else:
                    # Arduino Mega pins for ILI9341
                    connections.extend([
                        [f"{mcu_id}:GND.1", f"{part_id}:GND", "black", ["v-50", "*", "v30"]],
                        [f"{mcu_id}:5V", f"{part_id}:VCC", "red", ["v30", "*", "v-30"]],
                        [f"{mcu_id}:53", f"{part_id}:CS", "violet", ["v-60", "*", "h20"]],
                        [f"{mcu_id}:49", f"{part_id}:RESET", "purple", ["v-65", "*", "h20"]],
                        [f"{mcu_id}:48", f"{part_id}:DC", "#8f4814", ["v-70", "*", "h20"]],
                        [f"{mcu_id}:51", f"{part_id}:MOSI", "green", ["v-75", "*", "h30"]],
                        [f"{mcu_id}:50", f"{part_id}:MISO", "orange", ["v-80", "*", "h30"]],
                        [f"{mcu_id}:52", f"{part_id}:SCK", "gray", ["v-85", "*", "h30"]]
                    ])
            elif 'microsd' in part_type or 'sd' in part_type:
                connections.extend([
                    [f"{mcu_id}:GND.2", f"{part_id}:GND", "black", ["v50", "*", "v-20"]],
                    [f"{mcu_id}:5V", f"{part_id}:VCC", "red", ["v40", "*", "v-20"]],
                    [f"{mcu_id}:10", f"{part_id}:CS", "blue", ["v35", "*", "v-20"]],
                    [f"{mcu_id}:51", f"{part_id}:MOSI", "green", ["v-5", "*", "h10"]],
                    [f"{mcu_id}:50", f"{part_id}:MISO", "orange", ["v-10", "*", "h10"]],
                    [f"{mcu_id}:52", f"{part_id}:SCK", "gray", ["v-15", "*", "h10"]]
                ])
            elif 'pushbutton' in part_type or 'button' in part_type:
                if 'esp32' in mcu['type'].lower():
                    connections.extend([
                        [f"{mcu_id}:5", f"{part_id}:1.l", "green", ["h19.2", "v96"]],
                        [f"{mcu_id}:GND.2", f"{part_id}:2.l", "black", ["h76.8", "v201.4"]]
                    ])
                else:
                    connections.extend([
                        [f"{mcu_id}:{pin_idx}", f"{part_id}:1.l", "green", ["v-25", "h45", "*", "v30"]],
                        [f"{mcu_id}:GND.1", f"{part_id}:2.l", "black", ["v-20", "*", "v25"]]
                    ])
                pin_idx += 1
            elif 'buzzer' in part_type:
                connections.extend([
                    [f"{mcu_id}:GND.3", f"{part_id}:1", "black", ["v60", "*", "v-10"]],
                    [f"{mcu_id}:47", f"{part_id}:2", "purple", ["v55", "*", "v-10"]]
                ])
            elif 'led' in part_type:
                connections.extend([
                    [f"{mcu_id}:{pin_idx}", f"{part_id}:A", "red", wire_paths['digital1']],
                    [f"{mcu_id}:GND.1", f"{part_id}:C", "black", wire_paths['power']]
                ])
                pin_idx += 1
            elif 'resistor' in part_type:
                # Resistors are usually connected inline, but for demo purposes
                # we'll connect them between power and a digital pin
                connections.extend([
                    [f"{mcu_id}:{pin_idx}", f"{part_id}:1", "yellow", wire_paths['digital1']],
                    [f"{mcu_id}:{pin_idx+1}", f"{part_id}:2", "orange", wire_paths['digital2']]
                ])
                pin_idx += 2
            elif 'dht' in part_type or 'temperature' in part_type:
                connections.extend([
                    [f"{mcu_id}:GND.1", f"{part_id}:GND", "black", wire_paths['power']],
                    [f"{mcu_id}:5V", f"{part_id}:VCC", "red", wire_paths['power_alt']],
                    [f"{mcu_id}:{pin_idx}", f"{part_id}:SDA", "blue", wire_paths['digital1']]
                ])
                pin_idx += 1
            else:
                # Default wiring for unknown components
                connections.extend([
                    [f"{mcu_id}:GND.1", f"{part_id}:GND", "black", wire_paths['power']],
                    [f"{mcu_id}:{pin_idx}", f"{part_id}:SIG", "gray", wire_paths['digital1']]
                ])
                pin_idx += 1
        
        return self.finalize_diagram(parts, connections)
    
    def calculate_wire_paths(self, mcu: Dict[str, Any], component: Dict[str, Any]) -> Dict[str, List[str]]:
        """Calculate optimized wire paths based on component positions"""
        
        mcu_top = mcu.get('top', 0)
        mcu_left = mcu.get('left', 0)
        comp_top = component.get('top', 0)
        comp_left = component.get('left', 0)
        
        # Calculate relative positions
        v_offset = int((comp_top - mcu_top) * 0.3)  # Scale down for wire routing
        h_offset = int((comp_left - mcu_left) * 0.2)
        
        # Generate different path patterns to avoid overlaps
        paths = {
            'power': [f"v{v_offset}", "*", f"v{-v_offset//2}"],
            'power_alt': [f"v{v_offset-10}", "*", f"v{-v_offset//2+5}"],
            'analog1': [f"v{v_offset-20}", f"h{h_offset//2}", "*", f"v{-v_offset//3}"],
            'analog2': [f"v{v_offset-25}", f"h{h_offset//3}", "*", f"v{-v_offset//4}"],
            'digital1': [f"v{v_offset-30}", f"h{h_offset//4}", "*", f"h{-h_offset//8}", f"v{-v_offset//5}"],
            'digital2': [f"v{v_offset-35}", f"h{h_offset//5}", "*", f"h{-h_offset//10}", f"v{-v_offset//6}"]
        }
        
        return paths
    
    def finalize_diagram(self, parts: List[Dict[str, Any]], connections: List) -> str:
        """Create the final diagram JSON"""
        diagram = {
            "version": 1,
            "author": "RAG AI Generator",
            "editor": "wokwi",
            "parts": parts,
            "connections": connections,
            "dependencies": {}
        }
        
        return json.dumps(diagram, indent=2)

# Main function - this is what the user calls
def generate_circuit_diagram_json(parts: List[Dict[str, Any]], save_to_file: str = "diagram.json") -> str:
    """
    Simple function: parts in → diagram.json out
    
    Args:
        parts: Array of circuit parts
        save_to_file: Filename to save the diagram (default: "diagram.json", set to None to skip saving)
        
    Returns:
        Complete diagram.json as string
    """
    generator = RAGCircuitGenerator()
    diagram_json = generator.generate_diagram(parts)
    
    if save_to_file:
        # Save to specified filename
        with open(save_to_file, 'w') as f:
            f.write(diagram_json)
        print(f"Saved diagram to {save_to_file} file")
    
    return diagram_json

# Test the generator
if __name__ == "__main__":
    # Example: User inputs parts (your exact example)
    parts = [
        {
            "type": "wokwi-arduino-mega",
            "id": "mega",
            "top": 272.86,
            "left": -34.52,
            "attrs": {"__fakeRamSize": "65000"}
        },
        {
            "type": "board-ili9341-cap-touch",
            "id": "lcd1",
            "top": -149.52,
            "left": 75.06,
            "attrs": {}
        },
        {
            "type": "wokwi-microsd-card",
            "id": "sd1",
            "top": 39.23,
            "left": 395.41,
            "rotate": 90,
            "attrs": {}
        },
        {
            "type": "wokwi-buzzer",
            "id": "bz1",
            "top": 481.7,
            "left": 153.47,
            "attrs": {"volume": "0.025"}
        }
    ]
    
    # RAG AI generates diagram.json with proper wire placement
    diagram_json = generate_circuit_diagram_json(parts)
    print("Generated diagram.json with proper wire placement:")
    print(diagram_json)
