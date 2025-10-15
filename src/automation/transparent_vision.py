"""
Enhanced vision controller with transparency support for template matching.
This extends the base VisionController to handle PNG templates with alpha channels.
"""

import cv2
import numpy as np
import time
import threading
from typing import List, Tuple, Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from .vision import VisionController, ImageMatcher, ScreenCapture, ColorDetector

logger = logging.getLogger(__name__)

class TemplateWatcherEvent(Enum):
    """Types of template watcher events."""
    TEMPLATE_FOUND = "template_found"
    TEMPLATE_LOST = "template_lost"
    TEMPLATE_MOVED = "template_moved"

@dataclass
class TemplateWatcherConfig:
    """Configuration for a template watcher."""
    template_path: str
    callback: Callable[[Dict[str, Any]], None]
    event_type: TemplateWatcherEvent
    
    # Matching parameters
    threshold: float = 0.8
    use_transparency: bool = True
    region: Optional[Dict[str, int]] = None
    
    # Timing parameters
    check_interval: float = 0.5
    
    # Event filtering
    cooldown: float = 0.0
    trigger_once: bool = False
    
    # Movement detection (for TEMPLATE_MOVED)
    movement_threshold: int = 10  # pixels
    
    # Additional metadata
    name: str = ""
    enabled: bool = True

