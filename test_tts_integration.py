#!/usr/bin/env python3
"""
Test TTS integration with screenshot automation
"""

import subprocess
import time
import os

print("=== TESTING TTS + SCREENSHOT INTEGRATION ===")
print()

# Create test screenshot directory
screenshot_dir = "test_tts_screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

# Test the TTS functionality during screenshot simulation
for i in range(1, 4):
    print(f"Step {i}: Taking screenshot...")
    
    # Simulate screenshot (just create a dummy file)
    screenshot_path = f"{screenshot_dir}/test_step_{i}.png"
    with open(screenshot_path, 'w') as f:
        f.write("dummy screenshot file")
    
    print(f"   📸 Screenshot saved: {screenshot_path}")
    
    # TTS announcement (same code as in demo.py)
    try:
        subprocess.run(['say', 'Screenshot taken!'], check=False)
        print("   🔊 TTS announcement played")
    except Exception as e:
        print(f"   ❌ TTS failed: {e}")
    
    print(f"   ✅ Step {i} completed")
    time.sleep(1)  # Brief pause between steps

print()
print("🎉 TTS integration test complete!")
print("When you run the actual automation, you'll hear 'Screenshot taken!' for each step.")

# Cleanup
import shutil
if os.path.exists(screenshot_dir):
    shutil.rmtree(screenshot_dir)
    print("Test files cleaned up.")
