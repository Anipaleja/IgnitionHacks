"""
Model Configuration Options for Circuit Generation
Choose the best model based on your hardware capabilities
"""

# Model options ranked by capability and resource requirements

MODEL_CONFIGS = {
    "codellama_70b": {
        "model_name": "codellama/CodeLlama-70b-Instruct-hf",
        "description": "Largest and most capable, requires high-end GPU(s)",
        "requirements": "48GB+ VRAM, multiple GPUs recommended",
        "context_length": 4096,
        "batch_size": 1,
        "load_in_8bit": True
    },
    
    "codellama_34b": {
        "model_name": "codellama/CodeLlama-34b-Instruct-hf", 
        "description": "Very capable, more reasonable resource requirements",
        "requirements": "24GB+ VRAM",
        "context_length": 4096,
        "batch_size": 1,
        "load_in_8bit": True
    },
    
    "codellama_13b": {
        "model_name": "codellama/CodeLlama-13b-Instruct-hf",
        "description": "Good balance of capability and efficiency",
        "requirements": "12GB+ VRAM",
        "context_length": 4096,
        "batch_size": 2,
        "load_in_8bit": False
    },
    
    "codellama_7b": {
        "model_name": "codellama/CodeLlama-7b-Instruct-hf",
        "description": "Fastest, works on consumer GPUs",
        "requirements": "8GB+ VRAM",
        "context_length": 4096,
        "batch_size": 4,
        "load_in_8bit": False
    },
    
    "starcoder_15b": {
        "model_name": "bigcode/starcoder",
        "description": "Alternative code generation model",
        "requirements": "16GB+ VRAM",
        "context_length": 8192,
        "batch_size": 2,
        "load_in_8bit": True
    },
    
    "codet5p_16b": {
        "model_name": "Salesforce/codet5p-16b",
        "description": "Microsoft's code generation model",
        "requirements": "20GB+ VRAM", 
        "context_length": 2048,
        "batch_size": 1,
        "load_in_8bit": True
    }
}

def get_recommended_model():
    """Get recommended model based on system capabilities"""
    import torch
    
    if not torch.cuda.is_available():
        return "codellama_7b"  # CPU fallback
    
    # Get GPU memory
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
    
    if gpu_memory >= 48:
        return "codellama_70b"
    elif gpu_memory >= 24:
        return "codellama_34b"
    elif gpu_memory >= 12:
        return "codellama_13b"
    else:
        return "codellama_7b"

def print_model_info():
    """Print information about available models"""
    import torch
    
    print("🤖 Available AI Models for Circuit Generation")
    print("=" * 60)
    
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"🖥️  Detected GPU Memory: {gpu_memory:.1f} GB")
        recommended = get_recommended_model()
        print(f"💡 Recommended Model: {recommended}")
    else:
        print("🖥️  No GPU detected - CPU mode")
        recommended = "codellama_7b"
    
    print("\n📋 Model Options:")
    print("-" * 60)
    
    for key, config in MODEL_CONFIGS.items():
        status = "✅ RECOMMENDED" if key == recommended else ""
        print(f"\n{key}: {status}")
        print(f"   Model: {config['model_name']}")
        print(f"   Description: {config['description']}")
        print(f"   Requirements: {config['requirements']}")
        print(f"   Context Length: {config['context_length']}")

if __name__ == "__main__":
    print_model_info()
