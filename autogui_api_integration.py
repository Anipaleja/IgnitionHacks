#!/usr/bin/env python3
"""
AutoGUI Integration with Flask API
==================================

This script shows how to combine the Flask API with AutoGUI automation
for complete end-to-end circuit generation and testing in Wokwi.
"""

import requests
import json
import time
import webbrowser
import tempfile
from pathlib import Path

# Try to import pyautogui, install if not available
try:
    import pyautogui
    AUTOGUI_AVAILABLE = True
except ImportError:
    print("PyAutoGUI not available. Install with: pip install pyautogui")
    AUTOGUI_AVAILABLE = False

# Configuration
API_BASE_URL = "http://localhost:5001"
WOKWI_URL = "https://wokwi.com/projects/new/arduino-uno"

def generate_circuit_via_api(description):
    """Generate circuit using the Flask API"""
    try:
        data = {"description": description}
        response = requests.post(f"{API_BASE_URL}/api/generate", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API: Circuit generated with {result['total_parts']} parts")
            return result['circuit_json']
        else:
            error = response.json()
            print(f"❌ API Error: {error['error']}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ API server not running. Start it with: python start_api.py --port 5001")
        return None
    except Exception as e:
        print(f"❌ API Error: {e}")
        return None

def open_wokwi_with_circuit(circuit_json):
    """Open Wokwi in browser and load the circuit"""
    print("🌐 Opening Wokwi in browser...")
    
    # Open Wokwi
    webbrowser.open(WOKWI_URL)
    
    if not AUTOGUI_AVAILABLE:
        print("⚠️  AutoGUI not available - manual steps required:")
        print("1. Wait for Wokwi to load")
        print("2. Click on the code editor")
        print("3. Press Ctrl+A to select all")
        print("4. Paste the following JSON:")
        print(json.dumps(circuit_json, indent=2))
        return
    
    # Wait for browser to load
    print("⏳ Waiting for Wokwi to load...")
    time.sleep(5)
    
    try:
        # Use AutoGUI to interact with Wokwi
        print("🤖 Using AutoGUI to load circuit...")
        
        # Look for the diagram.json tab or editor
        time.sleep(2)
        
        # Try to click on diagram.json tab (this might need adjustment based on Wokwi UI)
        # These coordinates are approximate and may need adjustment
        pyautogui.click(400, 100)  # Click on diagram.json tab area
        time.sleep(1)
        
        # Select all and replace content
        pyautogui.hotkey('cmd', 'a')  # macOS: cmd+a, Windows/Linux: ctrl+a
        time.sleep(0.5)
        
        # Type the circuit JSON
        circuit_str = json.dumps(circuit_json, indent=2)
        pyautogui.write(circuit_str, interval=0.01)
        
        print("✅ Circuit loaded in Wokwi!")
        print("🎯 You can now test the circuit in the simulator")
        
    except Exception as e:
        print(f"❌ AutoGUI Error: {e}")
        print("💡 Try manual approach - the circuit JSON is ready to paste")

def capture_wokwi_screenshot(filename="wokwi_screenshot.png"):
    """Capture a screenshot of the Wokwi circuit"""
    if not AUTOGUI_AVAILABLE:
        print("⚠️  AutoGUI not available - cannot capture screenshot")
        return None
    
    try:
        print(f"📸 Capturing screenshot to {filename}...")
        time.sleep(2)  # Wait for circuit to render
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        
        print(f"✅ Screenshot saved to {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Screenshot Error: {e}")
        return None

def automated_circuit_workflow(description):
    """Complete automated workflow: API → Wokwi → Screenshot"""
    print(f"🚀 Starting automated workflow for: {description}")
    print("=" * 60)
    
    # Step 1: Generate circuit via API
    print("🔧 Step 1: Generating circuit via API...")
    circuit_json = generate_circuit_via_api(description)
    
    if not circuit_json:
        print("❌ Workflow failed at circuit generation")
        return None
    
    # Step 2: Save circuit to temporary file
    print("💾 Step 2: Saving circuit to file...")
    timestamp = int(time.time())
    circuit_file = f"automated_circuit_{timestamp}.json"
    
    with open(circuit_file, 'w') as f:
        json.dump(circuit_json, f, indent=2)
    
    print(f"   Circuit saved to {circuit_file}")
    
    # Step 3: Open in Wokwi
    print("🌐 Step 3: Opening circuit in Wokwi...")
    open_wokwi_with_circuit(circuit_json)
    
    # Step 4: Capture screenshot
    print("📸 Step 4: Capturing screenshot...")
    screenshot_file = f"automated_screenshot_{timestamp}.png"
    capture_wokwi_screenshot(screenshot_file)
    
    print("✅ Automated workflow completed!")
    return {
        "circuit_file": circuit_file,
        "screenshot_file": screenshot_file,
        "circuit_json": circuit_json
    }

def batch_circuit_generation(descriptions):
    """Generate multiple circuits via API"""
    print("📦 Batch Circuit Generation")
    print("=" * 40)
    
    results = []
    
    for i, description in enumerate(descriptions, 1):
        print(f"\n🔄 Processing {i}/{len(descriptions)}: {description}")
        
        circuit_json = generate_circuit_via_api(description)
        
        if circuit_json:
            # Save circuit
            filename = f"batch_circuit_{i}.json"
            with open(filename, 'w') as f:
                json.dump(circuit_json, f, indent=2)
            
            results.append({
                "description": description,
                "filename": filename,
                "circuit_json": circuit_json,
                "success": True
            })
            
            print(f"   ✅ Saved to {filename}")
        else:
            results.append({
                "description": description,
                "filename": None,
                "circuit_json": None,
                "success": False
            })
            print("   ❌ Failed to generate")
    
    print(f"\n📊 Batch Results: {sum(1 for r in results if r['success'])}/{len(results)} successful")
    return results

def wokwi_progressive_automation():
    """Automate Wokwi with progressive demo step files"""
    print("🤖 Wokwi Progressive Circuit Automation")
    print("=" * 70)
    
    if not AUTOGUI_AVAILABLE:
        print("❌ PyAutoGUI not available. Install with: pip install pyautogui")
        return
    
    # ---------- CONFIGURATION ----------
    url = "https://wokwi.com/projects/342032431249883731"
    
    # Find demo step files
    demo_files = []
    for i in range(1, 10):  # Check for demo_step_1.json to demo_step_9.json
        step_file = Path(f"demo_step_{i}.json")
        if step_file.exists():
            with open(step_file, 'r') as f:
                content = f.read()
                demo_files.append({
                    "file": step_file.name,
                    "content": content
                })
    
    if not demo_files:
        print("❌ No demo step files found. Run demo.py first to generate them.")
        return
    
    print(f"✅ Found {len(demo_files)} demo step files")
    for file_info in demo_files:
        print(f"   - {file_info['file']}")
    
    # File save naming pattern
    screenshot_dir = "wokwi_screenshots"
    Path(screenshot_dir).mkdir(exist_ok=True)
    file_prefix = "demo_step"
    
    # Delay times
    load_delay = 8       # seconds to wait for page load
    update_delay = 4     # seconds to wait for diagram.json update to reflect
    click_delay = 0.3    # short delay between clicks
    
    # Example coordinates (adjust for your screen)
    diagram_tab_pos = (297, 177)  # Click "diagram.json" tab
    code_area_pos = (400, 400)    # Text editor area
    empty_click_pos = (900, 300)  # Area on the right with the circuit view
    # -----------------------------------
    
    print(f"\n🌐 Opening Wokwi project: {url}")
    webbrowser.open(url)
    print(f"⏳ Waiting {load_delay} seconds for page to load...")
    time.sleep(load_delay)
    
    print("\n📸 Starting progressive screenshot capture...")
    print("💡 Make sure Wokwi is visible and focused!")
    
    for i, file_info in enumerate(demo_files, start=1):
        print(f"\n🔄 Processing {file_info['file']} (Step {i}/{len(demo_files)})")
        
        try:
            # Step 2: Click diagram.json tab
            print("   📋 Clicking diagram.json tab...")
            pyautogui.click(diagram_tab_pos)
            time.sleep(click_delay)
            
            # Step 3: Click code area and replace text
            print("   ✏️  Replacing circuit JSON...")
            pyautogui.click(code_area_pos)
            pyautogui.hotkey('cmd', 'a')   # select all (macOS)
            time.sleep(0.2)
            pyautogui.press('delete')      # delete selected text
            time.sleep(0.2)
            pyautogui.write(file_info['content'], interval=0.001)  # Type the JSON
            
            # Step 4: Wait for auto-update
            print(f"   ⏳ Waiting {update_delay}s for circuit to update...")
            time.sleep(update_delay)
            
            # Step 5: Click on empty area (so text cursor not visible in screenshot)
            pyautogui.click(empty_click_pos)
            time.sleep(0.5)
            
            # Step 6: Screenshot of circuit area
            screenshot_path = f"{screenshot_dir}/{file_prefix}_{i}.png"
            print(f"   � Capturing screenshot: {screenshot_path}")
            pyautogui.screenshot(screenshot_path, region=(672, 287, 1004, 860))
            # ^ region = (x, y, width, height) — adjust for your monitor
            
            print(f"   ✅ Step {i} completed successfully")
            
        except Exception as e:
            print(f"   ❌ Error processing step {i}: {e}")
            continue
    
    print(f"\n🎉 All {len(demo_files)} screenshots captured!")
    print(f"📁 Screenshots saved in: {screenshot_dir}/")
    print("✨ You now have visual documentation of your progressive circuit!")

def demo_api_autogui_integration():
    """Main demo function"""
    print("🤖 RAG AI Circuit Generator - Progressive Wokwi Automation")
    print("=" * 70)
    
    # Check for demo files first
    demo_files_exist = any(Path(f"demo_step_{i}.json").exists() for i in range(1, 10))
    
    if demo_files_exist:
        print("✅ Demo step files found - running Wokwi automation")
        wokwi_progressive_automation()
    else:
        print("❌ No demo step files found")
        print("💡 Generate them first with:")
        print("   1. Run: python demo.py")
        print("   2. Choose option 1 (Generate Progressive Circuits)")
        print("   3. Enter components: arduino uno, led, buzzer, oled")
        print("   4. Then run this script again")
    
    print("\n🎯 Integration Benefits:")
    print("✨ Automated Wokwi circuit testing")
    print("📸 Progressive screenshot capture")
    print("🎓 Visual circuit documentation")
    print("🔄 Complete demo workflow automation")

if __name__ == "__main__":
    demo_api_autogui_integration()
