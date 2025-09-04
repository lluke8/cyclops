#!/usr/bin/env python3
"""
Test script to exactly replicate F2 behavior
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
from automation.workflow_manager import WorkflowManager

# Setup logging to see debug messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_f2_exact():
    """Test the exact F2 sequence as implemented in the main application"""
    
    print("Testing F2 Exact Sequence...")
    print("This replicates exactly what happens when you press F2 in the main app.")
    
    # Initialize components exactly like the main application
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
    
    # Create workflow manager exactly like the main application
    workflow_manager = WorkflowManager(
        config_manager,
        screen_capture,
        input_simulator,
        state_monitor
    )
    
    print("Starting F2 test in 5 seconds...")
    print("Make sure your target window is running and visible.")
    
    time.sleep(5)
    
    try:
        print("\n=== F2 Test: _test_rune_creation() ===")
        
        # This is exactly what F2 does in the main application
        rune_automation = workflow_manager.get_automation('rune_creation')
        if not rune_automation:
            print("❌ Rune creation automation not available")
            return
        
        # Check if rune positions are configured
        positions = rune_automation.get_rune_positions()
        if not positions:
            print("❌ No rune positions configured for test")
            return
        
        print(f"✅ Testing rune creation logic with {len(positions)} positions...")
        
        # Execute the rune creation sequence (this is what F2 does)
        success = rune_automation._create_rune_sequence()
        
        if success:
            print("✅ F2 rune creation sequence completed successfully!")
        else:
            print("❌ F2 rune creation sequence failed!")
            
    except Exception as e:
        print(f"❌ F2 test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== F2 test completed ===")

if __name__ == "__main__":
    test_f2_exact()
