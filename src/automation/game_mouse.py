"""
Enhanced mouse controller specifically designed for games that hide the cursor
or use exclusive input modes. Uses Windows API directly for better compatibility.
"""

import time
import ctypes
import ctypes.wintypes
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Windows API constants
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000

# Window message constants
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP = 0x0208
WM_MOUSEWHEEL = 0x020A

# Virtual key codes for mouse buttons
VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
VK_MBUTTON = 0x04

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class GameMouseController:
    """Enhanced mouse controller for games using Windows API directly."""
    
    def __init__(self):
        """Initialize GameMouseController."""
        # Load Windows API functions
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
        # Get screen dimensions
        self.screen_width = self.user32.GetSystemMetrics(0)
        self.screen_height = self.user32.GetSystemMetrics(1)
        
        logger.info(f"GameMouseController initialized. Screen size: {self.screen_width}x{self.screen_height}")
    
    def get_foreground_window(self) -> Optional[int]:
        """Get handle to the foreground (active) window."""
        return self.user32.GetForegroundWindow()
    
    def get_window_rect(self, hwnd: int) -> Optional[Tuple[int, int, int, int]]:
        """Get window rectangle (left, top, right, bottom)."""
        rect = ctypes.wintypes.RECT()
        if self.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return (rect.left, rect.top, rect.right, rect.bottom)
        return None
    
    def screen_to_client(self, hwnd: int, x: int, y: int) -> Tuple[int, int]:
        """Convert screen coordinates to client coordinates."""
        point = POINT(x, y)
        self.user32.ScreenToClient(hwnd, ctypes.byref(point))
        return (point.x, point.y)
    
    def click_direct_api(self, x: int, y: int, button: str = 'left', clicks: int = 1) -> bool:
        """
        Click using direct Windows API mouse_event.
        This bypasses the normal message queue and works better with games.
        """
        try:
            # Convert to absolute coordinates (0-65535 range)
            abs_x = int(x * 65536 / self.screen_width)
            abs_y = int(y * 65536 / self.screen_height)
            
            # Determine button flags
            if button == 'left':
                down_flag = MOUSEEVENTF_LEFTDOWN
                up_flag = MOUSEEVENTF_LEFTUP
            elif button == 'right':
                down_flag = MOUSEEVENTF_RIGHTDOWN
                up_flag = MOUSEEVENTF_RIGHTUP
            elif button == 'middle':
                down_flag = MOUSEEVENTF_MIDDLEDOWN
                up_flag = MOUSEEVENTF_MIDDLEUP
            else:
                logger.error(f"Invalid button: {button}")
                return False
            
            logger.info(f"Direct API click at ({x}, {y}) with {button} button")
            
            # Move to position first
            self.user32.mouse_event(
                MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
                abs_x, abs_y, 0, 0
            )
            
            # Perform clicks
            for i in range(clicks):
                # Mouse down
                self.user32.mouse_event(down_flag, abs_x, abs_y, 0, 0)
                time.sleep(0.01)  # Small delay
                
                # Mouse up
                self.user32.mouse_event(up_flag, abs_x, abs_y, 0, 0)
                
                if i < clicks - 1:  # Don't sleep after last click
                    time.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error(f"Direct API click failed: {e}")
            return False
    
    def click_window_message(self, hwnd: int, x: int, y: int, button: str = 'left') -> bool:
        """
        Click by sending window messages directly to a specific window.
        This can work even when the window doesn't have focus.
        """
        try:
            # Convert to client coordinates
            client_x, client_y = self.screen_to_client(hwnd, x, y)
            
            # Pack coordinates into lParam
            lParam = (client_y << 16) | (client_x & 0xFFFF)
            
            # Determine message types
            if button == 'left':
                down_msg = WM_LBUTTONDOWN
                up_msg = WM_LBUTTONUP
            elif button == 'right':
                down_msg = WM_RBUTTONDOWN
                up_msg = WM_RBUTTONUP
            elif button == 'middle':
                down_msg = WM_MBUTTONDOWN
                up_msg = WM_MBUTTONUP
            else:
                logger.error(f"Invalid button: {button}")
                return False
            
            logger.info(f"Window message click at ({x}, {y}) -> client ({client_x}, {client_y})")
            
            # Send mouse down and up messages
            self.user32.PostMessageW(hwnd, down_msg, 0, lParam)
            time.sleep(0.01)
            self.user32.PostMessageW(hwnd, up_msg, 0, lParam)
            
            return True
            
        except Exception as e:
            logger.error(f"Window message click failed: {e}")
            return False
    
    def click_hybrid(self, x: int, y: int, button: str = 'left', clicks: int = 1, 
                    target_window: bool = True) -> bool:
        """
        Hybrid click method that tries multiple approaches for maximum compatibility.
        
        Args:
            x: X coordinate
            y: Y coordinate  
            button: Mouse button ('left', 'right', 'middle')
            clicks: Number of clicks
            target_window: Whether to target the active window specifically
        """
        success = False
        
        if target_window:
            # Try window message approach first for games
            hwnd = self.get_foreground_window()
            if hwnd:
                logger.info("Attempting window message click...")
                success = self.click_window_message(hwnd, x, y, button)
        
        if not success:
            # Fall back to direct API approach
            logger.info("Attempting direct API click...")
            success = self.click_direct_api(x, y, button, clicks)
        
        return success
    
    def mouse_down_api(self, x: int, y: int, button: str = 'left') -> bool:
        """Press mouse button down using Windows API."""
        try:
            abs_x = int(x * 65536 / self.screen_width)
            abs_y = int(y * 65536 / self.screen_height)
            
            if button == 'left':
                flag = MOUSEEVENTF_LEFTDOWN
            elif button == 'right':
                flag = MOUSEEVENTF_RIGHTDOWN
            elif button == 'middle':
                flag = MOUSEEVENTF_MIDDLEDOWN
            else:
                return False
            
            # Move to position
            self.user32.mouse_event(
                MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
                abs_x, abs_y, 0, 0
            )
            
            # Press down
            self.user32.mouse_event(flag, abs_x, abs_y, 0, 0)
            
            logger.info(f"Mouse down at ({x}, {y}) with {button} button")
            return True
            
        except Exception as e:
            logger.error(f"Mouse down failed: {e}")
            return False
    
    def mouse_up_api(self, button: str = 'left') -> bool:
        """Release mouse button using Windows API."""
        try:
            if button == 'left':
                flag = MOUSEEVENTF_LEFTUP
            elif button == 'right':
                flag = MOUSEEVENTF_RIGHTUP
            elif button == 'middle':
                flag = MOUSEEVENTF_MIDDLEUP
            else:
                return False
            
            self.user32.mouse_event(flag, 0, 0, 0, 0)
            
            logger.info(f"Mouse up for {button} button")
            return True
            
        except Exception as e:
            logger.error(f"Mouse up failed: {e}")
            return False
    
    def get_position(self) -> Tuple[int, int]:
        """Get current mouse position using Windows API."""
        point = POINT()
        self.user32.GetCursorPos(ctypes.byref(point))
        return (point.x, point.y)
    
    def move_to_api(self, x: int, y: int, duration: float = 0.0) -> bool:
        """Move mouse to position using Windows API."""
        try:
            if duration <= 0:
                # Instant move
                abs_x = int(x * 65536 / self.screen_width)
                abs_y = int(y * 65536 / self.screen_height)
                
                self.user32.mouse_event(
                    MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
                    abs_x, abs_y, 0, 0
                )
            else:
                # Smooth move
                start_x, start_y = self.get_position()
                steps = max(1, int(duration * 100))  # 100 steps per second
                
                for i in range(steps + 1):
                    progress = i / steps
                    current_x = int(start_x + (x - start_x) * progress)
                    current_y = int(start_y + (y - start_y) * progress)
                    
                    abs_x = int(current_x * 65536 / self.screen_width)
                    abs_y = int(current_y * 65536 / self.screen_height)
                    
                    self.user32.mouse_event(
                        MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
                        abs_x, abs_y, 0, 0
                    )
                    
                    if i < steps:
                        time.sleep(duration / steps)
            
            return True
            
        except Exception as e:
            logger.error(f"Move to failed: {e}")
            return False
    
    def scroll_api(self, clicks: int, x: int = None, y: int = None) -> bool:
        """Scroll using Windows API."""
        try:
            if x is not None and y is not None:
                # Move to position first
                self.move_to_api(x, y)
            
            # Scroll (positive = up, negative = down)
            wheel_delta = clicks * 120  # Standard wheel delta
            
            self.user32.mouse_event(
                MOUSEEVENTF_WHEEL,
                0, 0, wheel_delta, 0
            )
            
            logger.info(f"Scrolled {clicks} clicks")
            return True
            
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return False
    
    def is_button_pressed(self, button: str) -> bool:
        """Check if a mouse button is currently pressed."""
        try:
            if button == 'left':
                vk_code = VK_LBUTTON
            elif button == 'right':
                vk_code = VK_RBUTTON
            elif button == 'middle':
                vk_code = VK_MBUTTON
            else:
                return False
            
            # Check if high bit is set (button is pressed)
            state = self.user32.GetAsyncKeyState(vk_code)
            return (state & 0x8000) != 0
            
        except Exception as e:
            logger.error(f"Button state check failed: {e}")
            return False
    
    def get_game_window_info(self) -> dict:
        """Get information about the current game window."""
        hwnd = self.get_foreground_window()
        if not hwnd:
            return {"error": "No foreground window"}
        
        # Get window title
        title_length = self.user32.GetWindowTextLengthW(hwnd)
        title_buffer = ctypes.create_unicode_buffer(title_length + 1)
        self.user32.GetWindowTextW(hwnd, title_buffer, title_length + 1)
        title = title_buffer.value
        
        # Get window rectangle
        rect = self.get_window_rect(hwnd)
        
        # Get window class name
        class_buffer = ctypes.create_unicode_buffer(256)
        self.user32.GetClassNameW(hwnd, class_buffer, 256)
        class_name = class_buffer.value
        
        return {
            "hwnd": hwnd,
            "title": title,
            "class_name": class_name,
            "rect": rect,
            "width": rect[2] - rect[0] if rect else 0,
            "height": rect[3] - rect[1] if rect else 0,
        }

