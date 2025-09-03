"""
Status display for Cyclops automation system.
Provides real-time status monitoring and logging display.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import logging
import threading
import time
from typing import Dict, Any, Optional
from automation.workflow_manager import WorkflowManager

class StatusDisplay:
    """Status display with real-time monitoring and logging"""
    
    def __init__(self, parent, workflow_manager: WorkflowManager):
        """
        Initialize status display
        
        Args:
            parent: Parent widget
            workflow_manager: Workflow manager instance
        """
        self.parent = parent
        self.workflow_manager = workflow_manager
        self.logger = logging.getLogger(__name__)
        
        # Status tracking
        self.last_status = {}
        self.status_history = []
        self.max_history = 100
        
        # Logging setup
        self.log_handler = None
        self._setup_logging()
        
        self._create_widgets()
        self._start_monitoring()
    
    def _create_widgets(self):
        """Create status display widgets"""
        # Create main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for different displays
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self._create_status_tab()
        self._create_logs_tab()
        self._create_performance_tab()
        
        # Create control buttons
        self._create_control_buttons(main_frame)
    
    def _create_status_tab(self):
        """Create status monitoring tab"""
        status_frame = ttk.Frame(self.notebook)
        self.notebook.add(status_frame, text="Status")
        
        # Create status display
        self.status_text = scrolledtext.ScrolledText(status_frame, height=20, width=80)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure text widget
        self.status_text.config(font=('Consolas', 9))
        
        # Create status summary
        summary_frame = ttk.LabelFrame(status_frame, text="Quick Status")
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.summary_labels = {}
        self._create_summary_labels(summary_frame)
    
    def _create_summary_labels(self, parent):
        """Create summary status labels"""
        # Create grid for summary labels
        for i, (label_name, label_text) in enumerate([
            ('workflows', 'Active Workflows: 0'),
            ('automations', 'Running Automations: 0'),
            ('health', 'System Health: OK'),
            ('uptime', 'Uptime: 00:00:00')
        ]):
            row = i // 2
            col = i % 2
            
            label = ttk.Label(parent, text=label_text, font=('Arial', 10, 'bold'))
            label.grid(row=row, column=col, padx=10, pady=5, sticky=tk.W)
            self.summary_labels[label_name] = label
    
    def _create_logs_tab(self):
        """Create logs display tab"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs")
        
        # Create logs display
        self.logs_text = scrolledtext.ScrolledText(logs_frame, height=20, width=80)
        self.logs_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure text widget
        self.logs_text.config(font=('Consolas', 9))
        
        # Create log level filter
        filter_frame = ttk.Frame(logs_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Log Level:").pack(side=tk.LEFT)
        self.log_level_var = tk.StringVar(value="INFO")
        log_combo = ttk.Combobox(filter_frame, textvariable=self.log_level_var,
                                values=['DEBUG', 'INFO', 'WARNING', 'ERROR'], state='readonly')
        log_combo.pack(side=tk.LEFT, padx=5)
        log_combo.bind('<<ComboboxSelected>>', self._filter_logs)
    
    def _create_performance_tab(self):
        """Create performance monitoring tab"""
        perf_frame = ttk.Frame(self.notebook)
        self.notebook.add(perf_frame, text="Performance")
        
        # Create performance display
        self.perf_text = scrolledtext.ScrolledText(perf_frame, height=20, width=80)
        self.perf_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure text widget
        self.perf_text.config(font=('Consolas', 9))
        
        # Performance metrics
        self.performance_metrics = {
            'start_time': time.time(),
            'status_updates': 0,
            'log_entries': 0,
            'errors': 0
        }
    
    def _create_control_buttons(self, parent):
        """Create control buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Clear Status", 
                  command=self._clear_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Logs", 
                  command=self._clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Logs", 
                  command=self._export_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", 
                  command=self._refresh_display).pack(side=tk.LEFT, padx=5)
    
    def _setup_logging(self):
        """Setup logging handler for display"""
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.after(0, lambda: self._append_log(msg))
            
            def _append_log(self, msg):
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
                
                # Limit log size
                lines = self.text_widget.get(1.0, tk.END).split('\n')
                if len(lines) > 1000:
                    self.text_widget.delete(1.0, f"{len(lines) - 1000}.0")
        
        # Create and add handler
        self.log_handler = TextHandler(self.logs_text)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Add to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)
    
    def _start_monitoring(self):
        """Start status monitoring"""
        def monitor_loop():
            while True:
                try:
                    self.parent.after(0, self._update_status)
                    threading.Event().wait(1)  # Update every second
                except Exception as e:
                    self.logger.error(f"Status monitoring error: {e}")
                    break
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def _update_status(self):
        """Update status display"""
        try:
            # Get current status
            workflow_status = self.workflow_manager.get_all_workflow_status()
            automation_status = self.workflow_manager.get_all_automation_status()
            
            # Update summary
            self._update_summary(workflow_status, automation_status)
            
            # Update detailed status
            self._update_detailed_status(workflow_status, automation_status)
            
            # Update performance metrics
            self._update_performance_metrics()
            
            # Track status changes
            self._track_status_changes(workflow_status, automation_status)
            
        except Exception as e:
            self.logger.error(f"Failed to update status: {e}")
    
    def _update_summary(self, workflow_status: Dict, automation_status: Dict):
        """Update summary labels"""
        try:
            # Count active workflows
            active_workflows = sum(1 for status in workflow_status.values() 
                                 if status.get('is_active', False))
            
            # Count running automations
            running_automations = sum(1 for status in automation_status.values() 
                                    if status.get('is_running', False))
            
            # Calculate uptime
            uptime_seconds = int(time.time() - self.performance_metrics['start_time'])
            uptime_str = f"{uptime_seconds // 3600:02d}:{(uptime_seconds % 3600) // 60:02d}:{uptime_seconds % 60:02d}"
            
            # Determine system health
            health = "OK"
            if self.performance_metrics['errors'] > 10:
                health = "WARNING"
            if self.performance_metrics['errors'] > 50:
                health = "ERROR"
            
            # Update labels
            self.summary_labels['workflows'].config(text=f"Active Workflows: {active_workflows}")
            self.summary_labels['automations'].config(text=f"Running Automations: {running_automations}")
            self.summary_labels['health'].config(text=f"System Health: {health}")
            self.summary_labels['uptime'].config(text=f"Uptime: {uptime_str}")
            
        except Exception as e:
            self.logger.error(f"Failed to update summary: {e}")
    
    def _update_detailed_status(self, workflow_status: Dict, automation_status: Dict):
        """Update detailed status display"""
        try:
            # Clear and update status text
            self.status_text.delete(1.0, tk.END)
            
            # Add timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            self.status_text.insert(tk.END, f"=== Status Update - {timestamp} ===\n\n")
            
            # Add workflow status
            self.status_text.insert(tk.END, "WORKFLOWS:\n")
            for workflow_name, status in workflow_status.items():
                active = "ACTIVE" if status.get('is_active', False) else "INACTIVE"
                self.status_text.insert(tk.END, f"  {workflow_name}: {active}\n")
            
            self.status_text.insert(tk.END, "\nAUTOMATIONS:\n")
            for automation_name, status in automation_status.items():
                if 'error' not in status:
                    running = "RUNNING" if status.get('is_running', False) else "STOPPED"
                    enabled = "ENABLED" if status.get('is_enabled', False) else "DISABLED"
                    self.status_text.insert(tk.END, f"  {automation_name}: {running} ({enabled})\n")
                else:
                    self.status_text.insert(tk.END, f"  {automation_name}: ERROR - {status['error']}\n")
            
            # Auto-scroll to bottom
            self.status_text.see(tk.END)
            
        except Exception as e:
            self.logger.error(f"Failed to update detailed status: {e}")
    
    def _update_performance_metrics(self):
        """Update performance metrics display"""
        try:
            # Clear and update performance text
            self.perf_text.delete(1.0, tk.END)
            
            # Add timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            self.perf_text.insert(tk.END, f"=== Performance Metrics - {timestamp} ===\n\n")
            
            # Calculate metrics
            uptime = time.time() - self.performance_metrics['start_time']
            status_rate = self.performance_metrics['status_updates'] / uptime if uptime > 0 else 0
            log_rate = self.performance_metrics['log_entries'] / uptime if uptime > 0 else 0
            
            # Display metrics
            self.perf_text.insert(tk.END, f"Uptime: {uptime:.1f} seconds\n")
            self.perf_text.insert(tk.END, f"Status Updates: {self.performance_metrics['status_updates']}\n")
            self.perf_text.insert(tk.END, f"Log Entries: {self.performance_metrics['log_entries']}\n")
            self.perf_text.insert(tk.END, f"Errors: {self.performance_metrics['errors']}\n")
            self.perf_text.insert(tk.END, f"Status Update Rate: {status_rate:.2f}/sec\n")
            self.perf_text.insert(tk.END, f"Log Rate: {log_rate:.2f}/sec\n")
            
            # Auto-scroll to bottom
            self.perf_text.see(tk.END)
            
        except Exception as e:
            self.logger.error(f"Failed to update performance metrics: {e}")
    
    def _track_status_changes(self, workflow_status: Dict, automation_status: Dict):
        """Track status changes for history"""
        try:
            current_status = {
                'timestamp': time.time(),
                'workflows': workflow_status,
                'automations': automation_status
            }
            
            # Add to history
            self.status_history.append(current_status)
            
            # Limit history size
            if len(self.status_history) > self.max_history:
                self.status_history.pop(0)
            
            # Update metrics
            self.performance_metrics['status_updates'] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to track status changes: {e}")
    
    def _filter_logs(self, event=None):
        """Filter logs by level"""
        try:
            # This is a placeholder for log filtering
            # In a real implementation, you would filter the log display
            pass
        except Exception as e:
            self.logger.error(f"Failed to filter logs: {e}")
    
    def _clear_status(self):
        """Clear status display"""
        self.status_text.delete(1.0, tk.END)
        self.status_history.clear()
        self.performance_metrics['status_updates'] = 0
    
    def _clear_logs(self):
        """Clear logs display"""
        self.logs_text.delete(1.0, tk.END)
        self.performance_metrics['log_entries'] = 0
    
    def _export_logs(self):
        """Export logs to file"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                title="Export Logs",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.logs_text.get(1.0, tk.END))
                
                self.logger.info(f"Logs exported to {filename}")
                
        except Exception as e:
            self.logger.error(f"Failed to export logs: {e}")
    
    def _refresh_display(self):
        """Refresh all displays"""
        self._update_status()
    
    def log_message(self, level: str, message: str):
        """Log a message to the display"""
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"{timestamp} - {level.upper()} - {message}\n"
            
            self.logs_text.insert(tk.END, log_entry)
            self.logs_text.see(tk.END)
            
            # Update metrics
            self.performance_metrics['log_entries'] += 1
            if level.upper() in ['ERROR', 'CRITICAL']:
                self.performance_metrics['errors'] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to log message: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.log_handler:
                root_logger = logging.getLogger()
                root_logger.removeHandler(self.log_handler)
        except Exception as e:
            self.logger.error(f"Failed to cleanup status display: {e}")
