"""
Comprehensive examples of VisionController usage for computer vision automation.

This demonstrates all the current capabilities of the VisionController including:
- Template matching (finding images on screen)
- Color detection
- Screen capture and region-specific searching
- Pixel color detection
- Waiting for images to appear
"""

import time
import os
from src.automation import VisionController, MouseController
from src.automation.vision import create_hsv_range, rgb_to_hsv_range

def setup_demo_environment():
    """Create directories for template images and screenshots."""
    os.makedirs("templates", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    print("✓ Created templates/ and screenshots/ directories")

def demo_basic_vision_usage():
    """Demonstrate basic VisionController usage."""
    print("\n=== Basic Vision Controller Usage ===")
    
    # Initialize with custom threshold
    vision = VisionController(match_threshold=0.8)
    
    # 1. SCREEN CAPTURE
    print("\n1. Screen Capture Capabilities:")
    
    # Capture full screen and save it
    vision.screen_capture.save_screenshot("screenshots/fullscreen.png")
    print("✓ Captured full screen -> screenshots/fullscreen.png")
    
    # Capture specific region (example: top-left quarter of screen)
    region = {
        'top': 0,
        'left': 0, 
        'width': 400,
        'height': 300
    }
    vision.screen_capture.save_screenshot("screenshots/region.png", region)
    print("✓ Captured region -> screenshots/region.png")
    
    # 2. PIXEL COLOR DETECTION
    print("\n2. Pixel Color Detection:")
    
    # Get color of pixel at screen center
    screen_width = 1920  # Adjust based on your screen
    screen_height = 1080
    center_x = screen_width // 2
    center_y = screen_height // 2
    
    pixel_color = vision.get_pixel_color(center_x, center_y)
    print(f"✓ Pixel color at screen center ({center_x}, {center_y}): RGB{pixel_color}")
    
    # Check multiple points
    points_to_check = [
        (100, 100),   # Top-left area
        (center_x, center_y),  # Center
        (screen_width-100, screen_height-100)  # Bottom-right area
    ]
    
    for x, y in points_to_check:
        color = vision.get_pixel_color(x, y)
        print(f"  Pixel at ({x}, {y}): RGB{color}")

def demo_template_matching():
    """Demonstrate template matching capabilities."""
    print("\n=== Template Matching Demo ===")
    
    vision = VisionController(match_threshold=0.7)
    
    print("Template matching allows you to find specific images on screen.")
    print("You need to provide template images (screenshots of UI elements you want to find).")
    
    # Example usage (these files would need to exist)
    template_examples = [
        "templates/start_button.png",
        "templates/fishing_rod_icon.png", 
        "templates/fish_caught_dialog.png",
        "templates/inventory_slot.png"
    ]
    
    print("\nExample template files you might create:")
    for template in template_examples:
        print(f"  📁 {template}")
    
    print("\nHow to use template matching:")
    print("""
    # Find a UI element on screen
    match = vision.find_on_screen('templates/start_button.png')
    if match:
        print(f"Found button at: {match['center']}")
        print(f"Confidence: {match['confidence']:.2f}")
        
        # Click on the found button
        mouse = MouseController()
        mouse.click(*match['center'])
    """)
    
    print("\nAdvanced usage with regions:")
    print("""
    # Search only in specific area (faster, more accurate)
    ui_region = {'top': 0, 'left': 0, 'width': 400, 'height': 100}
    match = vision.find_on_screen('templates/menu_item.png', region=ui_region)
    """)
    
    print("\nWaiting for elements to appear:")
    print("""
    # Wait up to 10 seconds for a dialog to appear
    dialog = vision.wait_for_image('templates/confirmation_dialog.png', timeout=10.0)
    if dialog:
        # Dialog appeared, interact with it
        mouse.click(*dialog['center'])
    else:
        print("Dialog didn't appear within timeout")
    """)

def demo_color_detection():
    """Demonstrate color-based detection."""
    print("\n=== Color Detection Demo ===")
    
    vision = VisionController()
    
    print("Color detection finds objects/regions based on their color.")
    print("Useful for:")
    print("  - Finding UI elements by their distinctive colors")
    print("  - Detecting game objects (health bars, fish, etc.)")
    print("  - Monitoring status indicators")
    
    # Capture current screen for color detection
    screen = vision.screen_capture.capture_screen()
    
    if screen.size > 0:
        print(f"✓ Captured screen for analysis: {screen.shape}")
        
        # Example color ranges for common UI elements
        color_examples = [
            ("Red (Health bars, errors)", rgb_to_hsv_range(255, 0, 0, tolerance=30)),
            ("Green (Success, go buttons)", rgb_to_hsv_range(0, 255, 0, tolerance=30)),
            ("Blue (Water, info)", rgb_to_hsv_range(0, 100, 255, tolerance=30)),
            ("Yellow (Warnings, gold)", rgb_to_hsv_range(255, 255, 0, tolerance=30)),
        ]
        
        print("\nAnalyzing screen for common colors:")
        for color_name, color_range in color_examples:
            regions = vision.color_detector.find_color_regions(screen, color_range)
            print(f"  {color_name}: Found {len(regions)} regions")
            
            # Show details for largest region
            if regions:
                largest = max(regions, key=lambda r: r['area'])
                x, y, w, h = largest['bbox']
                center = largest['center']
                print(f"    Largest region: {w}x{h} at {center}, area={largest['area']}")
    
    print("\nCustom color detection example:")
    print("""
    # Create custom color range
    fishing_line_color = rgb_to_hsv_range(200, 200, 200, tolerance=20)  # Light gray
    
    # Find all fishing line segments
    line_segments = vision.color_detector.find_color_regions(screen, fishing_line_color)
    
    # Process each segment
    for segment in line_segments:
        center_x, center_y = segment['center']
        area = segment['area']
        if area > 50:  # Filter small noise
            print(f"Found fishing line at ({center_x}, {center_y})")
    """)

def demo_practical_gaming_scenarios():
    """Show practical gaming automation scenarios."""
    print("\n=== Practical Gaming Scenarios ===")
    
    print("Here are common computer vision patterns for game automation:")
    
    scenarios = [
        {
            "name": "🎣 Fishing Game Automation",
            "description": "Monitor fishing rod states and fish indicators",
            "code": """
# Wait for fishing cast to be ready
cast_ready = vision.wait_for_image('templates/cast_ready_button.png', timeout=5.0)
if cast_ready:
    mouse.click(*cast_ready['center'])

# Monitor for fish bite indicator (color change)
fishing_area = {'top': 200, 'left': 300, 'width': 400, 'height': 300}
bite_color = rgb_to_hsv_range(255, 100, 0, tolerance=25)  # Orange bite indicator

while True:
    screen = vision.screen_capture.capture_screen(fishing_area)
    bite_regions = vision.color_detector.find_color_regions(screen, bite_color)
    
    if bite_regions and bite_regions[0]['area'] > 100:
        print("Fish bite detected!")
        keyboard.press_key('space')  # Set hook
        break
    time.sleep(0.1)
"""
        },
        {
            "name": "🎮 GUI Automation",
            "description": "Navigate menus and click buttons",
            "code": """
# Click through a series of menu items
menu_items = [
    'templates/inventory_button.png',
    'templates/fishing_tab.png', 
    'templates/bait_slot.png'
]

for item_template in menu_items:
    item = vision.find_on_screen(item_template)
    if item:
        mouse.click(*item['center'])
        time.sleep(0.5)  # Wait for UI to update
    else:
        print(f"Could not find {item_template}")
        break
"""
        },
        {
            "name": "⚡ Real-time Monitoring",
            "description": "Monitor health, mana, or status bars",
            "code": """
# Monitor health bar by color
health_area = {'top': 50, 'left': 50, 'width': 200, 'height': 20}
red_health = rgb_to_hsv_range(255, 0, 0, tolerance=30)

while True:
    screen = vision.screen_capture.capture_screen(health_area) 
    red_regions = vision.color_detector.find_color_regions(screen, red_health)
    
    total_red_area = sum(r['area'] for r in red_regions)
    health_percentage = (total_red_area / (200 * 20)) * 100
    
    if health_percentage < 30:
        print("Low health! Using health potion")
        keyboard.press_key('h')  # Health potion hotkey
        break
        
    time.sleep(0.5)
"""
        },
        {
            "name": "🔄 State Machine Automation",
            "description": "Different actions based on game state",
            "code": """
def detect_game_state(vision):
    # Check for different UI states
    if vision.find_on_screen('templates/main_menu.png'):
        return 'main_menu'
    elif vision.find_on_screen('templates/in_game_ui.png'):
        return 'playing' 
    elif vision.find_on_screen('templates/inventory_open.png'):
        return 'inventory'
    elif vision.find_on_screen('templates/fishing_ui.png'):
        return 'fishing'
    else:
        return 'unknown'

# State-based automation loop
while True:
    state = detect_game_state(vision)
    
    if state == 'main_menu':
        play_button = vision.find_on_screen('templates/play_button.png')
        if play_button:
            mouse.click(*play_button['center'])
    
    elif state == 'playing':
        # Start fishing
        fishing_spot = vision.find_on_screen('templates/fishing_spot.png')
        if fishing_spot:
            mouse.click(*fishing_spot['center'])
    
    elif state == 'fishing':
        # Handle fishing logic here
        pass
    
    time.sleep(1.0)
"""
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}")
        print(f"Description: {scenario['description']}")
        print("Code example:")
        print(scenario['code'])

def demo_region_optimization():
    """Show how to optimize performance with regions."""
    print("\n=== Performance Optimization with Regions ===")
    
    vision = VisionController()
    
    print("Regions dramatically improve performance by:")
    print("  1. Reducing screenshot size")
    print("  2. Limiting template matching area") 
    print("  3. Reducing false positives")
    print("  4. Enabling parallel processing of different UI areas")
    
    # Example region definitions for a typical game UI
    ui_regions = {
        'top_menu': {'top': 0, 'left': 0, 'width': 1920, 'height': 100},
        'left_sidebar': {'top': 100, 'left': 0, 'width': 200, 'height': 800},
        'main_game_area': {'top': 100, 'left': 200, 'width': 1520, 'height': 800},
        'bottom_hotbar': {'top': 900, 'left': 200, 'width': 1520, 'height': 100},
        'minimap': {'top': 100, 'left': 1720, 'width': 200, 'height': 200}
    }
    
    print("\nExample UI regions for optimization:")
    for region_name, coords in ui_regions.items():
        print(f"  {region_name}: {coords['width']}x{coords['height']} at ({coords['left']}, {coords['top']})")
    
    print("\nOptimized search example:")
    print("""
# Instead of searching entire screen (slow)
button = vision.find_on_screen('templates/menu_button.png')

# Search only in top menu area (fast)
button = vision.find_on_screen('templates/menu_button.png', 
                              region=ui_regions['top_menu'])
""")

def main():
    """Run all computer vision demos."""
    print("=== VisionController Usage Examples ===")
    print("This demonstrates how to use the computer vision capabilities")
    print("for game automation and screen interaction.")
    
    response = input("\nRun examples? (y/n): ").lower().strip()
    if response != 'y':
        print("Exiting...")
        return
    
    try:
        setup_demo_environment()
        demo_basic_vision_usage()
        demo_template_matching()
        demo_color_detection()
        demo_practical_gaming_scenarios()
        demo_region_optimization()
        
        print("\n=== VisionController Examples Completed! ===")
        print("\nNext steps to implement computer vision:")
        print("1. Take screenshots of UI elements you want to detect")
        print("2. Save them as template images in templates/ folder")
        print("3. Use vision.find_on_screen() to locate them")
        print("4. Use mouse.click() on the found coordinates")
        print("5. Use color detection for dynamic elements")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\nError occurred: {e}")

if __name__ == "__main__":
    main()