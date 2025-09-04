"""
VMware-specific input simulator
Addresses common VMware mouse input issues
"""

import logging
import time
import random
from typing import Tuple, Optional, List, Union
import pyautogui
import win32api
import win32con
import win32gui
import psutil

class VMwareInputSimulator:
    """Input simulator optimized for VMware environments"""
    
    def __init__(self, config: dict):
        """Initialize VMware input simulator"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # VMware-specific settings
        self.vmware_mode = config.get('vmware_mode', True)
        self.input_delay = config.get('input_delay', 0.2)
        self.movement_duration = config.get('movement_duration', 1.0)
        self.click_delay = config.get('click_delay', 0.1)
        
        # Configure pyautogui for VMware
        if self.vmware_mode:
            pyautogui.FAILSAFE = False  # Disable failsafe in VM
            pyautogui.PAUSE = self.input_delay  # Add delay between actions
        
        self.logger.info("VMware Input Simulator initialized")
        self.logger.info(f"VMware mode: {self.vmware_mode}")
        self.logger.info(f"Input delay: {self.input_delay}s")
        self.logger.info(f"Movement duration: {self.movement_duration}s")
    
    def click(self, x: int, y: int, button: str = 'left', clicks: int = 1) -> bool:
        """
        Perform a click at the specified coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ('left', 'right', 'middle')
            clicks: Number of clicks
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"VMware click at ({x}, {y}) with {button} button, {clicks} clicks")
            
            # Method 1: Try pyautogui first (usually works in VMware)
            if self.vmware_mode:
                # Move to position first
                pyautogui.moveTo(x, y, duration=self.movement_duration)
                time.sleep(self.click_delay)
                
                # Perform click
                pyautogui.click(x, y, clicks=clicks, button=button)
                self.logger.info("pyautogui click successful")
                return True
            else:
                # Standard pyautogui
                pyautogui.click(x, y, clicks=clicks, button=button)
                return True
                
        except Exception as e:
            self.logger.error(f"pyautogui click failed: {e}")
            
            # Method 2: Fallback to win32api
            try:
                self.logger.info("Trying win32api fallback...")
                win32api.SetCursorPos((x, y))
                time.sleep(self.click_delay)
                
                # Map button names to win32 constants
                button_map = {
                    'left': win32con.MOUSEEVENTF_LEFTDOWN,
                    'right': win32con.MOUSEEVENTF_RIGHTDOWN,
                    'middle': win32con.MOUSEEVENTF_MIDDLEDOWN
                }
                
                if button in button_map:
                    for _ in range(clicks):
                        win32api.mouse_event(button_map[button], x, y, 0, 0)
                        time.sleep(0.05)
                        win32api.mouse_event(button_map[button] | 0x0004, x, y, 0, 0)  # Release
                        time.sleep(0.05)
                    
                    self.logger.info("win32api click successful")
                    return True
                else:
                    self.logger.error(f"Unsupported button: {button}")
                    return False
                    
            except Exception as e2:
                self.logger.error(f"win32api click also failed: {e2}")
                return False
    
    def drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1.0) -> bool:
        """
        Perform drag and drop operation
        
        Args:
            start_x: Start X coordinate
            start_y: Start Y coordinate
            end_x: End X coordinate
            end_y: End Y coordinate
            duration: Duration of the drag operation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"VMware drag from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            
            if self.vmware_mode:
                # VMware-optimized drag
                # Step 1: Move to start position
                pyautogui.moveTo(start_x, start_y, duration=self.movement_duration)
                time.sleep(self.click_delay)
                
                # Step 2: Click and hold
                pyautogui.mouseDown(button='left')
                time.sleep(0.2)  # Hold for a moment
                
                # Step 3: Drag to end position
                pyautogui.dragTo(end_x, end_y, duration=duration, button='left')
                time.sleep(0.1)
                
                # Step 4: Release
                pyautogui.mouseUp(button='left')
                
                self.logger.info("VMware drag successful")
                return True
            else:
                # Standard drag
                pyautogui.drag(start_x, start_y, end_x - start_x, end_y - start_y, duration=duration)
                return True
                
        except Exception as e:
            self.logger.error(f"VMware drag failed: {e}")
            
            # Fallback: Try win32api drag
            try:
                self.logger.info("Trying win32api drag fallback...")
                
                # Move to start
                win32api.SetCursorPos((start_x, start_y))
                time.sleep(self.click_delay)
                
                # Mouse down
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, start_x, start_y, 0, 0)
                time.sleep(0.2)
                
                # Drag to end
                steps = max(10, int(duration * 10))  # At least 10 steps
                for i in range(steps):
                    progress = i / steps
                    current_x = int(start_x + (end_x - start_x) * progress)
                    current_y = int(start_y + (end_y - start_y) * progress)
                    
                    win32api.SetCursorPos((current_x, current_y))
                    time.sleep(duration / steps)
                
                # Mouse up
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, end_x, end_y, 0, 0)
                
                self.logger.info("win32api drag successful")
                return True
                
            except Exception as e2:
                self.logger.error(f"win32api drag also failed: {e2}")
                return False
    
    def press_key(self, key: str) -> bool:
        """
        Press a key
        
        Args:
            key: Key to press
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"VMware key press: {key}")
            
            if self.vmware_mode:
                # Add delay before key press
                time.sleep(self.input_delay)
            
            pyautogui.press(key)
            self.logger.info("Key press successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Key press failed: {e}")
            return False
    
    def type_text(self, text: str) -> bool:
        """
        Type text
        
        Args:
            text: Text to type
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"VMware text input: {text[:50]}...")
            
            if self.vmware_mode:
                # Add delay before typing
                time.sleep(self.input_delay)
            
            pyautogui.typewrite(text, interval=0.05)  # Slow typing for VM
            self.logger.info("Text input successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Text input failed: {e}")
            return False
    
    def move_to(self, x: int, y: int, duration: float = None) -> bool:
        """
        Move mouse to coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Movement duration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if duration is None:
                duration = self.movement_duration
                
            self.logger.info(f"VMware move to ({x}, {y})")
            
            pyautogui.moveTo(x, y, duration=duration)
            self.logger.info("Move successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Move failed: {e}")
            return False
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse position
        
        Returns:
            Tuple of (x, y) coordinates
        """
        try:
            pos = pyautogui.position()
            return (pos.x, pos.y)
        except Exception as e:
            self.logger.error(f"Failed to get mouse position: {e}")
            return (0, 0)
    
    def test_vmware_input(self) -> dict:
        """
        Test VMware input functionality
        
        Returns:
            Dictionary with test results
        """
        results = {
            'click_test': False,
            'drag_test': False,
            'key_test': False,
            'move_test': False,
            'overall': False
        }
        
        try:
            self.logger.info("Testing VMware input functionality...")
            
            # Test 1: Click test
            try:
                current_pos = self.get_mouse_position()
                self.click(current_pos[0], current_pos[1])
                results['click_test'] = True
                self.logger.info("✅ Click test passed")
            except Exception as e:
                self.logger.error(f"❌ Click test failed: {e}")
            
            # Test 2: Move test
            try:
                self.move_to(100, 100)
                time.sleep(0.5)
                self.move_to(200, 200)
                results['move_test'] = True
                self.logger.info("✅ Move test passed")
            except Exception as e:
                self.logger.error(f"❌ Move test failed: {e}")
            
            # Test 3: Drag test
            try:
                self.drag_and_drop(100, 100, 200, 200, 0.5)
                results['drag_test'] = True
                self.logger.info("✅ Drag test passed")
            except Exception as e:
                self.logger.error(f"❌ Drag test failed: {e}")
            
            # Test 4: Key test
            try:
                self.press_key('space')
                results['key_test'] = True
                self.logger.info("✅ Key test passed")
            except Exception as e:
                self.logger.error(f"❌ Key test failed: {e}")
            
            # Overall result
            results['overall'] = all([
                results['click_test'],
                results['move_test'],
                results['drag_test'],
                results['key_test']
            ])
            
            if results['overall']:
                self.logger.info("🎉 All VMware input tests passed!")
            else:
                self.logger.warning("⚠️ Some VMware input tests failed")
            
        except Exception as e:
            self.logger.error(f"VMware input test failed: {e}")
        
        return results
