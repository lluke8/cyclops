"""
Automation panel for Cyclops automation system.
Provides detailed control and monitoring of individual automation routines.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import threading
from typing import Dict, Any, Optional
from automation.workflow_manager import WorkflowManager

class AutomationPanel:
    """Automation panel with detailed control and monitoring"""
    
    def __init__(self, parent, workflow_manager: WorkflowManager):
        """
        Initialize automation panel
        
        Args:
            parent: Parent widget
            workflow_manager: Workflow manager instance
        """
        self.parent = parent
        self.workflow_manager = workflow_manager
        self.logger = logging.getLogger(__name__)
        
        # Automation status tracking
        self.status_labels: Dict[str, ttk.Label] = {}
        self.control_buttons: Dict[str, ttk.Button] = {}
        
        self._create_widgets()
        self._start_status_updates()
    
    def _create_widgets(self):
        """Create automation panel widgets"""
        # Create main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create title
        title_label = ttk.Label(main_frame, text="Automation Control Panel", 
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Create automation sections
        self._create_automation_sections(main_frame)
        
        # Create status summary
        self._create_status_summary(main_frame)
    
    def _create_automation_sections(self, parent):
        """Create sections for each automation"""
        # Get available automations
        automations = self.workflow_manager.get_available_automations()
        
        for automation_name in automations:
            self._create_automation_section(parent, automation_name)
    
    def _create_automation_section(self, parent, automation_name: str):
        """Create section for a specific automation"""
        # Create frame for this automation
        auto_frame = ttk.LabelFrame(parent, text=automation_name.replace('_', ' ').title())
        auto_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Status display
        status_frame = ttk.Frame(auto_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.status_labels[automation_name] = ttk.Label(status_frame, text="Stopped", 
                                                       foreground='red')
        self.status_labels[automation_name].pack(side=tk.LEFT, padx=5)
        
        # Control buttons
        button_frame = ttk.Frame(auto_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Start button
        start_btn = ttk.Button(button_frame, text="Start", 
                              command=lambda: self._start_automation(automation_name))
        start_btn.pack(side=tk.LEFT, padx=2)
        
        # Stop button
        stop_btn = ttk.Button(button_frame, text="Stop", 
                             command=lambda: self._stop_automation(automation_name),
                             state=tk.DISABLED)
        stop_btn.pack(side=tk.LEFT, padx=2)
        
        # Status button
        status_btn = ttk.Button(button_frame, text="Status", 
                               command=lambda: self._show_automation_status(automation_name))
        status_btn.pack(side=tk.LEFT, padx=2)
        
        # Store button references
        self.control_buttons[automation_name] = {
            'start': start_btn,
            'stop': stop_btn,
            'status': status_btn
        }
        
        # Statistics display
        stats_frame = ttk.Frame(auto_frame)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self._create_statistics_display(stats_frame, automation_name)
    
    def _create_statistics_display(self, parent, automation_name: str):
        """Create statistics display for automation"""
        # Create labels for statistics
        stats_labels = ttk.LabelFrame(parent, text="Statistics")
        stats_labels.pack(fill=tk.X)
        
        # These will be updated dynamically
        self._create_stat_labels(stats_labels, automation_name)
    
    def _create_stat_labels(self, parent, automation_name: str):
        """Create statistic labels for automation"""
        # Create a frame for the stats
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Create labels that will be updated
        self.status_labels[f"{automation_name}_stats"] = {}
        
        # Common statistics
        common_stats = ['is_enabled', 'is_running']
        
        for stat in common_stats:
            label_frame = ttk.Frame(stats_frame)
            label_frame.pack(fill=tk.X)
            
            ttk.Label(label_frame, text=f"{stat.replace('_', ' ').title()}:", width=15).pack(side=tk.LEFT)
            self.status_labels[f"{automation_name}_stats"][stat] = ttk.Label(label_frame, text="N/A")
            self.status_labels[f"{automation_name}_stats"][stat].pack(side=tk.LEFT, padx=5)
    
    def _create_status_summary(self, parent):
        """Create overall status summary"""
        summary_frame = ttk.LabelFrame(parent, text="Overall Status")
        summary_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Summary labels
        self.summary_labels = {}
        
        summary_stats_frame = ttk.Frame(summary_frame)
        summary_stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Active workflows
        ttk.Label(summary_stats_frame, text="Active Workflows:", width=20).pack(side=tk.LEFT)
        self.summary_labels['active_workflows'] = ttk.Label(summary_stats_frame, text="0")
        self.summary_labels['active_workflows'].pack(side=tk.LEFT, padx=5)
        
        # Running automations
        ttk.Label(summary_stats_frame, text="Running Automations:", width=20).pack(side=tk.LEFT)
        self.summary_labels['running_automations'] = ttk.Label(summary_stats_frame, text="0")
        self.summary_labels['running_automations'].pack(side=tk.LEFT, padx=5)
        
        # Control buttons for all automations
        control_frame = ttk.Frame(summary_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Start All", 
                  command=self._start_all_automations).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Stop All", 
                  command=self._stop_all_automations).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Refresh Status", 
                  command=self._refresh_all_status).pack(side=tk.LEFT, padx=2)
    
    def _start_automation(self, automation_name: str):
        """Start a specific automation"""
        try:
            # Get the automation instance
            automation = self.workflow_manager.automations.get(automation_name)
            if not automation:
                messagebox.showerror("Error", f"Automation '{automation_name}' not found")
                return
            
            # Start automation in a separate thread
            thread = threading.Thread(target=automation.start_automation, daemon=True)
            thread.start()
            
            # Update button states
            self.control_buttons[automation_name]['start'].config(state=tk.DISABLED)
            self.control_buttons[automation_name]['stop'].config(state=tk.NORMAL)
            
            self.logger.info(f"Started automation: {automation_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to start automation '{automation_name}': {e}")
            messagebox.showerror("Start Error", f"Failed to start automation: {e}")
    
    def _stop_automation(self, automation_name: str):
        """Stop a specific automation"""
        try:
            # Get the automation instance
            automation = self.workflow_manager.automations.get(automation_name)
            if not automation:
                messagebox.showerror("Error", f"Automation '{automation_name}' not found")
                return
            
            # Stop automation
            automation.stop_automation()
            
            # Update button states
            self.control_buttons[automation_name]['start'].config(state=tk.NORMAL)
            self.control_buttons[automation_name]['stop'].config(state=tk.DISABLED)
            
            self.logger.info(f"Stopped automation: {automation_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to stop automation '{automation_name}': {e}")
            messagebox.showerror("Stop Error", f"Failed to stop automation: {e}")
    
    def _show_automation_status(self, automation_name: str):
        """Show detailed status for an automation"""
        try:
            status = self.workflow_manager.get_automation_status(automation_name)
            
            # Create status window
            status_window = tk.Toplevel(self.parent)
            status_window.title(f"{automation_name} Status")
            status_window.geometry("400x300")
            
            # Create text widget for status display
            text_widget = tk.Text(status_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Format and display status
            status_text = self._format_status(status)
            text_widget.insert(tk.END, status_text)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Failed to show automation status: {e}")
            messagebox.showerror("Status Error", f"Failed to show status: {e}")
    
    def _format_status(self, status: Dict[str, Any]) -> str:
        """Format status dictionary as readable text"""
        if 'error' in status:
            return f"Error: {status['error']}\n"
        
        formatted = "Automation Status:\n\n"
        for key, value in status.items():
            formatted += f"{key.replace('_', ' ').title()}: {value}\n"
        
        return formatted
    
    def _start_all_automations(self):
        """Start all available automations"""
        automations = self.workflow_manager.get_available_automations()
        
        for automation_name in automations:
            try:
                self._start_automation(automation_name)
            except Exception as e:
                self.logger.error(f"Failed to start automation '{automation_name}': {e}")
    
    def _stop_all_automations(self):
        """Stop all running automations"""
        automations = self.workflow_manager.get_available_automations()
        
        for automation_name in automations:
            try:
                self._stop_automation(automation_name)
            except Exception as e:
                self.logger.error(f"Failed to stop automation '{automation_name}': {e}")
    
    def _refresh_all_status(self):
        """Refresh status for all automations"""
        self._update_all_status()
    
    def _update_all_status(self):
        """Update status display for all automations"""
        try:
            # Update individual automation status
            automations = self.workflow_manager.get_available_automations()
            
            for automation_name in automations:
                status = self.workflow_manager.get_automation_status(automation_name)
                
                if 'error' not in status:
                    # Update main status
                    is_running = status.get('is_running', False)
                    status_text = "Running" if is_running else "Stopped"
                    status_color = 'green' if is_running else 'red'
                    
                    if automation_name in self.status_labels:
                        self.status_labels[automation_name].config(text=status_text, foreground=status_color)
                    
                    # Update statistics
                    if f"{automation_name}_stats" in self.status_labels:
                        stats_labels = self.status_labels[f"{automation_name}_stats"]
                        
                        for stat_key, stat_value in status.items():
                            if stat_key in stats_labels:
                                stats_labels[stat_key].config(text=str(stat_value))
            
            # Update summary
            self._update_summary_status()
            
        except Exception as e:
            self.logger.error(f"Failed to update status: {e}")
    
    def _update_summary_status(self):
        """Update summary status display"""
        try:
            # Count active workflows
            workflow_status = self.workflow_manager.get_all_workflow_status()
            active_workflows = sum(1 for status in workflow_status.values() if status.get('is_active', False))
            
            # Count running automations
            automation_status = self.workflow_manager.get_all_automation_status()
            running_automations = sum(1 for status in automation_status.values() 
                                    if status.get('is_running', False))
            
            # Update summary labels
            self.summary_labels['active_workflows'].config(text=str(active_workflows))
            self.summary_labels['running_automations'].config(text=str(running_automations))
            
        except Exception as e:
            self.logger.error(f"Failed to update summary status: {e}")
    
    def _start_status_updates(self):
        """Start periodic status updates"""
        def update_loop():
            while True:
                try:
                    # Update status every 2 seconds
                    self.parent.after(0, self._update_all_status)
                    threading.Event().wait(2)
                except Exception as e:
                    self.logger.error(f"Status update error: {e}")
                    break
        
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()
