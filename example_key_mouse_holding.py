"""
Example demonstrating how to hold down keyboard keys and mouse buttons simultaneously.

This is perfect for gaming applications where you need to hold multiple controls at once,
such as holding a movement key while also holding down a mouse button to aim or cast.
"""

import time
from src.automation import MouseController, KeyboardController

def example_simultaneous_holding():
    """Demonstrate holding keyboard key and mouse button at the same time."""
    print("=== Simultaneous Key and Mouse Holding Example ===")
    
    mouse = MouseController(fail_safe=True, pause_duration=0.1)
    keyboard = KeyboardController(pause_duration=0.1)
    
    # Get screen center for safe mouse operations
    screen_center_x = mouse.screen_size.width // 2
    screen_center_y = mouse.screen_size.height // 2
    
    print("This example will:")
    print("1. Hold down the 'W' key (movement)")
    print("2. Simultaneously hold down the left mouse button")
    print("3. Keep both held for 3 seconds")
    print("4. Release both")
    print("\nPress Enter when ready...")
    input()
    
    print("Starting simultaneous hold...")
    
    # Method 1: Manual control with key_down/key_up and mouse_down/mouse_up
    print("Phase 1: Manual control")
    
    # Press and hold keyboard key
    keyboard.key_down('w')
    print("✓ W key pressed down")
    
    # Press and hold mouse button at screen center
    mouse.mouse_down(screen_center_x, screen_center_y, button='left')
    print("✓ Left mouse button pressed down")
    
    # Hold both for 3 seconds
    print("Holding both for 3 seconds...")
    time.sleep(3.0)
    
    # Release both
    keyboard.key_up('w')
    print("✓ W key released")
    
    mouse.mouse_up(button='left')
    print("✓ Left mouse button released")
    
    print("Phase 1 completed!\n")


def example_gaming_scenario():
    """Example of a typical gaming scenario."""
    print("=== Gaming Scenario Example ===")
    
    mouse = MouseController(fail_safe=True, pause_duration=0.1)
    keyboard = KeyboardController(pause_duration=0.1)
    
    screen_center_x = mouse.screen_size.width // 2
    screen_center_y = mouse.screen_size.height // 2
    
    print("Gaming scenario: Hold Shift (run) + W (forward) + Right Mouse (aim)")
    print("Press Enter when ready...")
    input()
    
    # Complex gaming sequence
    print("Starting gaming sequence...")
    
    # 1. Start running (hold Shift)
    keyboard.key_down('shift')
    print("✓ Started running (Shift held)")
    
    # 2. Start moving forward (hold W)
    keyboard.key_down('w')
    print("✓ Started moving forward (W held)")
    
    # 3. Start aiming (hold right mouse button)
    mouse.mouse_down(screen_center_x, screen_center_y, button='right')
    print("✓ Started aiming (Right mouse held)")
    
    # 4. Hold all three for 2 seconds
    print("Performing action (all buttons held)...")
    time.sleep(2.0)
    
    # 5. Release aiming but keep moving
    mouse.mouse_up(button='right')
    print("✓ Stopped aiming")
    
    # 6. Continue moving for 1 more second
    time.sleep(1.0)
    
    # 7. Stop running but keep walking
    keyboard.key_up('shift')
    print("✓ Stopped running")
    
    # 8. Walk for 1 more second
    time.sleep(1.0)
    
    # 9. Stop moving
    keyboard.key_up('w')
    print("✓ Stopped moving")
    
    print("Gaming sequence completed!\n")


