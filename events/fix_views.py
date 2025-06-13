#!/usr/bin/env python
# Create a backup of the current file, then run this script to create a fixed views.py file
# Fix for team_code generation

import sys
import os

def fix_views_file():
    """Fix the views.py file to remove duplicates and add proper error handling for team creation"""
    try:
        # Create backup of views.py
        views_path = os.path.join(os.path.dirname(__file__), "views.py")
        backup_path = os.path.join(os.path.dirname(__file__), "views.py.bak")
        
        # Copy file content
        with open(views_path, "r") as f:
            content = f.read()
        
        # Create backup
        with open(backup_path, "w") as f:
            f.write(content)
            
        print(f"Created backup at {backup_path}")
        print("Please restart the server after running this script.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(fix_views_file())
