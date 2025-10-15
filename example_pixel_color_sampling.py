"""
Example demonstrating pixel color sampling with VisionController.

This shows how to:
1. Get RGB values of specific pixels
2. Monitor pixel colors for changes
3. Use pixel sampling for automation triggers
4. Create color-based automation logic
"""

import time
from src.automation import VisionController, MouseController, KeyboardController

def demo_basic_pixel_sampling():
    """Demonstrate basic pixel color sampling."""
    print("=== Basic Pixel Color Sampling ===")
    
    vision = VisionController()
    mouse = MouseController()
    
    # Sample some common screen locations
    test_coordinates = [
        (100, 100),    # Top-left area
        (960, 540),    # Screen center (assuming 1920x1080)
        (1800, 100),   # Top-right area
        (100, 980),    # Bottom-left area
        (1800, 980),   # Bottom-right area
    ]
    
    print("Sampling pixel colors at various screen locations:")
    for x, y in test_coordinates:
        rgb_color = vision.get_pixel_color(x, y)
        print(f"  Pixel at ({x:4d}, {y:4d}): RGB{rgb_color}")
    
    print("\nInteractive pixel sampling:")
    print("Position your mouse where you want to sample and press Enter...")
    
    input("Press Enter to sample current mouse position...")
    mouse_pos = mouse.get_position()
    sampled_color = vision.get_pixel_color(*mouse_pos)
    
    print(f"✓ Sampled color at mouse position {mouse_pos}: RGB{sampled_color}")
    print(f"  Red component: {sampled_color[0]}")
    print(f"  Green component: {sampled_color[1]}")
    print(f"  Blue component: {sampled_color[2]}")

def demo_color_change_detection():
    """Monitor a pixel for color changes."""
    print("\n=== Color Change Detection ===")
    
    vision = VisionController()
    mouse = MouseController()
    
    print("This demo monitors a pixel for color changes.")
    print("Useful for detecting:")
    print("  - UI state changes")
    print("  - Health bar changes") 
    print("  - Fish bite indicators")
    print("  - Button state changes")
    
    # Get monitoring position
    print("\nPosition your mouse over the pixel you want to monitor...")
    input("Press Enter to set monitoring position...")
    
    monitor_pos = mouse.get_position()
    print(f"✓ Monitoring pixel at {monitor_pos}")
    
    # Get initial color
    initial_color = vision.get_pixel_color(*monitor_pos)
    print(f"Initial color: RGB{initial_color}")
    
    print("\nMonitoring for changes... (Press Ctrl+C to stop)")
    print("Try changing something on screen at that location!")
    
    try:
        change_threshold = 30  # How much RGB values need to change
        while True:
            current_color = vision.get_pixel_color(*monitor_pos)
            
            # Calculate color difference
            color_diff = sum(abs(a - b) for a, b in zip(initial_color, current_color))
            
            if color_diff > change_threshold:
                print(f"🔍 Color change detected!")
                print(f"  From: RGB{initial_color}")
                print(f"  To:   RGB{current_color}")
                print(f"  Difference: {color_diff}")
                
                # Update initial color for next comparison
                initial_color = current_color
            
            time.sleep(0.1)  # Check 10 times per second
            
    except KeyboardInterrupt:
        print("\n✓ Monitoring stopped")

