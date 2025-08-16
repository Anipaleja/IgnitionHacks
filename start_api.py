#!/usr/bin/env python3
"""
Startup script for the RAG AI Circuit Generator Flask API
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def start_api_server():
    """Start the Flask API server"""
    print("Starting RAG AI Circuit Generator API...")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    venv_python = Path(".venv/bin/python")
    if venv_python.exists():
        python_cmd = str(venv_python.absolute())
        print(f"Using virtual environment: {python_cmd}")
    else:
        python_cmd = sys.executable
        print(f"Using system Python: {python_cmd}")
    
    # Start the API server
    try:
        cmd = [python_cmd, "api.py"]
        process = subprocess.Popen(cmd, cwd=os.getcwd())
        
        print(f"API server started with PID: {process.pid}")
        print("API endpoints available at:")
        print("  http://localhost:5000/")
        print("  http://localhost:5000/api/health")
        print("  http://localhost:5000/api/generate")
        print("  http://localhost:5000/api/components")
        print("  http://localhost:5000/api/progressive")
        print("  http://localhost:5000/api/parse")
        print("\nPress Ctrl+C to stop the server")
        
        # Handle graceful shutdown
        def signal_handler(sig, frame):
            print("\nShutting down API server...")
            process.terminate()
            process.wait()
            print("Server stopped.")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Wait for the process to finish
        process.wait()
        
    except Exception as e:
        print(f"Error starting API server: {e}")
        return False
    
    return True

def start_with_test():
    """Start API server and run tests"""
    import threading
    import time
    
    # Start server in background
    def run_server():
        start_api_server()
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    print("Starting server...")
    time.sleep(3)
    
    # Run tests
    print("Running API tests...")
    try:
        venv_python = Path(".venv/bin/python")
        if venv_python.exists():
            python_cmd = str(venv_python.absolute())
        else:
            python_cmd = sys.executable
        
        subprocess.run([python_cmd, "test_api.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Tests failed: {e}")
    except Exception as e:
        print(f"Error running tests: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start RAG AI Circuit Generator API")
    parser.add_argument("--test", action="store_true", help="Run API tests after starting server")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the server on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ['PORT'] = str(args.port)
    if args.debug:
        os.environ['DEBUG'] = 'true'
    
    if args.test:
        start_with_test()
    else:
        start_api_server()
