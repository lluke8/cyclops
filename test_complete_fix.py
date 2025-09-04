#!/usr/bin/env python3
"""
Test complete fix for both issues:
1. F2 test stopping after window focus
2. F2 only working when GUI is focused
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import time
import logging
from utils.config_manager import ConfigManager
from core.screen_capture import ScreenCapture
from core.computer_vision import ComputerVision
from core.input_simulator import InputSimulator
from core.state_monitor import StateMonitor
from automation.rune_creation import RuneCreationAutomation
from core.global_hotkeys import GlobalHotkeyManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_rune_creation():
    """Test rune creation (same as F2)"""
    print("🎯 Testing Rune Creation (F2 equivalent)...")
    
    # Initialize components
    config_manager = ConfigManager()
    screen_capture = ScreenCapture(config_manager.config)
    computer_vision = ComputerVision(config_manager.config)
    input_simulator = InputSimulator(config_manager.config)
    state_monitor = StateMonitor(config_manager.config, screen_capture, None, computer_vision)
    
    rune_automation = RuneCreationAutomation(config_manager, screen_capture, computer_vision, input_simulator, state_monitor)
    
    # Test the rune creation sequence
    success = rune_automation._create_rune_sequence()
    
    if success:
        print("✅ Rune creation completed successfully!")
    else:
        print("❌ Rune creation failed!")
    
    return success

def test_complete_fix():
    """Test both fixes"""
    print("=== Complete Fix Test ===")
    print("This tests both issues:")
    print("1. F2 test stopping after window focus")
    print("2. F2 only working when GUI is focused")
    print()
    
    # Test 1: Rune creation sequence
    print("=== Test 1: Rune Creation Sequence ===")
    print("Testing if the rune creation sequence works completely...")
    print("Starting in 3 seconds...")
    time.sleep(3)
    
    success = test_rune_creation()
    
    if success:
        print("✅ Issue 1 FIXED: Rune creation sequence works completely!")
    else:
        print("❌ Issue 1 NOT FIXED: Rune creation still stops after window focus")
    
    print()
    
    # Test 2: Global hotkeys
    print("=== Test 2: Global Hotkeys ===")
    print("Testing if F2 works from any window...")
    print("Press F2 from ANY window to test!")
    print("Press Ctrl+C to exit")
    print()
    
    # Create global hotkey manager
    hotkey_manager = GlobalHotkeyManager()
    
    # Register F2 hotkey
    hotkey_manager.register_hotkey('f2', test_rune_creation, "Test Rune Creation")
    
    # Start the manager
    hotkey_manager.start()
    
    try:
        print("✅ Global hotkeys are now active!")
        print("   Try pressing F2 from any window (browser, notepad, etc.)")
        print("   The rune creation should start!")
        
        # Keep the program running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping global hotkeys...")
        hotkey_manager.stop()
        print("✅ Global hotkeys stopped.")

if __name__ == "__main__":
    test_complete_fix()
