"""
Unit tests for keyboard automation module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import time
import pyautogui
from src.automation.keyboard import KeyboardController


@pytest.fixture
def keyboard_controller():
    """Fixture for KeyboardController instance."""
    return KeyboardController(pause_duration=0)


@pytest.fixture
def mock_pyautogui():
    """Fixture for mocking pyautogui functions."""
    with patch('src.automation.keyboard.pyautogui') as mock_pg:
        mock_pg.typewrite = Mock()
        mock_pg.press = Mock()
        mock_pg.keyDown = Mock()
        mock_pg.keyUp = Mock()
        mock_pg.hotkey = Mock()
        yield mock_pg


class TestKeyboardController:
    """Test cases for KeyboardController class."""

    def test_initialization(self):
        """Test KeyboardController initialization."""
        controller = KeyboardController(pause_duration=0.2)
        assert pyautogui.PAUSE == 0.2

    def test_type_text_success(self, keyboard_controller, mock_pyautogui):
        """Test typing text successfully."""
        result = keyboard_controller.type_text("Hello World", interval=0.1)
        
        assert result == True
        mock_pyautogui.typewrite.assert_called_once_with("Hello World", interval=0.1)

    def test_type_text_empty_string(self, keyboard_controller, mock_pyautogui):
        """Test typing empty string."""
        result = keyboard_controller.type_text("", interval=0.0)
        
        assert result == True
        mock_pyautogui.typewrite.assert_called_once_with("", interval=0.0)

    def test_type_text_with_exception(self, keyboard_controller, mock_pyautogui):
        """Test typing text when pyautogui raises an exception."""
        mock_pyautogui.typewrite.side_effect = Exception("Test exception")
        
        result = keyboard_controller.type_text("Hello")
        
        assert result == False

    def test_press_key_valid(self, keyboard_controller, mock_pyautogui):
        """Test pressing a valid key."""
        result = keyboard_controller.press_key('enter', presses=1, interval=0.0)
        
        assert result == True
        mock_pyautogui.press.assert_called_once_with('enter', presses=1, interval=0.0)

    def test_press_key_multiple_presses(self, keyboard_controller, mock_pyautogui):
        """Test pressing a key multiple times."""
        result = keyboard_controller.press_key('space', presses=3, interval=0.1)
        
        assert result == True
        mock_pyautogui.press.assert_called_once_with('space', presses=3, interval=0.1)

    def test_press_key_invalid(self, keyboard_controller, mock_pyautogui):
        """Test pressing an invalid key."""
        result = keyboard_controller.press_key('invalid_key')
        
        assert result == False
        mock_pyautogui.press.assert_not_called()

    def test_press_key_with_exception(self, keyboard_controller, mock_pyautogui):
        """Test pressing key when pyautogui raises an exception."""
        mock_pyautogui.press.side_effect = Exception("Test exception")
        
        result = keyboard_controller.press_key('enter')
        
        assert result == False

    def test_press_keys_sequence_valid(self, keyboard_controller, mock_pyautogui):
        """Test pressing a sequence of valid keys."""
        with patch('time.sleep') as mock_sleep:
            result = keyboard_controller.press_keys(['a', 'b', 'c'], interval=0.1)
        
        assert result == True
        assert mock_pyautogui.press.call_count == 3
        mock_pyautogui.press.assert_any_call('a')
        mock_pyautogui.press.assert_any_call('b')
        mock_pyautogui.press.assert_any_call('c')
        assert mock_sleep.call_count == 3

    def test_press_keys_sequence_no_interval(self, keyboard_controller, mock_pyautogui):
        """Test pressing a sequence of keys with no interval."""
        with patch('time.sleep') as mock_sleep:
            result = keyboard_controller.press_keys(['enter', 'tab'], interval=0.0)
        
        assert result == True
        assert mock_pyautogui.press.call_count == 2
        mock_sleep.assert_not_called()

    def test_press_keys_invalid_key_in_sequence(self, keyboard_controller, mock_pyautogui):
        """Test pressing keys when one key in sequence is invalid."""
        result = keyboard_controller.press_keys(['a', 'invalid_key', 'c'])
        
        assert result == False
        mock_pyautogui.press.assert_not_called()

    def test_press_keys_with_exception(self, keyboard_controller, mock_pyautogui):
        """Test pressing keys when pyautogui raises an exception."""
        mock_pyautogui.press.side_effect = Exception("Test exception")
        
        result = keyboard_controller.press_keys(['a', 'b'])
        
        assert result == False

    def test_hold_key_valid(self, keyboard_controller, mock_pyautogui):
        """Test holding a valid key."""
        with patch('time.sleep') as mock_sleep:
            result = keyboard_controller.hold_key('shift', duration=2.0)
        
        assert result == True
        mock_pyautogui.keyDown.assert_called_once_with('shift')
        mock_sleep.assert_called_once_with(2.0)
        mock_pyautogui.keyUp.assert_called_once_with('shift')

    def test_hold_key_invalid(self, keyboard_controller, mock_pyautogui):
        """Test holding an invalid key."""
        result = keyboard_controller.hold_key('invalid_key', duration=1.0)
        
        assert result == False
        mock_pyautogui.keyDown.assert_not_called()
        mock_pyautogui.keyUp.assert_not_called()

    def test_hold_key_with_exception(self, keyboard_controller, mock_pyautogui):
        """Test holding key when pyautogui raises an exception."""
        mock_pyautogui.keyDown.side_effect = Exception("Test exception")
        
        result = keyboard_controller.hold_key('shift', duration=1.0)
        
        assert result == False

    def test_key_combination_valid(self, keyboard_controller, mock_pyautogui):
        """Test pressing a valid key combination."""
        result = keyboard_controller.key_combination(['ctrl', 'c'])
        
        assert result == True
        mock_pyautogui.hotkey.assert_called_once_with('ctrl', 'c')

    def test_key_combination_multiple_keys(self, keyboard_controller, mock_pyautogui):
        """Test pressing a combination with multiple keys."""
        result = keyboard_controller.key_combination(['ctrl', 'shift', 's'])
        
        assert result == True
        mock_pyautogui.hotkey.assert_called_once_with('ctrl', 'shift', 's')

    def test_key_combination_invalid_key(self, keyboard_controller, mock_pyautogui):
        """Test key combination with invalid key."""
        result = keyboard_controller.key_combination(['ctrl', 'invalid_key'])
        
        assert result == False
        mock_pyautogui.hotkey.assert_not_called()

    def test_key_combination_with_exception(self, keyboard_controller, mock_pyautogui):
        """Test key combination when pyautogui raises an exception."""
        mock_pyautogui.hotkey.side_effect = Exception("Test exception")
        
        result = keyboard_controller.key_combination(['ctrl', 'c'])
        
        assert result == False

    def test_key_down_valid(self, keyboard_controller, mock_pyautogui):
        """Test pressing key down."""
        result = keyboard_controller.key_down('shift')
        
        assert result == True
        mock_pyautogui.keyDown.assert_called_once_with('shift')

    def test_key_down_invalid(self, keyboard_controller, mock_pyautogui):
        """Test pressing invalid key down."""
        result = keyboard_controller.key_down('invalid_key')
        
        assert result == False
        mock_pyautogui.keyDown.assert_not_called()

    def test_key_down_with_exception(self, keyboard_controller, mock_pyautogui):
        """Test key down when pyautogui raises an exception."""
        mock_pyautogui.keyDown.side_effect = Exception("Test exception")
        
        result = keyboard_controller.key_down('shift')
        
        assert result == False

    def test_key_up_valid(self, keyboard_controller, mock_pyautogui):
        """Test releasing key."""
        result = keyboard_controller.key_up('shift')
        
        assert result == True
        mock_pyautogui.keyUp.assert_called_once_with('shift')

    def test_key_up_invalid(self, keyboard_controller, mock_pyautogui):
        """Test releasing invalid key."""
        result = keyboard_controller.key_up('invalid_key')
        
        assert result == False
        mock_pyautogui.keyUp.assert_not_called()

    def test_key_up_with_exception(self, keyboard_controller, mock_pyautogui):
        """Test key up when pyautogui raises an exception."""
        mock_pyautogui.keyUp.side_effect = Exception("Test exception")
        
        result = keyboard_controller.key_up('shift')
        
        assert result == False

    def test_clear_text_ctrl_a_delete(self, keyboard_controller, mock_pyautogui):
        """Test clearing text with ctrl+a+delete method."""
        result = keyboard_controller.clear_text('ctrl_a_delete')
        
        assert result == True
        mock_pyautogui.hotkey.assert_called_once_with('ctrl', 'a')
        mock_pyautogui.press.assert_called_once_with('delete', presses=1, interval=0.0)

    def test_clear_text_ctrl_a_backspace(self, keyboard_controller, mock_pyautogui):
        """Test clearing text with ctrl+a+backspace method."""
        result = keyboard_controller.clear_text('ctrl_a_backspace')
        
        assert result == True
        mock_pyautogui.hotkey.assert_called_once_with('ctrl', 'a')
        mock_pyautogui.press.assert_called_once_with('backspace', presses=1, interval=0.0)

    def test_clear_text_home_shift_end_delete(self, keyboard_controller, mock_pyautogui):
        """Test clearing text with home+shift+end+delete method."""
        result = keyboard_controller.clear_text('home_shift_end_delete')
        
        assert result == True
        # Should call home, shift+end, then delete
        assert mock_pyautogui.press.call_count == 2  # home and delete
        assert mock_pyautogui.hotkey.call_count == 1  # shift+end

    def test_clear_text_invalid_method(self, keyboard_controller, mock_pyautogui):
        """Test clearing text with invalid method."""
        result = keyboard_controller.clear_text('invalid_method')
        
        assert result == False
        mock_pyautogui.hotkey.assert_not_called()
        mock_pyautogui.press.assert_not_called()

    def test_navigate_valid_directions(self, keyboard_controller, mock_pyautogui):
        """Test navigation in all valid directions."""
        directions = ['up', 'down', 'left', 'right']
        
        for direction in directions:
            mock_pyautogui.press.reset_mock()
            result = keyboard_controller.navigate(direction, steps=3)
            
            assert result == True
            mock_pyautogui.press.assert_called_once_with(direction, presses=3, interval=0.0)

    def test_navigate_invalid_direction(self, keyboard_controller, mock_pyautogui):
        """Test navigation with invalid direction."""
        result = keyboard_controller.navigate('invalid_direction', steps=1)
        
        assert result == False
        mock_pyautogui.press.assert_not_called()

    def test_navigate_with_exception(self, keyboard_controller, mock_pyautogui):
        """Test navigation when pyautogui raises an exception."""
        mock_pyautogui.press.side_effect = Exception("Test exception")
        
        result = keyboard_controller.navigate('up')
        
        assert result == False

    def test_function_key_valid_range(self, keyboard_controller, mock_pyautogui):
        """Test pressing valid function keys."""
        for i in range(1, 13):
            mock_pyautogui.press.reset_mock()
            result = keyboard_controller.function_key(i)
            
            assert result == True
            mock_pyautogui.press.assert_called_once_with(f'f{i}')

    def test_function_key_invalid_range(self, keyboard_controller, mock_pyautogui):
        """Test pressing invalid function key numbers."""
        invalid_numbers = [0, 13, -1, 100]
        
        for number in invalid_numbers:
            result = keyboard_controller.function_key(number)
            assert result == False
        
        mock_pyautogui.press.assert_not_called()

    def test_function_key_with_exception(self, keyboard_controller, mock_pyautogui):
        """Test function key when pyautogui raises an exception."""
        mock_pyautogui.press.side_effect = Exception("Test exception")
        
        result = keyboard_controller.function_key(1)
        
        assert result == False

    def test_validate_key_valid_keys(self, keyboard_controller):
        """Test key validation with valid keys."""
        valid_keys = [
            'a', 'z', '1', '9', 'enter', 'tab', 'space', 'ctrl', 'shift',
            'f1', 'f12', 'up', 'down', 'home', 'end', '.', ',', '!'
        ]
        
        for key in valid_keys:
            assert keyboard_controller._validate_key(key) == True

    def test_validate_key_invalid_keys(self, keyboard_controller):
        """Test key validation with invalid keys."""
        invalid_keys = [
            'invalid_key', 'f13', 'f0', 'unknown', ''
        ]
        
        for key in invalid_keys:
            assert keyboard_controller._validate_key(key) == False

    def test_validate_key_case_insensitive(self, keyboard_controller):
        """Test key validation is case insensitive."""
        assert keyboard_controller._validate_key('A') == True
        assert keyboard_controller._validate_key('ENTER') == True
        assert keyboard_controller._validate_key('F1') == True


class TestKeyboardControllerIntegration:
    """Integration tests for KeyboardController."""

    def test_typing_sequence(self, mock_pyautogui):
        """Test a complete typing sequence."""
        controller = KeyboardController(pause_duration=0)
        
        # Perform a sequence of operations
        controller.clear_text()
        controller.type_text("Hello World!")
        controller.press_key('enter')
        controller.key_combination(['ctrl', 's'])
        
        # Verify operations were called
        assert mock_pyautogui.hotkey.call_count >= 1
        assert mock_pyautogui.typewrite.call_count == 1
        assert mock_pyautogui.press.call_count >= 1

    def test_error_recovery(self, keyboard_controller, mock_pyautogui):
        """Test error recovery in keyboard operations."""
        # First operation fails, second succeeds
        mock_pyautogui.press.side_effect = [Exception("First fails"), None]
        
        result1 = keyboard_controller.press_key('a')
        result2 = keyboard_controller.press_key('b')
        
        assert result1 == False
        assert result2 == True
        assert mock_pyautogui.press.call_count == 2

    def test_complex_key_operations(self, keyboard_controller, mock_pyautogui):
        """Test complex key operations sequence."""
        # Simulate copying and pasting text
        keyboard_controller.key_combination(['ctrl', 'a'])  # Select all
        keyboard_controller.key_combination(['ctrl', 'c'])  # Copy
        keyboard_controller.navigate('right', steps=5)      # Move cursor
        keyboard_controller.key_combination(['ctrl', 'v'])  # Paste
        
        assert mock_pyautogui.hotkey.call_count == 3
        assert mock_pyautogui.press.call_count == 1  # navigate calls press


if __name__ == "__main__":
    pytest.main([__file__])
