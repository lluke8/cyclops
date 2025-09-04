#!/usr/bin/env python3
"""
Quick F2 test to identify the exact issue
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=== Quick F2 Test ===")
print("This will test each step of the F2 process...")

from utils.config_manager import ConfigManager
from core.screen_capture import ScreenCapture
from core.computer_vision import ComputerVision
from core.input_simulator import InputSimulator
from core.state_monitor import StateMonitor
from automation.rune_creation import RuneCreationAutomation

# Initialize
config_manager = ConfigManager()
screen_capture = ScreenCapture(config_manager.config)
computer_vision = ComputerVision(config_manager.config)
input_simulator = InputSimulator(config_manager.config)
state_monitor = StateMonitor(config_manager.config, screen_capture, None, computer_vision)

rune_automation = RuneCreationAutomation(config_manager, screen_capture, computer_vision, input_simulator, state_monitor)

print("\n1. Testing window focus...")
target_window = config_manager.get('automation.rune_creation.target_window_name', '')
if target_window:
    print(f"   Target window: '{target_window}'")
    focus_result = input_simulator.ensure_target_window_focus(target_window, exact_match=False)
    print(f"   Window focus result: {focus_result}")
else:
    print("   ❌ No target window configured!")

print("\n2. Testing blank rune detection...")
blank_rune_location = rune_automation._find_blank_rune()
if blank_rune_location:
    print(f"   ✅ Blank rune found at: {blank_rune_location}")
else:
    print("   ❌ Blank rune NOT found!")
    print("   This is why F2 stops after window focus!")

print("\n3. Testing rune positions...")
positions = rune_automation.get_rune_positions()
print(f"   Rune positions: {len(positions)} configured")
if positions:
    print(f"   Positions: {positions}")
else:
    print("   ❌ No rune positions configured!")

print("\n=== Test Complete ===")
print("If blank rune detection fails, that's why F2 stops after window focus.")
