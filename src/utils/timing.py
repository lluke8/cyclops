"""
Timing utilities for Cyclops automation system.
Handles delays, timing, and cooldown management.
"""

import time
import random
import logging
from typing import Dict, Optional, Callable, Any

class TimingUtils:
    """Timing utilities for automation with randomization and cooldowns"""
    
    def __init__(self):
        """Initialize timing utilities"""
        self.logger = logging.getLogger(__name__)
        self.cooldowns: Dict[str, float] = {}
        self.last_actions: Dict[str, float] = {}
        
        self.logger.debug("Timing utilities initialized")
    
    def adaptive_delay(self, base_delay: float, variance: float = 0.2, 
                      min_delay: float = 0.1) -> float:
        """
        Create adaptive delay with randomization to prevent detection
        
        Args:
            base_delay: Base delay in seconds
            variance: Variance factor (0.0 to 1.0)
            min_delay: Minimum delay in seconds
            
        Returns:
            Actual delay used
        """
        try:
            # Add randomization
            random_factor = random.uniform(1 - variance, 1 + variance)
            actual_delay = max(min_delay, base_delay * random_factor)
            
            time.sleep(actual_delay)
            return actual_delay
            
        except Exception as e:
            self.logger.error(f"Adaptive delay failed: {e}")
            time.sleep(base_delay)
            return base_delay
    
    def wait_for_condition(self, condition_func: Callable[[], bool], 
                          timeout: float = 10.0, check_interval: float = 0.5,
                          timeout_message: str = "Condition timeout") -> bool:
        """
        Wait until condition is met or timeout occurs
        
        Args:
            condition_func: Function that returns True when condition is met
            timeout: Maximum wait time in seconds
            check_interval: How often to check the condition
            timeout_message: Message to log on timeout
            
        Returns:
            True if condition was met, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if condition_func():
                    elapsed = time.time() - start_time
                    self.logger.debug(f"Condition met after {elapsed:.2f} seconds")
                    return True
            except Exception as e:
                self.logger.error(f"Error checking condition: {e}")
            
            time.sleep(check_interval)
        
        self.logger.warning(f"{timeout_message} after {timeout} seconds")
        return False
    
    def wait_for_change(self, value_func: Callable[[], Any], 
                       timeout: float = 10.0, check_interval: float = 0.5) -> bool:
        """
        Wait for a value to change from its initial state
        
        Args:
            value_func: Function that returns the value to monitor
            timeout: Maximum wait time in seconds
            check_interval: How often to check for changes
            
        Returns:
            True if value changed, False if timeout
        """
        try:
            initial_value = value_func()
            return self.wait_for_condition(
                lambda: value_func() != initial_value,
                timeout=timeout,
                check_interval=check_interval,
                timeout_message="Value did not change"
            )
        except Exception as e:
            self.logger.error(f"Wait for change failed: {e}")
            return False
    
    def set_cooldown(self, action_name: str, cooldown_seconds: float):
        """
        Set cooldown for an action
        
        Args:
            action_name: Name of the action
            cooldown_seconds: Cooldown duration in seconds
        """
        self.cooldowns[action_name] = cooldown_seconds
        self.logger.debug(f"Set cooldown for '{action_name}': {cooldown_seconds}s")
    
    def can_act(self, action_name: str) -> bool:
        """
        Check if an action can be performed (not in cooldown)
        
        Args:
            action_name: Name of the action
            
        Returns:
            True if action can be performed, False if in cooldown
        """
        if action_name not in self.cooldowns:
            return True
        
        last_action_time = self.last_actions.get(action_name, 0)
        cooldown = self.cooldowns[action_name]
        
        can_act = (time.time() - last_action_time) >= cooldown
        
        if not can_act:
            remaining = cooldown - (time.time() - last_action_time)
            self.logger.debug(f"Action '{action_name}' in cooldown, {remaining:.1f}s remaining")
        
        return can_act
    
    def record_action(self, action_name: str):
        """
        Record that an action was performed
        
        Args:
            action_name: Name of the action
        """
        self.last_actions[action_name] = time.time()
        self.logger.debug(f"Recorded action: {action_name}")
    
    def get_remaining_cooldown(self, action_name: str) -> float:
        """
        Get remaining cooldown time for an action
        
        Args:
            action_name: Name of the action
            
        Returns:
            Remaining cooldown in seconds (0 if not in cooldown)
        """
        if action_name not in self.cooldowns:
            return 0.0
        
        last_action_time = self.last_actions.get(action_name, 0)
        cooldown = self.cooldowns[action_name]
        elapsed = time.time() - last_action_time
        
        return max(0.0, cooldown - elapsed)
    
    def wait_for_cooldown(self, action_name: str) -> bool:
        """
        Wait for an action's cooldown to expire
        
        Args:
            action_name: Name of the action
            
        Returns:
            True if cooldown expired, False if action not found
        """
        if action_name not in self.cooldowns:
            return True
        
        remaining = self.get_remaining_cooldown(action_name)
        if remaining > 0:
            self.logger.debug(f"Waiting {remaining:.1f}s for cooldown of '{action_name}'")
            time.sleep(remaining)
        
        return True
    
    def safe_action(self, action_name: str, action_func: Callable[[], Any], 
                   cooldown_seconds: float = 1.0) -> Any:
        """
        Perform an action with cooldown protection
        
        Args:
            action_name: Name of the action
            action_func: Function to execute
            cooldown_seconds: Cooldown duration
            
        Returns:
            Result of action function or None if in cooldown
        """
        if not self.can_act(action_name):
            return None
        
        try:
            result = action_func()
            self.record_action(action_name)
            self.set_cooldown(action_name, cooldown_seconds)
            return result
        except Exception as e:
            self.logger.error(f"Safe action '{action_name}' failed: {e}")
            return None
    
    def retry_with_backoff(self, func: Callable[[], Any], max_retries: int = 3, 
                          base_delay: float = 1.0, backoff_factor: float = 2.0) -> Any:
        """
        Retry a function with exponential backoff
        
        Args:
            func: Function to retry
            max_retries: Maximum number of retries
            base_delay: Base delay between retries
            backoff_factor: Factor to multiply delay by each retry
            
        Returns:
            Result of successful function call or None if all retries failed
        """
        delay = base_delay
        
        for attempt in range(max_retries + 1):
            try:
                result = func()
                if attempt > 0:
                    self.logger.info(f"Function succeeded on attempt {attempt + 1}")
                return result
            except Exception as e:
                if attempt == max_retries:
                    self.logger.error(f"Function failed after {max_retries + 1} attempts: {e}")
                    return None
                
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying in {delay:.1f}s")
                time.sleep(delay)
                delay *= backoff_factor
        
        return None
    
    def measure_time(self, func: Callable[[], Any]) -> tuple[Any, float]:
        """
        Measure execution time of a function
        
        Args:
            func: Function to measure
            
        Returns:
            Tuple of (result, execution_time_seconds)
        """
        start_time = time.time()
        try:
            result = func()
            execution_time = time.time() - start_time
            return result, execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Function failed after {execution_time:.3f}s: {e}")
            raise
    
    def create_timer(self, duration: float) -> 'Timer':
        """
        Create a timer for measuring elapsed time
        
        Args:
            duration: Timer duration in seconds
            
        Returns:
            Timer instance
        """
        return Timer(duration)
    
    def sleep_until(self, target_time: float):
        """
        Sleep until a specific time
        
        Args:
            target_time: Target time (time.time() format)
        """
        current_time = time.time()
        if target_time > current_time:
            sleep_duration = target_time - current_time
            self.logger.debug(f"Sleeping for {sleep_duration:.2f} seconds")
            time.sleep(sleep_duration)

class Timer:
    """Simple timer for measuring elapsed time"""
    
    def __init__(self, duration: float):
        """
        Initialize timer
        
        Args:
            duration: Timer duration in seconds
        """
        self.duration = duration
        self.start_time = time.time()
        self.logger = logging.getLogger(__name__)
    
    def is_expired(self) -> bool:
        """Check if timer has expired"""
        return time.time() - self.start_time >= self.duration
    
    def get_elapsed(self) -> float:
        """Get elapsed time in seconds"""
        return time.time() - self.start_time
    
    def get_remaining(self) -> float:
        """Get remaining time in seconds"""
        return max(0.0, self.duration - self.get_elapsed())
    
    def reset(self):
        """Reset timer to start time"""
        self.start_time = time.time()
        self.logger.debug("Timer reset")
    
    def wait_for_expiry(self):
        """Wait until timer expires"""
        remaining = self.get_remaining()
        if remaining > 0:
            time.sleep(remaining)
