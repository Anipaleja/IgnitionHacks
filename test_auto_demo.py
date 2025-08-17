#!/usr/bin/env python3
"""
Test Auto-Demo API Endpoint
===========================

This script demonstrates how to trigger automatic demo generation + screenshot automation
via the API endpoint.
"""

import requests
import json
import time

def test_auto_demo_api():
    """Test the auto-demo API endpoint"""
    
    print("🚀 Testing Auto-Demo API Endpoint")
    print("=" * 50)
    
    # API endpoint
    url = "http://localhost:5000/api/auto-demo"
    
    # Test data
    test_data = {
        "description": "Arduino Uno with LED, button, and buzzer for an interactive alarm system"
    }
    
    print(f"📡 Sending request to: {url}")
    print(f"📝 Description: {test_data['description']}")
    print("\n🔄 Making API request...")
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API request successful!")
            print(f"📊 Response: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print("\n🎯 Auto-demo started successfully!")
                print(f"🔧 Components: {result.get('components', [])}")
                print(f"📸 Automation: {result.get('automation_status', 'unknown')}")
                print("\n💡 The AutoGUI automation should now be running in the background...")
                print("🖥️  Check your browser for automatic Wokwi interactions!")
                
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - make sure the API server is running!")
        print("💡 Start the API server with: python api.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_auto_demo_api()
