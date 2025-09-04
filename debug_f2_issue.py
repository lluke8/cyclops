#!/usr/bin/env python3
"""
Debug script to identify F2 issue
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import time
import logging
from utils.config_manager import ConfigManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def debug_f2_issue():
    """Debug the F2 issue step by step"""
    
    print("=== F2 Issue Debug ===")
    
    # Check configuration
    config_manager = ConfigManager()
    
    print("\n1. Configuration Check:")
    print(f"   Config file: {config_manager.config_path}")
    print(f"   Window focus enabled: {config_manager.get('automation.rune_creation.window_focus_enabled')}")
    print(f"   Target window name: '{config_manager.get('automation.rune_creation.target_window_name')}'")
    print(f"   Hotkey: {config_manager.get('automation.rune_creation.hotkey')}")
    
    # Check if blank rune image exists
    print("\n2. Blank Rune Image Check:")
    blank_image = config_manager.get('automation.rune_creation.blank_rune_image', 'blank.png')
    print(f"   Blank image config: {blank_image}")
    
    # Check if file exists
    from utils.resource_loader import find_resource, get_image_path
    blank_path = find_resource(blank_image) or get_image_path(blank_image)
    print(f"   Resolved path: {blank_path}")
    print(f"   File exists: {os.path.exists(blank_path) if blank_path else False}")
    
    # Check search region
    print("\n3. Search Region Check:")
    search_region = config_manager.get('automation.rune_creation.search_region', {})
    print(f"   Search region: {search_region}")
    
    # Check rune positions
    print("\n4. Rune Positions Check:")
    rune_positions = config_manager.get('automation.rune_creation.rune_positions', [])
    print(f"   Rune positions: {rune_positions}")
    print(f"   Number of positions: {len(rune_positions)}")
    
    print("\n=== Debug Complete ===")
    print("\nIf you press F2 and it only does window focus but nothing else,")
    print("the issue is likely that the main application is not reloading")
    print("the configuration or there's a different config being used.")

if __name__ == "__main__":
    debug_f2_issue()
