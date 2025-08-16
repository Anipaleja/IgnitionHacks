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
import os
import requests
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class RAGCircuitGenerator:
    """Simple RAG AI circuit diagram generator"""
    
    def __init__(self):
        self.model_trainer = None
        self.load_env_file()  # Load environment variables
        self.gemini_api_key = os.getenv('AIzaSyBovE7s8MkNa9E4edP_IXM3IVxEzpEAvy4')
        self.load_rag_model()
    
    def load_env_file(self):
        """Load environment variables from .env file if it exists"""
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
    
    def load_rag_model(self):
        """Load the trained RAG AI model"""
        try:
            from comprehensive_model_trainer import ComprehensiveHardwareModelTrainer
            self.model_trainer = ComprehensiveHardwareModelTrainer()
            print("🤖 RAG AI model loaded successfully")
        except Exception as e:
            print(f"⚠️ RAG model not available - using pattern-based generation")
            print(f"   Reason: {str(e)[:100]}...")
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

CRITICAL WIRING REQUIREMENTS:
1. Use ACCURATE pin assignments for each microcontroller type:
   - Arduino Uno: SPI (MOSI=11, MISO=12, SCK=13), I2C (SDA=A4, SCL=A5)
   - Arduino Mega: SPI (MOSI=51, MISO=50, SCK=52), I2C (SDA=20, SCL=21)
   - ESP32: SPI (MOSI=23, MISO=19, SCK=18), I2C (SDA=21, SCL=22)

2. Follow STANDARD component pin names:
   - ILI9341 TFT: VCC, GND, CS, RESET, DC, MOSI, MISO, SCK
   - OLED SSD1306: VCC, GND, SDA, SCL
   - MicroSD: VCC, GND, CS, MOSI, MISO, SCK
   - Push buttons: 1.l, 2.l (with pullup to digital pin, pulldown to GND)
   - LEDs: A (anode), C (cathode)
   - Buzzers: 1 (GND), 2 (signal)

3. Use PROPER wire colors:
   - Red: Power (5V/3.3V)
   - Black: Ground (GND)
   - Standard colors for signals: Green, Blue, Yellow, Orange, Purple, etc.

4. Generate CLEAN wire routing with minimal crossings:
   - Use format: ["v10", "h20", "*", "v-5"] where * is connection point
   - Avoid complex routing unless necessary

