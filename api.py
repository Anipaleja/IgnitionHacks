#!/usr/bin/env python3
"""
Flask API for RAG AI Circuit Generator
=====================================

Provides REST API endpoints for generating circuit diagrams from text descriptions.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import sys
import time
import subprocess
from pathlib import Path
import tempfile
import zipfile
from datetime import datetime

# Add the current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from main import generate_circuit_diagram_json
from demo import parse_text_input, generate_step_instructions

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/', methods=['GET'])
def home():
    """API documentation endpoint"""
    return jsonify({
        "message": "RAG AI Circuit Generator API",
        "version": "1.0.0",
        "endpoints": {
            "/api/generate": {
                "method": "POST",
                "description": "Generate circuit from text description",
                "parameters": {
                    "description": "Text description of circuit components",
                    "mode": "single or progressive (default: single)",
                    "filename": "Output filename (optional)"
                }
            },
            "/api/components": {
                "method": "POST", 
                "description": "Generate circuit from component list",
                "parameters": {
                    "components": "Array of component objects",
                    "mode": "single or progressive (default: single)"
                }
            },
            "/api/progressive": {
                "method": "POST",
                "description": "Generate progressive circuit files as ZIP",
                "parameters": {
                    "description": "Text description of circuit components"
                }
            },
            "/api/health": {
                "method": "GET",
                "description": "Health check endpoint"
            }
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "RAG AI Circuit Generator API"
    })

@app.route('/api/generate', methods=['POST'])
def generate_circuit():
    """Generate a single circuit diagram from text description"""
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                "error": "Missing 'description' field in request body"
            }), 400
        
        description = data['description']
        filename = data.get('filename', 'circuit.json')
        
        # Ensure filename has .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Parse text input into components
        components = parse_text_input(description)
        
        if not components:
            return jsonify({
                "error": "No components could be parsed from description"
            }), 400
        
        # Generate circuit diagram
        circuit_json = generate_circuit_diagram_json(
            parts=components,
            save_to_file=None  # Don't save to file, return content
        )
        
        # Parse the generated JSON to get statistics
        circuit_data = json.loads(circuit_json)
        
        return jsonify({
            "success": True,
            "description": description,
            "filename": filename,
            "components_detected": len(components),
            "total_parts": len(circuit_data['parts']),
            "connections": len(circuit_data['connections']),
            "detected_components": [
                {
                    "id": comp['id'],
                    "type": comp['type'],
                    "name": comp['type'].replace('wokwi-', '').replace('board-', '').replace('-', ' ').title()
                }
                for comp in components
            ],
            "circuit_json": circuit_data
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to generate circuit"
        }), 500

@app.route('/api/components', methods=['POST'])
def generate_from_components():
    """Generate circuit from explicit component list"""
    try:
        data = request.get_json()
        
        if not data or 'components' not in data:
            return jsonify({
                "error": "Missing 'components' field in request body"
            }), 400
        
        components = data['components']
        
        if not isinstance(components, list) or len(components) == 0:
            return jsonify({
                "error": "'components' must be a non-empty array"
            }), 400
        
        # Validate component structure
        for i, comp in enumerate(components):
            if not isinstance(comp, dict) or 'type' not in comp or 'id' not in comp:
                return jsonify({
                    "error": f"Component {i} must have 'type' and 'id' fields"
                }), 400
        
        # Generate circuit diagram
        circuit_json = generate_circuit_diagram_json(
            parts=components,
            save_to_file=None
        )
        
        # Parse the generated JSON to get statistics
        circuit_data = json.loads(circuit_json)
        
        return jsonify({
            "success": True,
            "components_provided": len(components),
            "total_parts": len(circuit_data['parts']),
            "connections": len(circuit_data['connections']),
            "circuit_json": circuit_data
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to generate circuit from components"
        }), 500

@app.route('/api/auto-demo', methods=['POST'])
def auto_demo():
    """Generate progressive circuits and automatically start screenshot automation"""
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                "error": "Missing 'description' field in request body"
            }), 400
        
        description = data['description']
        
        # Parse text input into components
        components = parse_text_input(description)
        
        if not components:
            return jsonify({
                "error": "No components could be parsed from description"
            }), 400
        
        # Generate circuit JSON files directly using the same approach as demo.py
        import threading
        import subprocess
        
        print(f"\n🎯 Auto-Demo API: Generating progressive circuits...")
        print(f"Components: {[comp['type'] for comp in components]}")
        
        # Generate the progressive circuits locally
        mcu = None
        other_components = []
        
        for comp in components:
            comp_type = comp['type'].lower()
            if any(x in comp_type for x in ['arduino', 'esp32', 'mega', 'nano']):
                mcu = comp
            else:
                other_components.append(comp)
        
        if not mcu:
            mcu = {"type": "wokwi-arduino-uno", "id": "mcu"}
        
        # Generate step files
        steps = [
            [mcu],  # Step 1: Just microcontroller
            [mcu] + other_components[:1],  # Step 2: MCU + first component
            [mcu] + other_components[:2],  # Step 3: MCU + first two components
            [mcu] + other_components  # Step 4: All components
        ]
        
        generated_files = []
        for i, step_components in enumerate(steps, 1):
            if len(step_components) > 0:
                circuit_json = generate_circuit_diagram_json(
                    parts=step_components,
                    save_to_file=None
                )
                
                filename = f"demo_step_{i}.json"
                with open(filename, 'w') as f:
                    f.write(circuit_json)
                generated_files.append(filename)
                print(f"✅ Generated {filename}")
        
        # Start screenshot automation in background using subprocess
        def run_automation():
            time.sleep(2)  # Give API time to respond
            print("🚀 Starting AutoGUI screenshot automation via subprocess...")
            try:
                # Create a simple Python script to run the automation
                automation_script = f"""
