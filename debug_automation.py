#!/usr/bin/env python3
"""
Simple debug script to test clipboard and basic automation
"""

import pyautogui
import pyperclip
import time

# Test JSON (shorter version for testing)
test_json = '{"version":1,"author":"Test","parts":[{"type":"wokwi-arduino-uno","id":"mcu","top":200,"left":200}],"connections":[]}'

print("=== CLIPBOARD AND AUTOMATION DEBUG ===")
print()

# Test 1: Clipboard functionality
print("1. Testing clipboard...")
pyperclip.copy(test_json)
time.sleep(0.1)
result = pyperclip.paste()
print(f"   Original length: {len(test_json)}")
print(f"   Clipboard length: {len(result)}")
print(f"   Match: {result == test_json}")
if result != test_json:
    print(f"   Original: {test_json[:50]}...")
    print(f"   Clipboard: {result[:50]}...")
print()

# Test 2: Mouse position
print("2. Current mouse position:")
x, y = pyautogui.position()
print(f"   Mouse at: ({x}, {y})")
print()

# Test 3: Simple automation test
print("3. Testing basic automation...")
print("   In 5 seconds, this will:")
print("   - Click at current mouse position")
print("   - Try to select all (Cmd+A)")
print("   - Try to paste the JSON")
print("   - Take a screenshot")
print()

for i in range(5, 0, -1):
    print(f"   Starting in {i}...")
    time.sleep(1)

print("   Executing automation test...")

# Get current mouse position and use it
x, y = pyautogui.position()
print(f"   Clicking at ({x}, {y})...")
pyautogui.click(x, y)
time.sleep(0.5)

print("   Selecting all...")
pyautogui.hotkey('cmd', 'a')
time.sleep(0.5)

print("   Pasting...")
pyautogui.hotkey('cmd', 'v')
time.sleep(1)

print("   Taking screenshot...")
screenshot = pyautogui.screenshot()
screenshot.save('debug_test.png')
print("   Screenshot saved as debug_test.png")

print()
print("=== TEST COMPLETE ===")
print("Check debug_test.png to see what was captured")
print("If you see the JSON pasted somewhere, the automation is working!")
