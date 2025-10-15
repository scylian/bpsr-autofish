"""
Examples demonstrating pixel waiting functionality.

This shows how to:
1. Wait for a pixel to turn a specific color
2. Wait for a pixel to change from its current color
3. Use pixel waiting for fishing automation
4. Implement advanced pixel-based triggers
"""

import time
from src.automation import VisionController, MouseController, KeyboardController

def demo_wait_for_specific_color():
    """Demonstrate waiting for a pixel to turn a specific color."""
    print("=== Wait for Specific Pixel Color ===")
    
    vision = VisionController()
    mouse = MouseController()
    
    print("This demo waits for a pixel to turn a specific color.")
    print("Use cases:")
    print("  - Wait for fishing bobber to turn red (fish bite)")
    print("  - Wait for button to turn green (ready state)")
    print("  - Wait for health bar to turn red (low health)")
    
    # Get monitoring position
    print("\nPosition your mouse where you want to monitor...")
    input("Press Enter to set monitoring position...")
    
    monitor_pos = mouse.get_position()
    current_color = vision.get_pixel_color(*monitor_pos)
    
    print(f"✓ Monitoring pixel at {monitor_pos}")
    print(f"Current color: RGB{current_color}")
    
    # Get target color
    print("\nChoose target color:")
    print("1. Red (255, 0, 0) - for fish bite indicators")
    print("2. Green (0, 255, 0) - for ready indicators") 
    print("3. Blue (0, 0, 255) - for water/mana indicators")
    print("4. White (255, 255, 255) - for bright indicators")
    print("5. Custom color")
    
    choice = input("Choose (1-5): ").strip()
    
    color_options = {
        '1': (255, 0, 0),    # Red
        '2': (0, 255, 0),    # Green  
        '3': (0, 0, 255),    # Blue
        '4': (255, 255, 255), # White
    }
    
    if choice in color_options:
        target_color = color_options[choice]
    elif choice == '5':
        try:
            r = int(input("Enter Red (0-255): "))
            g = int(input("Enter Green (0-255): "))
            b = int(input("Enter Blue (0-255): "))
            target_color = (r, g, b)
        except ValueError:
            print("Invalid input, using red as default")
            target_color = (255, 0, 0)
    else:
        print("Invalid choice, using red as default")
        target_color = (255, 0, 0)
    
    tolerance = int(input(f"Enter color tolerance (0-50, default 10): ") or "10")
    timeout = float(input(f"Enter timeout in seconds (default 30): ") or "30")
    
    print(f"\n🔍 Waiting for pixel at {monitor_pos} to become RGB{target_color}")
    print(f"Tolerance: {tolerance}, Timeout: {timeout}s")
    print("Change something at that pixel location to test!")
    
    # Wait for the color change
    success = vision.wait_for_pixel_color(*monitor_pos, target_color, 
                                         tolerance=tolerance, timeout=timeout)
    
    if success:
        print("🎉 SUCCESS! Pixel reached the target color!")
        final_color = vision.get_pixel_color(*monitor_pos)
        print(f"Final color: RGB{final_color}")
    else:
        print("⏰ Timeout reached - pixel did not reach target color")

def demo_wait_for_any_change():
    """Demonstrate waiting for a pixel to change to any different color."""
    print("\n=== Wait for Any Pixel Change ===")
    
    vision = VisionController()
    mouse = MouseController()
    
    print("This demo waits for a pixel to change to ANY different color.")
    print("Use cases:")
    print("  - Detect when UI updates")
    print("  - Wait for animations to finish")
    print("  - Detect state transitions")
    
    # Get monitoring position
    print("\nPosition your mouse where you want to monitor...")
    input("Press Enter to set monitoring position...")
    
    monitor_pos = mouse.get_position()
    initial_color = vision.get_pixel_color(*monitor_pos)
    
    print(f"✓ Monitoring pixel at {monitor_pos}")
    print(f"Initial color: RGB{initial_color}")
    
    min_change = int(input("Enter minimum change threshold (default 20): ") or "20")
    timeout = float(input("Enter timeout in seconds (default 15): ") or "15")
    
    print(f"\n🔍 Waiting for pixel to change from RGB{initial_color}")
    print(f"Minimum change: {min_change}, Timeout: {timeout}s")
    print("Make any change at that pixel location!")
    
    # Wait for any color change
    changed, new_color = vision.wait_for_pixel_change(*monitor_pos, 
                                                     timeout=timeout, 
                                                     min_change=min_change)
    
    if changed:
        print("🎉 SUCCESS! Pixel color changed!")
        print(f"From: RGB{initial_color}")
        print(f"To:   RGB{new_color}")
        
        color_diff = sum(abs(a - b) for a, b in zip(initial_color, new_color))
        print(f"Total change: {color_diff}")
    else:
        print("⏰ Timeout reached - pixel did not change significantly")

