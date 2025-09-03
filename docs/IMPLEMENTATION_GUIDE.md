# Cyclops Implementation Guide

## Development Workflow

### 1. Setting Up Development Environment

```bash
# 1. Activate virtual environment (recommended)
py -m venv venv
venv\Scripts\activate

# 2. Install dependencies
py -m pip install -r requirements.txt

# 3. Run tests to verify setup
py -m pytest tests/

# 4. Start development server
py main.py
```

### 2. Core Module Development Pattern

When implementing core modules, follow this pattern:

```python
# Example: src/core/screen_capture.py
import logging
import time
from typing import Optional, Tuple
import pyautogui
import cv2
import numpy as np

class ScreenCapture:
    """Screen capture functionality with error handling and optimization"""
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.last_capture = None
        self.capture_count = 0
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        Capture screen with error handling and optimization
        
        Args:
            region: (x, y, width, height) tuple for region capture
            
        Returns:
            numpy array representing the captured image
            
        Raises:
            ScreenCaptureError: If capture fails
        """
        try:
            self.logger.debug(f"Capturing screen, region: {region}")
            
            # Take screenshot
            screenshot = pyautogui.screenshot(region=region)
            
            # Convert to numpy array for OpenCV compatibility
            img_array = np.array(screenshot)
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            self.capture_count += 1
            self.last_capture = img_array
            
            self.logger.debug(f"Screen captured successfully, count: {self.capture_count}")
            return img_array
            
        except Exception as e:
            self.logger.error(f"Screen capture failed: {e}")
            raise ScreenCaptureError(f"Failed to capture screen: {e}")
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """Capture specific screen region"""
        return self.capture_screen((x, y, width, height))
    
    def save_capture(self, filename: str, region: Optional[Tuple[int, int, int, int]] = None):
        """Save capture to file for debugging"""
        if self.config.get('save_screenshots', False):
            img = self.capture_screen(region)
            cv2.imwrite(filename, img)
            self.logger.info(f"Screenshot saved: {filename}")

class ScreenCaptureError(Exception):
    """Custom exception for screen capture errors"""
    pass
```

### 3. Automation Module Development Pattern

```python
# Example: src/automation/rune_creation.py
import logging
import time
from typing import Optional, Tuple
from ..core.screen_capture import ScreenCapture
from ..core.computer_vision import ComputerVision
from ..core.input_simulator import InputSimulator
from ..utils.timing import TimingUtils

class RuneCreationAutomation:
    """Rune creation automation with robust error handling"""
    
    def __init__(self, config: dict, screen_capture: ScreenCapture, 
                 computer_vision: ComputerVision, input_simulator: InputSimulator):
        self.config = config
        self.screen_capture = screen_capture
        self.computer_vision = computer_vision
        self.input_simulator = input_simulator
        self.timing = TimingUtils()
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        
    def start_automation(self):
        """Start the rune creation automation"""
        if not self.config.get('enabled', False):
            self.logger.warning("Rune creation automation is disabled")
            return False
        
        self.logger.info("Starting rune creation automation")
        self.is_running = True
        
        try:
            while self.is_running:
                if self._check_for_rune_item():
                    self._create_rune()
                    self.timing.adaptive_delay(2.0)  # Wait between creations
                else:
                    self.timing.adaptive_delay(1.0)  # Check again in 1 second
                    
        except Exception as e:
            self.logger.error(f"Rune creation automation failed: {e}")
            return False
        finally:
            self.is_running = False
        
        return True
    
    def stop_automation(self):
        """Stop the automation"""
        self.logger.info("Stopping rune creation automation")
        self.is_running = False
    
    def _check_for_rune_item(self) -> bool:
        """Check if rune item is present on screen"""
        try:
            # Capture current screen
            screenshot = self.screen_capture.capture_screen()
            
            # Load template
            template_path = self.config.get('item_template_path')
            if not template_path:
                self.logger.error("Template path not configured")
                return False
            
            # Find template
            location = self.computer_vision.find_template(screenshot, template_path)
            return location is not None
            
        except Exception as e:
            self.logger.error(f"Error checking for rune item: {e}")
            return False
    
    def _create_rune(self):
        """Execute rune creation sequence"""
        try:
            self.logger.info("Creating rune...")
            
            # Find item location
            screenshot = self.screen_capture.capture_screen()
            template_path = self.config.get('item_template_path')
            location = self.computer_vision.find_template(screenshot, template_path)
            
            if not location:
                self.logger.warning("Could not find rune item for creation")
                return False
            
            # Get item center coordinates
            item_x = location.left + location.width // 2
            item_y = location.top + location.height // 2
            
            # Get target position
            target_pos = self.config.get('target_position', [500, 300])
            target_x, target_y = target_pos
            
            # Drag item to target location
            self.input_simulator.drag_and_drop(item_x, item_y, target_x, target_y)
            
            # Press hotkey
            hotkey = self.config.get('hotkey', 'f1')
            self.input_simulator.press_key(hotkey)
            
            self.logger.info("Rune creation completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Rune creation failed: {e}")
            return False
```

