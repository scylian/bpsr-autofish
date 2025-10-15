"""
Keyboard automation module for performing keyboard actions.
"""
import time
import pyautogui
from typing import List, Union, Optional
import logging

logger = logging.getLogger(__name__)


class KeyboardController:
    """Controller for keyboard automation actions."""
    
    def __init__(self, pause_duration: float = 0.1):
        """
        Initialize KeyboardController.
        
        Args:
            pause_duration: Pause duration between actions
        """
        pyautogui.PAUSE = pause_duration
        logger.info("KeyboardController initialized")
    
    def type_text(self, text: str, interval: float = 0.0) -> bool:
        """
        Type text at the current cursor position.
        
        Args:
            text: Text to type
            interval: Interval between characters
            
        Returns:
            True if typing was successful, False otherwise
        """
        try:
            logger.info(f"Typing text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            pyautogui.typewrite(text, interval=interval)
            return True
            
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return False
    
    def press_key(self, key: str, presses: int = 1, interval: float = 0.0) -> bool:
        """
        Press a single key.
        
        Args:
            key: Key to press (e.g., 'enter', 'tab', 'space', 'a', 'ctrl')
            presses: Number of times to press the key
            interval: Interval between presses
            
        Returns:
            True if key press was successful, False otherwise
        """
        try:
            if not self._validate_key(key):
                logger.error(f"Invalid key: '{key}'")
                return False
            
            logger.info(f"Pressing key '{key}' {presses} times")
            pyautogui.press(key, presses=presses, interval=interval)
            return True
            
        except Exception as e:
            logger.error(f"Failed to press key '{key}': {e}")
            return False
    
    def press_keys(self, keys: List[str], interval: float = 0.0) -> bool:
        """
        Press multiple keys in sequence.
        
        Args:
            keys: List of keys to press in sequence
            interval: Interval between key presses
            
        Returns:
            True if all key presses were successful, False otherwise
        """
        try:
            for key in keys:
                if not self._validate_key(key):
                    logger.error(f"Invalid key in sequence: '{key}'")
                    return False
            
            logger.info(f"Pressing keys in sequence: {keys}")
            for key in keys:
                pyautogui.press(key)
                if interval > 0:
                    time.sleep(interval)
            return True
            
        except Exception as e:
            logger.error(f"Failed to press keys in sequence {keys}: {e}")
            return False
    
    def hold_key(self, key: str, duration: float = 1.0) -> bool:
        """
        Hold a key for a specified duration.
        
        Args:
            key: Key to hold
            duration: Duration to hold the key in seconds
            
        Returns:
            True if key hold was successful, False otherwise
        """
        try:
            if not self._validate_key(key):
                logger.error(f"Invalid key: '{key}'")
                return False
            
            logger.info(f"Holding key '{key}' for {duration} seconds")
            pyautogui.keyDown(key)
            time.sleep(duration)
            pyautogui.keyUp(key)
            return True
            
        except Exception as e:
            logger.error(f"Failed to hold key '{key}': {e}")
            return False
    
    def key_combination(self, keys: List[str]) -> bool:
        """
        Press a combination of keys simultaneously (e.g., Ctrl+C).
        
        Args:
            keys: List of keys to press simultaneously
            
        Returns:
            True if key combination was successful, False otherwise
        """
        try:
            for key in keys:
                if not self._validate_key(key):
                    logger.error(f"Invalid key in combination: '{key}'")
                    return False
            
            logger.info(f"Pressing key combination: {'+'.join(keys)}")
            pyautogui.hotkey(*keys)
            return True
            
        except Exception as e:
            logger.error(f"Failed to press key combination {keys}: {e}")
            return False
    
    def key_down(self, key: str) -> bool:
        """
        Press and hold a key down (without releasing).
        
        Args:
            key: Key to press down
            
        Returns:
            True if key down was successful, False otherwise
        """
        try:
            if not self._validate_key(key):
                logger.error(f"Invalid key: '{key}'")
                return False
            
            logger.info(f"Pressing down key '{key}'")
            pyautogui.keyDown(key)
            return True
            
        except Exception as e:
            logger.error(f"Failed to press down key '{key}': {e}")
            return False
    
    def key_up(self, key: str) -> bool:
        """
        Release a key that was pressed down.
        
        Args:
            key: Key to release
            
        Returns:
            True if key up was successful, False otherwise
        """
        try:
            if not self._validate_key(key):
                logger.error(f"Invalid key: '{key}'")
                return False
            
            logger.info(f"Releasing key '{key}'")
            pyautogui.keyUp(key)
            return True
            
        except Exception as e:
            logger.error(f"Failed to release key '{key}': {e}")
            return False
    
    def clear_text(self, method: str = 'ctrl_a_delete') -> bool:
        """
        Clear text using different methods.
        
        Args:
            method: Method to use ('ctrl_a_delete', 'ctrl_a_backspace', 'home_shift_end_delete')
            
        Returns:
            True if text clearing was successful, False otherwise
        """
        try:
            logger.info(f"Clearing text using method: {method}")
            
            if method == 'ctrl_a_delete':
                self.key_combination(['ctrl', 'a'])
                self.press_key('delete')
            elif method == 'ctrl_a_backspace':
                self.key_combination(['ctrl', 'a'])
                self.press_key('backspace')
            elif method == 'home_shift_end_delete':
                self.press_key('home')
                self.key_combination(['shift', 'end'])
                self.press_key('delete')
            else:
                logger.error(f"Invalid clear method: {method}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear text: {e}")
            return False
    
    def navigate(self, direction: str, steps: int = 1) -> bool:
        """
        Navigate using arrow keys.
        
        Args:
            direction: Direction to navigate ('up', 'down', 'left', 'right')
            steps: Number of steps to take
            
        Returns:
            True if navigation was successful, False otherwise
        """
        try:
            valid_directions = ['up', 'down', 'left', 'right']
            if direction not in valid_directions:
                logger.error(f"Invalid direction: {direction}. Must be one of {valid_directions}")
                return False
            
            logger.info(f"Navigating {direction} {steps} steps")
            return self.press_key(direction, presses=steps)
            
        except Exception as e:
            logger.error(f"Failed to navigate {direction}: {e}")
            return False
    
    def function_key(self, number: int) -> bool:
        """
        Press a function key (F1-F12).
        
        Args:
            number: Function key number (1-12)
            
        Returns:
            True if function key press was successful, False otherwise
        """
        try:
            if not (1 <= number <= 12):
                logger.error(f"Invalid function key number: {number}. Must be 1-12")
                return False
            
            key = f'f{number}'
            logger.info(f"Pressing function key {key}")
            pyautogui.press(key)
            return True
            
        except Exception as e:
            logger.error(f"Failed to press function key F{number}: {e}")
            return False
    
    def _validate_key(self, key: str) -> bool:
        """
        Validate if a key is supported by pyautogui.
        
        Args:
            key: Key to validate
            
        Returns:
            True if key is valid, False otherwise
        """
        # Common valid keys (this is not exhaustive but covers most use cases)
        valid_keys = {
            # Letters
            *'abcdefghijklmnopqrstuvwxyz',
            # Numbers
            *'0123456789',
            # Function keys
            *[f'f{i}' for i in range(1, 13)],
            # Special keys
            'enter', 'return', 'tab', 'space', 'backspace', 'delete',
            'shift', 'ctrl', 'alt', 'cmd', 'win', 'winleft', 'winright',
            'up', 'down', 'left', 'right',
            'home', 'end', 'pageup', 'pagedown', 'insert',
            'escape', 'esc', 'capslock', 'numlock', 'scrolllock',
            'pause', 'break', 'printscreen', 'prtsc',
            # Punctuation
            '.', ',', ';', ':', '!', '?', "'", '"',
            '(', ')', '[', ']', '{', '}', '<', '>',
            '/', '\\', '|', '-', '_', '=', '+',
            '`', '~', '@', '#', '$', '%', '^', '&', '*'
        }
        
        return key.lower() in valid_keys