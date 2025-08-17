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
import json
import re
import math
import time
sys.path.append('.')

from main import generate_circuit_diagram_json

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
        'piezo': {"type": "wokwi-piezo-buzzer", "id": "piezo1"},
        'piezo buzzer': {"type": "wokwi-piezo-buzzer", "id": "piezo1"},
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
    display_added = False  # Special flag for display components
    
    for keyword, comp_info in component_mappings.items():
        if keyword in text_lower:
            comp_type = comp_info['type']
            
            # Avoid duplicate microcontrollers
            if comp_type in ['wokwi-arduino-uno', 'wokwi-arduino-mega', 'wokwi-esp32-devkit-v1']:
                if not any(c['type'] in ['wokwi-arduino-uno', 'wokwi-arduino-mega', 'wokwi-esp32-devkit-v1'] for c in components):
                    components.append(comp_info.copy())
                    added_types.add(comp_type)
            else:
                # Special handling for display components - only add one display
                if comp_type in ['board-ssd1306', 'board-ili9341-cap-touch']:
                    if not display_added:
                        comp = comp_info.copy()
                        if comp['id'] != 'mcu':
                            comp['id'] = f"comp{comp_counter}"
                            comp_counter += 1
                        components.append(comp)
                        added_types.add(comp_type)
                        display_added = True
                        print(f"🖥️  Added display: {comp_type}")
                # For other components, avoid duplicates of the same type
                elif comp_type not in added_types:
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