5. NO PIN CONFLICTS - each pin used only once

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
                    
                    # Double-check with Gemini API if available
                    if self.gemini_api_key:
                        enhanced_json = self.gemini_double_check(json_text, parts)
                        if enhanced_json:
                            return enhanced_json
                    
                    return json.dumps(parsed, indent=2)
            except:
                pass
        
        # Fallback: use simple patterns
        pattern_result = self.generate_with_patterns(parts)
        
        # Double-check pattern result with Gemini API if available
        if self.gemini_api_key:
            enhanced_result = self.gemini_double_check(pattern_result, parts)
            if enhanced_result:
                return enhanced_result
        
        return pattern_result
    
    def gemini_double_check(self, initial_diagram_json: str, parts: List[Dict[str, Any]]) -> str:
        """Use Gemini API to double-check and enhance the circuit diagram"""
        
        if not self.gemini_api_key:
            print("No Gemini API key found - skipping double-check")
            return None
            
        try:
            # Parse the initial diagram to understand the components
            initial_diagram = json.loads(initial_diagram_json)
            
            # Create component summary for Gemini
            parts_summary = []
            for part in parts:
                parts_summary.append(f"- {part['id']}: {part['type']}")
            
            connections_summary = []
            if 'connections' in initial_diagram:
                for conn in initial_diagram['connections']:
                    connections_summary.append(f"  {conn[0]} → {conn[1]} ({conn[2]} wire)")
            
            gemini_prompt = f"""As an expert electronics engineer, please review and enhance this Wokwi circuit diagram JSON.

COMPONENTS:
{chr(10).join(parts_summary)}

CURRENT CONNECTIONS:
{chr(10).join(connections_summary)}

CURRENT JSON:
{initial_diagram_json}

CRITICAL - Use EXACT Wokwi pin names (DO NOT change these):
- ESP32: GND.1, GND.2, 3.3V, 5V, pins 2,4,5,18,19,21,22,23 etc.
- LEDs: A (anode), C (cathode) - NEVER change to K
- Buttons: 1.l, 2.l (with .l suffix)
- OLED SSD1306: VCC, GND, SDA, SCL
- DHT22: VCC, GND, SDA (for data pin)

Please analyze and improve:
1. WIRING ACCURACY: Verify all pin assignments are correct
2. ELECTRICAL SAFETY: Check for proper power/ground connections  
3. FUNCTIONALITY: Ensure connections will work in real hardware
4. PIN CONFLICTS: Verify no MCU pins are used twice
5. WIRE ROUTING: Optimize paths but keep pin names EXACTLY as shown

Requirements:
- Keep the exact same parts array
- Use EXACT Wokwi component pin names (don't change working pin names)
- Follow proper electrical conventions (red=power, black=ground)
- Use realistic wire routing paths: ["v10", "h20", "*", "v-5"]
- Ensure all SPI devices share MOSI/MISO/SCK but have unique CS pins
- I2C devices should share SDA/SCL lines

Return ONLY the improved JSON in this exact format:
{{
  "version": 1,
  "author": "Gemini Enhanced Circuit Generator",
  "editor": "wokwi",
  "parts": [original parts array],
  "connections": [enhanced connections with correct pin names],
  "dependencies": {{}}
}}"""

            # Call Gemini API
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.gemini_api_key}"
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": gemini_prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.1,  # Low temperature for more consistent results
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 4096,
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    gemini_text = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # Extract JSON from Gemini response
                    if "{" in gemini_text and "}" in gemini_text:
                        start = gemini_text.find("{")
                        end = gemini_text.rfind("}") + 1
                        enhanced_json_text = gemini_text[start:end]
                        
                        # Validate the enhanced JSON
                        try:
                            enhanced_diagram = json.loads(enhanced_json_text)
                            
                            # Verify it has the required structure
                            if ('parts' in enhanced_diagram and 
                                'connections' in enhanced_diagram and
                                len(enhanced_diagram['parts']) == len(parts)):
                                
                                print("✅ Gemini API enhanced the circuit diagram")
                                return json.dumps(enhanced_diagram, indent=2)
                            else:
                                print("⚠️ Gemini response invalid structure - using original")
                                
                        except json.JSONDecodeError:
                            print("⚠️ Gemini response not valid JSON - using original")
                else:
                    print("⚠️ No valid Gemini response - using original")
            else:
                print(f"⚠️ Gemini API error {response.status_code} - using original")
                
        except requests.exceptions.Timeout:
            print("⚠️ Gemini API timeout - using original")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Gemini API request failed: {e} - using original")
        except Exception as e:
            print(f"⚠️ Gemini double-check failed: {e} - using original")
            
        return None  # Return None to use original
    
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
        used_pins = set()  # Track used pins to avoid conflicts
        pin_allocator = self.get_pin_allocator(mcu['type'])
        
        for part in parts:
            if part == mcu:
                continue
                
            part_type = part['type'].lower()
            part_id = part['id']
            mcu_id = mcu['id']
            
            # Calculate wire paths based on component positions
            wire_paths = self.calculate_wire_paths(mcu, part)
            
            # Pattern matching with accurate pin assignments
            if 'ssd1306' in part_type or 'oled' in part_type:
                # I2C OLED Display - uses SDA/SCL pins
                sda_pin = pin_allocator.get_i2c_sda()
                scl_pin = pin_allocator.get_i2c_scl()
                power_pin = pin_allocator.get_power_3v3() or pin_allocator.get_power_5v()
                gnd_pin = pin_allocator.get_ground()
                
                connections.extend([
                    [f"{mcu_id}:{gnd_pin}", f"{part_id}:GND", "black", wire_paths['power']],
                    [f"{mcu_id}:{power_pin}", f"{part_id}:VCC", "red", wire_paths['power_alt']],
                    [f"{mcu_id}:{sda_pin}", f"{part_id}:SDA", "gold", wire_paths['analog1']],
                    [f"{mcu_id}:{scl_pin}", f"{part_id}:SCL", "cyan", wire_paths['analog2']]
                ])
                
            elif 'ili9341' in part_type or 'tft' in part_type:
                # SPI TFT Display - requires multiple pins
                spi_pins = pin_allocator.get_spi_pins()
                cs_pin = pin_allocator.get_next_digital()
                rst_pin = pin_allocator.get_next_digital()
                dc_pin = pin_allocator.get_next_digital()
                power_pin = pin_allocator.get_power_5v()
                gnd_pin = pin_allocator.get_ground()
                
                connections.extend([
                    [f"{mcu_id}:{gnd_pin}", f"{part_id}:GND", "black", wire_paths['power']],
                    [f"{mcu_id}:{power_pin}", f"{part_id}:VCC", "red", wire_paths['power_alt']],
                    [f"{mcu_id}:{cs_pin}", f"{part_id}:CS", "violet", wire_paths['digital1']],
                    [f"{mcu_id}:{rst_pin}", f"{part_id}:RESET", "purple", wire_paths['digital2']],
                    [f"{mcu_id}:{dc_pin}", f"{part_id}:DC", "#8f4814", wire_paths['analog1']],
                    [f"{mcu_id}:{spi_pins['mosi']}", f"{part_id}:MOSI", "green", wire_paths['analog2']],
                    [f"{mcu_id}:{spi_pins['miso']}", f"{part_id}:MISO", "orange", wire_paths['digital_alt1']],
                    [f"{mcu_id}:{spi_pins['sck']}", f"{part_id}:SCK", "gray", wire_paths['digital_alt2']]
                ])
                
            elif 'microsd' in part_type or 'sd' in part_type:
                # SD Card Module - SPI interface
                spi_pins = pin_allocator.get_spi_pins()
                cs_pin = pin_allocator.get_next_digital()
                power_pin = pin_allocator.get_power_5v()
                gnd_pin = pin_allocator.get_ground()
                
                connections.extend([
                    [f"{mcu_id}:{gnd_pin}", f"{part_id}:GND", "black", wire_paths['power']],
                    [f"{mcu_id}:{power_pin}", f"{part_id}:VCC", "red", wire_paths['power_alt']],
                    [f"{mcu_id}:{cs_pin}", f"{part_id}:CS", "blue", wire_paths['digital1']],
                    [f"{mcu_id}:{spi_pins['mosi']}", f"{part_id}:MOSI", "green", wire_paths['digital2']],
                    [f"{mcu_id}:{spi_pins['miso']}", f"{part_id}:MISO", "orange", wire_paths['analog1']],
                    [f"{mcu_id}:{spi_pins['sck']}", f"{part_id}:SCK", "gray", wire_paths['analog2']]
                ])
                
            elif 'pushbutton' in part_type or 'button' in part_type:
                # Push button with pull-up resistor configuration
                digital_pin = pin_allocator.get_next_digital()
                gnd_pin = pin_allocator.get_ground()
                
                connections.extend([
                    [f"{mcu_id}:{digital_pin}", f"{part_id}:1.l", "green", wire_paths['digital1']],
                    [f"{mcu_id}:{gnd_pin}", f"{part_id}:2.l", "black", wire_paths['power']]
                ])
                
            elif 'buzzer' in part_type or 'piezo' in part_type:
                # Active buzzer or piezo buzzer
                digital_pin = pin_allocator.get_next_digital()
                gnd_pin = pin_allocator.get_ground()
                
                connections.extend([
                    [f"{mcu_id}:{gnd_pin}", f"{part_id}:1", "black", wire_paths['power']],
                    [f"{mcu_id}:{digital_pin}", f"{part_id}:2", "purple", wire_paths['digital1']]
                ])
                
            elif 'led' in part_type:
                # LED with current limiting (assumes external resistor)
                digital_pin = pin_allocator.get_next_digital()
                gnd_pin = pin_allocator.get_ground()
                
                connections.extend([
                    [f"{mcu_id}:{digital_pin}", f"{part_id}:A", "red", wire_paths['digital1']],
                    [f"{mcu_id}:{gnd_pin}", f"{part_id}:C", "black", wire_paths['power']]
                ])
                
            elif 'resistor' in part_type:
                # Resistor - typically used inline, but we'll show as pullup/pulldown
                digital_pin1 = pin_allocator.get_next_digital()
                digital_pin2 = pin_allocator.get_next_digital()
                
                connections.extend([
                    [f"{mcu_id}:{digital_pin1}", f"{part_id}:1", "yellow", wire_paths['digital1']],
                    [f"{mcu_id}:{digital_pin2}", f"{part_id}:2", "orange", wire_paths['digital2']]
                ])
                
            elif 'dht' in part_type or 'temperature' in part_type or 'humidity' in part_type:
                # DHT sensor - digital temperature/humidity sensor
                digital_pin = pin_allocator.get_next_digital()
                power_pin = pin_allocator.get_power_5v()
                gnd_pin = pin_allocator.get_ground()
                
                connections.extend([
                    [f"{mcu_id}:{gnd_pin}", f"{part_id}:GND", "black", wire_paths['power']],
                    [f"{mcu_id}:{power_pin}", f"{part_id}:VCC", "red", wire_paths['power_alt']],
                    [f"{mcu_id}:{digital_pin}", f"{part_id}:SDA", "blue", wire_paths['digital1']]
                ])
                
            elif 'servo' in part_type:
                # Servo motor - PWM control
                pwm_pin = pin_allocator.get_next_pwm()
                power_pin = pin_allocator.get_power_5v()
                gnd_pin = pin_allocator.get_ground()
                
                connections.extend([
                    [f"{mcu_id}:{gnd_pin}", f"{part_id}:GND", "brown", wire_paths['power']],
                    [f"{mcu_id}:{power_pin}", f"{part_id}:V+", "red", wire_paths['power_alt']],
                    [f"{mcu_id}:{pwm_pin}", f"{part_id}:PWM", "orange", wire_paths['digital1']]
                ])
                
            elif 'ultrasonic' in part_type or 'hc-sr04' in part_type:
                # Ultrasonic sensor - requires trigger and echo pins
                trig_pin = pin_allocator.get_next_digital()
                echo_pin = pin_allocator.get_next_digital()
                power_pin = pin_allocator.get_power_5v()
                gnd_pin = pin_allocator.get_ground()
                
                connections.extend([
                    [f"{mcu_id}:{gnd_pin}", f"{part_id}:GND", "black", wire_paths['power']],
                    [f"{mcu_id}:{power_pin}", f"{part_id}:VCC", "red", wire_paths['power_alt']],
                    [f"{mcu_id}:{trig_pin}", f"{part_id}:TRIG", "blue", wire_paths['digital1']],
                    [f"{mcu_id}:{echo_pin}", f"{part_id}:ECHO", "green", wire_paths['digital2']]
                ])
                
            elif 'potentiometer' in part_type or 'pot' in part_type:
                # Potentiometer - analog input
                analog_pin = pin_allocator.get_next_analog()
                power_pin = pin_allocator.get_power_5v()
                gnd_pin = pin_allocator.get_ground()
                
                connections.extend([
                    [f"{mcu_id}:{gnd_pin}", f"{part_id}:GND", "black", wire_paths['power']],
                    [f"{mcu_id}:{power_pin}", f"{part_id}:VCC", "red", wire_paths['power_alt']],
                    [f"{mcu_id}:{analog_pin}", f"{part_id}:SIG", "yellow", wire_paths['analog1']]
                ])
                
            else:
                # Default wiring for unknown components
                digital_pin = pin_allocator.get_next_digital()
                gnd_pin = pin_allocator.get_ground()
                
                connections.extend([
                    [f"{mcu_id}:{gnd_pin}", f"{part_id}:GND", "black", wire_paths['power']],
                    [f"{mcu_id}:{digital_pin}", f"{part_id}:SIG", "gray", wire_paths['digital1']]
                ])
        
        # Add automatic resistors where needed
        final_parts, final_connections = self.add_automatic_resistors(parts, connections)
        
        return self.finalize_diagram(final_parts, final_connections)
    
    def add_automatic_resistors(self, parts: List[Dict[str, Any]], connections: List) -> tuple:
        """Automatically add resistors where needed for circuit safety"""
        
        new_parts = parts.copy()
        new_connections = connections.copy()
        resistor_counter = 1
        
        # Find components that need current limiting resistors
        components_needing_resistors = []
        
        for part in parts:
            part_type = part['type'].lower()
            part_id = part['id']
            
            # LEDs need current limiting resistors
            if 'led' in part_type:
                # Check if there's already a resistor for this LED
                has_resistor = any('resistor' in p['type'].lower() and 
                                 any(part_id in str(conn) for conn in connections 
                                     if p['id'] in str(conn)) 
                                 for p in parts)
                
                if not has_resistor:
                    components_needing_resistors.append({
                        'component': part,
                        'resistor_type': 'current_limiting',
                        'value': '220',  # 220 ohm for LED
                        'reason': f'Current limiting for {part_id}'
                    })
            
            # Piezo buzzers might need current limiting
            elif 'piezo' in part_type:
                has_resistor = any('resistor' in p['type'].lower() and 
                               any(part_id in str(conn) for conn in connections 
                                   if p['id'] in str(conn)) 
                               for p in parts)
                
                if not has_resistor:
                    components_needing_resistors.append({
                        'component': part,
                        'resistor_type': 'current_limiting', 
                        'value': '100',  # 100 ohm for piezo
                        'reason': f'Current limiting for piezo {part_id}'
                    })
        
        # Add resistors and update connections
        for item in components_needing_resistors:
            component = item['component']
            resistor_value = item['value']
            
            # Create resistor component
            resistor_id = f"R{resistor_counter}"
            resistor_part = {
                "type": "wokwi-resistor",
                "id": resistor_id,
                "top": component.get('top', 0) + 30,  # Place near original component
                "left": component.get('left', 0) - 50,
                "attrs": {"value": resistor_value}
            }
            
            new_parts.append(resistor_part)
            
            # Find MCU
            mcu = None
            for part in parts:
                if any(x in part['type'].lower() for x in ['arduino', 'esp32', 'mega', 'nano']):
                    mcu = part
                    break
            
            if mcu:
                # Update connections to go through resistor
                updated_connections = []
                
                for conn in new_connections:
                    if conn[1].startswith(f"{component['id']}:"):
                        # This connection goes to our component
                        if 'led' in component['type'].lower() and conn[1].endswith(':A'):
                            # LED anode connection - insert resistor
                            # Original: MCU:pin -> LED:A
                            # New: MCU:pin -> Resistor:1, Resistor:2 -> LED:A
                            
                            # Connection from MCU to resistor
                            mcu_to_resistor = [conn[0], f"{resistor_id}:1", conn[2], conn[3]]
                            updated_connections.append(mcu_to_resistor)
                            
                            # Connection from resistor to LED
                            resistor_to_led = [f"{resistor_id}:2", conn[1], conn[2], ["h10", "*", "h-5"]]
                            updated_connections.append(resistor_to_led)
                            
                            print(f"🔧 Auto-added {resistor_value}Ω resistor ({resistor_id}) for {component['id']}")
                        elif 'piezo' in component['type'].lower() and conn[1].endswith(':2'):
                            # Piezo signal connection - insert resistor
                            mcu_to_resistor = [conn[0], f"{resistor_id}:1", conn[2], conn[3]]
                            updated_connections.append(mcu_to_resistor)
                            
                            resistor_to_piezo = [f"{resistor_id}:2", conn[1], conn[2], ["h10", "*", "h-5"]]
                            updated_connections.append(resistor_to_piezo)
                            
                            print(f"🔧 Auto-added {resistor_value}Ω resistor ({resistor_id}) for piezo {component['id']}")
                        else:
                            # Keep other connections as-is
                            updated_connections.append(conn)
                    else:
                        # Keep connections not related to this component
                        updated_connections.append(conn)
                
                new_connections = updated_connections
            
            resistor_counter += 1
        
        return new_parts, new_connections
    
    def get_pin_allocator(self, mcu_type: str):
        """Get the appropriate pin allocator for the MCU type"""
        mcu_type_lower = mcu_type.lower()
        
        if 'esp32' in mcu_type_lower:
            return ESP32PinAllocator()
        elif 'mega' in mcu_type_lower:
            return ArduinoMegaPinAllocator()
        elif 'uno' in mcu_type_lower:
            return ArduinoUnoPinAllocator()
        elif 'nano' in mcu_type_lower:
            return ArduinoNanoPinAllocator()
        else:
            # Default to Uno-like pinout
            return ArduinoUnoPinAllocator()
    
    def calculate_wire_paths(self, mcu: Dict[str, Any], component: Dict[str, Any]) -> Dict[str, List[str]]:
        """Calculate optimized wire paths based on component positions"""
        
        mcu_top = mcu.get('top', 0)
        mcu_left = mcu.get('left', 0)
        comp_top = component.get('top', 0)
        comp_left = component.get('left', 0)
        
        # Calculate relative positions
        v_offset = int((comp_top - mcu_top) * 0.1)  # Reduced scale for cleaner paths
        h_offset = int((comp_left - mcu_left) * 0.1)
        
        # Ensure minimum offsets for visibility
        v_offset = max(min(v_offset, 100), -100)
        h_offset = max(min(h_offset, 150), -150)
        
        # Generate different path patterns to avoid overlaps
        paths = {
            'power': [f"v{v_offset}", "*", f"v{-v_offset//3}"] if v_offset != 0 else ["*"],
            'power_alt': [f"v{v_offset-15}", "*", f"v{-v_offset//3+8}"] if v_offset != 15 else ["h5", "*", "h-5"],
            'analog1': [f"v{v_offset-25}", f"h{h_offset//3}", "*", f"v{-v_offset//4}"] if v_offset != 25 else [f"h{h_offset//3}", "*"],
            'analog2': [f"v{v_offset-30}", f"h{h_offset//4}", "*", f"v{-v_offset//5}"] if v_offset != 30 else [f"h{h_offset//4}", "*"],
            'digital1': [f"v{v_offset-35}", f"h{h_offset//5}", "*", f"h{-h_offset//10}", f"v{-v_offset//6}"] if v_offset != 35 else [f"h{h_offset//5}", "*", f"h{-h_offset//10}"],
            'digital2': [f"v{v_offset-40}", f"h{h_offset//6}", "*", f"h{-h_offset//12}", f"v{-v_offset//7}"] if v_offset != 40 else [f"h{h_offset//6}", "*", f"h{-h_offset//12}"],
            'digital_alt1': [f"v{v_offset-45}", f"h{h_offset//7}", "*", f"v{-v_offset//8}"] if v_offset != 45 else [f"h{h_offset//7}", "*"],
            'digital_alt2': [f"v{v_offset-50}", f"h{h_offset//8}", "*", f"v{-v_offset//9}"] if v_offset != 50 else [f"h{h_offset//8}", "*"]
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

class PinAllocator:
    """Base class for MCU pin allocation"""
    
    def __init__(self):
        self.used_pins = set()
        self.digital_pin_idx = 0
        self.analog_pin_idx = 0
        self.pwm_pin_idx = 0
        self.ground_pin_idx = 0  # Track which ground pin to use next
    
    def get_ground(self):
        """Get the next available ground pin, cycling through all GND pins"""
        ground_pins = self.get_ground_pins()
        current_gnd = ground_pins[self.ground_pin_idx % len(ground_pins)]
        self.ground_pin_idx += 1
        return current_gnd
    
    def get_ground_pins(self):
        """Return list of available ground pins for this MCU"""
        return ["GND.1"]  # Default, override in subclasses
    
    def get_power_5v(self):
        return "5V"
    
    def get_power_3v3(self):
        return "3.3V"
    
    def get_next_digital(self):
        raise NotImplementedError
    
    def get_next_analog(self):
        raise NotImplementedError
    
    def get_next_pwm(self):
        raise NotImplementedError
    
    def get_i2c_sda(self):
        raise NotImplementedError
    
    def get_i2c_scl(self):
        raise NotImplementedError
    
    def get_spi_pins(self):
        raise NotImplementedError

class ArduinoUnoPinAllocator(PinAllocator):
    """Pin allocator for Arduino Uno"""
    
    def __init__(self):
        super().__init__()
        self.digital_pins = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        self.analog_pins = ['A0', 'A1', 'A2', 'A3']  # A4/A5 reserved for I2C
        self.pwm_pins = [3, 5, 6, 9, 10, 11]
    
    def get_ground_pins(self):
        """Arduino Uno has 3 ground pins"""
        return ["GND.1", "GND.2", "GND.3"]
    
    def get_next_digital(self):
        while self.digital_pin_idx < len(self.digital_pins):
            pin = self.digital_pins[self.digital_pin_idx]
            self.digital_pin_idx += 1
            if pin not in self.used_pins:
                self.used_pins.add(pin)
                return str(pin)
        return "2"  # Fallback
    
    def get_next_analog(self):
        while self.analog_pin_idx < len(self.analog_pins):
            pin = self.analog_pins[self.analog_pin_idx]
            self.analog_pin_idx += 1
            if pin not in self.used_pins:
                self.used_pins.add(pin)
                return pin
        return "A0"  # Fallback
    
    def get_next_pwm(self):
        for pin in self.pwm_pins:
            if pin not in self.used_pins:
                self.used_pins.add(pin)
                return str(pin)
        return "3"  # Fallback
    
    def get_i2c_sda(self):
        return "A4"
    
    def get_i2c_scl(self):
        return "A5"
    
    def get_spi_pins(self):
        return {
            'mosi': '11',
            'miso': '12',
            'sck': '13'
        }

class ArduinoMegaPinAllocator(PinAllocator):
    """Pin allocator for Arduino Mega"""
    
    def __init__(self):
        super().__init__()
        self.digital_pins = list(range(2, 54))  # Pins 2-53
        self.analog_pins = [f'A{i}' for i in range(16)]  # A0-A15
        self.pwm_pins = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 44, 45, 46]
    
    def get_ground_pins(self):
        """Arduino Mega has 4 ground pins"""
        return ["GND.1", "GND.2", "GND.3", "GND.4"]
    
    def get_next_digital(self):
        while self.digital_pin_idx < len(self.digital_pins):
            pin = self.digital_pins[self.digital_pin_idx]
            self.digital_pin_idx += 1
            if pin not in self.used_pins:
                self.used_pins.add(pin)
                return str(pin)
        return "2"  # Fallback
    
    def get_next_analog(self):
        while self.analog_pin_idx < len(self.analog_pins):
            pin = self.analog_pins[self.analog_pin_idx]
            self.analog_pin_idx += 1
            if pin not in self.used_pins:
                self.used_pins.add(pin)
                return pin
        return "A0"  # Fallback
    
    def get_next_pwm(self):
        for pin in self.pwm_pins:
            if pin not in self.used_pins:
                self.used_pins.add(pin)
                return str(pin)
        return "3"  # Fallback
    
    def get_i2c_sda(self):
        return "20"  # SDA on Mega
    
    def get_i2c_scl(self):
        return "21"  # SCL on Mega
    
    def get_spi_pins(self):
        return {
            'mosi': '51',
            'miso': '50',
            'sck': '52'
        }