class HybridMouseController:
    """
    Hybrid mouse controller that combines PyAutoGUI and GameMouseController
    for maximum compatibility across different applications and games.
    """
    
    def __init__(self):
        """Initialize both mouse controllers."""
        # Import PyAutoGUI here to avoid circular imports
        import pyautogui
        self.pyautogui = pyautogui
        self.game_mouse = GameMouseController()
        
        # Configure PyAutoGUI
        self.pyautogui.FAILSAFE = True
        self.pyautogui.PAUSE = 0.01  # Faster than default
        
        logger.info("HybridMouseController initialized")
    
    def click(self, x: int, y: int, button: str = 'left', clicks: int = 1, 
              method: str = 'auto') -> bool:
        """
        Click using the best available method.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button
            clicks: Number of clicks
            method: 'auto', 'pyautogui', 'winapi', 'game'
        """
        if method == 'pyautogui':
            try:
                self.pyautogui.click(x, y, clicks=clicks, button=button)
                return True
            except Exception as e:
                logger.error(f"PyAutoGUI click failed: {e}")
                return False
        
        elif method == 'winapi':
            return self.game_mouse.click_direct_api(x, y, button, clicks)
        
        elif method == 'game':
            return self.game_mouse.click_hybrid(x, y, button, clicks)
        
        else:  # 'auto'
            # Try game method first, fall back to PyAutoGUI
            if not self.game_mouse.click_hybrid(x, y, button, clicks):
                try:
                    self.pyautogui.click(x, y, clicks=clicks, button=button)
                    return True
                except Exception as e:
                    logger.error(f"All click methods failed: {e}")
                    return False
            return True
    
    def get_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        return self.game_mouse.get_position()
    
    def move_to(self, x: int, y: int, duration: float = 0.0) -> bool:
        """Move mouse to position."""
        return self.game_mouse.move_to_api(x, y, duration)
    
    def mouse_down(self, x: int, y: int, button: str = 'left') -> bool:
        """Press mouse button down."""
        return self.game_mouse.mouse_down_api(x, y, button)
    
    def mouse_up(self, button: str = 'left') -> bool:
        """Release mouse button."""
        return self.game_mouse.mouse_up_api(button)
    
    def scroll(self, clicks: int, x: int = None, y: int = None) -> bool:
        """Scroll at position."""
        return self.game_mouse.scroll_api(clicks, x, y)
    
    def is_button_pressed(self, button: str) -> bool:
        """Check if button is pressed."""
        return self.game_mouse.is_button_pressed(button)
    
    def get_window_info(self) -> dict:
        """Get game window information."""
        return self.game_mouse.get_game_window_info()