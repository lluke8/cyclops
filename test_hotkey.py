#!/usr/bin/env python3
"""
Test script to verify hotkey pressing functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.input_simulator import InputSimulator

def test_hotkey():
    """Test if F6 hotkey can be pressed"""
    config = {
        'input_simulation': {
            'mouse_speed': 0.5,
            'key_press_duration': 0.1,
            'fail_safe_enabled': True,
            'fail_safe_position': [0, 0]
        }
    }
    
    simulator = InputSimulator(config)
    
    print("Testing F6 hotkey press...")
    print("You should see F6 being pressed in 3 seconds...")
    
    import time
    time.sleep(3)
    
    result = simulator.press_key('f6')
    print(f"Hotkey press result: {result}")
    
    if result:
        print("✅ F6 hotkey press successful!")
    else:
        print("❌ F6 hotkey press failed!")

if __name__ == "__main__":
    test_hotkey()