def demo_fishing_automation():
    """Complete fishing automation example using pixel waiting."""
    print("\n=== Fishing Automation with Pixel Waiting ===")
    
    vision = VisionController()
    mouse = MouseController()
    keyboard = KeyboardController()
    
    print("This example shows complete fishing automation using pixel waiting.")
    print("\nSetup steps:")
    print("1. Position mouse over fishing bobber")
    print("2. System learns normal bobber color")
    print("3. Waits for bobber to turn red/orange (fish bite)")
    print("4. Automatically sets hook")
    
    # Setup bobber monitoring
    print("\nStep 1: Position mouse over your fishing bobber...")
    input("Press Enter when positioned...")
    
    bobber_pos = mouse.get_position()
    normal_color = vision.get_pixel_color(*bobber_pos)
    
    print(f"✓ Bobber position: {bobber_pos}")
    print(f"Normal bobber color: RGB{normal_color}")
    
    # Configure bite detection
    print("\nBite detection configuration:")
    bite_colors = [
        (255, 100, 0),   # Orange
        (255, 0, 0),     # Red
        (255, 150, 50),  # Light orange
    ]
    
    print("Common fish bite colors:")
    for i, color in enumerate(bite_colors, 1):
        print(f"  {i}. RGB{color}")
    print("  4. Custom color")
    
    choice = input("Choose bite color (1-4): ").strip()
    
    if choice in ['1', '2', '3']:
        bite_color = bite_colors[int(choice) - 1]
    elif choice == '4':
        try:
            r = int(input("Enter Red (0-255): "))
            g = int(input("Enter Green (0-255): "))
            b = int(input("Enter Blue (0-255): "))
            bite_color = (r, g, b)
        except ValueError:
            bite_color = (255, 100, 0)  # Default orange
    else:
        bite_color = (255, 100, 0)  # Default orange
    
    tolerance = int(input("Enter color tolerance (default 30): ") or "30")
    
    print(f"\n🎣 Fishing automation configured:")
    print(f"  Bobber position: {bobber_pos}")
    print(f"  Normal color: RGB{normal_color}")
    print(f"  Bite color: RGB{bite_color}")
    print(f"  Tolerance: {tolerance}")
    
    # Start fishing automation
    if input("\nStart fishing automation? (y/n): ").lower().strip() == 'y':
        print("\n🎣 Starting automated fishing...")
        print("Press Ctrl+C to stop")
        
        try:
            fish_caught = 0
            while True:
                print(f"\n--- Fishing Attempt #{fish_caught + 1} ---")
                
                # Wait for fish bite (bobber turns red/orange)
                print("🔍 Waiting for fish bite...")
                bite_detected = vision.wait_for_pixel_color(
                    *bobber_pos, bite_color, 
                    tolerance=tolerance, 
                    timeout=30.0,  # 30 second timeout
                    check_interval=0.05  # Check 20 times per second
                )
                
                if bite_detected:
                    print("🎣 FISH BITE DETECTED!")
                    
                    # Set the hook immediately
                    keyboard.press_key('space')
                    print("⚡ Hook set!")
                    
                    fish_caught += 1
                    
                    # Wait for bobber to return to normal (fish caught/escaped)
                    print("Waiting for catch to complete...")
                    returned_normal = vision.wait_for_pixel_color(
                        *bobber_pos, normal_color,
                        tolerance=20,
                        timeout=10.0
                    )
                    
                    if returned_normal:
                        print("✅ Fish caught/escaped - ready for next cast")
                    else:
                        print("⚠️ Bobber didn't return to normal - recalibrating...")
                        normal_color = vision.get_pixel_color(*bobber_pos)
                    
                    # Brief pause before next attempt
                    time.sleep(2.0)
                    
                else:
                    print("⏰ No bite detected within timeout - trying again")
                    
                    # Recast if needed (example - press '1' key)
                    keyboard.press_key('1')
                    time.sleep(1.0)
                
        except KeyboardInterrupt:
            print(f"\n\n🎣 Fishing automation stopped!")
            print(f"Fish caught: {fish_caught}")

