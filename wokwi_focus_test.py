#!/usr/bin/env python3
"""
Robust macOS Wokwi automation - focus and typing approach
"""

import pyautogui
import pyperclip
import time
import os

# Configure for macOS
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

# Shorter JSON for testing
json_texts = [
    '{"version":1,"parts":[{"type":"wokwi-arduino-uno","id":"mcu","top":200,"left":200}],"connections":[]}',
    '{"version":1,"parts":[{"type":"wokwi-arduino-uno","id":"mcu","top":200,"left":200},{"type":"wokwi-led","id":"led1","top":100,"left":350}],"connections":[["mcu:13","led1:A","red"],["mcu:GND.1","led1:C","black"]]}',
]

screenshot_dir = "wokwi_screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

print("=== ROBUST MACOS WOKWI AUTOMATION ===")
print()
print("1. Open Wokwi: https://wokwi.com/projects/342032431249883731")
print("2. Position browser so you can see the diagram.json tab")
print("3. We'll get coordinates and test focus")
print()

def get_coordinates(description):
    input(f"Position mouse over {description} and press Enter: ")
    x, y = pyautogui.position()
    print(f"   Recorded: ({x}, {y})")
    return (x, y)

# Get coordinates
diagram_tab_pos = get_coordinates("the 'diagram.json' tab")
code_area_pos = get_coordinates("the text editor area")

print()
print("Testing browser focus and shortcuts...")

# Click in the browser to ensure focus
pyautogui.click(code_area_pos)
time.sleep(1)

# Test keyboard shortcuts in the browser
print("Testing select all in browser...")
pyperclip.copy("test content")
time.sleep(0.2)

# Try Command+A in the focused browser
pyautogui.hotkey('command', 'a')
time.sleep(0.5)

# Try Command+V in the focused browser  
pyautogui.hotkey('command', 'v')
time.sleep(0.5)

print("If you see 'test content' in the browser, shortcuts work!")
print()

# Wait for user confirmation
input("Did the shortcuts work in the browser? (Press Enter to continue or Ctrl+C to stop): ")

print("Starting automation with focus handling...")
time.sleep(2)

for i, text in enumerate(json_texts, start=1):
    print(f"\n📝 Step {i}/{len(json_texts)}...")
    
    # Step 1: Ensure browser focus by clicking multiple places
    print("   Ensuring browser focus...")
    pyautogui.click(diagram_tab_pos)  # Click tab
    time.sleep(0.5)
    pyautogui.click(code_area_pos)    # Click editor
    time.sleep(0.5)
    pyautogui.click(code_area_pos)    # Click again to be sure
    time.sleep(0.5)
    
    # Step 2: Copy JSON to clipboard
    print(f"   Copying JSON ({len(text)} chars)...")
    pyperclip.copy(text)
    time.sleep(0.3)
    
    # Step 3: Select all with multiple methods
    print("   Selecting all content...")
    
    # Method 1: Triple-click to select all
    pyautogui.click(code_area_pos, clicks=3)
    time.sleep(0.5)
    
    # Method 2: Also try Command+A as backup
    pyautogui.hotkey('command', 'a')
    time.sleep(0.5)
    
    # Step 4: Paste
    print("   Pasting JSON...")
    success = False
    
    # Try paste with Command+V
    try:
        pyautogui.hotkey('command', 'v')
        time.sleep(1)
        success = True
        print("   ✅ Paste with Command+V")
    except:
        print("   ⚠️ Command+V failed")
    
    # Fallback: Type directly (slower but more reliable)
    if not success:
        print("   Fallback: typing directly...")
        # Clear the area first
        pyautogui.hotkey('command', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.2)
        # Type the JSON
        pyautogui.write(text, interval=0.005)
        time.sleep(1)
        print("   ✅ Text typed directly")
    
    # Step 5: Wait and screenshot
    print("   Waiting for update...")
    time.sleep(3)
    
    print("   Taking screenshot...")
    screenshot = pyautogui.screenshot()
    screenshot_path = f"{screenshot_dir}/focus_test_{i}.png"
    screenshot.save(screenshot_path)
    
    size = os.path.getsize(screenshot_path)
    print(f"   ✅ Saved: {screenshot_path} ({size:,} bytes)")

print("\n🎉 Test complete!")
print("Check the screenshots to see if the JSON was properly loaded into Wokwi.")