class ArduinoNanoPinAllocator(ArduinoUnoPinAllocator):
    """Pin allocator for Arduino Nano (same as Uno)"""
    pass

class ESP32PinAllocator(PinAllocator):
    """Pin allocator for ESP32"""
    
    def __init__(self):
        super().__init__()
        # ESP32 available GPIO pins (avoiding strapping and input-only pins)
        self.digital_pins = [2, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 23, 25, 26, 27, 32, 33]
        self.analog_pins = [32, 33, 34, 35, 36, 39]  # ADC1 pins
        self.pwm_pins = [2, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 23, 25, 26, 27]
    
    def get_ground_pins(self):
        """ESP32 has multiple ground pins"""
        return ["GND.1", "GND.2", "GND.3"]
    
    def get_power_3v3(self):
        return "3.3V"
    
    def get_power_5v(self):
        return "5V"  # ESP32 boards often have 5V from USB
    
    def get_next_digital(self):
        while self.digital_pin_idx < len(self.digital_pins):
            pin = self.digital_pins[self.digital_pin_idx]
            self.digital_pin_idx += 1
            if pin not in self.used_pins:
                self.used_pins.add(pin)
                return str(pin)
        return "2"  # Fallback
    
    def get_next_analog(self):
        while self.analog_pin_idx < len(self.analog_pins):
            pin = self.analog_pins[self.analog_pin_idx]
            self.analog_pin_idx += 1
            if pin not in self.used_pins:
                self.used_pins.add(pin)
                return str(pin)
        return "32"  # Fallback
    
    def get_next_pwm(self):
        for pin in self.pwm_pins:
            if pin not in self.used_pins:
                self.used_pins.add(pin)
                return str(pin)
        return "2"  # Fallback
    
    def get_i2c_sda(self):
        return "21"  # Default SDA for ESP32
    
    def get_i2c_scl(self):
        return "22"  # Default SCL for ESP32
    
    def get_spi_pins(self):
        return {
            'mosi': '23',
            'miso': '19',
            'sck': '18'
        }
    
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
