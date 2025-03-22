"""
Build script for File Combiner application
This script will create a standalone executable using PyInstaller
"""

import os
import sys
import subprocess

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not."""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
        return True
    except ImportError:
        print("PyInstaller is not installed. Installing now...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller installed successfully.")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install PyInstaller. Please install it manually with:")
            print("pip install pyinstaller")
            return False

def build_executable(python_script):
    """Build standalone executable from the Python script."""
    if not os.path.exists(python_script):
        print(f"Error: Script {python_script} not found.")
        return False
    
    # Make sure the script name is valid
    if not python_script.endswith('.py'):
        print("Error: Script must be a Python file (.py extension)")
        return False
    
    print(f"Building executable for {python_script}...")
    
    # Build the executable with PyInstaller
    try:
        # Build with a simple GUI window (no console)
        subprocess.check_call([
            "pyinstaller",
            "--onefile",  # Create a single executable file
            "--windowed",  # No console window (for GUI apps)
            "--name", "FileCombiner",  # Name of the executable
            "--icon", "NONE",  # No icon
            python_script
        ])
        
        print("\nBuild completed successfully!")
        
        # Get the absolute path to the executable
        dist_dir = os.path.abspath(os.path.join(os.getcwd(), "dist"))
        if os.name == 'nt':  # Windows
            exe_path = os.path.join(dist_dir, "FileCombiner.exe")
        else:  # macOS/Linux
            exe_path = os.path.join(dist_dir, "FileCombiner")
            
        if os.path.exists(exe_path):
            print(f"\nExecutable created at: {exe_path}")
            return True
        else:
            print("\nError: Executable was not created.")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\nError during build process: {e}")
        return False

if __name__ == "__main__":
    # Script file name - replace with your actual script name if different
    script_name = "file_combiner.py"
    
    # Check command line arguments
    if len(sys.argv) > 1:
        script_name = sys.argv[1]
    
    if check_pyinstaller():
        build_executable(script_name)
    else:
        print("Build process aborted.")