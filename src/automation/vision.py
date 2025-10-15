"""
Computer vision module for screen recognition and image detection.
This module provides the foundation for detecting objects, text, and patterns on screen.
"""
import cv2
import numpy as np
import mss
from typing import List, Tuple, Optional, Dict, Any
import logging
from PIL import Image
import pyautogui
import threading

logger = logging.getLogger(__name__)


class ScreenCapture:
    """Handle screen capture operations with thread safety."""
    
    def __init__(self):
        """Initialize ScreenCapture."""
        # Use thread-local storage for mss instances
        self._local = threading.local()
        logger.info("ScreenCapture initialized with thread safety")
    
    def _get_sct(self):
        """Get thread-local mss instance."""
        if not hasattr(self._local, 'sct') or self._local.sct is None:
            self._local.sct = mss.mss()
        return self._local.sct
    
    def capture_screen(self, region: Optional[Dict[str, int]] = None) -> np.ndarray:
        """
        Capture screenshot of entire screen or specified region.
        
        Args:
            region: Dictionary with 'top', 'left', 'width', 'height' keys.
                   If None, captures entire screen.
        
        Returns:
            Screenshot as numpy array in BGR format
        """
        try:
            # Try mss first (faster)
            sct = self._get_sct()
            
            if region is None:
                # Capture entire screen
                screenshot = sct.grab(sct.monitors[1])  # Primary monitor
            else:
                screenshot = sct.grab(region)
            
            # Convert to numpy array and change from RGBA to BGR
            img_array = np.array(screenshot)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
            
            logger.debug(f"Captured screen region: {region or 'full screen'}")
            return img_bgr
            
        except Exception as e:
            logger.warning(f"MSS screen capture failed: {e}, falling back to PyAutoGUI")
            return self._capture_screen_fallback(region)
    
    def _capture_screen_fallback(self, region: Optional[Dict[str, int]] = None) -> np.ndarray:
        """
        Fallback screen capture using PyAutoGUI (slower but more compatible).
        
        Args:
            region: Dictionary with 'top', 'left', 'width', 'height' keys.
        
        Returns:
            Screenshot as numpy array in BGR format
        """
        try:
            if region is None:
                # Capture entire screen
                screenshot = pyautogui.screenshot()
            else:
                # Convert region format for PyAutoGUI
                screenshot = pyautogui.screenshot(
                    region=(region['left'], region['top'], 
                           region['width'], region['height'])
                )
            
            # Convert PIL image to numpy array
            img_array = np.array(screenshot)
            # Convert from RGB to BGR for OpenCV
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            logger.debug(f"Captured screen using PyAutoGUI fallback: {region or 'full screen'}")
            return img_bgr
            
        except Exception as e:
            logger.error(f"PyAutoGUI screen capture also failed: {e}")
            return np.array([])
    
    def save_screenshot(self, filepath: str, region: Optional[Dict[str, int]] = None) -> bool:
        """
        Save screenshot to file.
        
        Args:
            filepath: Path to save the screenshot
            region: Screen region to capture
        
        Returns:
            True if successful, False otherwise
        """
        try:
            screenshot = self.capture_screen(region)
            if screenshot.size > 0:
                cv2.imwrite(filepath, screenshot)
                logger.info(f"Screenshot saved to {filepath}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            return False
    
    def cleanup(self):
        """Cleanup thread-local resources."""
        try:
            if hasattr(self._local, 'sct') and self._local.sct is not None:
                self._local.sct.close()
                self._local.sct = None
        except Exception as e:
            logger.debug(f"Error cleaning up screen capture: {e}")
    
    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.cleanup()
        except (TypeError, AttributeError):
            pass


class ImageMatcher:
    """Handle image matching and template detection."""
    
    def __init__(self, threshold: float = 0.8):
        """
        Initialize ImageMatcher.
        
        Args:
            threshold: Matching threshold (0.0 to 1.0)
        """
        self.threshold = threshold
        logger.info(f"ImageMatcher initialized with threshold {threshold}")
    
    def find_template(self, screen: np.ndarray, template: np.ndarray, 
                     threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Find template matches in screen image.
        
        Args:
            screen: Screen image as numpy array
            template: Template image as numpy array
            threshold: Override default threshold
        
        Returns:
            List of dictionaries with 'position', 'confidence', 'center' keys
        """
        try:
            match_threshold = threshold or self.threshold
            
            # Perform template matching
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= match_threshold)
            
            matches = []
            h, w = template.shape[:2]
            
            for pt in zip(*locations[::-1]):  # Switch columns and rows
                confidence = result[pt[1], pt[0]]
                center = (pt[0] + w // 2, pt[1] + h // 2)
                
                matches.append({
                    'position': pt,
                    'confidence': float(confidence),
                    'center': center,
                    'size': (w, h)
                })
            
            logger.debug(f"Found {len(matches)} template matches")
            return matches
            
        except Exception as e:
            logger.error(f"Template matching failed: {e}")
            return []
    
    def find_best_match(self, screen: np.ndarray, template: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Find the best template match in screen image.
        
        Args:
            screen: Screen image as numpy array
            template: Template image as numpy array
        
        Returns:
            Dictionary with match info or None if no match found
        """
        try:
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= self.threshold:
                h, w = template.shape[:2]
                center = (max_loc[0] + w // 2, max_loc[1] + h // 2)
                
                return {
                    'position': max_loc,
                    'confidence': float(max_val),
                    'center': center,
                    'size': (w, h)
                }
            
            logger.debug(f"No match found above threshold {self.threshold}")
            return None
            
        except Exception as e:
            logger.error(f"Best match search failed: {e}")
            return None
    
    def load_template(self, filepath: str) -> Optional[np.ndarray]:
        """
        Load template image from file.
        
        Args:
            filepath: Path to template image file
        
        Returns:
            Template image as numpy array or None if loading failed
        """
        try:
            template = cv2.imread(filepath, cv2.IMREAD_COLOR)
            if template is not None:
                logger.debug(f"Loaded template from {filepath}")
                return template
            else:
                logger.error(f"Failed to load template from {filepath}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading template: {e}")
            return None


class ColorDetector:
    """Handle color-based detection and filtering."""
    
    def __init__(self):
        """Initialize ColorDetector."""
        logger.info("ColorDetector initialized")
    
    def find_color_regions(self, image: np.ndarray, color_range: Dict[str, Tuple]) -> List[Dict[str, Any]]:
        """
        Find regions matching a specific color range.
        
        Args:
            image: Image as numpy array
            color_range: Dictionary with 'lower' and 'upper' HSV color bounds
        
        Returns:
            List of detected regions with bounding boxes
        """
        try:
            # Convert BGR to HSV for color filtering
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Create mask for color range
            mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            regions = []
            for contour in contours:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)
                
                regions.append({
                    'bbox': (x, y, w, h),
                    'center': (x + w // 2, y + h // 2),
                    'area': area,
                    'contour': contour
                })
            
            logger.debug(f"Found {len(regions)} color regions")
            return regions
            
        except Exception as e:
            logger.error(f"Color detection failed: {e}")
            return []


class VisionController:
    """Main controller for computer vision operations."""
    
    def __init__(self, match_threshold: float = 0.8):
        """
        Initialize VisionController.
        
        Args:
            match_threshold: Default matching threshold
        """
        self.screen_capture = ScreenCapture()
        self.image_matcher = ImageMatcher(threshold=match_threshold)
        self.color_detector = ColorDetector()
        
        # Cache for templates
        self.template_cache = {}
        
        logger.info("VisionController initialized")
    
    def find_on_screen(self, template_path: str, region: Optional[Dict[str, int]] = None,
                      threshold: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Find template on screen and return best match.
        
        Args:
            template_path: Path to template image file
            region: Screen region to search in
            threshold: Override default threshold
        
        Returns:
            Match information or None if not found
        """
        try:
            # Load template (with caching)
            if template_path not in self.template_cache:
                template = self.image_matcher.load_template(template_path)
                if template is None:
                    return None
                self.template_cache[template_path] = template
            else:
                template = self.template_cache[template_path]
            
            # Capture screen
            screen = self.screen_capture.capture_screen(region)
            if screen.size == 0:
                return None
            
            # Find best match
            match = self.image_matcher.find_best_match(screen, template)
            
            # Adjust coordinates if region was specified
            if match and region:
                match['position'] = (
                    match['position'][0] + region['left'],
                    match['position'][1] + region['top']
                )
                match['center'] = (
                    match['center'][0] + region['left'],
                    match['center'][1] + region['top']
                )
            
            return match
            
        except Exception as e:
            logger.error(f"Screen search failed: {e}")
            return None
    
    def wait_for_image(self, template_path: str, timeout: float = 10.0,
                      check_interval: float = 0.5, region: Optional[Dict[str, int]] = None) -> Optional[Dict[str, Any]]:
        """
        Wait for an image to appear on screen.
        
        Args:
            template_path: Path to template image file
            timeout: Maximum time to wait in seconds
            check_interval: Time between checks in seconds
            region: Screen region to search in
        
        Returns:
            Match information or None if timeout reached
        """
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            match = self.find_on_screen(template_path, region)
            if match:
                logger.info(f"Image found after {time.time() - start_time:.2f} seconds")
                return match
            
            time.sleep(check_interval)
        
        logger.warning(f"Image not found within {timeout} seconds")
        return None
    
    def get_pixel_color(self, x: int, y: int) -> Tuple[int, int, int]:
        """
        Get RGB color of pixel at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Returns:
            RGB color tuple
        """
        try:
            # Using pyautogui for single pixel capture (faster than full screenshot)
            pixel = pyautogui.pixel(x, y)
            logger.debug(f"Pixel at ({x}, {y}): {pixel}")
            return pixel
            
        except Exception as e:
            logger.error(f"Failed to get pixel color: {e}")
            return (0, 0, 0)
    
    def wait_for_pixel_color(self, x: int, y: int, target_color: Tuple[int, int, int], 
                            tolerance: int = 10, timeout: float = 10.0, 
                            check_interval: float = 0.1) -> bool:
        """
        Wait for a pixel to change to a specific color.
        
        Args:
            x: X coordinate of pixel to monitor
            y: Y coordinate of pixel to monitor
            target_color: Target RGB color as tuple (r, g, b)
            tolerance: Acceptable difference per color component (0-255)
            timeout: Maximum time to wait in seconds
            check_interval: Time between checks in seconds
            
        Returns:
            True if pixel reached target color, False if timeout
        """
        import time
        
        start_time = time.time()
        
        logger.info(f"Waiting for pixel at ({x}, {y}) to become RGB{target_color} (tolerance={tolerance})")
        
        while time.time() - start_time < timeout:
            current_color = self.get_pixel_color(x, y)
            
            # Check if current color matches target within tolerance
            if self._colors_match(current_color, target_color, tolerance):
                elapsed = time.time() - start_time
                logger.info(f"Pixel color matched after {elapsed:.2f} seconds")
                return True
            
            time.sleep(check_interval)
        
        logger.warning(f"Pixel color did not match within {timeout} seconds")
        return False
    
    def wait_for_pixel_change(self, x: int, y: int, timeout: float = 10.0, 
                             check_interval: float = 0.1, min_change: int = 10) -> Tuple[bool, Tuple[int, int, int]]:
        """
        Wait for a pixel to change from its current color.
        
        Args:
            x: X coordinate of pixel to monitor
            y: Y coordinate of pixel to monitor
            timeout: Maximum time to wait in seconds
            check_interval: Time between checks in seconds
            min_change: Minimum total RGB change to consider significant
            
        Returns:
            Tuple of (changed, new_color) where changed is bool and new_color is RGB tuple
        """
        import time
        
        # Get initial color
        initial_color = self.get_pixel_color(x, y)
        start_time = time.time()
        
        logger.info(f"Waiting for pixel at ({x}, {y}) to change from RGB{initial_color}")
        
        while time.time() - start_time < timeout:
            current_color = self.get_pixel_color(x, y)
            
            # Calculate total color difference
            color_diff = sum(abs(a - b) for a, b in zip(initial_color, current_color))
            
            if color_diff >= min_change:
                elapsed = time.time() - start_time
                logger.info(f"Pixel changed after {elapsed:.2f} seconds: RGB{initial_color} → RGB{current_color}")
                return True, current_color
            
            time.sleep(check_interval)
        
        logger.warning(f"Pixel did not change within {timeout} seconds")
        return False, initial_color
    
    def _colors_match(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], tolerance: int) -> bool:
        """
        Check if two RGB colors match within tolerance.
        
        Args:
            color1: First RGB color tuple
            color2: Second RGB color tuple
            tolerance: Maximum difference per color component
            
        Returns:
            True if colors match within tolerance
        """
        return all(abs(a - b) <= tolerance for a, b in zip(color1, color2))
    
    def clear_template_cache(self):
        """Clear the template cache to free memory."""
        self.template_cache.clear()
        logger.info("Template cache cleared")


# Helper functions for creating color ranges
def create_hsv_range(hue: int, saturation: int, value: int, tolerance: int = 20) -> Dict[str, Tuple]:
    """
    Create HSV color range for color detection.
    
    Args:
        hue: Hue value (0-179)
        saturation: Saturation value (0-255)
        value: Value/brightness (0-255)
        tolerance: Tolerance for the range
    
    Returns:
        Dictionary with 'lower' and 'upper' HSV bounds
    """
    return {
        'lower': (max(0, hue - tolerance), max(0, saturation - tolerance), max(0, value - tolerance)),
        'upper': (min(179, hue + tolerance), min(255, saturation + tolerance), min(255, value + tolerance))
    }


def rgb_to_hsv_range(r: int, g: int, b: int, tolerance: int = 20) -> Dict[str, Tuple]:
    """
    Convert RGB color to HSV range for detection.
    
    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)
        tolerance: Tolerance for the range
    
    Returns:
        Dictionary with 'lower' and 'upper' HSV bounds
    """
    # Convert RGB to HSV
    rgb_array = np.uint8([[[r, g, b]]])
    hsv_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2HSV)
    h, s, v = hsv_array[0][0]
    
    return create_hsv_range(h, s, v, tolerance)