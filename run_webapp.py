#!/usr/bin/env python
"""
Helper script to run the Sales Automation AI web application.
This script ensures the correct Python path is set before running the app.
"""

import os
import sys

# Add the project root directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    # Import and run the application
    from webapp.app import create_app, run_app
    
    if __name__ == "__main__":
        print("Starting Sales Automation AI web application...")
        print("Access the application at: http://localhost:8080")
        app = create_app()
        run_app(app, host='0.0.0.0', port=8080, debug=True)
        
except ImportError as e:
    print(f"Error: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Make sure you're running this script from the project root directory")
    print("2. Verify that the 'webapp' directory exists in:", current_dir)
    print("3. Check for any circular import issues in the webapp modules")
    print("4. Make sure all dependencies are installed: pip install -r requirements.txt") 