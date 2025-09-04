#!/usr/bin/env python3
"""
Test VMware mouse input fixes
Tests both debugging and VMware-specific input methods
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
from core.vmware_input_simulator import VMwareInputSimulator
from core.state_monitor import StateMonitor
from automation.rune_creation import RuneCreationAutomation

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_vmware_input_simulator():
    """Test VMware input simulator"""
    print("=== Testing VMware Input Simulator ===")
    
    config_manager = ConfigManager()
    vmware_simulator = VMwareInputSimulator(config_manager.config)
    
    # Test VMware input functionality
    results = vmware_simulator.test_vmware_input()
    
    print(f"Click test: {'✅' if results['click_test'] else '❌'}")
    print(f"Move test: {'✅' if results['move_test'] else '❌'}")
    print(f"Drag test: {'✅' if results['drag_test'] else '❌'}")
    print(f"Key test: {'✅' if results['key_test'] else '❌'}")
    print(f"Overall: {'✅' if results['overall'] else '❌'}")
    
    return results['overall']

def test_rune_creation_with_vmware():
    """Test rune creation with VMware input simulator"""
    print("\n=== Testing Rune Creation with VMware Input ===")
    
    # Initialize components
    config_manager = ConfigManager()
    screen_capture = ScreenCapture(config_manager.config)
    computer_vision = ComputerVision(config_manager.config)
    input_simulator = InputSimulator(config_manager.config)
    state_monitor = StateMonitor(config_manager.config, screen_capture, None, computer_vision)
    
    # Create rune automation with VMware input
    rune_automation = RuneCreationAutomation(config_manager, screen_capture, computer_vision, input_simulator, state_monitor)
    
    print("Starting rune creation sequence with VMware input...")
    print("This will test:")
    print("1. Window focus (should work)")
    print("2. Blank rune detection (should work)")
    print("3. VMware mouse click (NEW)")
    print("4. VMware drag and drop (NEW)")
    print("5. Hotkey press (should work)")
    print()
    
    # Test the rune creation sequence
    success = rune_automation._create_rune_sequence()
    
    if success:
        print("🎉 Rune creation with VMware input completed successfully!")
        print("✅ The VMware mouse input fix worked!")
    else:
        print("❌ Rune creation with VMware input failed!")
        print("   Check the logs above to see what failed")
    
    return success

def test_comparison():
    """Test comparison between standard and VMware input"""
    print("\n=== Testing Input Method Comparison ===")
    
    config_manager = ConfigManager()
    
    # Test 1: Standard input simulator
    print("Testing standard input simulator...")
    standard_simulator = InputSimulator(config_manager.config)
    
    # Test 2: VMware input simulator
    print("Testing VMware input simulator...")
    vmware_simulator = VMwareInputSimulator(config_manager.config)
    
    # Test coordinates
    test_x, test_y = 100, 100
    
    print(f"\nTesting click at ({test_x}, {test_y})...")
    
    # Standard click
    print("Standard click:")
    try:
        result1 = standard_simulator.click(test_x, test_y)
        print(f"  Result: {'✅' if result1 else '❌'}")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(1)
    
    # VMware click
    print("VMware click:")
    try:
        result2 = vmware_simulator.click(test_x, test_y)
        print(f"  Result: {'✅' if result2 else '❌'}")
    except Exception as e:
        print(f"  Error: {e}")
    
    return result1, result2

def main():
    """Main test function"""
    print("VMware Mouse Input Fix Test")
    print("==========================")
    print("This tests the VMware-specific mouse input fixes")
    print("to resolve the drag and drop issues in VMware.")
    print()
    print("Make sure:")
    print("1. VMware window is focused and visible")
    print("2. You can see the mouse cursor moving")
    print("3. You're ready to observe the tests")
    print()
    
    input("Press Enter to start testing...")
    
    try:
        # Test 1: VMware input simulator
        vmware_input_works = test_vmware_input_simulator()
        
        if vmware_input_works:
            print("\n✅ VMware input simulator is working!")
        else:
            print("\n❌ VMware input simulator has issues!")
            print("   Run the debug script to identify the problem:")
            print("   python debug_vmware_mouse.py")
            return
        
        # Test 2: Input method comparison
        standard_result, vmware_result = test_comparison()
        
        print(f"\nComparison results:")
        print(f"Standard input: {'✅' if standard_result else '❌'}")
        print(f"VMware input: {'✅' if vmware_result else '❌'}")
        
        # Test 3: Full rune creation with VMware input
        if vmware_result:
            print("\nTesting full rune creation with VMware input...")
            rune_success = test_rune_creation_with_vmware()
            
            if rune_success:
                print("\n🎉 SUCCESS! The VMware mouse input fix worked!")
                print("   Your rune creation should now work properly!")
            else:
                print("\n❌ Rune creation still failed!")
                print("   Check the logs for specific error details")
        else:
            print("\n⚠️ VMware input not working, skipping rune creation test")
        
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
    except Exception as e:
        print(f"\nTest suite failed: {e}")

if __name__ == "__main__":
    main()
