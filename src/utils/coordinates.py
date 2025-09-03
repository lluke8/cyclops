"""
Coordinate utilities for Cyclops automation system.
Handles coordinate system conversions and utilities.
"""

import logging
from typing import Tuple, List, Optional

class CoordinateUtils:
    """Coordinate system utilities and conversions"""
    
    def __init__(self, base_region: Optional[Tuple[int, int, int, int]] = None):
        """
        Initialize coordinate utilities
        
        Args:
            base_region: Base region (x, y, width, height) for relative coordinates
        """
        self.logger = logging.getLogger(__name__)
        self.base_region = base_region or (0, 0, 1920, 1080)
        self.logger.debug(f"Coordinate utils initialized with base region: {self.base_region}")
    
    def to_absolute(self, relative_x: int, relative_y: int) -> Tuple[int, int]:
        """
        Convert relative coordinates to absolute
        
        Args:
            relative_x: Relative X coordinate
            relative_y: Relative Y coordinate
            
        Returns:
            Absolute (x, y) coordinates
        """
        base_x, base_y, _, _ = self.base_region
        return base_x + relative_x, base_y + relative_y
    
    def to_relative(self, absolute_x: int, absolute_y: int) -> Tuple[int, int]:
        """
        Convert absolute coordinates to relative
        
        Args:
            absolute_x: Absolute X coordinate
            absolute_y: Absolute Y coordinate
            
        Returns:
            Relative (x, y) coordinates
        """
        base_x, base_y, _, _ = self.base_region
        return absolute_x - base_x, absolute_y - base_y
    
    def is_within_region(self, x: int, y: int, region: Tuple[int, int, int, int]) -> bool:
        """
        Check if coordinates are within a region
        
        Args:
            x: X coordinate
            y: Y coordinate
            region: Region (x, y, width, height)
            
        Returns:
            True if coordinates are within region
        """
        region_x, region_y, region_w, region_h = region
        return (region_x <= x <= region_x + region_w and 
                region_y <= y <= region_y + region_h)
    
    def get_region_center(self, region: Tuple[int, int, int, int]) -> Tuple[int, int]:
        """
        Get center coordinates of a region
        
        Args:
            region: Region (x, y, width, height)
            
        Returns:
            Center (x, y) coordinates
        """
        x, y, width, height = region
        return x + width // 2, y + height // 2
    
    def expand_region(self, region: Tuple[int, int, int, int], 
                     padding: int) -> Tuple[int, int, int, int]:
        """
        Expand region by padding
        
        Args:
            region: Region (x, y, width, height)
            padding: Padding amount
            
        Returns:
            Expanded region
        """
        x, y, width, height = region
        return (x - padding, y - padding, width + 2 * padding, height + 2 * padding)
    
    def shrink_region(self, region: Tuple[int, int, int, int], 
                     padding: int) -> Tuple[int, int, int, int]:
        """
        Shrink region by padding
        
        Args:
            region: Region (x, y, width, height)
            padding: Padding amount
            
        Returns:
            Shrunk region
        """
        x, y, width, height = region
        new_x = max(0, x + padding)
        new_y = max(0, y + padding)
        new_width = max(1, width - 2 * padding)
        new_height = max(1, height - 2 * padding)
        return (new_x, new_y, new_width, new_height)
    
    def normalize_coordinates(self, x: int, y: int, 
                            source_size: Tuple[int, int], 
                            target_size: Tuple[int, int]) -> Tuple[int, int]:
        """
        Normalize coordinates from source size to target size
        
        Args:
            x: Source X coordinate
            y: Source Y coordinate
            source_size: Source size (width, height)
            target_size: Target size (width, height)
            
        Returns:
            Normalized (x, y) coordinates
        """
        source_w, source_h = source_size
        target_w, target_h = target_size
        
        norm_x = int((x / source_w) * target_w)
        norm_y = int((y / source_h) * target_h)
        
        return norm_x, norm_y
    
    def distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """
        Calculate distance between two points
        
        Args:
            x1, y1: First point coordinates
            x2, y2: Second point coordinates
            
        Returns:
            Distance between points
        """
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    
    def find_closest_point(self, target_x: int, target_y: int, 
                          points: List[Tuple[int, int]]) -> Tuple[int, int]:
        """
        Find closest point to target from a list of points
        
        Args:
            target_x, target_y: Target coordinates
            points: List of (x, y) points
            
        Returns:
            Closest point coordinates
        """
        if not points:
            return target_x, target_y
        
        closest_point = points[0]
        min_distance = self.distance(target_x, target_y, closest_point[0], closest_point[1])
        
        for point in points[1:]:
            dist = self.distance(target_x, target_y, point[0], point[1])
            if dist < min_distance:
                min_distance = dist
                closest_point = point
        
        return closest_point
