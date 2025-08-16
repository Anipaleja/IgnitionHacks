# RAG AI Circuit Generator - Flask API

A REST API for generating circuit diagrams from natural language descriptions using RAG AI and Gemini validation.

## Features

- **Text-to-Circuit Generation**: Convert natural language descriptions into Wokwi circuit diagrams
- **Progressive Circuit Generation**: Create step-by-step circuit files with instructions
- **Component Parsing**: Extract components from text descriptions
- **Automatic Resistor Insertion**: Automatically adds appropriate resistors (220Ω for LEDs, 100Ω for piezo)
- **Distributed Ground Connections**: Uses different ground pins (GND.1, GND.2, GND.3) for professional wiring
- **Beginner Instructions**: Generates step-by-step wiring instructions for each circuit

## Quick Start

### 1. Install Dependencies

```bash
# Install Flask dependencies
pip install -r api_requirements.txt

# Install existing project dependencies
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
# Using the startup script
python start_api.py

# Or directly
python api.py

# With debug mode
python start_api.py --debug

# On a different port
python start_api.py --port 8080
```

### 3. Test the API

```bash
# Run automated tests
python start_api.py --test

# Or test manually
python test_api.py
```

### 4. Use the Web Interface

Open `web_interface.html` in your browser to interact with the API through a user-friendly interface.

## API Endpoints

### Base URL
```
http://localhost:5000
```

### 1. Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00",
  "service": "RAG AI Circuit Generator API"
}
```

### 2. Generate Circuit from Description
```http
POST /api/generate
```

**Request Body:**
```json
{
  "description": "arduino uno with led and buzzer",
  "filename": "my_circuit.json"  // optional
}
```

**Response:**
```json
{
  "success": true,
  "description": "arduino uno with led and buzzer",
  "filename": "my_circuit.json",
  "components_detected": 3,
  "total_parts": 4,
  "connections": 6,
  "detected_components": [
    {
      "id": "mcu",
      "type": "wokwi-arduino-uno",
      "name": "Arduino Uno"
    },
    {
      "id": "comp1",
      "type": "wokwi-led",
      "name": "Led"
    },
    {
      "id": "comp2",
      "type": "wokwi-buzzer",
      "name": "Buzzer"
    }
  ],
  "circuit_json": {
    "version": 1,
    "author": "RAG AI Generator",
    "editor": "wokwi",
    "parts": [...],
    "connections": [...],
    "dependencies": {}
  }
}
```

### 3. Parse Components from Text
```http
POST /api/parse
```

**Request Body:**
```json
{
  "description": "arduino uno, led, button, ultrasonic sensor"
}
```

**Response:**
```json
{
  "success": true,
  "description": "arduino uno, led, button, ultrasonic sensor",
  "components_detected": 4,
  "components": [
    {
      "id": "mcu",
      "type": "wokwi-arduino-uno",
      "name": "Arduino Uno",
      "category": "Microcontroller"
    },
    {
      "id": "comp1",
      "type": "wokwi-led",
      "name": "Led",
      "category": "Output"
    },
    {
      "id": "comp2",
      "type": "wokwi-pushbutton",
      "name": "Pushbutton",
      "category": "Input"
    },
    {
      "id": "comp3",
      "type": "wokwi-hc-sr04",
      "name": "Hc Sr04",
      "category": "Sensor"
    }
  ]
}
```

### 4. Generate from Component List
```http
POST /api/components
```

**Request Body:**
```json
{
  "components": [
    {"type": "wokwi-arduino-uno", "id": "mcu"},
    {"type": "wokwi-led", "id": "led1"},
    {"type": "wokwi-buzzer", "id": "buzzer1"}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "components_provided": 3,
  "total_parts": 4,
  "connections": 6,
  "circuit_json": {...}
}
```

### 5. Generate Progressive Circuits
```http
POST /api/progressive
```

**Request Body:**
```json
{
  "description": "arduino uno, led, buzzer, oled display"
}
```

**Response:**
- Downloads a ZIP file containing:
  - `step_1_circuit.json` - Arduino Uno only
  - `step_1_instructions.txt` - Basic setup instructions
  - `step_2_circuit.json` - Arduino + LED
  - `step_2_instructions.txt` - LED wiring instructions
  - `step_3_circuit.json` - Arduino + LED + Buzzer
  - `step_3_instructions.txt` - Buzzer wiring instructions
  - `step_4_circuit.json` - Complete circuit
  - `step_4_instructions.txt` - Final instructions

## Supported Components

### Microcontrollers
- Arduino Uno (`wokwi-arduino-uno`)
- Arduino Mega (`wokwi-arduino-mega`)
- ESP32 (`wokwi-esp32-devkit-v1`)
- Arduino Nano (`wokwi-arduino-nano`)

### Output Components
- LED (`wokwi-led`)
- RGB LED (`wokwi-rgb-led`)
- Buzzer (`wokwi-buzzer`)
- Piezo Buzzer (`wokwi-piezo-buzzer`)

### Input Components
- Push Button (`wokwi-pushbutton`)
- Slide Switch (`wokwi-slide-switch`)
- Potentiometer (`wokwi-potentiometer`)

### Displays
- OLED Display (`board-ssd1306`)
- LCD Display (`wokwi-lcd1602`)
- TFT Display (`wokwi-ili9341`)

### Sensors
- Ultrasonic Sensor (`wokwi-hc-sr04`)
- DHT22 Temperature/Humidity (`wokwi-dht22`)
- Photoresistor (`wokwi-photoresistor-sensor`)
- PIR Motion Sensor (`wokwi-pir-motion-sensor`)

### Actuators
- Servo Motor (`wokwi-servo`)
- DC Motor (`wokwi-dc-motor`)

### Passive Components
- Resistor (`wokwi-resistor`)
- Capacitor (`wokwi-capacitor`)

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request (missing required fields, invalid data)
- `413` - Request Entity Too Large (file size limit exceeded)
- `404` - Endpoint Not Found
- `500` - Internal Server Error

Error responses include details:
```json
{
  "error": "Missing 'description' field in request body",
  "message": "Additional error context"
}
```

## Examples

### Using curl

```bash
# Generate a simple circuit
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "arduino uno with led and buzzer"}'

