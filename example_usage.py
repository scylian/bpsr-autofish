"""
Example usage of the automation framework.

This script demonstrates how to use the mouse, keyboard, and automation controllers
for basic automation tasks. Before running the complex conditional logic with
computer vision, you can use this script to test the basic automation functionality.
"""

import time
import logging
from src.automation import MouseController, KeyboardController, AutomationController, AutomationAction

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def test_mouse_operations():
    """Test basic mouse operations."""
    print("\n=== Testing Mouse Operations ===")
    
    mouse = MouseController(fail_safe=True, pause_duration=0.5)
    
    # Get current mouse position
    current_pos = mouse.get_position()
    print(f"Current mouse position: {current_pos}")
    
    # Move mouse to a safe location (center of screen)
    screen_center_x = mouse.screen_size.width // 2
    screen_center_y = mouse.screen_size.height // 2
    
    print(f"Moving mouse to screen center: ({screen_center_x}, {screen_center_y})")
    mouse.move_to(screen_center_x, screen_center_y, duration=1.0)
    
    # Test clicking (be careful where you click!)
    print("Performing a single click...")
    mouse.click(screen_center_x, screen_center_y)
    
    print("Mouse operations completed!")


def test_keyboard_operations():
    """Test basic keyboard operations."""
    print("\n=== Testing Keyboard Operations ===")
    
    keyboard = KeyboardController(pause_duration=0.3)
    
    # Wait for user to position cursor
    print("Please open a text editor (like Notepad) and position your cursor.")
    print("Press Enter here when ready...")
    input()
    
    # Test typing
    keyboard.type_text("Hello, this is a test of the automation framework!")
    keyboard.press_key('enter')
    
    # Test key combinations
    keyboard.type_text("This text will be selected and copied.")
    keyboard.press_key('enter')
    
    # Select all and copy
    keyboard.key_combination(['ctrl', 'a'])
    time.sleep(0.5)
    keyboard.key_combination(['ctrl', 'c'])
    
    # Clear and paste
    keyboard.clear_text()
    keyboard.key_combination(['ctrl', 'v'])
    
    print("Keyboard operations completed!")


def test_automation_controller():
    """Test the automation controller with a sequence of actions."""
    print("\n=== Testing Automation Controller ===")
    
    controller = AutomationController(
        mouse_fail_safe=True,
        mouse_pause=0.5,
        keyboard_pause=0.3
    )
    
    # Create a sequence of actions
    actions = [
        controller.create_wait_action(1.0, "Wait for user to get ready"),
        controller.create_type_action("Testing automation sequence...", 
                                    description="Type test message"),
        controller.create_key_action('enter', description="Press Enter"),
        controller.create_key_action('enter', description="Press Enter again"),
        controller.create_type_action("This demonstrates the automation controller!", 
                                    description="Type second message"),
    ]
    
    print("Please position your cursor in a text editor.")
    print("Press Enter when ready...")
    input()
    
    # Execute the sequence
    results = controller.execute_sequence(actions, stop_on_failure=True)
    
    # Display results
    print(f"\nExecuted {len(results)} actions:")
    for i, result in enumerate(results, 1):
        status = "✓" if result.success else "✗"
        print(f"{status} Action {i}: {result.action.description} "
              f"({result.execution_time:.2f}s)")
    
    print("Automation controller test completed!")


def demonstrate_safety_features():
    """Demonstrate safety features of the automation framework."""
    print("\n=== Safety Features Demo ===")
    
    mouse = MouseController(fail_safe=True, pause_duration=0.1)
    
    print("The framework includes several safety features:")
    print("1. Coordinate validation - prevents clicking outside screen bounds")
    print("2. Key validation - prevents using invalid key names")
    print("3. Fail-safe mode - move mouse to top-left corner to stop")
    print("4. Pause duration - adds delays between operations")
    print("5. Exception handling - gracefully handles errors")
    
    # Test coordinate validation
    print("\nTesting coordinate validation...")
    result1 = mouse.click(-100, -100)  # Should fail
    result2 = mouse.click(10000, 10000)  # Should fail
    print(f"Invalid coordinates (-100, -100): {'Failed' if not result1 else 'Passed'}")
    print(f"Invalid coordinates (10000, 10000): {'Failed' if not result2 else 'Passed'}")
    
    # Test key validation
    keyboard = KeyboardController(pause_duration=0.1)
    result3 = keyboard.press_key('invalid_key')  # Should fail
    print(f"Invalid key 'invalid_key': {'Failed' if not result3 else 'Passed'}")
    
    print("Safety features demonstration completed!")


def main():
    """Main function to run all examples."""
    print("=== Automation Framework Example Usage ===")
    print("This script demonstrates the basic functionality of the automation framework.")
    print("\nWARNING: This will control your mouse and keyboard!")
    print("Make sure you're ready and have positioned windows appropriately.")
    print("You can press Ctrl+C to interrupt at any time.")
    
    response = input("\nDo you want to continue? (y/n): ").lower().strip()
    if response != 'y':
        print("Exiting...")
        return
    
    try:
        # Run demonstrations
        demonstrate_safety_features()
        test_mouse_operations()
        test_keyboard_operations() 
        test_automation_controller()
        
        print("\n=== All demonstrations completed successfully! ===")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run unit tests: python -m pytest tests/ -v")
        print("3. Start building your computer vision conditional logic")
        print("4. Use the VisionController for screen recognition tasks")
        print("5. Combine vision detection with mouse/keyboard automation")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting safely...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Check the logs for more details.")


if __name__ == "__main__":
    main()