class PersistentTemplateWatcher:
    """A persistent template watcher that monitors for template appearances/disappearances."""
    
    def __init__(self, config: TemplateWatcherConfig, vision_controller):
        """Initialize the persistent template watcher."""
        self.config = config
        self.vision = vision_controller
        self.running = False
        self.thread = None
        self.last_trigger_time = 0.0
        self.trigger_count = 0
        self.last_match = None  # Store last found match for movement detection
        self.template_present = False  # Track if template is currently visible
    
    def start(self):
        """Start the template watcher in a separate thread."""
        if self.running:
            logger.warning(f"Template watcher '{self.config.name}' is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()
        logger.info(f"Started template watcher '{self.config.name}' for {self.config.template_path}")
    
    def stop(self):
        """Stop the template watcher."""
        if not self.running:
            return
        
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        try:
            # Cleanup screen capture resources for this thread
            if hasattr(self.vision, 'screen_capture'):
                self.vision.screen_capture.cleanup()
            logger.info(f"Stopped template watcher '{self.config.name}' (triggered {self.trigger_count} times)")
        except (TypeError, AttributeError):
            pass
    
    def _watch_loop(self):
        """Main watching loop that runs in a separate thread."""
        try:
            while self.running and self.config.enabled:
                if self._should_check():
                    self._check_template()
                
                time.sleep(self.config.check_interval)
                
        except Exception as e:
            logger.error(f"Error in template watcher '{self.config.name}': {e}")
        finally:
            self.running = False
    
    def _should_check(self) -> bool:
        """Check if enough time has passed since last trigger (cooldown)."""
        if self.config.cooldown <= 0:
            return True
        
        return time.time() - self.last_trigger_time >= self.config.cooldown
    
    def _check_template(self):
        """Check for template presence and trigger appropriate events."""
        try:
            # Search for template
            match = self.vision.find_on_screen(
                self.config.template_path,
                region=self.config.region,
                threshold=self.config.threshold,
                use_transparency=self.config.use_transparency
            )
            
            current_time = time.time()
            
            if self.config.event_type == TemplateWatcherEvent.TEMPLATE_FOUND:
                self._handle_template_found(match, current_time)
            elif self.config.event_type == TemplateWatcherEvent.TEMPLATE_LOST:
                self._handle_template_lost(match, current_time)
            elif self.config.event_type == TemplateWatcherEvent.TEMPLATE_MOVED:
                self._handle_template_moved(match, current_time)
                
        except Exception as e:
            logger.error(f"Error checking template in watcher '{self.config.name}': {e}")
    
    def _handle_template_found(self, match, current_time):
        """Handle TEMPLATE_FOUND event type."""
        if match and not self.template_present:
            # Template appeared
            self.template_present = True
            self.last_match = match
            self._trigger_event({
                'event_type': TemplateWatcherEvent.TEMPLATE_FOUND,
                'match': match,
                'template_path': self.config.template_path,
                'timestamp': current_time,
                'trigger_count': self.trigger_count + 1
            })
        elif not match and self.template_present:
            # Template disappeared (update state but don't trigger)
            self.template_present = False
            self.last_match = None
    
    def _handle_template_lost(self, match, current_time):
        """Handle TEMPLATE_LOST event type."""
        if not match and self.template_present:
            # Template disappeared
            self.template_present = False
            self.last_match = None
            self._trigger_event({
                'event_type': TemplateWatcherEvent.TEMPLATE_LOST,
                'template_path': self.config.template_path,
                'timestamp': current_time,
                'trigger_count': self.trigger_count + 1
            })
        elif match and not self.template_present:
            # Template appeared (update state but don't trigger)
            self.template_present = True
            self.last_match = match
    
    def _handle_template_moved(self, match, current_time):
        """Handle TEMPLATE_MOVED event type."""
        if match:
            if self.last_match:
                # Calculate movement distance
                old_center = self.last_match['center']
                new_center = match['center']
                distance = ((old_center[0] - new_center[0]) ** 2 + 
                           (old_center[1] - new_center[1]) ** 2) ** 0.5
                
                if distance >= self.config.movement_threshold:
                    self._trigger_event({
                        'event_type': TemplateWatcherEvent.TEMPLATE_MOVED,
                        'match': match,
                        'previous_match': self.last_match,
                        'movement_distance': distance,
                        'template_path': self.config.template_path,
                        'timestamp': current_time,
                        'trigger_count': self.trigger_count + 1
                    })
            
            self.template_present = True
            self.last_match = match
        else:
            self.template_present = False
            self.last_match = None
    
    def _trigger_event(self, event_data: Dict[str, Any]):
        """Trigger the callback with event data."""
        try:
            self.trigger_count += 1
            self.last_trigger_time = time.time()
            
            # Add watcher metadata to event
            event_data.update({
                'watcher_name': self.config.name,
                'watcher_id': id(self),
                'template_present': self.template_present
            })
            
            # Call the callback
            self.config.callback(event_data)
            
            # Stop if this was a one-time trigger
            if self.config.trigger_once:
                self.stop()
                
        except Exception as e:
            logger.error(f"Error in callback for template watcher '{self.config.name}': {e}")

class TemplateWatcherManager:
    """Manager for multiple persistent template watchers."""
    
    def __init__(self, vision_controller):
        """Initialize the template watcher manager."""
        self.vision = vision_controller
        self.watchers: Dict[str, PersistentTemplateWatcher] = {}
        self.global_callbacks: List[Callable[[Dict[str, Any]], None]] = []
    
    def add_template_watcher(self, name: str, template_path: str, event_type: TemplateWatcherEvent,
                           callback: Callable[[Dict[str, Any]], None], threshold: float = 0.8,
                           use_transparency: bool = True, region: Optional[Dict[str, int]] = None,
                           check_interval: float = 0.5, cooldown: float = 0.0,
                           trigger_once: bool = False, movement_threshold: int = 10) -> str:
        """Add a template watcher."""
        config = TemplateWatcherConfig(
            template_path=template_path,
            callback=self._wrap_callback(callback),
            event_type=event_type,
            threshold=threshold,
            use_transparency=use_transparency,
            region=region,
            check_interval=check_interval,
            cooldown=cooldown,
            trigger_once=trigger_once,
            movement_threshold=movement_threshold,
            name=name
        )
        
        watcher = PersistentTemplateWatcher(config, self.vision)
        self.watchers[name] = watcher
        
        logger.info(f"Added template watcher '{name}' for {template_path} ({event_type.value})")
        return name
    
    def add_global_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add a global callback that receives all watcher events."""
        self.global_callbacks.append(callback)
    
    def _wrap_callback(self, callback: Callable[[Dict[str, Any]], None]) -> Callable[[Dict[str, Any]], None]:
        """Wrap user callback to also trigger global callbacks."""
        def wrapped_callback(event_data: Dict[str, Any]):
            # Call user callback first
            callback(event_data)
            
            # Then call global callbacks
            for global_callback in self.global_callbacks:
                try:
                    global_callback(event_data)
                except Exception as e:
                    logger.error(f"Error in global template callback: {e}")
        
        return wrapped_callback
    
    def start_watcher(self, name: str):
        """Start a specific watcher."""
        if name in self.watchers:
            self.watchers[name].start()
        else:
            logger.error(f"Template watcher '{name}' not found")
    
    def stop_watcher(self, name: str):
        """Stop a specific watcher."""
        if name in self.watchers:
            self.watchers[name].stop()
        else:
            logger.error(f"Template watcher '{name}' not found")
    
    def start_all(self):
        """Start all watchers."""
        for watcher in self.watchers.values():
            watcher.start()
        try:
            logger.info(f"Started {len(self.watchers)} template watchers")
        except (TypeError, AttributeError):
            pass
    
    def stop_all(self):
        """Stop all watchers."""
        for watcher in self.watchers.values():
            watcher.stop()
        try:
            logger.info("Stopped all template watchers")
        except (TypeError, AttributeError):
            pass
    
    def remove_watcher(self, name: str):
        """Remove a watcher (stops it first if running)."""
        if name in self.watchers:
            self.watchers[name].stop()
            del self.watchers[name]
            try:
                logger.info(f"Removed template watcher '{name}'")
            except (TypeError, AttributeError):
                pass
        else:
            logger.error(f"Template watcher '{name}' not found")
    
    def get_watcher_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get status information for a watcher."""
        if name not in self.watchers:
            return None
        
        watcher = self.watchers[name]
        return {
            'name': name,
            'running': watcher.running,
            'trigger_count': watcher.trigger_count,
            'template_path': watcher.config.template_path,
            'event_type': watcher.config.event_type.value,
            'enabled': watcher.config.enabled,
            'template_present': watcher.template_present,
            'last_trigger_time': watcher.last_trigger_time,
            'check_interval': watcher.config.check_interval,
        }
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all watchers."""
        return {name: self.get_watcher_status(name) for name in self.watchers.keys()}
    
    def enable_watcher(self, name: str):
        """Enable a watcher (allows it to trigger events)."""
        if name in self.watchers:
            self.watchers[name].config.enabled = True
            try:
                logger.info(f"Enabled template watcher '{name}'")
            except (TypeError, AttributeError):
                pass
    
    def disable_watcher(self, name: str):
        """Disable a watcher (prevents it from triggering events)."""
        if name in self.watchers:
            self.watchers[name].config.enabled = False
            try:
                logger.info(f"Disabled template watcher '{name}'")
            except (TypeError, AttributeError):
                pass
    
    def __del__(self):
        """Cleanup: stop all watchers when manager is destroyed."""
        try:
            self.stop_all()
        except (TypeError, AttributeError, ImportError):
            pass

class TransparentImageMatcher(ImageMatcher):
    """Enhanced ImageMatcher that handles transparency in template images."""
    
    def __init__(self, threshold: float = 0.8):
        """Initialize TransparentImageMatcher."""
        super().__init__(threshold)
        self.template_masks = {}  # Cache for template masks
        logger.info("TransparentImageMatcher initialized with transparency support")
    
    def load_template(self, filepath: str) -> Optional[np.ndarray]:
        """
        Load template image from file, preserving alpha channel if present.
        
        Args:
            filepath: Path to template image file
        
        Returns:
            Template image as numpy array or None if loading failed
        """
        try:
            # First try to load with alpha channel
            template_rgba = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
            
            if template_rgba is None:
                logger.error(f"Failed to load template from {filepath}")
                return None
            
            # Check if image has alpha channel
            if template_rgba.shape[2] == 4:  # RGBA
                logger.debug(f"Loaded RGBA template from {filepath}")
                
                # Separate RGB and Alpha channels
                template_rgb = template_rgba[:, :, :3]  # RGB channels
                alpha_channel = template_rgba[:, :, 3]   # Alpha channel
                
                # Store the mask for later use
                mask_key = filepath
                # Create mask: 255 where alpha > 0 (opaque), 0 where alpha = 0 (transparent)
                self.template_masks[mask_key] = (alpha_channel > 0).astype(np.uint8) * 255
                
                # Convert RGB from BGR to BGR (OpenCV format)
                template_bgr = cv2.cvtColor(template_rgb, cv2.COLOR_RGB2BGR)
                
                return template_bgr
            
            elif template_rgba.shape[2] == 3:  # RGB/BGR
                logger.debug(f"Loaded RGB template from {filepath} (no transparency)")
                return template_rgba
            
            else:  # Grayscale
                logger.debug(f"Loaded grayscale template from {filepath}")
                return template_rgba
                
        except Exception as e:
            logger.error(f"Error loading template: {e}")
            return None
    
    def find_template_with_mask(self, screen: np.ndarray, template: np.ndarray, 
                               mask: Optional[np.ndarray] = None,
                               threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Find template matches using mask to ignore transparent areas.
        
        Args:
            screen: Screen image as numpy array
            template: Template image as numpy array
            mask: Mask where 255 = match this pixel, 0 = ignore this pixel
            threshold: Override default threshold
        
        Returns:
            List of match dictionaries
        """
        try:
            match_threshold = threshold or self.threshold
            
            # Perform masked template matching
            if mask is not None:
                result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED, mask=mask)
            else:
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
                    'size': (w, h),
                    'has_transparency': mask is not None
                })
            
            logger.debug(f"Found {len(matches)} masked template matches")
            return matches
            
        except Exception as e:
            logger.error(f"Masked template matching failed: {e}")
            return []
    
    def find_best_match_with_mask(self, screen: np.ndarray, template: np.ndarray,
                                 mask: Optional[np.ndarray] = None) -> Optional[Dict[str, Any]]:
        """
        Find the best template match using mask to ignore transparent areas.
        
        Args:
            screen: Screen image as numpy array
            template: Template image as numpy array
            mask: Mask where 255 = match this pixel, 0 = ignore this pixel
        
        Returns:
            Best match dictionary or None if no match found
        """
        try:
            if mask is not None:
                result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED, mask=mask)
            else:
                result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= self.threshold:
                h, w = template.shape[:2]
                center = (max_loc[0] + w // 2, max_loc[1] + h // 2)
                
                return {
                    'position': max_loc,
                    'confidence': float(max_val),
                    'center': center,
                    'size': (w, h),
                    'has_transparency': mask is not None
                }
            
            logger.debug(f"No masked match found above threshold {self.threshold}")
            return None
            
        except Exception as e:
            logger.error(f"Masked best match search failed: {e}")
            return None
    
    def get_template_mask(self, filepath: str) -> Optional[np.ndarray]:
        """Get the transparency mask for a template file."""
        return self.template_masks.get(filepath)
    
    def has_transparency_support(self) -> bool:
        """Check if OpenCV version supports masked template matching."""
        try:
            # Try to use mask parameter - available in OpenCV 4.1+
            dummy_screen = np.zeros((100, 100, 3), dtype=np.uint8)
            dummy_template = np.zeros((10, 10, 3), dtype=np.uint8)
            dummy_mask = np.ones((10, 10), dtype=np.uint8) * 255
            
            cv2.matchTemplate(dummy_screen, dummy_template, cv2.TM_CCOEFF_NORMED, mask=dummy_mask)
            return True
        except TypeError:
            # Older OpenCV version doesn't support mask parameter
            logger.warning("OpenCV version doesn't support masked template matching")
            return False
    
    def create_shape_mask(self, template: np.ndarray, shape_type: str = "circle") -> np.ndarray:
        """
        Create a mask for template matching based on shape.
        
        Args:
            template: Template image
            shape_type: Type of shape ("circle", "ellipse", "rounded_rect")
            
        Returns:
            Mask array where 255 = match, 0 = ignore
        """
        h, w = template.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        
        if shape_type == "circle":
            center = (w // 2, h // 2)
            radius = min(w, h) // 2
            cv2.circle(mask, center, radius, 255, -1)
            
        elif shape_type == "ellipse":
            center = (w // 2, h // 2)
            axes = (w // 2, h // 2)
            cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
            
        elif shape_type == "rounded_rect":
            # Create rounded rectangle
            corner_radius = min(w, h) // 8
            cv2.rectangle(mask, (corner_radius, 0), (w - corner_radius, h), 255, -1)
            cv2.rectangle(mask, (0, corner_radius), (w, h - corner_radius), 255, -1)
            
            # Add rounded corners
            cv2.circle(mask, (corner_radius, corner_radius), corner_radius, 255, -1)
            cv2.circle(mask, (w - corner_radius, corner_radius), corner_radius, 255, -1)
            cv2.circle(mask, (corner_radius, h - corner_radius), corner_radius, 255, -1)
            cv2.circle(mask, (w - corner_radius, h - corner_radius), corner_radius, 255, -1)
        
        return mask

class TransparentVisionController(VisionController):
    """
    Enhanced VisionController with transparency support.
    Handles PNG templates with alpha channels properly.
    """
    
    def __init__(self, match_threshold: float = 0.8):
        """Initialize TransparentVisionController."""
        # Initialize base components
        self.screen_capture = ScreenCapture()
        self.color_detector = ColorDetector()
        
        # Use transparent image matcher instead of regular one
        self.image_matcher = TransparentImageMatcher(threshold=match_threshold)
        
        # Cache for templates and their masks
        self.template_cache = {}
        self.mask_cache = {}
        
        # Template watcher manager
        self.template_watcher_manager = TemplateWatcherManager(self)
        
        logger.info("TransparentVisionController initialized with transparency support")
    
    def find_on_screen(self, template_path: str, region: Optional[Dict[str, int]] = None,
                      threshold: Optional[float] = None, use_transparency: bool = True) -> Optional[Dict[str, Any]]:
        """
        Find template on screen with optional transparency support.
        
        Args:
            template_path: Path to template image file
            region: Screen region to search in
            threshold: Override default threshold
            use_transparency: Whether to use transparency mask if available
        
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
            
            # Get mask if transparency is requested and available
            mask = None
            if use_transparency:
                mask = self.image_matcher.get_template_mask(template_path)
            
            # Capture screen
            screen = self.screen_capture.capture_screen(region)
            if screen.size == 0:
                return None
            
            # Find best match with or without mask
            if mask is not None and self.image_matcher.has_transparency_support():
                match = self.image_matcher.find_best_match_with_mask(screen, template, mask)
            else:
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
            logger.error(f"Transparent screen search failed: {e}")
            return None
    
    def find_all_on_screen(self, template_path: str, region: Optional[Dict[str, int]] = None,
                          threshold: Optional[float] = None, use_transparency: bool = True) -> List[Dict[str, Any]]:
        """
        Find all template matches on screen with transparency support.
        
        Args:
            template_path: Path to template image file
            region: Screen region to search in
            threshold: Override default threshold
            use_transparency: Whether to use transparency mask if available
        
        Returns:
            List of match dictionaries
        """
        try:
            # Load template
            if template_path not in self.template_cache:
                template = self.image_matcher.load_template(template_path)
                if template is None:
                    return []
                self.template_cache[template_path] = template
            else:
                template = self.template_cache[template_path]
            
            # Get mask if transparency is requested
            mask = None
            if use_transparency:
                mask = self.image_matcher.get_template_mask(template_path)
            
            # Capture screen
            screen = self.screen_capture.capture_screen(region)
            if screen.size == 0:
                return []
            
            # Find all matches
            if mask is not None and self.image_matcher.has_transparency_support():
                matches = self.image_matcher.find_template_with_mask(screen, template, mask, threshold)
            else:
                matches = self.image_matcher.find_template(screen, template, threshold)
            
            # Adjust coordinates if region was specified
            if matches and region:
                for match in matches:
                    match['position'] = (
                        match['position'][0] + region['left'],
                        match['position'][1] + region['top']
                    )
                    match['center'] = (
                        match['center'][0] + region['left'],
                        match['center'][1] + region['top']
                    )
            
            return matches
            
        except Exception as e:
            logger.error(f"Transparent screen search failed: {e}")
            return []
    
    def find_with_custom_mask(self, template_path: str, mask_shape: str = "circle",
                            region: Optional[Dict[str, int]] = None,
                            threshold: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Find template using a custom shape mask.
        
        Args:
            template_path: Path to template image file
            mask_shape: Shape of mask ("circle", "ellipse", "rounded_rect")
            region: Screen region to search in
            threshold: Override default threshold
        
        Returns:
            Match information or None if not found
        """
        try:
            # Load template
            if template_path not in self.template_cache:
                template = self.image_matcher.load_template(template_path)
                if template is None:
                    return None
                self.template_cache[template_path] = template
            else:
                template = self.template_cache[template_path]
            
            # Create custom mask
            mask_key = f"{template_path}_{mask_shape}"
            if mask_key not in self.mask_cache:
                mask = self.image_matcher.create_shape_mask(template, mask_shape)
                self.mask_cache[mask_key] = mask
            else:
                mask = self.mask_cache[mask_key]
            
            # Capture screen
            screen = self.screen_capture.capture_screen(region)
            if screen.size == 0:
                return None
            
            # Find match with custom mask
            if self.image_matcher.has_transparency_support():
                match = self.image_matcher.find_best_match_with_mask(screen, template, mask)
            else:
                logger.warning("Custom masks require OpenCV 4.1+, falling back to normal matching")
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
                
            if match:
                match['custom_mask'] = mask_shape
            
            return match
            
        except Exception as e:
            logger.error(f"Custom mask search failed: {e}")
            return None
    
    def get_transparency_info(self, template_path: str) -> Dict[str, Any]:
        """
        Get information about a template's transparency.
        
        Args:
            template_path: Path to template image file
            
        Returns:
            Dictionary with transparency information
        """
        try:
            # Load the template if not cached
            if template_path not in self.template_cache:
                template = self.image_matcher.load_template(template_path)
                if template is None:
                    return {"error": "Could not load template"}
            
            # Get mask if available
            mask = self.image_matcher.get_template_mask(template_path)
            
            info = {
                "has_transparency": mask is not None,
                "opencv_supports_masks": self.image_matcher.has_transparency_support(),
                "template_cached": template_path in self.template_cache
            }
            
            if mask is not None:
                # Calculate transparency statistics
                total_pixels = mask.size
                opaque_pixels = np.sum(mask > 0)
                transparent_pixels = total_pixels - opaque_pixels
                
                info.update({
                    "total_pixels": int(total_pixels),
                    "opaque_pixels": int(opaque_pixels),
                    "transparent_pixels": int(transparent_pixels),
                    "opacity_ratio": float(opaque_pixels / total_pixels),
                    "transparency_ratio": float(transparent_pixels / total_pixels)
                })
            
            return info
            
        except Exception as e:
            return {"error": str(e)}
    
    def save_template_mask(self, template_path: str, output_path: str) -> bool:
        """
        Save the transparency mask of a template as a separate image.
        
        Args:
            template_path: Path to template image file
            output_path: Path to save the mask image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load template to ensure mask is created
            if template_path not in self.template_cache:
                template = self.image_matcher.load_template(template_path)
                if template is None:
                    return False
            
            # Get mask
            mask = self.image_matcher.get_template_mask(template_path)
            if mask is None:
                logger.error(f"No transparency mask available for {template_path}")
                return False
            
            # Save mask as grayscale image
            cv2.imwrite(output_path, mask)
            logger.info(f"Saved transparency mask to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save mask: {e}")
            return False
    
    # Template Watcher Methods
    def watch_template_found(self, name: str, template_path: str,
                           callback: Callable[[Dict[str, Any]], None], threshold: float = 0.8,
                           use_transparency: bool = True, region: Optional[Dict[str, int]] = None,
                           check_interval: float = 0.5, cooldown: float = 0.0,
                           trigger_once: bool = False, auto_start: bool = True) -> str:
        """
        Watch for a template to appear on screen.
        
        Args:
            name: Unique name for the watcher
            template_path: Path to template image file
            callback: Function to call when template is found
            threshold: Matching threshold (0.0 to 1.0)
            use_transparency: Whether to use transparency mask if available
            region: Screen region to search in
            check_interval: Time between checks in seconds
            cooldown: Minimum time between triggers in seconds
            trigger_once: Whether to trigger only once then stop
            auto_start: Whether to start the watcher immediately
            
        Returns:
            Watcher name
        """
        watcher_name = self.template_watcher_manager.add_template_watcher(
            name, template_path, TemplateWatcherEvent.TEMPLATE_FOUND, callback,
            threshold, use_transparency, region, check_interval, cooldown,
            trigger_once
        )
        
        if auto_start:
            self.template_watcher_manager.start_watcher(watcher_name)
        
        return watcher_name
    
    def watch_template_lost(self, name: str, template_path: str,
                          callback: Callable[[Dict[str, Any]], None], threshold: float = 0.8,
                          use_transparency: bool = True, region: Optional[Dict[str, int]] = None,
                          check_interval: float = 0.5, cooldown: float = 0.0,
                          trigger_once: bool = False, auto_start: bool = True) -> str:
        """
        Watch for a template to disappear from screen.
        
        Args:
            name: Unique name for the watcher
            template_path: Path to template image file
            callback: Function to call when template is lost
            threshold: Matching threshold (0.0 to 1.0)
            use_transparency: Whether to use transparency mask if available
            region: Screen region to search in
            check_interval: Time between checks in seconds
            cooldown: Minimum time between triggers in seconds
            trigger_once: Whether to trigger only once then stop
            auto_start: Whether to start the watcher immediately
            
        Returns:
            Watcher name
        """
        watcher_name = self.template_watcher_manager.add_template_watcher(
            name, template_path, TemplateWatcherEvent.TEMPLATE_LOST, callback,
            threshold, use_transparency, region, check_interval, cooldown,
            trigger_once
        )
        
        if auto_start:
            self.template_watcher_manager.start_watcher(watcher_name)
        
        return watcher_name
    
    def watch_template_moved(self, name: str, template_path: str,
                           callback: Callable[[Dict[str, Any]], None], threshold: float = 0.8,
                           use_transparency: bool = True, region: Optional[Dict[str, int]] = None,
                           check_interval: float = 0.5, cooldown: float = 0.0,
                           movement_threshold: int = 10, trigger_once: bool = False,
                           auto_start: bool = True) -> str:
        """
        Watch for a template to move on screen.
        
        Args:
            name: Unique name for the watcher
            template_path: Path to template image file
            callback: Function to call when template moves
            threshold: Matching threshold (0.0 to 1.0)
            use_transparency: Whether to use transparency mask if available
            region: Screen region to search in
            check_interval: Time between checks in seconds
            cooldown: Minimum time between triggers in seconds
            movement_threshold: Minimum movement distance in pixels to trigger
            trigger_once: Whether to trigger only once then stop
            auto_start: Whether to start the watcher immediately
            
        Returns:
            Watcher name
        """
        watcher_name = self.template_watcher_manager.add_template_watcher(
            name, template_path, TemplateWatcherEvent.TEMPLATE_MOVED, callback,
            threshold, use_transparency, region, check_interval, cooldown,
            trigger_once, movement_threshold
        )
        
        if auto_start:
            self.template_watcher_manager.start_watcher(watcher_name)
        
        return watcher_name
    
    def start_template_watcher(self, name: str):
        """Start a template watcher."""
        self.template_watcher_manager.start_watcher(name)
    
    def stop_template_watcher(self, name: str):
        """Stop a template watcher."""
        self.template_watcher_manager.stop_watcher(name)
    
    def start_all_template_watchers(self):
        """Start all template watchers."""
        self.template_watcher_manager.start_all()
    
    def stop_all_template_watchers(self):
        """Stop all template watchers."""
        self.template_watcher_manager.stop_all()
    
    def remove_template_watcher(self, name: str):
        """Remove a template watcher."""
        self.template_watcher_manager.remove_watcher(name)
    
    def get_template_watcher_status(self, name: str = None) -> Dict[str, Any]:
        """Get status for one or all template watchers."""
        if name:
            return self.template_watcher_manager.get_watcher_status(name)
        else:
            return self.template_watcher_manager.get_all_status()
    
    def add_global_template_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add a callback that receives all template watcher events."""
        self.template_watcher_manager.add_global_callback(callback)
    
    def __del__(self):
        """Cleanup: stop all watchers when controller is destroyed."""
        try:
            if hasattr(self, 'template_watcher_manager'):
                self.template_watcher_manager.stop_all()
        except (TypeError, AttributeError, ImportError):
            pass
