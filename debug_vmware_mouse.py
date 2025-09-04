#!/usr/bin/env python3
"""
Debug VMware mouse input issues
Tests various mouse input methods to identify the problem
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import time
import logging
import pyautogui
import win32api
import win32con
import win32gui
from typing import Tuple, List

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VMwareMouseDebugger:
    """Debug mouse input issues in VMware environment"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_positions = [
            (100, 100),   # Top-left
            (500, 300),   # Center
            (800, 600),   # Bottom-right
        ]
        
    def test_basic_mouse_movement(self):
        """Test basic mouse movement"""
        self.logger.info("=== Testing Basic Mouse Movement ===")
        
        for i, (x, y) in enumerate(self.test_positions):
            self.logger.info(f"Test {i+1}: Moving to ({x}, {y})")
            
            try:
                # Method 1: pyautogui
                pyautogui.moveTo(x, y, duration=0.5)
                current_pos = pyautogui.position()
                self.logger.info(f"  pyautogui: Moved to {current_pos}")
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"  pyautogui failed: {e}")
    
    def test_mouse_clicks(self):
        """Test mouse clicking"""
        self.logger.info("=== Testing Mouse Clicks ===")
        
        for i, (x, y) in enumerate(self.test_positions):
            self.logger.info(f"Test {i+1}: Clicking at ({x}, {y})")
            
            try:
                # Method 1: pyautogui
                pyautogui.click(x, y)
                self.logger.info(f"  pyautogui: Click successful")
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"  pyautogui click failed: {e}")
    
    def test_drag_operations(self):
        """Test drag and drop operations"""
        self.logger.info("=== Testing Drag Operations ===")
        
        start_pos = (100, 100)
        end_pos = (300, 300)
        
        self.logger.info(f"Testing drag from {start_pos} to {end_pos}")
        
        try:
            # Method 1: pyautogui drag
            pyautogui.drag(start_pos[0], start_pos[1], end_pos[0] - start_pos[0], end_pos[1] - start_pos[1], duration=1.0)
            self.logger.info(f"  pyautogui: Drag successful")
            
        except Exception as e:
            self.logger.error(f"  pyautogui drag failed: {e}")
    
    def test_win32_mouse_events(self):
        """Test Windows API mouse events"""
        self.logger.info("=== Testing Win32 Mouse Events ===")
        
        for i, (x, y) in enumerate(self.test_positions):
            self.logger.info(f"Test {i+1}: Win32 mouse at ({x}, {y})")
            
            try:
                # Method 2: win32api
                win32api.SetCursorPos((x, y))
                current_pos = win32api.GetCursorPos()
                self.logger.info(f"  win32api: Moved to {current_pos}")
                
                # Test click
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
                time.sleep(0.1)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
                self.logger.info(f"  win32api: Click successful")
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"  win32api failed: {e}")
    
    def test_vmware_specific_fixes(self):
        """Test VMware-specific mouse input fixes"""
        self.logger.info("=== Testing VMware-Specific Fixes ===")
        
        # Test 1: Disable pyautogui failsafe
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.1
        
        # Test 2: Use slower, more deliberate movements
        self.logger.info("Testing slow, deliberate movements...")
        
        for i, (x, y) in enumerate(self.test_positions):
            self.logger.info(f"Slow test {i+1}: Moving to ({x}, {y})")
            
            try:
                # Very slow movement
                pyautogui.moveTo(x, y, duration=2.0)
                current_pos = pyautogui.position()
                self.logger.info(f"  Slow movement: Moved to {current_pos}")
                
                # Click with delay
                time.sleep(0.5)
                pyautogui.click()
                self.logger.info(f"  Slow click: Successful")
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"  Slow movement failed: {e}")
    
    def test_coordinate_system(self):
        """Test coordinate system accuracy"""
        self.logger.info("=== Testing Coordinate System ===")
        
        # Get screen dimensions
        screen_width, screen_height = pyautogui.size()
        self.logger.info(f"Screen dimensions: {screen_width}x{screen_height}")
        
        # Test center of screen
        center_x, center_y = screen_width // 2, screen_height // 2
        self.logger.info(f"Center coordinates: ({center_x}, {center_y})")
        
        try:
            pyautogui.moveTo(center_x, center_y)
            current_pos = pyautogui.position()
            self.logger.info(f"Center test: Moved to {current_pos}")
            
            # Test if coordinates match
            if abs(current_pos.x - center_x) < 5 and abs(current_pos.y - center_y) < 5:
                self.logger.info("✅ Coordinate system is accurate")
            else:
                self.logger.warning("⚠️ Coordinate system may have issues")
                
        except Exception as e:
            self.logger.error(f"Coordinate test failed: {e}")
    
    def run_all_tests(self):
        """Run all mouse debugging tests"""
        self.logger.info("Starting VMware Mouse Input Debugging...")
        self.logger.info("Make sure VMware window is focused and visible!")
        self.logger.info("Press Ctrl+C to stop at any time")
        
        try:
            # Test 1: Basic movement
            self.test_basic_mouse_movement()
            time.sleep(2)
            
            # Test 2: Clicks
            self.test_mouse_clicks()
            time.sleep(2)
            
            # Test 3: Drag operations
            self.test_drag_operations()
            time.sleep(2)
            
            # Test 4: Win32 API
            self.test_win32_mouse_events()
            time.sleep(2)
            
            # Test 5: VMware-specific fixes
            self.test_vmware_specific_fixes()
            time.sleep(2)
            
            # Test 6: Coordinate system
            self.test_coordinate_system()
            
            self.logger.info("=== All tests completed ===")
            self.logger.info("Check the logs above to identify which method works!")
            
        except KeyboardInterrupt:
            self.logger.info("Tests interrupted by user")
        except Exception as e:
            self.logger.error(f"Test suite failed: {e}")

def main():
    """Main function"""
    print("VMware Mouse Input Debugger")
    print("==========================")
    print("This will test various mouse input methods to identify")
    print("which one works in your VMware environment.")
    print()
    print("Make sure:")
    print("1. VMware window is focused and visible")
    print("2. You can see the mouse cursor moving")
    print("3. You're ready to observe the tests")
    print()
    
    input("Press Enter to start testing...")
    
    debugger = VMwareMouseDebugger()
    debugger.run_all_tests()

if __name__ == "__main__":
    main()
