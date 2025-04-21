"""
Main script to run the ResearchAssistant application.
"""

import os
import sys
import subprocess
import time

# Add the project root to the Python path to ensure imports work correctly
sys.path.insert(0, os.path.abspath('.'))

def check_environment():
    """
    Check if the required environment is set up correctly.
    """
     # Check if our package is installed
    try:
        import research_assistant
        print(f"Found research_assistant package at: {research_assistant.__file__}")
    except ImportError:
        print("Warning: research_assistant package not found in Python path.")
        print("The application may still work if the directory structure is correct.")
    
    required_dirs = [
        "src/research_assistant/retrieval",
        "src/research_assistant/ranking",
        "src/research_assistant/api",
        "src/research_assistant/utils"
    ]

    for directory in required_dirs:
        if not os.path.isdir(directory):
            print(f"Error: Directory '{directory}' not found. Are you running this from the project root?")
            return False
        
    required_files = [
        "src/research_assistant/api/app.py",
        "ui/index.html",
        "requirements.txt"
    ]

    for file_path in required_files:
        if not os.path.isfile(file_path):
            print(f"Error: File '{file_path}' not found.")
            return False
    
    return True

def start_api_server():
    """
    Start the API server in a new process.
    """
    print("Starting API server...")
    # Use Python executable that's running this script
    python_exec = sys.executable

    # Use subprocess to start the server in the background
    api_process = subprocess.Popen(
        [python_exec, "src/research_assistant/api/app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a bit for the server to start
    time.sleep(2)

    # Check if the server start successfully
    for _ in range(10): # wait for up to 10 seconds
        try:
            import requests
            response = requests.get("http://localhost:5000/")
            if response.status_code == 404: # The server is running but no root route defined
                print("API server started successfully on http://localhost:5000")
                return api_process
        except:
            time.sleep(1)

    # if we get here, the server did not start successfully
    print("API server output:")
    for line in api_process.stdout.readlines():
        print(line.strip())
    print("API server errors")
    for line in api_process.stderr.readlines():
        print(line.strip())
    
    print("Warning: API server might not have started properly.")
    return api_process


def main():
    """
    Main function to run the ResearchAssistant application.
    """
    if not check_environment():
        print("Environment check failed. Please ensure you're running this script from the project root.")
        sys.exit(1)

    # Start the API server
    api_process = start_api_server()
    if api_process is None:
        print("Failed to start API server.")
        return

    print("\nResearchAssistant is now running!")
    print("API server: http://localhost:5000")
    print("To use the UI, manually open the file:")
    print("  file://" + os.path.abspath("ui/index.html"))
    print("\nPress Ctrl+C to stop the application")

    try:
        # Wait for the API server process to finish
        api_process.wait()
    except KeyboardInterrupt:
        print("\nStopping ResearchAssistant...")
        api_process.terminate()
        print("Application stopped.")

if __name__ == "__main__":
    main()