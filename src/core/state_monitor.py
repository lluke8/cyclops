"""
State monitoring functionality for Cyclops automation system.
Handles continuous monitoring of screen states and conditions.
"""

import logging
import time
import threading
from typing import Dict, List, Callable, Optional, Any, Tuple
import cv2
import numpy as np
from .screen_capture import ScreenCapture
from .ocr_engine import OCREngine
from .computer_vision import ComputerVision

class StateMonitor:
    """State monitoring with continuous screen analysis and condition checking"""
    
    def __init__(self, config: dict, screen_capture: ScreenCapture, 
                 ocr_engine: OCREngine, computer_vision: ComputerVision):
        """
        Initialize state monitor with dependencies
        
        Args:
            config: Configuration dictionary
            screen_capture: Screen capture instance
            ocr_engine: OCR engine instance
            computer_vision: Computer vision instance
        """
        self.config = config
        self.screen_capture = screen_capture
        self.ocr_engine = ocr_engine
        self.computer_vision = computer_vision
        self.logger = logging.getLogger(__name__)
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread = None
        self.monitoring_interval = 0.5  # seconds
        
        # Condition callbacks
        self.condition_callbacks: Dict[str, List[Callable]] = {}
        self.last_states: Dict[str, Any] = {}
        
        # State history for change detection
        self.state_history: Dict[str, List[Any]] = {}
        self.max_history_size = 10
        
        self.logger.info("State Monitor initialized")
    
    def start_monitoring(self):
        """Start continuous state monitoring"""
        if self.is_monitoring:
            self.logger.warning("State monitoring is already running")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("State monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous state monitoring"""
        if not self.is_monitoring:
            self.logger.warning("State monitoring is not running")
            return
        
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        
        self.logger.info("State monitoring stopped")
    
    def register_condition(self, condition_name: str, callback: Callable, 
                          check_interval: float = 1.0):
        """
        Register a condition to monitor
        
        Args:
            condition_name: Unique name for the condition
            callback: Function to call when condition is checked
            check_interval: How often to check this condition (seconds)
        """
        if condition_name not in self.condition_callbacks:
            self.condition_callbacks[condition_name] = []
        
        self.condition_callbacks[condition_name].append({
            'callback': callback,
            'interval': check_interval,
            'last_check': 0
        })
        
        self.logger.info(f"Registered condition: {condition_name}")
    
    def unregister_condition(self, condition_name: str):
        """
        Unregister a condition
        
        Args:
            condition_name: Name of condition to unregister
        """
        if condition_name in self.condition_callbacks:
            del self.condition_callbacks[condition_name]
            self.logger.info(f"Unregistered condition: {condition_name}")
    
    def check_condition_once(self, condition_name: str) -> Any:
        """
        Check a specific condition once
        
        Args:
            condition_name: Name of condition to check
            
        Returns:
            Result of condition check
        """
        if condition_name not in self.condition_callbacks:
            self.logger.warning(f"Condition '{condition_name}' not registered")
            return None
        
        callbacks = self.condition_callbacks[condition_name]
        if not callbacks:
            return None
        
        # Use the first callback
        callback_info = callbacks[0]
        try:
            result = callback_info['callback']()
            self.last_states[condition_name] = result
            return result
        except Exception as e:
            self.logger.error(f"Condition check failed for '{condition_name}': {e}")
            return None
    
    def get_last_state(self, condition_name: str) -> Any:
        """
        Get the last known state of a condition
        
        Args:
            condition_name: Name of condition
            
        Returns:
            Last state value or None
        """
        return self.last_states.get(condition_name)
    
    def is_state_changed(self, condition_name: str) -> bool:
        """
        Check if a condition's state has changed
        
        Args:
            condition_name: Name of condition
            
        Returns:
            True if state has changed, False otherwise
        """
        if condition_name not in self.state_history:
            return False
        
        history = self.state_history[condition_name]
        if len(history) < 2:
            return False
        
        return history[-1] != history[-2]
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                current_time = time.time()
                
                # Check all registered conditions
                for condition_name, callbacks in self.condition_callbacks.items():
                    for callback_info in callbacks:
                        # Check if it's time to evaluate this condition
                        if current_time - callback_info['last_check'] >= callback_info['interval']:
                            try:
                                result = callback_info['callback']()
                                
                                # Update state history
                                if condition_name not in self.state_history:
                                    self.state_history[condition_name] = []
                                
                                self.state_history[condition_name].append(result)
                                
                                # Limit history size
                                if len(self.state_history[condition_name]) > self.max_history_size:
                                    self.state_history[condition_name].pop(0)
                                
                                # Update last state
                                self.last_states[condition_name] = result
                                
                                # Update last check time
                                callback_info['last_check'] = current_time
                                
                            except Exception as e:
                                self.logger.error(f"Error in condition '{condition_name}': {e}")
                
                # Sleep before next iteration
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1.0)  # Wait before retrying
    
    def create_image_search_monitor(self, region: Tuple[int, int, int, int], 
                                   image_path: str = 'health_reference.png',
                                   confidence_threshold: float = 0.8) -> str:
        """
        Create a monitor that searches for a specific image in a region
        
        Args:
            region: Region to search in
            image_path: Path to the reference image to search for
            confidence_threshold: Minimum confidence for a match
            
        Returns:
            Condition name for the image search monitor
        """
        condition_name = "image_search_monitor"
        
        def image_search_check():
            try:
                # Capture the region
                image = self.screen_capture.capture_region(*region)
                
                if image is None:
                    self.logger.error("Failed to capture search region image")
                    return None
                
                # Load the reference image
                try:
                    import cv2
                    reference = cv2.imread(image_path, cv2.IMREAD_COLOR)
                    if reference is None:
                        self.logger.error(f"Could not load reference image: {image_path}")
                        return None
                except Exception as e:
                    self.logger.error(f"Failed to load reference image: {e}")
                    return None
                
                # Perform template matching
                result = cv2.matchTemplate(image, reference, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                # Determine if image was found
                image_found = max_val >= confidence_threshold
                
                result_data = {
                    'image_found': image_found,
                    'confidence': max_val,
                    'threshold': confidence_threshold,
                    'match_location': max_loc,
                    'region': region,
                    'reference_image': image_path
                }
                
                return result_data
                
            except Exception as e:
                self.logger.error(f"Image search check failed: {e}")
                return None
        
        self.register_condition(condition_name, image_search_check, check_interval=0.5)
        return condition_name

    def test_image_search(self, region: Tuple[int, int, int, int], 
                         image_path: str = 'health_reference.png',
                         confidence_threshold: float = 0.8) -> dict:
        """
        Test image search manually (for PageDown testing)
        
        Args:
            region: Region to search in
            image_path: Path to the reference image to search for
            confidence_threshold: Minimum confidence for a match
            
        Returns:
            Dictionary with test results
        """
        try:
            # Capture the region
            image = self.screen_capture.capture_region(*region)
            
            if image is None:
                self.logger.error("Failed to capture test region image")
                return {'success': False, 'error': 'Failed to capture region'}
            
            # Load the reference image
            try:
                import cv2
                reference = cv2.imread(image_path, cv2.IMREAD_COLOR)
                if reference is None:
                    self.logger.error(f"Could not load reference image: {image_path}")
                    return {'success': False, 'error': f'Could not load {image_path}'}
            except Exception as e:
                self.logger.error(f"Failed to load reference image: {e}")
                return {'success': False, 'error': str(e)}
            
            # Perform template matching
            result = cv2.matchTemplate(image, reference, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Determine if image was found
            image_found = max_val >= confidence_threshold
            
            # Log the result
            if image_found:
                self.logger.info(f"SUCCESS, IMAGE FOUND! (Confidence: {max_val:.3f})")
            else:
                self.logger.warning(f"HEALTH IMAGE NOT FOUND! (Confidence: {max_val:.3f} < {confidence_threshold})")
            
            return {
                'success': True,
                'image_found': image_found,
                'confidence': max_val,
                'threshold': confidence_threshold,
                'match_location': max_loc
            }
            
        except Exception as e:
            self.logger.error(f"Image search test failed: {e}")
            return {'success': False, 'error': str(e)}

    def create_template_health_monitor(self, region: Tuple[int, int, int, int], 
                                      low_health_threshold: float = 0.3) -> str:
        """
        Create a health monitor using template matching instead of OCR
        
        Args:
            region: Region containing the health bar
            low_health_threshold: Confidence threshold for low health detection
            
        Returns:
            Condition name for the template monitor
        """
        condition_name = "template_health_monitor"
        
        def template_health_check():
            try:
                # Capture the region
                image = self.screen_capture.capture_region(*region)
                
                if image is None:
                    self.logger.error("Failed to capture health region image")
                    return None
                
                # Log capture details for debugging
                if not hasattr(self, '_template_capture_debugged'):
                    self.logger.info(f"Successfully captured template region: {region}, image shape: {image.shape}")
                    # Save the captured image for debugging
                    try:
                        from PIL import Image
                        import cv2
                        if len(image.shape) == 3:
                            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                        else:
                            pil_image = Image.fromarray(image)
                        pil_image.save('debug_template_capture.png')
                        self.logger.info("Saved captured template image as 'debug_template_capture.png' for debugging")
                    except Exception as e:
                        self.logger.warning(f"Could not save debug template image: {e}")
                    self._template_capture_debugged = True
                
                # Analyze health using template matching
                health_data = self._analyze_health_template(image, low_health_threshold)
                
                result = {
                    'health': health_data,
                    'is_low_health': health_data['confidence'] < low_health_threshold,
                    'region': region
                }
                
                return result
                
            except Exception as e:
                self.logger.error(f"Template health check failed: {e}")
                return None
        
        self.register_condition(condition_name, template_health_check, check_interval=0.5)
        return condition_name

    def create_dual_health_mana_monitor(self, region: Tuple[int, int, int, int], 
                                       low_health_threshold: float = 0.3,
                                       max_health: int = 1000, max_mana: int = 1000) -> str:
        """
        Create a monitor for both health and mana using color detection
        
        Args:
            region: Region containing both health and mana bars with numbers
            low_health_threshold: Health percentage threshold for low health
            max_health: Maximum health value
            max_mana: Maximum mana value
            
        Returns:
            Condition name for the dual monitor
        """
        condition_name = "dual_health_mana_monitor"
        
        def dual_health_mana_check():
            try:
                # Capture the region
                image = self.screen_capture.capture_region(*region)
                
                if image is None:
                    self.logger.error("Failed to capture dual health/mana region image")
                    return None
                
                # Log capture details for debugging
                if not hasattr(self, '_dual_capture_debugged'):
                    self.logger.info(f"Successfully captured dual region: {region}, image shape: {image.shape}")
                    # Save the captured image for debugging
                    try:
                        from PIL import Image
                        import cv2
                        if len(image.shape) == 3:
                            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                        else:
                            pil_image = Image.fromarray(image)
                        pil_image.save('debug_dual_capture.png')
                        self.logger.info("Saved captured dual image as 'debug_dual_capture.png' for debugging")
                    except Exception as e:
                        self.logger.warning(f"Could not save debug dual image: {e}")
                    self._dual_capture_debugged = True
                
                # Simple OCR test - always run this
                try:
                    from PIL import Image
                    import pytesseract
                    import cv2
                    if len(image.shape) == 3:
                        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                    else:
                        pil_image = Image.fromarray(image)
                    simple_text = pytesseract.image_to_string(pil_image).strip()
                    self.logger.info(f"Region {region} -> Image {image.shape} -> OCR: '{simple_text}'")
                    
                    # If OCR returns empty or garbage, try with image preprocessing
                    if not simple_text or any(char in simple_text for char in ['—', '"', '|', '~']):
                        # Try with image preprocessing
                        try:
                            import numpy as np
                            
                            # Convert to grayscale
                            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                            
                            # Try different preprocessing approaches
                            preprocessed_images = [
                                ('original', pil_image),
                                ('grayscale', Image.fromarray(gray)),
                                ('inverted', Image.fromarray(255 - gray)),
                                ('threshold', Image.fromarray(cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1])),
                                ('adaptive', Image.fromarray(cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2))),
                                ('morphology', Image.fromarray(cv2.morphologyEx(gray, cv2.MORPH_CLOSE, np.ones((2,2), np.uint8)))),
                            ]
                            
                            # Try each preprocessed image with different OCR configs
                            configs = [
                                r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789',
                                r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789',
                                r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789',
                                r'--oem 3 --psm 13 -c tessedit_char_whitelist=0123456789',
                            ]
                            
                            for img_name, processed_img in preprocessed_images:
                                for config in configs:
                                    try:
                                        test_text = pytesseract.image_to_string(processed_img, config=config).strip()
                                        if test_text and test_text.replace(' ', '').isdigit():
                                            self.logger.info(f"SUCCESS! {img_name} + {config}: '{test_text}'")
                                            # Save the successful preprocessed image
                                            processed_img.save(f'debug_success_{img_name}.png')
                                            break
                                    except:
                                        continue
                                else:
                                    continue
                                break
                        except Exception as e:
                            self.logger.error(f"Image preprocessing failed: {e}")
                except Exception as e:
                    self.logger.error(f"Simple OCR test failed: {e}")
                
                # Analyze both health and mana
                health_data, mana_data = self._analyze_dual_health_mana(image, max_health, max_mana)
                
                result = {
                    'health': health_data,
                    'mana': mana_data,
                    'is_low_health': health_data['percentage'] < low_health_threshold,
                    'region': region
                }
                
                return result
                
            except Exception as e:
                self.logger.error(f"Dual health/mana check failed: {e}")
                return None
        
        self.register_condition(condition_name, dual_health_mana_check, check_interval=0.5)
        return condition_name

    def create_health_monitor(self, health_region: Tuple[int, int, int, int], 
                            low_health_threshold: float = 0.3) -> str:
        """
        Create a health monitoring condition
        
        Args:
            health_region: (x, y, width, height) region of health bar
            low_health_threshold: Threshold for low health (0.0 to 1.0)
            
        Returns:
            Condition name for the health monitor
        """
        condition_name = "health_monitor"
        
        def health_check():
            try:
                # Capture health bar region
                health_image = self.screen_capture.capture_region(*health_region)
                
                if health_image is None:
                    self.logger.error("Failed to capture health region image")
                    return None
                
                # Log capture details for debugging
                if not hasattr(self, '_capture_debugged'):
                    self.logger.info(f"Successfully captured region: {health_region}, image shape: {health_image.shape}")
                    # Save the captured image for debugging
                    try:
                        from PIL import Image
                        import cv2
                        if len(health_image.shape) == 3:
                            pil_image = Image.fromarray(cv2.cvtColor(health_image, cv2.COLOR_BGR2RGB))
                        else:
                            pil_image = Image.fromarray(health_image)
                        pil_image.save('debug_health_capture.png')
                        self.logger.info("Saved captured image as 'debug_health_capture.png' for debugging")
                    except Exception as e:
                        self.logger.warning(f"Could not save debug image: {e}")
                    self._capture_debugged = True
                
                # Analyze health bar using OCR
                health_percentage = self._analyze_health_bar(health_image)
                
                result = {
                    'percentage': health_percentage,
                    'is_low': health_percentage < low_health_threshold,
                    'region': health_region
                }
                
                return result
                
            except Exception as e:
                self.logger.error(f"Health check failed: {e}")
                return None
        
        self.register_condition(condition_name, health_check, check_interval=0.5)
        return condition_name
    
    def create_text_monitor(self, text_to_find: str, 
                          region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """
        Create a text monitoring condition
        
        Args:
            text_to_find: Text to search for
            region: Optional region to search in
            
        Returns:
            Condition name for the text monitor
        """
        condition_name = f"text_monitor_{text_to_find.replace(' ', '_')}"
        
        def text_check():
            try:
                # Capture screen or region
                if region:
                    image = self.screen_capture.capture_region(*region)
                else:
                    image = self.screen_capture.capture_screen()
                
                # Search for text
                matches = self.ocr_engine.find_text(image, text_to_find, region)
                
                return {
                    'found': len(matches) > 0,
                    'matches': matches,
                    'text': text_to_find
                }
                
            except Exception as e:
                self.logger.error(f"Text check failed: {e}")
                return None
        
        self.register_condition(condition_name, text_check, check_interval=1.0)
        return condition_name
    
    def create_template_monitor(self, template_path: str, 
                              region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """
        Create a template monitoring condition
        
        Args:
            template_path: Path to template image
            region: Optional region to search in
            
        Returns:
            Condition name for the template monitor
        """
        condition_name = f"template_monitor_{template_path.split('/')[-1].split('.')[0]}"
        
        def template_check():
            try:
                # Capture screen or region
                if region:
                    image = self.screen_capture.capture_region(*region)
                else:
                    image = self.screen_capture.capture_screen()
                
                # Find template
                location = self.computer_vision.find_template(image, template_path)
                
                return {
                    'found': location is not None,
                    'location': location,
                    'template': template_path
                }
                
            except Exception as e:
                self.logger.error(f"Template check failed: {e}")
                return None
        
        self.register_condition(condition_name, template_check, check_interval=1.0)
        return condition_name
    
    def create_color_monitor(self, target_color: Tuple[int, int, int], 
                           region: Tuple[int, int, int, int], 
                           tolerance: int = 30) -> str:
        """
        Create a color monitoring condition
        
        Args:
            target_color: BGR color to monitor
            region: Region to monitor
            tolerance: Color tolerance
            
        Returns:
            Condition name for the color monitor
        """
        condition_name = f"color_monitor_{target_color}"
        
        def color_check():
            try:
                # Capture region
                image = self.screen_capture.capture_region(*region)
                
                # Find color regions
                color_regions = self.computer_vision.detect_color_region(
                    image, target_color, tolerance
                )
                
                return {
                    'found': len(color_regions) > 0,
                    'regions': color_regions,
                    'color': target_color
                }
                
            except Exception as e:
                self.logger.error(f"Color check failed: {e}")
                return None
        
        self.register_condition(condition_name, color_check, check_interval=0.5)
        return condition_name
    
    def _analyze_health_bar(self, health_image: np.ndarray) -> float:
        """
        Analyze health bar image to determine health percentage using OCR
        
        Args:
            health_image: Image of health bar region
            
        Returns:
            Health percentage (0.0 to 1.0)
        """
        try:
            # Use OCR to read the health number
            current_health = self._read_health_number(health_image)
            
            if current_health is None:
                self.logger.warning("Could not read health number from image")
                return 0.0
            
            # Get max health from configuration
            max_health = self.config.get('automation', {}).get('health_monitoring', {}).get('max_health', 1000)
            
            if max_health <= 0:
                self.logger.error(f"Invalid max health value: {max_health}")
                return 0.0
            
            # Calculate percentage
            health_percentage = current_health / max_health
            health_percentage = min(1.0, max(0.0, health_percentage))  # Clamp between 0 and 1
            
            # Only log health calculation once
            if not hasattr(self, '_health_calc_logged'):
                self.logger.info(f"Health calculation: {current_health}/{max_health} = {health_percentage:.1%}")
                self._health_calc_logged = True
            return health_percentage
            
        except Exception as e:
            self.logger.error(f"Health bar analysis failed: {e}")
            return 0.0
    
    def _read_health_number(self, health_image: np.ndarray) -> Optional[int]:
        """
        Read health number from image using OCR with multiple preprocessing attempts
        
        Args:
            health_image: Image of health bar region
            
        Returns:
            Current health value or None if reading failed
        """
        try:
            from PIL import Image
            import pytesseract
            import cv2
            import numpy as np
            
            # Convert to PIL Image
            if len(health_image.shape) == 3:
                pil_image = Image.fromarray(cv2.cvtColor(health_image, cv2.COLOR_BGR2RGB))
            else:
                pil_image = Image.fromarray(health_image)
            
            # Try multiple OCR configurations
            ocr_configs = [
                # Config 1: Numbers only, single word
                r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789',
                # Config 2: Numbers only, single text line
                r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789',
                # Config 3: Numbers only, single character
                r'--oem 3 --psm 10 -c tessedit_char_whitelist=0123456789',
                # Config 4: Default config for numbers
                r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789',
                # Config 5: No whitelist, single word
                r'--oem 3 --psm 8',
            ]
            
            # Try different image preprocessing
            processed_images = []
            
            # Original grayscale
            gray_image = pil_image.convert('L')
            processed_images.append(('grayscale', gray_image))
            
            # Otsu thresholding
            gray_array = np.array(gray_image)
            _, thresh = cv2.threshold(gray_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(('otsu_thresh', Image.fromarray(thresh)))
            
            # Adaptive thresholding
            adaptive_thresh = cv2.adaptiveThreshold(gray_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            processed_images.append(('adaptive_thresh', Image.fromarray(adaptive_thresh)))
            
            # Inverted threshold
            _, inv_thresh = cv2.threshold(gray_array, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            processed_images.append(('inverted_thresh', Image.fromarray(inv_thresh)))
            
            # Try each combination
            for img_name, processed_image in processed_images:
                for config_name, custom_config in zip(['config1', 'config2', 'config3', 'config4', 'config5'], ocr_configs):
                    try:
                        text = pytesseract.image_to_string(processed_image, config=custom_config).strip()
                        
                        # Log what OCR is actually reading for debugging (only once)
                        if not hasattr(self, '_ocr_debugged'):
                            self.logger.info(f"OCR attempt - {img_name} + {config_name}: '{text}' (length: {len(text)})")
                        
                        # Extract number from text
                        if text and text.isdigit():
                            health_value = int(text)
                            # Only log once when we successfully read health
                            if not hasattr(self, '_ocr_logged'):
                                self.logger.info(f"OCR successfully reading health: {health_value} using {img_name} + {config_name}")
                                self._ocr_logged = True
                            return health_value
                        elif text and any(c.isdigit() for c in text):
                            # Try to extract numbers from mixed text
                            import re
                            numbers = re.findall(r'\d+', text)
                            if numbers:
                                health_value = int(numbers[0])
                                if not hasattr(self, '_ocr_logged'):
                                    self.logger.info(f"OCR extracted number from mixed text: {health_value} from '{text}' using {img_name} + {config_name}")
                                    self._ocr_logged = True
                                return health_value
                    except Exception as e:
                        continue
            
            # If we get here, all attempts failed
            if not hasattr(self, '_ocr_failure_logged'):
                self.logger.warning("All OCR attempts failed to read health number")
                self._ocr_failure_logged = True
            return None
                
        except Exception as e:
            self.logger.error(f"OCR health reading failed: {e}")
            return None

    def _analyze_dual_health_mana(self, image: np.ndarray, max_health: int, max_mana: int) -> tuple:
        """
        Analyze image to extract both health and mana using color detection and OCR
        
        Args:
            image: Captured image containing health and mana bars with numbers
            max_health: Maximum health value
            max_mana: Maximum mana value
            
        Returns:
            Tuple of (health_data, mana_data) dictionaries
        """
        try:
            import cv2
            import numpy as np
            
            # Convert to different color spaces for better color detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define color ranges for health (red) and mana (blue)
            # Red range for health
            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 50, 50])
            upper_red2 = np.array([180, 255, 255])
            
            # Blue range for mana
            lower_blue = np.array([100, 50, 50])
            upper_blue = np.array([130, 255, 255])
            
            # Create masks for red and blue regions
            mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask_red = mask_red1 + mask_red2
            mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
            
            # Find contours for health and mana bars
            health_contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            mana_contours, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Debug contour detection
            if not hasattr(self, '_contour_debugged'):
                self.logger.info(f"Found {len(health_contours)} red contours, {len(mana_contours)} blue contours")
                self._contour_debugged = True
            
            # Get the largest contours (main bars)
            health_bar = max(health_contours, key=cv2.contourArea) if health_contours else None
            mana_bar = max(mana_contours, key=cv2.contourArea) if mana_contours else None
            
            # Extract numbers using OCR
            numbers = self._extract_all_numbers(image)
            
            # Map numbers to health/mana based on position relative to bars
            health_value = None
            mana_value = None
            
            if health_bar is not None and mana_bar is not None:
                # Get bounding boxes
                health_bbox = cv2.boundingRect(health_bar)
                mana_bbox = cv2.boundingRect(mana_bar)
                
                # Determine which bar is on top (health is usually above mana)
                if health_bbox[1] < mana_bbox[1]:  # health is above mana
                    health_y_center = health_bbox[1] + health_bbox[3] // 2
                    mana_y_center = mana_bbox[1] + mana_bbox[3] // 2
                else:  # mana is above health
                    health_y_center = mana_bbox[1] + mana_bbox[3] // 2
                    mana_y_center = health_bbox[1] + health_bbox[3] // 2
                
                # Map numbers to health/mana based on Y position
                for number in numbers:
                    num_y = number['y'] + number['height'] // 2
                    if abs(num_y - health_y_center) < abs(num_y - mana_y_center):
                        health_value = number['value']
                    else:
                        mana_value = number['value']
            else:
                # Fallback: if color detection fails, assume top number is health, bottom is mana
                if not hasattr(self, '_fallback_used'):
                    self.logger.warning("Color detection failed, using fallback: assuming top number is health, bottom is mana")
                    self._fallback_used = True
                
                if len(numbers) >= 2:
                    # Sort by Y position (top to bottom)
                    sorted_numbers = sorted(numbers, key=lambda n: n['y'])
                    health_value = sorted_numbers[0]['value']  # Top number
                    mana_value = sorted_numbers[1]['value']   # Bottom number
                elif len(numbers) == 1:
                    # Only one number found, assume it's health
                    health_value = numbers[0]['value']
            
            # Calculate percentages
            health_percentage = (health_value / max_health) if health_value else 0.0
            mana_percentage = (mana_value / max_mana) if mana_value else 0.0
            
            health_data = {
                'value': health_value,
                'percentage': health_percentage,
                'max': max_health
            }
            
            mana_data = {
                'value': mana_value,
                'percentage': mana_percentage,
                'max': max_mana
            }
            
            # Log results
            if not hasattr(self, '_dual_analysis_logged'):
                self.logger.info(f"Dual analysis - Health: {health_value}/{max_health} ({health_percentage:.1%}), Mana: {mana_value}/{max_mana} ({mana_percentage:.1%})")
                self._dual_analysis_logged = True
            
            return health_data, mana_data
            
        except Exception as e:
            self.logger.error(f"Dual health/mana analysis failed: {e}")
            return {'value': None, 'percentage': 0.0, 'max': max_health}, {'value': None, 'percentage': 0.0, 'max': max_mana}

    def _extract_all_numbers(self, image: np.ndarray) -> list:
        """
        Extract all numbers from image using OCR
        
        Returns:
            List of dictionaries with 'value', 'x', 'y', 'width', 'height'
        """
        try:
            from PIL import Image
            import pytesseract
            import cv2
            import numpy as np
            import re
            
            # Convert to PIL Image
            if len(image.shape) == 3:
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            else:
                pil_image = Image.fromarray(image)
            
            # Try different preprocessing approaches
            processed_images = []
            
            # Grayscale
            gray_image = pil_image.convert('L')
            processed_images.append(('grayscale', gray_image))
            
            # Otsu thresholding
            gray_array = np.array(gray_image)
            _, thresh = cv2.threshold(gray_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(('otsu_thresh', Image.fromarray(thresh)))
            
            # Try OCR on each processed image
            for img_name, processed_image in processed_images:
                try:
                    # Use OCR to get text with bounding boxes
                    data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
                    
                    # Debug OCR output
                    if not hasattr(self, '_ocr_data_debugged'):
                        all_text = [text.strip() for text in data['text'] if text.strip()]
                        self.logger.info(f"OCR data from {img_name}: {all_text}")
                        self._ocr_data_debugged = True
                    
                    numbers = []
                    for i in range(len(data['text'])):
                        text = data['text'][i].strip()
                        if text and re.match(r'^\d+$', text):  # Only pure numbers
                            x = data['left'][i]
                            y = data['top'][i]
                            width = data['width'][i]
                            height = data['height'][i]
                            value = int(text)
                            
                            numbers.append({
                                'value': value,
                                'x': x,
                                'y': y,
                                'width': width,
                                'height': height
                            })
                    
                    if numbers:
                        if not hasattr(self, '_numbers_extracted'):
                            self.logger.info(f"Extracted {len(numbers)} numbers using {img_name}: {[n['value'] for n in numbers]}")
                            self._numbers_extracted = True
                        return numbers
                        
                except Exception as e:
                    continue
            
            return []
            
        except Exception as e:
            self.logger.error(f"Number extraction failed: {e}")
            return []

    def _analyze_health_template(self, image: np.ndarray, low_health_threshold: float) -> dict:
        """
        Analyze health using template matching approach
        
        Args:
            image: Captured image of the health bar region
            low_health_threshold: Confidence threshold for low health detection
            
        Returns:
            Dictionary with health analysis results
        """
        try:
            import cv2
            import numpy as np
            
            # Check if we have a saved health bar template
            template_path = 'health_bar_template.png'
            
            if not hasattr(self, '_template_created'):
                # First time - create template from current image
                try:
                    from PIL import Image
                    if len(image.shape) == 3:
                        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                    else:
                        pil_image = Image.fromarray(image)
                    pil_image.save(template_path)
                    self.logger.info(f"Created health bar template: {template_path}")
                    self._template_created = True
                    
                    # Return high confidence for first run (assume full health)
                    return {
                        'confidence': 1.0,
                        'template_created': True,
                        'method': 'template_matching'
                    }
                except Exception as e:
                    self.logger.error(f"Failed to create template: {e}")
                    return {
                        'confidence': 0.0,
                        'template_created': False,
                        'method': 'template_matching'
                    }
            
            # Load the template
            try:
                template = cv2.imread(template_path, cv2.IMREAD_COLOR)
                if template is None:
                    self.logger.error("Could not load health bar template")
                    return {
                        'confidence': 0.0,
                        'template_loaded': False,
                        'method': 'template_matching'
                    }
                
                # Perform template matching
                result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                # Log template matching results
                if not hasattr(self, '_template_matching_logged'):
                    self.logger.info(f"Template matching confidence: {max_val:.3f} (threshold: {low_health_threshold})")
                    self._template_matching_logged = True
                
                return {
                    'confidence': max_val,
                    'template_loaded': True,
                    'method': 'template_matching',
                    'match_location': max_loc
                }
                
            except Exception as e:
                self.logger.error(f"Template matching failed: {e}")
                return {
                    'confidence': 0.0,
                    'template_loaded': False,
                    'method': 'template_matching'
                }
                
        except Exception as e:
            self.logger.error(f"Health template analysis failed: {e}")
            return {
                'confidence': 0.0,
                'method': 'template_matching'
            }

class StateMonitorError(Exception):
    """Custom exception for state monitoring errors"""
    pass
