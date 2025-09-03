"""
State monitoring functionality for Cyclops automation system.
Handles continuous monitoring of screen states and conditions.
"""

import logging
import time
import threading
from typing import Dict, List, Callable, Optional, Any, Tuple
import cv2
import numpy as np
from .screen_capture import ScreenCapture
from .ocr_engine import OCREngine
from .computer_vision import ComputerVision

class StateMonitor:
    """State monitoring with continuous screen analysis and condition checking"""
    
    def __init__(self, config: dict, screen_capture: ScreenCapture, 
                 ocr_engine: OCREngine, computer_vision: ComputerVision):
        """
        Initialize state monitor with dependencies
        
        Args:
            config: Configuration dictionary
            screen_capture: Screen capture instance
            ocr_engine: OCR engine instance
            computer_vision: Computer vision instance
        """
        self.config = config
        self.screen_capture = screen_capture
        self.ocr_engine = ocr_engine
        self.computer_vision = computer_vision
        self.logger = logging.getLogger(__name__)
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread = None
        self.monitoring_interval = 0.5  # seconds
        
        # Condition callbacks
        self.condition_callbacks: Dict[str, List[Callable]] = {}
        self.last_states: Dict[str, Any] = {}
        
        # State history for change detection
        self.state_history: Dict[str, List[Any]] = {}
        self.max_history_size = 10
        
        self.logger.info("State Monitor initialized")
    
    def start_monitoring(self):
        """Start continuous state monitoring"""
        if self.is_monitoring:
            self.logger.warning("State monitoring is already running")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("State monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous state monitoring"""
        if not self.is_monitoring:
            self.logger.warning("State monitoring is not running")
            return
        
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        
        self.logger.info("State monitoring stopped")
    
    def register_condition(self, condition_name: str, callback: Callable, 
                          check_interval: float = 1.0):
        """
        Register a condition to monitor
        
        Args:
            condition_name: Unique name for the condition
            callback: Function to call when condition is checked
            check_interval: How often to check this condition (seconds)
        """
        if condition_name not in self.condition_callbacks:
            self.condition_callbacks[condition_name] = []
        
        self.condition_callbacks[condition_name].append({
            'callback': callback,
            'interval': check_interval,
            'last_check': 0
        })
        
        self.logger.info(f"Registered condition: {condition_name}")
    
    def unregister_condition(self, condition_name: str):
        """
        Unregister a condition
        
        Args:
            condition_name: Name of condition to unregister
        """
        if condition_name in self.condition_callbacks:
            del self.condition_callbacks[condition_name]
            self.logger.info(f"Unregistered condition: {condition_name}")
    
    def check_condition_once(self, condition_name: str) -> Any:
        """
        Check a specific condition once
        
        Args:
            condition_name: Name of condition to check
            
        Returns:
            Result of condition check
        """
        if condition_name not in self.condition_callbacks:
            self.logger.warning(f"Condition '{condition_name}' not registered")
            return None
        
        callbacks = self.condition_callbacks[condition_name]
        if not callbacks:
            return None
        
        # Use the first callback
        callback_info = callbacks[0]
        try:
            result = callback_info['callback']()
            self.last_states[condition_name] = result
            return result
        except Exception as e:
            self.logger.error(f"Condition check failed for '{condition_name}': {e}")
            return None
    
    def get_last_state(self, condition_name: str) -> Any:
        """
        Get the last known state of a condition
        
        Args:
            condition_name: Name of condition
            
        Returns:
            Last state value or None
        """
        return self.last_states.get(condition_name)
    
    def is_state_changed(self, condition_name: str) -> bool:
        """
        Check if a condition's state has changed
        
        Args:
            condition_name: Name of condition
            
        Returns:
            True if state has changed, False otherwise
        """
        if condition_name not in self.state_history:
            return False
        
        history = self.state_history[condition_name]
        if len(history) < 2:
            return False
        
        return history[-1] != history[-2]
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                current_time = time.time()
                
                # Check all registered conditions
                for condition_name, callbacks in self.condition_callbacks.items():
                    for callback_info in callbacks:
                        # Check if it's time to evaluate this condition
                        if current_time - callback_info['last_check'] >= callback_info['interval']:
                            try:
                                result = callback_info['callback']()
                                
                                # Update state history
                                if condition_name not in self.state_history:
                                    self.state_history[condition_name] = []
                                
                                self.state_history[condition_name].append(result)
                                
                                # Limit history size
                                if len(self.state_history[condition_name]) > self.max_history_size:
                                    self.state_history[condition_name].pop(0)
                                
                                # Update last state
                                self.last_states[condition_name] = result
                                
                                # Update last check time
                                callback_info['last_check'] = current_time
                                
                            except Exception as e:
                                self.logger.error(f"Error in condition '{condition_name}': {e}")
                
                # Sleep before next iteration
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1.0)  # Wait before retrying
    
    def create_health_monitor(self, health_region: Tuple[int, int, int, int], 
                            low_health_threshold: float = 0.3) -> str:
        """
        Create a health monitoring condition
        
        Args:
            health_region: (x, y, width, height) region of health bar
            low_health_threshold: Threshold for low health (0.0 to 1.0)
            
        Returns:
            Condition name for the health monitor
        """
        condition_name = "health_monitor"
        
        def health_check():
            try:
                # Capture health bar region
                health_image = self.screen_capture.capture_region(*health_region)
                
                # Analyze health bar (simplified - assumes red/green color detection)
                health_percentage = self._analyze_health_bar(health_image)
                
                return {
                    'percentage': health_percentage,
                    'is_low': health_percentage < low_health_threshold,
                    'region': health_region
                }
                
            except Exception as e:
                self.logger.error(f"Health check failed: {e}")
                return None
        
        self.register_condition(condition_name, health_check, check_interval=0.5)
        return condition_name
    
    def create_text_monitor(self, text_to_find: str, 
                          region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """
        Create a text monitoring condition
        
        Args:
            text_to_find: Text to search for
            region: Optional region to search in
            
        Returns:
            Condition name for the text monitor
        """
        condition_name = f"text_monitor_{text_to_find.replace(' ', '_')}"
        
        def text_check():
            try:
                # Capture screen or region
                if region:
                    image = self.screen_capture.capture_region(*region)
                else:
                    image = self.screen_capture.capture_screen()
                
                # Search for text
                matches = self.ocr_engine.find_text(image, text_to_find, region)
                
                return {
                    'found': len(matches) > 0,
                    'matches': matches,
                    'text': text_to_find
                }
                
            except Exception as e:
                self.logger.error(f"Text check failed: {e}")
                return None
        
        self.register_condition(condition_name, text_check, check_interval=1.0)
        return condition_name
    
    def create_template_monitor(self, template_path: str, 
                              region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """
        Create a template monitoring condition
        
        Args:
            template_path: Path to template image
            region: Optional region to search in
            
        Returns:
            Condition name for the template monitor
        """
        condition_name = f"template_monitor_{template_path.split('/')[-1].split('.')[0]}"
        
        def template_check():
            try:
                # Capture screen or region
                if region:
                    image = self.screen_capture.capture_region(*region)
                else:
                    image = self.screen_capture.capture_screen()
                
                # Find template
                location = self.computer_vision.find_template(image, template_path)
                
                return {
                    'found': location is not None,
                    'location': location,
                    'template': template_path
                }
                
            except Exception as e:
                self.logger.error(f"Template check failed: {e}")
                return None
        
        self.register_condition(condition_name, template_check, check_interval=1.0)
        return condition_name
    
    def create_color_monitor(self, target_color: Tuple[int, int, int], 
                           region: Tuple[int, int, int, int], 
                           tolerance: int = 30) -> str:
        """
        Create a color monitoring condition
        
        Args:
            target_color: BGR color to monitor
            region: Region to monitor
            tolerance: Color tolerance
            
        Returns:
            Condition name for the color monitor
        """
        condition_name = f"color_monitor_{target_color}"
        
        def color_check():
            try:
                # Capture region
                image = self.screen_capture.capture_region(*region)
                
                # Find color regions
                color_regions = self.computer_vision.detect_color_region(
                    image, target_color, tolerance
                )
                
                return {
                    'found': len(color_regions) > 0,
                    'regions': color_regions,
                    'color': target_color
                }
                
            except Exception as e:
                self.logger.error(f"Color check failed: {e}")
                return None
        
        self.register_condition(condition_name, color_check, check_interval=0.5)
        return condition_name
    
    def _analyze_health_bar(self, health_image: np.ndarray) -> float:
        """
        Analyze health bar image to determine health percentage
        
        Args:
            health_image: Image of health bar region
            
        Returns:
            Health percentage (0.0 to 1.0)
        """
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(health_image, cv2.COLOR_BGR2HSV)
            
            # Define color ranges for health (green) and damage (red)
            # Green range for health
            lower_green = np.array([40, 50, 50])
            upper_green = np.array([80, 255, 255])
            
            # Red range for damage
            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 50, 50])
            upper_red2 = np.array([180, 255, 255])
            
            # Create masks
            green_mask = cv2.inRange(hsv, lower_green, upper_green)
            red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_mask = cv2.bitwise_or(red_mask1, red_mask2)
            
            # Count pixels
            green_pixels = cv2.countNonZero(green_mask)
            red_pixels = cv2.countNonZero(red_mask)
            total_pixels = green_pixels + red_pixels
            
            if total_pixels == 0:
                return 0.0
            
            health_percentage = green_pixels / total_pixels
            return min(1.0, max(0.0, health_percentage))
            
        except Exception as e:
            self.logger.error(f"Health bar analysis failed: {e}")
            return 0.0

class StateMonitorError(Exception):
    """Custom exception for state monitoring errors"""
    pass