import sys
import os
sys.path.append('.')
os.chdir('{os.getcwd()}')

from demo import run_progressive_screenshot_automation

# The generated files are already saved to disk
generated_files = {generated_files}
print(f"🎯 AutoGUI: Using files: {{generated_files}}")

run_progressive_screenshot_automation(generated_files)
"""
                # Write the script to a temporary file and run it
                with open('temp_automation.py', 'w') as f:
                    f.write(automation_script)
                
                subprocess.Popen([sys.executable, 'temp_automation.py'], cwd=os.getcwd())
                print("✅ AutoGUI process started successfully")
            except Exception as e:
                print(f"❌ Failed to start AutoGUI: {e}")
        
        automation_thread = threading.Thread(target=run_automation)
        automation_thread.daemon = True
        automation_thread.start()
        
        return jsonify({
            "success": True,
            "message": "Progressive circuits generated and AutoGUI automation started",
            "components_count": len(components),
            "components": [comp['type'] for comp in components],
            "automation_status": "started",
            "files_generated": generated_files
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to run auto-demo"
        }), 500

@app.route('/api/progressive', methods=['POST'])
def generate_progressive():
    """Generate progressive circuit files and return as ZIP"""
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                "error": "Missing 'description' field in request body"
            }), 400
        
        description = data['description']
        auto_screenshot = data.get('auto_screenshot', False)
        
        # Parse text input into components
        components = parse_text_input(description)
        
        if not components:
            return jsonify({
                "error": "No components could be parsed from description"
            }), 400
        
        # Create temporary directory for files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Generate progressive circuits
            generated_files = generate_progressive_circuits_api(components, temp_path)
            
            # Also generate local demo files if auto_screenshot is requested
            if auto_screenshot:
                # Import the demo functions
                from demo import generate_progressive_circuits, run_progressive_screenshot_automation
                
                # Generate local demo files
                print(f"\n🎯 API Request: Generating progressive circuits with AutoGUI automation...")
                generate_progressive_circuits(components)
                
                # Start screenshot automation in background
                import threading
                def run_automation():
                    time.sleep(1)  # Small delay to ensure API response is sent
                    print("🚀 Starting AutoGUI screenshot automation...")
                    run_progressive_screenshot_automation()
                
                automation_thread = threading.Thread(target=run_automation)
                automation_thread.daemon = True
                automation_thread.start()
            
            # Create ZIP file
            zip_path = temp_path / "progressive_circuits.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path in generated_files:
                    zipf.write(file_path, file_path.name)
            
            # Return the ZIP file
            response_data = {
                "success": True,
                "auto_screenshot": auto_screenshot,
                "message": "Progressive circuits generated successfully"
            }
            
            if auto_screenshot:
                response_data["automation"] = "AutoGUI screenshot automation started"
            
            # For auto_screenshot, return JSON response instead of file
            if auto_screenshot:
                return jsonify(response_data)
            else:
                return send_file(
                    zip_path,
                    as_attachment=True,
                    download_name=f"progressive_circuits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mimetype='application/zip'
                )
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to generate progressive circuits"
        }), 500

def generate_progressive_circuits_api(components, output_dir):
    """Generate progressive circuit files for API (modified from demo.py)"""
    generated_files = []
    
    # Separate microcontroller from other components
    mcu = None
    other_components = []
    
    for comp in components:
        comp_type = comp['type'].lower()
        if any(x in comp_type for x in ['arduino', 'esp32', 'mega', 'nano']):
            mcu = comp
        else:
            other_components.append(comp)
    
    if not mcu:
        mcu = {"type": "wokwi-arduino-uno", "id": "mcu"}
    
    # Position components with proper spacing
    arduino_center = {"top": 200, "left": 200}
    positioned_components = [mcu.copy()]
    positioned_components[0].update(arduino_center)
    
    # Position other components in a logical layout
    spacing_patterns = [
        {"top": -120, "left": 150},   # Above and right
        {"top": 120, "left": 150},    # Below and right
        {"top": -50, "left": 250},    # Above and far right
        {"top": 50, "left": 250},     # Below and far right
        {"top": -120, "left": -150},  # Above and left
        {"top": 120, "left": -150},   # Below and left
        {"top": 0, "left": 300},      # Right side
        {"top": 0, "left": -200},     # Left side
    ]
    
    for i, comp in enumerate(other_components):
        positioned_comp = comp.copy()
        if i < len(spacing_patterns):
            pattern = spacing_patterns[i]
            positioned_comp.update({
                "top": arduino_center["top"] + pattern["top"],
                "left": arduino_center["left"] + pattern["left"]
            })
        else:
            # Fallback positioning for many components
            import math
            angle = (i * 45) % 360
            radius = 200 + (i // 8) * 50
            positioned_comp.update({
                "top": arduino_center["top"] + int(radius * math.sin(math.radians(angle))),
                "left": arduino_center["left"] + int(radius * math.cos(math.radians(angle)))
            })
        
        positioned_components.append(positioned_comp)
    
    # Generate step-by-step circuits
    for step in range(1, len(positioned_components) + 1):
        current_components = positioned_components[:step]
        
        # Generate circuit file
        step_filename = output_dir / f"step_{step}_circuit.json"
        circuit_json = generate_circuit_diagram_json(
            parts=current_components,
            save_to_file=str(step_filename)
        )
        generated_files.append(step_filename)
        
        # Generate instruction file
        instruction_filename = output_dir / f"step_{step}_instructions.txt"
        circuit_data = json.loads(circuit_json)
        generate_step_instructions(step, current_components, circuit_data, str(instruction_filename), arduino_center)
        generated_files.append(instruction_filename)
    
    return generated_files

@app.route('/api/parse', methods=['POST'])
def parse_components():
    """Parse text description into component list without generating circuit"""
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                "error": "Missing 'description' field in request body"
            }), 400
        
        description = data['description']
        
        # Parse text input into components
        components = parse_text_input(description)
        
        return jsonify({
            "success": True,
            "description": description,
            "components_detected": len(components),
            "components": [
                {
                    "id": comp['id'],
                    "type": comp['type'],
                    "name": comp['type'].replace('wokwi-', '').replace('board-', '').replace('-', ' ').title(),
                    "category": get_component_category(comp['type'])
                }
                for comp in components
            ]
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to parse components"
        }), 500

def get_component_category(component_type):
    """Get category for a component type"""
    comp_type = component_type.lower()
    
    if any(x in comp_type for x in ['arduino', 'esp32', 'mega', 'nano']):
        return "Microcontroller"
    elif 'led' in comp_type:
        return "Output"
    elif any(x in comp_type for x in ['button', 'switch']):
        return "Input"
    elif any(x in comp_type for x in ['buzzer', 'piezo', 'speaker']):
        return "Audio Output"
    elif any(x in comp_type for x in ['display', 'oled', 'tft', 'lcd']):
        return "Display"
    elif any(x in comp_type for x in ['sensor', 'dht', 'temperature', 'ultrasonic', 'photoresistor']):
        return "Sensor"
    elif 'resistor' in comp_type:
        return "Passive Component"
    elif any(x in comp_type for x in ['motor', 'servo']):
        return "Actuator"
    else:
        return "Other"

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        "error": "Request entity too large",
        "message": "File size exceeds maximum allowed size"
    }), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested endpoint does not exist"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"Starting RAG AI Circuit Generator API on port {port}")
    print(f"Debug mode: {debug}")
    print("Available endpoints:")
    print("  GET  /                - API documentation")
    print("  GET  /api/health      - Health check")
    print("  POST /api/generate    - Generate single circuit")
    print("  POST /api/components  - Generate from component list")
    print("  POST /api/progressive - Generate progressive circuits (ZIP)")
    print("  POST /api/auto-demo   - Generate circuits + AutoGUI automation")
    print("  POST /api/parse       - Parse text to components")
    print("  POST /api/parse       - Parse text to components")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
