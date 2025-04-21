"""
Command-line interface for the Research Assistant.
"""

import os
import sys
import subprocess
import webbrowser
import time
import argparse
from pathlib import Path

def get_package_root():
    """Get the root directory of the installed package."""
    import research_assistant
    return Path(research_assistant.__file__).parent

def start_api_server(port=5000):
    """Start the API server in a new process."""
    print("Starting API server...")
    
    # Use Python executable that's running this script
    python_exec = sys.executable
    
    # Get the path to the app.py file
    app_path = get_package_root() / "api" / "app.py"
    
    # Use subprocess to start the server in the background
    api_process = subprocess.Popen(
        [python_exec, str(app_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a moment for the server to start
    time.sleep(2)
    
    # Check if the server started successfully
    try:
        import requests
        response = requests.get(f"http://localhost:{port}/")
        if response.status_code == 404:  # The server is running but no root route defined
            print(f"API server started successfully on http://localhost:{port}")
    except:
        print("Warning: Could not confirm API server started properly.")
        print("API server output:")
        for line in api_process.stdout.readlines():
            print(line.strip())
        print("API server errors:")
        for line in api_process.stderr.readlines():
            print(line.strip())
    
    return api_process

def open_ui():
    """Open the UI in the default web browser."""
    ui_path = get_package_root().parent.parent / "ui" / "index.html"
    if not ui_path.exists():
        print(f"UI file not found at {ui_path}")
        print("Searching for UI files...")
        
        # Try to find UI files in common locations
        possible_locations = [
            Path.cwd() / "ui" / "index.html",
            Path.home() / "research-assistant" / "ui" / "index.html",
        ]
        
        for location in possible_locations:
            if location.exists():
                ui_path = location
                print(f"Found UI at {ui_path}")
                break
        else:
            print("UI files not found. Please specify the location with --ui-path")
            return False
    
    print(f"Opening UI at {ui_path}")
    webbrowser.open(f"file://{ui_path}")
    return True

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Research Assistant")
    parser.add_argument("--api-only", action="store_true", help="Start only the API server")
    parser.add_argument("--ui-only", action="store_true", help="Open only the UI")
    parser.add_argument("--port", type=int, default=5000, help="Port for the API server")
    parser.add_argument("--ui-path", type=str, help="Path to the UI files")
    
    args = parser.parse_args()
    
    if args.api_only:
        api_process = start_api_server(args.port)
    elif args.ui_only:
        if args.ui_path:
            ui_path = Path(args.ui_path)
            if ui_path.exists():
                print(f"Opening UI at {ui_path}")
                webbrowser.open(f"file://{ui_path}")
            else:
                print(f"UI file not found at {ui_path}")
                return 1
        else:
            if not open_ui():
                return 1
    else:
        # Start both API and UI
        api_process = start_api_server(args.port)
        if not open_ui():
            api_process.terminate()
            return 1
        
        print("\nResearchAssistant is now running!")
        print(f"API server: http://localhost:{args.port}")
        print("\nPress Ctrl+C to stop the application")
        
        try:
            # Keep the script running until user interrupts
            api_process.wait()
        except KeyboardInterrupt:
            print("\nStopping ResearchAssistant...")
            api_process.terminate()
            print("Application stopped.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())