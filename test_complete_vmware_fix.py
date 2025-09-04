#!/usr/bin/env python3
"""
Complete VMware mouse input fix test
Tests all aspects of the VMware mouse input solution
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

def test_vmware_debugging():
    """Test VMware mouse debugging"""
    print("=== Step 1: VMware Mouse Debugging ===")
    print("This will test various mouse input methods to identify")
    print("which one works in your VMware environment.")
    print()
    
    input("Press Enter to start VMware debugging...")
    
    # Import and run the debug script
    try:
        from debug_vmware_mouse import VMwareMouseDebugger
        debugger = VMwareMouseDebugger()
        debugger.run_all_tests()
        return True
    except Exception as e:
        print(f"Debug test failed: {e}")
        return False

def test_vmware_input_simulator():
    """Test VMware input simulator"""
    print("\n=== Step 2: VMware Input Simulator ===")
    
    config_manager = ConfigManager()
    vmware_simulator = VMwareInputSimulator(config_manager.config)
    
    print("Testing VMware input functionality...")
    results = vmware_simulator.test_vmware_input()
    
    print(f"\nResults:")
    print(f"  Click test: {'✅' if results['click_test'] else '❌'}")
    print(f"  Move test: {'✅' if results['move_test'] else '❌'}")
    print(f"  Drag test: {'✅' if results['drag_test'] else '❌'}")
    print(f"  Key test: {'✅' if results['key_test'] else '❌'}")
    print(f"  Overall: {'✅' if results['overall'] else '❌'}")
    
    return results['overall']

def test_rune_creation_sequence():
    """Test complete rune creation sequence"""
    print("\n=== Step 3: Complete Rune Creation Sequence ===")
    
    # Initialize components
    config_manager = ConfigManager()
    screen_capture = ScreenCapture(config_manager.config)
    computer_vision = ComputerVision(config_manager.config)
    input_simulator = InputSimulator(config_manager.config)
    state_monitor = StateMonitor(config_manager.config, screen_capture, None, computer_vision)
    
    # Create rune automation
    rune_automation = RuneCreationAutomation(config_manager, screen_capture, computer_vision, input_simulator, state_monitor)
    
    print("Testing complete rune creation sequence...")
    print("This will test:")
    print("1. Window focus (should work)")
    print("2. Blank rune detection (should work)")
    print("3. VMware mouse click (NEW)")
    print("4. VMware drag and drop (NEW)")
    print("5. Hotkey press (should work)")
    print()
    
    input("Press Enter to start rune creation test...")
    
    # Test the rune creation sequence
    success = rune_automation._create_rune_sequence()
    
    if success:
        print("🎉 Rune creation sequence completed successfully!")
        print("✅ The VMware mouse input fix worked!")
    else:
        print("❌ Rune creation sequence failed!")
        print("   Check the logs above to see what failed")
    
    return success

def test_global_hotkeys():
    """Test global hotkeys"""
    print("\n=== Step 4: Global Hotkeys Test ===")
    
    try:
        from core.global_hotkeys import GlobalHotkeyManager
        
        def test_callback():
            print("🎉 GLOBAL HOTKEY TRIGGERED! This works from anywhere!")
        
        # Create global hotkey manager
        hotkey_manager = GlobalHotkeyManager()
        
        # Register F2 hotkey
        hotkey_manager.register_hotkey('f2', test_callback, "Test Global F2")
        
        # Start the manager
        hotkey_manager.start()
        
        print("Global hotkeys are now active!")
        print("Press F2 from ANY window to test!")
        print("Press Ctrl+C to continue...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping global hotkeys...")
            hotkey_manager.stop()
            print("✅ Global hotkeys test completed")
            return True
            
    except Exception as e:
        print(f"Global hotkeys test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Complete VMware Mouse Input Fix Test")
    print("====================================")
    print("This comprehensive test will:")
    print("1. Debug VMware mouse input issues")
    print("2. Test VMware-specific input simulator")
    print("3. Test complete rune creation sequence")
    print("4. Test global hotkeys")
    print()
    print("Make sure:")
    print("1. VMware window is focused and visible")
    print("2. You can see the mouse cursor moving")
    print("3. You're ready to observe the tests")
    print()
    
    input("Press Enter to start the complete test suite...")
    
    try:
        # Test 1: VMware debugging
        debug_success = test_vmware_debugging()
        
        if not debug_success:
            print("\n❌ VMware debugging failed!")
            print("   Check the debug output above for issues")
            return
        
        # Test 2: VMware input simulator
        vmware_input_success = test_vmware_input_simulator()
        
        if not vmware_input_success:
            print("\n❌ VMware input simulator failed!")
            print("   The VMware-specific input methods are not working")
            return
        
        # Test 3: Complete rune creation sequence
        rune_creation_success = test_rune_creation_sequence()
        
        if not rune_creation_success:
            print("\n❌ Rune creation sequence failed!")
            print("   Check the logs for specific error details")
            return
        
        # Test 4: Global hotkeys
        global_hotkeys_success = test_global_hotkeys()
        
        if not global_hotkeys_success:
            print("\n❌ Global hotkeys failed!")
            print("   F2 may not work from other windows")
            return
        
        # Final summary
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("="*50)
        print("✅ VMware mouse input debugging works")
        print("✅ VMware input simulator works")
        print("✅ Complete rune creation sequence works")
        print("✅ Global hotkeys work")
        print()
        print("Your VMware mouse input issues should now be resolved!")
        print("You can now:")
        print("1. Press F2 from any window to test rune creation")
        print("2. The rune creation should work completely")
        print("3. Mouse movement and drag operations should work")
        print()
        print("If you still have issues, check the logs above for specific errors.")
        
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
    except Exception as e:
        print(f"\nTest suite failed: {e}")

if __name__ == "__main__":
    main()
