"""
OCR (Optical Character Recognition) engine for Cyclops automation system.
Handles text recognition using Tesseract OCR with robust error handling.
"""

import logging
import os
import time
from typing import List, Dict, Optional, Tuple
import cv2
import numpy as np
import pytesseract
from PIL import Image

class OCREngine:
    """OCR engine with Tesseract backend and robust text recognition"""
    
    def __init__(self, config: dict):
        """
        Initialize OCR engine with configuration
        
        Args:
            config: Configuration dictionary containing OCR settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.ocr_config = config.get('ocr', {})
        
        # Configure Tesseract
        self._setup_tesseract()
        
        # OCR settings
        self.language = self.ocr_config.get('language', 'eng')
        self.confidence_threshold = self.ocr_config.get('confidence_threshold', 0.7)
        
        self.logger.info(f"OCR Engine initialized with language: {self.language}")
    
    def _setup_tesseract(self):
        """Setup Tesseract executable path"""
        tesseract_path = self.ocr_config.get('tesseract_path')
        
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            self.logger.info(f"Tesseract path set to: {tesseract_path}")
        else:
            # Try common Windows paths
            common_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', ''))
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    self.logger.info(f"Found Tesseract at: {path}")
                    return
            
            self.logger.warning("Tesseract executable not found in common paths")
    
    def extract_text(self, image: np.ndarray, region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """
        Extract text from image using OCR
        
        Args:
            image: Input image as numpy array
            region: Optional (x, y, width, height) region to process
            
        Returns:
            Extracted text string
        """
        try:
            # Extract region if specified
            if region:
                x, y, width, height = region
                image = image[y:y+height, x:x+width]
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(processed_image, lang=self.language)
            
            self.logger.debug(f"OCR extracted text: '{text.strip()}'")
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"OCR text extraction failed: {e}")
            return ""
    
    def extract_text_with_confidence(self, image: np.ndarray, 
                                   region: Optional[Tuple[int, int, int, int]] = None) -> List[Dict]:
        """
        Extract text with confidence scores
        
        Args:
            image: Input image as numpy array
            region: Optional (x, y, width, height) region to process
            
        Returns:
            List of dictionaries containing text, confidence, and bounding box
        """
        try:
            # Extract region if specified
            if region:
                x, y, width, height = region
                image = image[y:y+height, x:x+width]
            
            # Preprocess image
            processed_image = self._preprocess_image(image)
            
            # Get detailed OCR data
            data = pytesseract.image_to_data(processed_image, lang=self.language, 
                                           output_type=pytesseract.Output.DICT)
            
            results = []
            for i, conf in enumerate(data['conf']):
                confidence = int(conf) / 100.0
                text = data['text'][i].strip()
                
                if text and confidence >= self.confidence_threshold:
                    results.append({
                        'text': text,
                        'confidence': confidence,
                        'bbox': (data['left'][i], data['top'][i], 
                                data['width'][i], data['height'][i])
                    })
            
            self.logger.debug(f"OCR extracted {len(results)} text elements with confidence >= {self.confidence_threshold}")
            return results
            
        except Exception as e:
            self.logger.error(f"OCR confidence extraction failed: {e}")
            return []
    
    def find_text(self, image: np.ndarray, target_text: str, 
                 region: Optional[Tuple[int, int, int, int]] = None) -> List[Dict]:
        """
        Find specific text in image
        
        Args:
            image: Input image as numpy array
            target_text: Text to search for
            region: Optional (x, y, width, height) region to search
            
        Returns:
            List of matches with text, confidence, and bounding box
        """
        try:
            # Extract text with confidence
            text_elements = self.extract_text_with_confidence(image, region)
            
            # Filter for target text
            matches = []
            target_lower = target_text.lower()
            
            for element in text_elements:
                if target_lower in element['text'].lower():
                    matches.append(element)
            
            self.logger.debug(f"Found {len(matches)} matches for text: '{target_text}'")
            return matches
            
        except Exception as e:
            self.logger.error(f"Text search failed: {e}")
            return []
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply thresholding
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            self.logger.error(f"Image preprocessing failed: {e}")
            return image
    
    def get_text_regions(self, image: np.ndarray, 
                        min_area: int = 100) -> List[Tuple[int, int, int, int]]:
        """
        Get regions containing text
        
        Args:
            image: Input image as numpy array
            min_area: Minimum area for text regions
            
        Returns:
            List of (x, y, width, height) tuples for text regions
        """
        try:
            # Preprocess image
            processed = self._preprocess_image(image)
            
            # Find contours
            contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            regions = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area >= min_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    regions.append((x, y, w, h))
            
            self.logger.debug(f"Found {len(regions)} text regions")
            return regions
            
        except Exception as e:
            self.logger.error(f"Text region detection failed: {e}")
            return []
    
    def is_text_visible(self, image: np.ndarray, target_text: str, 
                       region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """
        Check if specific text is visible in image
        
        Args:
            image: Input image as numpy array
            target_text: Text to check for
            region: Optional (x, y, width, height) region to check
            
        Returns:
            True if text is found, False otherwise
        """
        matches = self.find_text(image, target_text, region)
        return len(matches) > 0
    
    def get_text_density(self, image: np.ndarray, 
                        region: Optional[Tuple[int, int, int, int]] = None) -> float:
        """
        Calculate text density in image region
        
        Args:
            image: Input image as numpy array
            region: Optional (x, y, width, height) region to analyze
            
        Returns:
            Text density as percentage (0.0 to 1.0)
        """
        try:
            if region:
                x, y, width, height = region
                image = image[y:y+height, x:x+width]
            
            # Get text regions
            text_regions = self.get_text_regions(image)
            
            if not text_regions:
                return 0.0
            
            # Calculate total text area
            total_text_area = sum(w * h for _, _, w, h in text_regions)
            image_area = image.shape[0] * image.shape[1]
            
            density = total_text_area / image_area
            return min(density, 1.0)
            
        except Exception as e:
            self.logger.error(f"Text density calculation failed: {e}")
            return 0.0

class OCRError(Exception):
    """Custom exception for OCR errors"""
    pass
