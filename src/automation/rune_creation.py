"""
Rune creation automation for Cyclops automation system.
Implements automated rune creation workflow with image recognition and drag-and-drop.
"""

import logging
import time
import random
import os
from typing import Optional, Tuple, Dict, Any, List
from core.screen_capture import ScreenCapture
from core.computer_vision import ComputerVision
from core.input_simulator import InputSimulator
from core.state_monitor import StateMonitor
from utils.timing import TimingUtils
from utils.config_manager import ConfigManager

class RuneCreationAutomation:
    """Rune creation automation with image recognition and position management"""
    
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
        
        # Rune position management
        self.rune_positions = []  # List of (x, y) tuples for target positions
        self.min_delay_minutes = self.config.get('min_delay_minutes', 2.0)
        self.max_delay_minutes = self.config.get('max_delay_minutes', 5.0)
        self.next_create_time = 0  # Timestamp for next rune creation
        
        # Blank rune image path
        self.blank_rune_path = os.path.join(os.path.dirname(__file__), '..', '..', 'blank.png')
        
        # Setup cooldowns
        self.timing.set_cooldown('rune_creation', 2.0)
        self.timing.set_cooldown('image_detection', 1.0)
        
        self.logger.info("Rune Creation Automation initialized")
        self.logger.info(f"Rune positions: {len(self.rune_positions)} configured")
        self.logger.info(f"Delay range: {self.min_delay_minutes}-{self.max_delay_minutes} minutes")
        self.logger.info(f"Blank rune image: {self.blank_rune_path}")
    
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
        
        if not self.rune_positions:
            self.logger.warning("No rune target positions configured")
            return False
        
        self.logger.info("Starting rune creation automation")
        self.is_running = True
        self.creation_count = 0
        self.failure_count = 0
        
        # Schedule first rune creation
        self._schedule_next_create()
        
        try:
            # Main automation loop
            while self.is_running:
                current_time = time.time()
                
                # Check if it's time to create a rune
                if current_time >= self.next_create_time:
                    if self._create_rune_sequence():
                        self.creation_count += 1
                        self.logger.info(f"Rune created successfully (total: {self.creation_count})")
                        # Schedule next rune creation
                        self._schedule_next_create()
                    else:
                        self.failure_count += 1
                        self.logger.warning(f"Rune creation failed (failures: {self.failure_count})")
                        # Schedule retry with shorter delay
                        self._schedule_next_create(retry=True)
                
                # Check for stop conditions
                if self.failure_count >= 5:
                    self.logger.error("Too many failures, stopping automation")
                    break
                
                # Sleep for a short time to avoid busy waiting
                time.sleep(1.0)
                    
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
    
    def _schedule_next_create(self, retry: bool = False):
        """Schedule the next rune creation time"""
        try:
            current_time = time.time()
            
            if retry:
                # Shorter delay for retries (30 seconds to 2 minutes)
                delay_minutes = random.uniform(0.5, 2.0)
            else:
                # Normal delay range
                delay_minutes = random.uniform(self.min_delay_minutes, self.max_delay_minutes)
            
            self.next_create_time = current_time + (delay_minutes * 60)
            
            self.logger.info(f"Next rune creation scheduled in {delay_minutes:.1f} minutes")
            
        except Exception as e:
            self.logger.error(f"Failed to schedule next rune creation: {e}")
    
    def _find_blank_rune(self) -> Optional[Tuple[int, int]]:
        """
        Find the blank rune in the configured search region using image recognition
        
        Returns:
            (x, y) coordinates of the blank rune center, or None if not found
        """
        if not self.timing.can_act('image_detection'):
            return None
        
        try:
            # Check if blank rune image exists
            if not os.path.exists(self.blank_rune_path):
                self.logger.error(f"Blank rune image not found at: {self.blank_rune_path}")
                return None
            
            # Get search region from configuration
            search_region_dict = self.config_manager.get('automation.rune_creation.search_region', {})
            if not search_region_dict or not all(key in search_region_dict for key in ['x', 'y', 'width', 'height']):
                self.logger.error("No search region configured for blank rune detection")
                return None
            
            # Extract region coordinates
            x, y, width, height = search_region_dict['x'], search_region_dict['y'], search_region_dict['width'], search_region_dict['height']
            self.logger.debug(f"Searching for blank rune in region: ({x}, {y}) - {width}x{height}")
            
            # Capture the specific region
            screenshot = self.screen_capture.capture_region(x, y, width, height)
            
            # Find blank rune using template matching in the region
            location = self.computer_vision.find_template_multi_scale(screenshot, self.blank_rune_path)
            
            if location:
                # Convert relative coordinates to absolute screen coordinates
                absolute_x = x + location[0]
                absolute_y = y + location[1]
                self.logger.info(f"Blank rune found at relative position {location}, absolute: ({absolute_x}, {absolute_y})")
                self.logger.info(f"Search region: ({x}, {y}) - {width}x{height}")
                self.timing.record_action('image_detection')
                return (absolute_x, absolute_y)
            
            self.logger.debug("Blank rune not found in search region")
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding blank rune: {e}")
            return None
    
    def _create_rune_sequence(self) -> bool:
        """
        Execute the complete rune creation sequence
        
        Returns:
            True if rune creation was successful, False otherwise
        """
        try:
            self.logger.info("Starting rune creation sequence...")
            
            # Step 1: Find blank rune on screen
            blank_rune_location = self._find_blank_rune()
            if not blank_rune_location:
                self.logger.warning("Could not find blank rune on screen")
                return False
            
            blank_x, blank_y = blank_rune_location
            self.logger.info(f"Found blank rune at ({blank_x}, {blank_y})")
            
            # Step 2: Select random target position
            if not self.rune_positions:
                self.logger.error("No rune target positions configured")
                return False
            
            target_x, target_y = random.choice(self.rune_positions)
            self.logger.info(f"Selected target position: ({target_x}, {target_y})")
            
            # Step 3: Perform drag and drop
            self.logger.info(f"Performing drag and drop from ({blank_x}, {blank_y}) to ({target_x}, {target_y})...")
            if not self.input_simulator.drag_and_drop(blank_x, blank_y, target_x, target_y, duration=1.0):
                self.logger.error("Drag and drop failed")
                return False
            
            # Step 4: Wait for drop to complete
            time.sleep(0.5)
            
            # Step 5: Press configurable hotkey
            hotkey = self.config.get('hotkey', 'f6')
            self.logger.info(f"Pressing hotkey: {hotkey}")
            if not self.input_simulator.press_key(hotkey):
                self.logger.error("Hotkey press failed")
                return False
            
            # Step 6: Wait for creation to complete
            time.sleep(1.0)
            
            self.logger.info("Rune creation sequence completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Rune creation sequence failed: {e}")
            return False
    
    def add_rune_position(self, x: int, y: int) -> bool:
        """
        Add a rune target position
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if position was added, False if maximum positions reached
        """
        if len(self.rune_positions) >= 3:
            self.logger.warning("Maximum of 3 rune positions allowed")
            return False
        
        self.rune_positions.append((x, y))
        self.logger.info(f"Added rune position: ({x}, {y})")
        self._save_rune_positions()
        return True
    
    def remove_rune_position(self, x: int, y: int) -> bool:
        """
        Remove a specific rune position
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if position was removed, False if not found
        """
        try:
            self.rune_positions.remove((x, y))
            self.logger.info(f"Removed rune position: ({x}, {y})")
            self._save_rune_positions()
            return True
        except ValueError:
            self.logger.warning(f"Rune position not found: ({x}, {y})")
            return False
    
    def clear_rune_positions(self):
        """Clear all rune positions"""
        self.rune_positions.clear()
        self.logger.info("Cleared all rune positions")
        self._save_rune_positions()
    
    def get_rune_positions(self) -> List[Tuple[int, int]]:
        """
        Get a copy of the current rune positions
        
        Returns:
            List of (x, y) tuples
        """
        return self.rune_positions.copy()
    
    def _save_rune_positions(self):
        """Save rune positions to configuration"""
        try:
            self.config_manager.set('automation.rune_creation.rune_positions', self.rune_positions)
            self.logger.debug(f"Saved {len(self.rune_positions)} rune positions to configuration")
        except Exception as e:
            self.logger.error(f"Failed to save rune positions: {e}")
    
    def set_delay_range(self, min_minutes: float, max_minutes: float):
        """
        Set the delay range for rune creation
        
        Args:
            min_minutes: Minimum delay in minutes
            max_minutes: Maximum delay in minutes
        """
        self.min_delay_minutes = min_minutes
        self.max_delay_minutes = max_minutes
        self.logger.info(f"Set rune creation delay range: {min_minutes}-{max_minutes} minutes")
    
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
            'rune_positions': self.rune_positions,
            'rune_position_count': len(self.rune_positions),
            'delay_range_minutes': f"{self.min_delay_minutes}-{self.max_delay_minutes}",
            'next_create_time': self.next_create_time,
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
            
            # Update delay range if provided
            if 'min_delay_minutes' in new_config:
                self.min_delay_minutes = new_config['min_delay_minutes']
            if 'max_delay_minutes' in new_config:
                self.max_delay_minutes = new_config['max_delay_minutes']
            
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
