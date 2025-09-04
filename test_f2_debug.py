#!/usr/bin/env python3
"""
Debug script to test F2 rune creation with window focus
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

# Setup logging to see debug messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_f2_debug():
    """Debug F2 rune creation with window focus"""
    
    print("Debug F2 Rune Creation with Window Focus...")
    
    # Initialize components
    config_manager = ConfigManager()
    screen_capture = ScreenCapture(config_manager.config)
    computer_vision = ComputerVision(config_manager.config)
    input_simulator = InputSimulator(config_manager.config)
    state_monitor = StateMonitor(
        config_manager.config, 
        screen_capture, 
        None,  # OCR not needed for this test
        computer_vision
    )
    
    # Check current configuration
    print("\n=== Current Configuration ===")
    window_focus_enabled = config_manager.get('automation.rune_creation.window_focus_enabled', True)
    target_window = config_manager.get('automation.rune_creation.target_window_name', '')
    
    print(f"Window focus enabled: {window_focus_enabled}")
    print(f"Target window name: '{target_window}'")
    
    if not target_window:
        print("\n❌ ISSUE FOUND: No target window name configured!")
        print("This is why window focus is being skipped.")
        print("\nTo fix this:")
        print("1. Open the main application GUI")
        print("2. Go to the Rune Creation section")
        print("3. In the 'Window Focus' section:")
        print("   - Make sure 'Enable Window Focus' is checked")
        print("   - Enter a target window name (e.g., 'VMware Workstation')")
        print("   - Or use 'Refresh Window List' and double-click a window")
        print("   - Click 'Test Window Focus' to verify it works")
        print("4. Save the configuration")
        return
    
    # Create rune creation automation
    rune_automation = RuneCreationAutomation(
        config_manager, screen_capture, computer_vision, 
        input_simulator, state_monitor
    )
    
    print(f"\n✅ Configuration looks good. Target window: '{target_window}'")
    print("Starting F2 test in 5 seconds...")
    print("Make sure your target window is running and visible.")
    
    time.sleep(5)
    
    try:
        print("\n=== Starting F2 Rune Creation Sequence ===")
        
        # Test the rune creation sequence (same as F2)
        success = rune_automation._create_rune_sequence()
        
        if success:
            print("✅ F2 rune creation sequence completed successfully!")
        else:
            print("❌ F2 rune creation sequence failed!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Debug completed ===")

if __name__ == "__main__":
    test_f2_debug()
