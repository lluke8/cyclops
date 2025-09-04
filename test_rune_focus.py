#!/usr/bin/env python3
"""
Test script to verify the improved rune creation with focus handling
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import time
from utils.config_manager import ConfigManager
from core.screen_capture import ScreenCapture
from core.computer_vision import ComputerVision
from core.input_simulator import InputSimulator
from core.state_monitor import StateMonitor
from automation.rune_creation import RuneCreationAutomation

def test_rune_creation_with_focus():
    """Test rune creation with the new VM focus handling"""
    
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
    
    print("Testing rune creation with VM focus handling...")
    print("This will test the complete sequence including:")
    print("  - VM window focus before drag operation")
    print("  - Drag and drop with proper focus")
    print("  - Game window focus before hotkey press")
    print("  - Hotkey press with retry logic")
    print("\nMake sure your VM/game is running and visible.")
    print("Starting test in 5 seconds...")
    
    time.sleep(5)
    
    # Test the rune creation sequence
    try:
        result = rune_automation._create_rune_sequence()
        
        if result:
            print("✅ Rune creation sequence completed successfully!")
            print("The sequence should have:")
            print("  - Focused the VM window before dragging")
            print("  - Performed drag and drop correctly")
            print("  - Focused the game window before hotkey")
            print("  - Pressed F6 with retry logic")
        else:
            print("❌ Rune creation sequence failed!")
            print("Check the logs for more details.")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    print("\nTest completed. Check your VM/game to see if the rune was created.")

if __name__ == "__main__":
    test_rune_creation_with_focus()
