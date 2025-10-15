"""
Enhanced pixel monitoring system with persistent watchers that can trigger multiple times.
This extends the VisionController with event-driven pixel monitoring capabilities.
"""

import time
import threading
from typing import Callable, Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from .vision import VisionController

logger = logging.getLogger(__name__)

class WatcherEvent(Enum):
    """Types of pixel watcher events."""
    COLOR_MATCH = "color_match"
    COLOR_CHANGE = "color_change"
    PATTERN_DETECTED = "pattern_detected"

@dataclass
class PixelWatcherConfig:
    """Configuration for a pixel watcher."""
    x: int
    y: int
    event_type: WatcherEvent
    callback: Callable[[Dict[str, Any]], None]
    
    # Color matching parameters
    target_color: Optional[Tuple[int, int, int]] = None
    tolerance: int = 10
    
    # Change detection parameters
    min_change: int = 10
    
    # Timing parameters
    check_interval: float = 0.1
    
    # Event filtering
    cooldown: float = 0.0  # Minimum time between triggers
    trigger_once: bool = False  # Only trigger once then stop
    
    # Additional metadata
    name: str = ""
    enabled: bool = True

class PersistentPixelWatcher:
    """
    A persistent pixel watcher that can monitor pixels continuously 
    and trigger callbacks when conditions are met.
    """
    
    def __init__(self, config: PixelWatcherConfig):
        """Initialize the persistent pixel watcher."""
        self.config = config
        self.vision = VisionController()
        self.running = False
        self.thread = None
        self.last_trigger_time = 0.0
        self.trigger_count = 0
        self.last_known_color = None
        
        # Initialize last known color for change detection
        if self.config.event_type == WatcherEvent.COLOR_CHANGE:
            self.last_known_color = self.vision.get_pixel_color(config.x, config.y)
    
    def start(self):
        """Start the pixel watcher in a separate thread."""
        if self.running:
            logger.warning(f"Watcher '{self.config.name}' is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()
        logger.info(f"Started pixel watcher '{self.config.name}' at ({self.config.x}, {self.config.y})")
    
    def stop(self):
        """Stop the pixel watcher."""
        if not self.running:
            return
        
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        try:
            logger.info(f"Stopped pixel watcher '{self.config.name}' (triggered {self.trigger_count} times)")
        except (TypeError, AttributeError):
            pass
    
    def _watch_loop(self):
        """Main watching loop that runs in a separate thread."""
        try:
            while self.running and self.config.enabled:
                if self._should_check():
                    current_color = self.vision.get_pixel_color(self.config.x, self.config.y)
                    
                    if self.config.event_type == WatcherEvent.COLOR_MATCH:
                        self._check_color_match(current_color)
                    elif self.config.event_type == WatcherEvent.COLOR_CHANGE:
                        self._check_color_change(current_color)
                
                time.sleep(self.config.check_interval)
                
        except Exception as e:
            logger.error(f"Error in watcher '{self.config.name}': {e}")
        finally:
            self.running = False
    
    def _should_check(self) -> bool:
        """Check if enough time has passed since last trigger (cooldown)."""
        if self.config.cooldown <= 0:
            return True
        
        return time.time() - self.last_trigger_time >= self.config.cooldown
    
    def _check_color_match(self, current_color: Tuple[int, int, int]):
        """Check if current color matches target color."""
        if not self.config.target_color:
            return
        
        if self._colors_match(current_color, self.config.target_color, self.config.tolerance):
            self._trigger_event({
                'event_type': WatcherEvent.COLOR_MATCH,
                'position': (self.config.x, self.config.y),
                'current_color': current_color,
                'target_color': self.config.target_color,
                'tolerance': self.config.tolerance,
                'trigger_count': self.trigger_count + 1,
                'timestamp': time.time()
            })
    
    def _check_color_change(self, current_color: Tuple[int, int, int]):
        """Check if color has changed significantly from last known color."""
        if self.last_known_color is None:
            self.last_known_color = current_color
            return
        
        # Calculate color difference
        color_diff = sum(abs(a - b) for a, b in zip(self.last_known_color, current_color))
        
        if color_diff >= self.config.min_change:
            self._trigger_event({
                'event_type': WatcherEvent.COLOR_CHANGE,
                'position': (self.config.x, self.config.y),
                'previous_color': self.last_known_color,
                'current_color': current_color,
                'color_difference': color_diff,
                'trigger_count': self.trigger_count + 1,
                'timestamp': time.time()
            })
            
            # Update last known color
            self.last_known_color = current_color
    
    def _trigger_event(self, event_data: Dict[str, Any]):
        """Trigger the callback with event data."""
        try:
            self.trigger_count += 1
            self.last_trigger_time = time.time()
            
            # Add watcher metadata to event
            event_data.update({
                'watcher_name': self.config.name,
                'watcher_id': id(self),
            })
            
            # Call the callback
            self.config.callback(event_data)
            
            # Stop if this was a one-time trigger
            if self.config.trigger_once:
                self.stop()
                
        except Exception as e:
            logger.error(f"Error in callback for watcher '{self.config.name}': {e}")
    
    def _colors_match(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], tolerance: int) -> bool:
        """Check if two RGB colors match within tolerance."""
        return all(abs(a - b) <= tolerance for a, b in zip(color1, color2))

