#!/usr/bin/env python3
"""
Coordinate finder for Wokwi automation
Use this to find the right click positions for your screen
"""

import pyautogui
import time

print("COORDINATE FINDER")
print("================")
print()
print("Instructions:")
print("1. Open Wokwi in your browser: https://wokwi.com/projects/342032431249883731")
print("2. Make sure you can see the 'diagram.json' tab and the text editor")
print("3. This script will show your mouse position every second")
print("4. Move your mouse to each location and note the coordinates:")
print("   - diagram.json tab")
print("   - text editor area (where you can type)")
print("   - empty area in the circuit view")
print()
print("Press Ctrl+C to stop")
print()

try:
    while True:
        x, y = pyautogui.position()
        print(f"Mouse position: ({x}, {y})", end='\r')
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nDone! Use these coordinates in demo1.py")
