"""
Automation package for mouse, keyboard, and computer vision operations.
"""
from .mouse import MouseController
from .keyboard import KeyboardController
from .vision import VisionController
from .controller import AutomationController, AutomationAction, AutomationResult
from .game_mouse import HybridMouseController, GameMouseController
from .game_keyboard import HybridKeyboardController, GameKeyboardController
from .pixel_watcher import EnhancedVisionController, PixelWatcherManager, PersistentPixelWatcher
from .transparent_vision import TransparentVisionController, TransparentImageMatcher, TemplateWatcherEvent, TemplateWatcherManager

__all__ = [
    'MouseController',
    'KeyboardController', 
    'VisionController',
    'AutomationController',
    'AutomationAction',
    'AutomationResult',
    'HybridMouseController',
    'GameMouseController',
    'HybridKeyboardController',
    'GameKeyboardController',
    'EnhancedVisionController',
    'PixelWatcherManager',
    'PersistentPixelWatcher',
    'TransparentVisionController',
    'TransparentImageMatcher',
    'TemplateWatcherEvent',
    'TemplateWatcherManager'
]
