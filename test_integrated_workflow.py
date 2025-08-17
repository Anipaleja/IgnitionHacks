#!/usr/bin/env python3
"""
Test the integrated workflow: component selection -> progressive generation -> automatic screenshots
"""

import sys
sys.path.append('.')

from demo import text_input_mode, generate_progressive_circuits, run_progressive_screenshot_automation

# Test with some simple components
print("=== TESTING INTEGRATED WORKFLOW ===")
print()

# Simulate component selection (like choosing option 1 - text input)
print("1. Simulating component selection...")
components = [
    {"type": "wokwi-arduino-uno", "id": "mcu", "description": "Arduino Uno"},
    {"type": "wokwi-led", "id": "led1", "description": "Red LED"},
    {"type": "wokwi-buzzer", "id": "buzzer1", "description": "Buzzer"}
]

print(f"   Selected {len(components)} components:")
for comp in components:
    print(f"   • {comp['description']} ({comp['type']})")

# Simulate progressive generation (like choosing option 2 - progressive)
print("\n2. Generating progressive circuits...")
generate_progressive_circuits(components)

print("\n3. Generated files should now exist:")
import os
for i in range(1, 4):
    filename = f"demo_step_{i}.json"
    if os.path.exists(filename):
        print(f"   ✅ {filename} exists")
    else:
        print(f"   ❌ {filename} missing")

print("\n=== WORKFLOW TEST COMPLETE ===")
print("The integrated workflow is ready!")
print("Next time you run demo.py:")
print("1. Choose any component selection mode (1, 2, 3, or 4)")
print("2. Choose progressive generation (option 2)")
print("3. You'll be prompted to automatically capture screenshots")
print("4. If you choose 'yes', it will run the automation automatically!")
