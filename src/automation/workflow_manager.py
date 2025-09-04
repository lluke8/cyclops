"""
Workflow manager for Cyclops automation system.
Orchestrates complex automation sequences and manages multiple automation routines.
"""

import logging
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from core.screen_capture import ScreenCapture
from core.input_simulator import InputSimulator
from core.state_monitor import StateMonitor
from utils.timing import TimingUtils
from utils.config_manager import ConfigManager
from automation.rune_creation import RuneCreationAutomation
from automation.food_eating import FoodEatingAutomation
from automation.health_monitor import HealthMonitorAutomation

class WorkflowManager:
    """Workflow manager for orchestrating automation sequences"""
    
    def __init__(self, config_manager: ConfigManager, screen_capture: ScreenCapture, 
                 input_simulator: InputSimulator, state_monitor: StateMonitor):
        """
        Initialize workflow manager
        
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
        
        # Initialize automation modules
        self.automations: Dict[str, Any] = {}
        self._initialize_automations()
        
        # Workflow state
        self.is_running = False
        self.active_workflows: List[str] = []
        self.workflow_threads: Dict[str, threading.Thread] = {}
        
        # Process coordination
        self.process_lock = threading.Lock()
        self.active_process = None  # 'rune_creation' or 'food_eating' or None
        self.pending_processes = []  # Queue of processes waiting to run
        
        # Callbacks for automation events
        self.automation_callbacks: Dict[str, List[Callable]] = {}
        
        # Workflow definitions
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self._define_default_workflows()
        
        self.logger.info("Workflow Manager initialized")
    
    def _initialize_automations(self):
        """Initialize all automation modules"""
        try:
            # Initialize individual automation modules
            self.automations['rune_creation'] = RuneCreationAutomation(
                self.config_manager, self.screen_capture, 
                self._get_computer_vision(), self.input_simulator, self.state_monitor
            )
            
            self.automations['food_eating'] = FoodEatingAutomation(
                self.config_manager, self.screen_capture, 
                self.input_simulator, self.state_monitor
            )
            
            self.automations['health_monitor'] = HealthMonitorAutomation(
                self.config_manager, self.screen_capture, 
                self.input_simulator, self.state_monitor
            )
            
            self.logger.info("All automation modules initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize automations: {e}")
    
    def _get_computer_vision(self):
        """Get computer vision instance (lazy import to avoid circular dependencies)"""
        try:
            from core.computer_vision import ComputerVision
            return ComputerVision(self.config_manager.config)
        except Exception as e:
            self.logger.error(f"Failed to get computer vision instance: {e}")
            return None
    
    def _define_default_workflows(self):
        """Define default workflow configurations"""
        self.workflows = {
            'basic_gameplay': {
                'name': 'Basic Gameplay',
                'description': 'Basic automation with health monitoring and food eating',
                'automations': ['health_monitor', 'food_eating'],
                'enabled': False
            },
            'rune_farming': {
                'name': 'Rune Farming',
                'description': 'Automated rune creation with health monitoring',
                'automations': ['rune_creation', 'health_monitor'],
                'enabled': False
            },
            'full_automation': {
                'name': 'Full Automation',
                'description': 'All automations running simultaneously',
                'automations': ['rune_creation', 'food_eating', 'health_monitor'],
                'enabled': False
            },
            'emergency_only': {
                'name': 'Emergency Only',
                'description': 'Only health monitoring for emergency situations',
                'automations': ['health_monitor'],
                'enabled': False
            }
        }
    
    def start_workflow(self, workflow_name: str) -> bool:
        """
        Start a specific workflow
        
        Args:
            workflow_name: Name of the workflow to start
            
        Returns:
            True if workflow started successfully, False otherwise
        """
        if workflow_name not in self.workflows:
            self.logger.error(f"Unknown workflow: {workflow_name}")
            return False
        
        if workflow_name in self.active_workflows:
            self.logger.warning(f"Workflow '{workflow_name}' is already running")
            return False
        
        workflow = self.workflows[workflow_name]
        self.logger.info(f"Starting workflow: {workflow['name']}")
        
        try:
            # Start individual automations in the workflow
            for automation_name in workflow['automations']:
                if automation_name in self.automations:
                    automation = self.automations[automation_name]
                    
                    # Start automation in a separate thread
                    thread = threading.Thread(
                        target=self._run_automation,
                        args=(automation_name, automation),
                        daemon=True
                    )
                    thread.start()
                    self.workflow_threads[automation_name] = thread
                    
                    self.logger.info(f"Started automation: {automation_name}")
                else:
                    self.logger.warning(f"Automation not found: {automation_name}")
            
            # Mark workflow as active
            self.active_workflows.append(workflow_name)
            self.is_running = True
            
            self.logger.info(f"Workflow '{workflow_name}' started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start workflow '{workflow_name}': {e}")
            return False
    
    def stop_workflow(self, workflow_name: str) -> bool:
        """
        Stop a specific workflow
        
        Args:
            workflow_name: Name of the workflow to stop
            
        Returns:
            True if workflow stopped successfully, False otherwise
        """
        if workflow_name not in self.workflows:
            self.logger.error(f"Unknown workflow: {workflow_name}")
            return False
        
        if workflow_name not in self.active_workflows:
            self.logger.warning(f"Workflow '{workflow_name}' is not running")
            return False
        
        workflow = self.workflows[workflow_name]
        self.logger.info(f"Stopping workflow: {workflow['name']}")
        
        try:
            # Stop individual automations in the workflow
            for automation_name in workflow['automations']:
                if automation_name in self.automations:
                    automation = self.automations[automation_name]
                    automation.stop_automation()
                    
                    # Wait for thread to finish (with better error handling)
                    if automation_name in self.workflow_threads:
                        thread = self.workflow_threads[automation_name]
                        try:
                            # Check if we're not trying to join the current thread
                            if thread != threading.current_thread():
                                thread.join(timeout=2.0)
                            else:
                                self.logger.warning(f"Skipping thread join for {automation_name} - current thread")
                        except Exception as thread_error:
                            self.logger.warning(f"Thread join failed for {automation_name}: {thread_error}")
                        finally:
                            # Always clean up the thread reference
                            del self.workflow_threads[automation_name]
                    
                    self.logger.info(f"Stopped automation: {automation_name}")
            
            # Remove from active workflows
            self.active_workflows.remove(workflow_name)
            
            # Update running state
            if not self.active_workflows:
                self.is_running = False
            
            self.logger.info(f"Workflow '{workflow_name}' stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop workflow '{workflow_name}': {e}")
            # Even if stopping failed, clean up the workflow state
            try:
                if workflow_name in self.active_workflows:
                    self.active_workflows.remove(workflow_name)
                if not self.active_workflows:
                    self.is_running = False
            except:
                pass
            return False
    
    def stop_all_workflows(self):
        """Stop all active workflows"""
        self.logger.info("Stopping all workflows...")
        
        active_workflows = self.active_workflows.copy()
        for workflow_name in active_workflows:
            self.stop_workflow(workflow_name)
        
        self.logger.info("All workflows stopped")
    
    def _run_automation(self, automation_name: str, automation: Any):
        """
        Run an automation in a separate thread
        
        Args:
            automation_name: Name of the automation
            automation: Automation instance
        """
        try:
            self.logger.info(f"Running automation: {automation_name}")
            
            # Notify callbacks that automation is starting
            self._notify_callbacks(automation_name, 'started')
            
            automation.start_automation()
            
            # Notify callbacks that automation has stopped
            self._notify_callbacks(automation_name, 'stopped')
            
        except Exception as e:
            self.logger.error(f"Automation '{automation_name}' failed: {e}")
            self._notify_callbacks(automation_name, 'error', str(e))
    
    def register_callback(self, automation_name: str, callback: Callable):
        """
        Register a callback for automation events
        
        Args:
            automation_name: Name of the automation to monitor
            callback: Callback function (automation_name, event, *args)
        """
        if automation_name not in self.automation_callbacks:
            self.automation_callbacks[automation_name] = []
        self.automation_callbacks[automation_name].append(callback)
        self.logger.info(f"Registered callback for {automation_name}")
    
    def _notify_callbacks(self, automation_name: str, event: str, *args):
        """
        Notify all callbacks for an automation event
        
        Args:
            automation_name: Name of the automation
            event: Event type ('started', 'stopped', 'error')
            *args: Additional arguments
        """
        if automation_name in self.automation_callbacks:
            for callback in self.automation_callbacks[automation_name]:
                try:
                    callback(automation_name, event, *args)
                except Exception as e:
                    self.logger.error(f"Callback error for {automation_name}: {e}")
    
    def get_workflow_status(self, workflow_name: str) -> Dict[str, Any]:
        """
        Get status of a specific workflow
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            Dictionary containing workflow status
        """
        if workflow_name not in self.workflows:
            return {'error': f'Unknown workflow: {workflow_name}'}
        
        workflow = self.workflows[workflow_name]
        is_active = workflow_name in self.active_workflows
        
        automation_statuses = {}
        for automation_name in workflow['automations']:
            if automation_name in self.automations:
                automation = self.automations[automation_name]
                automation_statuses[automation_name] = automation.get_status()
        
        return {
            'name': workflow['name'],
            'description': workflow['description'],
            'is_active': is_active,
            'automations': automation_statuses
        }
    
    def get_all_workflow_status(self) -> Dict[str, Any]:
        """
        Get status of all workflows
        
        Returns:
            Dictionary containing all workflow statuses
        """
        return {
            workflow_name: self.get_workflow_status(workflow_name)
            for workflow_name in self.workflows.keys()
        }
    
    def get_automation_status(self, automation_name: str) -> Dict[str, Any]:
        """
        Get status of a specific automation
        
        Args:
            automation_name: Name of the automation
            
        Returns:
            Dictionary containing automation status
        """
        if automation_name not in self.automations:
            return {'error': f'Unknown automation: {automation_name}'}
        
        automation = self.automations[automation_name]
        return automation.get_status()
    
    def get_all_automation_status(self) -> Dict[str, Any]:
        """
        Get status of all automations
        
        Returns:
            Dictionary containing all automation statuses
        """
        return {
            automation_name: self.get_automation_status(automation_name)
            for automation_name in self.automations.keys()
        }
    
    def create_custom_workflow(self, name: str, description: str, 
                              automations: List[str]) -> bool:
        """
        Create a custom workflow
        
        Args:
            name: Workflow name
            description: Workflow description
            automations: List of automation names to include
            
        Returns:
            True if workflow created successfully, False otherwise
        """
        try:
            # Validate automations
            for automation_name in automations:
                if automation_name not in self.automations:
                    self.logger.error(f"Unknown automation: {automation_name}")
                    return False
            
            # Create workflow
            self.workflows[name] = {
                'name': name,
                'description': description,
                'automations': automations,
                'enabled': False
            }
            
            self.logger.info(f"Created custom workflow: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create custom workflow: {e}")
            return False
    
    def delete_workflow(self, workflow_name: str) -> bool:
        """
        Delete a workflow
        
        Args:
            workflow_name: Name of the workflow to delete
            
        Returns:
            True if workflow deleted successfully, False otherwise
        """
        if workflow_name not in self.workflows:
            self.logger.error(f"Unknown workflow: {workflow_name}")
            return False
        
        if workflow_name in self.active_workflows:
            self.logger.error(f"Cannot delete active workflow: {workflow_name}")
            return False
        
        try:
            del self.workflows[workflow_name]
            self.logger.info(f"Deleted workflow: {workflow_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete workflow: {e}")
            return False
    
    def get_available_workflows(self) -> List[str]:
        """
        Get list of available workflow names
        
        Returns:
            List of workflow names
        """
        return list(self.workflows.keys())
    
    def get_available_automations(self) -> List[str]:
        """
        Get list of available automation names
        
        Returns:
            List of automation names
        """
        return list(self.automations.keys())
    
    def get_automation(self, automation_name: str) -> Optional[Any]:
        """
        Get a specific automation instance
        
        Args:
            automation_name: Name of the automation to retrieve
            
        Returns:
            Automation instance if found, None otherwise
        """
        return self.automations.get(automation_name)
    
    def request_process_access(self, process_name: str) -> bool:
        """
        Request access to run a process (rune_creation or food_eating)
        
        Args:
            process_name: Name of the process requesting access
            
        Returns:
            True if access granted, False if denied
        """
        with self.process_lock:
            if self.active_process is None:
                # No process is running, grant access
                self.active_process = process_name
                self.logger.info(f"Process access granted to: {process_name}")
                return True
            elif self.active_process == process_name:
                # Same process is already running, grant access
                return True
            else:
                # Another process is running, queue this one
                if process_name not in self.pending_processes:
                    self.pending_processes.append(process_name)
                    self.logger.info(f"Process {process_name} queued, {self.active_process} is active")
                return False
    
    def release_process_access(self, process_name: str):
        """
        Release process access and start next queued process
        
        Args:
            process_name: Name of the process releasing access
        """
        with self.process_lock:
            if self.active_process == process_name:
                self.active_process = None
                self.logger.info(f"Process access released by: {process_name}")
                
                # Start next queued process if any
                if self.pending_processes:
                    next_process = self.pending_processes.pop(0)
                    self.active_process = next_process
                    self.logger.info(f"Started queued process: {next_process}")
                    
                    # Trigger the queued process to run immediately
                    self._trigger_queued_process(next_process)
    
    def _trigger_queued_process(self, process_name: str):
        """
        Trigger a queued process to run immediately
        
        Args:
            process_name: Name of the process to trigger
        """
        try:
            if process_name == 'rune_creation':
                rune_automation = self.get_automation('rune_creation')
                if rune_automation and rune_automation.is_running:
                    # Force immediate execution
                    rune_automation.next_create_time = 0
            elif process_name == 'food_eating':
                food_automation = self.get_automation('food_eating')
                if food_automation and food_automation.is_running:
                    # Force immediate execution
                    food_automation.next_eat_time = 0
        except Exception as e:
            self.logger.error(f"Failed to trigger queued process {process_name}: {e}")
    
    def get_process_status(self) -> Dict[str, Any]:
        """
        Get current process coordination status
        
        Returns:
            Dictionary with process status information
        """
        with self.process_lock:
            return {
                'active_process': self.active_process,
                'pending_processes': self.pending_processes.copy(),
                'queue_length': len(self.pending_processes)
            }

class WorkflowManagerError(Exception):
    """Custom exception for workflow manager errors"""
    pass
