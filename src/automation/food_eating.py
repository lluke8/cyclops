"""
Food eating automation for Cyclops automation system.
Implements automated food consumption with multiple positions and human-like behavior.
"""

import logging
import time
import random
from typing import Optional, Tuple, Dict, Any, List
from core.screen_capture import ScreenCapture
from core.input_simulator import InputSimulator
from core.state_monitor import StateMonitor
from utils.timing import TimingUtils
from utils.config_manager import ConfigManager

class FoodEatingAutomation:
    """Food eating automation with multiple positions and human-like behavior"""
    
    def __init__(self, config_manager: ConfigManager, screen_capture: ScreenCapture, 
                 input_simulator: InputSimulator, state_monitor: StateMonitor):
        """
        Initialize food eating automation
        
        Args:
            config_manager: Configuration manager instance
            screen_capture: Screen capture instance
            input_simulator: Input simulator instance
            state_monitor: State monitor instance
        """
        self.config_manager = config_manager
        self.screen_capture = screen_capture
        self.input_simulator = input_simulator
        self.state_monitor = state_monitor
        self.timing = TimingUtils()
        self.logger = logging.getLogger(__name__)
        
        # Get automation configuration
        self.config = self.config_manager.get_automation_config('food_eating')
        self.is_running = False
        self.eating_count = 0
        self.last_eat_time = 0
        self.next_eat_time = 0
        
        # Food positions (up to 3 positions)
        self.food_positions = self.config.get('food_positions', [])
        
        # Configuration for human-like behavior
        self.min_clicks = self.config.get('min_clicks', 3)
        self.max_clicks = self.config.get('max_clicks', 6)
        self.min_delay_minutes = self.config.get('min_delay_minutes', 4)
        self.max_delay_minutes = self.config.get('max_delay_minutes', 8)
        
        # Setup cooldowns (for manual triggers)
        cooldown_seconds = self.config.get('cooldown_seconds', 5)
        self.timing.set_cooldown('food_eating', cooldown_seconds)
        
        self.logger.info("Food Eating Automation initialized")
        self.logger.info(f"Food positions: {len(self.food_positions)} configured")
        self.logger.info(f"Click range: {self.min_clicks}-{self.max_clicks}")
        self.logger.info(f"Delay range: {self.min_delay_minutes}-{self.max_delay_minutes} minutes")
    
    def start_automation(self) -> bool:
        """
        Start the food eating automation
        
        Returns:
            True if started successfully, False otherwise
        """
        if not self.config.get('enabled', False):
            self.logger.warning("Food eating automation is disabled in configuration")
            return False
        
        if self.is_running:
            self.logger.warning("Food eating automation is already running")
            return False
        
        if len(self.food_positions) == 0:
            self.logger.error("No food positions configured. Please set up food positions first.")
            return False
        
        self.logger.info("Starting food eating automation")
        self.is_running = True
        self.eating_count = 0
        
        # Set initial next eat time
        self._schedule_next_eat()
        
        try:
            # Main automation loop
            while self.is_running:
                current_time = time.time()
                
                # Check if it's time to eat
                if current_time >= self.next_eat_time:
                    if self._eat_food_sequence():
                        self.eating_count += 1
                        self.logger.info(f"Food eating sequence completed (total: {self.eating_count})")
                        self._schedule_next_eat()
                    else:
                        self.logger.warning("Food eating sequence failed")
                        # Schedule retry in 1 minute
                        self.next_eat_time = current_time + 60
                
                # Wait before next check (check every 10 seconds)
                self.timing.adaptive_delay(10.0, variance=2.0)
                    
        except Exception as e:
            self.logger.error(f"Food eating automation failed: {e}")
            return False
        finally:
            self.is_running = False
        
        self.logger.info(f"Food eating automation stopped. Total eaten: {self.eating_count}")
        return True
    
    def stop_automation(self):
        """Stop the automation"""
        self.logger.info("Stopping food eating automation")
        self.is_running = False
    
    def _schedule_next_eat(self):
        """Schedule the next food eating time with random delay"""
        # Random delay between min and max minutes
        delay_minutes = random.uniform(self.min_delay_minutes, self.max_delay_minutes)
        delay_seconds = delay_minutes * 60
        
        self.next_eat_time = time.time() + delay_seconds
        
        # Log next scheduled time
        next_time_str = time.strftime("%H:%M:%S", time.localtime(self.next_eat_time))
        self.logger.info(f"Next food eating scheduled in {delay_minutes:.1f} minutes at {next_time_str}")
    
    def _eat_food_sequence(self) -> bool:
        """
        Execute a complete food eating sequence with human-like behavior
        
        Returns:
            True if sequence was successful, False otherwise
        """
        try:
            # Randomly select a food position
            if not self.food_positions:
                self.logger.error("No food positions available")
                return False
            
            selected_position = random.choice(self.food_positions)
            food_x, food_y = selected_position
            
            # Randomly determine number of clicks
            click_count = random.randint(self.min_clicks, self.max_clicks)
            
            self.logger.info(f"Starting food eating sequence at position ({food_x}, {food_y}) with {click_count} clicks")
            
            # Move mouse to food position once, then click multiple times
            self.logger.debug(f"Moving mouse to food position ({food_x}, {food_y})")
            if not self.input_simulator.move_mouse(food_x, food_y):
                self.logger.error("Failed to move mouse to food position")
                return False
            
            # Perform the clicking sequence at the same position
            for i in range(click_count):
                # Only check is_running if we're in an active automation loop
                # Allow manual testing even when automation is not running
                # (Remove the is_running check for manual testing)
                
                # Right-click at current mouse position (no movement)
                if not self.input_simulator.right_click():
                    self.logger.error(f"Right-click {i+1} failed")
                    return False
                
                self.logger.debug(f"Right-click {i+1}/{click_count} at ({food_x}, {food_y})")
                
                # Small delay between clicks (0.1 to 0.3 seconds for fast clicking)
                if i < click_count - 1:  # Don't delay after the last click
                    click_delay = random.uniform(0.1, 0.3)
                    time.sleep(click_delay)
            
            # Record the action
            self.last_eat_time = time.time()
            
            self.logger.info(f"Food eating sequence completed: {click_count} clicks at position ({food_x}, {food_y})")
            return True
            
        except Exception as e:
            self.logger.error(f"Food eating sequence failed: {e}")
            return False
    
    def eat_food_once(self) -> bool:
        """
        Eat food once (manual trigger)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.timing.can_act('food_eating'):
            remaining = self.timing.get_remaining_cooldown('food_eating')
            self.logger.warning(f"Food eating in cooldown, {remaining:.1f}s remaining")
            return False
        
        return self._eat_food_sequence()
    
    def add_food_position(self, x: int, y: int) -> bool:
        """
        Add a food position
        
        Args:
            x: X coordinate of food position
            y: Y coordinate of food position
            
        Returns:
            True if position was added, False if maximum positions reached
        """
        if len(self.food_positions) >= 3:
            self.logger.warning("Maximum of 3 food positions allowed")
            return False
        
        position = [x, y]
        if position not in self.food_positions:
            self.food_positions.append(position)
            self._save_food_positions()
            self.logger.info(f"Added food position: ({x}, {y}) - Total positions: {len(self.food_positions)}")
            return True
        else:
            self.logger.warning(f"Food position ({x}, {y}) already exists")
            return False
    
    def remove_food_position(self, x: int, y: int) -> bool:
        """
        Remove a food position
        
        Args:
            x: X coordinate of food position
            y: Y coordinate of food position
            
        Returns:
            True if position was removed, False if position not found
        """
        position = [x, y]
        if position in self.food_positions:
            self.food_positions.remove(position)
            self._save_food_positions()
            self.logger.info(f"Removed food position: ({x}, {y}) - Total positions: {len(self.food_positions)}")
            return True
        else:
            self.logger.warning(f"Food position ({x}, {y}) not found")
            return False
    
    def clear_food_positions(self):
        """Clear all food positions"""
        self.food_positions.clear()
        self._save_food_positions()
        self.logger.info("Cleared all food positions")
    
    def _save_food_positions(self):
        """Save food positions to configuration"""
        self.config['food_positions'] = self.food_positions
        self.config_manager.set('automation.food_eating.food_positions', self.food_positions)
    
    def set_click_range(self, min_clicks: int, max_clicks: int):
        """
        Set the click count range
        
        Args:
            min_clicks: Minimum number of clicks
            max_clicks: Maximum number of clicks
        """
        if min_clicks > max_clicks:
            min_clicks, max_clicks = max_clicks, min_clicks
        
        self.min_clicks = min_clicks
        self.max_clicks = max_clicks
        self.config['min_clicks'] = min_clicks
        self.config['max_clicks'] = max_clicks
        self.config_manager.set('automation.food_eating.min_clicks', min_clicks)
        self.config_manager.set('automation.food_eating.max_clicks', max_clicks)
        self.logger.info(f"Updated click range to: {min_clicks}-{max_clicks}")
    
    def set_delay_range(self, min_minutes: float, max_minutes: float):
        """
        Set the delay range between food eating sessions
        
        Args:
            min_minutes: Minimum delay in minutes
            max_minutes: Maximum delay in minutes
        """
        if min_minutes > max_minutes:
            min_minutes, max_minutes = max_minutes, min_minutes
        
        self.min_delay_minutes = min_minutes
        self.max_delay_minutes = max_minutes
        self.config['min_delay_minutes'] = min_minutes
        self.config['max_delay_minutes'] = max_minutes
        self.config_manager.set('automation.food_eating.min_delay_minutes', min_minutes)
        self.config_manager.set('automation.food_eating.max_delay_minutes', max_minutes)
        self.logger.info(f"Updated delay range to: {min_minutes}-{max_minutes} minutes")
    
    def set_cooldown(self, cooldown_seconds: float):
        """
        Set the cooldown for manual food eating
        
        Args:
            cooldown_seconds: Cooldown duration in seconds
        """
        self.timing.set_cooldown('food_eating', cooldown_seconds)
        self.config['cooldown_seconds'] = cooldown_seconds
        self.config_manager.set('automation.food_eating.cooldown_seconds', cooldown_seconds)
        self.logger.info(f"Updated food eating cooldown to: {cooldown_seconds}s")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current automation status
        
        Returns:
            Dictionary containing status information
        """
        next_eat_str = "Not scheduled"
        if self.next_eat_time > 0:
            next_eat_str = time.strftime("%H:%M:%S", time.localtime(self.next_eat_time))
        
        return {
            'is_running': self.is_running,
            'is_enabled': self.config.get('enabled', False),
            'eating_count': self.eating_count,
            'can_act': self.timing.can_act('food_eating'),
            'remaining_cooldown': self.timing.get_remaining_cooldown('food_eating'),
            'food_positions': self.food_positions,
            'food_position_count': len(self.food_positions),
            'click_range': f"{self.min_clicks}-{self.max_clicks}",
            'delay_range_minutes': f"{self.min_delay_minutes}-{self.max_delay_minutes}",
            'cooldown_seconds': self.config.get('cooldown_seconds', 5),
            'last_eat_time': self.last_eat_time,
            'next_eat_time': next_eat_str
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
                self.config_manager.set(f'automation.food_eating.{key}', value)
            
            # Update specific settings if changed
            if 'cooldown_seconds' in new_config:
                self.set_cooldown(new_config['cooldown_seconds'])
            
            if 'min_clicks' in new_config and 'max_clicks' in new_config:
                self.set_click_range(new_config['min_clicks'], new_config['max_clicks'])
            
            if 'min_delay_minutes' in new_config and 'max_delay_minutes' in new_config:
                self.set_delay_range(new_config['min_delay_minutes'], new_config['max_delay_minutes'])
            
            if 'food_positions' in new_config:
                self.food_positions = new_config['food_positions']
                self._save_food_positions()
            
            self.logger.info(f"Updated food eating configuration: {new_config}")
            
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
    
    def get_food_positions(self) -> List[List[int]]:
        """
        Get all configured food positions
        
        Returns:
            List of food positions as [x, y] coordinates
        """
        return self.food_positions.copy()
    
    def reset_counters(self):
        """Reset eating counter"""
        self.eating_count = 0
        self.logger.info("Reset food eating counter")

class FoodEatingError(Exception):
    """Custom exception for food eating errors"""
    pass
