#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import webbrowser
from pathlib import Path

def main():
    """Open index.html file in the default web browser."""
    try:
        # Look for index.html starting from current directory
        current_dir = Path.cwd()
        
        # Search in current directory and subdirectories
        for file_path in current_dir.rglob('index.html'):
            if file_path.is_file():
                # Convert to file URL
                url = f"file://{file_path.absolute()}"
                print(f"Opening: {url}")
                webbrowser.open(url)
                print("index.html opened in your default browser!")
                return
        
        print("Error: index.html not found in the project directory or subdirectories.")
        print(f"Searched in: {current_dir}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
