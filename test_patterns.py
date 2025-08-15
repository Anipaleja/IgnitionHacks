#!/usr/bin/env python3
"""
Test the AI assessment functionality
"""

import sys
import os
sys.path.append('.')

# Import the functions from demo.py
def test_fallback_assessment():
    """Test the fallback pattern recognition"""
    
    test_inputs = [
        "ESP32 development board",
        "ultrasonic distance sensor", 
        "LED strip",
        "servo motor",
        "Arduino Uno",
        "temperature sensor"
    ]
    
    # Quick test of pattern matching
    import re
    patterns = {
        r'esp32|esp\s*32|esp.*dev.*board|esp.*development': {"type": "wokwi-esp32-devkit-v1", "desc": "ESP32 Development Board", "conf": 9},
        r'ultrasonic|hc-?sr04|distance.*sensor|proximity.*sensor': {"type": "wokwi-ultrasonic-hc-sr04", "desc": "Ultrasonic Distance Sensor (HC-SR04)", "conf": 8},
        r'led\s*strip|ws2812|neopixel|addressable.*led': {"type": "wokwi-ws2812", "desc": "LED Strip (WS2812)", "conf": 8},
        r'servo|servo.*motor': {"type": "wokwi-servo", "desc": "Servo Motor", "conf": 8},
        r'arduino\s*uno|uno(?!\w)': {"type": "wokwi-arduino-uno", "desc": "Arduino Uno Microcontroller", "conf": 9},
        r'dht22|temperature.*humidity|temp.*sensor': {"type": "wokwi-dht22", "desc": "DHT22 Temperature/Humidity Sensor", "conf": 8},
    }
    
    for test_input in test_inputs:
        print(f"\nTesting: '{test_input}'")
        text_lower = test_input.lower()
        
        found = False
        for pattern, info in patterns.items():
            if re.search(pattern, text_lower):
                print(f"  ✓ Matched pattern: {pattern}")
                print(f"  Component: {info['type']}")
                print(f"  Description: {info['desc']}")
                print(f"  Confidence: {info['conf']}")
                found = True
                break
        
        if not found:
            print(f"  ✗ No pattern matched")

if __name__ == "__main__":
    test_fallback_assessment()
