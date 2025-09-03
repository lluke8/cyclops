# Cyclops - Philosophical Approach to Robust Automation

## Core Principles

### 1. Reactive Automation Philosophy
- **State-Driven**: Automation should respond to screen state changes, not time-based triggers
- **Conditional Logic**: Every action should be preceded by a condition check
- **Fail-Safe Design**: Always have an escape mechanism and error recovery

### 2. Robustness Strategies

#### A. Timing and Delays
```python
# Recommended timing strategies:

# 1. Adaptive Delays
def adaptive_delay(base_delay=1.0, variance=0.2):
    """Add randomness to prevent detection"""
    import random
    actual_delay = base_delay + random.uniform(-variance, variance)
    time.sleep(actual_delay)

# 2. Wait for Conditions
def wait_for_condition(condition_func, timeout=10, check_interval=0.5):
    """Wait until condition is met or timeout occurs"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(check_interval)
    return False

# 3. Cooldown Management
class CooldownManager:
    def __init__(self):
        self.last_actions = {}
    
    def can_act(self, action_name, cooldown_seconds):
        now = time.time()
        last_action = self.last_actions.get(action_name, 0)
        return (now - last_action) >= cooldown_seconds
    
    def record_action(self, action_name):
        self.last_actions[action_name] = time.time()
```

#### B. Coordinate System Management
```python
# Recommended coordinate strategies:

# 1. Relative vs Absolute Coordinates
class CoordinateSystem:
    def __init__(self, base_region=None):
        self.base_region = base_region or (0, 0, 1920, 1080)
    
    def to_absolute(self, relative_x, relative_y):
        """Convert relative coordinates to absolute"""
        base_x, base_y, _, _ = self.base_region
        return base_x + relative_x, base_y + relative_y
    
    def to_relative(self, absolute_x, absolute_y):
        """Convert absolute coordinates to relative"""
        base_x, base_y, _, _ = self.base_region
        return absolute_x - base_x, absolute_y - base_y

# 2. Region-Based Operations
def click_in_region(region, offset_x=0, offset_y=0):
    """Click within a defined region with optional offset"""
    x, y, w, h = region
    target_x = x + (w // 2) + offset_x
    target_y = y + (h // 2) + offset_y
    pyautogui.click(target_x, target_y)

# 3. Dynamic Region Detection
def find_dynamic_region(template_image, confidence=0.8):
    """Find region dynamically using template matching"""
    screenshot = pyautogui.screenshot()
    location = pyautogui.locate(template_image, screenshot, confidence=confidence)
    return location
```

#### C. Error Handling and Recovery
```python
# Recommended error handling strategies:

# 1. Retry Mechanism
def retry_operation(operation, max_retries=3, delay=1.0):
    """Retry operation with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay * (2 ** attempt))

# 2. Graceful Degradation
def safe_automation_sequence(sequence):
    """Execute automation sequence with error recovery"""
    for step in sequence:
        try:
            step.execute()
        except StepFailedException as e:
            logger.warning(f"Step failed: {e}")
            if step.is_critical:
                raise e
            else:
                step.recover()
                continue

# 3. State Validation
def validate_state_before_action(action, required_state):
    """Validate current state before performing action"""
    current_state = get_current_state()
    if not matches_required_state(current_state, required_state):
        raise StateMismatchException(f"Expected {required_state}, got {current_state}")
    return action()
```

#### D. Image Matching Robustness
```python
# Recommended image matching strategies:

# 1. Multi-Scale Template Matching
def robust_template_matching(template, screenshot, scales=[0.8, 0.9, 1.0, 1.1, 1.2]):
    """Template matching with multiple scales"""
    best_match = None
    best_confidence = 0
    
    for scale in scales:
        scaled_template = cv2.resize(template, None, fx=scale, fy=scale)
        matches = pyautogui.locateAll(scaled_template, screenshot, confidence=0.7)
        
        for match in matches:
            confidence = pyautogui.locate(scaled_template, screenshot, confidence=0.7)
            if confidence and confidence > best_confidence:
                best_confidence = confidence
                best_match = match
    
    return best_match

# 2. Color-Based Detection
def detect_color_region(image, target_color, tolerance=30):
    """Detect regions with specific color"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array([target_color[0] - tolerance, 50, 50])
    upper = np.array([target_color[0] + tolerance, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

# 3. OCR with Confidence Scoring
def robust_ocr(image, min_confidence=0.7):
    """OCR with confidence validation"""
    text_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    
    valid_text = []
    for i, conf in enumerate(text_data['conf']):
        if int(conf) > min_confidence * 100:
            text = text_data['text'][i].strip()
            if text:
                valid_text.append({
                    'text': text,
                    'confidence': conf / 100,
                    'bbox': (text_data['left'][i], text_data['top'][i], 
                            text_data['width'][i], text_data['height'][i])
                })
    
    return valid_text
```

### 3. Safety Mechanisms

