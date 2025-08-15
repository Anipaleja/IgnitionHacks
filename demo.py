#!/usr/bin/env python3
"""
RAG AI Circuit Generator - Interactive Demo
==========================================

This demonstrates the complete RAG AI system with two modes:
1. Interactive component selection
2. Text input for natural language component description

Usage: Just run this script and choose your preferred mode!
"""

import sys
import os
sys.path.append('.')

from main import generate_circuit_diagram_json
import json
import re

def ai_component_assessment(component_input):
    """AI-powered component assessment and recognition"""
    # First try fallback assessment (more reliable)
    fallback_result = fallback_component_assessment(component_input)
    
    # If fallback found a good match, use it
    if fallback_result['recognized'] and fallback_result['confidence'] >= 7:
        return fallback_result
    
    # Otherwise try the AI model for more complex analysis
    try:
        sys.path.insert(0, './src')
        from comprehensive_model_trainer import ComprehensiveHardwareModelTrainer
        
        trainer = ComprehensiveHardwareModelTrainer()
        
        # Ask the AI to assess the component
        prompt = f"""
        Analyze this component input: "{component_input}"
        
        Tasks:
        1. Identify if this is a known hardware component
        2. Determine the correct Wokwi component type
        3. Suggest appropriate wiring connections
        4. Provide confidence level (1-10)
        
        Known component types include:
        - wokwi-arduino-uno, wokwi-arduino-mega, wokwi-esp32-devkit-v1
        - wokwi-led, wokwi-resistor, wokwi-pushbutton, wokwi-buzzer
        - board-ssd1306, wokwi-dht22, board-ili9341-cap-touch
        - wokwi-microsd-card, board-l298n, wokwi-servo
        - wokwi-ultrasonic-hc-sr04, wokwi-photoresistor-sensor
        
        Respond with:
        COMPONENT: [wokwi-component-type]
        CONFIDENCE: [1-10]
        DESCRIPTION: [brief description]
        WIRING: [suggested pin connections]
        """
        
        try:
            response = trainer.generate_response(prompt)
            ai_result = parse_ai_response(response, component_input)
            
            # Use AI result if it's better than fallback
            if ai_result['recognized'] and ai_result['confidence'] > fallback_result['confidence']:
                return ai_result
            else:
                return fallback_result
                
        except Exception as e:
            print(f"    AI analysis failed: {e}")
            return fallback_result
            
    except Exception as e:
        print(f"    AI model unavailable: {e}")
        return fallback_result

def parse_ai_response(ai_response, original_input):
    """Parse AI response into structured component data"""
    lines = ai_response.split('\n')
    result = {
        'component_type': None,
        'confidence': 5,
        'description': original_input,
        'wiring_info': 'Standard connections',
        'recognized': False
    }
    
    for line in lines:
        line = line.strip()
        if line.startswith('COMPONENT:'):
            component = line.split(':', 1)[1].strip()
            if component and component != '[wokwi-component-type]':
                result['component_type'] = component
                result['recognized'] = True
        elif line.startswith('CONFIDENCE:'):
            try:
                confidence = int(line.split(':', 1)[1].strip().split('-')[0])
                result['confidence'] = min(max(confidence, 1), 10)
            except:
                pass
        elif line.startswith('DESCRIPTION:'):
            desc = line.split(':', 1)[1].strip()
            if desc and desc != '[brief description]':
                result['description'] = desc
        elif line.startswith('WIRING:'):
            wiring = line.split(':', 1)[1].strip()
            if wiring and wiring != '[suggested pin connections]':
                result['wiring_info'] = wiring
    
    return result

