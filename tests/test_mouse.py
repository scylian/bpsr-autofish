"""
Unit tests for mouse automation module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pyautogui
from src.automation.mouse import MouseController


@pytest.fixture
def mouse_controller():
    """Fixture for MouseController instance."""
    with patch('pyautogui.size') as mock_size:
        mock_size.return_value = MagicMock(width=1920, height=1080)
        controller = MouseController(fail_safe=False, pause_duration=0)
        return controller


@pytest.fixture
def mock_pyautogui():
    """Fixture for mocking pyautogui functions."""
    with patch('src.automation.mouse.pyautogui') as mock_pg:
        mock_pg.click = Mock()
        mock_pg.drag = Mock()
        mock_pg.moveTo = Mock()
        mock_pg.position = Mock(return_value=(100, 200))
        mock_pg.scroll = Mock()
        mock_pg.mouseDown = Mock()
        mock_pg.mouseUp = Mock()
        mock_pg.size = Mock(return_value=MagicMock(width=1920, height=1080))
        yield mock_pg


class TestMouseController:
    """Test cases for MouseController class."""

    def test_initialization(self):
        """Test MouseController initialization."""
        with patch('pyautogui.size') as mock_size:
            mock_size.return_value = MagicMock(width=1920, height=1080)
            controller = MouseController(fail_safe=True, pause_duration=0.2)
            
            assert controller.screen_size.width == 1920
            assert controller.screen_size.height == 1080
            assert pyautogui.FAILSAFE == True
            assert pyautogui.PAUSE == 0.2

    def test_click_valid_coordinates(self, mouse_controller, mock_pyautogui):
        """Test clicking with valid coordinates."""
        result = mouse_controller.click(100, 200, button='left', clicks=1)
        
        assert result == True
        mock_pyautogui.click.assert_called_once_with(
            100, 200, clicks=1, interval=0.0, button='left', duration=0.0
        )

    def test_click_invalid_coordinates(self, mouse_controller, mock_pyautogui):
        """Test clicking with invalid coordinates."""
        # Test coordinates outside screen bounds
        result1 = mouse_controller.click(-10, 200)
        result2 = mouse_controller.click(2000, 200)
        result3 = mouse_controller.click(100, -10)
        result4 = mouse_controller.click(100, 1500)
        
        assert result1 == False
        assert result2 == False
        assert result3 == False
        assert result4 == False
        mock_pyautogui.click.assert_not_called()

    def test_click_with_exception(self, mouse_controller, mock_pyautogui):
        """Test clicking when pyautogui raises an exception."""
        mock_pyautogui.click.side_effect = Exception("Test exception")
        
        result = mouse_controller.click(100, 200)
        
        assert result == False

    def test_double_click(self, mouse_controller, mock_pyautogui):
        """Test double click functionality."""
        result = mouse_controller.double_click(100, 200, button='left')
        
        assert result == True
        mock_pyautogui.click.assert_called_once_with(
            100, 200, clicks=2, interval=0.0, button='left', duration=0.0
        )

    def test_right_click(self, mouse_controller, mock_pyautogui):
        """Test right click functionality."""
        result = mouse_controller.right_click(100, 200, duration=0.5)
        
        assert result == True
        mock_pyautogui.click.assert_called_once_with(
            100, 200, clicks=1, interval=0.0, button='right', duration=0.5
        )

    def test_drag_valid_coordinates(self, mouse_controller, mock_pyautogui):
        """Test dragging with valid coordinates."""
        result = mouse_controller.drag(100, 200, 300, 400, duration=1.0, button='left')
        
        assert result == True
        mock_pyautogui.drag.assert_called_once_with(200, 200, duration=1.0, button='left')

    def test_drag_invalid_coordinates(self, mouse_controller, mock_pyautogui):
        """Test dragging with invalid coordinates."""
        # Invalid start coordinates
        result1 = mouse_controller.drag(-10, 200, 300, 400)
        # Invalid end coordinates
        result2 = mouse_controller.drag(100, 200, 2000, 400)
        
        assert result1 == False
        assert result2 == False
        mock_pyautogui.drag.assert_not_called()

    def test_drag_with_exception(self, mouse_controller, mock_pyautogui):
        """Test dragging when pyautogui raises an exception."""
        mock_pyautogui.drag.side_effect = Exception("Test exception")
        
        result = mouse_controller.drag(100, 200, 300, 400)
        
        assert result == False

    def test_move_to_valid_coordinates(self, mouse_controller, mock_pyautogui):
        """Test moving mouse to valid coordinates."""
        result = mouse_controller.move_to(500, 600, duration=0.5)
        
        assert result == True
        mock_pyautogui.moveTo.assert_called_once_with(500, 600, duration=0.5)

    def test_move_to_invalid_coordinates(self, mouse_controller, mock_pyautogui):
        """Test moving mouse to invalid coordinates."""
        result = mouse_controller.move_to(-10, 600)
        
        assert result == False
        mock_pyautogui.moveTo.assert_not_called()

    def test_move_to_with_exception(self, mouse_controller, mock_pyautogui):
        """Test moving mouse when pyautogui raises an exception."""
        mock_pyautogui.moveTo.side_effect = Exception("Test exception")
        
        result = mouse_controller.move_to(500, 600)
        
        assert result == False

    def test_get_position(self, mouse_controller, mock_pyautogui):
        """Test getting current mouse position."""
        mock_pyautogui.position.return_value = (150, 250)
        
        position = mouse_controller.get_position()
        
        assert position == (150, 250)
        mock_pyautogui.position.assert_called_once()

    def test_scroll_with_coordinates(self, mouse_controller, mock_pyautogui):
        """Test scrolling with specified coordinates."""
        result = mouse_controller.scroll(3, x=400, y=500)
        
        assert result == True
        mock_pyautogui.scroll.assert_called_once_with(3, x=400, y=500)

    def test_scroll_at_current_position(self, mouse_controller, mock_pyautogui):
        """Test scrolling at current position."""
        result = mouse_controller.scroll(-2)
        
        assert result == True
        mock_pyautogui.scroll.assert_called_once_with(-2)

    def test_scroll_invalid_coordinates(self, mouse_controller, mock_pyautogui):
        """Test scrolling with invalid coordinates."""
        result = mouse_controller.scroll(3, x=-10, y=500)
        
        assert result == False
        mock_pyautogui.scroll.assert_not_called()

    def test_scroll_with_exception(self, mouse_controller, mock_pyautogui):
        """Test scrolling when pyautogui raises an exception."""
        mock_pyautogui.scroll.side_effect = Exception("Test exception")
        
        result = mouse_controller.scroll(3)
        
        assert result == False

    def test_validate_coordinates_valid(self, mouse_controller):
        """Test coordinate validation with valid coordinates."""
        assert mouse_controller._validate_coordinates(0, 0) == True
        assert mouse_controller._validate_coordinates(100, 200) == True
        assert mouse_controller._validate_coordinates(1919, 1079) == True

    def test_validate_coordinates_invalid(self, mouse_controller):
        """Test coordinate validation with invalid coordinates."""
        assert mouse_controller._validate_coordinates(-1, 200) == False
        assert mouse_controller._validate_coordinates(100, -1) == False
        assert mouse_controller._validate_coordinates(1920, 200) == False
        assert mouse_controller._validate_coordinates(100, 1080) == False


class TestMouseControllerIntegration:
    """Integration tests for MouseController."""

    def test_click_sequence(self, mock_pyautogui):
        """Test a sequence of mouse operations."""
        with patch('pyautogui.size') as mock_size:
            mock_size.return_value = MagicMock(width=1920, height=1080)
            controller = MouseController(fail_safe=False, pause_duration=0)
        
        # Perform a sequence of operations
        controller.move_to(100, 100)
        controller.click(100, 100)
        controller.double_click(200, 200)
        controller.right_click(300, 300)
        controller.drag(100, 100, 400, 400)
        controller.scroll(3, x=500, y=500)
        
        # Verify all operations were called
        assert mock_pyautogui.moveTo.call_count == 1
        assert mock_pyautogui.click.call_count == 3  # click, double_click, right_click
        assert mock_pyautogui.drag.call_count == 1
        assert mock_pyautogui.scroll.call_count == 1

    def test_error_recovery(self, mouse_controller, mock_pyautogui):
        """Test error recovery in mouse operations."""
        # First operation fails, second succeeds
        mock_pyautogui.click.side_effect = [Exception("First fails"), None]
        
        result1 = mouse_controller.click(100, 100)
        result2 = mouse_controller.click(200, 200)
        
        assert result1 == False
        assert result2 == True
        assert mock_pyautogui.click.call_count == 2

    def test_mouse_down_valid_coordinates(self, mouse_controller, mock_pyautogui):
        """Test pressing mouse button down with valid coordinates."""
        mock_pyautogui.mouseDown = Mock()
        
        result = mouse_controller.mouse_down(100, 200, button='left')
        
        assert result == True
        mock_pyautogui.moveTo.assert_called_once_with(100, 200)
        mock_pyautogui.mouseDown.assert_called_once_with(button='left')

    def test_mouse_down_invalid_coordinates(self, mouse_controller, mock_pyautogui):
        """Test pressing mouse button down with invalid coordinates."""
        mock_pyautogui.mouseDown = Mock()
        
        result = mouse_controller.mouse_down(-10, 200)
        
        assert result == False
        mock_pyautogui.moveTo.assert_not_called()
        mock_pyautogui.mouseDown.assert_not_called()

    def test_mouse_down_with_exception(self, mouse_controller, mock_pyautogui):
        """Test mouse down when pyautogui raises an exception."""
        mock_pyautogui.mouseDown = Mock(side_effect=Exception("Test exception"))
        
        result = mouse_controller.mouse_down(100, 200)
        
        assert result == False

    def test_mouse_up_valid(self, mouse_controller, mock_pyautogui):
        """Test releasing mouse button."""
        mock_pyautogui.mouseUp = Mock()
        
        result = mouse_controller.mouse_up(button='right')
        
        assert result == True
        mock_pyautogui.mouseUp.assert_called_once_with(button='right')

    def test_mouse_up_with_exception(self, mouse_controller, mock_pyautogui):
        """Test mouse up when pyautogui raises an exception."""
        mock_pyautogui.mouseUp = Mock(side_effect=Exception("Test exception"))
        
        result = mouse_controller.mouse_up()
        
        assert result == False

    def test_hold_mouse_button_valid(self, mouse_controller, mock_pyautogui):
        """Test holding mouse button for duration."""
        mock_pyautogui.mouseDown = Mock()
        mock_pyautogui.mouseUp = Mock()
        
        with patch('time.sleep') as mock_sleep:
            result = mouse_controller.hold_mouse_button(300, 400, button='middle', duration=2.5)
        
        assert result == True
        mock_pyautogui.moveTo.assert_called_once_with(300, 400)
        mock_pyautogui.mouseDown.assert_called_once_with(button='middle')
        mock_sleep.assert_called_once_with(2.5)
        mock_pyautogui.mouseUp.assert_called_once_with(button='middle')

    def test_hold_mouse_button_invalid_coordinates(self, mouse_controller, mock_pyautogui):
        """Test holding mouse button with invalid coordinates."""
        mock_pyautogui.mouseDown = Mock()
        mock_pyautogui.mouseUp = Mock()
        
        result = mouse_controller.hold_mouse_button(2000, 400)
        
        assert result == False
        mock_pyautogui.moveTo.assert_not_called()
        mock_pyautogui.mouseDown.assert_not_called()
        mock_pyautogui.mouseUp.assert_not_called()

    def test_hold_mouse_button_with_exception(self, mouse_controller, mock_pyautogui):
        """Test holding mouse button when pyautogui raises an exception."""
        mock_pyautogui.mouseDown = Mock(side_effect=Exception("Test exception"))
        mock_pyautogui.mouseUp = Mock()
        
        result = mouse_controller.hold_mouse_button(100, 200)
        
        assert result == False


if __name__ == "__main__":
    pytest.main([__file__])