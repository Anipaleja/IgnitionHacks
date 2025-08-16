#!/usr/bin/env python3
"""
Test Code Llama 70B Integration
Verifies that the upgraded model works for circuit generation
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from comprehensive_model_trainer import ComprehensiveHardwareModelTrainer
import json

def test_code_llama():
    """Test Code Llama 70B for circuit generation"""
    
    print("🧪 Testing Code Llama 70B Integration")
    print("=" * 50)
    
    # Initialize the trainer with Code Llama
    trainer = ComprehensiveHardwareModelTrainer()
    
    # Test circuit generation
    test_prompt = """Generate complete Wokwi circuit diagram JSON for: ESP32, LED, Button

Components:
- esp32: wokwi-esp32-devkit-v1
- led1: wokwi-led  
- btn1: wokwi-pushbutton

Create proper connections with wire routing."""
    
    print("🔄 Generating circuit with Code Llama...")
    response = trainer.generate_response(test_prompt, max_length=1024, temperature=0.2)
    
    print("\n📄 Generated Response:")
    print("-" * 30)
    print(response)
    
    # Try to parse as JSON
    try:
        parsed = json.loads(response)
        print("\n✅ Valid JSON generated!")
        print(f"   - Parts: {len(parsed.get('parts', []))}")
        print(f"   - Connections: {len(parsed.get('connections', []))}")
        
        # Save test result
        with open("test_codellama_output.json", "w") as f:
            json.dump(parsed, f, indent=2)
        print("   - Saved to test_codellama_output.json")
        
    except json.JSONDecodeError as e:
        print(f"\n❌ Invalid JSON generated: {e}")
        print("   The model may need fine-tuning or the response needs cleaning")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_code_llama()