def fallback_component_assessment(component_input):
    """Fallback component assessment using pattern matching"""
    text_lower = component_input.lower()
    
    # Component recognition patterns
    patterns = {
        # Microcontrollers
        r'arduino\s*uno|uno(?!\w)': {"type": "wokwi-arduino-uno", "desc": "Arduino Uno Microcontroller", "conf": 9},
        r'arduino\s*mega|mega(?!\w)': {"type": "wokwi-arduino-mega", "desc": "Arduino Mega Microcontroller", "conf": 9},
        r'esp32|esp\s*32|esp.*dev.*board|esp.*development': {"type": "wokwi-esp32-devkit-v1", "desc": "ESP32 Development Board", "conf": 9},
        
        # Basic components
        r'led(?!\w)|light\s*emitting\s*diode': {"type": "wokwi-led", "desc": "Light Emitting Diode", "conf": 8},
        r'led\s*strip|ws2812|neopixel|addressable.*led': {"type": "wokwi-ws2812", "desc": "LED Strip (WS2812)", "conf": 8},
        r'resistor|resistance': {"type": "wokwi-resistor", "desc": "Resistor", "conf": 8},
        r'button|pushbutton|push\s*button|switch': {"type": "wokwi-pushbutton", "desc": "Push Button", "conf": 8},
        r'buzzer|beeper|alarm': {"type": "wokwi-buzzer", "desc": "Buzzer/Beeper", "conf": 8},
        
        # Displays
        r'oled|ssd1306|display.*128.*64': {"type": "board-ssd1306", "desc": "OLED Display (SSD1306)", "conf": 7},
        r'tft|ili9341|lcd.*touch': {"type": "board-ili9341-cap-touch", "desc": "TFT Touchscreen Display", "conf": 7},
        r'display|screen|lcd': {"type": "board-ssd1306", "desc": "Display (assuming OLED)", "conf": 5},
        
        # Sensors
        r'dht22|temperature.*humidity|temp.*sensor': {"type": "wokwi-dht22", "desc": "DHT22 Temperature/Humidity Sensor", "conf": 8},
        r'ultrasonic|hc-?sr04|distance.*sensor|proximity.*sensor': {"type": "wokwi-ultrasonic-hc-sr04", "desc": "Ultrasonic Distance Sensor (HC-SR04)", "conf": 8},
        r'photoresistor|ldr|light.*sensor': {"type": "wokwi-photoresistor-sensor", "desc": "Light Sensor (LDR)", "conf": 7},
        
        # Actuators
        r'servo|servo.*motor': {"type": "wokwi-servo", "desc": "Servo Motor", "conf": 8},
        r'motor.*driver|l298n': {"type": "board-l298n", "desc": "Motor Driver (L298N)", "conf": 8},
        
        # Storage
        r'sd.*card|microsd|storage': {"type": "wokwi-microsd-card", "desc": "SD Card Module", "conf": 7},
    }
    
    best_match = None
    highest_confidence = 0
    
    for pattern, info in patterns.items():
        if re.search(pattern, text_lower):
            if info['conf'] > highest_confidence:
                highest_confidence = info['conf']
                best_match = info
    
    if best_match:
        return {
            'component_type': best_match['type'],
            'confidence': highest_confidence,
            'description': best_match['desc'],
            'wiring_info': 'Standard wiring based on component type',
            'recognized': True
        }
    else:
        return {
            'component_type': None,
            'confidence': 1,
            'description': f"Unknown component: {component_input}",
            'wiring_info': 'Manual wiring required',
            'recognized': False
        }

