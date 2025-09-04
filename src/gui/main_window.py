"""
Main window for Cyclops automation system.
Provides the primary user interface for controlling automation.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
import threading
import time
from typing import Dict, Any, Optional
from utils.config_manager import ConfigManager
from core.screen_capture import ScreenCapture
from core.ocr_engine import OCREngine
from core.computer_vision import ComputerVision
from core.input_simulator import InputSimulator
from core.state_monitor import StateMonitor
from automation.workflow_manager import WorkflowManager

class CyclopsMainWindow:
    """Main application window with tabbed interface"""
    
    def __init__(self, root):
        """
        Initialize main window
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.config_manager = ConfigManager()
        self.screen_capture = ScreenCapture(self.config_manager.config)
        self.ocr_engine = OCREngine(self.config_manager.config)
        self.computer_vision = ComputerVision(self.config_manager.config)
        self.input_simulator = InputSimulator(self.config_manager.config)
        self.state_monitor = StateMonitor(
            self.config_manager.config, 
            self.screen_capture, 
            self.ocr_engine, 
            self.computer_vision
        )
        self.workflow_manager = WorkflowManager(
            self.config_manager,
            self.screen_capture,
            self.input_simulator,
            self.state_monitor
        )
        
        # GUI state
        self.is_running = False
        self.status_update_thread = None
        
        # Overlay management
        self.persistent_overlay = None
        self.rune_persistent_overlay = None
        
        # Setup window
        self._setup_window()
        self._create_widgets()
        self._setup_bindings()
        self._start_status_updates()
        
        # Create persistent overlay if region is configured and overlay is enabled
        if self.show_overlay.get():
            current_region = self.config_manager.get('automation.health_monitoring.health_bar_region', [50, 50, 200, 20])
            self._create_persistent_overlay(
                current_region['x'], current_region['y'],
                current_region['width'], current_region['height']
            )
        
        # Create persistent overlay for rune search region if configured
        rune_search_region = self.config_manager.get('automation.rune_creation.search_region', {})
        if rune_search_region and all(key in rune_search_region for key in ['x', 'y', 'width', 'height']):
            self._create_rune_persistent_overlay(
                rune_search_region['x'], rune_search_region['y'],
                rune_search_region['width'], rune_search_region['height']
            )
        
        # Register callback for health monitoring automation events
        self.workflow_manager.register_callback('health_monitor', self._on_health_monitoring_event)
        
        # Set up emergency stop callback for health monitor
        health_automation = self.workflow_manager.get_automation('health_monitor')
        if health_automation:
            health_automation.set_emergency_stop_callback(self._on_emergency_stop)
        
        # Start countdown timer update
        self.root.after(1000, self._update_countdown)
        
        self.logger.info("Main window initialized")
    
    def _setup_window(self):
        """Setup main window properties"""
        self.root.title("Cyclops - Automation System")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 10))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
    
    def _create_widgets(self):
        """Create and layout widgets"""
        # Create main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create title
        title_label = ttk.Label(main_frame, text="Cyclops Desktop Automation", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self._create_automation_tab()
        self._create_config_tab()
        self._create_status_tab()
        self._create_logs_tab()
        
        # Create status bar
        self._create_status_bar(main_frame)
    
    def _create_automation_tab(self):
        """Create automation control tab"""
        automation_frame = ttk.Frame(self.notebook)
        self.notebook.add(automation_frame, text="Automation")
        
        # Main automation controls
        control_frame = ttk.LabelFrame(automation_frame, text="Automation Control")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Main control button and countdown timer frame
        button_timer_frame = ttk.Frame(control_frame)
        button_timer_frame.pack(pady=20)
        
        # Main control button
        self.active_button = ttk.Button(button_timer_frame, text="ACTIVE", 
                                       command=self._toggle_active, style='Active.TButton')
        self.active_button.pack(side=tk.LEFT, padx=(0, 20))
        
        # Countdown timer for next food and rune interactions
        self.countdown_label = ttk.Label(button_timer_frame, text="Food: --:--:-- | Rune: --:--:--", 
                                        font=('Arial', 12, 'bold'), foreground='blue')
        self.countdown_label.pack(side=tk.LEFT)
        
        # Configure button styles
        style = ttk.Style()
        style.configure('Active.TButton', font=('Arial', 14, 'bold'))
        style.configure('Stop.TButton', font=('Arial', 14, 'bold'), foreground='red')
        
        # Automation checkboxes
        checkbox_frame = ttk.Frame(automation_frame)
        checkbox_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Rune Creation
        self.rune_enabled = tk.BooleanVar()
        self.rune_enabled.set(self.config_manager.get('automation.rune_creation.enabled', False))
        ttk.Checkbutton(checkbox_frame, text="Rune Maker", 
                       variable=self.rune_enabled,
                       command=lambda: self._update_automation_config('rune_creation', 'enabled', self.rune_enabled.get())).pack(anchor=tk.W, pady=5)
        
        # Food Eating
        self.food_enabled = tk.BooleanVar()
        self.food_enabled.set(self.config_manager.get('automation.food_eating.enabled', False))
        ttk.Checkbutton(checkbox_frame, text="Food", 
                       variable=self.food_enabled,
                       command=lambda: self._update_automation_config('food_eating', 'enabled', self.food_enabled.get())).pack(anchor=tk.W, pady=5)
        
        # Health Monitoring
        self.health_enabled = tk.BooleanVar()
        self.health_enabled.set(self.config_manager.get('automation.health_monitoring.enabled', False))
        ttk.Checkbutton(checkbox_frame, text="Health Monitoring", 
                       variable=self.health_enabled,
                       command=lambda: self._update_automation_config('health_monitoring', 'enabled', self.health_enabled.get())).pack(anchor=tk.W, pady=5)
        
        # Emergency Actions Configuration
        emergency_frame = ttk.LabelFrame(automation_frame, text="Emergency Actions")
        emergency_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Number of emergency clicks
        click_count_frame = ttk.Frame(emergency_frame)
        click_count_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(click_count_frame, text="Number of Emergency Clicks:").pack(side=tk.LEFT)
        self.emergency_click_count = tk.IntVar()
        self.emergency_click_count.set(self.config_manager.get('automation.health_monitoring.emergency_click_count', 1))
        click_spinbox = ttk.Spinbox(click_count_frame, from_=1, to=10, width=5, 
                                   textvariable=self.emergency_click_count,
                                   command=self._update_emergency_config)
        click_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Record emergency clicks button
        self.record_emergency_button = ttk.Button(emergency_frame, text="Record Emergency Clicks", 
                                                 command=self._record_emergency_clicks)
        self.record_emergency_button.pack(pady=5)
        
        # Show recorded clicks
        self.emergency_clicks_label = ttk.Label(emergency_frame, text="No emergency clicks recorded")
        self.emergency_clicks_label.pack(pady=2)
        
        # Initialize emergency clicks display
        self._update_emergency_clicks_display()
    
    def _toggle_active(self):
        """Toggle the main automation system on/off"""
        if not self.is_running:
            # Start automation
            self._start_automation()
        else:
            # Stop automation
            self._stop_automation()
    
    def _start_automation(self):
        """Start the main automation system"""
        try:
            # Get enabled automations (using correct names from workflow manager)
            enabled_automations = []
            if self.rune_enabled.get():
                enabled_automations.append('rune_creation')
            if self.food_enabled.get():
                enabled_automations.append('food_eating')
            if self.health_enabled.get():
                enabled_automations.append('health_monitor')  # Note: health_monitor, not health_monitoring
            
            if not enabled_automations:
                messagebox.showwarning("No Automations Selected", "Please enable at least one automation before starting.")
                return
            
            self.logger.info(f"Starting automations: {enabled_automations}")
            
            # Create a custom workflow with selected automations
            workflow_name = "custom_automation"
            workflow_description = f"Custom automation with: {', '.join(enabled_automations)}"
            
            # Check if workflow is already running and stop it first
            if workflow_name in self.workflow_manager.active_workflows:
                self.logger.info(f"Stopping existing workflow '{workflow_name}' before restarting")
                self.workflow_manager.stop_workflow(workflow_name)
                # Give a moment for cleanup
                time.sleep(0.5)
            
            # Create or update the custom workflow
            self.workflow_manager.create_custom_workflow(
                workflow_name, 
                workflow_description, 
                enabled_automations
            )
            
            # Start the custom workflow
            success = self.workflow_manager.start_workflow(workflow_name)
            if not success:
                self.logger.error("Failed to start custom workflow")
                messagebox.showerror("Start Failed", "Failed to start automation")
                return
            
            # Update UI
            self.is_running = True
            self.active_button.config(text="STOP", style='Stop.TButton')
            self.status_label.config(text="Running")
            self._log_status("Automation started")
            
        except Exception as e:
            self.logger.error(f"Failed to start automation: {e}")
            messagebox.showerror("Error", f"Failed to start automation: {e}")
    
    def _stop_automation(self):
        """Stop the main automation system"""
        try:
            self.logger.info("Stopping all automations")
            
            # Stop the custom workflow
            self.workflow_manager.stop_workflow("custom_automation")
            
            # Update UI
            self.is_running = False
            self.active_button.config(text="ACTIVE", style='Active.TButton')
            self.status_label.config(text="Stopped")
            self._log_status("Automation stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop automation: {e}")
            messagebox.showerror("Error", f"Failed to stop automation: {e}")
    
    def _update_emergency_config(self):
        """Update emergency configuration when click count changes"""
        try:
            self.config_manager.set('automation.health_monitoring.emergency_click_count', 
                                  self.emergency_click_count.get())
            self._update_emergency_clicks_display()
        except Exception as e:
            self.logger.error(f"Failed to update emergency config: {e}")
    
    def _record_emergency_clicks(self):
        """Record emergency click locations"""
        try:
            click_count = self.emergency_click_count.get()
            if click_count < 1:
                messagebox.showwarning("Invalid Count", "Please set at least 1 emergency click.")
                return
            
            # Show instructions
            messagebox.showinfo("Record Emergency Clicks", 
                              f"Click {click_count} location(s) on the screen where emergency actions should happen.\n\n"
                              f"Click in the order you want them to be executed.")
            
            # Start click recording
            self._start_emergency_click_recording(click_count)
            
        except Exception as e:
            self.logger.error(f"Failed to start emergency click recording: {e}")
            messagebox.showerror("Error", f"Failed to start recording: {e}")
    
    def _start_emergency_click_recording(self, click_count: int):
        """Start recording emergency click locations"""
        try:
            from gui.region_selector import ClickRecorder
            
            # Create click recorder
            self.click_recorder = ClickRecorder(click_count, self._on_emergency_clicks_recorded)
            self.click_recorder.start_recording()
            
            # Update button state
            self.record_emergency_button.config(text="Recording...", state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Failed to start click recording: {e}")
            messagebox.showerror("Error", f"Failed to start recording: {e}")
    
    def _on_emergency_clicks_recorded(self, click_locations: list):
        """Callback when emergency clicks are recorded"""
        try:
            # Save click locations to config
            self.config_manager.set('automation.health_monitoring.emergency_clicks', click_locations)
            
            # Update display
            self._update_emergency_clicks_display()
            
            # Reset button
            self.record_emergency_button.config(text="Record Emergency Clicks", state=tk.NORMAL)
            
            self.logger.info(f"Recorded {len(click_locations)} emergency click locations")
            
        except Exception as e:
            self.logger.error(f"Failed to save emergency clicks: {e}")
            self.record_emergency_button.config(text="Record Emergency Clicks", state=tk.NORMAL)
    
    def _update_emergency_clicks_display(self):
        """Update the display of recorded emergency clicks"""
        try:
            click_locations = self.config_manager.get('automation.health_monitoring.emergency_clicks', [])
            if click_locations:
                self.emergency_clicks_label.config(text=f"Recorded {len(click_locations)} emergency clicks")
            else:
                self.emergency_clicks_label.config(text="No emergency clicks recorded")
        except Exception as e:
            self.logger.error(f"Failed to update emergency clicks display: {e}")
    
    def _create_config_tab(self):
        """Create configuration tab"""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configuration")
        
        # Create scrollable frame
        canvas = tk.Canvas(config_frame)
        scrollbar = ttk.Scrollbar(config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Rune Creation Configuration
        rune_config_frame = ttk.LabelFrame(scrollable_frame, text="Rune Creation")
        rune_config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Rune Target Positions
        ttk.Label(rune_config_frame, text="Rune Target Positions:").pack(anchor=tk.W, padx=5)
        self.rune_positions_display = tk.StringVar()
        self._update_rune_positions_display()
        ttk.Label(rune_config_frame, textvariable=self.rune_positions_display, font=('Arial', 9)).pack(anchor=tk.W, padx=5)
        
        # Rune position buttons
        rune_pos_frame = ttk.Frame(rune_config_frame)
        rune_pos_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(rune_pos_frame, text="Record Rune Positions", 
                  command=self._record_rune_positions).pack(side=tk.LEFT, padx=2)
        ttk.Button(rune_pos_frame, text="Clear All Positions", 
                  command=self._clear_rune_positions).pack(side=tk.LEFT, padx=2)
        
        # Rune creation hotkey
        hotkey_frame = ttk.Frame(rune_config_frame)
        hotkey_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(hotkey_frame, text="Creation Hotkey:").pack(side=tk.LEFT, padx=5)
        self.rune_hotkey = tk.StringVar()
        self.rune_hotkey.set(self.config_manager.get('automation.rune_creation.hotkey', 'f6'))
        ttk.Entry(hotkey_frame, textvariable=self.rune_hotkey, width=10).pack(side=tk.LEFT, padx=5)
        
        # Delay range for rune creation
        delay_range_frame = ttk.Frame(rune_config_frame)
        delay_range_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(delay_range_frame, text="Delay Range (minutes):").pack(side=tk.LEFT, padx=5)
        self.rune_min_delay = tk.StringVar()
        self.rune_min_delay.set(str(self.config_manager.get('automation.rune_creation.min_delay_minutes', 2.0)))
        ttk.Entry(delay_range_frame, textvariable=self.rune_min_delay, width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(delay_range_frame, text="to").pack(side=tk.LEFT, padx=2)
        self.rune_max_delay = tk.StringVar()
        self.rune_max_delay.set(str(self.config_manager.get('automation.rune_creation.max_delay_minutes', 5.0)))
        ttk.Entry(delay_range_frame, textvariable=self.rune_max_delay, width=8).pack(side=tk.LEFT, padx=2)
        
        # Rune search region
        search_region_frame = ttk.Frame(rune_config_frame)
        search_region_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_region_frame, text="Blank Rune Search Region:").pack(anchor=tk.W, padx=5)
        self.rune_search_region_display = tk.StringVar()
        self._update_rune_search_region_display()
        ttk.Label(search_region_frame, textvariable=self.rune_search_region_display, font=('Arial', 9)).pack(anchor=tk.W, padx=5)
        
        # Search region buttons
        search_region_buttons = ttk.Frame(search_region_frame)
        search_region_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(search_region_buttons, text="Select Search Region", 
                  command=self._select_rune_search_region).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_region_buttons, text="Test Detection (PageUp)", 
                  command=self._test_rune_detection).pack(side=tk.LEFT, padx=2)
        
        # Food Eating Configuration
        food_config_frame = ttk.LabelFrame(scrollable_frame, text="Food Eating")
        food_config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Food Positions
        ttk.Label(food_config_frame, text="Food Positions:").pack(anchor=tk.W, padx=5)
        self.food_positions_display = tk.StringVar()
        self._update_food_positions_display()
        ttk.Label(food_config_frame, textvariable=self.food_positions_display, font=('Arial', 9)).pack(anchor=tk.W, padx=5)
        
        # Food position buttons
        food_pos_frame = ttk.Frame(food_config_frame)
        food_pos_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(food_pos_frame, text="Record Food Position", 
                  command=self._record_food_position).pack(side=tk.LEFT, padx=2)
        ttk.Button(food_pos_frame, text="Clear All Positions", 
                  command=self._clear_food_positions).pack(side=tk.LEFT, padx=2)
        
        # Click count range
        click_range_frame = ttk.Frame(food_config_frame)
        click_range_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(click_range_frame, text="Click Count Range:").pack(anchor=tk.W)
        click_input_frame = ttk.Frame(click_range_frame)
        click_input_frame.pack(anchor=tk.W, pady=2)
        
        ttk.Label(click_input_frame, text="Min:").pack(side=tk.LEFT)
        self.food_min_clicks = tk.StringVar()
        self.food_min_clicks.set(str(self.config_manager.get('automation.food_eating.min_clicks', 3)))
        ttk.Entry(click_input_frame, textvariable=self.food_min_clicks, width=5).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(click_input_frame, text="Max:").pack(side=tk.LEFT, padx=(10, 0))
        self.food_max_clicks = tk.StringVar()
        self.food_max_clicks.set(str(self.config_manager.get('automation.food_eating.max_clicks', 6)))
        ttk.Entry(click_input_frame, textvariable=self.food_max_clicks, width=5).pack(side=tk.LEFT, padx=2)
        
        # Delay range
        delay_range_frame = ttk.Frame(food_config_frame)
        delay_range_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(delay_range_frame, text="Delay Range (minutes):").pack(anchor=tk.W)
        delay_input_frame = ttk.Frame(delay_range_frame)
        delay_input_frame.pack(anchor=tk.W, pady=2)
        
        ttk.Label(delay_input_frame, text="Min:").pack(side=tk.LEFT)
        self.food_min_delay = tk.StringVar()
        self.food_min_delay.set(str(self.config_manager.get('automation.food_eating.min_delay_minutes', 4)))
        ttk.Entry(delay_input_frame, textvariable=self.food_min_delay, width=5).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(delay_input_frame, text="Max:").pack(side=tk.LEFT, padx=(10, 0))
        self.food_max_delay = tk.StringVar()
        self.food_max_delay.set(str(self.config_manager.get('automation.food_eating.max_delay_minutes', 8)))
        ttk.Entry(delay_input_frame, textvariable=self.food_max_delay, width=5).pack(side=tk.LEFT, padx=2)
        
        # Manual cooldown (for manual triggers)
        ttk.Label(food_config_frame, text="Manual Cooldown (seconds):").pack(anchor=tk.W, padx=5)
        self.food_cooldown = tk.StringVar()
        self.food_cooldown.set(str(self.config_manager.get('automation.food_eating.cooldown_seconds', 5)))
        ttk.Entry(food_config_frame, textvariable=self.food_cooldown, width=10).pack(anchor=tk.W, padx=5)
        
        # Health Monitoring Configuration
        health_config_frame = ttk.LabelFrame(scrollable_frame, text="Health Monitoring")
        health_config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(health_config_frame, text="Low Health Threshold (%):").pack(anchor=tk.W, padx=5)
        self.health_threshold = tk.StringVar()
        self.health_threshold.set(str(int(self.config_manager.get('automation.health_monitoring.low_health_threshold', 0.3) * 100)))
        ttk.Entry(health_config_frame, textvariable=self.health_threshold, width=10).pack(anchor=tk.W, padx=5)
        
        
        # Health Bar Region Selection
        region_frame = ttk.Frame(health_config_frame)
        region_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(region_frame, text="Health Bar Region:").pack(anchor=tk.W)
        
        # Current region display
        self.health_region_display = tk.StringVar()
        current_region = self.config_manager.get('automation.health_monitoring.health_bar_region', [50, 50, 200, 20])
        self.health_region_display.set(f"X:{current_region['x']}, Y:{current_region['y']}, W:{current_region['width']}, H:{current_region['height']}")
        ttk.Label(region_frame, textvariable=self.health_region_display, font=('Arial', 9)).pack(anchor=tk.W, pady=2)
        
        # Region selector button
        self.select_region_button = ttk.Button(region_frame, text="Select Health Bar Region", 
                                             command=self._select_health_region)
        self.select_region_button.pack(anchor=tk.W, pady=2)
        
        # Clear region button
        self.clear_region_button = ttk.Button(region_frame, text="Clear Region", 
                                            command=self._clear_health_region)
        self.clear_region_button.pack(anchor=tk.W, pady=2)
        
        # Overlay toggle
        self.show_overlay = tk.BooleanVar()
        self.show_overlay.set(True)  # Default to showing overlay
        ttk.Checkbutton(region_frame, text="Show Region Overlay", 
                       variable=self.show_overlay,
                       command=self._toggle_overlay).pack(anchor=tk.W, pady=2)
        
        # Save button
        save_button = ttk.Button(scrollable_frame, text="Save Configuration", 
                                command=self._save_config)
        save_button.pack(pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_status_tab(self):
        """Create status display tab"""
        status_frame = ttk.Frame(self.notebook)
        self.notebook.add(status_frame, text="Status")
        
        # Status display
        self.status_text = scrolledtext.ScrolledText(status_frame, height=20, width=80)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Clear button
        clear_button = ttk.Button(status_frame, text="Clear Status", 
                                 command=self._clear_status)
        clear_button.pack(pady=5)
    
    def _create_logs_tab(self):
        """Create logs display tab"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs")
        
        # Logs display
        self.logs_text = scrolledtext.ScrolledText(logs_frame, height=20, width=80)
        self.logs_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Clear button
        clear_logs_button = ttk.Button(logs_frame, text="Clear Logs", 
                                      command=self._clear_logs)
        clear_logs_button.pack(pady=5)
    
    def _create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready", style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT)
        
        self.connection_label = ttk.Label(status_frame, text="Connected", style='Success.TLabel')
        self.connection_label.pack(side=tk.RIGHT)
    
    def _setup_bindings(self):
        """Setup event bindings"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.bind('<Next>', lambda e: self._test_image_search())  # PageDown key
        self.root.bind('<Prior>', lambda e: self._test_rune_detection())  # PageUp key
        self.root.bind('<F2>', lambda e: self._test_rune_creation())  # F2 key
        self.root.bind('<F3>', lambda e: self._test_food_eating())  # F3 key
    
    def _test_image_search(self):
        """Test image search manually (PageDown key)"""
        try:
            # Get current health region
            health_region_dict = self.config_manager.get('automation.health_monitoring.health_bar_region', {'x': 50, 'y': 50, 'width': 200, 'height': 20})
            health_region = (health_region_dict['x'], health_region_dict['y'], 
                           health_region_dict['width'], health_region_dict['height'])
            
            # Test image search
            result = self.workflow_manager.state_monitor.test_image_search(
                health_region, 'health_reference.png', 0.8
            )
            
            if result['success']:
                if result['image_found']:
                    self.logger.info("PageDown test: SUCCESS, IMAGE FOUND!")
                else:
                    self.logger.warning("PageDown test: HEALTH IMAGE NOT FOUND!")
            else:
                self.logger.error(f"PageDown test failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"PageDown test error: {e}")
    
    def _test_food_eating(self):
        """Test food eating logic manually (F3 key)"""
        try:
            food_automation = self.workflow_manager.get_automation('food_eating')
            if not food_automation:
                self.logger.error("Food eating automation not available")
                return
            
            # Check if food positions are configured
            positions = food_automation.get_food_positions()
            if not positions:
                self.logger.warning("No food positions configured for test")
                return
            
            # Test the food eating sequence
            self.logger.info(f"Testing food eating logic with {len(positions)} positions...")
            
            # Execute the food eating sequence
            success = food_automation._eat_food_sequence()
            
            if success:
                self.logger.info("Food eating test completed successfully")
            else:
                self.logger.error("Food eating test failed - sequence returned False")
                
        except Exception as e:
            self.logger.error(f"Food eating test failed with exception: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _refresh_status(self):
        """Refresh status display"""
        try:
            self._update_status_display()
        except Exception as e:
            self.logger.error(f"Failed to refresh status: {e}")
    
    def _update_countdown(self):
        """Update the countdown timer for next food and rune interactions"""
        try:
            import time
            
            current_time = time.time()
            
            # Get food eating automation
            food_automation = self.workflow_manager.get_automation('food_eating')
            rune_automation = self.workflow_manager.get_automation('rune_creation')
            
            # Build countdown text for both processes
            countdown_parts = []
            overall_color = 'blue'
            
            # Food countdown
            if food_automation and food_automation.is_running:
                next_eat_time = getattr(food_automation, 'next_eat_time', 0)
                if next_eat_time > 0 and next_eat_time > current_time:
                    time_remaining = next_eat_time - current_time
                    hours = int(time_remaining // 3600)
                    minutes = int((time_remaining % 3600) // 60)
                    seconds = int(time_remaining % 60)
                    
                    if hours > 0:
                        food_text = f"Food: {hours:02d}:{minutes:02d}:{seconds:02d}"
                    else:
                        food_text = f"Food: {minutes:02d}:{seconds:02d}"
                    
                    countdown_parts.append(food_text)
                    
                    # Update overall color based on food timing
                    if time_remaining < 60:
                        overall_color = 'red'
                    elif time_remaining < 300 and overall_color != 'red':
                        overall_color = 'orange'
                else:
                    countdown_parts.append("Food: Calculating...")
                    if overall_color != 'red':
                        overall_color = 'orange'
            elif food_automation:
                countdown_parts.append("Food: Stopped")
                if overall_color != 'red':
                    overall_color = 'red'
            else:
                countdown_parts.append("Food: N/A")
                if overall_color != 'red':
                    overall_color = 'gray'
            
            # Rune countdown
            if rune_automation and rune_automation.is_running:
                next_create_time = getattr(rune_automation, 'next_create_time', 0)
                if next_create_time > 0 and next_create_time > current_time:
                    time_remaining = next_create_time - current_time
                    hours = int(time_remaining // 3600)
                    minutes = int((time_remaining % 3600) // 60)
                    seconds = int(time_remaining % 60)
                    
                    if hours > 0:
                        rune_text = f"Rune: {hours:02d}:{minutes:02d}:{seconds:02d}"
                    else:
                        rune_text = f"Rune: {minutes:02d}:{seconds:02d}"
                    
                    countdown_parts.append(rune_text)
                    
                    # Update overall color based on rune timing (most urgent)
                    if time_remaining < 60:
                        overall_color = 'red'
                    elif time_remaining < 300 and overall_color not in ['red']:
                        overall_color = 'orange'
                else:
                    countdown_parts.append("Rune: Calculating...")
                    if overall_color not in ['red']:
                        overall_color = 'orange'
            elif rune_automation:
                countdown_parts.append("Rune: Stopped")
                if overall_color not in ['red']:
                    overall_color = 'red'
            else:
                countdown_parts.append("Rune: N/A")
                if overall_color not in ['red', 'orange']:
                    overall_color = 'gray'
            
            # Combine countdown text
            if countdown_parts:
                countdown_text = " | ".join(countdown_parts)
            else:
                countdown_text = "No automations available"
                overall_color = 'gray'
            
            # Update the label
            self.countdown_label.config(text=countdown_text, foreground=overall_color)
            
            # Schedule next update
            self.root.after(1000, self._update_countdown)
            
        except Exception as e:
            self.logger.error(f"Failed to update countdown: {e}")
            # Schedule next update even if there's an error
            self.root.after(1000, self._update_countdown)
    
    def _update_automation_config(self, automation: str, key: str, value: Any):
        """Update automation configuration"""
        try:
            self.config_manager.set(f'automation.{automation}.{key}', value)
            self.logger.info(f"Updated {automation}.{key} = {value}")
        except Exception as e:
            self.logger.error(f"Failed to update automation config: {e}")
    
    def _save_config(self):
        """Save current configuration"""
        try:
            # Update configuration values
            self.config_manager.set('automation.rune_creation.hotkey', self.rune_hotkey.get())
            self.config_manager.set('automation.rune_creation.min_delay_minutes', float(self.rune_min_delay.get()))
            self.config_manager.set('automation.rune_creation.max_delay_minutes', float(self.rune_max_delay.get()))
            self.config_manager.set('automation.food_eating.cooldown_seconds', int(self.food_cooldown.get()))
            self.config_manager.set('automation.food_eating.min_clicks', int(self.food_min_clicks.get()))
            self.config_manager.set('automation.food_eating.max_clicks', int(self.food_max_clicks.get()))
            self.config_manager.set('automation.food_eating.min_delay_minutes', float(self.food_min_delay.get()))
            self.config_manager.set('automation.food_eating.max_delay_minutes', float(self.food_max_delay.get()))
            self.config_manager.set('automation.health_monitoring.low_health_threshold', 
                                  int(self.health_threshold.get()) / 100)
            
            # Save to file
            self.config_manager.save_config()
            
            messagebox.showinfo("Configuration Saved", "Configuration has been saved successfully.")
            self.logger.info("Configuration saved")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            messagebox.showerror("Save Failed", f"Failed to save configuration: {e}")
    
    def _log_status(self, message: str):
        """Log status message"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
    
    def _clear_status(self):
        """Clear status display"""
        self.status_text.delete(1.0, tk.END)
    
    def _clear_logs(self):
        """Clear logs display"""
        self.logs_text.delete(1.0, tk.END)
    
    def _update_status_display(self):
        """Update status display with current information"""
        try:
            # Clear and update status
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, "=== AUTOMATION STATUS ===\n\n")
            
            # Show main system status
            self.status_text.insert(tk.END, f"System Status: {'Running' if self.is_running else 'Stopped'}\n\n")
            
            # Show individual automation status
            self.status_text.insert(tk.END, "Individual Automations:\n")
            self.status_text.insert(tk.END, f"  Rune Maker: {'Enabled' if self.rune_enabled.get() else 'Disabled'}\n")
            self.status_text.insert(tk.END, f"  Food: {'Enabled' if self.food_enabled.get() else 'Disabled'}\n")
            self.status_text.insert(tk.END, f"  Health Monitoring: {'Enabled' if self.health_enabled.get() else 'Disabled'}\n")
            
        except Exception as e:
            self.logger.error(f"Failed to update status display: {e}")
    
    def _start_status_updates(self):
        """Start periodic status updates"""
        def update_loop():
            while True:
                try:
                    if self.is_running:
                        self.root.after(0, self._update_status_display)
                    time.sleep(2)  # Update every 2 seconds
                except Exception as e:
                    self.logger.error(f"Status update error: {e}")
                    break
        
        self.status_update_thread = threading.Thread(target=update_loop, daemon=True)
        self.status_update_thread.start()
    
    def _select_health_region(self):
        """Open region selector for health bar"""
        try:
            # Hide main window temporarily
            self.root.withdraw()
            
            # Create region selector
            from gui.region_selector import RegionSelector
            selector = RegionSelector(self.root, self._on_region_selected, self._on_region_cancelled)
            
        except Exception as e:
            self.logger.error(f"Failed to open region selector: {e}")
            messagebox.showerror("Error", f"Failed to open region selector: {e}")
            self.root.deiconify()
    
    def _on_region_selected(self, x, y, width, height):
        """Handle region selection result"""
        try:
            # Update configuration
            region = {"x": x, "y": y, "width": width, "height": height}
            self.config_manager.set('automation.health_monitoring.health_bar_region', region)
            
            # Update display
            self.health_region_display.set(f"X:{x}, Y:{y}, W:{width}, H:{height}")
            
            # Create persistent overlay immediately
            self._create_persistent_overlay(x, y, width, height)
            
            # Show main window
            self.root.deiconify()
            
            self.logger.info(f"Health region selected: {region}")
            messagebox.showinfo("Region Selected", f"Health bar region set to: X:{x}, Y:{y}, W:{width}, H:{height}")
            
        except Exception as e:
            self.logger.error(f"Failed to save region: {e}")
            messagebox.showerror("Error", f"Failed to save region: {e}")
            self.root.deiconify()
    
    def _on_region_cancelled(self):
        """Handle region selection cancellation"""
        self.root.deiconify()
        self.logger.info("Region selection cancelled")
    
    def _clear_health_region(self):
        """Clear the health region selection"""
        try:
            # Reset to default region
            default_region = {"x": 50, "y": 50, "width": 200, "height": 20}
            self.config_manager.set('automation.health_monitoring.health_bar_region', default_region)
            
            # Update display
            self.health_region_display.set(f"X:{default_region['x']}, Y:{default_region['y']}, W:{default_region['width']}, H:{default_region['height']}")
            
            # Update persistent overlay
            self._create_persistent_overlay(
                default_region['x'], default_region['y'], 
                default_region['width'], default_region['height']
            )
            
            self.logger.info("Health region cleared and reset to default")
            messagebox.showinfo("Region Cleared", "Health region has been reset to default values")
            
        except Exception as e:
            self.logger.error(f"Failed to clear region: {e}")
            messagebox.showerror("Error", f"Failed to clear region: {e}")
    
    def _toggle_overlay(self):
        """Toggle region overlay visibility"""
        try:
            if self.show_overlay.get():
                # Show overlay - create it if it doesn't exist
                if not self.persistent_overlay:
                    # Get current region from config
                    current_region = self.config_manager.get('automation.health_monitoring.health_bar_region', [50, 50, 200, 20])
                    self._create_persistent_overlay(
                        current_region['x'], current_region['y'],
                        current_region['width'], current_region['height']
                    )
            else:
                # Hide overlay
                if self.persistent_overlay:
                    self.persistent_overlay.destroy()
                    self.persistent_overlay = None
            
            # Also update health monitoring automation if it exists
            health_automation = self.workflow_manager.get_automation('health_monitor')
            if health_automation:
                health_automation.toggle_overlay(self.show_overlay.get())
            
            self.logger.info(f"Overlay visibility toggled: {self.show_overlay.get()}")
        except Exception as e:
            self.logger.error(f"Failed to toggle overlay: {e}")
    
    def _create_persistent_overlay(self, x, y, width, height):
        """Create persistent overlay for region visualization"""
        try:
            # Destroy existing overlay if any
            if self.persistent_overlay:
                self.persistent_overlay.destroy()
            
            # Import here to avoid circular imports
            from gui.region_selector import RegionOverlay
            
            # Create new overlay
            self.persistent_overlay = RegionOverlay(
                x, y, width, height, is_active=False  # Start as inactive (red)
            )
            
            self.logger.info(f"Persistent overlay created at ({x}, {y}) - {width}x{height}")
            
        except Exception as e:
            self.logger.error(f"Failed to create persistent overlay: {e}")
            self.persistent_overlay = None
    
    def _create_rune_persistent_overlay(self, x, y, width, height):
        """Create persistent overlay for rune search region visualization"""
        try:
            # Destroy existing overlay if any
            if self.rune_persistent_overlay:
                self.rune_persistent_overlay.destroy()
            
            # Import here to avoid circular imports
            from gui.region_selector import RegionOverlay
            
            # Create new overlay with cyan color for rune search region
            self.rune_persistent_overlay = RegionOverlay(
                x, y, width, height, is_active=False, color='cyan'  # Start as inactive (cyan)
            )
            self.logger.info(f"Rune persistent overlay created at ({x}, {y}) - {width}x{height}")
            
        except Exception as e:
            self.logger.error(f"Failed to create rune persistent overlay: {e}")
            self.rune_persistent_overlay = None
    
    def _update_persistent_overlay_status(self, is_active):
        """Update persistent overlay status"""
        if self.persistent_overlay:
            self.persistent_overlay.update_status(is_active)
    
    def _on_health_monitoring_event(self, automation_name, event, *args):
        """Handle health monitoring automation events"""
        try:
            if event == 'started':
                self.logger.info("Health monitoring started - updating overlay to green")
                self._update_persistent_overlay_status(True)
            elif event == 'stopped':
                self.logger.info("Health monitoring stopped - updating overlay to yellow")
                self._update_persistent_overlay_status(False)
            elif event == 'error':
                self.logger.error(f"Health monitoring error: {args[0] if args else 'Unknown error'}")
                self._update_persistent_overlay_status(False)
        except Exception as e:
            self.logger.error(f"Error handling health monitoring event: {e}")
    
    def _on_emergency_stop(self):
        """Handle emergency stop - stop all automations and update UI"""
        try:
            self.logger.warning("Emergency stop triggered - stopping all automations")
            
            # Stop all automations
            self.workflow_manager.stop_all_workflows()
            
            # Update UI to show stopped state
            self.is_running = False
            self.active_button.config(text="ACTIVE", style='Active.TButton')
            self.status_label.config(text="Emergency Stop")
            self._log_status("Automation stopped due to emergency")
            
            # Show emergency notification
            messagebox.showwarning("Emergency Stop", 
                                 "Health emergency detected!\n\n"
                                 "Emergency actions have been executed.\n"
                                 "Automation has been stopped.\n\n"
                                 "Click ACTIVE to restart when ready.")
            
        except Exception as e:
            self.logger.error(f"Failed to handle emergency stop: {e}")

    def _on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            try:
                # Stop all workflows
                self.workflow_manager.stop_all_workflows()
                
                # Destroy persistent overlays
                if self.persistent_overlay:
                    self.persistent_overlay.destroy()
                if self.rune_persistent_overlay:
                    self.rune_persistent_overlay.destroy()
                
                # Save configuration
                self._save_config()
                
                self.logger.info("Application closing")
                self.root.destroy()
                
            except Exception as e:
                self.logger.error(f"Error during shutdown: {e}")
                self.root.destroy()
    
    def _update_food_positions_display(self):
        """Update the food positions display"""
        try:
            food_automation = self.workflow_manager.get_automation('food_eating')
            if food_automation:
                positions = food_automation.get_food_positions()
                self.logger.info(f"Updating food positions display. Current positions: {positions}")
                if positions:
                    pos_str = ", ".join([f"({x}, {y})" for x, y in positions])
                    display_text = f"Positions: {pos_str} ({len(positions)}/3)"
                    self.food_positions_display.set(display_text)
                    self.logger.info(f"Updated display to: {display_text}")
                else:
                    self.food_positions_display.set("No positions configured (0/3)")
                    self.logger.info("Updated display to: No positions configured (0/3)")
            else:
                self.food_positions_display.set("Food automation not available")
                self.logger.warning("Food automation not available for display update")
        except Exception as e:
            self.logger.error(f"Failed to update food positions display: {e}")
            self.food_positions_display.set("Error loading positions")
    
    def _record_food_position(self):
        """Record 3 food positions by clicking on the screen"""
        try:
            food_automation = self.workflow_manager.get_automation('food_eating')
            if not food_automation:
                self.logger.error("Food eating automation not available")
                return
            
            # Start position recording directly (no popup)
            self.logger.info("Starting food position recording...")
            self._start_food_position_recording()
            
        except Exception as e:
            self.logger.error(f"Failed to start food position recording: {e}")
    
    def _start_food_position_recording(self):
        """Start recording a food position"""
        try:
            from gui.region_selector import FoodPositionRecorder
            
            # Create a simple food position recorder
            self.food_position_recorder = FoodPositionRecorder(self._on_food_position_recorded)
            self.food_position_recorder.start_recording()
            
        except Exception as e:
            self.logger.error(f"Failed to start food position recording: {e}")
            messagebox.showerror("Error", f"Failed to start recording: {e}")
    
    def _on_food_position_recorded(self, positions):
        """Handle food position recording completion"""
        try:
            self.logger.info(f"Food position recording callback received: {positions}")
            
            if not positions:
                self.logger.warning("No food positions were recorded (empty or cancelled)")
                return
            
            # Clear existing positions and add all new ones
            food_automation = self.workflow_manager.get_automation('food_eating')
            if food_automation:
                # Clear existing positions
                food_automation.clear_food_positions()
                
                # Add all recorded positions
                success_count = 0
                for i, (x, y) in enumerate(positions):
                    self.logger.info(f"Adding food position {i+1}: ({x}, {y})")
                    if food_automation.add_food_position(x, y):
                        success_count += 1
                        self.logger.info(f"Successfully added food position {i+1}: ({x}, {y})")
                    else:
                        self.logger.warning(f"Failed to add food position {i+1}: ({x}, {y})")
                
                # Update display
                self._update_food_positions_display()
                
                if success_count == len(positions):
                    messagebox.showinfo("Positions Added", f"Successfully added {success_count} food positions!")
                else:
                    messagebox.showwarning("Partial Success", f"Added {success_count} out of {len(positions)} food positions.")
            else:
                self.logger.error("Food eating automation not available")
                messagebox.showerror("Error", "Food eating automation not available")
                
        except Exception as e:
            self.logger.error(f"Failed to process recorded food positions: {e}")
            messagebox.showerror("Error", f"Failed to process positions: {e}")
    
    def _clear_food_positions(self):
        """Clear all food positions"""
        try:
            result = messagebox.askyesno("Clear Food Positions", 
                                       "Are you sure you want to clear all food positions?")
            if result:
                food_automation = self.workflow_manager.get_automation('food_eating')
                if food_automation:
                    food_automation.clear_food_positions()
                    self._update_food_positions_display()
                    messagebox.showinfo("Positions Cleared", "All food positions have been cleared.")
                else:
                    messagebox.showerror("Error", "Food eating automation not available")
                    
        except Exception as e:
            self.logger.error(f"Failed to clear food positions: {e}")
            messagebox.showerror("Error", f"Failed to clear positions: {e}")
    
    def _update_rune_positions_display(self):
        """Update the rune positions display"""
        try:
            rune_automation = self.workflow_manager.get_automation('rune_creation')
            if rune_automation:
                positions = rune_automation.get_rune_positions()
                self.logger.info(f"Updating rune positions display. Current positions: {positions}")
                if positions:
                    pos_str = ", ".join([f"({x}, {y})" for x, y in positions])
                    display_text = f"Positions: {pos_str} ({len(positions)}/3)"
                    self.rune_positions_display.set(display_text)
                    self.logger.info(f"Updated display to: {display_text}")
                else:
                    self.rune_positions_display.set("No positions configured (0/3)")
                    self.logger.info("Updated display to: No positions configured (0/3)")
            else:
                self.rune_positions_display.set("Rune automation not available")
                self.logger.warning("Rune automation not available for display update")
        except Exception as e:
            self.logger.error(f"Failed to update rune positions display: {e}")
            self.rune_positions_display.set("Error loading positions")
    
    def _record_rune_positions(self):
        """Record 3 rune target positions by clicking on the screen"""
        try:
            rune_automation = self.workflow_manager.get_automation('rune_creation')
            if not rune_automation:
                self.logger.error("Rune creation automation not available")
                return
            
            # Start position recording directly (no popup)
            self.logger.info("Starting rune position recording...")
            self._start_rune_position_recording()
            
        except Exception as e:
            self.logger.error(f"Failed to start rune position recording: {e}")
    
    def _start_rune_position_recording(self):
        """Start recording rune target positions"""
        try:
            from gui.region_selector import RunePositionRecorder
            
            # Create a rune position recorder
            self.rune_position_recorder = RunePositionRecorder(self._on_rune_position_recorded)
            self.rune_position_recorder.start_recording()
            
        except Exception as e:
            self.logger.error(f"Failed to start rune position recording: {e}")
            messagebox.showerror("Error", f"Failed to start recording: {e}")
    
    def _on_rune_position_recorded(self, positions):
        """Handle rune position recording completion"""
        try:
            self.logger.info(f"Rune position recording callback received: {positions}")
            
            if not positions:
                self.logger.warning("No rune positions were recorded (empty or cancelled)")
                return
            
            # Clear existing positions and add all new ones
            rune_automation = self.workflow_manager.get_automation('rune_creation')
            if rune_automation:
                # Clear existing positions
                rune_automation.clear_rune_positions()
                
                # Add all recorded positions
                success_count = 0
                for i, (x, y) in enumerate(positions):
                    self.logger.info(f"Adding rune position {i+1}: ({x}, {y})")
                    if rune_automation.add_rune_position(x, y):
                        success_count += 1
                        self.logger.info(f"Successfully added rune position {i+1}: ({x}, {y})")
                    else:
                        self.logger.warning(f"Failed to add rune position {i+1}: ({x}, {y})")
                
                # Update display
                self._update_rune_positions_display()
                
                if success_count == len(positions):
                    messagebox.showinfo("Positions Added", f"Successfully added {success_count} rune target positions!")
                else:
                    messagebox.showwarning("Partial Success", f"Added {success_count} out of {len(positions)} rune positions.")
            else:
                self.logger.error("Rune creation automation not available")
                messagebox.showerror("Error", "Rune creation automation not available")
                
        except Exception as e:
            self.logger.error(f"Failed to process recorded rune positions: {e}")
            messagebox.showerror("Error", f"Failed to process positions: {e}")
    
    def _clear_rune_positions(self):
        """Clear all rune positions"""
        try:
            result = messagebox.askyesno("Clear Rune Positions", 
                                       "Are you sure you want to clear all rune target positions?")
            if result:
                rune_automation = self.workflow_manager.get_automation('rune_creation')
                if rune_automation:
                    rune_automation.clear_rune_positions()
                    self._update_rune_positions_display()
                    messagebox.showinfo("Cleared", "All rune target positions have been cleared.")
                else:
                    messagebox.showerror("Error", "Rune creation automation not available")
        except Exception as e:
            self.logger.error(f"Failed to clear rune positions: {e}")
            messagebox.showerror("Error", f"Failed to clear positions: {e}")
    
    def _test_rune_creation(self):
        """Test rune creation logic manually (F2 key)"""
        try:
            rune_automation = self.workflow_manager.get_automation('rune_creation')
            if not rune_automation:
                self.logger.error("Rune creation automation not available")
                return
            
            # Check if rune positions are configured
            positions = rune_automation.get_rune_positions()
            if not positions:
                self.logger.warning("No rune positions configured for test")
                return
            
            # Test the rune creation sequence
            self.logger.info(f"Testing rune creation logic with {len(positions)} positions...")
            
            # Execute the rune creation sequence
            success = rune_automation._create_rune_sequence()
            
            if success:
                self.logger.info("Rune creation test completed successfully")
            else:
                self.logger.error("Rune creation test failed - sequence returned False")
                
        except Exception as e:
            self.logger.error(f"Rune creation test failed with exception: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _update_rune_search_region_display(self):
        """Update the rune search region display"""
        try:
            region_dict = self.config_manager.get('automation.rune_creation.search_region', {})
            if region_dict and all(key in region_dict for key in ['x', 'y', 'width', 'height']):
                x, y, w, h = region_dict['x'], region_dict['y'], region_dict['width'], region_dict['height']
                display_text = f"Region: ({x}, {y}) - {w}x{h}"
                self.rune_search_region_display.set(display_text)
                self.logger.info(f"Updated rune search region display: {display_text}")
            else:
                self.rune_search_region_display.set("No search region configured")
                self.logger.info("Updated rune search region display: No region configured")
        except Exception as e:
            self.logger.error(f"Failed to update rune search region display: {e}")
            self.rune_search_region_display.set("Error loading region")
    
    def _select_rune_search_region(self):
        """Select search region for blank rune detection"""
        try:
            from gui.region_selector import RegionSelector
            
            # Create region selector with both callbacks
            selector = RegionSelector(self.root, self._on_rune_search_region_selected, self._on_rune_search_region_cancelled)
            
        except Exception as e:
            self.logger.error(f"Failed to start rune search region selection: {e}")
            messagebox.showerror("Error", f"Failed to start region selection: {e}")
    
    def _on_rune_search_region_selected(self, x, y, width, height):
        """Handle rune search region selection"""
        try:
            self.logger.info(f"Rune search region selected: ({x}, {y}) - {width}x{height}")
            
            # Save to configuration
            region_dict = {'x': x, 'y': y, 'width': width, 'height': height}
            self.config_manager.set('automation.rune_creation.search_region', region_dict)
            
            # Update display
            self._update_rune_search_region_display()
            
            # Create persistent overlay for the rune search region
            self._create_rune_persistent_overlay(x, y, width, height)
            
            messagebox.showinfo("Region Selected", 
                              f"Rune search region set to:\n"
                              f"Position: ({x}, {y})\n"
                              f"Size: {width}x{height}")
                
        except Exception as e:
            self.logger.error(f"Failed to process rune search region selection: {e}")
            messagebox.showerror("Error", f"Failed to save region: {e}")
    
    def _on_rune_search_region_cancelled(self):
        """Handle rune search region selection cancellation"""
        self.logger.info("Rune search region selection cancelled")
    
    def _test_rune_detection(self):
        """Test blank rune detection manually (PageUp key)"""
        try:
            self.logger.info("Testing blank rune detection...")
            
            # Get rune creation automation
            rune_automation = self.workflow_manager.get_automation('rune_creation')
            if not rune_automation:
                self.logger.error("Rune creation automation not available")
                return
            
            # Test the blank rune detection
            blank_rune_location = rune_automation._find_blank_rune()
            
            if blank_rune_location:
                x, y = blank_rune_location
                self.logger.info(f"SUCCESS: BLANK IMAGE FOUND at ({x}, {y})")
                messagebox.showinfo("Detection Test", 
                                  f"SUCCESS: BLANK IMAGE FOUND\n"
                                  f"Location: ({x}, {y})")
            else:
                self.logger.warning("ERROR: BLANK IMAGE NOT FOUND")
                messagebox.showwarning("Detection Test", 
                                     "ERROR: BLANK IMAGE NOT FOUND\n"
                                     "Check if:\n"
                                     "• Search region is configured\n"
                                     "• Blank rune is visible in the region\n"
                                     "• blank.png image file exists")
                
        except Exception as e:
            self.logger.error(f"Rune detection test failed: {e}")
            messagebox.showerror("Test Failed", f"Detection test failed: {e}")