#### A. Fail-Safe Implementation
```python
class FailSafeManager:
    def __init__(self):
        self.fail_safe_position = (0, 0)
        self.fail_safe_enabled = True
        self.last_mouse_position = pyautogui.position()
    
    def check_fail_safe(self):
        """Check if mouse is in fail-safe position"""
        current_pos = pyautogui.position()
        if current_pos == self.fail_safe_position:
            raise FailSafeTriggeredException("Mouse moved to fail-safe position")
    
    def monitor_mouse(self):
        """Continuously monitor mouse position"""
        while True:
            current_pos = pyautogui.position()
            if current_pos != self.last_mouse_position:
                self.last_mouse_position = current_pos
                self.check_fail_safe()
            time.sleep(0.1)
```

#### B. Timeout Management
```python
class TimeoutManager:
    def __init__(self):
        self.timeouts = {}
    
    def set_timeout(self, operation_name, timeout_seconds):
        """Set timeout for an operation"""
        self.timeouts[operation_name] = {
            'start_time': time.time(),
            'duration': timeout_seconds
        }
    
    def check_timeout(self, operation_name):
        """Check if operation has timed out"""
        if operation_name not in self.timeouts:
            return False
        
        timeout_info = self.timeouts[operation_name]
        elapsed = time.time() - timeout_info['start_time']
        return elapsed > timeout_info['duration']
    
    def clear_timeout(self, operation_name):
        """Clear timeout for an operation"""
        if operation_name in self.timeouts:
            del self.timeouts[operation_name]
```

### 4. Performance Optimization

#### A. Efficient Screen Capture
```python
class EfficientScreenCapture:
    def __init__(self, region=None):
        self.region = region
        self.last_capture = None
        self.capture_cache = {}
    
    def capture_if_changed(self, region=None):
        """Only capture if screen has changed"""
        target_region = region or self.region
        current_capture = pyautogui.screenshot(region=target_region)
        
        if self.last_capture is None:
            self.last_capture = current_capture
            return current_capture
        
        # Simple change detection
        if self.last_capture != current_capture:
            self.last_capture = current_capture
            return current_capture
        
        return self.last_capture
```

#### B. Caching Strategies
```python
class TemplateCache:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def get_template(self, template_path):
        """Get cached template or load from disk"""
        if template_path in self.cache:
            template, load_time = self.cache[template_path]
            if time.time() - load_time < self.cache_ttl:
                return template
        
        # Load template from disk
        template = cv2.imread(template_path)
        self.cache[template_path] = (template, time.time())
        return template
```

### 5. Configuration Management

#### A. Environment-Specific Settings
```python
class EnvironmentConfig:
    def __init__(self):
        self.environments = {
            'development': {
                'debug_mode': True,
                'screenshot_save': True,
                'log_level': 'DEBUG'
            },
            'production': {
                'debug_mode': False,
                'screenshot_save': False,
                'log_level': 'INFO'
            },
            'vm': {
                'screen_region': (0, 0, 1920, 1080),
                'input_delay': 0.1,
                'capture_fps': 5
            }
        }
    
    def get_config(self, environment='production'):
        """Get configuration for specific environment"""
        return self.environments.get(environment, self.environments['production'])
```

### 6. Testing and Validation

#### A. Automated Testing
```python
class AutomationTester:
    def __init__(self):
        self.test_results = []
    
    def test_screen_capture(self):
        """Test screen capture functionality"""
        try:
            screenshot = pyautogui.screenshot()
            assert screenshot is not None
            self.test_results.append(('screen_capture', True, 'Success'))
        except Exception as e:
            self.test_results.append(('screen_capture', False, str(e)))
    
    def test_ocr_functionality(self):
        """Test OCR functionality"""
        try:
            # Create test image with known text
            test_image = create_test_image("TEST")
            text = pytesseract.image_to_string(test_image)
            assert "TEST" in text.upper()
            self.test_results.append(('ocr', True, 'Success'))
        except Exception as e:
            self.test_results.append(('ocr', False, str(e)))
    
    def run_all_tests(self):
        """Run all automation tests"""
        self.test_screen_capture()
        self.test_ocr_functionality()
        # Add more tests as needed
        
        return self.test_results
```

## Best Practices Summary

1. **Always validate state before actions**
2. **Use adaptive timing with randomization**
3. **Implement comprehensive error handling**
4. **Cache frequently used resources**
5. **Monitor for fail-safe conditions**
6. **Use relative coordinates when possible**
7. **Implement timeout mechanisms**
8. **Log all automation activities**
9. **Test automation routines thoroughly**
10. **Provide user feedback and control**

## Common Pitfalls to Avoid

1. **Hard-coded coordinates** - Use relative positioning
2. **Fixed timing** - Use adaptive delays
3. **No error handling** - Always handle exceptions
4. **Infinite loops** - Always have exit conditions
5. **No user control** - Provide stop mechanisms
6. **Poor logging** - Log all important events
7. **Resource leaks** - Clean up resources properly
8. **No testing** - Test all automation routines
