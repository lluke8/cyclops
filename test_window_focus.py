#!/usr/bin/env python3
"""
Test script to verify window focus functionality
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

def test_window_focus():
    """Test window focus functionality"""
    
    print("Testing Window Focus Functionality...")
    print("This will test the complete window focus system.")
    print("Starting test in 3 seconds...")
    
    time.sleep(3)
    
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
    
    # Test 1: List available windows
    print("\n=== Test 1: List Available Windows ===")
    try:
        windows = input_simulator.get_available_windows()
        print(f"Found {len(windows)} windows:")
        for i, window in enumerate(windows[:10]):  # Show first 10
            print(f"  {i+1}. {window}")
        if len(windows) > 10:
            print(f"  ... and {len(windows) - 10} more")
    except Exception as e:
        print(f"❌ Failed to list windows: {e}")
    
    # Test 2: Test window focus (if user provides a window name)
    print("\n=== Test 2: Window Focus Test ===")
    print("Enter a window name to test focus (or press Enter to skip):")
    window_name = input("Window name: ").strip()
    
    if window_name:
        try:
            result = input_simulator.test_window_focus(window_name)
            if result['success']:
                print(f"✅ Window focus test successful!")
                print(f"   Window: {result['window_info']['title']}")
                print(f"   Process: {result['window_info']['process']}")
                print(f"   Size: {result['window_info']['size']}")
            else:
                print(f"❌ Window focus test failed: {result['message']}")
        except Exception as e:
            print(f"❌ Window focus test error: {e}")
    else:
        print("Skipping window focus test")
    
    # Test 3: Test rune creation with window focus
    print("\n=== Test 3: Rune Creation with Window Focus ===")
    print("This will test the complete rune creation sequence with window focus.")
    print("Make sure your target window is running and visible.")
    print("Starting test in 5 seconds...")
    
    time.sleep(5)
    
    # Create rune creation automation
    rune_automation = RuneCreationAutomation(
        config_manager, screen_capture, computer_vision, 
        input_simulator, state_monitor
    )
    
    try:
        print("\n=== Starting Rune Creation Sequence with Window Focus ===")
        
        # Test the rune creation sequence (same as F2)
        success = rune_automation._create_rune_sequence()
        
        if success:
            print("✅ Rune creation sequence completed successfully!")
            print("The sequence should have:")
            print("  - Found and focused the target window")
            print("  - Found the blank rune")
            print("  - Clicked on blank rune for VM focus")
            print("  - Performed drag and drop")
            print("  - Focused game window for hotkey")
            print("  - Pressed F6 with retry logic")
        else:
            print("❌ Rune creation sequence failed!")
            print("Check the logs for more details.")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_window_focus()