class PixelWatcherManager:
    """
    Manager for multiple persistent pixel watchers.
    Provides easy control over multiple watchers and event coordination.
    """
    
    def __init__(self):
        """Initialize the pixel watcher manager."""
        self.watchers: Dict[str, PersistentPixelWatcher] = {}
        self.global_callbacks: List[Callable[[Dict[str, Any]], None]] = []
    
    def add_color_watcher(self, name: str, x: int, y: int, target_color: Tuple[int, int, int],
                         callback: Callable[[Dict[str, Any]], None], tolerance: int = 10,
                         check_interval: float = 0.1, cooldown: float = 0.0, 
                         trigger_once: bool = False) -> str:
        """
        Add a color matching watcher.
        
        Args:
            name: Unique name for the watcher
            x, y: Pixel coordinates to monitor
            target_color: RGB color to watch for
            callback: Function to call when color matches
            tolerance: Color matching tolerance (0-255)
            check_interval: Time between checks in seconds
            cooldown: Minimum time between triggers in seconds
            trigger_once: Whether to trigger only once then stop
            
        Returns:
            Watcher name (same as input)
        """
        config = PixelWatcherConfig(
            x=x, y=y,
            event_type=WatcherEvent.COLOR_MATCH,
            callback=self._wrap_callback(callback),
            target_color=target_color,
            tolerance=tolerance,
            check_interval=check_interval,
            cooldown=cooldown,
            trigger_once=trigger_once,
            name=name
        )
        
        watcher = PersistentPixelWatcher(config)
        self.watchers[name] = watcher
        
        logger.info(f"Added color watcher '{name}' for RGB{target_color} at ({x}, {y})")
        return name
    
    def add_change_watcher(self, name: str, x: int, y: int,
                          callback: Callable[[Dict[str, Any]], None], min_change: int = 10,
                          check_interval: float = 0.1, cooldown: float = 0.0,
                          trigger_once: bool = False) -> str:
        """
        Add a color change watcher.
        
        Args:
            name: Unique name for the watcher
            x, y: Pixel coordinates to monitor
            callback: Function to call when color changes
            min_change: Minimum total RGB change to trigger
            check_interval: Time between checks in seconds
            cooldown: Minimum time between triggers in seconds
            trigger_once: Whether to trigger only once then stop
            
        Returns:
            Watcher name (same as input)
        """
        config = PixelWatcherConfig(
            x=x, y=y,
            event_type=WatcherEvent.COLOR_CHANGE,
            callback=self._wrap_callback(callback),
            min_change=min_change,
            check_interval=check_interval,
            cooldown=cooldown,
            trigger_once=trigger_once,
            name=name
        )
        
        watcher = PersistentPixelWatcher(config)
        self.watchers[name] = watcher
        
        logger.info(f"Added change watcher '{name}' with min_change={min_change} at ({x}, {y})")
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
                    logger.error(f"Error in global callback: {e}")
        
        return wrapped_callback
    
    def start_watcher(self, name: str):
        """Start a specific watcher."""
        if name in self.watchers:
            self.watchers[name].start()
        else:
            logger.error(f"Watcher '{name}' not found")
    
    def stop_watcher(self, name: str):
        """Stop a specific watcher."""
        if name in self.watchers:
            self.watchers[name].stop()
        else:
            logger.error(f"Watcher '{name}' not found")
    
    def start_all(self):
        """Start all watchers."""
        for watcher in self.watchers.values():
            watcher.start()
        logger.info(f"Started {len(self.watchers)} pixel watchers")
    
    def stop_all(self):
        """Stop all watchers."""
        for watcher in self.watchers.values():
            watcher.stop()
        try:
            logger.info("Stopped all pixel watchers")
        except (TypeError, AttributeError):
            # Logger may be None during Python shutdown
            pass
    
    def remove_watcher(self, name: str):
        """Remove a watcher (stops it first if running)."""
        if name in self.watchers:
            self.watchers[name].stop()
            del self.watchers[name]
            try:
                logger.info(f"Removed watcher '{name}'")
            except (TypeError, AttributeError):
                pass
        else:
            logger.error(f"Watcher '{name}' not found")
    
    def get_watcher_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get status information for a watcher."""
        if name not in self.watchers:
            return None
        
        watcher = self.watchers[name]
        return {
            'name': name,
            'running': watcher.running,
            'trigger_count': watcher.trigger_count,
            'position': (watcher.config.x, watcher.config.y),
            'event_type': watcher.config.event_type.value,
            'enabled': watcher.config.enabled,
            'last_trigger_time': watcher.last_trigger_time,
        }
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all watchers."""
        return {name: self.get_watcher_status(name) for name in self.watchers.keys()}
    
    def enable_watcher(self, name: str):
        """Enable a watcher (allows it to trigger events)."""
        if name in self.watchers:
            self.watchers[name].config.enabled = True
            logger.info(f"Enabled watcher '{name}'")
    
    def disable_watcher(self, name: str):
        """Disable a watcher (prevents it from triggering events)."""
        if name in self.watchers:
            self.watchers[name].config.enabled = False
            logger.info(f"Disabled watcher '{name}'")
    
    def __del__(self):
        """Cleanup: stop all watchers when manager is destroyed."""
        try:
            self.stop_all()
        except (TypeError, AttributeError, ImportError):
            # Ignore errors during Python shutdown
            pass

