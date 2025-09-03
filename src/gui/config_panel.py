"""
Configuration panel for Cyclops automation system.
Provides detailed configuration interface for all automation settings.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import Dict, Any, Optional
from utils.config_manager import ConfigManager

class ConfigPanel:
    """Configuration panel with detailed settings"""
    
    def __init__(self, parent, config_manager: ConfigManager):
        """
        Initialize configuration panel
        
        Args:
            parent: Parent widget
            config_manager: Configuration manager instance
        """
        self.parent = parent
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Configuration variables
        self.config_vars: Dict[str, tk.Variable] = {}
        
        self._create_widgets()
        self._load_config()
    
    def _create_widgets(self):
        """Create configuration widgets"""
        # Create main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for different config sections
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create configuration tabs
        self._create_general_tab()
        self._create_screen_capture_tab()
        self._create_ocr_tab()
        self._create_automation_tab()
        self._create_advanced_tab()
        
        # Create button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Save Configuration", 
                  command=self._save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Configuration", 
                  command=self._load_config_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", 
                  command=self._reset_to_defaults).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Configuration", 
                  command=self._export_config).pack(side=tk.LEFT, padx=5)
    
    def _create_general_tab(self):
        """Create general configuration tab"""
        general_frame = ttk.Frame(self.notebook)
        self.notebook.add(general_frame, text="General")
        
        # Application settings
        app_frame = ttk.LabelFrame(general_frame, text="Application Settings")
        app_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Debug mode
        self.config_vars['debug_mode'] = tk.BooleanVar()
        ttk.Checkbutton(app_frame, text="Enable Debug Mode", 
                       variable=self.config_vars['debug_mode']).pack(anchor=tk.W, padx=5, pady=2)
        
        # Log level
        ttk.Label(app_frame, text="Log Level:").pack(anchor=tk.W, padx=5)
        self.config_vars['log_level'] = tk.StringVar()
        log_combo = ttk.Combobox(app_frame, textvariable=self.config_vars['log_level'], 
                                values=['DEBUG', 'INFO', 'WARNING', 'ERROR'], state='readonly')
        log_combo.pack(anchor=tk.W, padx=5, pady=2)
        
        # Auto-save
        self.config_vars['auto_save'] = tk.BooleanVar()
        ttk.Checkbutton(app_frame, text="Auto-save Configuration", 
                       variable=self.config_vars['auto_save']).pack(anchor=tk.W, padx=5, pady=2)
    
    def _create_screen_capture_tab(self):
        """Create screen capture configuration tab"""
        capture_frame = ttk.Frame(self.notebook)
        self.notebook.add(capture_frame, text="Screen Capture")
        
        # Screen capture settings
        sc_frame = ttk.LabelFrame(capture_frame, text="Screen Capture Settings")
        sc_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Default region
        ttk.Label(sc_frame, text="Default Region (x, y, width, height):").pack(anchor=tk.W, padx=5)
        region_frame = ttk.Frame(sc_frame)
        region_frame.pack(anchor=tk.W, padx=5, pady=2)
        
        self.config_vars['region_x'] = tk.StringVar()
        self.config_vars['region_y'] = tk.StringVar()
        self.config_vars['region_width'] = tk.StringVar()
        self.config_vars['region_height'] = tk.StringVar()
        
        ttk.Entry(region_frame, textvariable=self.config_vars['region_x'], width=8).pack(side=tk.LEFT, padx=2)
        ttk.Entry(region_frame, textvariable=self.config_vars['region_y'], width=8).pack(side=tk.LEFT, padx=2)
        ttk.Entry(region_frame, textvariable=self.config_vars['region_width'], width=8).pack(side=tk.LEFT, padx=2)
        ttk.Entry(region_frame, textvariable=self.config_vars['region_height'], width=8).pack(side=tk.LEFT, padx=2)
        
        # Capture FPS
        ttk.Label(sc_frame, text="Capture FPS:").pack(anchor=tk.W, padx=5)
        self.config_vars['capture_fps'] = tk.StringVar()
        ttk.Entry(sc_frame, textvariable=self.config_vars['capture_fps'], width=10).pack(anchor=tk.W, padx=5, pady=2)
        
        # Save screenshots
        self.config_vars['save_screenshots'] = tk.BooleanVar()
        ttk.Checkbutton(sc_frame, text="Save Screenshots for Debugging", 
                       variable=self.config_vars['save_screenshots']).pack(anchor=tk.W, padx=5, pady=2)
    
    def _create_ocr_tab(self):
        """Create OCR configuration tab"""
        ocr_frame = ttk.Frame(self.notebook)
        self.notebook.add(ocr_frame, text="OCR")
        
        # OCR settings
        ocr_config_frame = ttk.LabelFrame(ocr_frame, text="OCR Settings")
        ocr_config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Tesseract path
        ttk.Label(ocr_config_frame, text="Tesseract Path:").pack(anchor=tk.W, padx=5)
        path_frame = ttk.Frame(ocr_config_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.config_vars['tesseract_path'] = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.config_vars['tesseract_path']).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="Browse", command=self._browse_tesseract_path).pack(side=tk.RIGHT, padx=5)
        
        # Language
        ttk.Label(ocr_config_frame, text="Language:").pack(anchor=tk.W, padx=5)
        self.config_vars['ocr_language'] = tk.StringVar()
        ttk.Entry(ocr_config_frame, textvariable=self.config_vars['ocr_language'], width=10).pack(anchor=tk.W, padx=5, pady=2)
        
        # Confidence threshold
        ttk.Label(ocr_config_frame, text="Confidence Threshold (0.0-1.0):").pack(anchor=tk.W, padx=5)
        self.config_vars['confidence_threshold'] = tk.StringVar()
        ttk.Entry(ocr_config_frame, textvariable=self.config_vars['confidence_threshold'], width=10).pack(anchor=tk.W, padx=5, pady=2)
    
    def _create_automation_tab(self):
        """Create automation configuration tab"""
        auto_frame = ttk.Frame(self.notebook)
        self.notebook.add(auto_frame, text="Automation")
        
        # Rune Creation
        rune_frame = ttk.LabelFrame(auto_frame, text="Rune Creation")
        rune_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.config_vars['rune_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(rune_frame, text="Enable Rune Creation", 
                       variable=self.config_vars['rune_enabled']).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Label(rune_frame, text="Hotkey:").pack(anchor=tk.W, padx=5)
        self.config_vars['rune_hotkey'] = tk.StringVar()
        ttk.Entry(rune_frame, textvariable=self.config_vars['rune_hotkey'], width=10).pack(anchor=tk.W, padx=5, pady=2)
        
        # Food Eating
        food_frame = ttk.LabelFrame(auto_frame, text="Food Eating")
        food_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.config_vars['food_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(food_frame, text="Enable Food Eating", 
                       variable=self.config_vars['food_enabled']).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Label(food_frame, text="Cooldown (seconds):").pack(anchor=tk.W, padx=5)
        self.config_vars['food_cooldown'] = tk.StringVar()
        ttk.Entry(food_frame, textvariable=self.config_vars['food_cooldown'], width=10).pack(anchor=tk.W, padx=5, pady=2)
        
        # Health Monitoring
        health_frame = ttk.LabelFrame(auto_frame, text="Health Monitoring")
        health_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.config_vars['health_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(health_frame, text="Enable Health Monitoring", 
                       variable=self.config_vars['health_enabled']).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Label(health_frame, text="Low Health Threshold (%):").pack(anchor=tk.W, padx=5)
        self.config_vars['health_threshold'] = tk.StringVar()
        ttk.Entry(health_frame, textvariable=self.config_vars['health_threshold'], width=10).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Label(health_frame, text="Emergency Hotkey:").pack(anchor=tk.W, padx=5)
        self.config_vars['health_hotkey'] = tk.StringVar()
        ttk.Entry(health_frame, textvariable=self.config_vars['health_hotkey'], width=10).pack(anchor=tk.W, padx=5, pady=2)
    
    def _create_advanced_tab(self):
        """Create advanced configuration tab"""
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="Advanced")
        
        # Input simulation settings
        input_frame = ttk.LabelFrame(advanced_frame, text="Input Simulation")
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(input_frame, text="Mouse Speed (0.1-2.0):").pack(anchor=tk.W, padx=5)
        self.config_vars['mouse_speed'] = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.config_vars['mouse_speed'], width=10).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Label(input_frame, text="Key Press Duration (seconds):").pack(anchor=tk.W, padx=5)
        self.config_vars['key_duration'] = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.config_vars['key_duration'], width=10).pack(anchor=tk.W, padx=5, pady=2)
        
        self.config_vars['fail_safe_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(input_frame, text="Enable Fail-Safe", 
                       variable=self.config_vars['fail_safe_enabled']).pack(anchor=tk.W, padx=5, pady=2)
        
        # Computer vision settings
        cv_frame = ttk.LabelFrame(advanced_frame, text="Computer Vision")
        cv_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(cv_frame, text="Template Matching Threshold (0.0-1.0):").pack(anchor=tk.W, padx=5)
        self.config_vars['template_threshold'] = tk.StringVar()
        ttk.Entry(cv_frame, textvariable=self.config_vars['template_threshold'], width=10).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Label(cv_frame, text="Max Matches:").pack(anchor=tk.W, padx=5)
        self.config_vars['max_matches'] = tk.StringVar()
        ttk.Entry(cv_frame, textvariable=self.config_vars['max_matches'], width=10).pack(anchor=tk.W, padx=5, pady=2)
    
    def _browse_tesseract_path(self):
        """Browse for Tesseract executable"""
        filename = filedialog.askopenfilename(
            title="Select Tesseract Executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.config_vars['tesseract_path'].set(filename)
    
    def _load_config(self):
        """Load configuration values into widgets"""
        try:
            # General settings
            self.config_vars['debug_mode'].set(self.config_manager.get('application.debug_mode', False))
            self.config_vars['log_level'].set(self.config_manager.get('application.log_level', 'INFO'))
            self.config_vars['auto_save'].set(self.config_manager.get('gui.auto_save_config', True))
            
            # Screen capture settings
            region = self.config_manager.get('screen_capture.default_region', [0, 0, 1920, 1080])
            self.config_vars['region_x'].set(str(region[0]))
            self.config_vars['region_y'].set(str(region[1]))
            self.config_vars['region_width'].set(str(region[2]))
            self.config_vars['region_height'].set(str(region[3]))
            self.config_vars['capture_fps'].set(str(self.config_manager.get('screen_capture.capture_fps', 10)))
            self.config_vars['save_screenshots'].set(self.config_manager.get('screen_capture.save_screenshots', False))
            
            # OCR settings
            self.config_vars['tesseract_path'].set(self.config_manager.get('ocr.tesseract_path', ''))
            self.config_vars['ocr_language'].set(self.config_manager.get('ocr.language', 'eng'))
            self.config_vars['confidence_threshold'].set(str(self.config_manager.get('ocr.confidence_threshold', 0.7)))
            
            # Automation settings
            self.config_vars['rune_enabled'].set(self.config_manager.get('automation.rune_creation.enabled', False))
            self.config_vars['rune_hotkey'].set(self.config_manager.get('automation.rune_creation.hotkey', 'f1'))
            self.config_vars['food_enabled'].set(self.config_manager.get('automation.food_eating.enabled', False))
            self.config_vars['food_cooldown'].set(str(self.config_manager.get('automation.food_eating.cooldown_seconds', 5)))
            self.config_vars['health_enabled'].set(self.config_manager.get('automation.health_monitoring.enabled', False))
            self.config_vars['health_threshold'].set(str(int(self.config_manager.get('automation.health_monitoring.low_health_threshold', 0.3) * 100)))
            self.config_vars['health_hotkey'].set(self.config_manager.get('automation.health_monitoring.emergency_hotkey', 'f2'))
            
            # Advanced settings
            self.config_vars['mouse_speed'].set(str(self.config_manager.get('input_simulation.mouse_speed', 0.5)))
            self.config_vars['key_duration'].set(str(self.config_manager.get('input_simulation.key_press_duration', 0.1)))
            self.config_vars['fail_safe_enabled'].set(self.config_manager.get('input_simulation.fail_safe_enabled', True))
            self.config_vars['template_threshold'].set(str(self.config_manager.get('computer_vision.template_matching_threshold', 0.8)))
            self.config_vars['max_matches'].set(str(self.config_manager.get('computer_vision.max_matches', 10)))
            
            self.logger.info("Configuration loaded into panel")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            messagebox.showerror("Load Error", f"Failed to load configuration: {e}")
    
    def _save_config(self):
        """Save configuration from widgets"""
        try:
            # General settings
            self.config_manager.set('application.debug_mode', self.config_vars['debug_mode'].get())
            self.config_manager.set('application.log_level', self.config_vars['log_level'].get())
            self.config_manager.set('gui.auto_save_config', self.config_vars['auto_save'].get())
            
            # Screen capture settings
            region = [
                int(self.config_vars['region_x'].get()),
                int(self.config_vars['region_y'].get()),
                int(self.config_vars['region_width'].get()),
                int(self.config_vars['region_height'].get())
            ]
            self.config_manager.set('screen_capture.default_region', region)
            self.config_manager.set('screen_capture.capture_fps', int(self.config_vars['capture_fps'].get()))
            self.config_manager.set('screen_capture.save_screenshots', self.config_vars['save_screenshots'].get())
            
            # OCR settings
            self.config_manager.set('ocr.tesseract_path', self.config_vars['tesseract_path'].get())
            self.config_manager.set('ocr.language', self.config_vars['ocr_language'].get())
            self.config_manager.set('ocr.confidence_threshold', float(self.config_vars['confidence_threshold'].get()))
            
            # Automation settings
            self.config_manager.set('automation.rune_creation.enabled', self.config_vars['rune_enabled'].get())
            self.config_manager.set('automation.rune_creation.hotkey', self.config_vars['rune_hotkey'].get())
            self.config_manager.set('automation.food_eating.enabled', self.config_vars['food_enabled'].get())
            self.config_manager.set('automation.food_eating.cooldown_seconds', int(self.config_vars['food_cooldown'].get()))
            self.config_manager.set('automation.health_monitoring.enabled', self.config_vars['health_enabled'].get())
            self.config_manager.set('automation.health_monitoring.low_health_threshold', 
                                  int(self.config_vars['health_threshold'].get()) / 100)
            self.config_manager.set('automation.health_monitoring.emergency_hotkey', self.config_vars['health_hotkey'].get())
            
            # Advanced settings
            self.config_manager.set('input_simulation.mouse_speed', float(self.config_vars['mouse_speed'].get()))
            self.config_manager.set('input_simulation.key_press_duration', float(self.config_vars['key_duration'].get()))
            self.config_manager.set('input_simulation.fail_safe_enabled', self.config_vars['fail_safe_enabled'].get())
            self.config_manager.set('computer_vision.template_matching_threshold', float(self.config_vars['template_threshold'].get()))
            self.config_manager.set('computer_vision.max_matches', int(self.config_vars['max_matches'].get()))
            
            # Save to file
            self.config_manager.save_config()
            
            messagebox.showinfo("Configuration Saved", "Configuration has been saved successfully.")
            self.logger.info("Configuration saved from panel")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            messagebox.showerror("Save Error", f"Failed to save configuration: {e}")
    
    def _load_config_file(self):
        """Load configuration from file"""
        filename = filedialog.askopenfilename(
            title="Load Configuration File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.config_manager.config_path = filename
                self.config_manager.reload_config()
                self._load_config()
                messagebox.showinfo("Configuration Loaded", f"Configuration loaded from {filename}")
            except Exception as e:
                self.logger.error(f"Failed to load configuration file: {e}")
                messagebox.showerror("Load Error", f"Failed to load configuration file: {e}")
    
    def _reset_to_defaults(self):
        """Reset configuration to defaults"""
        if messagebox.askyesno("Reset Configuration", "Are you sure you want to reset to default configuration?"):
            try:
                self.config_manager.config = self.config_manager._get_default_config()
                self._load_config()
                messagebox.showinfo("Configuration Reset", "Configuration has been reset to defaults.")
            except Exception as e:
                self.logger.error(f"Failed to reset configuration: {e}")
                messagebox.showerror("Reset Error", f"Failed to reset configuration: {e}")
    
    def _export_config(self):
        """Export configuration to file"""
        filename = filedialog.asksaveasfilename(
            title="Export Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.config_manager.save_config(filename)
                messagebox.showinfo("Configuration Exported", f"Configuration exported to {filename}")
            except Exception as e:
                self.logger.error(f"Failed to export configuration: {e}")
                messagebox.showerror("Export Error", f"Failed to export configuration: {e}")
