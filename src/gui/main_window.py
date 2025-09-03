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
        
        # Setup window
        self._setup_window()
        self._create_widgets()
        self._setup_bindings()
        self._start_status_updates()
        
        self.logger.info("Main window initialized")
    
    def _setup_window(self):
        """Setup main window properties"""
        self.root.title("Cyclops - Desktop Automation System")
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
        
        # Workflow selection
        ttk.Label(control_frame, text="Select Workflow:").pack(anchor=tk.W, padx=5, pady=5)
        
        self.workflow_var = tk.StringVar()
        self.workflow_combo = ttk.Combobox(control_frame, textvariable=self.workflow_var, 
                                          state='readonly', width=30)
        self.workflow_combo.pack(anchor=tk.W, padx=5, pady=5)
        self._update_workflow_list()
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Workflow", 
                                      command=self._start_workflow)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Workflow", 
                                     command=self._stop_workflow, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.refresh_button = ttk.Button(button_frame, text="Refresh", 
                                        command=self._refresh_status)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Individual automation controls
        auto_frame = ttk.LabelFrame(automation_frame, text="Individual Automations")
        auto_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self._create_automation_controls(auto_frame)
    
    def _create_automation_controls(self, parent):
        """Create controls for individual automations"""
        # Rune Creation
        rune_frame = ttk.LabelFrame(parent, text="Rune Creation")
        rune_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.rune_enabled = tk.BooleanVar()
        self.rune_enabled.set(self.config_manager.get('automation.rune_creation.enabled', False))
        ttk.Checkbutton(rune_frame, text="Enable Rune Creation", 
                       variable=self.rune_enabled,
                       command=lambda: self._update_automation_config('rune_creation', 'enabled', self.rune_enabled.get())).pack(anchor=tk.W, padx=5)
        
        # Food Eating
        food_frame = ttk.LabelFrame(parent, text="Food Eating")
        food_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.food_enabled = tk.BooleanVar()
        self.food_enabled.set(self.config_manager.get('automation.food_eating.enabled', False))
        ttk.Checkbutton(food_frame, text="Enable Food Eating", 
                       variable=self.food_enabled,
                       command=lambda: self._update_automation_config('food_eating', 'enabled', self.food_enabled.get())).pack(anchor=tk.W, padx=5)
        
        # Health Monitoring
        health_frame = ttk.LabelFrame(parent, text="Health Monitoring")
        health_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.health_enabled = tk.BooleanVar()
        self.health_enabled.set(self.config_manager.get('automation.health_monitoring.enabled', False))
        ttk.Checkbutton(health_frame, text="Enable Health Monitoring", 
                       variable=self.health_enabled,
                       command=lambda: self._update_automation_config('health_monitoring', 'enabled', self.health_enabled.get())).pack(anchor=tk.W, padx=5)
    
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
        
        ttk.Label(rune_config_frame, text="Hotkey:").pack(anchor=tk.W, padx=5)
        self.rune_hotkey = tk.StringVar()
        self.rune_hotkey.set(self.config_manager.get('automation.rune_creation.hotkey', 'f1'))
        ttk.Entry(rune_config_frame, textvariable=self.rune_hotkey, width=10).pack(anchor=tk.W, padx=5)
        
        # Food Eating Configuration
        food_config_frame = ttk.LabelFrame(scrollable_frame, text="Food Eating")
        food_config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(food_config_frame, text="Cooldown (seconds):").pack(anchor=tk.W, padx=5)
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
        
        ttk.Label(health_config_frame, text="Emergency Hotkey:").pack(anchor=tk.W, padx=5)
        self.health_hotkey = tk.StringVar()
        self.health_hotkey.set(self.config_manager.get('automation.health_monitoring.emergency_hotkey', 'f2'))
        ttk.Entry(health_config_frame, textvariable=self.health_hotkey, width=10).pack(anchor=tk.W, padx=5)
        
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
    
    def _start_workflow(self):
        """Start selected workflow"""
        workflow_name = self.workflow_var.get()
        if not workflow_name:
            messagebox.showwarning("No Workflow Selected", "Please select a workflow to start.")
            return
        
        try:
            self.logger.info(f"Starting workflow: {workflow_name}")
            success = self.workflow_manager.start_workflow(workflow_name)
            
            if success:
                self.is_running = True
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                self.status_label.config(text=f"Running: {workflow_name}")
                self._log_status(f"Started workflow: {workflow_name}")
            else:
                messagebox.showerror("Start Failed", f"Failed to start workflow: {workflow_name}")
                
        except Exception as e:
            self.logger.error(f"Failed to start workflow: {e}")
            messagebox.showerror("Error", f"Failed to start workflow: {e}")
    
    def _stop_workflow(self):
        """Stop current workflow"""
        workflow_name = self.workflow_var.get()
        if not workflow_name:
            return
        
        try:
            self.logger.info(f"Stopping workflow: {workflow_name}")
            success = self.workflow_manager.stop_workflow(workflow_name)
            
            if success:
                self.is_running = False
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
                self.status_label.config(text="Stopped")
                self._log_status(f"Stopped workflow: {workflow_name}")
            else:
                messagebox.showerror("Stop Failed", f"Failed to stop workflow: {workflow_name}")
                
        except Exception as e:
            self.logger.error(f"Failed to stop workflow: {e}")
            messagebox.showerror("Error", f"Failed to stop workflow: {e}")
    
    def _refresh_status(self):
        """Refresh status display"""
        try:
            self._update_status_display()
            self._update_workflow_list()
        except Exception as e:
            self.logger.error(f"Failed to refresh status: {e}")
    
    def _update_workflow_list(self):
        """Update workflow dropdown list"""
        try:
            workflows = self.workflow_manager.get_available_workflows()
            self.workflow_combo['values'] = workflows
            if workflows and not self.workflow_var.get():
                self.workflow_var.set(workflows[0])
        except Exception as e:
            self.logger.error(f"Failed to update workflow list: {e}")
    
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
            self.config_manager.set('automation.food_eating.cooldown_seconds', int(self.food_cooldown.get()))
            self.config_manager.set('automation.health_monitoring.low_health_threshold', 
                                  int(self.health_threshold.get()) / 100)
            self.config_manager.set('automation.health_monitoring.emergency_hotkey', self.health_hotkey.get())
            
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
            # Get workflow status
            workflow_status = self.workflow_manager.get_all_workflow_status()
            
            # Clear and update status
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, "=== WORKFLOW STATUS ===\n\n")
            
            for workflow_name, status in workflow_status.items():
                self.status_text.insert(tk.END, f"Workflow: {status['name']}\n")
                self.status_text.insert(tk.END, f"  Active: {status['is_active']}\n")
                self.status_text.insert(tk.END, f"  Description: {status['description']}\n")
                
                for auto_name, auto_status in status['automations'].items():
                    self.status_text.insert(tk.END, f"    {auto_name}: {auto_status.get('is_running', False)}\n")
                
                self.status_text.insert(tk.END, "\n")
            
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
    
    def _on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            try:
                # Stop all workflows
                self.workflow_manager.stop_all_workflows()
                
                # Save configuration
                self._save_config()
                
                self.logger.info("Application closing")
                self.root.destroy()
                
            except Exception as e:
                self.logger.error(f"Error during shutdown: {e}")
                self.root.destroy()
