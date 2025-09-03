"""
Health monitoring automation for Cyclops automation system.
Implements health bar monitoring and emergency response automation.
"""

import logging
import time
from typing import Optional, Tuple, Dict, Any, List
from core.screen_capture import ScreenCapture
from core.input_simulator import InputSimulator
from core.state_monitor import StateMonitor
from utils.timing import TimingUtils
from utils.config_manager import ConfigManager

class HealthMonitorAutomation:
    """Health monitoring automation with emergency response"""
    
    def __init__(self, config_manager: ConfigManager, screen_capture: ScreenCapture, 
                 input_simulator: InputSimulator, state_monitor: StateMonitor):
        """
        Initialize health monitoring automation
        
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
        self.config = self.config_manager.get_automation_config('health_monitoring')
        self.is_running = False
        self.emergency_count = 0
        self.last_health_check = 0
        self.current_health_percentage = 1.0
        
        # Setup cooldowns
        self.timing.set_cooldown('health_check', 0.5)  # Check every 0.5 seconds
        self.timing.set_cooldown('emergency_response', 2.0)  # Emergency response cooldown
        
        # Health monitoring state
        self.health_condition_name = None
        self.is_low_health = False
        self.emergency_sequence = []
        
        self.logger.info("Health Monitor Automation initialized")
    
    def start_automation(self) -> bool:
        """
        Start the health monitoring automation
        
        Returns:
            True if started successfully, False otherwise
        """
        if not self.config.get('enabled', False):
            self.logger.warning("Health monitoring automation is disabled in configuration")
            return False
        
        if self.is_running:
            self.logger.warning("Health monitoring automation is already running")
            return False
        
        self.logger.info("Starting health monitoring automation")
        self.is_running = True
        self.emergency_count = 0
        
        try:
            # Setup health monitoring
            self._setup_health_monitoring()
            
            # Main monitoring loop
            while self.is_running:
                if self._check_health_status():
                    if self.is_low_health and self.timing.can_act('emergency_response'):
                        if self._execute_emergency_response():
                            self.emergency_count += 1
                            self.logger.warning(f"Emergency response executed (total: {self.emergency_count})")
                        else:
                            self.logger.error("Emergency response failed")
                
                # Wait before next check
                self.timing.adaptive_delay(0.5, variance=0.1)
                    
        except Exception as e:
            self.logger.error(f"Health monitoring automation failed: {e}")
            return False
        finally:
            self.is_running = False
        
        self.logger.info(f"Health monitoring automation stopped. Emergency responses: {self.emergency_count}")
        return True
    
    def stop_automation(self):
        """Stop the automation"""
        self.logger.info("Stopping health monitoring automation")
        self.is_running = False
    
    def _setup_health_monitoring(self):
        """Setup health bar monitoring"""
        try:
            # Get health bar region
            health_region = self.config.get('health_bar_region', [50, 50, 200, 20])
            low_health_threshold = self.config.get('low_health_threshold', 0.3)
            
            # Create health monitor
            self.health_condition_name = self.state_monitor.create_health_monitor(
                tuple(health_region), low_health_threshold
            )
            
            self.logger.info(f"Setup health monitoring with condition: {self.health_condition_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to setup health monitoring: {e}")
    
    def _check_health_status(self) -> bool:
        """
        Check current health status
        
        Returns:
            True if health check was successful, False otherwise
        """
        if not self.timing.can_act('health_check'):
            return False
        
        try:
            # Get health status from state monitor
            if self.health_condition_name:
                health_data = self.state_monitor.get_last_state(self.health_condition_name)
                
                if health_data:
                    self.current_health_percentage = health_data.get('percentage', 1.0)
                    self.is_low_health = health_data.get('is_low', False)
                    
                    self.logger.debug(f"Health: {self.current_health_percentage:.1%}, Low: {self.is_low_health}")
                    
                    self.timing.record_action('health_check')
                    self.last_health_check = time.time()
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Health status check failed: {e}")
            return False
    
    def _execute_emergency_response(self) -> bool:
        """
        Execute emergency response sequence
        
        Returns:
            True if emergency response was successful, False otherwise
        """
        try:
            self.logger.warning("Executing emergency response sequence...")
            
            # Get emergency configuration
            emergency_hotkey = self.config.get('emergency_hotkey', 'f2')
            emergency_sequence = self.config.get('emergency_sequence', [])
            
            # Execute emergency hotkey
            if emergency_hotkey:
                self.logger.debug(f"Pressing emergency hotkey: {emergency_hotkey}")
                if not self.input_simulator.press_key(emergency_hotkey):
                    self.logger.error("Emergency hotkey press failed")
                    return False
            
            # Execute emergency sequence if configured
            if emergency_sequence:
                self.logger.debug("Executing emergency sequence...")
                for action in emergency_sequence:
                    if not self._execute_emergency_action(action):
                        self.logger.warning(f"Emergency action failed: {action}")
                    self.timing.adaptive_delay(0.2, variance=0.1)
            
            # Record emergency response
            self.timing.record_action('emergency_response')
            
            self.logger.info("Emergency response sequence completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Emergency response sequence failed: {e}")
            return False
    
    def _execute_emergency_action(self, action: Dict[str, Any]) -> bool:
        """
        Execute a single emergency action
        
        Args:
            action: Action configuration dictionary
            
        Returns:
            True if action was successful, False otherwise
        """
        try:
            action_type = action.get('type', '')
            
            if action_type == 'key_press':
                key = action.get('key', '')
                if key:
                    return self.input_simulator.press_key(key)
            
            elif action_type == 'hotkey':
                keys = action.get('keys', [])
                if keys:
                    return self.input_simulator.press_hotkey(*keys)
            
            elif action_type == 'click':
                x = action.get('x', 0)
                y = action.get('y', 0)
                button = action.get('button', 'left')
                return self.input_simulator.click(x, y, button=button)
            
            elif action_type == 'move':
                x = action.get('x', 0)
                y = action.get('y', 0)
                return self.input_simulator.move_mouse(x, y)
            
            elif action_type == 'delay':
                delay = action.get('delay', 0.5)
                time.sleep(delay)
                return True
            
            else:
                self.logger.warning(f"Unknown emergency action type: {action_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Emergency action execution failed: {e}")
            return False
    
    def get_current_health(self) -> float:
        """
        Get current health percentage
        
        Returns:
            Health percentage (0.0 to 1.0)
        """
        return self.current_health_percentage
    
    def is_health_low(self) -> bool:
        """
        Check if health is currently low
        
        Returns:
            True if health is low, False otherwise
        """
        return self.is_low_health
    
    def set_health_region(self, x: int, y: int, width: int, height: int):
        """
        Set the health bar region
        
        Args:
            x: X coordinate of health bar
            y: Y coordinate of health bar
            width: Width of health bar
            height: Height of health bar
        """
        health_region = [x, y, width, height]
        self.config['health_bar_region'] = health_region
        self.config_manager.set('automation.health_monitoring.health_bar_region', health_region)
        self.logger.info(f"Updated health bar region to: {health_region}")
    
    def set_low_health_threshold(self, threshold: float):
        """
        Set the low health threshold
        
        Args:
            threshold: Low health threshold (0.0 to 1.0)
        """
        if not 0.0 <= threshold <= 1.0:
            self.logger.error(f"Invalid health threshold: {threshold}")
            return
        
        self.config['low_health_threshold'] = threshold
        self.config_manager.set('automation.health_monitoring.low_health_threshold', threshold)
        self.logger.info(f"Updated low health threshold to: {threshold:.1%}")
    
    def set_emergency_hotkey(self, hotkey: str):
        """
        Set the emergency hotkey
        
        Args:
            hotkey: Emergency hotkey (e.g., 'f2', 'ctrl+h')
        """
        self.config['emergency_hotkey'] = hotkey
        self.config_manager.set('automation.health_monitoring.emergency_hotkey', hotkey)
        self.logger.info(f"Updated emergency hotkey to: {hotkey}")
    
    def set_emergency_sequence(self, sequence: List[Dict[str, Any]]):
        """
        Set the emergency response sequence
        
        Args:
            sequence: List of emergency actions
        """
        self.config['emergency_sequence'] = sequence
        self.config_manager.set('automation.health_monitoring.emergency_sequence', sequence)
        self.logger.info(f"Updated emergency sequence with {len(sequence)} actions")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current automation status
        
        Returns:
            Dictionary containing status information
        """
        return {
            'is_running': self.is_running,
            'is_enabled': self.config.get('enabled', False),
            'emergency_count': self.emergency_count,
            'current_health': self.current_health_percentage,
            'is_low_health': self.is_low_health,
            'can_act': self.timing.can_act('emergency_response'),
            'remaining_cooldown': self.timing.get_remaining_cooldown('emergency_response'),
            'health_bar_region': self.config.get('health_bar_region', [0, 0, 0, 0]),
            'low_health_threshold': self.config.get('low_health_threshold', 0.3),
            'emergency_hotkey': self.config.get('emergency_hotkey', 'f2'),
            'last_health_check': self.last_health_check
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
                self.config_manager.set(f'automation.health_monitoring.{key}', value)
            
            self.logger.info(f"Updated health monitoring configuration: {new_config}")
            
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
    
    def reset_counters(self):
        """Reset emergency counter"""
        self.emergency_count = 0
        self.logger.info("Reset health monitoring counter")

class HealthMonitorError(Exception):
    """Custom exception for health monitoring errors"""
    pass
