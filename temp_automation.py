
import sys
import os
sys.path.append('.')
os.chdir('/Users/anishpaleja/IgnitionHacks-1')

from demo import run_progressive_screenshot_automation

# The generated files are already saved to disk
generated_files = ['demo_step_1.json', 'demo_step_2.json', 'demo_step_3.json', 'demo_step_4.json']
print(f"🎯 AutoGUI: Using files: {generated_files}")

run_progressive_screenshot_automation(generated_files)