def example_with_automation_controller():
    """Example using the AutomationController for complex sequences."""
    print("=== Using AutomationController for Complex Sequences ===")
    
    from src.automation import AutomationController, AutomationAction
    
    controller = AutomationController(
        mouse_fail_safe=True,
        mouse_pause=0.1,
        keyboard_pause=0.1
    )
    
    print("This will demonstrate a complex automation sequence.")
    print("Press Enter when ready...")
    input()
    
    # Create a complex sequence that involves both keyboard and mouse holding
    actions = [
        # Start the sequence
        AutomationAction('key_down', {'key': 'shift'}, description="Start running"),
        controller.create_wait_action(0.5, "Brief pause"),
        
        # Add movement
        AutomationAction('key_down', {'key': 'w'}, description="Start moving forward"),
        controller.create_wait_action(0.5, "Brief pause"),
        
        # Add mouse interaction
        AutomationAction('mouse_down', {'x': 500, 'y': 400, 'button': 'right'}, 
                        description="Start aiming"),
        controller.create_wait_action(2.0, "Perform action"),
        
        # Release in reverse order
        AutomationAction('mouse_up', {'button': 'right'}, description="Stop aiming"),
        controller.create_wait_action(0.5, "Brief pause"),
        
        AutomationAction('key_up', {'key': 'w'}, description="Stop moving"),
        controller.create_wait_action(0.5, "Brief pause"),
        
        AutomationAction('key_up', {'key': 'shift'}, description="Stop running"),
    ]
    
    # Execute the sequence
    results = controller.execute_sequence(actions, stop_on_failure=True)
    
    # Show results
    print("\nSequence Results:")
    for i, result in enumerate(results, 1):
        status = "✓" if result.success else "✗"
        print(f"{status} Step {i}: {result.action.description}")
    
    print("AutomationController sequence completed!\n")


def example_fishing_game_scenario():
    """Example specifically for fishing game mechanics."""
    print("=== Fishing Game Scenario ===")
    
    mouse = MouseController(fail_safe=True, pause_duration=0.1)
    keyboard = KeyboardController(pause_duration=0.1)
    
    screen_center_x = mouse.screen_size.width // 2  
    screen_center_y = mouse.screen_size.height // 2
    
    print("Fishing game simulation:")
    print("1. Hold Space to charge cast")
    print("2. Hold mouse to aim")
    print("3. Release both to cast")
    print("4. Hold mouse to reel in")
    print("\nPress Enter when ready...")
    input()
    
    print("=== CASTING PHASE ===")
    
    # Phase 1: Charging cast
    keyboard.key_down('space')
    print("✓ Charging cast (Space held)...")
    time.sleep(1.5)
    
    # Phase 2: Aiming while charging
    mouse.mouse_down(screen_center_x, screen_center_y, button='left')
    print("✓ Aiming while charging (Mouse + Space held)...")
    time.sleep(1.0)
    
    # Phase 3: Release to cast
    keyboard.key_up('space')
    mouse.mouse_up(button='left')
    print("✓ CAST! (Both released)")
    time.sleep(0.5)
    
    print("\n=== REELING PHASE ===")
    
    # Phase 4: Reeling in
    print("Reeling in fish...")
    mouse.hold_mouse_button(screen_center_x, screen_center_y, button='left', duration=3.0)
    print("✓ Fish caught!")
    
    print("Fishing scenario completed!\n")


def main():
    """Main function to run all examples."""
    print("=== Keyboard + Mouse Button Holding Examples ===")
    print("This demonstrates the framework's ability to hold keyboard keys")
    print("and mouse buttons simultaneously - perfect for gaming automation!")
    
    print("\nAvailable methods:")
    print("🔹 keyboard.key_down(key) + keyboard.key_up(key)")
    print("🔹 keyboard.hold_key(key, duration)")
    print("🔹 mouse.mouse_down(x, y, button) + mouse.mouse_up(button)")
    print("🔹 mouse.hold_mouse_button(x, y, button, duration)")
    
    response = input("\nRun examples? (y/n): ").lower().strip()
    if response != 'y':
        print("Exiting...")
        return
    
    try:
        # Run all examples
        example_simultaneous_holding()
        
        time.sleep(1)
        example_gaming_scenario()
        
        time.sleep(1)
        example_with_automation_controller()
        
        time.sleep(1)
        example_fishing_game_scenario()
        
        print("=== All Examples Completed Successfully! ===")
        print("\nYou now have full control over simultaneous keyboard and mouse operations!")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting safely...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()