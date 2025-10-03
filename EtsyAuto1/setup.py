# setup.py
import os
import subprocess
import platform
from pathlib import Path

def setup_environment():
    """Set up the project environment"""
    
    print("Setting up Etsy Automation environment...")
    
    # Create necessary directories
    base_dir = Path.home() / "Documents" / "EtsyAutomation"
    output_dir = base_dir / "Output"
    log_dir = base_dir / "Logs"
    
    for directory in [base_dir, output_dir, log_dir]:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Install requirements
    print("Installing Python requirements...")
    try:
        subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
        print("Requirements installed successfully!")
    except subprocess.CalledProcessError:
        print("Error installing requirements. Make sure pip is available.")
    
    # Platform-specific checks
    system = platform.system()
    if system == "Darwin":
        db_path = Path.home() / "Snowflakes Database"
        if db_path.exists():
            print(f"✅ Database found at: {db_path}")
        else:
            print(f"❌ Database not found. Please ensure it's at: {db_path}")
    
    print("Setup complete!")

if __name__ == "__main__":
    setup_environment()