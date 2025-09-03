"""
Input simulation functionality for Cyclops automation system.
Handles mouse and keyboard automation with safety features.
"""

import logging
import time
import random
from typing import Tuple, Optional, List, Union
import pyautogui
import keyboard

class InputSimulator:
    """Input simulation with mouse and keyboard automation"""
    
    def __init__(self, config: dict):
        """
        Initialize input simulator with configuration
        
        Args:
            config: Configuration dictionary containing input settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.input_config = config.get('input_simulation', {})
        
        # Configure pyautogui
        self.mouse_speed = self.input_config.get('mouse_speed', 0.5)
        self.key_duration = self.input_config.get('key_press_duration', 0.1)
        self.fail_safe_enabled = self.input_config.get('fail_safe_enabled', True)
        self.fail_safe_position = tuple(self.input_config.get('fail_safe_position', [0, 0]))
        
        pyautogui.FAILSAFE = self.fail_safe_enabled
        pyautogui.PAUSE = 0.1  # Small pause between actions
        
        # Action tracking
        self.last_action_time = {}
        self.action_cooldowns = {}
        
        self.logger.info("Input Simulator initialized")
    
    def click(self, x: int, y: int, button: str = 'left', clicks: int = 1, 
              interval: float = 0.1) -> bool:
        """
        Perform mouse click at specified coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ('left', 'right', 'middle')
            clicks: Number of clicks
            interval: Interval between clicks
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.debug(f"Clicking at ({x}, {y}) with {button} button")
            
            # Move mouse to position first
            self.move_mouse(x, y)
            
            # Perform click
            pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
            
            # Add small delay
            time.sleep(0.1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Click failed: {e}")
            return False
    
    def right_click(self, x: int, y: int) -> bool:
        """Perform right click at specified coordinates"""
        return self.click(x, y, button='right')
    
    def double_click(self, x: int, y: int) -> bool:
        """Perform double click at specified coordinates"""
        return self.click(x, y, clicks=2)
    
    def move_mouse(self, x: int, y: int, duration: Optional[float] = None) -> bool:
        """
        Move mouse to specified coordinates
        
        Args:
            x: Target X coordinate
            y: Target Y coordinate
            duration: Movement duration (None for default speed)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.debug(f"Moving mouse to ({x}, {y})")
            
            # Use configured speed if duration not specified
            if duration is None:
                duration = self.mouse_speed
            
            # Add slight randomization to movement
            actual_x = x + random.randint(-2, 2)
            actual_y = y + random.randint(-2, 2)
            
            pyautogui.moveTo(actual_x, actual_y, duration=duration)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Mouse movement failed: {e}")
            return False
    
    def drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int, 
                     duration: float = 1.0) -> bool:
        """
        Perform drag and drop operation
        
        Args:
            start_x: Start X coordinate
            start_y: Start Y coordinate
            end_x: End X coordinate
            end_y: End Y coordinate
            duration: Drag duration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.debug(f"Dragging from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            
            # Move to start position
            self.move_mouse(start_x, start_y)
            
            # Perform drag
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Drag and drop failed: {e}")
            return False
    
    def press_key(self, key: str, duration: Optional[float] = None) -> bool:
        """
        Press a single key
        
        Args:
            key: Key to press (e.g., 'a', 'enter', 'f1', 'ctrl')
            duration: Key press duration (None for default)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.debug(f"Pressing key: {key}")
            
            # Use configured duration if not specified
            if duration is None:
                duration = self.key_duration
            
            pyautogui.press(key)
            time.sleep(duration)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Key press failed: {e}")
            return False
    
    def press_hotkey(self, *keys: str) -> bool:
        """
        Press key combination (hotkey)
        
        Args:
            *keys: Keys to press simultaneously (e.g., 'ctrl', 'c')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.debug(f"Pressing hotkey: {'+'.join(keys)}")
            
            pyautogui.hotkey(*keys)
            time.sleep(0.1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Hotkey press failed: {e}")
            return False
    
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """
        Type text with specified interval between characters
        
        Args:
            text: Text to type
            interval: Interval between characters
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.debug(f"Typing text: '{text}'")
            
            pyautogui.write(text, interval=interval)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Text typing failed: {e}")
            return False
    
    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """
        Perform mouse scroll
        
        Args:
            clicks: Number of scroll clicks (positive for up, negative for down)
            x: X coordinate for scroll (None for current position)
            y: Y coordinate for scroll (None for current position)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.debug(f"Scrolling {clicks} clicks at ({x}, {y})")
            
            if x is not None and y is not None:
                self.move_mouse(x, y)
            
            pyautogui.scroll(clicks)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Scroll failed: {e}")
            return False
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        try:
            return pyautogui.position()
        except Exception as e:
            self.logger.error(f"Failed to get mouse position: {e}")
            return (0, 0)
    
    def is_key_pressed(self, key: str) -> bool:
        """
        Check if a key is currently pressed
        
        Args:
            key: Key to check
            
        Returns:
            True if key is pressed, False otherwise
        """
        try:
            return keyboard.is_pressed(key)
        except Exception as e:
            self.logger.error(f"Key check failed: {e}")
            return False
    
    def wait_for_key(self, key: str, timeout: float = 10.0) -> bool:
        """
        Wait for a key to be pressed
        
        Args:
            key: Key to wait for
            timeout: Maximum wait time in seconds
            
        Returns:
            True if key was pressed, False if timeout
        """
        try:
            self.logger.debug(f"Waiting for key: {key} (timeout: {timeout}s)")
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.is_key_pressed(key):
                    return True
                time.sleep(0.1)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Key wait failed: {e}")
            return False
    
    def set_action_cooldown(self, action_name: str, cooldown_seconds: float):
        """
        Set cooldown for an action to prevent spam
        
        Args:
            action_name: Name of the action
            cooldown_seconds: Cooldown duration in seconds
        """
        self.action_cooldowns[action_name] = cooldown_seconds
    
    def can_perform_action(self, action_name: str) -> bool:
        """
        Check if an action can be performed (not in cooldown)
        
        Args:
            action_name: Name of the action
            
        Returns:
            True if action can be performed, False if in cooldown
        """
        if action_name not in self.action_cooldowns:
            return True
        
        last_time = self.last_action_time.get(action_name, 0)
        cooldown = self.action_cooldowns[action_name]
        
        return (time.time() - last_time) >= cooldown
    
    def record_action(self, action_name: str):
        """
        Record that an action was performed (for cooldown tracking)
        
        Args:
            action_name: Name of the action
        """
        self.last_action_time[action_name] = time.time()
    
    def safe_click(self, x: int, y: int, action_name: str = "click", 
                  cooldown: float = 0.5, **kwargs) -> bool:
        """
        Perform click with cooldown protection
        
        Args:
            x: X coordinate
            y: Y coordinate
            action_name: Action name for cooldown tracking
            cooldown: Cooldown duration in seconds
            **kwargs: Additional arguments for click method
            
        Returns:
            True if successful, False otherwise
        """
        if not self.can_perform_action(action_name):
            self.logger.debug(f"Action '{action_name}' is in cooldown")
            return False
        
        success = self.click(x, y, **kwargs)
        if success:
            self.record_action(action_name)
            self.set_action_cooldown(action_name, cooldown)
        
        return success
    
    def safe_press_key(self, key: str, action_name: str = None, 
                      cooldown: float = 0.5) -> bool:
        """
        Press key with cooldown protection
        
        Args:
            key: Key to press
            action_name: Action name for cooldown tracking (defaults to key)
            cooldown: Cooldown duration in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if action_name is None:
            action_name = f"key_{key}"
        
        if not self.can_perform_action(action_name):
            self.logger.debug(f"Action '{action_name}' is in cooldown")
            return False
        
        success = self.press_key(key)
        if success:
            self.record_action(action_name)
            self.set_action_cooldown(action_name, cooldown)
        
        return success

class InputSimulatorError(Exception):
    """Custom exception for input simulation errors"""
    pass
