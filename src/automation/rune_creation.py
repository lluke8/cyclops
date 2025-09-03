"""
Rune creation automation for Cyclops automation system.
Implements automated rune creation workflow with item detection and drag-and-drop.
"""

import logging
import time
from typing import Optional, Tuple, Dict, Any
from core.screen_capture import ScreenCapture
from core.computer_vision import ComputerVision
from core.input_simulator import InputSimulator
from core.state_monitor import StateMonitor
from utils.timing import TimingUtils
from utils.config_manager import ConfigManager

class RuneCreationAutomation:
    """Rune creation automation with robust error handling"""
    
    def __init__(self, config_manager: ConfigManager, screen_capture: ScreenCapture, 
                 computer_vision: ComputerVision, input_simulator: InputSimulator,
                 state_monitor: StateMonitor):
        """
        Initialize rune creation automation
        
        Args:
            config_manager: Configuration manager instance
            screen_capture: Screen capture instance
            computer_vision: Computer vision instance
            input_simulator: Input simulator instance
            state_monitor: State monitor instance
        """
        self.config_manager = config_manager
        self.screen_capture = screen_capture
        self.computer_vision = computer_vision
        self.input_simulator = input_simulator
        self.state_monitor = state_monitor
        self.timing = TimingUtils()
        self.logger = logging.getLogger(__name__)
        
        # Get automation configuration
        self.config = self.config_manager.get_automation_config('rune_creation')
        self.is_running = False
        self.creation_count = 0
        self.failure_count = 0
        
        # Setup cooldowns
        self.timing.set_cooldown('rune_creation', 2.0)
        self.timing.set_cooldown('item_detection', 1.0)
        
        self.logger.info("Rune Creation Automation initialized")
    
    def start_automation(self) -> bool:
        """
        Start the rune creation automation
        
        Returns:
            True if started successfully, False otherwise
        """
        if not self.config.get('enabled', False):
            self.logger.warning("Rune creation automation is disabled in configuration")
            return False
        
        if self.is_running:
            self.logger.warning("Rune creation automation is already running")
            return False
        
        self.logger.info("Starting rune creation automation")
        self.is_running = True
        self.creation_count = 0
        self.failure_count = 0
        
        try:
            # Start monitoring for rune items
            self._setup_item_monitoring()
            
            # Main automation loop
            while self.is_running:
                if self._check_for_rune_item():
                    if self._create_rune():
                        self.creation_count += 1
                        self.logger.info(f"Rune created successfully (total: {self.creation_count})")
                    else:
                        self.failure_count += 1
                        self.logger.warning(f"Rune creation failed (failures: {self.failure_count})")
                    
                    # Wait before next creation attempt
                    self.timing.adaptive_delay(2.0, variance=0.3)
                else:
                    # Wait before checking again
                    self.timing.adaptive_delay(1.0, variance=0.2)
                
                # Check for stop conditions
                if self.failure_count >= 5:
                    self.logger.error("Too many failures, stopping automation")
                    break
                    
        except Exception as e:
            self.logger.error(f"Rune creation automation failed: {e}")
            return False
        finally:
            self.is_running = False
        
        self.logger.info(f"Rune creation automation stopped. Created: {self.creation_count}, Failed: {self.failure_count}")
        return True
    
    def stop_automation(self):
        """Stop the automation"""
        self.logger.info("Stopping rune creation automation")
        self.is_running = False
    
    def _setup_item_monitoring(self):
        """Setup monitoring for rune items"""
        try:
            template_path = self.config.get('item_template_path')
            if not template_path:
                self.logger.error("Item template path not configured")
                return
            
            # Create template monitor
            condition_name = self.state_monitor.create_template_monitor(template_path)
            self.logger.info(f"Setup item monitoring with condition: {condition_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to setup item monitoring: {e}")
    
    def _check_for_rune_item(self) -> bool:
        """
        Check if rune item is present on screen
        
        Returns:
            True if rune item is found, False otherwise
        """
        if not self.timing.can_act('item_detection'):
            return False
        
        try:
            # Capture current screen
            screenshot = self.screen_capture.capture_screen()
            
            # Get template path
            template_path = self.config.get('item_template_path')
            if not template_path:
                self.logger.error("Template path not configured")
                return False
            
            # Find template using multi-scale matching for better detection
            location = self.computer_vision.find_template_multi_scale(screenshot, template_path)
            
            if location:
                self.logger.debug(f"Rune item found at: {location}")
                self.timing.record_action('item_detection')
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking for rune item: {e}")
            return False
    
    def _create_rune(self) -> bool:
        """
        Execute rune creation sequence
        
        Returns:
            True if rune creation was successful, False otherwise
        """
        if not self.timing.can_act('rune_creation'):
            return False
        
        try:
            self.logger.info("Starting rune creation sequence...")
            
            # Step 1: Find item location
            screenshot = self.screen_capture.capture_screen()
            template_path = self.config.get('item_template_path')
            location = self.computer_vision.find_template_multi_scale(screenshot, template_path)
            
            if not location:
                self.logger.warning("Could not find rune item for creation")
                return False
            
            # Step 2: Get item center coordinates
            item_x, item_y = location
            self.logger.debug(f"Item found at: ({item_x}, {item_y})")
            
            # Step 3: Get target position
            target_pos = self.config.get('target_position', [500, 300])
            target_x, target_y = target_pos
            self.logger.debug(f"Target position: ({target_x}, {target_y})")
            
            # Step 4: Perform drag and drop
            self.logger.debug("Performing drag and drop...")
            if not self.input_simulator.drag_and_drop(item_x, item_y, target_x, target_y, duration=1.0):
                self.logger.error("Drag and drop failed")
                return False
            
            # Step 5: Wait for drop to complete
            self.timing.adaptive_delay(0.5, variance=0.1)
            
            # Step 6: Press hotkey
            hotkey = self.config.get('hotkey', 'f1')
            self.logger.debug(f"Pressing hotkey: {hotkey}")
            if not self.input_simulator.press_key(hotkey):
                self.logger.error("Hotkey press failed")
                return False
            
            # Step 7: Wait for creation to complete
            self.timing.adaptive_delay(1.0, variance=0.2)
            
            # Step 8: Verify creation (optional)
            if self._verify_rune_creation():
                self.logger.debug("Rune creation verified")
            else:
                self.logger.warning("Could not verify rune creation")
            
            self.timing.record_action('rune_creation')
            return True
            
        except Exception as e:
            self.logger.error(f"Rune creation sequence failed: {e}")
            return False
    
    def _verify_rune_creation(self) -> bool:
        """
        Verify that rune creation was successful
        
        Returns:
            True if creation appears successful, False otherwise
        """
        try:
            # This is a simplified verification - in a real implementation,
            # you might check for specific visual indicators of successful creation
            
            # Wait a moment for any visual feedback
            self.timing.adaptive_delay(0.5)
            
            # For now, we'll assume success if we get this far
            # In a real implementation, you might:
            # - Check for success message text
            # - Look for visual indicators
            # - Monitor inventory changes
            # - Check for sound/audio cues
            
            return True
            
        except Exception as e:
            self.logger.error(f"Rune creation verification failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current automation status
        
        Returns:
            Dictionary containing status information
        """
        return {
            'is_running': self.is_running,
            'is_enabled': self.config.get('enabled', False),
            'creation_count': self.creation_count,
            'failure_count': self.failure_count,
            'success_rate': self.creation_count / max(1, self.creation_count + self.failure_count),
            'can_act': self.timing.can_act('rune_creation'),
            'remaining_cooldown': self.timing.get_remaining_cooldown('rune_creation')
        }
    
    def update_config(self, new_config: Dict[str, Any]):
        """
        Update automation configuration
        
        Args:
            new_config: New configuration values
        """
        try:
            # Update local config
            self.config.update(new_config)
            
            # Update global config
            for key, value in new_config.items():
                self.config_manager.set(f'automation.rune_creation.{key}', value)
            
            self.logger.info(f"Updated rune creation configuration: {new_config}")
            
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
    
    def reset_counters(self):
        """Reset creation and failure counters"""
        self.creation_count = 0
        self.failure_count = 0
        self.logger.info("Reset rune creation counters")

class RuneCreationError(Exception):
    """Custom exception for rune creation errors"""
    pass
