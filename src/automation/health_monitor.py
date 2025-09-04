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
from utils.resource_loader import find_resource, get_image_path

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
        
        # Emergency stop callback
        self.emergency_stop_callback = None
        
        # Overlay management
        self.region_overlay = None
        self.show_overlay = True
        
        self.logger.info("Health Monitor Automation initialized")
    
    def set_emergency_stop_callback(self, callback):
        """Set callback to be called when emergency stop occurs"""
        self.emergency_stop_callback = callback
    
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
            
            # Start state monitoring
            self.state_monitor.start_monitoring()
            
            # Create region overlay if enabled
            if self.show_overlay:
                self._create_region_overlay()
            
            # Main monitoring loop
            self.logger.info("Starting health monitoring loop...")
            loop_count = 0
            while self.is_running:
                loop_count += 1
                
                # Check health status (emergency response is handled inside this method)
                health_check_result = self._check_health_status()
                
                if not health_check_result:
                    # Health check failed (could be emergency stop or other error)
                    if not self.is_running:
                        # Emergency stop was triggered
                        self.logger.info("Health monitoring stopped due to emergency response")
                        break
                    else:
                        # Only log this warning occasionally to avoid spam
                        if loop_count % 10 == 1:  # Log every 10th failure
                            self.logger.warning(f"Health status check returned False (loop #{loop_count})")
                
                # Wait before next check
                self.timing.adaptive_delay(0.5, variance=0.1)
                    
        except Exception as e:
            self.logger.error(f"Health monitoring automation failed: {e}")
            return False
        finally:
            self.is_running = False
            
            # Stop state monitoring
            self.state_monitor.stop_monitoring()
        
        self.logger.info(f"Health monitoring automation stopped. Emergency responses: {self.emergency_count}")
        return True
    
    def stop_automation(self):
        """Stop the automation"""
        self.logger.info("Stopping health monitoring automation")
        self.is_running = False
        
        # Destroy overlay
        if self.region_overlay:
            self.region_overlay.destroy()
            self.region_overlay = None
    
    def _setup_health_monitoring(self):
        """Setup health bar monitoring"""
        try:
            # Get health bar region
            health_region_dict = self.config.get('health_bar_region', {'x': 50, 'y': 50, 'width': 200, 'height': 20})
            low_health_threshold = self.config.get('low_health_threshold', 0.3)
            max_health = self.config.get('max_health', 1000)
            
            # Convert region dict to tuple
            health_region = (health_region_dict['x'], health_region_dict['y'], 
                           health_region_dict['width'], health_region_dict['height'])
            
            self.logger.info(f"Setting up health monitoring:")
            self.logger.info(f"  Region: {health_region}")
            self.logger.info(f"  Low health threshold: {low_health_threshold:.1%}")
            self.logger.info(f"  Max health: {max_health}")
            
            # Create image search-based health monitor using resource path resolver
            health_image_path = self.config_manager.get('automation.health_monitoring.health_bar_image', 'health_reference.png')
            resolved_health_path = find_resource(health_image_path) or get_image_path(health_image_path)
            self.health_condition_name = self.state_monitor.create_image_search_monitor(
                health_region, resolved_health_path, 0.8
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
        # Health checks should run continuously without timing restrictions
        # (The main loop already has a 0.5 second delay)
        
        try:
            # Record that we're performing a health check
            self.timing.record_action('health_check')
            # Get health status from state monitor
            if self.health_condition_name:
                health_data = self.state_monitor.get_last_state(self.health_condition_name)
                
                if health_data:
                    # Handle image search data structure
                    if 'image_found' in health_data:
                        # Image search format
                        image_found = health_data.get('image_found', False)
                        confidence = health_data.get('confidence', 0.0)
                        self.current_health_percentage = 1.0 if image_found else 0.0
                        self.is_low_health = not image_found  # Low health when image is not found
                        
                        # Only log health status once when we first get data
                        if not hasattr(self, '_health_logged'):
                            if image_found:
                                self.logger.info(f"Health monitoring active - Image found! Confidence: {confidence:.3f}")
                            else:
                                self.logger.info(f"Health monitoring active - Image not found! Confidence: {confidence:.3f}")
                            self._health_logged = True
                        
                        # Log when health image is not found and execute emergency response
                        if self.is_low_health and not hasattr(self, '_emergency_detected_logged'):
                            self.logger.warning("HEALTH IMAGE NOT FOUND! Emergency detected !!")
                            self._emergency_detected_logged = True
                            
                            # Execute emergency response and stop automation
                            if self._execute_emergency_response():
                                self.logger.warning("Emergency response executed. Stopping automation.")
                                self.is_running = False  # Stop the health monitoring loop
                                
                                # Notify main window to stop all automations
                                if self.emergency_stop_callback:
                                    self.emergency_stop_callback()
                                
                                return False  # Exit the monitoring loop
                    else:
                        # Old single health format
                        self.current_health_percentage = health_data.get('percentage', 1.0)
                        self.is_low_health = health_data.get('is_low', False)
                        
                        # Only log health status once when we first get data
                        if not hasattr(self, '_health_logged'):
                            self.logger.info(f"Health monitoring active - Current: {self.current_health_percentage:.1%}, Low: {self.is_low_health}")
                            self._health_logged = True
                    
                    # Update overlay status
                    if self.region_overlay:
                        self.region_overlay.update_status(not self.is_low_health)
                    
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
            
            # Get emergency clicks from config
            emergency_clicks = self.config.get('emergency_clicks', [])
            
            if emergency_clicks:
                self.logger.info(f"Executing {len(emergency_clicks)} emergency clicks")
                
                # Execute each emergency click
                for i, (x, y) in enumerate(emergency_clicks):
                    self.logger.debug(f"Emergency click {i+1} at ({x}, {y})")
                    
                    # Perform the click
                    if not self.input_simulator.click(x, y):
                        self.logger.error(f"Emergency click {i+1} failed at ({x}, {y})")
                        return False
                    
                    # Small delay between clicks
                    if i < len(emergency_clicks) - 1:  # Don't delay after last click
                        self.timing.adaptive_delay(0.1, variance=0.05)
                
                self.logger.info("Emergency clicks executed successfully")
            else:
                # Fallback to old emergency hotkey system
                emergency_hotkey = self.config.get('emergency_hotkey', 'f2')
                if emergency_hotkey:
                    self.logger.debug(f"Pressing emergency hotkey: {emergency_hotkey}")
                    if not self.input_simulator.press_key(emergency_hotkey):
                        self.logger.error("Emergency hotkey press failed")
                        return False
                else:
                    self.logger.warning("No emergency actions configured")
            
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
    
    def _create_region_overlay(self):
        """Create region overlay for visual feedback"""
        try:
            # Get health bar region
            health_region = self.config.get('health_bar_region', [50, 50, 200, 20])
            
            # Import here to avoid circular imports
            from gui.region_selector import RegionOverlay
            
            # Create overlay
            self.region_overlay = RegionOverlay(
                health_region['x'], health_region['y'],
                health_region['width'], health_region['height'],
                is_active=True  # Start as active (green)
            )
            
            self.logger.info("Region overlay created")
            
        except Exception as e:
            self.logger.error(f"Failed to create region overlay: {e}")
            self.region_overlay = None
    
    def toggle_overlay(self, show: bool):
        """Toggle overlay visibility"""
        self.show_overlay = show
        
        if show and not self.region_overlay and self.is_running:
            self._create_region_overlay()
        elif not show and self.region_overlay:
            self.region_overlay.destroy()
            self.region_overlay = None
        
        self.logger.info(f"Overlay visibility: {show}")

class HealthMonitorError(Exception):
    """Custom exception for health monitoring errors"""
    pass
