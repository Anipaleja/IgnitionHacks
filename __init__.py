"""
AI Hardware Understanding System
================================

This system uses RAG (Retrieval Augmented Generation) and fine-tuning to understand
various hardware components, their pins, connections, and specifications.

Selected Hardware Components for Training:
1. ESP32 - Popular WiFi/Bluetooth microcontroller
2. Arduino Uno (ATmega328P) - Most common beginner microcontroller
3. DHT22 - Digital humidity and temperature sensor
4. HC-SR04 - Ultrasonic distance sensor
5. MPU6050 - 6-axis accelerometer/gyroscope
6. SSD1306 OLED - I2C display
7. WS2812 RGB LED - NeoPixel addressable LED
8. HC-05 Bluetooth module - Wireless communication
9. MQ-2 Gas sensor - Analog sensor
10. L298N Motor driver - H-bridge for motors
11. DS18B20 - 1-Wire temperature sensor
12. BMP280 - Barometric pressure sensor
13. RFID-RC522 - Radio frequency identification module

Features:
- Hardware specification extraction and storage
- Pin mapping and connection understanding
- Code example analysis
- Datasheet processing
- Interactive Q&A about hardware components
"""

import os
import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

__version__ = "1.0.0"
__author__ = "AI Hardware Understanding System"