class EnhancedVisionController(VisionController):
    """
    Enhanced VisionController with persistent pixel watching capabilities.
    Extends the base VisionController with event-driven monitoring.
    """
    
    def __init__(self, match_threshold: float = 0.8):
        """Initialize the enhanced vision controller."""
        super().__init__(match_threshold)
        self.watcher_manager = PixelWatcherManager()
    
    def watch_pixel_color(self, name: str, x: int, y: int, target_color: Tuple[int, int, int],
                         callback: Callable[[Dict[str, Any]], None], tolerance: int = 10,
                         check_interval: float = 0.1, cooldown: float = 0.0, 
                         trigger_once: bool = False, auto_start: bool = True) -> str:
        """
        Create a persistent pixel color watcher.
        
        Args:
            name: Unique name for the watcher
            x, y: Pixel coordinates to monitor
            target_color: RGB color to watch for
            callback: Function to call when color matches
            tolerance: Color matching tolerance (0-255)
            check_interval: Time between checks in seconds
            cooldown: Minimum time between triggers in seconds
            trigger_once: Whether to trigger only once then stop
            auto_start: Whether to start the watcher immediately
            
        Returns:
            Watcher name
        """
        watcher_name = self.watcher_manager.add_color_watcher(
            name, x, y, target_color, callback, tolerance, 
            check_interval, cooldown, trigger_once
        )
        
        if auto_start:
            self.watcher_manager.start_watcher(watcher_name)
        
        return watcher_name
    
    def watch_pixel_change(self, name: str, x: int, y: int,
                          callback: Callable[[Dict[str, Any]], None], min_change: int = 10,
                          check_interval: float = 0.1, cooldown: float = 0.0,
                          trigger_once: bool = False, auto_start: bool = True) -> str:
        """
        Create a persistent pixel change watcher.
        
        Args:
            name: Unique name for the watcher
            x, y: Pixel coordinates to monitor
            callback: Function to call when color changes
            min_change: Minimum total RGB change to trigger
            check_interval: Time between checks in seconds
            cooldown: Minimum time between triggers in seconds
            trigger_once: Whether to trigger only once then stop
            auto_start: Whether to start the watcher immediately
            
        Returns:
            Watcher name
        """
        watcher_name = self.watcher_manager.add_change_watcher(
            name, x, y, callback, min_change,
            check_interval, cooldown, trigger_once
        )
        
        if auto_start:
            self.watcher_manager.start_watcher(watcher_name)
        
        return watcher_name
    
    def start_watcher(self, name: str):
        """Start a pixel watcher."""
        self.watcher_manager.start_watcher(name)
    
    def stop_watcher(self, name: str):
        """Stop a pixel watcher."""
        self.watcher_manager.stop_watcher(name)
    
    def start_all_watchers(self):
        """Start all pixel watchers."""
        self.watcher_manager.start_all()
    
    def stop_all_watchers(self):
        """Stop all pixel watchers."""
        self.watcher_manager.stop_all()
    
    def remove_watcher(self, name: str):
        """Remove a pixel watcher."""
        self.watcher_manager.remove_watcher(name)
    
    def get_watcher_status(self, name: str = None) -> Dict[str, Any]:
        """Get status for one or all watchers."""
        if name:
            return self.watcher_manager.get_watcher_status(name)
        else:
            return self.watcher_manager.get_all_status()
    
    def add_global_watcher_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add a callback that receives all watcher events."""
        self.watcher_manager.add_global_callback(callback)
    
    def __del__(self):
        """Cleanup: stop all watchers when controller is destroyed."""
        try:
            if hasattr(self, 'watcher_manager'):
                self.watcher_manager.stop_all()
        except (TypeError, AttributeError, ImportError):
            # Ignore errors during Python shutdown
            pass
