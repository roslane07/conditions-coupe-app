"""
Launcher script for the cutting conditions calculator.
Handles environment setup and application launch.
"""

import subprocess
import os
import sys
import importlib.util
from datetime import datetime
import logging

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        filename="app.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def log_message(level: str, message: str):
    """
    Log a message with the specified level.
    
    Args:
        level (str): Log level (info, warning, error)
        message (str): Message to log
    """
    getattr(logging, level)(message)
    print(f"[{level.upper()}] {message}")

def check_requirements():
    """Check if all required packages are installed."""
    required_packages = ["streamlit", "pandas", "plotly", "numpy"]
    missing_packages = []
    
    for package in required_packages:
        if not importlib.util.find_spec(package):
            missing_packages.append(package)
            
    if missing_packages:
        log_message("error", f"Missing required packages: {', '.join(missing_packages)}")
        log_message("info", "Installing missing packages...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            log_message("info", "Packages installed successfully")
        except subprocess.CalledProcessError:
            log_message("error", "Failed to install packages")
            sys.exit(1)

def main():
    """Main launcher function."""
    setup_logging()
    log_message("info", "Starting application launcher")
    
    # Check project directory
    project_path = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(project_path, "src", "app.py")):
        log_message("error", f"Application file not found in: {project_path}")
        sys.exit(1)
        
    # Check requirements
    check_requirements()
    
    # Launch application
    try:
        log_message("info", "Launching application...")
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "src/app.py"],
            check=True,
            cwd=project_path
        )
    except subprocess.CalledProcessError as e:
        log_message("error", f"Application failed to start: {str(e)}")
        sys.exit(1)
    except Exception as e:
        log_message("error", f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