def demo_fishing_bite_detection():
    """Example of using pixel sampling for fishing bite detection."""
    print("\n=== Fishing Bite Detection Example ===")
    
    vision = VisionController()
    mouse = MouseController()
    keyboard = KeyboardController()
    
    print("This example shows how to use pixel color sampling")
    print("to detect when a fish bites in a fishing game.")
    print("\nTypical fishing games change the bobber color when fish bite:")
    print("  - Normal: White/Gray bobber")
    print("  - Bite:   Red/Orange bobber")
    
    # Set up monitoring position
    print("\nStep 1: Position mouse over your fishing bobber...")
    input("Press Enter to set bobber monitoring position...")
    
    bobber_pos = mouse.get_position()
    print(f"✓ Monitoring bobber at {bobber_pos}")
    
    # Sample normal bobber color
    normal_color = vision.get_pixel_color(*bobber_pos)
    print(f"Normal bobber color: RGB{normal_color}")
    
    # Define what we consider a "bite" color change
    bite_threshold = 50  # RGB difference threshold
    
    print(f"\nFishing automation logic:")
    print(f"  1. Monitor pixel at {bobber_pos}")
    print(f"  2. When color changes by >{bite_threshold}, fish has bitten")
    print(f"  3. Press Space to set hook")
    
    simulate = input("\nRun simulation? (y/n): ").lower().strip() == 'y'
    
    if simulate:
        print("\nSimulating fishing bite detection...")
        print("Change the color at the bobber position to trigger detection!")
        print("(Press Ctrl+C to stop)")
        
        try:
            while True:
                current_color = vision.get_pixel_color(*bobber_pos)
                color_diff = sum(abs(a - b) for a, b in zip(normal_color, current_color))
                
                if color_diff > bite_threshold:
                    print("🎣 FISH BITE DETECTED!")
                    print(f"  Color changed from RGB{normal_color} to RGB{current_color}")
                    print("  Setting hook...")
                    
                    # Set the hook (press Space)
                    keyboard.press_key('space')
                    
                    # Wait a bit before resuming monitoring
                    print("  Waiting for next cast...")
                    time.sleep(3.0)
                    
                    # Update normal color (bobber might look different after catch)
                    normal_color = vision.get_pixel_color(*bobber_pos)
                    print(f"  Updated normal color: RGB{normal_color}")
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n✓ Fishing simulation stopped")

def demo_health_bar_monitoring():
    """Example of monitoring health bar using pixel sampling."""
    print("\n=== Health Bar Monitoring Example ===")
    
    vision = VisionController()
    keyboard = KeyboardController()
    mouse = MouseController()
    
    print("This example shows how to monitor a health bar using pixel sampling.")
    print("Many games use red pixels to show health, which decreases as you take damage.")
    
    # Get health bar position
    print("\nPosition mouse over your health bar (red part)...")
    input("Press Enter to set health monitoring position...")
    
    health_pos = mouse.get_position()
    print(f"✓ Monitoring health at {health_pos}")
    
    # Sample initial health color
    health_color = vision.get_pixel_color(*health_pos)
    print(f"Current health pixel color: RGB{health_color}")
    
    # Define what we consider "healthy" red
    red_threshold = 150  # Minimum red component for healthy
    
    print(f"\nHealth monitoring logic:")
    print(f"  - Red component > {red_threshold}: Healthy")
    print(f"  - Red component < {red_threshold}: Low health, use potion")
    
    simulate = input("\nRun health monitoring simulation? (y/n): ").lower().strip() == 'y'
    
    if simulate:
        print("\nMonitoring health... (Press Ctrl+C to stop)")
        print("Try opening a dark window over the health bar to simulate damage!")
        
        try:
            while True:
                current_color = vision.get_pixel_color(*health_pos)
                red_component = current_color[0]
                
                if red_component < red_threshold:
                    print("⚠️ LOW HEALTH DETECTED!")
                    print(f"  Red component: {red_component} (below threshold {red_threshold})")
                    print("  Using health potion... (pressing 'H')")
                    
                    keyboard.press_key('h')  # Health potion hotkey
                    
                    # Wait before checking again
                    time.sleep(2.0)
                else:
                    print(f"Health OK - Red: {red_component}")
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n✓ Health monitoring stopped")

