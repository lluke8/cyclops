"""
Screen capture functionality for Cyclops automation system.
Handles screenshot capture, window detection, and region selection.
"""

import logging
import time
from typing import Optional, Tuple, List
import pyautogui
import cv2
import numpy as np
from PIL import Image

class ScreenCapture:
    """Screen capture functionality with error handling and optimization"""
    
    def __init__(self, config: dict):
        """
        Initialize screen capture with configuration
        
        Args:
            config: Configuration dictionary containing capture settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.last_capture = None
        self.capture_count = 0
        self.capture_cache = {}
        
        # Configure pyautogui
        pyautogui.FAILSAFE = config.get('input_simulation', {}).get('fail_safe_enabled', True)
        
        # Get screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        self.logger.info(f"Screen resolution: {self.screen_width}x{self.screen_height}")
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        Capture screen with error handling and optimization
        
        Args:
            region: (x, y, width, height) tuple for region capture
            
        Returns:
            numpy array representing the captured image
            
        Raises:
            ScreenCaptureError: If capture fails
        """
        try:
            self.logger.debug(f"Capturing screen, region: {region}")
            
            # Take screenshot
            screenshot = pyautogui.screenshot(region=region)
            
            # Convert to numpy array for OpenCV compatibility
            img_array = np.array(screenshot)
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            self.capture_count += 1
            self.last_capture = img_array
            
            self.logger.debug(f"Screen captured successfully, count: {self.capture_count}")
            return img_array
            
        except Exception as e:
            self.logger.error(f"Screen capture failed: {e}")
            raise ScreenCaptureError(f"Failed to capture screen: {e}")
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """
        Capture specific screen region
        
        Args:
            x: Left coordinate
            y: Top coordinate
            width: Region width
            height: Region height
            
        Returns:
            numpy array representing the captured region
        """
        return self.capture_screen((x, y, width, height))
    
    def capture_window(self, window_title: str) -> Optional[np.ndarray]:
        """
        Capture specific window by title
        
        Args:
            window_title: Title of the window to capture
            
        Returns:
            numpy array of window content or None if window not found
        """
        try:
            # Find window
            windows = pyautogui.getWindowsWithTitle(window_title)
            if not windows:
                self.logger.warning(f"Window '{window_title}' not found")
                return None
            
            window = windows[0]
            if window.isMinimized:
                self.logger.warning(f"Window '{window_title}' is minimized")
                return None
            
            # Capture window region
            region = (window.left, window.top, window.width, window.height)
            return self.capture_screen(region)
            
        except Exception as e:
            self.logger.error(f"Window capture failed: {e}")
            return None
    
    def save_capture(self, filename: str, region: Optional[Tuple[int, int, int, int]] = None):
        """
        Save capture to file for debugging
        
        Args:
            filename: Path to save the screenshot
            region: Optional region to capture
        """
        if self.config.get('screen_capture', {}).get('save_screenshots', False):
            try:
                img = self.capture_screen(region)
                cv2.imwrite(filename, img)
                self.logger.info(f"Screenshot saved: {filename}")
            except Exception as e:
                self.logger.error(f"Failed to save screenshot: {e}")
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get current screen dimensions"""
        return self.screen_width, self.screen_height
    
    def is_region_valid(self, region: Tuple[int, int, int, int]) -> bool:
        """
        Validate if region is within screen bounds
        
        Args:
            region: (x, y, width, height) tuple
            
        Returns:
            True if region is valid, False otherwise
        """
        x, y, width, height = region
        return (x >= 0 and y >= 0 and 
                x + width <= self.screen_width and 
                y + height <= self.screen_height and
                width > 0 and height > 0)
    
    def get_available_windows(self) -> List[dict]:
        """
        Get list of available windows
        
        Returns:
            List of window information dictionaries
        """
        try:
            windows = []
            for window in pyautogui.getAllWindows():
                if window.title.strip():  # Only include windows with titles
                    windows.append({
                        'title': window.title,
                        'left': window.left,
                        'top': window.top,
                        'width': window.width,
                        'height': window.height,
                        'isMinimized': window.isMinimized,
                        'isMaximized': window.isMaximized
                    })
            return windows
        except Exception as e:
            self.logger.error(f"Failed to get window list: {e}")
            return []
    
    def capture_with_change_detection(self, region: Optional[Tuple[int, int, int, int]] = None, 
                                    threshold: float = 0.1) -> Tuple[np.ndarray, bool]:
        """
        Capture screen and detect if it has changed from last capture
        
        Args:
            region: Optional region to capture
            threshold: Change detection threshold (0.0 to 1.0)
            
        Returns:
            Tuple of (current_image, has_changed)
        """
        current_capture = self.capture_screen(region)
        
        if self.last_capture is None:
            self.last_capture = current_capture
            return current_capture, True
        
        # Calculate difference
        diff = cv2.absdiff(self.last_capture, current_capture)
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        change_percentage = np.sum(diff_gray > 30) / diff_gray.size
        
        has_changed = change_percentage > threshold
        
        if has_changed:
            self.last_capture = current_capture
        
        return current_capture, has_changed

class ScreenCaptureError(Exception):
    """Custom exception for screen capture errors"""
    pass
