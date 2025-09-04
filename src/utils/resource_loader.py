"""
Resource loading utilities for PyInstaller compatibility.
Handles file paths correctly in both development and packaged environments.
"""

import sys
import os
import logging
from typing import Optional

def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for both development and PyInstaller exe.
    
    Args:
        relative_path: Path relative to the project root
        
    Returns:
        Absolute path to the resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            # Running from PyInstaller executable
            base_path = sys._MEIPASS
        else:
            # Running from source
            base_path = os.path.abspath(".")
        
        full_path = os.path.join(base_path, relative_path)
        
        # Normalize path separators for Windows
        full_path = os.path.normpath(full_path)
        
        return full_path
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to resolve resource path '{relative_path}': {e}")
        # Fallback to relative path
        return relative_path

def find_resource(relative_path: str, search_paths: Optional[list] = None) -> Optional[str]:
    """
    Find a resource file, checking multiple possible locations.
    
    Args:
        relative_path: Path relative to the project root
        search_paths: Additional paths to search (optional)
        
    Returns:
        Full path to the resource if found, None otherwise
    """
    if search_paths is None:
        search_paths = []
    
    # Add the resource path resolver result
    search_paths.insert(0, resource_path(relative_path))
    
    # Add current directory as fallback
    search_paths.append(relative_path)
    
    for path in search_paths:
        if os.path.exists(path):
            return os.path.normpath(path)
    
    return None

def get_config_path(config_name: str = "default_config.json") -> str:
    """
    Get the path to a configuration file.
    
    Args:
        config_name: Name of the config file
        
    Returns:
        Path to the config file
    """
    return resource_path(f"config/{config_name}")

def get_image_path(image_name: str) -> str:
    """
    Get the path to an image file.
    
    Args:
        image_name: Name of the image file
        
    Returns:
        Path to the image file
    """
    return resource_path(image_name)

def ensure_directory_exists(path: str) -> bool:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to create directory '{path}': {e}")
        return False

def get_user_data_dir() -> str:
    """
    Get the user data directory for storing user-specific files.
    
    Returns:
        Path to user data directory
    """
    if hasattr(sys, '_MEIPASS'):
        # When running from PyInstaller, use a writable directory
        import tempfile
        return os.path.join(tempfile.gettempdir(), "Cyclops")
    else:
        # When running from source, use project directory
        return os.path.abspath(".")
