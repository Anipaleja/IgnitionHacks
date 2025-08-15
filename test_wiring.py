#!/usr/bin/env python3
"""
Test the circuit generator to ensure all components are properly wired
"""

from main import generate_circuit_diagram_json
import json

def test_component_wiring():
    """Test that all components get properly wired"""
    
    print("Testing component wiring...")
    
    # Test case 1: LED and resistor
    print("\nTest 1: LED and resistor")
    parts1 = [
        {"type": "wokwi-arduino-uno", "id": "uno"},
        {"type": "wokwi-led", "id": "led1"},
        {"type": "wokwi-resistor", "id": "r1"}
    ]
    
    diagram1 = generate_circuit_diagram_json(parts1, save_to_file="test_led_resistor.json")
    data1 = json.loads(diagram1)
    print(f"Components: {len(data1['parts'])}")
    print(f"Connections: {len(data1['connections'])}")
    
    # Test case 2: Display and sensor
    print("\nTest 2: Display and sensor")
    parts2 = [
        {"type": "wokwi-arduino-mega", "id": "mega"},
        {"type": "board-ssd1306", "id": "oled1"},
        {"type": "wokwi-dht22", "id": "temp1"}
    ]
    
    diagram2 = generate_circuit_diagram_json(parts2, save_to_file="test_display_sensor.json")
    data2 = json.loads(diagram2)
    print(f"Components: {len(data2['parts'])}")
    print(f"Connections: {len(data2['connections'])}")
    
    # Test case 3: Button and buzzer
    print("\nTest 3: Button and buzzer")
    parts3 = [
        {"type": "wokwi-esp32-devkit-v1", "id": "esp32"},
        {"type": "wokwi-pushbutton", "id": "btn1"},
        {"type": "wokwi-buzzer", "id": "bz1"}
    ]
    
    diagram3 = generate_circuit_diagram_json(parts3, save_to_file="test_button_buzzer.json")
    data3 = json.loads(diagram3)
    print(f"Components: {len(data3['parts'])}")
    print(f"Connections: {len(data3['connections'])}")
    
    print("\nAll tests completed. Check the generated files for proper wiring.")

if __name__ == "__main__":
    test_component_wiring()
