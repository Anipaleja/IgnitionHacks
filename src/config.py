"""
Configuration settings for the AI Hardware Understanding System
"""

import os
from pathlib import Path
from typing import Dict, List

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
VECTOR_DB_DIR = DATA_DIR / "vector_db"

# Hardware components to focus on
HARDWARE_COMPONENTS = [
    {
        "name": "ESP32",
        "category": "microcontroller",
        "pins": 38,
        "interfaces": ["WiFi", "Bluetooth", "SPI", "I2C", "UART", "ADC", "DAC", "PWM"],
        "voltage": "3.3V",
        "description": "Dual-core WiFi and Bluetooth microcontroller"
    },
    {
        "name": "Arduino Uno (ATmega328P)",
        "category": "microcontroller",
        "pins": 28,
        "interfaces": ["SPI", "I2C", "UART", "ADC", "PWM"],
        "voltage": "5V",
        "description": "8-bit AVR microcontroller, most popular for beginners"
    },
    {
        "name": "DHT22",
        "category": "sensor",
        "pins": 4,
        "interfaces": ["Digital One-Wire"],
        "voltage": "3.3V-5V",
        "description": "Digital humidity and temperature sensor"
    },
    {
        "name": "HC-SR04",
        "category": "sensor",
        "pins": 4,
        "interfaces": ["Digital GPIO"],
        "voltage": "5V",
        "description": "Ultrasonic distance sensor"
    },
    {
        "name": "MPU6050",
        "category": "sensor",
        "pins": 8,
        "interfaces": ["I2C"],
        "voltage": "3.3V-5V",
        "description": "6-axis accelerometer and gyroscope"
    },
    {
        "name": "SSD1306 OLED",
        "category": "display",
        "pins": 4,
        "interfaces": ["I2C", "SPI"],
        "voltage": "3.3V-5V",
        "description": "128x64 monochrome OLED display"
    },
    {
        "name": "WS2812 RGB LED",
        "category": "output",
        "pins": 4,
        "interfaces": ["Digital Data"],
        "voltage": "5V",
        "description": "Addressable RGB LED (NeoPixel)"
    },
    {
        "name": "HC-05 Bluetooth",
        "category": "communication",
        "pins": 6,
        "interfaces": ["UART"],
        "voltage": "3.3V-5V",
        "description": "Bluetooth serial communication module"
    },
    {
        "name": "MQ-2 Gas Sensor",
        "category": "sensor",
        "pins": 4,
        "interfaces": ["Analog", "Digital"],
        "voltage": "5V",
        "description": "Smoke and gas detection sensor"
    },
    {
        "name": "L298N Motor Driver",
        "category": "driver",
        "pins": 15,
        "interfaces": ["PWM", "Digital GPIO"],
        "voltage": "5V-35V",
        "description": "Dual H-bridge motor driver"
    },
    {
        "name": "DS18B20",
        "category": "sensor",
        "pins": 3,
        "interfaces": ["1-Wire"],
        "voltage": "3.0V-5.5V",
        "description": "Digital temperature sensor"
    },
    {
        "name": "BMP280",
        "category": "sensor",
        "pins": 6,
        "interfaces": ["I2C", "SPI"],
        "voltage": "1.8V-3.6V",
        "description": "Barometric pressure and temperature sensor"
    },
    {
        "name": "RFID-RC522",
        "category": "communication",
        "pins": 8,
        "interfaces": ["SPI"],
        "voltage": "3.3V",
        "description": "13.56MHz RFID reader/writer module"
    }
]

# Model configurations
MODEL_CONFIG = {
    "base_model": "microsoft/DialoGPT-medium",
    "fine_tune_model": "microsoft/DialoGPT-small",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "max_length": 512,
    "batch_size": 8,
    "learning_rate": 5e-5,
    "num_epochs": 3,
    "warmup_steps": 100
}

# Vector database settings
VECTOR_DB_CONFIG = {
    "collection_name": "hardware_knowledge",
    "embedding_dimension": 384,
    "similarity_threshold": 0.7,
    "max_results": 5
}

# Data sources
DATA_SOURCES = [
    "https://docs.wokwi.com/",
    "https://www.arduino.cc/reference/",
    "https://docs.espressif.com/",
    "https://randomnerdtutorials.com/",
    "https://learn.adafruit.com/",
    "https://www.electronicshub.org/",
    "https://www.sparkfun.com/tutorials",
    "https://components101.com/"
]

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WANDB_API_KEY = os.getenv("WANDB_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# Create directories
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, VECTOR_DB_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
