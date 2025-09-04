#!/usr/bin/env python3
"""
Test script to debug F2 rune creation sequence
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

def test_f2_sequence():
    """Test the complete F2 rune creation sequence"""
    
    print("Testing F2 rune creation sequence...")
    print("This will simulate what happens when you press F2.")
    print("Make sure your VM/game is running and visible.")
    print("Starting test in 5 seconds...")
    
    time.sleep(5)
    
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
    
    # Create rune creation automation
    rune_automation = RuneCreationAutomation(
        config_manager, screen_capture, computer_vision, 
        input_simulator, state_monitor
    )
    
    try:
        print("\n=== Starting Rune Creation Sequence ===")
        
        # Test the rune creation sequence (same as F2)
        success = rune_automation._create_rune_sequence()
        
        if success:
            print("✅ Rune creation sequence completed successfully!")
        else:
            print("❌ Rune creation sequence failed!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_f2_sequence()