# Parse components only
curl -X POST http://localhost:5000/api/parse \
  -H "Content-Type: application/json" \
  -d '{"description": "arduino, led, button, sensor"}'

# Download progressive circuits
curl -X POST http://localhost:5000/api/progressive \
  -H "Content-Type: application/json" \
  -d '{"description": "arduino uno, led, buzzer, oled"}' \
  --output progressive_circuits.zip
```

### Using Python requests

```python
import requests
import json

# Generate circuit
response = requests.post('http://localhost:5000/api/generate', 
    json={
        'description': 'arduino uno with led, buzzer, and oled display',
        'filename': 'my_awesome_circuit.json'
    })

if response.status_code == 200:
    result = response.json()
    print(f"Generated circuit with {result['total_parts']} parts")
    
    # Save the circuit JSON
    with open('circuit.json', 'w') as f:
        json.dump(result['circuit_json'], f, indent=2)
else:
    print(f"Error: {response.json()['error']}")
```

### Using JavaScript (fetch)

```javascript
// Generate circuit
fetch('http://localhost:5000/api/generate', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        description: 'arduino uno with led and button',
        filename: 'my_circuit.json'
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('Circuit generated!', data);
        // Use data.circuit_json for the Wokwi circuit
    } else {
        console.error('Error:', data.error);
    }
});
```

## Development

### Project Structure
```
├── api.py                  # Flask API server
├── api_requirements.txt    # Flask dependencies
├── start_api.py           # API startup script
├── test_api.py            # API test suite
├── web_interface.html     # Web testing interface
├── main.py                # Core circuit generation
├── demo.py                # Demo functionality
└── requirements.txt       # Main project dependencies
```

### Adding New Components

To add support for new components, update the component recognition in `demo.py`:

```python
# In parse_text_input function
component_mapping = {
    'new_component': 'wokwi-new-component',
    # ... existing mappings
}
```

### Customizing Output

The API uses the same circuit generation logic as the main project. Customize:

- **Pin allocation**: Modify `PinAllocator` classes in `main.py`
- **Component positioning**: Update positioning logic in `generate_progressive_circuits_api`
- **Instruction generation**: Modify `generate_step_instructions` in `demo.py`

## Deployment

### Production Deployment

```bash
# Using Gunicorn (recommended)
gunicorn --bind 0.0.0.0:5000 --workers 4 api:app

# Using the startup script with production settings
export PORT=8080
export DEBUG=false
python start_api.py
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN pip install -r api_requirements.txt

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "api:app"]
```

### Environment Variables

- `PORT`: Server port (default: 5000)
- `DEBUG`: Enable debug mode (default: false)
- `MAX_CONTENT_LENGTH`: Maximum request size (default: 16MB)

## License

Same as the main project license.
