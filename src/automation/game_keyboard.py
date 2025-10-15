"""
Enhanced keyboard controller specifically designed for games that may block
standard input methods. Uses Windows API directly for better compatibility.
"""

import time
import ctypes
import ctypes.wintypes
from typing import List, Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)

# Windows API constants for keyboard input
KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

# Window message constants
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105

# Virtual key code mapping for common keys
VK_CODES = {
    # Letters
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45, 'f': 0x46, 'g': 0x47,
    'h': 0x48, 'i': 0x49, 'j': 0x4A, 'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E,
    'o': 0x4F, 'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54, 'u': 0x55,
    'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59, 'z': 0x5A,
    
    # Numbers
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
    
    # Function keys
    'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5': 0x74, 'f6': 0x75,
    'f7': 0x76, 'f8': 0x77, 'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,
    
    # Special keys
    'backspace': 0x08, 'tab': 0x09, 'enter': 0x0D, 'return': 0x0D,
    'shift': 0x10, 'ctrl': 0x11, 'alt': 0x12, 'pause': 0x13, 'capslock': 0x14,
    'escape': 0x1B, 'esc': 0x1B, 'space': 0x20, 'pageup': 0x21, 'pagedown': 0x22,
    'end': 0x23, 'home': 0x24, 'left': 0x25, 'up': 0x26, 'right': 0x27, 'down': 0x28,
    'select': 0x29, 'print': 0x2A, 'execute': 0x2B, 'printscreen': 0x2C, 'prtsc': 0x2C,
    'insert': 0x2D, 'delete': 0x2E, 'help': 0x2F,
    
    # Windows keys
    'win': 0x5B, 'winleft': 0x5B, 'winright': 0x5C, 'cmd': 0x5B,
    
    # Numpad
    'numpad0': 0x60, 'numpad1': 0x61, 'numpad2': 0x62, 'numpad3': 0x63, 'numpad4': 0x64,
    'numpad5': 0x65, 'numpad6': 0x66, 'numpad7': 0x67, 'numpad8': 0x68, 'numpad9': 0x69,
    'multiply': 0x6A, 'add': 0x6B, 'separator': 0x6C, 'subtract': 0x6D,
    'decimal': 0x6E, 'divide': 0x6F, 'numlock': 0x90,
    
    # Lock keys
    'scrolllock': 0x91,
    
    # Shift keys
    'shiftleft': 0xA0, 'shiftright': 0xA1,
    'ctrlleft': 0xA2, 'ctrlright': 0xA3,
    'altleft': 0xA4, 'altright': 0xA5,
    
    # Punctuation and symbols (these may require shift combinations)
    ';': 0xBA, '=': 0xBB, ',': 0xBC, '-': 0xBD, '.': 0xBE, '/': 0xBF, '`': 0xC0,
    '[': 0xDB, '\\': 0xDC, ']': 0xDD, "'": 0xDE,
}

# Scan code mapping (hardware-independent)
SCAN_CODES = {
    'escape': 0x01, 'esc': 0x01,
    '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06,
    '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0A, '0': 0x0B,
    '-': 0x0C, '=': 0x0D, 'backspace': 0x0E,
    'tab': 0x0F, 'q': 0x10, 'w': 0x11, 'e': 0x12, 'r': 0x13, 't': 0x14,
    'y': 0x15, 'u': 0x16, 'i': 0x17, 'o': 0x18, 'p': 0x19,
    '[': 0x1A, ']': 0x1B, 'enter': 0x1C, 'return': 0x1C,
    'ctrl': 0x1D, 'a': 0x1E, 's': 0x1F, 'd': 0x20, 'f': 0x21,
    'g': 0x22, 'h': 0x23, 'j': 0x24, 'k': 0x25, 'l': 0x26,
    ';': 0x27, "'": 0x28, '`': 0x29, 'shift': 0x2A,
    '\\': 0x2B, 'z': 0x2C, 'x': 0x2D, 'c': 0x2E, 'v': 0x2F,
    'b': 0x30, 'n': 0x31, 'm': 0x32, ',': 0x33, '.': 0x34,
    '/': 0x35, 'space': 0x39,
}

