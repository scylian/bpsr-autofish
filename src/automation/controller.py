"""
Main automation controller that coordinates mouse, keyboard, and computer vision operations.
"""
import time
import logging
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass

from .mouse import MouseController
from .keyboard import KeyboardController
from .vision import VisionController

logger = logging.getLogger(__name__)


@dataclass
class AutomationAction:
    """Represents an automation action to be executed."""
    action_type: str  # 'click', 'type', 'key', 'wait_for_image', etc.
    parameters: Dict[str, Any]
    condition: Optional[Callable[[], bool]] = None  # Optional condition function
    description: str = ""


@dataclass
class AutomationResult:
    """Result of an automation action."""
    success: bool
    action: AutomationAction
    details: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None


class AutomationController:
    """Main controller for coordinating automation operations."""
    
    def __init__(self, 
                 mouse_fail_safe: bool = True,
                 mouse_pause: float = 0.1,
                 keyboard_pause: float = 0.1,
                 vision_threshold: float = 0.8):
        """
        Initialize AutomationController.
        
        Args:
            mouse_fail_safe: Enable mouse fail-safe mode
            mouse_pause: Pause duration for mouse operations
            keyboard_pause: Pause duration for keyboard operations
            vision_threshold: Default matching threshold for computer vision
        """
        self.mouse = MouseController(fail_safe=mouse_fail_safe, pause_duration=mouse_pause)
        self.keyboard = KeyboardController(pause_duration=keyboard_pause)
        self.vision = VisionController(match_threshold=vision_threshold)
        
        # Action history for debugging and recovery
        self.action_history: List[AutomationResult] = []
        self.max_history = 100
        
        logger.info("AutomationController initialized")
    
    def execute_action(self, action: AutomationAction) -> AutomationResult:
        """
        Execute a single automation action.
        
        Args:
            action: AutomationAction to execute
        
        Returns:
            AutomationResult with execution details
        """
        start_time = time.time()
        
        try:
            logger.info(f"Executing action: {action.action_type} - {action.description}")
            
            # Check condition if provided
            if action.condition and not action.condition():
                logger.warning(f"Action condition not met: {action.description}")
                return AutomationResult(
                    success=False,
                    action=action,
                    details={'reason': 'condition_not_met'},
                    execution_time=time.time() - start_time,
                    error_message="Action condition not met"
                )
            
            # Execute the action based on type
            success, details = self._execute_by_type(action)
            
            result = AutomationResult(
                success=success,
                action=action,
                details=details,
                execution_time=time.time() - start_time
            )
            
            # Add to history (limit size)
            self.action_history.append(result)
            if len(self.action_history) > self.max_history:
                self.action_history.pop(0)
            
            logger.info(f"Action completed in {result.execution_time:.3f}s: {'SUCCESS' if success else 'FAILED'}")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Action execution failed: {str(e)}"
            logger.error(error_msg)
            
            result = AutomationResult(
                success=False,
                action=action,
                details={'exception': str(e)},
                execution_time=execution_time,
                error_message=error_msg
            )
            
            self.action_history.append(result)
            if len(self.action_history) > self.max_history:
                self.action_history.pop(0)
            
            return result
    
    def _execute_by_type(self, action: AutomationAction) -> tuple[bool, Dict[str, Any]]:
        """Execute action based on its type."""
        action_type = action.action_type.lower()
        params = action.parameters
        
        if action_type == 'click':
            success = self.mouse.click(
                params['x'], params['y'],
                button=params.get('button', 'left'),
                clicks=params.get('clicks', 1),
                duration=params.get('duration', 0.0)
            )
            return success, {'coordinates': (params['x'], params['y'])}
        
        elif action_type == 'double_click':
            success = self.mouse.double_click(
                params['x'], params['y'],
                button=params.get('button', 'left'),
                duration=params.get('duration', 0.0)
            )
            return success, {'coordinates': (params['x'], params['y'])}
        
        elif action_type == 'right_click':
            success = self.mouse.right_click(
                params['x'], params['y'],
                duration=params.get('duration', 0.0)
            )
            return success, {'coordinates': (params['x'], params['y'])}
        
        elif action_type == 'drag':
            success = self.mouse.drag(
                params['start_x'], params['start_y'],
                params['end_x'], params['end_y'],
                duration=params.get('duration', 1.0),
                button=params.get('button', 'left')
            )
            return success, {
                'start': (params['start_x'], params['start_y']),
                'end': (params['end_x'], params['end_y'])
            }
        
        elif action_type == 'scroll':
            success = self.mouse.scroll(
                params['clicks'],
                x=params.get('x'),
                y=params.get('y')
            )
            return success, {'scroll_clicks': params['clicks']}
        
        elif action_type == 'type':
            success = self.keyboard.type_text(
                params['text'],
                interval=params.get('interval', 0.0)
            )
            return success, {'text_length': len(params['text'])}
        
        elif action_type == 'key':
            success = self.keyboard.press_key(
                params['key'],
                presses=params.get('presses', 1),
                interval=params.get('interval', 0.0)
            )
            return success, {'key': params['key'], 'presses': params.get('presses', 1)}
        
        elif action_type == 'key_combination':
            success = self.keyboard.key_combination(params['keys'])
            return success, {'keys': params['keys']}
        
        elif action_type == 'wait':
            duration = params.get('duration', 1.0)
            time.sleep(duration)
            return True, {'wait_duration': duration}
        
        elif action_type == 'find_image':
            match = self.vision.find_on_screen(
                params['template_path'],
                region=params.get('region'),
                threshold=params.get('threshold')
            )
            success = match is not None
            return success, {'match': match}
        
        elif action_type == 'wait_for_image':
            match = self.vision.wait_for_image(
                params['template_path'],
                timeout=params.get('timeout', 10.0),
                check_interval=params.get('check_interval', 0.5),
                region=params.get('region')
            )
            success = match is not None
            return success, {'match': match}
        
        elif action_type == 'click_image':
            # Find image and click on it
            match = self.vision.find_on_screen(
                params['template_path'],
                region=params.get('region'),
                threshold=params.get('threshold')
            )
            if match:
                click_x, click_y = match['center']
                success = self.mouse.click(
                    click_x, click_y,
                    button=params.get('button', 'left'),
                    clicks=params.get('clicks', 1),
                    duration=params.get('duration', 0.0)
                )
                return success, {'match': match, 'clicked_at': (click_x, click_y)}
            else:
                return False, {'error': 'Image not found'}
        
        elif action_type == 'mouse_down':
            success = self.mouse.mouse_down(
                params['x'], params['y'],
                button=params.get('button', 'left')
            )
            return success, {'coordinates': (params['x'], params['y']), 'button': params.get('button', 'left')}
        
        elif action_type == 'mouse_up':
            success = self.mouse.mouse_up(
                button=params.get('button', 'left')
            )
            return success, {'button': params.get('button', 'left')}
        
        elif action_type == 'hold_mouse_button':
            success = self.mouse.hold_mouse_button(
                params['x'], params['y'],
                button=params.get('button', 'left'),
                duration=params.get('duration', 1.0)
            )
            return success, {
                'coordinates': (params['x'], params['y']),
                'button': params.get('button', 'left'),
                'duration': params.get('duration', 1.0)
            }
        
        elif action_type == 'key_down':
            success = self.keyboard.key_down(params['key'])
            return success, {'key': params['key']}
        
        elif action_type == 'key_up':
            success = self.keyboard.key_up(params['key'])
            return success, {'key': params['key']}
        
        elif action_type == 'hold_key':
            success = self.keyboard.hold_key(
                params['key'],
                duration=params.get('duration', 1.0)
            )
            return success, {'key': params['key'], 'duration': params.get('duration', 1.0)}
        
        elif action_type == 'get_pixel_color':
            color = self.vision.get_pixel_color(params['x'], params['y'])
            return True, {'color': color, 'coordinates': (params['x'], params['y'])}
        
        else:
            return False, {'error': f'Unknown action type: {action_type}'}
    
    def execute_sequence(self, actions: List[AutomationAction], 
                        stop_on_failure: bool = True) -> List[AutomationResult]:
        """
        Execute a sequence of automation actions.
        
        Args:
            actions: List of AutomationAction objects to execute
            stop_on_failure: Whether to stop sequence execution on first failure
        
        Returns:
            List of AutomationResult objects
        """
        results = []
        
        logger.info(f"Starting execution of {len(actions)} actions")
        
        for i, action in enumerate(actions):
            logger.debug(f"Executing action {i+1}/{len(actions)}")
            result = self.execute_action(action)
            results.append(result)
            
            if not result.success and stop_on_failure:
                logger.warning(f"Stopping sequence execution due to failure at action {i+1}")
                break
        
        successful_actions = sum(1 for r in results if r.success)
        logger.info(f"Sequence execution completed: {successful_actions}/{len(results)} actions successful")
        
        return results
    
    def create_click_action(self, x: int, y: int, button: str = 'left', 
                           clicks: int = 1, duration: float = 0.0,
                           description: str = "", condition: Optional[Callable] = None) -> AutomationAction:
        """Create a click action."""
        return AutomationAction(
            action_type='click',
            parameters={
                'x': x, 'y': y, 'button': button, 'clicks': clicks, 'duration': duration
            },
            condition=condition,
            description=description or f"Click at ({x}, {y})"
        )
    
    def create_type_action(self, text: str, interval: float = 0.0,
                          description: str = "", condition: Optional[Callable] = None) -> AutomationAction:
        """Create a type text action."""
        return AutomationAction(
            action_type='type',
            parameters={'text': text, 'interval': interval},
            condition=condition,
            description=description or f"Type: '{text[:30]}{'...' if len(text) > 30 else ''}'"
        )
    
    def create_key_action(self, key: str, presses: int = 1, interval: float = 0.0,
                         description: str = "", condition: Optional[Callable] = None) -> AutomationAction:
        """Create a key press action."""
        return AutomationAction(
            action_type='key',
            parameters={'key': key, 'presses': presses, 'interval': interval},
            condition=condition,
            description=description or f"Press key: {key} ({presses}x)"
        )
    
    def create_wait_action(self, duration: float,
                          description: str = "", condition: Optional[Callable] = None) -> AutomationAction:
        """Create a wait action."""
        return AutomationAction(
            action_type='wait',
            parameters={'duration': duration},
            condition=condition,
            description=description or f"Wait {duration}s"
        )
    
    def create_image_click_action(self, template_path: str, button: str = 'left',
                                 region: Optional[Dict] = None, threshold: Optional[float] = None,
                                 description: str = "", condition: Optional[Callable] = None) -> AutomationAction:
        """Create an action to find and click on an image."""
        return AutomationAction(
            action_type='click_image',
            parameters={
                'template_path': template_path, 'button': button,
                'region': region, 'threshold': threshold
            },
            condition=condition,
            description=description or f"Click image: {template_path}"
        )
    
    def get_last_results(self, count: int = 10) -> List[AutomationResult]:
        """Get the last N action results."""
        return self.action_history[-count:] if self.action_history else []
    
    def get_failed_actions(self, count: int = 10) -> List[AutomationResult]:
        """Get the last N failed actions."""
        failed = [r for r in self.action_history if not r.success]
        return failed[-count:] if failed else []
    
    def clear_history(self):
        """Clear the action history."""
        self.action_history.clear()
        logger.info("Action history cleared")


# Convenience functions for common automation patterns
def create_login_sequence(username: str, password: str, 
                         username_field_coords: tuple, password_field_coords: tuple,
                         login_button_coords: tuple) -> List[AutomationAction]:
    """Create a common login sequence."""
    controller = AutomationController()
    
    return [
        controller.create_click_action(*username_field_coords, description="Click username field"),
        controller.create_type_action(username, description="Type username"),
        controller.create_click_action(*password_field_coords, description="Click password field"),
        controller.create_type_action(password, description="Type password"),
        controller.create_click_action(*login_button_coords, description="Click login button")
    ]


def create_copy_paste_sequence(source_coords: tuple, dest_coords: tuple) -> List[AutomationAction]:
    """Create a copy-paste sequence."""
    controller = AutomationController()
    
    return [
        controller.create_click_action(*source_coords, description="Click source location"),
        AutomationAction('key_combination', {'keys': ['ctrl', 'a']}, description="Select all"),
        AutomationAction('key_combination', {'keys': ['ctrl', 'c']}, description="Copy"),
        controller.create_click_action(*dest_coords, description="Click destination"),
        AutomationAction('key_combination', {'keys': ['ctrl', 'v']}, description="Paste")
    ]