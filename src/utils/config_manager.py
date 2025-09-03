"""
Configuration management for Cyclops automation system.
Handles loading, saving, and validation of configuration files.
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List

class ConfigManager:
    """Configuration management with validation and defaults"""
    
    def __init__(self, config_path: str = "config/default_config.json"):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()
        
        self.logger.info(f"Configuration manager initialized with: {config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file with fallback to defaults"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.logger.info(f"Configuration loaded from {self.config_path}")
                return config
            else:
                self.logger.warning(f"Config file not found: {self.config_path}")
                return self._get_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "application": {
                "name": "Cyclops",
                "version": "1.0.0",
                "debug_mode": False,
                "log_level": "INFO"
            },
            "screen_capture": {
                "default_region": [0, 0, 1920, 1080],
                "capture_fps": 10,
                "save_screenshots": False
            },
            "ocr": {
                "tesseract_path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
                "language": "eng",
                "confidence_threshold": 0.7
            },
            "computer_vision": {
                "template_matching_threshold": 0.8,
                "max_matches": 10,
                "scale_factors": [0.8, 0.9, 1.0, 1.1, 1.2]
            },
            "input_simulation": {
                "mouse_speed": 0.5,
                "key_press_duration": 0.1,
                "fail_safe_enabled": True,
                "fail_safe_position": [0, 0]
            },
            "automation": {
                "rune_creation": {
                    "enabled": False,
                    "item_template_path": "assets/templates/rune_item.png",
                    "target_position": [500, 300],
                    "hotkey": "f1"
                },
                "food_eating": {
                    "enabled": False,
                    "food_position": [100, 100],
                    "cooldown_seconds": 5
                },
                "health_monitoring": {
                    "enabled": False,
                    "health_bar_region": [50, 50, 200, 20],
                    "low_health_threshold": 0.3,
                    "emergency_hotkey": "f2"
                }
            },
            "gui": {
                "window_size": [800, 600],
                "theme": "default",
                "auto_save_config": True
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key_path: Dot-separated path to configuration value
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """
        Set configuration value using dot notation
        
        Args:
            key_path: Dot-separated path to configuration value
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        
        self.logger.debug(f"Set config value: {key_path} = {value}")
    
    def save_config(self, path: Optional[str] = None) -> bool:
        """
        Save configuration to file
        
        Args:
            path: Optional path to save to (defaults to original path)
            
        Returns:
            True if successful, False otherwise
        """
        save_path = path or self.config_path
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration saved to {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            return False
    
    def reload_config(self) -> bool:
        """
        Reload configuration from file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.config = self._load_config()
            self.logger.info("Configuration reloaded")
            return True
        except Exception as e:
            self.logger.error(f"Failed to reload config: {e}")
            return False
    
    def validate_config(self) -> List[str]:
        """
        Validate configuration and return list of issues
        
        Returns:
            List of validation error messages
        """
        issues = []
        
        try:
            # Validate required sections
            required_sections = ['application', 'screen_capture', 'ocr', 'computer_vision', 'input_simulation']
            for section in required_sections:
                if section not in self.config:
                    issues.append(f"Missing required section: {section}")
            
            # Validate screen capture settings
            if 'screen_capture' in self.config:
                sc_config = self.config['screen_capture']
                if 'default_region' in sc_config:
                    region = sc_config['default_region']
                    if not isinstance(region, list) or len(region) != 4:
                        issues.append("screen_capture.default_region must be a list of 4 integers")
                    elif any(not isinstance(x, int) or x < 0 for x in region):
                        issues.append("screen_capture.default_region values must be non-negative integers")
            
            # Validate OCR settings
            if 'ocr' in self.config:
                ocr_config = self.config['ocr']
                if 'confidence_threshold' in ocr_config:
                    threshold = ocr_config['confidence_threshold']
                    if not isinstance(threshold, (int, float)) or not (0 <= threshold <= 1):
                        issues.append("ocr.confidence_threshold must be a number between 0 and 1")
            
            # Validate automation settings
            if 'automation' in self.config:
                auto_config = self.config['automation']
                for automation_name, automation_config in auto_config.items():
                    if not isinstance(automation_config, dict):
                        continue
                    
                    if 'enabled' in automation_config and not isinstance(automation_config['enabled'], bool):
                        issues.append(f"automation.{automation_name}.enabled must be a boolean")
            
        except Exception as e:
            issues.append(f"Validation error: {e}")
        
        if issues:
            self.logger.warning(f"Configuration validation found {len(issues)} issues")
        else:
            self.logger.info("Configuration validation passed")
        
        return issues
    
    def get_automation_config(self, automation_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific automation
        
        Args:
            automation_name: Name of the automation
            
        Returns:
            Configuration dictionary for the automation
        """
        return self.get(f'automation.{automation_name}', {})
    
    def is_automation_enabled(self, automation_name: str) -> bool:
        """
        Check if an automation is enabled
        
        Args:
            automation_name: Name of the automation
            
        Returns:
            True if enabled, False otherwise
        """
        return self.get(f'automation.{automation_name}.enabled', False)
    
    def enable_automation(self, automation_name: str):
        """
        Enable an automation
        
        Args:
            automation_name: Name of the automation
        """
        self.set(f'automation.{automation_name}.enabled', True)
        self.logger.info(f"Enabled automation: {automation_name}")
    
    def disable_automation(self, automation_name: str):
        """
        Disable an automation
        
        Args:
            automation_name: Name of the automation
        """
        self.set(f'automation.{automation_name}.enabled', False)
        self.logger.info(f"Disabled automation: {automation_name}")
    
    def create_backup(self, backup_path: Optional[str] = None) -> bool:
        """
        Create a backup of the current configuration
        
        Args:
            backup_path: Optional path for backup file
            
        Returns:
            True if successful, False otherwise
        """
        if backup_path is None:
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.config_path}.backup_{timestamp}"
        
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration backup created: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return False
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """
        Restore configuration from backup
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(backup_path):
                self.logger.error(f"Backup file not found: {backup_path}")
                return False
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_config = json.load(f)
            
            # Validate backup before restoring
            temp_manager = ConfigManager()
            temp_manager.config = backup_config
            issues = temp_manager.validate_config()
            
            if issues:
                self.logger.error(f"Backup validation failed: {issues}")
                return False
            
            # Restore configuration
            self.config = backup_config
            self.save_config()
            
            self.logger.info(f"Configuration restored from backup: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore from backup: {e}")
            return False

class ConfigError(Exception):
    """Custom exception for configuration errors"""
    pass