def demo_advanced_pixel_triggers():
    """Advanced examples of pixel-based triggers."""
    print("\n=== Advanced Pixel-Based Triggers ===")
    
    vision = VisionController()
    mouse = MouseController()
    keyboard = KeyboardController()
    
    print("Advanced pixel trigger examples:")
    print("1. Health bar monitoring (red threshold)")
    print("2. Mana bar monitoring (blue threshold)")  
    print("3. Multi-pixel state detection")
    print("4. Pixel sequence detection")
    
    choice = input("Choose example (1-4): ").strip()
    
    if choice == "1":
        # Health bar monitoring
        print("\n💚 Health Bar Monitoring")
        print("Position mouse over health bar...")
        input("Press Enter...")
        
        health_pos = mouse.get_position()
        print(f"Monitoring health at {health_pos}")
        
        # Wait for health to drop (red component decreases)
        print("Waiting for low health (red < 150)...")
        
        try:
            while True:
                current_color = vision.get_pixel_color(*health_pos)
                if current_color[0] < 150:  # Red component too low
                    print("🚨 LOW HEALTH! Using health potion")
                    keyboard.press_key('h')
                    time.sleep(3.0)  # Wait for potion to take effect
                
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("Health monitoring stopped")
    
    elif choice == "2":
        # Mana bar monitoring
        print("\n💙 Mana Bar Monitoring")
        print("Position mouse over mana bar...")
        input("Press Enter...")
        
        mana_pos = mouse.get_position()
        print(f"Monitoring mana at {mana_pos}")
        
        try:
            while True:
                current_color = vision.get_pixel_color(*mana_pos)
                if current_color[2] < 100:  # Blue component too low
                    print("🔵 LOW MANA! Using mana potion")
                    keyboard.press_key('m')
                    time.sleep(3.0)
                
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("Mana monitoring stopped")
    
    elif choice == "3":
        # Multi-pixel state detection
        print("\n🔍 Multi-Pixel State Detection")
        print("Set up 3 monitoring points...")
        
        points = []
        for i in range(3):
            print(f"Position mouse for point {i+1}...")
            input("Press Enter...")
            pos = mouse.get_position()
            color = vision.get_pixel_color(*pos)
            points.append((pos, color))
            print(f"Point {i+1}: {pos} RGB{color}")
        
        print("\nMonitoring all points for changes...")
        try:
            while True:
                for i, (pos, original_color) in enumerate(points):
                    current_color = vision.get_pixel_color(*pos)
                    color_diff = sum(abs(a - b) for a, b in zip(original_color, current_color))
                    
                    if color_diff > 50:
                        print(f"Point {i+1} changed: RGB{original_color} → RGB{current_color}")
                        points[i] = (pos, current_color)  # Update reference
                
                time.sleep(0.2)
        except KeyboardInterrupt:
            print("Multi-point monitoring stopped")

def main():
    """Run pixel waiting examples."""
    print("=== Pixel Waiting Methods Demo ===")
    print("This demonstrates the new pixel waiting functionality:")
    print("  - wait_for_pixel_color() - Wait for specific color")
    print("  - wait_for_pixel_change() - Wait for any change")
    
    examples = [
        ("1", "Wait for specific color", demo_wait_for_specific_color),
        ("2", "Wait for any change", demo_wait_for_any_change),
        ("3", "Fishing automation example", demo_fishing_automation),
        ("4", "Advanced pixel triggers", demo_advanced_pixel_triggers),
    ]
    
    while True:
        print(f"\n🎯 Pixel Waiting Examples:")
        for num, name, _ in examples:
            print(f"{num}. {name}")
        print("5. Exit")
        
        choice = input(f"\nChoose example (1-5): ").strip()
        
        if choice == "5":
            print("👋 Goodbye!")
            break
        
        # Find and run the chosen example
        for num, name, func in examples:
            if choice == num:
                try:
                    func()
                except KeyboardInterrupt:
                    print("\n⚠️ Example interrupted")
                except Exception as e:
                    print(f"❌ Error: {e}")
                break
        else:
            print("❌ Invalid choice. Please try again.")
    
    print(f"\n📖 New Methods Summary:")
    print(f"vision.wait_for_pixel_color(x, y, target_color, tolerance, timeout)")
    print(f"  - Waits for pixel to become specific RGB color")
    print(f"  - Returns True if matched, False if timeout")
    print(f"")
    print(f"vision.wait_for_pixel_change(x, y, timeout, min_change)")
    print(f"  - Waits for pixel to change from current color")
    print(f"  - Returns (changed, new_color) tuple")

if __name__ == "__main__":
    main()