#!/usr/bin/env python3
"""
Wokwi Progressive Circuit Automation
====================================

This script automatically loads    # Step 2: Ensure browser is focused first (CRITICAL for macOS)
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
    time.sleep(0.5)e demo circuit files into Wokwi
and captures screenshots of each step. 

Your demo files:
- Step 1: Arduino Uno only
- Step 2: Arduino + LED (with 220Ω resistor)  
- Step 3: Arduino + LED + Buzzer (distributed ground pins)
- Step 4: Complete circuit with OLED display

Usage:
1. Make sure Wokwi is open and visible in your browser
2. Run this script: python demo1.py
3. Watch the automation capture progressive screenshots
4. Find results in wokwi_screenshots/ folder

Note: Adjust coordinates if clicks miss their targets
"""

import pyautogui
import time
import webbrowser
import pyperclip  # For clipboard operations

# ---------- CONFIGURATION ----------
url = "https://wokwi.com/projects/342032431249883731"

# Demo step JSON files from your progressive circuit generation
json_texts = [
    # Step 1: Arduino Uno only
    '{"version":1,"author":"RAG AI Generator","editor":"wokwi","parts":[{"type":"wokwi-arduino-uno","id":"mcu","top":200,"left":200}],"connections":[],"dependencies":{}}',
    
    # Step 2: Arduino Uno + LED
    '{"version":1,"author":"RAG AI Generator","editor":"wokwi","parts":[{"type":"wokwi-arduino-uno","id":"mcu","top":200,"left":200},{"type":"wokwi-led","id":"comp1","top":80,"left":350},{"type":"wokwi-resistor","id":"R1","top":110,"left":300,"attrs":{"value":"220"}}],"connections":[["mcu:2","R1:1","red",["v-47","h3","*","h-2","v2"]],["R1:2","comp1:A","red",["h10","*","h-5"]],["mcu:GND.1","comp1:C","black",["v-12","*","v4"]]],"dependencies":{}}',
    
    # Step 3: Arduino Uno + LED + Buzzer
    '{"version":1,"author":"RAG AI Generator","editor":"wokwi","parts":[{"type":"wokwi-arduino-uno","id":"mcu","top":200,"left":200},{"type":"wokwi-led","id":"comp1","top":80,"left":350},{"type":"wokwi-buzzer","id":"comp2","top":320,"left":350},{"type":"wokwi-resistor","id":"R1","top":110,"left":300,"attrs":{"value":"220"}}],"connections":[["mcu:2","R1:1","red",["v-47","h3","*","h-2","v2"]],["R1:2","comp1:A","red",["h10","*","h-5"]],["mcu:GND.1","comp1:C","black",["v-12","*","v4"]],["mcu:GND.2","comp2:1","black",["v12","*","v-4"]],["mcu:3","comp2:2","purple",["v-23","h3","*","h-2","v-2"]]],"dependencies":{}}',
    
    # Step 4: Complete circuit with OLED
    '{"version":1,"author":"RAG AI Generator","editor":"wokwi","parts":[{"type":"wokwi-arduino-uno","id":"mcu","top":200,"left":200},{"type":"wokwi-led","id":"comp1","top":80,"left":350},{"type":"wokwi-buzzer","id":"comp2","top":320,"left":350},{"type":"board-ssd1306","id":"comp3","top":150,"left":450},{"type":"wokwi-resistor","id":"R1","top":110,"left":300,"attrs":{"value":"220"}}],"connections":[["mcu:2","R1:1","red",["v-47","h3","*","h-2","v2"]],["R1:2","comp1:A","red",["h10","*","h-5"]],["mcu:GND.1","comp1:C","black",["v-12","*","v4"]],["mcu:GND.2","comp2:1","black",["v12","*","v-4"]],["mcu:3","comp2:2","purple",["v-23","h3","*","h-2","v-2"]],["mcu:GND.3","comp3:GND","black",["v-5","*","v1"]],["mcu:3.3V","comp3:VCC","red",["v-20","*","v9"]],["mcu:A4","comp3:SDA","gold",["v-30","h8","*","v1"]],["mcu:A5","comp3:SCL","cyan",["v-35","h6","*","v1"]]],"dependencies":{}}'
]

# File save naming pattern
screenshot_dir = "wokwi_screenshots"
file_prefix = "demo_step"

# Delay times
load_delay = 8       # seconds to wait for page load
update_delay = 4     # seconds to wait for diagram.json update to reflect
click_delay = 0.3    # short delay between clicks
# -----------------------------------

# Create screenshots directory
import os
os.makedirs(screenshot_dir, exist_ok=True)

print(f"Starting Wokwi Progressive Circuit Automation")
print(f"Screenshots will be saved to: {screenshot_dir}/")
print(f"Processing {len(json_texts)} demo steps...")
print()

# Step 1: Open Wokwi project
webbrowser.open(url)
time.sleep(load_delay)

# You will need to manually position the browser window before running this,
# or use pyautogui to click on specific coordinates after you record them.
# Record positions with: pyautogui.position()

# Example coordinates (replace with your own):
diagram_tab_pos = (297, 177)  # Click "diagram.json" tab
code_area_pos = (400, 400)    # Text editor area
empty_click_pos = (900, 300)  # Area on the right with the circuit view

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

for i, text in enumerate(json_texts, start=1):
    print(f"Processing Step {i}/4...")
    
    # Step 2: Ensure browser is focused first
    print(f"   Focusing browser window...")
    pyautogui.click(500, 100)  # Click somewhere in browser area
    time.sleep(0.5)
    
    # Step 3: Click diagram.json tab multiple times to ensure it's selected
    print(f"   Clicking diagram.json tab...")
    pyautogui.click(diagram_tab_pos)
    time.sleep(0.3)
    pyautogui.click(diagram_tab_pos)  # Click twice to be sure
    time.sleep(0.5)

    # Step 4: Click in the text editor area and ensure it's focused
    print(f"   Clicking in text editor...")
    pyautogui.click(code_area_pos)
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

    # Step 4: Wait for auto-update
    print(f"   Waiting {update_delay}s for circuit to update...")
    time.sleep(update_delay)

    # Step 5: Click on empty area (so text cursor not visible in screenshot)
    pyautogui.click(empty_click_pos)
    time.sleep(0.5)

    # Step 6: Take full screenshot first to see what we're capturing
    debug_path = f"{screenshot_dir}/debug_full_{i}.png"
    print(f"   Taking debug screenshot: {debug_path}")
    debug_screenshot = pyautogui.screenshot()
    debug_screenshot.save(debug_path)

    # Step 7: Screenshot of circuit area
    screenshot_path = f"{screenshot_dir}/{file_prefix}_{i}.png"
    print(f"   Taking circuit screenshot: {screenshot_path}")
    screenshot = pyautogui.screenshot(region=(672, 287, 1004, 860))  
    screenshot.save(screenshot_path)
    # ^ region = (x, y, width, height) — adjust for your monitor
    
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
print("   • demo_step_1.png - Arduino Uno only")
print("   • demo_step_2.png - Arduino + LED") 
print("   • demo_step_3.png - Arduino + LED + Buzzer")
print("   • demo_step_4.png - Complete circuit with OLED")
print()
print("You now have visual documentation of your progressive circuit!")
print("Use these images for tutorials, presentations, or documentation.")