def generate_step_instructions(step_num, components, diagram_data, filename, arduino_center):
    """Generate detailed step-by-step instructions for beginners"""
    
    # Component name mapping for friendly names
    component_names = {
        'wokwi-arduino-uno': 'Arduino Uno',
        'wokwi-arduino-mega': 'Arduino Mega',
        'wokwi-esp32-devkit-v1': 'ESP32 Development Board',
        'wokwi-led': 'LED (Light Emitting Diode)',
        'wokwi-resistor': 'Resistor',
        'wokwi-pushbutton': 'Push Button',
        'wokwi-buzzer': 'Buzzer',
        'wokwi-piezo-buzzer': 'Piezo Buzzer',
        'board-ssd1306': 'OLED Display (SSD1306)',
        'wokwi-dht22': 'Temperature & Humidity Sensor (DHT22)',
        'board-ili9341-cap-touch': 'TFT Display (ILI9341)',
        'wokwi-microsd-card': 'SD Card Module',
        'board-l298n': 'Motor Driver (L298N)',
        'wokwi-servo': 'Servo Motor'
    }
    
    # Pin description mapping
    pin_descriptions = {
        'GND': 'Ground (negative power)',
        '5V': '5 volt power supply',
        '3.3V': '3.3 volt power supply',
        'A4': 'Analog pin A4 (SDA for I2C)',
        'A5': 'Analog pin A5 (SCL for I2C)',
        'VCC': 'Positive power input',
        'SDA': 'Serial Data Line (I2C communication)',
        'SCL': 'Serial Clock Line (I2C communication)',
        'A': 'Anode (positive leg of LED)',
        'C': 'Cathode (negative leg of LED)',
        '1': 'Pin 1',
        '2': 'Pin 2'
    }
    
    with open(filename, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write(f"STEP {step_num} BUILDING INSTRUCTIONS - BEGINNER GUIDE\n")
        f.write("=" * 70 + "\n\n")
        
        # What you're building
        if step_num == 1:
            f.write("WHAT YOU'RE BUILDING:\n")
            f.write("In this first step, you'll set up your microcontroller.\n")
            f.write("This is the 'brain' of your circuit that will control everything.\n\n")
        else:
            new_comp = components[-1]  # Last component is the new one
            comp_name = component_names.get(new_comp['type'], new_comp['type'])
            f.write("WHAT YOU'RE ADDING:\n")
            f.write(f"In this step, you'll add a {comp_name} to your circuit.\n\n")
        
        # Components needed
        f.write("COMPONENTS NEEDED FOR THIS STEP:\n")
        f.write("-" * 40 + "\n")
        for i, comp in enumerate(components, 1):
            comp_name = component_names.get(comp['type'], comp['type'])
            f.write(f"{i}. {comp_name}\n")
            
            # Add component description
            if 'arduino' in comp['type']:
                f.write("   - This is your microcontroller board\n")
                f.write("   - It has many pins for connecting components\n")
            elif 'led' in comp['type']:
                f.write("   - This light will turn on/off when controlled\n")
                f.write("   - Has two legs: long leg is positive (+), short leg is negative (-)\n")
            elif 'resistor' in comp['type']:
                resistance = "220"  # Default
                for part in diagram_data['parts']:
                    if part['id'] == comp['id'] and 'attrs' in part:
                        resistance = part['attrs'].get('value', '220')
                        break
                f.write(f"   - Limits electrical current (this one is {resistance} ohms)\n")
                f.write("   - Protects components from too much electricity\n")
            elif 'buzzer' in comp['type'] or 'piezo' in comp['type']:
                f.write("   - Makes sound when electricity passes through it\n")
                f.write("   - Has two pins for positive and negative connections\n")
            elif 'ssd1306' in comp['type'] or 'oled' in comp['type']:
                f.write("   - Small screen that can display text and graphics\n")
                f.write("   - Uses I2C communication (only needs 4 wires)\n")
            elif 'pushbutton' in comp['type']:
                f.write("   - Press to complete the circuit\n")
                f.write("   - Has 4 pins but only 2 are used typically\n")
        
        # Tools needed
        f.write(f"\nTOOLS YOU'LL NEED:\n")
        f.write("-" * 20 + "\n")
        f.write("- Breadboard (for making connections)\n")
        f.write("- Jumper wires (various colors recommended)\n")
        if step_num > 1:
            f.write("- Wire strippers (if using solid core wire)\n")
        f.write("- USB cable (to power and program the Arduino)\n\n")
        
        # Safety first
        f.write("SAFETY FIRST:\n")
        f.write("-" * 15 + "\n")
        f.write("- Always disconnect power before making changes\n")
        f.write("- Double-check all connections before powering on\n")
        f.write("- Never connect power pins directly together\n")
        f.write("- Be gentle with components - they can be fragile\n\n")
        
        if step_num == 1:
            f.write("STEP-BY-STEP INSTRUCTIONS:\n")
            f.write("-" * 30 + "\n")
            f.write("1. PREPARE YOUR WORKSPACE:\n")
            f.write("   - Find a clean, well-lit area\n")
            f.write("   - Have your breadboard ready\n")
            f.write("   - Keep components organized\n\n")
            
            f.write("2. POSITION YOUR ARDUINO:\n")
            f.write("   - Place the Arduino Uno on your work surface\n")
            f.write("   - Note the pin labels along the edges\n")
            f.write("   - The USB connector should be easily accessible\n\n")
            
            f.write("3. FAMILIARIZE YOURSELF WITH PINS:\n")
            f.write("   - Digital pins: 0-13 (used for on/off signals)\n")
            f.write("   - Analog pins: A0-A5 (used for sensors)\n")
            f.write("   - Power pins: 5V, 3.3V, GND (for powering components)\n\n")
            
            f.write("4. CONNECT USB CABLE:\n")
            f.write("   - Plug USB cable into Arduino\n")
            f.write("   - Connect other end to your computer\n")
            f.write("   - The power LED should light up\n\n")
            
            f.write("WHAT HAPPENS NEXT:\n")
            f.write("- Your Arduino is now ready for programming\n")
            f.write("- In the next step, we'll add our first component\n\n")
        
        else:
            # For steps 2+, show detailed wiring instructions
            f.write("STEP-BY-STEP WIRING INSTRUCTIONS:\n")
            f.write("-" * 40 + "\n")
            
            # Get the new component (last one added)
            new_comp = components[-1]
            new_comp_name = component_names.get(new_comp['type'], new_comp['type'])
            
            f.write(f"You are adding: {new_comp_name}\n\n")
            
            # Find connections for the new component
            new_connections = [conn for conn in diagram_data['connections'] if new_comp['id'] in conn[1]]
            
            if new_connections:
                f.write("WIRE CONNECTIONS TO MAKE:\n")
                f.write("-" * 30 + "\n")
                
                for i, conn in enumerate(new_connections, 1):
                    source = conn[0]  # e.g., "arduino:2"
                    target = conn[1]  # e.g., "comp1:A"
                    color = conn[2]   # wire color
                    
                    # Parse source and target
                    source_parts = source.split(':')
                    target_parts = target.split(':')
                    
                    source_device = source_parts[0]
                    source_pin = source_parts[1] if len(source_parts) > 1 else ""
                    target_device = target_parts[0]
                    target_pin = target_parts[1] if len(target_parts) > 1 else ""
                    
                    # Get pin descriptions
                    source_desc = pin_descriptions.get(source_pin, source_pin)
                    target_desc = pin_descriptions.get(target_pin, target_pin)
                    
                    f.write(f"CONNECTION {i}:\n")
                    f.write(f"   From: Arduino pin {source_pin} ({source_desc})\n")
                    f.write(f"   To:   {new_comp_name} pin {target_pin} ({target_desc})\n")
                    f.write(f"   Use:  {color.upper()} wire (or any color you prefer)\n")
                    
                    # Add specific instructions based on component type
                    if 'led' in new_comp['type'] and target_pin == 'A':
                        f.write("   Note: This connects to the LONG leg of the LED (positive)\n")
                    elif 'led' in new_comp['type'] and target_pin == 'C':
                        f.write("   Note: This connects to the SHORT leg of the LED (negative)\n")
                    elif target_pin == 'GND':
                        f.write("   Note: This is the negative/ground connection\n")
                    elif target_pin in ['VCC', '5V', '3.3V']:
                        f.write("   Note: This provides power to the component\n")
                    elif target_pin in ['SDA', 'SCL']:
                        f.write("   Note: This is for I2C communication with the display\n")
                    
                    f.write("\n")
                
                # Add resistor information if present
                resistors = [p for p in diagram_data['parts'] if 'resistor' in p['type'].lower()]
                if resistors:
                    f.write("IMPORTANT - RESISTOR CONNECTIONS:\n")
                    f.write("-" * 35 + "\n")
                    for resistor in resistors:
                        if resistor['id'] not in [c['id'] for c in components]:  # Auto-added resistor
                            resistance = resistor['attrs'].get('value', '???')
                            f.write(f"A {resistance} ohm resistor has been automatically added for safety.\n")
                            f.write("This resistor prevents too much current from damaging components.\n")
                            f.write("The resistor goes between the Arduino pin and the component.\n\n")
            
            # Physical placement tips
            f.write("PLACEMENT TIPS:\n")
            f.write("-" * 15 + "\n")
            rel_top = new_comp.get('top', 200) - arduino_center['top']
            rel_left = new_comp.get('left', 200) - arduino_center['left']
            
            if rel_top < 0:
                f.write(f"- Place the {new_comp_name} ABOVE your Arduino\n")
            elif rel_top > 0:
                f.write(f"- Place the {new_comp_name} BELOW your Arduino\n")
            
            if rel_left < 0:
                f.write(f"- Position it to the LEFT side\n")
            elif rel_left > 0:
                f.write(f"- Position it to the RIGHT side\n")
            
            f.write("- Keep wire connections neat and organized\n")
            f.write("- Use different colored wires for different types of connections\n")
            f.write("- Leave some space between components for easy access\n\n")
        
        # Testing section
        f.write("TESTING YOUR CIRCUIT:\n")
        f.write("-" * 25 + "\n")
        f.write("1. Double-check all connections match the instructions above\n")
        f.write("2. Make sure no wires are touching that shouldn't be\n")
        f.write("3. Connect power (USB cable to Arduino)\n")
        
        if step_num == 1:
            f.write("4. Look for the power LED on the Arduino - it should be ON\n")
            f.write("5. If the power LED is off, check your USB connection\n")
        else:
            if 'led' in new_comp['type']:
                f.write("4. The LED might not light up until you upload code\n")
                f.write("5. This is normal - the LED needs to be programmed to turn on\n")
            elif 'buzzer' in new_comp['type'] or 'piezo' in new_comp['type']:
                f.write("4. The buzzer will be silent until programmed\n")
                f.write("5. You'll need to upload code to make it beep\n")
            elif 'ssd1306' in new_comp['type']:
                f.write("4. The display will be blank until programmed\n")
                f.write("5. You'll need special code to show text/graphics\n")
        
        f.write("\nTROUBLESHOOTING:\n")
        f.write("-" * 15 + "\n")
        f.write("- If something doesn't work, disconnect power immediately\n")
        f.write("- Check that all wire connections are secure\n")
        f.write("- Verify you're using the correct pins\n")
        f.write("- Make sure components are oriented correctly\n")
        f.write("- For LEDs: long leg goes to positive, short leg to negative\n\n")
        
        # Next steps
        if step_num < len(components):
            f.write("WHAT'S NEXT:\n")
            f.write("-" * 12 + "\n")
            f.write(f"Great job completing Step {step_num}!\n")
            f.write(f"In Step {step_num + 1}, you'll add the next component to build\n")
            f.write("an even more interesting circuit.\n\n")
        else:
            f.write("CONGRATULATIONS!\n")
            f.write("-" * 15 + "\n")
            f.write("You've completed building your circuit!\n")
            f.write("Now you can write code to control your components.\n")
            f.write("Check online tutorials for Arduino programming examples.\n\n")
        
        f.write("PROGRAMMING RESOURCES:\n")
        f.write("-" * 20 + "\n")
        f.write("- Arduino IDE: https://www.arduino.cc/en/software\n")
        f.write("- Arduino Tutorials: https://www.arduino.cc/en/Tutorial\n")
        f.write("- Wokwi Simulator: https://wokwi.com (test your circuit online)\n\n")
        
        f.write("=" * 70 + "\n")
        f.write("END OF STEP INSTRUCTIONS\n")
        f.write("=" * 70 + "\n")

def generate_progressive_circuits(components):
    """Generate progressive circuit diagrams step by step"""
    
    # Separate microcontroller from other components
    mcu = None
    other_components = []
    
    for comp in components:
        comp_type = comp['type'].lower()
        if any(x in comp_type for x in ['arduino', 'esp32', 'mega', 'nano']):
            mcu = comp
        else:
            other_components.append(comp)
    
    if not mcu:
        print("No microcontroller found! Adding Arduino Uno as default.")
        mcu = {"type": "wokwi-arduino-uno", "id": "mcu"}
    
    print(f"\nPROGRESSIVE CIRCUIT GENERATION")
    print("=" * 50)
    print(f"Building circuit step by step:")
    print(f"• Step 1: {mcu['type'].replace('wokwi-', '').replace('-', ' ').title()}")
    
    for i, comp in enumerate(other_components, 2):
        comp_name = comp.get('name', comp.get('description', comp['type'].replace('wokwi-', '').replace('board-', '').replace('-', ' ').title()))
        print(f"• Step {i}: + {comp_name}")
    print()
    
    # Position components with proper spacing
    arduino_center = {"top": 200, "left": 200}
    positioned_components = [mcu.copy()]
    positioned_components[0].update(arduino_center)
    
    # Position other components in a logical layout
    spacing_patterns = [
        {"top": -120, "left": 150},   # Above and right
        {"top": 120, "left": 150},    # Below and right
        {"top": -50, "left": 250},    # Above and far right
        {"top": 50, "left": 250},     # Below and far right
        {"top": -120, "left": -150},  # Above and left
        {"top": 120, "left": -150},   # Below and left
        {"top": 0, "left": 300},      # Right side
        {"top": 0, "left": -200},     # Left side
    ]
    
    for i, comp in enumerate(other_components):
        positioned_comp = comp.copy()
        if i < len(spacing_patterns):
            pattern = spacing_patterns[i]
            positioned_comp.update({
                "top": arduino_center["top"] + pattern["top"],
                "left": arduino_center["left"] + pattern["left"]
            })
        else:
            # Fallback positioning for many components
            angle = (i * 45) % 360
            import math
            radius = 200 + (i // 8) * 50
            positioned_comp.update({
                "top": arduino_center["top"] + int(radius * math.sin(math.radians(angle))),
                "left": arduino_center["left"] + int(radius * math.cos(math.radians(angle)))
            })
        
        positioned_components.append(positioned_comp)
    
    # Generate step-by-step circuits
    generated_files = []
    
    for step in range(1, len(positioned_components) + 1):
        current_components = positioned_components[:step]
        
        # Create step filename
        step_filename = f"demo_step_{step}.json"
        
        print(f"STEP {step}: ", end="")
        if step == 1:
            comp_name = mcu['type'].replace('wokwi-', '').replace('-', ' ').title()
            print(f"{comp_name}")
            print(f"--------------------------------------------------")
            print(f"   {comp_name}")
            print(f"       Position: Center (top: 200, left: 200)")
        else:
            new_comp = positioned_components[step-1]
            comp_name = new_comp.get('name', new_comp.get('description', new_comp['type'].replace('wokwi-', '').replace('board-', '').replace('-', ' ').title()))
            print(f"+ {comp_name}")
            print(f"--------------------------------------------------")
            
            # Show all components
            for i, comp in enumerate(current_components):
                if i == 0:
                    name = comp['type'].replace('wokwi-', '').replace('-', ' ').title()
                    print(f"   {name}")
                    print(f"       Position: Center (top: 200, left: 200)")
                else:
                    name = comp.get('name', comp.get('description', comp['type'].replace('wokwi-', '').replace('board-', '').replace('-', ' ').title()))
                    if i == step - 1:  # New component
                        print(f"   {name}")
                    else:
                        print(f"   {name}")
                    
                    # Calculate relative position
                    rel_top = comp.get('top', 200) - arduino_center['top']
                    rel_left = comp.get('left', 200) - arduino_center['left']
                    
                    if rel_top == 0 and rel_left == 0:
                        print(f"       Position: Same as Arduino")
                    else:
                        v_desc = f"{abs(rel_top)}px {'above' if rel_top < 0 else 'below'}" if rel_top != 0 else ""
                        h_desc = f"{abs(rel_left)}px {'left' if rel_left < 0 else 'right'}" if rel_left != 0 else ""
                        
                        if v_desc and h_desc:
                            print(f"       Position: {v_desc} and {h_desc} of Arduino")
                        elif v_desc:
                            print(f"       Position: {v_desc} of Arduino")
                        elif h_desc:
                            print(f"       Position: {h_desc} of Arduino")
        
        print(f"\nGenerating circuit diagram...")
        
        # Generate the circuit
        try:
            diagram_json = generate_circuit_diagram_json(
                parts=current_components,
                save_to_file=step_filename
            )
            
            # Parse to get statistics
            diagram_data = json.loads(diagram_json)
            total_parts = len(diagram_data['parts'])
            original_parts = len(current_components)
            auto_added = total_parts - original_parts
            connections = len(diagram_data['connections'])
            
            print(f"Circuit generated successfully!")
            print(f"   Components: {total_parts} total ({original_parts} original + {auto_added} auto-added)")
            print(f"   Connections: {connections} electrical connections")
            print(f"   Saved as: {step_filename}")
            
            # Generate instruction file for this step
            instruction_filename = f"demo_step_{step}_instructions.txt"
            generate_step_instructions(step, current_components, diagram_data, instruction_filename, arduino_center)
            print(f"   Instructions: {instruction_filename}")
            
            # Show auto-added components
            if auto_added > 0:
                auto_resistors = [p for p in diagram_data['parts'] if 'resistor' in p['type'].lower() and p['id'] not in [c['id'] for c in current_components]]
                if auto_resistors:
                    resistor_names = [f"{r['id']} ({r['attrs'].get('value', '??')}Ω)" for r in auto_resistors]
                    print(f"   Auto-added: {', '.join(resistor_names)}")
            
            # Show connections for new component
            if step > 1:
                new_comp_id = positioned_components[step-1]['id']
                new_connections = [conn for conn in diagram_data['connections'] if new_comp_id in conn[1]]
                if new_connections:
                    print(f"   {comp_name} connections:")
                    for conn in new_connections:
                        wire_color = conn[2]
                        source_pin = conn[0]
                        target_pin = conn[1]
                        print(f"      • {source_pin} → {target_pin} ({wire_color} wire)")
            
            generated_files.append(step_filename)
            
        except Exception as e:
            print(f"Error generating step {step}: {e}")
        
        print("\n" + "=" * 60 + "\n")
    
    # Final summary
    print(f"PROGRESSIVE GENERATION COMPLETE")
    print("=" * 40)
    print(f"Generated {len(generated_files)} circuit files:")
    for i, filename in enumerate(generated_files, 1):
        step_desc = "Arduino only" if i == 1 else f"Arduino + {i-1} component{'s' if i > 2 else ''}"
        print(f"   • {filename} ({step_desc})")
    
    print(f"\nAll files generated successfully!")
    print(f"You can now open these files in Wokwi to see the progressive circuit building.")
    
    # Ask if user wants to automatically capture screenshots
    print(f"\n" + "=" * 60)
    print("AUTOMATIC SCREENSHOT CAPTURE")
    print("=" * 60)
    print("Would you like to automatically capture screenshots of these circuits in Wokwi?")
    print("This will:")
    print("• Open Wokwi in your browser")
    print("• Load each circuit step automatically") 
    print("• Capture screenshots of the progressive build")
    print("• Save them as demo_step_1.png, demo_step_2.png, etc.")
    print()
    
    while True:
        auto_screenshot = input("Capture screenshots automatically? (y/n): ").strip().lower()
        if auto_screenshot in ['y', 'yes']:
            print("\nStarting automatic screenshot capture...")
            run_progressive_screenshot_automation(generated_files)
            break
        elif auto_screenshot in ['n', 'no']:
            print("\nSkipping automatic screenshots.")
            print("You can run screenshots later by choosing option 5 from the main menu.")
            break
        else:
            print("Please enter 'y' for yes or 'n' for no.")

def run_progressive_screenshot_automation(generated_files):
    """Run the proven macOS screenshot automation using generated files"""
    import webbrowser
    import os
    
    # Check for AutoGUI availability
    autogui_available = False
    try:
        import pyautogui
        import pyperclip
        autogui_available = True
    except ImportError:
        pass
    
    if not autogui_available:
        print("⚠️  Required packages not available!")
        print("Install with: pip install pyautogui pyperclip")
        print("Then choose option 5 from the main menu to run screenshot automation.")
        return
    
    # Load the generated JSON files
    demo_files = []
    for filename in generated_files:
        try:
            with open(filename, 'r') as f:
                content = f.read().strip()
                demo_files.append(content)
                print(f"✅ Loaded: {filename}")
        except Exception as e:
            print(f"⚠️  Could not read {filename}: {e}")
            return
    
    # Create screenshots directory
    screenshot_dir = "wokwi_screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    print(f"\nStarting Wokwi Progressive Circuit Automation")
    print(f"Screenshots will be saved to: {screenshot_dir}/")
    print(f"Processing {len(demo_files)} demo steps...")
    print()
    print("IMPORTANT SETUP INSTRUCTIONS:")
    print("1. Open Wokwi in your browser: https://wokwi.com/projects/342032431249883731")
    print("2. Make sure the browser window is visible and in focus")
    print("3. Click on the 'diagram.json' tab in Wokwi")
    print("4. You have 10 seconds to position your browser window...")
    print()
    
    for i in range(10, 0, -1):
        print(f"Starting automation in {i} seconds...")
        time.sleep(1)
    print("Starting automation now!")
    
    # Test clipboard functionality first
    print("Testing clipboard functionality...")
    test_text = "clipboard test 123"
    pyperclip.copy(test_text)
    time.sleep(0.1)
    result = pyperclip.paste()
    if result == test_text:
        print("✅ Clipboard working correctly")
    else:
        print(f"❌ Clipboard issue: expected '{test_text}', got '{result}'")
        print("   This may cause pasting problems...")
    
    # Test keyboard shortcuts
    print("Testing keyboard shortcuts...")
    print("   This will test Command+A and Command+V in 3 seconds...")
    print("   Position a text editor or text field in focus...")
    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    # Test select all
    print("   Testing Command+A (select all)...")
    try:
        pyautogui.hotkey('command', 'a')
        time.sleep(0.5)
        print("   ✅ Command+A worked")
    except Exception as e:
        print(f"   ❌ Command+A failed: {e}")
    
    # Test paste
    print("   Testing Command+V (paste)...")
    try:
        pyautogui.hotkey('command', 'v')
        time.sleep(0.5)
        print("   ✅ Command+V worked")
    except Exception as e:
        print(f"   ❌ Command+V failed: {e}")
    
    print("   ✅ Keyboard shortcuts tested")
    print()
    
    # Example coordinates (these will need to be adjusted for user's screen)
    diagram_tab_pos = (297, 177)  # Click "diagram.json" tab
    code_area_pos = (400, 400)    # Text editor area
    empty_click_pos = (700, 300)  # Area on the right with the circuit view
    
    # Delay times
    load_delay = 8       # seconds to wait for page load
    update_delay = 4     # seconds to wait for diagram.json update to reflect
    
    # Step 1: Open Wokwi project
    url = "https://wokwi.com/projects/342032431249883731"
    webbrowser.open(url)
    time.sleep(load_delay)
    
    for i, text in enumerate(demo_files, start=1):
        print(f"Processing Step {i}/{len(demo_files)}...")
        
        # Step 2: Ensure browser is focused first (CRITICAL for macOS)
        print(f"   Ensuring browser focus...")
        pyautogui.click(diagram_tab_pos)  # Click tab first
        time.sleep(0.3)
        pyautogui.click(diagram_tab_pos)  # Click twice to be sure
        time.sleep(0.5)
    
        # Step 3: Click diagram.json tab multiple times to ensure it's selected
        print(f"   Selecting diagram.json tab...")
        pyautogui.click(diagram_tab_pos)
        time.sleep(0.3)
    
        # Step 4: Click in the text editor area and ensure it's focused
        print(f"   Focusing text editor...")
        pyautogui.click(code_area_pos)
        time.sleep(0.3)
        pyautogui.click(code_area_pos)  # Click twice for focus
        time.sleep(0.5)
        
        # Step 5: Clear clipboard first, then copy new text
        print(f"   Preparing JSON text ({len(text)} characters)...")
        pyperclip.copy("")  # Clear clipboard
        time.sleep(0.1)
        pyperclip.copy(text)  # Copy our JSON
        time.sleep(0.3)
        
        # Verify clipboard content
        clipboard_content = pyperclip.paste()
        if len(clipboard_content) < 50:
            print(f"   WARNING: Clipboard content seems short: '{clipboard_content[:50]}...'")
        else:
            print(f"   ✅ Clipboard ready: {len(clipboard_content)} characters")
        
        # Step 6: Select all and replace (macOS-compatible method)
        print(f"   Selecting all text...")
        # Use triple-click first (more reliable), then Command+A as backup
        pyautogui.click(code_area_pos, clicks=3)  # Triple-click selects all
        time.sleep(0.3)
        pyautogui.hotkey('command', 'a')  # Backup method
        time.sleep(0.5)
        
        # Step 7: Paste the new JSON
        print(f"   Pasting JSON into Wokwi...")
        pyautogui.hotkey('command', 'v')
        time.sleep(1.5)  # Give more time for paste to complete
        print(f"   ✅ JSON pasted successfully")
    
        # Step 8: Wait for auto-update
        print(f"   Waiting {update_delay}s for circuit to update...")
        time.sleep(update_delay)
    
        # Step 9: Click on empty area (so text cursor not visible in screenshot)
        pyautogui.click(empty_click_pos)
        time.sleep(0.5)
    
        # Step 10: Screenshot of circuit area
        screenshot_path = f"{screenshot_dir}/demo_step_{i}.png"
        print(f"   Taking circuit screenshot: {screenshot_path}")
        screenshot = pyautogui.screenshot(region=(672, 287, 1004, 860))  
        screenshot.save(screenshot_path)
        
        # Text-to-speech announcement
        try:
            import subprocess
            subprocess.run(['say', 'Screenshot taken!'], check=False)
        except Exception:
            pass  # Silently fail if TTS not available
        
        print(f"   ✅ Step {i} completed: {screenshot_path}")
        time.sleep(1)  # Brief pause between steps
    
    print()
    print("All screenshots captured successfully!")
    print(f"Check the '{screenshot_dir}' folder for your progressive circuit images:")
    for i in range(1, len(demo_files) + 1):
        step_desc = "Arduino only" if i == 1 else f"Arduino + {i-1} component{'s' if i > 2 else ''}"
        print(f"   • demo_step_{i}.png - {step_desc}")
    print()
    print("You now have visual documentation of your progressive circuit!")
    print("Use these images for tutorials, presentations, or documentation.")

def wokwi_autogui_mode():
    """Mode that uses existing demo_step_X.json files for Wokwi AutoGUI automation"""
    from pathlib import Path
    import webbrowser
    import time
    
    # Try to import pyautogui
    try:
        import pyautogui
        autogui_available = True
    except ImportError:
        autogui_available = False
    
    print("Wokwi AutoGUI Automation Mode")
    print("=" * 35)
    print()
    print("This mode will automatically load your demo step files into Wokwi")
    print("and capture screenshots of each progressive circuit step.")
    print()
    
    # Find existing demo step files
    demo_files = []
    for i in range(1, 10):
        step_file = Path(f"demo_step_{i}.json")
        if step_file.exists():
            try:
                with open(step_file, 'r') as f:
                    content = f.read()
                    json.loads(content)  # Validate JSON
                    demo_files.append({
                        "file": step_file.name,
                        "content": content,
                        "step": i
                    })
            except json.JSONDecodeError:
                print(f"⚠️  Warning: {step_file.name} contains invalid JSON")
            except Exception as e:
                print(f"⚠️  Warning: Error reading {step_file.name}: {e}")
    
    if not demo_files:
        print("❌ No demo step files found!")
        print("\nTo create demo step files:")
        print("1. Choose option 1, 2, 3, or 4 to generate components")
        print("2. Select progressive generation mode")
        print("3. Then return to this AutoGUI mode")
        return
    
    print(f"✅ Found {len(demo_files)} demo step files:")
    for file_info in demo_files:
        print(f"   • {file_info['file']}")
    
    if not autogui_available:
        print("\n⚠️  PyAutoGUI not available!")
        print("Install with: pip install pyautogui")
        print("\nFor now, showing you the demo file contents that would be used:")
        
        for i, file_info in enumerate(demo_files, 1):
            print(f"\n--- Step {i}: {file_info['file']} ---")
            # Show a preview of the JSON
            try:
                data = json.loads(file_info['content'])
                print(f"Components: {len(data.get('parts', []))}")
                print(f"Connections: {len(data.get('connections', []))}")
                
                # Show component names
                parts = data.get('parts', [])
                if parts:
                    print("Parts:")
                    for part in parts:
                        part_name = part['type'].replace('wokwi-', '').replace('board-', '').replace('-', ' ').title()
                        print(f"  - {part_name} (ID: {part['id']})")
            except:
                print("Error parsing JSON content")
        
        return
    
    # Configuration for AutoGUI
    print(f"\nAutoGUI Configuration:")
    print("=" * 25)
    
    # Get Wokwi URL
    default_url = "https://wokwi.com/projects/342032431249883731"
    url = input(f"Wokwi project URL (or press Enter for default): ").strip()
    if not url:
        url = default_url
    
    print(f"Will use: {url}")
    
    # Get timing preferences
    print(f"\nTiming Settings:")
    try:
        load_delay = int(input("Page load delay in seconds (default 8): ").strip() or "8")
        update_delay = int(input("Circuit update delay in seconds (default 4): ").strip() or "4")
    except ValueError:
        load_delay = 8
        update_delay = 4
    
    # Create screenshots directory
    screenshot_dir = Path("wokwi_screenshots")
    screenshot_dir.mkdir(exist_ok=True)
    
    print(f"\nStarting AutoGUI automation...")
    print("=" * 35)
    print("⚠️  IMPORTANT: Position your browser window so Wokwi is visible!")
    print("💡 The automation will start in 5 seconds...")
    
    for i in range(5, 0, -1):
        print(f"   Starting in {i}...")
        time.sleep(1)
    
    # Open Wokwi
    print(f"\n🌐 Opening Wokwi: {url}")
    webbrowser.open(url)
    
    print(f"⏳ Waiting {load_delay} seconds for page to load...")
    time.sleep(load_delay)
    
    # Coordinates (these are the same as in wokwi_autogui.py)
    diagram_tab_pos = (297, 177)
    code_area_pos = (400, 400)
    empty_click_pos = (900, 300)
    screenshot_region = (672, 287, 1004, 660)
    
    print(f"\n🤖 Starting progressive automation...")
    
    for file_info in demo_files:
        step_num = file_info['step']
        content = file_info['content']
        
        print(f"\n🔄 Processing Step {step_num}: {file_info['file']}")
        
        try:
            # Click diagram.json tab
            print("   📋 Clicking diagram.json tab...")
            pyautogui.click(diagram_tab_pos)
            time.sleep(0.3)
            
            # Select all and replace text
            print("   ✏️  Updating circuit JSON...")
            pyautogui.click(code_area_pos)
            pyautogui.hotkey('cmd', 'a')  # macOS
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.2)
            pyautogui.write(content, interval=0.001)
            
            # Wait for update
            print(f"   ⏳ Waiting {update_delay}s for circuit to update...")
            time.sleep(update_delay)
            
            # Clear cursor
            pyautogui.click(empty_click_pos)
            time.sleep(0.5)
            
            # Take screenshot
            screenshot_path = screenshot_dir / f"demo_step_{step_num}.png"
            print(f"   📸 Capturing: {screenshot_path}")
            pyautogui.screenshot(str(screenshot_path), region=screenshot_region)
            
            # Text-to-speech announcement
            try:
                import subprocess
                subprocess.run(['say', 'Screenshot taken!'], check=False)
            except Exception:
                pass  # Silently fail if TTS not available
            
            print(f"   ✅ Step {step_num} completed!")
            
        except Exception as e:
            print(f"   ❌ Error in step {step_num}: {e}")
    
    print(f"\n🎉 AutoGUI automation completed!")
    print(f"📁 Screenshots saved in: {screenshot_dir}/")
    
    # Show results
    print(f"\nGenerated Screenshots:")
    for file_info in demo_files:
        screenshot_file = screenshot_dir / f"demo_step_{file_info['step']}.png"
        if screenshot_file.exists():
            print(f"   ✅ {screenshot_file.name}")
        else:
            print(f"   ❌ {screenshot_file.name} (failed)")
    
    print(f"\n🎯 What you can do next:")
    print("• Review the captured screenshots")
    print("• Use them for documentation or presentations")
    print("• Share your progressive circuit demos")
    print("• Adjust coordinates in the script if clicks were off-target")

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
    print("5. Wokwi AutoGUI - Use existing demo files for browser automation")
    print()
    
    # Mode selection
    while True:
        mode = input("Enter your choice (1, 2, 3, 4, or 5): ").strip()
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
        elif mode == "5":
            wokwi_autogui_mode()
            return  # Exit after AutoGUI mode
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")
    
    print(f"\nYour circuit will have {len(components)} components:")
    for part in components:
        name = part.get('name', part.get('description', part['type'].replace('wokwi-', '').replace('board-', '').replace('-', ' ').title()))
        confidence_info = ""
        if 'ai_confidence' in part:
            confidence_info = f" [AI Confidence: {part['ai_confidence']}/10]"
        print(f"   - {name} (ID: {part['id']}){confidence_info}")
        if 'wiring_notes' in part:
            print(f"     Note: {part['wiring_notes']}")
    
    # Ask user about generation mode
    print(f"\nChoose generation mode:")
    print("1. Single circuit file - Generate one complete circuit")
    print("2. Progressive circuit files - Generate step-by-step circuits")
    
    while True:
        gen_mode = input("Enter your choice (1 or 2): ").strip()
        if gen_mode in ["1", "2"]:
            break
        print("Invalid choice. Please enter 1 or 2.")
    
    if gen_mode == "1":
        # Original single file generation
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
    
    else:
        # Progressive generation
        print(f"\nGenerating progressive circuit diagrams...")
        generate_progressive_circuits(components)

if __name__ == "__main__":
    demo_rag_ai_circuit_generator()