### 4. Configuration Management Pattern

```python
# Example: src/utils/config_manager.py
import json
import os
import logging
from typing import Dict, Any

class ConfigManager:
    """Configuration management with validation and defaults"""
    
    def __init__(self, config_path: str = "config/default_config.json"):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file with fallback to defaults"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
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
            }
            # ... more defaults
        }
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def save_config(self, path: Optional[str] = None):
        """Save configuration to file"""
        save_path = path or self.config_path
        try:
            with open(save_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info(f"Configuration saved to {save_path}")
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
```

### 5. Testing Pattern

```python
# Example: tests/test_screen_capture.py
import pytest
import numpy as np
from unittest.mock import Mock, patch
from src.core.screen_capture import ScreenCapture, ScreenCaptureError

class TestScreenCapture:
    """Test cases for ScreenCapture class"""
    
    @pytest.fixture
    def screen_capture(self):
        """Create ScreenCapture instance for testing"""
        config = {
            'save_screenshots': False,
            'debug_mode': True
        }
        return ScreenCapture(config)
    
    def test_capture_screen_success(self, screen_capture):
        """Test successful screen capture"""
        with patch('pyautogui.screenshot') as mock_screenshot:
            # Mock screenshot return value
            mock_image = Mock()
            mock_image.__array__ = Mock(return_value=np.zeros((100, 100, 3), dtype=np.uint8))
            mock_screenshot.return_value = mock_image
            
            result = screen_capture.capture_screen()
            
            assert result is not None
            assert isinstance(result, np.ndarray)
            mock_screenshot.assert_called_once()
    
    def test_capture_screen_failure(self, screen_capture):
        """Test screen capture failure handling"""
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_screenshot.side_effect = Exception("Screenshot failed")
            
            with pytest.raises(ScreenCaptureError):
                screen_capture.capture_screen()
    
    def test_capture_region(self, screen_capture):
        """Test region capture"""
        with patch('pyautogui.screenshot') as mock_screenshot:
            mock_image = Mock()
            mock_image.__array__ = Mock(return_value=np.zeros((50, 50, 3), dtype=np.uint8))
            mock_screenshot.return_value = mock_image
            
            result = screen_capture.capture_region(100, 100, 200, 200)
            
            assert result is not None
            mock_screenshot.assert_called_once_with(region=(100, 100, 200, 200))
```

### 6. GUI Development Pattern

