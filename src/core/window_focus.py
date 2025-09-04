"""
Window focus handling for Cyclops automation system.
Provides functionality to find, focus, and manage target windows.
"""

import logging
import time
import re
from typing import Optional, List, Dict, Any, Tuple
import win32gui
import win32con
import win32api
import win32process
import psutil

class WindowFocusHandler:
    """Handles window focus operations for automation"""
    
    def __init__(self):
        """Initialize window focus handler"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Window Focus Handler initialized")
    
    def enumerate_windows(self) -> List[Dict[str, Any]]:
        """
        Enumerate all visible windows
        
        Returns:
            List of window dictionaries with title, hwnd, and other info
        """
        windows = []
        
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if window_title:  # Only include windows with titles
                    try:
                        # Get window rectangle
                        rect = win32gui.GetWindowRect(hwnd)
                        
                        # Get process info
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        try:
                            process = psutil.Process(pid)
                            process_name = process.name()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            process_name = "Unknown"
                        
                        windows.append({
                            'hwnd': hwnd,
                            'title': window_title,
                            'process_name': process_name,
                            'pid': pid,
                            'rect': rect,
                            'width': rect[2] - rect[0],
                            'height': rect[3] - rect[1]
                        })
                    except Exception as e:
                        self.logger.debug(f"Error getting window info for hwnd {hwnd}: {e}")
            
            return True
        
        try:
            win32gui.EnumWindows(enum_windows_callback, windows)
            self.logger.debug(f"Found {len(windows)} visible windows")
            return windows
        except Exception as e:
            self.logger.error(f"Failed to enumerate windows: {e}")
            return []
    
    def find_window_by_name(self, window_name: str, exact_match: bool = False) -> Optional[Dict[str, Any]]:
        """
        Find a window by name (exact or partial match)
        
        Args:
            window_name: Name or partial name of the window to find
            exact_match: If True, requires exact match; if False, uses partial match
            
        Returns:
            Window dictionary if found, None otherwise
        """
        if not window_name:
            return None
        
        windows = self.enumerate_windows()
        
        for window in windows:
            title = window['title']
            
            if exact_match:
                if title == window_name:
                    self.logger.info(f"Found exact match: '{title}'")
                    return window
            else:
                if window_name.lower() in title.lower():
                    self.logger.info(f"Found partial match: '{title}' (searching for '{window_name}')")
                    return window
        
        self.logger.warning(f"No window found matching '{window_name}'")
        return None
    
    def find_window_by_process(self, process_name: str) -> Optional[Dict[str, Any]]:
        """
        Find a window by process name
        
        Args:
            process_name: Name of the process (e.g., 'notepad.exe')
            
        Returns:
            Window dictionary if found, None otherwise
        """
        if not process_name:
            return None
        
        windows = self.enumerate_windows()
        
        for window in windows:
            if window['process_name'].lower() == process_name.lower():
                self.logger.info(f"Found window by process: '{window['title']}' (process: {process_name})")
                return window
        
        self.logger.warning(f"No window found with process '{process_name}'")
        return None
    
    def bring_window_to_foreground(self, window: Dict[str, Any]) -> bool:
        """
        Bring a window to the foreground and ensure it's active
        
        Args:
            window: Window dictionary from find_window_by_name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            hwnd = window['hwnd']
            title = window['title']
            
            self.logger.info(f"Bringing window to foreground: '{title}'")
            
            # Check if window is minimized
            if win32gui.IsIconic(hwnd):
                self.logger.debug("Window is minimized, restoring...")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.2)
            
            # Bring window to foreground
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.2)
            
            # Verify window is in foreground
            current_foreground = win32gui.GetForegroundWindow()
            if current_foreground == hwnd:
                self.logger.info(f"Successfully brought '{title}' to foreground")
                return True
            else:
                self.logger.warning(f"Failed to bring '{title}' to foreground")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to bring window to foreground: {e}")
            return False
    
    def ensure_window_focus(self, window_name: str, exact_match: bool = False) -> bool:
        """
        Find and focus a window by name
        
        Args:
            window_name: Name or partial name of the window
            exact_match: Whether to use exact or partial matching
            
        Returns:
            True if window was found and focused, False otherwise
        """
        try:
            # Find the window
            window = self.find_window_by_name(window_name, exact_match)
            if not window:
                return False
            
            # Bring it to foreground
            return self.bring_window_to_foreground(window)
            
        except Exception as e:
            self.logger.error(f"Failed to ensure window focus: {e}")
            return False
    
    def get_window_list(self) -> List[str]:
        """
        Get a list of all window titles for GUI display
        
        Returns:
            List of window titles
        """
        windows = self.enumerate_windows()
        return [f"{w['title']} ({w['process_name']})" for w in windows]
    
    def test_window_focus(self, window_name: str) -> Dict[str, Any]:
        """
        Test window focus functionality
        
        Args:
            window_name: Name of window to test
            
        Returns:
            Dictionary with test results
        """
        result = {
            'success': False,
            'window_found': False,
            'window_focused': False,
            'message': '',
            'window_info': None
        }
        
        try:
            # Find window
            window = self.find_window_by_name(window_name, exact_match=False)
            if window:
                result['window_found'] = True
                result['window_info'] = {
                    'title': window['title'],
                    'process': window['process_name'],
                    'size': f"{window['width']}x{window['height']}"
                }
                
                # Try to focus it
                if self.bring_window_to_foreground(window):
                    result['window_focused'] = True
                    result['success'] = True
                    result['message'] = f"Successfully focused window: '{window['title']}'"
                else:
                    result['message'] = f"Found window but failed to focus: '{window['title']}'"
            else:
                result['message'] = f"No window found matching: '{window_name}'"
                
        except Exception as e:
            result['message'] = f"Error during window focus test: {e}"
            self.logger.error(f"Window focus test failed: {e}")
        
        return result

class WindowFocusError(Exception):
    """Custom exception for window focus errors"""
    pass
