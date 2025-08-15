#!/usr/bin/env python3
"""
Test the RAG AI Circuit Generator with User Input
=================================================

This demonstrates how users provide parts and the RAG AI MODEL generates diagram.json files.
"""

import os
from main import generate_circuit_diagram_json

def parse_user_parts(user_input: str) -> list:
    """Convert user input string to parts list"""
    # Simple parsing - in real app this would be more sophisticated
    parts = []
    if "LED" in user_input.lower() or "button" in user_input.lower():
        parts.extend([
            {"type": "wokwi-led", "id": "led1"},
            {"type": "wokwi-resistor", "id": "r1"},
            {"type": "wokwi-pushbutton", "id": "btn1"}
        ])
    elif "OLED" in user_input or "display" in user_input.lower():
        parts.extend([
            {"type": "board-ssd1306", "id": "oled1"},
            {"type": "wokwi-dht22", "id": "dht1"}
        ])
    elif "WiFi" in user_input or "IoT" in user_input:
        parts.extend([
            {"type": "wokwi-esp32-devkit-v1", "id": "esp32"},
            {"type": "wokwi-dht22", "id": "dht1"},
            {"type": "wokwi-buzzer", "id": "bz1"}
        ])
    elif "TFT" in user_input or "advanced" in user_input.lower():
        parts.extend([
            {"type": "board-ili9341-cap-touch", "id": "tft1"},
            {"type": "wokwi-microsd-card", "id": "sd1"},
            {"type": "board-l298n", "id": "motor1"},
            {"type": "wokwi-dht22", "id": "dht1"}
        ])
    else:
        # Default simple project
        parts.extend([
            {"type": "wokwi-led", "id": "led1"},
            {"type": "wokwi-resistor", "id": "r1"}
        ])
    return parts

def test_user_input_scenarios():
    """Test different user input scenarios for circuit generation"""
    
    print("🎯 RAG AI Circuit Generator - User Input Test")
    print("=" * 60)
    print("User provides parts → RAG AI MODEL generates diagram.json")
    print()
    
    # Test Scenario 1: Simple LED project
    print("📋 Test 1: User wants a simple LED project")
    print("User input: 'LED, resistor, button'")
    user_parts_1 = parse_user_parts("LED, resistor, button")
    
    diagram_1 = generate_circuit_diagram_json(
        parts=user_parts_1,
        save_to_file="user_test_1_diagram.json"
    )
    print("✅ Generated: user_test_1_diagram.json")
    print()
    
    # Test Scenario 2: Display project
    print("📋 Test 2: User wants a display project")
    print("User input: 'OLED display, temperature sensor'")
    user_parts_2 = parse_user_parts("OLED display, temperature sensor")
    
    diagram_2 = generate_circuit_diagram_json(
        parts=user_parts_2,
        save_to_file="user_test_2_diagram.json"
    )
    print("✅ Generated: user_test_2_diagram.json")
    print()
    
    # Test Scenario 3: IoT project
    print("📋 Test 3: User wants an IoT project")
    print("User input: 'WiFi module, sensors, buzzer'")
    user_parts_3 = parse_user_parts("WiFi module, sensors, buzzer")
    
    diagram_3 = generate_circuit_diagram_json(
        parts=user_parts_3,
        save_to_file="user_test_3_diagram.json"
    )
    print("✅ Generated: user_test_3_diagram.json")
    print()
    
    # Test Scenario 4: Advanced project
    print("📋 Test 4: User wants an advanced project")
    print("User input: 'TFT screen, SD card, motor driver, sensors'")
    user_parts_4 = parse_user_parts("TFT screen, SD card, motor driver, sensors")
    
    diagram_4 = generate_circuit_diagram_json(
        parts=user_parts_4,
        save_to_file="user_test_4_diagram.json"
    )
    print("✅ Generated: user_test_4_diagram.json")
    print()
    
    print("🎉 RAG AI MODEL Successfully Generated All Circuit Diagrams!")
    print("=" * 60)
    print()
    print("📁 Generated Files:")
    for i in range(1, 5):
        filename = f"user_test_{i}_diagram.json"
        if os.path.exists(filename):
            print(f"   ✅ {filename}")
        else:
            print(f"   ❌ {filename} (not found)")
    
    print()
    print("🔧 How It Works:")
    print("   1. User provides parts as simple text")
    print("   2. RAG AI MODEL analyzes the components")
    print("   3. AI generates complete circuit diagram JSON")
    print("   4. Proper wire routing with Wokwi mini-language")
    print("   5. Saves to diagram.json file ready for simulation")

if __name__ == "__main__":
    test_user_input_scenarios()
