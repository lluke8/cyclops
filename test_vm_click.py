#!/usr/bin/env python3
"""
Test script to verify VM click functionality
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

def test_vm_click():
    """Test VM click functionality"""
    
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
    
    print("Testing VM click functionality...")
    print("This will test clicking on the blank rune position to ensure VM focus.")
    print("Make sure your VM/game is running and visible.")
    print("Starting test in 5 seconds...")
    
    time.sleep(5)
    
    # Test just the VM focus part
    try:
        # Get a blank rune position (simulate finding one)
        blank_x, blank_y = 1500, 250  # Example position
        print(f"Simulating blank rune at ({blank_x}, {blank_y})")
        
        # Test the VM focus click
        print("Clicking on blank rune position to ensure VM focus...")
        input_simulator.click(blank_x, blank_y)
        time.sleep(0.3)
        
        print("✅ VM focus click completed!")
        print("Check if your VM window gained focus.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    test_vm_click()