```python
# Example: src/gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from ..utils.config_manager import ConfigManager

class CyclopsMainWindow:
    """Main application window with tabbed interface"""
    
    def __init__(self, root):
        self.root = root
        self.config_manager = ConfigManager()
        self.logger = logging.getLogger(__name__)
        
        self._setup_window()
        self._create_widgets()
        self._setup_bindings()
    
    def _setup_window(self):
        """Setup main window properties"""
        self.root.title("Cyclops - Desktop Automation")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
    
    def _create_widgets(self):
        """Create and layout widgets"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self._create_automation_tab()
        self._create_config_tab()
        self._create_status_tab()
    
    def _create_automation_tab(self):
        """Create automation control tab"""
        automation_frame = ttk.Frame(self.notebook)
        self.notebook.add(automation_frame, text="Automation")
        
        # Automation controls
        ttk.Label(automation_frame, text="Automation Control").pack(pady=10)
        
        # Start/Stop buttons
        button_frame = ttk.Frame(automation_frame)
        button_frame.pack(pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start", command=self._start_automation)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self._stop_automation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
    
    def _create_config_tab(self):
        """Create configuration tab"""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configuration")
        
        # Configuration controls
        ttk.Label(config_frame, text="Configuration Settings").pack(pady=10)
        
        # Add configuration widgets here
        self._create_config_widgets(config_frame)
    
    def _create_status_tab(self):
        """Create status and logging tab"""
        status_frame = ttk.Frame(self.notebook)
        self.notebook.add(status_frame, text="Status")
        
        # Status display
        ttk.Label(status_frame, text="Application Status").pack(pady=10)
        
        # Log display
        self.log_text = tk.Text(status_frame, height=20, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _create_config_widgets(self, parent):
        """Create configuration widgets"""
        # Example: Rune creation configuration
        rune_frame = ttk.LabelFrame(parent, text="Rune Creation")
        rune_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Enable checkbox
        self.rune_enabled = tk.BooleanVar()
        self.rune_enabled.set(self.config_manager.get('automation.rune_creation.enabled', False))
        ttk.Checkbutton(rune_frame, text="Enable Rune Creation", 
                       variable=self.rune_enabled).pack(anchor=tk.W)
        
        # Hotkey setting
        ttk.Label(rune_frame, text="Hotkey:").pack(anchor=tk.W)
        self.rune_hotkey = tk.StringVar()
        self.rune_hotkey.set(self.config_manager.get('automation.rune_creation.hotkey', 'f1'))
        ttk.Entry(rune_frame, textvariable=self.rune_hotkey, width=10).pack(anchor=tk.W)
    
    def _setup_bindings(self):
        """Setup event bindings"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _start_automation(self):
        """Start automation"""
        try:
            self.logger.info("Starting automation...")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            # Start automation logic here
        except Exception as e:
            self.logger.error(f"Failed to start automation: {e}")
            messagebox.showerror("Error", f"Failed to start automation: {e}")
    
    def _stop_automation(self):
        """Stop automation"""
        try:
            self.logger.info("Stopping automation...")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            # Stop automation logic here
        except Exception as e:
            self.logger.error(f"Failed to stop automation: {e}")
            messagebox.showerror("Error", f"Failed to stop automation: {e}")
    
    def _on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self._save_config()
            self.root.destroy()
    
    def _save_config(self):
        """Save current configuration"""
        try:
            self.config_manager.set('automation.rune_creation.enabled', self.rune_enabled.get())
            self.config_manager.set('automation.rune_creation.hotkey', self.rune_hotkey.get())
            self.config_manager.save_config()
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
```

## Development Checklist

### Before Starting Development:
- [ ] Set up virtual environment
- [ ] Install all dependencies
- [ ] Run existing tests
- [ ] Review project structure
- [ ] Read philosophical approach document

### During Development:
- [ ] Follow naming conventions
- [ ] Add type hints
- [ ] Include docstrings
- [ ] Handle exceptions properly
- [ ] Add logging statements
- [ ] Write unit tests
- [ ] Update configuration as needed

### Before Committing:
- [ ] Run all tests
- [ ] Check code style
- [ ] Update documentation
- [ ] Test in different environments
- [ ] Verify error handling
- [ ] Check performance impact

### Code Review Checklist:
- [ ] Code follows project patterns
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate
- [ ] Tests cover new functionality
- [ ] Configuration is externalized
- [ ] Performance is acceptable
- [ ] Security considerations addressed