def ai_assessment_mode():
    """Mode where AI assesses user-input components and wires them intelligently"""
    print("AI Component Assessment Mode")
    print("=" * 32)
    print()
    print("The AI will analyze your components and determine:")
    print("  - Whether it recognizes the component")
    print("  - The correct Wokwi component type")
    print("  - Appropriate wiring connections")
    print("  - Confidence level in the assessment")
    print()
    
    components = []
    
    # First, get the microcontroller
    print("Step 1: Enter your microcontroller")
    while True:
        mcu_input = input("Describe your microcontroller (e.g., 'Arduino Uno', 'ESP32'): ").strip()
        if mcu_input:
            print(f"\nAnalyzing: '{mcu_input}'...")
            assessment = ai_component_assessment(mcu_input)
            
            print(f"AI Assessment:")
            print(f"  Recognized: {'Yes' if assessment['recognized'] else 'No'}")
            print(f"  Component Type: {assessment['component_type'] or 'Unknown'}")
            print(f"  Description: {assessment['description']}")
            print(f"  Confidence: {assessment['confidence']}/10")
            
            if assessment['recognized'] and assessment['confidence'] >= 6:
                components.append({
                    "type": assessment['component_type'],
                    "id": "mcu",
                    "description": assessment['description'],
                    "ai_confidence": assessment['confidence']
                })
                print(f"✓ Added microcontroller: {assessment['description']}")
                break
            else:
                retry = input("Low confidence or unrecognized. Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    # Add as unknown component
                    components.append({
                        "type": "wokwi-arduino-uno",  # Default fallback
                        "id": "mcu",
                        "description": "Unknown MCU (using Arduino Uno as fallback)",
                        "ai_confidence": 1
                    })
                    break
        else:
            print("Please enter a microcontroller description.")
    
    # Get additional components
    print(f"\nStep 2: Add additional components")
    print("Enter component descriptions (press Enter with empty input to finish)")
    
    comp_counter = 1
    while True:
        print(f"\nComponent {comp_counter}:")
        comp_input = input("  Describe component (or press Enter to finish): ").strip()
        
        if not comp_input:
            break
        
        print(f"  Analyzing: '{comp_input}'...")
        assessment = ai_component_assessment(comp_input)
        
        print(f"  AI Assessment:")
        print(f"    Recognized: {'Yes' if assessment['recognized'] else 'No'}")
        print(f"    Component Type: {assessment['component_type'] or 'Unknown'}")
        print(f"    Description: {assessment['description']}")
        print(f"    Confidence: {assessment['confidence']}/10")
        print(f"    Wiring Notes: {assessment['wiring_info']}")
        
        if assessment['recognized']:
            components.append({
                "type": assessment['component_type'],
                "id": f"comp{comp_counter}",
                "description": assessment['description'],
                "ai_confidence": assessment['confidence'],
                "wiring_notes": assessment['wiring_info']
            })
            print(f"  ✓ Added: {assessment['description']}")
            comp_counter += 1
        else:
            print(f"  ⚠ Component not recognized (confidence: {assessment['confidence']}/10)")
            add_anyway = input("  Add as custom component anyway? (y/n): ").strip().lower()
            if add_anyway == 'y':
                custom_type = input("  Enter Wokwi component type: ").strip()
                if custom_type:
                    components.append({
                        "type": custom_type,
                        "id": f"comp{comp_counter}",
                        "description": assessment['description'],
                        "ai_confidence": assessment['confidence'],
                        "wiring_notes": "Custom component - manual wiring"
                    })
                    print(f"  ✓ Added as custom: {custom_type}")
                    comp_counter += 1
    
    return components

def get_available_components():
    """Return available component types"""
    return {
        "1": {"type": "wokwi-arduino-uno", "name": "Arduino Uno"},
        "2": {"type": "wokwi-arduino-mega", "name": "Arduino Mega"},
        "3": {"type": "wokwi-esp32-devkit-v1", "name": "ESP32"},
        "4": {"type": "wokwi-led", "name": "LED"},
        "5": {"type": "wokwi-resistor", "name": "Resistor"},
        "6": {"type": "wokwi-pushbutton", "name": "Push Button"},
        "7": {"type": "wokwi-buzzer", "name": "Buzzer"},
        "8": {"type": "board-ssd1306", "name": "OLED Display (SSD1306)"},
        "9": {"type": "wokwi-dht22", "name": "Temperature Sensor (DHT22)"},
        "10": {"type": "board-ili9341-cap-touch", "name": "TFT Display (ILI9341)"},
        "11": {"type": "wokwi-microsd-card", "name": "SD Card Module"},
        "12": {"type": "board-l298n", "name": "Motor Driver (L298N)"}
    }

def parse_text_input(text_input):
    """Parse natural language text input into component list"""
    components = []
    text_lower = text_input.lower()
    
    # Component mapping with various name variations
    component_mappings = {
        # Microcontrollers
        'arduino uno': {"type": "wokwi-arduino-uno", "id": "mcu"},
        'uno': {"type": "wokwi-arduino-uno", "id": "mcu"},
        'arduino mega': {"type": "wokwi-arduino-mega", "id": "mcu"},
        'mega': {"type": "wokwi-arduino-mega", "id": "mcu"},
        'esp32': {"type": "wokwi-esp32-devkit-v1", "id": "mcu"},
        'esp': {"type": "wokwi-esp32-devkit-v1", "id": "mcu"},
        
        # Components
        'led': {"type": "wokwi-led", "id": "led1"},
        'light': {"type": "wokwi-led", "id": "led1"},
        'resistor': {"type": "wokwi-resistor", "id": "r1"},
        'button': {"type": "wokwi-pushbutton", "id": "btn1"},
        'pushbutton': {"type": "wokwi-pushbutton", "id": "btn1"},
        'push button': {"type": "wokwi-pushbutton", "id": "btn1"},
        'buzzer': {"type": "wokwi-buzzer", "id": "bz1"},
        'alarm': {"type": "wokwi-buzzer", "id": "bz1"},
        'speaker': {"type": "wokwi-buzzer", "id": "bz1"},
        
        # Displays
        'oled': {"type": "board-ssd1306", "id": "display1"},
        'display': {"type": "board-ssd1306", "id": "display1"},
        'screen': {"type": "board-ssd1306", "id": "display1"},
        'ssd1306': {"type": "board-ssd1306", "id": "display1"},
        'tft': {"type": "board-ili9341-cap-touch", "id": "tft1"},
        'ili9341': {"type": "board-ili9341-cap-touch", "id": "tft1"},
        'lcd': {"type": "board-ili9341-cap-touch", "id": "tft1"},
        
        # Sensors
        'temperature': {"type": "wokwi-dht22", "id": "temp1"},
        'temp': {"type": "wokwi-dht22", "id": "temp1"},
        'dht22': {"type": "wokwi-dht22", "id": "temp1"},
        'dht': {"type": "wokwi-dht22", "id": "temp1"},
        'humidity': {"type": "wokwi-dht22", "id": "temp1"},
        
        # Storage
        'sd card': {"type": "wokwi-microsd-card", "id": "sd1"},
        'sd': {"type": "wokwi-microsd-card", "id": "sd1"},
        'microsd': {"type": "wokwi-microsd-card", "id": "sd1"},
        'storage': {"type": "wokwi-microsd-card", "id": "sd1"},
        
        # Motors
        'motor': {"type": "board-l298n", "id": "motor1"},
        'motor driver': {"type": "board-l298n", "id": "motor1"},
        'l298n': {"type": "board-l298n", "id": "motor1"},
        'servo': {"type": "wokwi-servo", "id": "servo1"},
        'servo motor': {"type": "wokwi-servo", "id": "servo1"},
        
        # Sensors
        'ultrasonic': {"type": "wokwi-ultrasonic-hc-sr04", "id": "ultrasonic1"},
        'ultrasonic sensor': {"type": "wokwi-ultrasonic-hc-sr04", "id": "ultrasonic1"},
        'hc-sr04': {"type": "wokwi-ultrasonic-hc-sr04", "id": "ultrasonic1"},
        'distance sensor': {"type": "wokwi-ultrasonic-hc-sr04", "id": "ultrasonic1"},
        'photoresistor': {"type": "wokwi-photoresistor-sensor", "id": "light1"},
        'light sensor': {"type": "wokwi-photoresistor-sensor", "id": "light1"},
        'ldr': {"type": "wokwi-photoresistor-sensor", "id": "light1"},
    }
    
    # Check if a microcontroller is mentioned, if not add Arduino Uno as default
    mcu_found = False
    for keyword in ['arduino', 'esp32', 'esp', 'uno', 'mega']:
        if keyword in text_lower:
            mcu_found = True
            break
    
    if not mcu_found:
        components.append({"type": "wokwi-arduino-uno", "id": "mcu"})
        print("No microcontroller specified, using Arduino Uno as default")
    
    # Find components in the text
    comp_counter = 1
    added_types = set()  # Track added component types to avoid duplicates
    
    for keyword, comp_info in component_mappings.items():
        if keyword in text_lower:
            comp_type = comp_info['type']
            
            # Avoid duplicate microcontrollers
            if comp_type in ['wokwi-arduino-uno', 'wokwi-arduino-mega', 'wokwi-esp32-devkit-v1']:
                if not any(c['type'] in ['wokwi-arduino-uno', 'wokwi-arduino-mega', 'wokwi-esp32-devkit-v1'] for c in components):
                    components.append(comp_info.copy())
                    added_types.add(comp_type)
            else:
                # For other components, avoid duplicates of the same type
                if comp_type not in added_types:
                    comp = comp_info.copy()
                    if comp['id'] != 'mcu':
                        comp['id'] = f"comp{comp_counter}"
                        comp_counter += 1
                    components.append(comp)
                    added_types.add(comp_type)
    
    # If no components found except MCU, add some default components
    if len(components) <= 1:
        components.extend([
            {"type": "wokwi-led", "id": "comp1"},
            {"type": "wokwi-resistor", "id": "comp2"}
        ])
        print("No specific components found, adding LED and resistor as defaults")
    
    return components

def custom_component_mode():
    """Mode where user inputs custom component types and IDs"""
    print("Custom Component Mode")
    print("=" * 25)
    print()
    print("Enter your custom components manually.")
    print("You'll need to specify the Wokwi component type and a unique ID.")
    print()
    print("Common Wokwi component types:")
    print("  - wokwi-arduino-uno, wokwi-arduino-mega, wokwi-esp32-devkit-v1")
    print("  - wokwi-led, wokwi-resistor, wokwi-pushbutton, wokwi-buzzer")
    print("  - board-ssd1306, wokwi-dht22, board-ili9341-cap-touch")
    print("  - wokwi-microsd-card, board-l298n, wokwi-servo")
    print("  - wokwi-ultrasonic-hc-sr04, wokwi-photoresistor-sensor")
    print()
    
    components = []
    
    # First, get the microcontroller
    print("Step 1: Enter microcontroller")
    while True:
        mcu_type = input("Enter microcontroller type (e.g., wokwi-arduino-uno): ").strip()
        if mcu_type:
            mcu_id = input("Enter microcontroller ID (or press Enter for 'mcu'): ").strip()
            if not mcu_id:
                mcu_id = "mcu"
            
            components.append({
                "type": mcu_type,
                "id": mcu_id
            })
            print(f"Added: {mcu_type} (ID: {mcu_id})")
            break
        else:
            print("Please enter a microcontroller type.")
    
    # Then get additional components
    print("\nStep 2: Add additional components")
    print("Enter component details (press Enter with empty type to finish)")
    
    comp_counter = 1
    while True:
        print(f"\nComponent {comp_counter}:")
        comp_type = input("  Component type (or press Enter to finish): ").strip()
        
        if not comp_type:
            break
        
        comp_id = input(f"  Component ID (or press Enter for 'comp{comp_counter}'): ").strip()
        if not comp_id:
            comp_id = f"comp{comp_counter}"
        
        comp_name = input("  Component name/description (optional): ").strip()
        
        component = {
            "type": comp_type,
            "id": comp_id
        }
        
        if comp_name:
            component["name"] = comp_name
        
        components.append(component)
        print(f"  Added: {comp_type} (ID: {comp_id})")
        comp_counter += 1
    
    return components

def text_input_mode():
    """Mode where user describes components in natural language"""
    print("Text Input Mode - Describe Your Circuit")
    print("=" * 40)
    print()
    print("Describe the components you want in your circuit using natural language.")
    print("Examples:")
    print("  - 'Arduino Uno with LED and button'")
    print("  - 'ESP32 with temperature sensor and OLED display'")
    print("  - 'Arduino Mega with buzzer, SD card, and TFT screen'")
    print("  - 'temperature monitoring system with display and alarm'")
    print()
    
    while True:
        user_input = input("Describe your circuit: ").strip()
        if user_input:
            break
        print("Please enter a description of your circuit.")
    
    print(f"\nAnalyzing your request: '{user_input}'")
    
    # Parse the text input into components
    components = parse_text_input(user_input)
    
    print(f"\nDetected components:")
    for comp in components:
        comp_name = comp['type'].replace('wokwi-', '').replace('board-', '').replace('-', ' ').title()
        print(f"   - {comp_name} (ID: {comp['id']})")
    
    return components

def interactive_selection_mode():
    """Mode where user selects components from a menu"""
    print("Interactive Selection Mode")
    print("=" * 30)
    
    # Step 1: Select microcontroller
    print("\nStep 1: Select a microcontroller (required)")
    print("1. Arduino Uno")
    print("2. Arduino Mega") 
    print("3. ESP32")
    
    while True:
        choice = input("Enter your choice (1-3): ").strip()
        if choice == "1":
            mcu = {"type": "wokwi-arduino-uno", "id": "mcu"}
            break
        elif choice == "2":
            mcu = {"type": "wokwi-arduino-mega", "id": "mcu"}
            break
        elif choice == "3":
            mcu = {"type": "wokwi-esp32-devkit-v1", "id": "mcu"}
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
    
    # Step 2: Select components
    components = get_available_components()
    selected = [mcu]
    
    print("\nStep 2: Select additional components (enter numbers separated by commas)")
    print("Available components:")
    for key, comp in components.items():
        if int(key) > 3:  # Skip microcontrollers (already selected)
            print(f"{key}. {comp['name']}")
    
    print("0. Done selecting")
    
    while True:
        choices = input("\nEnter component numbers (e.g., 4,6,8 or 0 to finish): ").strip()
        
        if choices == "0":
            break
            
        try:
            numbers = [num.strip() for num in choices.split(",")]
            for num in numbers:
                if num in components and int(num) > 3:
                    comp = components[num]
                    comp_id = f"comp{len(selected)}"
                    selected.append({
                        "type": comp["type"],
                        "id": comp_id,
                        "name": comp["name"]
                    })
                    print(f"Added: {comp['name']}")
                elif num != "0":
                    print(f"Invalid component number: {num}")
        except:
            print("Invalid input format. Use numbers separated by commas.")
    
    return selected

def demo_rag_ai_circuit_generator():
    """Main demo function with mode selection"""
    
    print("RAG AI Circuit Generator - Interactive Demo")
    print("=" * 50)
    print()
    print("Choose your input mode:")
    print("1. Text Input - Describe components in natural language")
    print("2. Interactive Selection - Choose from component menu")
    print("3. Custom Components - Enter your own component types")
    print("4. AI Assessment - AI analyzes and wires your components")
    print()
    
    # Mode selection
    while True:
        mode = input("Enter your choice (1, 2, 3, or 4): ").strip()
        if mode == "1":
            components = text_input_mode()
            break
        elif mode == "2":
            components = interactive_selection_mode()
            break
        elif mode == "3":
            components = custom_component_mode()
            break
        elif mode == "4":
            components = ai_assessment_mode()
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")
    
    print(f"\nYour circuit will have {len(components)} components:")
    for part in components:
        name = part.get('name', part.get('description', part['type'].replace('wokwi-', '').replace('board-', '').replace('-', ' ').title()))
        confidence_info = ""
        if 'ai_confidence' in part:
            confidence_info = f" [AI Confidence: {part['ai_confidence']}/10]"
        print(f"   - {name} (ID: {part['id']}){confidence_info}")
        if 'wiring_notes' in part:
            print(f"     Note: {part['wiring_notes']}")
    
    # Generate filename
    filename = input("\nEnter filename for diagram (or press Enter for 'circuit.json'): ").strip()
    if not filename:
        filename = "circuit.json"
    if not filename.endswith('.json'):
        filename += '.json'
    
    print(f"\nGenerating circuit diagram...")
    
    # Generate the circuit diagram JSON
    diagram_json = generate_circuit_diagram_json(
        parts=components,
        save_to_file=filename
    )
    
    print(f"\nCircuit generated successfully!")
    print(f"Saved to: {filename}")
    
    # Show a preview of the generated JSON
    diagram_data = json.loads(diagram_json)
    
    print(f"\nGenerated circuit summary:")
    print(f"   Components: {len(diagram_data['parts'])}")
    print(f"   Connections: {len(diagram_data['connections'])} wires")
    
    print(f"\nWire connections:")
    for i, conn in enumerate(diagram_data["connections"][:5]):  # Show first 5
        print(f"   {conn[0]} -> {conn[1]} ({conn[2]} wire)")
    if len(diagram_data["connections"]) > 5:
        print(f"   ... and {len(diagram_data['connections']) - 5} more connections")
    
    print(f"\nYour circuit diagram is ready!")
    print(f"You can now open {filename} in Wokwi for simulation.")

if __name__ == "__main__":
    demo_rag_ai_circuit_generator()
