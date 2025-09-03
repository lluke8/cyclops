"""
Food eating automation for Cyclops automation system.
Implements automated food consumption with cooldown management.
"""

import logging
import time
from typing import Optional, Tuple, Dict, Any
from core.screen_capture import ScreenCapture
from core.input_simulator import InputSimulator
from core.state_monitor import StateMonitor
from utils.timing import TimingUtils
from utils.config_manager import ConfigManager

class FoodEatingAutomation:
    """Food eating automation with cooldown management"""
    
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
        
        # Setup cooldowns
        cooldown_seconds = self.config.get('cooldown_seconds', 5)
        self.timing.set_cooldown('food_eating', cooldown_seconds)
        
        self.logger.info("Food Eating Automation initialized")
    
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
        
        self.logger.info("Starting food eating automation")
        self.is_running = True
        self.eating_count = 0
        
        try:
            # Main automation loop
            while self.is_running:
                if self._should_eat_food():
                    if self._eat_food():
                        self.eating_count += 1
                        self.logger.info(f"Food eaten successfully (total: {self.eating_count})")
                    else:
                        self.logger.warning("Food eating failed")
                
                # Wait before next check
                self.timing.adaptive_delay(1.0, variance=0.2)
                    
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
        
        return self._eat_food()
    
    def _should_eat_food(self) -> bool:
        """
        Determine if food should be eaten
        
        Returns:
            True if food should be eaten, False otherwise
        """
        # Check cooldown
        if not self.timing.can_act('food_eating'):
            return False
        
        # Check if automation is enabled
        if not self.config.get('enabled', False):
            return False
        
        # For now, we'll eat food based on cooldown only
        # In a real implementation, you might check:
        # - Health percentage
        # - Hunger indicators
        # - Buff/debuff status
        # - User-defined triggers
        
        return True
    
    def _eat_food(self) -> bool:
        """
        Execute food eating sequence
        
        Returns:
            True if food eating was successful, False otherwise
        """
        try:
            self.logger.debug("Starting food eating sequence...")
            
            # Get food position
            food_pos = self.config.get('food_position', [100, 100])
            food_x, food_y = food_pos
            
            self.logger.debug(f"Eating food at position: ({food_x}, {food_y})")
            
            # Perform right-click on food
            if not self.input_simulator.right_click(food_x, food_y):
                self.logger.error("Right-click on food failed")
                return False
            
            # Wait for eating animation/effect
            self.timing.adaptive_delay(1.0, variance=0.2)
            
            # Record the action
            self.timing.record_action('food_eating')
            self.last_eat_time = time.time()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Food eating sequence failed: {e}")
            return False
    
    def set_food_position(self, x: int, y: int):
        """
        Set the food position
        
        Args:
            x: X coordinate of food
            y: Y coordinate of food
        """
        self.config['food_position'] = [x, y]
        self.config_manager.set('automation.food_eating.food_position', [x, y])
        self.logger.info(f"Updated food position to: ({x}, {y})")
    
    def set_cooldown(self, cooldown_seconds: float):
        """
        Set the cooldown for food eating
        
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
        return {
            'is_running': self.is_running,
            'is_enabled': self.config.get('enabled', False),
            'eating_count': self.eating_count,
            'can_act': self.timing.can_act('food_eating'),
            'remaining_cooldown': self.timing.get_remaining_cooldown('food_eating'),
            'food_position': self.config.get('food_position', [0, 0]),
            'cooldown_seconds': self.config.get('cooldown_seconds', 5),
            'last_eat_time': self.last_eat_time
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
            
            # Update cooldown if changed
            if 'cooldown_seconds' in new_config:
                self.set_cooldown(new_config['cooldown_seconds'])
            
            self.logger.info(f"Updated food eating configuration: {new_config}")
            
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
    
    def reset_counters(self):
        """Reset eating counter"""
        self.eating_count = 0
        self.logger.info("Reset food eating counter")

class FoodEatingError(Exception):
    """Custom exception for food eating errors"""
    pass
