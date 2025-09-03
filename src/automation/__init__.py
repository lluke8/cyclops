"""
Automation routines and workflows for Cyclops.
"""

from .rune_creation import RuneCreationAutomation
from .food_eating import FoodEatingAutomation
from .health_monitor import HealthMonitorAutomation
from .workflow_manager import WorkflowManager

__all__ = [
    'RuneCreationAutomation',
    'FoodEatingAutomation',
    'HealthMonitorAutomation',
    'WorkflowManager'
]
