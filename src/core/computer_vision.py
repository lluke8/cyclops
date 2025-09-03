"""
Computer Vision functionality for Cyclops automation system.
Handles image matching, template matching, and pattern recognition.
"""

import logging
import os
import time
from typing import List, Dict, Optional, Tuple, Union
import cv2
import numpy as np
import pyautogui
from PIL import Image

class ComputerVision:
    """Computer vision engine with template matching and pattern recognition"""
    
    def __init__(self, config: dict):
        """
        Initialize computer vision engine with configuration
        
        Args:
            config: Configuration dictionary containing CV settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.cv_config = config.get('computer_vision', {})
        
        # CV settings
        self.template_threshold = self.cv_config.get('template_matching_threshold', 0.8)
        self.max_matches = self.cv_config.get('max_matches', 10)
        self.scale_factors = self.cv_config.get('scale_factors', [0.8, 0.9, 1.0, 1.1, 1.2])
        
        # Template cache
        self.template_cache = {}
        
        self.logger.info("Computer Vision engine initialized")
    
    def find_template(self, image: np.ndarray, template_path: str, 
                     confidence: Optional[float] = None) -> Optional[pyautogui.Point]:
        """
        Find template in image using template matching
        
        Args:
            image: Input image as numpy array
            template_path: Path to template image
            confidence: Optional confidence threshold override
            
        Returns:
            Center point of match or None if not found
        """
        try:
            # Load template
            template = self._load_template(template_path)
            if template is None:
                return None
            
            # Use provided confidence or default
            conf = confidence or self.template_threshold
            
            # Convert numpy array to PIL Image for pyautogui
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Find template
            location = pyautogui.locate(template, pil_image, confidence=conf)
            
            if location:
                center = pyautogui.center(location)
                self.logger.debug(f"Template found at: {center}")
                return center
            
            return None
            
        except Exception as e:
            self.logger.error(f"Template matching failed: {e}")
            return None
    
    def find_all_templates(self, image: np.ndarray, template_path: str, 
                          confidence: Optional[float] = None) -> List[pyautogui.Point]:
        """
        Find all instances of template in image
        
        Args:
            image: Input image as numpy array
            template_path: Path to template image
            confidence: Optional confidence threshold override
            
        Returns:
            List of center points of matches
        """
        try:
            # Load template
            template = self._load_template(template_path)
            if template is None:
                return []
            
            # Use provided confidence or default
            conf = confidence or self.template_threshold
            
            # Convert numpy array to PIL Image for pyautogui
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Find all templates
            locations = list(pyautogui.locateAll(template, pil_image, confidence=conf))
            
            # Convert to center points
            centers = [pyautogui.center(loc) for loc in locations]
            
            self.logger.debug(f"Found {len(centers)} template matches")
            return centers
            
        except Exception as e:
            self.logger.error(f"Multi-template matching failed: {e}")
            return []
    
    def find_template_multi_scale(self, image: np.ndarray, template_path: str, 
                                 confidence: Optional[float] = None) -> Optional[pyautogui.Point]:
        """
        Find template using multiple scales for better matching
        
        Args:
            image: Input image as numpy array
            template_path: Path to template image
            confidence: Optional confidence threshold override
            
        Returns:
            Center point of best match or None if not found
        """
        try:
            # Load template
            template = self._load_template(template_path)
            if template is None:
                return None
            
            best_match = None
            best_confidence = 0
            conf = confidence or self.template_threshold
            
            # Convert numpy array to PIL Image for pyautogui
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Try different scales
            for scale in self.scale_factors:
                try:
                    # Scale template
                    scaled_template = template.resize(
                        (int(template.width * scale), int(template.height * scale)),
                        Image.Resampling.LANCZOS
                    )
                    
                    # Find template at this scale
                    location = pyautogui.locate(scaled_template, pil_image, confidence=conf)
                    
                    if location:
                        # Calculate actual confidence (pyautogui doesn't return it)
                        # For now, use scale as confidence proxy
                        scale_confidence = 1.0 - abs(1.0 - scale) * 0.2
                        
                        if scale_confidence > best_confidence:
                            best_confidence = scale_confidence
                            best_match = pyautogui.center(location)
                            
                except Exception as e:
                    self.logger.debug(f"Scale {scale} failed: {e}")
                    continue
            
            if best_match:
                self.logger.debug(f"Multi-scale template found at: {best_match} (confidence: {best_confidence:.2f})")
            
            return best_match
            
        except Exception as e:
            self.logger.error(f"Multi-scale template matching failed: {e}")
            return None
    
    def detect_color_region(self, image: np.ndarray, target_color: Tuple[int, int, int], 
                           tolerance: int = 30) -> List[Tuple[int, int, int, int]]:
        """
        Detect regions with specific color
        
        Args:
            image: Input image as numpy array
            target_color: BGR color tuple to detect
            tolerance: Color tolerance for detection
            
        Returns:
            List of (x, y, width, height) bounding boxes
        """
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Create color range
            target_hsv = cv2.cvtColor(np.uint8([[target_color]]), cv2.COLOR_BGR2HSV)[0][0]
            
            lower = np.array([max(0, target_hsv[0] - tolerance), 50, 50])
            upper = np.array([min(179, target_hsv[0] + tolerance), 255, 255])
            
            # Create mask
            mask = cv2.inRange(hsv, lower, upper)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Get bounding boxes
            regions = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Filter small regions
                    x, y, w, h = cv2.boundingRect(contour)
                    regions.append((x, y, w, h))
            
            self.logger.debug(f"Found {len(regions)} color regions")
            return regions
            
        except Exception as e:
            self.logger.error(f"Color region detection failed: {e}")
            return []
    
    def detect_edges(self, image: np.ndarray, low_threshold: int = 50, 
                    high_threshold: int = 150) -> np.ndarray:
        """
        Detect edges in image using Canny edge detection
        
        Args:
            image: Input image as numpy array
            low_threshold: Lower threshold for edge detection
            high_threshold: Upper threshold for edge detection
            
        Returns:
            Edge-detected image
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply Canny edge detection
            edges = cv2.Canny(blurred, low_threshold, high_threshold)
            
            return edges
            
        except Exception as e:
            self.logger.error(f"Edge detection failed: {e}")
            return image
    
    def find_contours(self, image: np.ndarray, min_area: int = 100) -> List[np.ndarray]:
        """
        Find contours in image
        
        Args:
            image: Input image as numpy array
            min_area: Minimum contour area
            
        Returns:
            List of contours
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Apply threshold
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter by area
            filtered_contours = [c for c in contours if cv2.contourArea(c) >= min_area]
            
            self.logger.debug(f"Found {len(filtered_contours)} contours")
            return filtered_contours
            
        except Exception as e:
            self.logger.error(f"Contour detection failed: {e}")
            return []
    
    def calculate_image_similarity(self, image1: np.ndarray, image2: np.ndarray) -> float:
        """
        Calculate similarity between two images
        
        Args:
            image1: First image
            image2: Second image
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        try:
            # Resize images to same size
            height = min(image1.shape[0], image2.shape[0])
            width = min(image1.shape[1], image2.shape[1])
            
            img1_resized = cv2.resize(image1, (width, height))
            img2_resized = cv2.resize(image2, (width, height))
            
            # Convert to grayscale
            gray1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)
            
            # Calculate structural similarity
            from skimage.metrics import structural_similarity as ssim
            similarity = ssim(gray1, gray2)
            
            return max(0.0, similarity)  # Ensure non-negative
            
        except Exception as e:
            self.logger.error(f"Image similarity calculation failed: {e}")
            return 0.0
    
    def _load_template(self, template_path: str) -> Optional[Image.Image]:
        """
        Load template image with caching
        
        Args:
            template_path: Path to template image
            
        Returns:
            PIL Image or None if loading fails
        """
        try:
            # Check cache first
            if template_path in self.template_cache:
                return self.template_cache[template_path]
            
            # Load from file
            if not os.path.exists(template_path):
                self.logger.error(f"Template file not found: {template_path}")
                return None
            
            template = Image.open(template_path)
            
            # Cache the template
            self.template_cache[template_path] = template
            
            self.logger.debug(f"Template loaded: {template_path}")
            return template
            
        except Exception as e:
            self.logger.error(f"Template loading failed: {e}")
            return None
    
    def clear_template_cache(self):
        """Clear the template cache"""
        self.template_cache.clear()
        self.logger.debug("Template cache cleared")

class ComputerVisionError(Exception):
    """Custom exception for computer vision errors"""
    pass