class KEYBDINPUT(ctypes.Structure):
    """Keyboard input structure for SendInput."""
    _fields_ = [
        ('wVk', ctypes.wintypes.WORD),
        ('wScan', ctypes.wintypes.WORD),
        ('dwFlags', ctypes.wintypes.DWORD),
        ('time', ctypes.wintypes.DWORD),
        ('dwExtraInfo', ctypes.POINTER(ctypes.wintypes.ULONG))
    ]

class INPUT(ctypes.Structure):
    """Input structure for SendInput."""
    class _INPUT(ctypes.Union):
        _fields_ = [('ki', KEYBDINPUT)]
    
    _anonymous_ = ('_input',)
    _fields_ = [
        ('type', ctypes.wintypes.DWORD),
        ('_input', _INPUT)
    ]

class GameKeyboardController:
    """Enhanced keyboard controller for games using Windows API directly."""
    
    def __init__(self):
        """Initialize GameKeyboardController."""
        # Load Windows API functions
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
        # Input type constants
        self.INPUT_KEYBOARD = 1
        
        logger.info("GameKeyboardController initialized")
    
    def get_vk_code(self, key: str) -> Optional[int]:
        """Get virtual key code for a key."""
        return VK_CODES.get(key.lower())
    
    def get_scan_code(self, key: str) -> Optional[int]:
        """Get scan code for a key."""
        return SCAN_CODES.get(key.lower())
    
    def press_key_api(self, key: str, presses: int = 1) -> bool:
        """Press a key using Windows API SendInput."""
        try:
            vk_code = self.get_vk_code(key)
            if vk_code is None:
                logger.error(f"Unknown key: {key}")
                return False
            
            logger.info(f"API key press: {key} ({presses} times)")
            
            for _ in range(presses):
                # Key down
                input_down = INPUT()
                input_down.type = self.INPUT_KEYBOARD
                input_down.ki.wVk = vk_code
                input_down.ki.wScan = 0
                input_down.ki.dwFlags = KEYEVENTF_KEYDOWN
                input_down.ki.time = 0
                input_down.ki.dwExtraInfo = None
                
                # Key up
                input_up = INPUT()
                input_up.type = self.INPUT_KEYBOARD
                input_up.ki.wVk = vk_code
                input_up.ki.wScan = 0
                input_up.ki.dwFlags = KEYEVENTF_KEYUP
                input_up.ki.time = 0
                input_up.ki.dwExtraInfo = None
                
                # Send both events
                events_sent = self.user32.SendInput(1, ctypes.byref(input_down), ctypes.sizeof(INPUT))
                time.sleep(0.01)  # Small delay between down and up
                events_sent += self.user32.SendInput(1, ctypes.byref(input_up), ctypes.sizeof(INPUT))
                
                if events_sent != 2:
                    logger.warning(f"SendInput returned {events_sent}, expected 2")
                
                if presses > 1:
                    time.sleep(0.05)  # Delay between multiple presses
            
            return True
            
        except Exception as e:
            logger.error(f"API key press failed for {key}: {e}")
            return False
    
    def press_key_scancode(self, key: str, presses: int = 1) -> bool:
        """Press a key using scan codes (hardware independent)."""
        try:
            scan_code = self.get_scan_code(key)
            if scan_code is None:
                logger.error(f"Unknown scan code for key: {key}")
                return False
            
            logger.info(f"Scan code key press: {key} ({presses} times)")
            
            for _ in range(presses):
                # Key down
                input_down = INPUT()
                input_down.type = self.INPUT_KEYBOARD
                input_down.ki.wVk = 0
                input_down.ki.wScan = scan_code
                input_down.ki.dwFlags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYDOWN
                input_down.ki.time = 0
                input_down.ki.dwExtraInfo = None
                
                # Key up
                input_up = INPUT()
                input_up.type = self.INPUT_KEYBOARD
                input_up.ki.wVk = 0
                input_up.ki.wScan = scan_code
                input_up.ki.dwFlags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP
                input_up.ki.time = 0
                input_up.ki.dwExtraInfo = None
                
                # Send events
                self.user32.SendInput(1, ctypes.byref(input_down), ctypes.sizeof(INPUT))
                time.sleep(0.01)
                self.user32.SendInput(1, ctypes.byref(input_up), ctypes.sizeof(INPUT))
                
                if presses > 1:
                    time.sleep(0.05)
            
            return True
            
        except Exception as e:
            logger.error(f"Scan code key press failed for {key}: {e}")
            return False
    
    def send_window_message(self, hwnd: int, key: str) -> bool:
        """Send keyboard message directly to a window."""
        try:
            vk_code = self.get_vk_code(key)
            if vk_code is None:
                logger.error(f"Unknown key for window message: {key}")
                return False
            
            logger.info(f"Sending window message for key: {key}")
            
            # Send WM_KEYDOWN and WM_KEYUP messages
            self.user32.PostMessageW(hwnd, WM_KEYDOWN, vk_code, 0)
            time.sleep(0.01)
            self.user32.PostMessageW(hwnd, WM_KEYUP, vk_code, 0)
            
            return True
            
        except Exception as e:
            logger.error(f"Window message failed for key {key}: {e}")
            return False
    
    def key_down_api(self, key: str) -> bool:
        """Press and hold a key down using Windows API."""
        try:
            vk_code = self.get_vk_code(key)
            if vk_code is None:
                logger.error(f"Unknown key: {key}")
                return False
            
            logger.info(f"API key down: {key}")
            
            input_down = INPUT()
            input_down.type = self.INPUT_KEYBOARD
            input_down.ki.wVk = vk_code
            input_down.ki.wScan = 0
            input_down.ki.dwFlags = KEYEVENTF_KEYDOWN
            input_down.ki.time = 0
            input_down.ki.dwExtraInfo = None
            
            events_sent = self.user32.SendInput(1, ctypes.byref(input_down), ctypes.sizeof(INPUT))
            return events_sent == 1
            
        except Exception as e:
            logger.error(f"API key down failed for {key}: {e}")
            return False
    
    def key_up_api(self, key: str) -> bool:
        """Release a key using Windows API."""
        try:
            vk_code = self.get_vk_code(key)
            if vk_code is None:
                logger.error(f"Unknown key: {key}")
                return False
            
            logger.info(f"API key up: {key}")
            
            input_up = INPUT()
            input_up.type = self.INPUT_KEYBOARD
            input_up.ki.wVk = vk_code
            input_up.ki.wScan = 0
            input_up.ki.dwFlags = KEYEVENTF_KEYUP
            input_up.ki.time = 0
            input_up.ki.dwExtraInfo = None
            
            events_sent = self.user32.SendInput(1, ctypes.byref(input_up), ctypes.sizeof(INPUT))
            return events_sent == 1
            
        except Exception as e:
            logger.error(f"API key up failed for {key}: {e}")
            return False
    
    def type_text_api(self, text: str) -> bool:
        """Type text using Windows API Unicode input."""
        try:
            logger.info(f"API type text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            
            for char in text:
                # Use Unicode input for character typing
                input_down = INPUT()
                input_down.type = self.INPUT_KEYBOARD
                input_down.ki.wVk = 0
                input_down.ki.wScan = ord(char)
                input_down.ki.dwFlags = KEYEVENTF_UNICODE
                input_down.ki.time = 0
                input_down.ki.dwExtraInfo = None
                
                self.user32.SendInput(1, ctypes.byref(input_down), ctypes.sizeof(INPUT))
                time.sleep(0.01)  # Small delay between characters
            
            return True
            
        except Exception as e:
            logger.error(f"API text typing failed: {e}")
            return False
    
    def key_combination_api(self, keys: List[str]) -> bool:
        """Press a key combination using Windows API."""
        try:
            # Get all virtual key codes
            vk_codes = []
            for key in keys:
                vk_code = self.get_vk_code(key)
                if vk_code is None:
                    logger.error(f"Unknown key in combination: {key}")
                    return False
                vk_codes.append((key, vk_code))
            
            logger.info(f"API key combination: {'+'.join(keys)}")
            
            # Press all keys down
            for key, vk_code in vk_codes:
                input_down = INPUT()
                input_down.type = self.INPUT_KEYBOARD
                input_down.ki.wVk = vk_code
                input_down.ki.wScan = 0
                input_down.ki.dwFlags = KEYEVENTF_KEYDOWN
                input_down.ki.time = 0
                input_down.ki.dwExtraInfo = None
                
                self.user32.SendInput(1, ctypes.byref(input_down), ctypes.sizeof(INPUT))
                time.sleep(0.01)
            
            # Small delay while keys are held
            time.sleep(0.05)
            
            # Release all keys (in reverse order)
            for key, vk_code in reversed(vk_codes):
                input_up = INPUT()
                input_up.type = self.INPUT_KEYBOARD
                input_up.ki.wVk = vk_code
                input_up.ki.wScan = 0
                input_up.ki.dwFlags = KEYEVENTF_KEYUP
                input_up.ki.time = 0
                input_up.ki.dwExtraInfo = None
                
                self.user32.SendInput(1, ctypes.byref(input_up), ctypes.sizeof(INPUT))
                time.sleep(0.01)
            
            return True
            
        except Exception as e:
            logger.error(f"API key combination failed: {e}")
            return False
    
    def is_key_pressed(self, key: str) -> bool:
        """Check if a key is currently pressed."""
        try:
            vk_code = self.get_vk_code(key)
            if vk_code is None:
                return False
            
            # Check if high bit is set (key is pressed)
            state = self.user32.GetAsyncKeyState(vk_code)
            return (state & 0x8000) != 0
            
        except Exception as e:
            logger.error(f"Key state check failed for {key}: {e}")
            return False
    
    def get_foreground_window(self) -> Optional[int]:
        """Get handle to the foreground window."""
        return self.user32.GetForegroundWindow()
    
    def press_key_hybrid(self, key: str, presses: int = 1, target_window: bool = True) -> bool:
        """
        Hybrid key press that tries multiple methods for maximum compatibility.
        
        Args:
            key: Key to press
            presses: Number of times to press
            target_window: Whether to target the active window specifically
        """
        success = False
        
        if target_window:
            # Try window message approach first
            hwnd = self.get_foreground_window()
            if hwnd:
                logger.info("Attempting window message key press...")
                for _ in range(presses):
                    if self.send_window_message(hwnd, key):
                        success = True
                    if presses > 1:
                        time.sleep(0.05)
        
        if not success:
            # Try SendInput with virtual key codes
            logger.info("Attempting API key press...")
            success = self.press_key_api(key, presses)
        
        if not success:
            # Try SendInput with scan codes
            logger.info("Attempting scan code key press...")
            success = self.press_key_scancode(key, presses)
        
        return success

class HybridKeyboardController:
    """
    Hybrid keyboard controller that combines PyAutoGUI and GameKeyboardController
    for maximum compatibility across different applications and games.
    """
    
    def __init__(self):
        """Initialize both keyboard controllers."""
        # Import PyAutoGUI here to avoid circular imports
        import pyautogui
        self.pyautogui = pyautogui
        self.game_keyboard = GameKeyboardController()
        
        # Configure PyAutoGUI
        self.pyautogui.PAUSE = 0.01  # Faster than default
        
        logger.info("HybridKeyboardController initialized")
    
    def press_key(self, key: str, presses: int = 1, method: str = 'auto') -> bool:
        """
        Press a key using the best available method.
        
        Args:
            key: Key to press
            presses: Number of times to press
            method: 'auto', 'pyautogui', 'winapi', 'scancode', 'game'
        """
        if method == 'pyautogui':
            try:
                self.pyautogui.press(key, presses=presses)
                return True
            except Exception as e:
                logger.error(f"PyAutoGUI key press failed: {e}")
                return False
        
        elif method == 'winapi':
            return self.game_keyboard.press_key_api(key, presses)
        
        elif method == 'scancode':
            return self.game_keyboard.press_key_scancode(key, presses)
        
        elif method == 'game':
            return self.game_keyboard.press_key_hybrid(key, presses)
        
        else:  # 'auto'
            # Try game method first, fall back to PyAutoGUI
            if not self.game_keyboard.press_key_hybrid(key, presses):
                try:
                    self.pyautogui.press(key, presses=presses)
                    return True
                except Exception as e:
                    logger.error(f"All key press methods failed: {e}")
                    return False
            return True
    
    def type_text(self, text: str, method: str = 'auto') -> bool:
        """Type text using the best available method."""
        if method == 'pyautogui':
            try:
                self.pyautogui.typewrite(text)
                return True
            except Exception as e:
                logger.error(f"PyAutoGUI text typing failed: {e}")
                return False
        
        elif method == 'winapi':
            return self.game_keyboard.type_text_api(text)
        
        else:  # 'auto'
            # Try API method first for games, fall back to PyAutoGUI
            if not self.game_keyboard.type_text_api(text):
                try:
                    self.pyautogui.typewrite(text)
                    return True
                except Exception as e:
                    logger.error(f"All text typing methods failed: {e}")
                    return False
            return True
    
    def key_combination(self, keys: List[str], method: str = 'auto') -> bool:
        """Press key combination using the best available method."""
        if method == 'pyautogui':
            try:
                self.pyautogui.hotkey(*keys)
                return True
            except Exception as e:
                logger.error(f"PyAutoGUI hotkey failed: {e}")
                return False
        
        elif method == 'winapi':
            return self.game_keyboard.key_combination_api(keys)
        
        else:  # 'auto'
            # Try API method first, fall back to PyAutoGUI
            if not self.game_keyboard.key_combination_api(keys):
                try:
                    self.pyautogui.hotkey(*keys)
                    return True
                except Exception as e:
                    logger.error(f"All hotkey methods failed: {e}")
                    return False
            return True
    
    def key_down(self, key: str, method: str = 'auto') -> bool:
        """Press key down using the best available method."""
        if method == 'pyautogui':
            try:
                self.pyautogui.keyDown(key)
                return True
            except Exception as e:
                logger.error(f"PyAutoGUI key down failed: {e}")
                return False
        
        elif method == 'winapi':
            return self.game_keyboard.key_down_api(key)
        
        else:  # 'auto'
            if not self.game_keyboard.key_down_api(key):
                try:
                    self.pyautogui.keyDown(key)
                    return True
                except Exception as e:
                    logger.error(f"All key down methods failed: {e}")
                    return False
            return True
    
    def key_up(self, key: str, method: str = 'auto') -> bool:
        """Release key using the best available method."""
        if method == 'pyautogui':
            try:
                self.pyautogui.keyUp(key)
                return True
            except Exception as e:
                logger.error(f"PyAutoGUI key up failed: {e}")
                return False
        
        elif method == 'winapi':
            return self.game_keyboard.key_up_api(key)
        
        else:  # 'auto'
            if not self.game_keyboard.key_up_api(key):
                try:
                    self.pyautogui.keyUp(key)
                    return True
                except Exception as e:
                    logger.error(f"All key up methods failed: {e}")
                    return False
            return True
    
    def hold_key(self, key: str, duration: float = 1.0, method: str = 'auto') -> bool:
        """Hold a key for specified duration."""
        if self.key_down(key, method):
            time.sleep(duration)
            return self.key_up(key, method)
        return False
    
    def is_key_pressed(self, key: str) -> bool:
        """Check if key is currently pressed."""
        return self.game_keyboard.is_key_pressed(key)
    
    def get_available_keys(self) -> List[str]:
        """Get list of available keys."""
        return list(VK_CODES.keys())