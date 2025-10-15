# BPSR AutoFish - Computer Vision Automation Framework

A Python automation framework that combines mouse/keyboard control with computer vision for intelligent screen-based automation tasks.

## 🚀 Features

- **Mouse Control**: Click, drag, scroll, and move operations with coordinate validation
- **Keyboard Control**: Type text, press keys, key combinations, and navigation
- **Computer Vision**: Screen capture, template matching, color detection (OpenCV-based)
- **Safety Features**: Fail-safe modes, coordinate validation, exception handling
- **Comprehensive Testing**: 62+ unit tests ensuring reliability
- **Easy Integration**: Modular design with clear API

## 📁 Project Structure

```
bpsr-autofish/
├── src/
│   └── automation/
│       ├── __init__.py           # Package exports
│       ├── mouse.py              # Mouse control operations
│       ├── keyboard.py           # Keyboard control operations  
│       ├── vision.py             # Computer vision functionality
│       └── controller.py         # Main automation controller
├── tests/
│   ├── test_mouse.py            # Mouse controller tests
│   └── test_keyboard.py         # Keyboard controller tests
├── requirements.txt             # Project dependencies
├── pytest.ini                  # Test configuration
├── example_usage.py            # Usage examples
└── README.md                   # This file
```

## 🔧 Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd bpsr-autofish
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run tests to verify installation:**
   ```bash
   python -m pytest tests/ -v
   ```

## 🎯 Quick Start

### Basic Mouse Operations

```python
from src.automation import MouseController

# Initialize mouse controller
mouse = MouseController(fail_safe=True, pause_duration=0.1)

# Click at specific coordinates
mouse.click(100, 200)

# Double-click and right-click
mouse.double_click(150, 250)
mouse.right_click(300, 400)

# Drag operations
mouse.drag(start_x=100, start_y=100, end_x=300, end_y=300)

# Scroll
mouse.scroll(3, x=400, y=500)  # Scroll up 3 clicks at position
```

### Basic Keyboard Operations

```python
from src.automation import KeyboardController

# Initialize keyboard controller
keyboard = KeyboardController(pause_duration=0.1)

# Type text
keyboard.type_text("Hello, World!")

# Press individual keys
keyboard.press_key('enter')
keyboard.press_key('tab', presses=3)

# Key combinations
keyboard.key_combination(['ctrl', 'c'])  # Copy
keyboard.key_combination(['ctrl', 'v'])  # Paste

# Navigation
keyboard.navigate('up', steps=5)  # Press up arrow 5 times
```

### Automation Controller (Recommended)

```python
from src.automation import AutomationController

# Initialize main controller
controller = AutomationController(
    mouse_fail_safe=True,
    mouse_pause=0.1,
    keyboard_pause=0.1
)

# Create action sequences
actions = [
    controller.create_click_action(100, 200, description="Click start button"),
    controller.create_type_action("Hello World", description="Type greeting"),
    controller.create_key_action('enter', description="Press Enter"),
    controller.create_wait_action(2.0, description="Wait 2 seconds")
]

# Execute sequence
results = controller.execute_sequence(actions, stop_on_failure=True)

# Check results
for result in results:
    print(f"Action: {result.action.description} - {'✓' if result.success else '✗'}")
```

### Computer Vision (Future Enhancement)

```python
from src.automation import VisionController

# Initialize vision controller
vision = VisionController(match_threshold=0.8)

# Find image on screen
match = vision.find_on_screen('template_images/button.png')
if match:
    print(f"Found image at: {match['center']}")
    
# Wait for image to appear
match = vision.wait_for_image('template_images/dialog.png', timeout=10.0)

# Get pixel color
color = vision.get_pixel_color(100, 200)
print(f"Pixel color (RGB): {color}")
```

## 🛡️ Safety Features

### 1. Coordinate Validation
```python
mouse = MouseController()
result = mouse.click(-100, -100)  # Returns False - invalid coordinates
```

### 2. Fail-Safe Mode
```python
# Move mouse to top-left corner (0,0) to trigger fail-safe
mouse = MouseController(fail_safe=True)
```

### 3. Key Validation
```python
keyboard = KeyboardController()
result = keyboard.press_key('invalid_key')  # Returns False - invalid key
```

### 4. Exception Handling
All operations return boolean success indicators and handle exceptions gracefully.

## 🧪 Testing

Run all tests:
```bash
python -m pytest tests/ -v
```

Run specific test file:
```bash
python -m pytest tests/test_mouse.py -v
python -m pytest tests/test_keyboard.py -v
```

Run tests with coverage (if installed):
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

## 📖 Example Usage Script

Run the included example to see the framework in action:

```bash
python example_usage.py
```

**⚠️ Warning**: This script will control your mouse and keyboard. Make sure you're prepared and have positioned windows appropriately.

## 🏗️ Architecture Overview

### Core Components

1. **MouseController**: Handles all mouse-related operations
   - Click operations (single, double, right-click)
   - Mouse movement and positioning
   - Drag and drop operations
   - Scroll functionality
   - Coordinate validation

2. **KeyboardController**: Manages keyboard input
   - Text typing with configurable intervals
   - Individual key presses
   - Key combinations and shortcuts
   - Navigation keys
   - Key validation

3. **VisionController**: Computer vision capabilities
   - Screen capture and regions
   - Template matching
   - Color detection
   - Image waiting and polling
   - Template caching for performance

4. **AutomationController**: High-level orchestration
   - Action sequencing
   - Result tracking and history
   - Conditional execution
   - Error handling and recovery
   - Helper methods for common patterns

### Dependencies

- **pyautogui**: Core automation library
- **opencv-python**: Computer vision operations
- **numpy**: Numerical operations for image processing
- **mss**: Fast screen capture
- **pytest**: Testing framework
- **PIL/Pillow**: Image processing support

## 🔮 Future Enhancements

1. **Advanced Computer Vision**
   - OCR text recognition
   - Object detection
   - GUI element recognition
   - Machine learning integration

2. **Enhanced Automation**
   - Conditional action execution
   - Loop and retry mechanisms
   - Configuration file support
   - Action recording and playback

3. **Monitoring & Debugging**
   - Real-time action visualization
   - Performance metrics
   - Debug mode with step-by-step execution
   - Action history export

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for new functionality
4. Ensure all tests pass (`python -m pytest tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## ⚠️ Disclaimers

- **Use Responsibly**: This framework can control your computer. Use it responsibly and test thoroughly.
- **Security**: Be careful with automation scripts that handle sensitive data or credentials.
- **Platform Support**: Primarily tested on Windows. Some features may need adjustment for macOS/Linux.
- **Dependencies**: Requires proper installation of OpenCV and related libraries.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [PyAutoGUI](https://pyautogui.readthedocs.io/) for automation
- Computer vision powered by [OpenCV](https://opencv.org/)
- Screen capture using [MSS](https://python-mss.readthedocs.io/)
- Testing with [pytest](https://pytest.org/)