#!/usr/bin/env python3
"""
Cyclops - Desktop Automation Application
Main entry point for the Cyclops automation system.

This application provides reactive automation based on screen state monitoring,
with capabilities for OCR, computer vision, and input simulation.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import logging

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('cyclops.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('cyclops')

def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        'pyautogui', 'cv2', 'pytesseract', 'PIL', 
        'keyboard', 'psutil', 'numpy'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        error_msg = f"Missing required modules: {', '.join(missing_modules)}\n"
        error_msg += "Please install them using: python -m pip install -r requirements.txt"
        messagebox.showerror("Missing Dependencies", error_msg)
        return False
    
    return True

def main():
    """Main application entry point"""
    logger = setup_logging()
    logger.info("Starting Cyclops Desktop Automation Application")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Missing dependencies. Exiting.")
        sys.exit(1)
    
    try:
        # Import GUI components
        from gui.main_window import CyclopsMainWindow
        
        # Create and run the main application
        root = tk.Tk()
        app = CyclopsMainWindow(root)
        
        logger.info("Application started successfully")
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application: {e}")
        sys.exit(1)
    
    logger.info("Application closed")

if __name__ == "__main__":
    main()