def demo_pixel_based_automation():
    """Complete automation example using pixel sampling."""
    print("\n=== Pixel-Based Automation Example ===")
    
    vision = VisionController()
    mouse = MouseController()
    keyboard = KeyboardController()
    
    print("This example shows a complete automation workflow using pixel sampling:")
    print("1. Monitor multiple pixels for different game states")
    print("2. Take actions based on pixel color changes")
    print("3. Implement a simple state machine")
    
    # Set up monitoring positions
    monitoring_points = {}
    
    points_to_setup = [
        ("health_bar", "Position over health bar (red pixels)"),
        ("mana_bar", "Position over mana bar (blue pixels)"),
        ("ready_indicator", "Position over ability ready indicator"),
    ]
    
    for point_name, description in points_to_setup:
        print(f"\n{description}...")
        if input(f"Set up {point_name} monitoring? (y/n): ").lower().strip() == 'y':
            input("Position mouse and press Enter...")
            pos = mouse.get_position()
            color = vision.get_pixel_color(*pos)
            monitoring_points[point_name] = {
                'position': pos,
                'normal_color': color
            }
            print(f"✓ {point_name} monitoring set at {pos} with color RGB{color}")
    
    if not monitoring_points:
        print("No monitoring points set up. Exiting...")
        return
    
    print(f"\n✅ Monitoring setup complete!")
    print(f"Monitoring {len(monitoring_points)} points:")
    for name, data in monitoring_points.items():
        print(f"  - {name}: {data['position']} RGB{data['normal_color']}")
    
    # Run monitoring loop
    if input("\nStart monitoring loop? (y/n): ").lower().strip() == 'y':
        print("\nStarting pixel-based automation... (Press Ctrl+C to stop)")
        
        try:
            while True:
                for name, data in monitoring_points.items():
                    pos = data['position']
                    normal_color = data['normal_color']
                    current_color = vision.get_pixel_color(*pos)
                    
                    # Calculate color difference
                    color_diff = sum(abs(a - b) for a, b in zip(normal_color, current_color))
                    
                    if color_diff > 50:  # Significant change detected
                        print(f"🔍 {name} changed: RGB{normal_color} → RGB{current_color}")
                        
                        # Take action based on which point changed
                        if name == "health_bar" and current_color[0] < 100:  # Red component low
                            print("  → Using health potion")
                            keyboard.press_key('h')
                        elif name == "mana_bar" and current_color[2] < 100:  # Blue component low
                            print("  → Using mana potion")
                            keyboard.press_key('m')
                        elif name == "ready_indicator":
                            print("  → Ability ready, using it")
                            keyboard.press_key('1')
                        
                        # Update normal color
                        monitoring_points[name]['normal_color'] = current_color
                
                time.sleep(0.2)  # Check 5 times per second
                
        except KeyboardInterrupt:
            print("\n✓ Automation stopped")

def main():
    """Run pixel color sampling examples."""
    print("=== Pixel Color Sampling with VisionController ===")
    print("This demonstrates how to use vision.get_pixel_color(x, y)")
    print("for various automation scenarios.")
    
    examples = [
        ("1", "Basic pixel sampling", demo_basic_pixel_sampling),
        ("2", "Color change detection", demo_color_change_detection),
        ("3", "Fishing bite detection", demo_fishing_bite_detection),
        ("4", "Health bar monitoring", demo_health_bar_monitoring),
        ("5", "Complete pixel automation", demo_pixel_based_automation),
    ]
    
    while True:
        print(f"\n🎯 Pixel Sampling Examples:")
        for num, name, _ in examples:
            print(f"{num}. {name}")
        print("6. Exit")
        
        choice = input(f"\nChoose example (1-6): ").strip()
        
        if choice == "6":
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
    
    print(f"\n📖 Summary:")
    print(f"vision.get_pixel_color(x, y) returns RGB tuple (R, G, B)")
    print(f"  - Values range from 0-255 for each color component")
    print(f"  - Perfect for monitoring UI state changes")
    print(f"  - Fast and efficient for real-time automation")

if __name__ == "__main__":
    main()