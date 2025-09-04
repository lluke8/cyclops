#!/usr/bin/env python3
"""
Test global hotkeys functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import time
import logging
from core.global_hotkeys import GlobalHotkeyManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_callback():
    """Test callback for global hotkeys"""
    print("🎉 GLOBAL HOTKEY TRIGGERED! This works from anywhere!")
    print("   You can now press F2 from any window!")

def test_global_hotkeys():
    """Test global hotkeys"""
    print("Testing Global Hotkeys...")
    print("Press F2 from any window to test!")
    print("Press Ctrl+C to exit")
    
    # Create global hotkey manager
    hotkey_manager = GlobalHotkeyManager()
    
    # Register F2 hotkey
    hotkey_manager.register_hotkey('f2', test_callback, "Test Global F2")
    
    # Start the manager
    hotkey_manager.start()
    
    try:
        print("Global hotkeys are now active!")
        print("Try pressing F2 from any window...")
        
        # Keep the program running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping global hotkeys...")
        hotkey_manager.stop()
        print("Global hotkeys stopped.")

if __name__ == "__main__":
    test_global_hotkeys()
