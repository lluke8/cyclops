"""
Global hotkey system for Cyclops automation.
Allows hotkeys to work even when the application is not focused.
"""

import logging
import threading
import time
from typing import Dict, Callable, Optional
import keyboard
import queue

class GlobalHotkeyManager:
    """Manages global hotkeys that work system-wide"""
    
    def __init__(self):
        """Initialize global hotkey manager"""
        self.logger = logging.getLogger(__name__)
        self.hotkeys: Dict[str, Callable] = {}
        self.is_running = False
        self.hotkey_thread: Optional[threading.Thread] = None
        self.event_queue = queue.Queue()
        
        self.logger.info("Global Hotkey Manager initialized")
    
    def register_hotkey(self, key: str, callback: Callable, description: str = ""):
        """
        Register a global hotkey
        
        Args:
            key: Hotkey combination (e.g., 'f2', 'ctrl+shift+f2')
            callback: Function to call when hotkey is pressed
            description: Description of what the hotkey does
        """
        try:
            # Convert key to keyboard format
            keyboard_key = self._convert_key(key)
            
            # Register with keyboard library
            keyboard.add_hotkey(keyboard_key, self._hotkey_callback, args=(key, callback))
            
            self.hotkeys[key] = {
                'callback': callback,
                'description': description,
                'keyboard_key': keyboard_key
            }
            
            self.logger.info(f"Registered global hotkey: {key} - {description}")
            
        except Exception as e:
            self.logger.error(f"Failed to register hotkey {key}: {e}")
    
    def unregister_hotkey(self, key: str):
        """
        Unregister a global hotkey
        
        Args:
            key: Hotkey to unregister
        """
        try:
            if key in self.hotkeys:
                keyboard_key = self.hotkeys[key]['keyboard_key']
                keyboard.remove_hotkey(keyboard_key)
                del self.hotkeys[key]
                self.logger.info(f"Unregistered global hotkey: {key}")
        except Exception as e:
            self.logger.error(f"Failed to unregister hotkey {key}: {e}")
    
    def _convert_key(self, key: str) -> str:
        """
        Convert key format to keyboard library format
        
        Args:
            key: Key in our format (e.g., 'f2', 'ctrl+f2')
            
        Returns:
            Key in keyboard library format
        """
        # Convert to lowercase and handle special cases
        key = key.lower()
        
        # Handle function keys
        if key.startswith('f') and key[1:].isdigit():
            return key  # F1, F2, etc. are already correct
        
        # Handle combinations
        if '+' in key:
            parts = key.split('+')
            return '+'.join(parts)
        
        return key
    
    def _hotkey_callback(self, key: str, callback: Callable):
        """
        Callback function for hotkey presses
        
        Args:
            key: The hotkey that was pressed
            callback: The callback function to execute
        """
        try:
            self.logger.info(f"Global hotkey pressed: {key}")
            
            # Execute callback in a separate thread to avoid blocking
            def execute_callback():
                try:
                    callback()
                except Exception as e:
                    self.logger.error(f"Error executing hotkey callback for {key}: {e}")
            
            thread = threading.Thread(target=execute_callback, daemon=True)
            thread.start()
            
        except Exception as e:
            self.logger.error(f"Error in hotkey callback for {key}: {e}")
    
    def start(self):
        """Start the global hotkey manager"""
        if not self.is_running:
            self.is_running = True
            self.logger.info("Global hotkey manager started")
    
    def stop(self):
        """Stop the global hotkey manager"""
        if self.is_running:
            self.is_running = False
            
            # Unregister all hotkeys
            for key in list(self.hotkeys.keys()):
                self.unregister_hotkey(key)
            
            self.logger.info("Global hotkey manager stopped")
    
    def get_registered_hotkeys(self) -> Dict[str, str]:
        """
        Get list of registered hotkeys and their descriptions
        
        Returns:
            Dictionary of hotkey -> description
        """
        return {key: info['description'] for key, info in self.hotkeys.items()}

class GlobalHotkeyError(Exception):
    """Custom exception for global hotkey errors"""
    pass
