"""
Mouse automation module for performing mouse actions.
"""
import time
import pyautogui
from typing import Tuple, Optional
import logging

# Configure pyautogui safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

logger = logging.getLogger(__name__)


class MouseController:
    """Controller for mouse automation actions."""
    
    def __init__(self, fail_safe: bool = True, pause_duration: float = 0.1):
        """
        Initialize MouseController.
        
        Args:
            fail_safe: Enable fail-safe mode (move mouse to top-left corner to abort)
            pause_duration: Pause duration between actions
        """
        pyautogui.FAILSAFE = fail_safe
        pyautogui.PAUSE = pause_duration
        self.screen_size = pyautogui.size()
        logger.info(f"MouseController initialized. Screen size: {self.screen_size}")
    
    def click(self, x: int, y: int, button: str = 'left', clicks: int = 1, 
              interval: float = 0.0, duration: float = 0.0) -> bool:
        """
        Click at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ('left', 'right', 'middle')
            clicks: Number of clicks
            interval: Interval between clicks
            duration: Duration to move to position
            
        Returns:
            True if click was successful, False otherwise
        """
        try:
            if not self._validate_coordinates(x, y):
                logger.error(f"Invalid coordinates: ({x}, {y})")
                return False
            
            logger.info(f"Clicking at ({x}, {y}) with {button} button, {clicks} times")
            pyautogui.click(x, y, clicks=clicks, interval=interval, 
                          button=button, duration=duration)
            return True
            
        except Exception as e:
            logger.error(f"Failed to click at ({x}, {y}): {e}")
            return False
    
    def double_click(self, x: int, y: int, button: str = 'left', 
                    interval: float = 0.0, duration: float = 0.0) -> bool:
        """
        Double click at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button
            interval: Interval between clicks
            duration: Duration to move to position
            
        Returns:
            True if double click was successful, False otherwise
        """
        return self.click(x, y, button=button, clicks=2, interval=interval, duration=duration)
    
    def right_click(self, x: int, y: int, duration: float = 0.0) -> bool:
        """
        Right click at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Duration to move to position
            
        Returns:
            True if right click was successful, False otherwise
        """
        return self.click(x, y, button='right', duration=duration)
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
             duration: float = 1.0, button: str = 'left') -> bool:
        """
        Drag from start coordinates to end coordinates.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Duration of the drag operation
            button: Mouse button to use for dragging
            
        Returns:
            True if drag was successful, False otherwise
        """
        try:
            if not (self._validate_coordinates(start_x, start_y) and 
                   self._validate_coordinates(end_x, end_y)):
                logger.error(f"Invalid coordinates for drag: ({start_x}, {start_y}) to ({end_x}, {end_y})")
                return False
            
            logger.info(f"Dragging from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration, 
                          button=button)
            return True
            
        except Exception as e:
            logger.error(f"Failed to drag from ({start_x}, {start_y}) to ({end_x}, {end_y}): {e}")
            return False
    
    def move_to(self, x: int, y: int, duration: float = 0.0) -> bool:
        """
        Move mouse to specified coordinates without clicking.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Duration to move to position
            
        Returns:
            True if move was successful, False otherwise
        """
        try:
            if not self._validate_coordinates(x, y):
                logger.error(f"Invalid coordinates: ({x}, {y})")
                return False
            
            logger.info(f"Moving mouse to ({x}, {y})")
            pyautogui.moveTo(x, y, duration=duration)
            return True
            
        except Exception as e:
            logger.error(f"Failed to move mouse to ({x}, {y}): {e}")
            return False
    
    def get_position(self) -> Tuple[int, int]:
        """
        Get current mouse position.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        return pyautogui.position()
    
    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """
        Scroll at specified position or current position.
        
        Args:
            clicks: Number of clicks to scroll (positive for up, negative for down)
            x: X coordinate (optional, uses current position if None)
            y: Y coordinate (optional, uses current position if None)
            
        Returns:
            True if scroll was successful, False otherwise
        """
        try:
            if x is not None and y is not None:
                if not self._validate_coordinates(x, y):
                    logger.error(f"Invalid coordinates for scroll: ({x}, {y})")
                    return False
                logger.info(f"Scrolling {clicks} clicks at ({x}, {y})")
                pyautogui.scroll(clicks, x=x, y=y)
            else:
                logger.info(f"Scrolling {clicks} clicks at current position")
                pyautogui.scroll(clicks)
            return True
            
        except Exception as e:
            logger.error(f"Failed to scroll: {e}")
            return False
    
    def mouse_down(self, x: int, y: int, button: str = 'left') -> bool:
        """
        Press and hold a mouse button down at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button to hold ('left', 'right', 'middle')
            
        Returns:
            True if mouse down was successful, False otherwise
        """
        try:
            if not self._validate_coordinates(x, y):
                logger.error(f"Invalid coordinates: ({x}, {y})")
                return False
            
            logger.info(f"Pressing down {button} mouse button at ({x}, {y})")
            # Move to position first, then press down
            pyautogui.moveTo(x, y)
            pyautogui.mouseDown(button=button)
            return True
            
        except Exception as e:
            logger.error(f"Failed to press down mouse button at ({x}, {y}): {e}")
            return False
    
    def mouse_up(self, button: str = 'left') -> bool:
        """
        Release a mouse button that was pressed down.
        
        Args:
            button: Mouse button to release ('left', 'right', 'middle')
            
        Returns:
            True if mouse up was successful, False otherwise
        """
        try:
            logger.info(f"Releasing {button} mouse button")
            pyautogui.mouseUp(button=button)
            return True
            
        except Exception as e:
            logger.error(f"Failed to release {button} mouse button: {e}")
            return False
    
    def hold_mouse_button(self, x: int, y: int, button: str = 'left', duration: float = 1.0) -> bool:
        """
        Hold a mouse button down at specified coordinates for a duration.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button to hold ('left', 'right', 'middle')
            duration: Duration to hold the button in seconds
            
        Returns:
            True if mouse hold was successful, False otherwise
        """
        try:
            if not self._validate_coordinates(x, y):
                logger.error(f"Invalid coordinates: ({x}, {y})")
                return False
            
            logger.info(f"Holding {button} mouse button at ({x}, {y}) for {duration} seconds")
            # Move to position, press down, wait, then release
            pyautogui.moveTo(x, y)
            pyautogui.mouseDown(button=button)
            time.sleep(duration)
            pyautogui.mouseUp(button=button)
            return True
            
        except Exception as e:
            logger.error(f"Failed to hold mouse button at ({x}, {y}): {e}")
            return False
    
    def _validate_coordinates(self, x: int, y: int) -> bool:
        """
        Validate that coordinates are within screen bounds.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if coordinates are valid, False otherwise
        """
        return (0 <= x < self.screen_size.width and 
                0 <= y < self.screen_size.height)
