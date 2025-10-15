"""
Simple example showing how to use the enhanced mouse controllers for games.
This demonstrates different approaches when standard PyAutoGUI doesn't work.
"""

from src.automation import HybridMouseController, GameMouseController, VisionController
import time

def basic_game_mouse_example():
    """Basic example of using game mouse controllers."""
    print("=== Enhanced Game Mouse Example ===")
    
    # Initialize the hybrid controller (tries multiple methods automatically)
    mouse = HybridMouseController()
    
    # Get current window information
    window_info = mouse.get_window_info()
    print(f"Current window: {window_info.get('title', 'Unknown')}")
    print(f"Window size: {window_info.get('width', 0)}x{window_info.get('height', 0)}")
    
    # Method 1: Let the system automatically choose the best method
    print("\\n1. Auto-detection click (tries game methods first)")
    x, y = mouse.get_position()
    print(f"Current mouse position: ({x}, {y})")
    
    input("Position mouse where you want to click, then press Enter...")
    test_x, test_y = mouse.get_position()
    
    # This will try Windows API first, then fall back to PyAutoGUI
    success = mouse.click(test_x, test_y, method='auto')
    print(f"Auto click: {'Success' if success else 'Failed'}")
    
    # Method 2: Force Windows API method (best for games)
    print("\\n2. Windows API click (direct system call)")
    input("Position mouse again, then press Enter...")
    test_x, test_y = mouse.get_position()
    
    success = mouse.click(test_x, test_y, method='winapi')
    print(f"WinAPI click: {'Success' if success else 'Failed'}")
    
    # Method 3: Window message method (works even without focus sometimes)
    print("\\n3. Window message click (direct to game window)")
    input("Position mouse again, then press Enter...")
    test_x, test_y = mouse.get_position()
    
    success = mouse.click(test_x, test_y, method='game')
    print(f"Game click: {'Success' if success else 'Failed'}")

def fishing_with_enhanced_mouse():
    """Fishing automation example using enhanced mouse input."""
    print("\\n=== Fishing with Enhanced Mouse ===")
    
    # Use the hybrid controller for maximum compatibility
    mouse = HybridMouseController()
    vision = VisionController()
    
    print("This example shows fishing automation using enhanced mouse input.")
    print("Position your mouse over the fishing bobber...")
    input("Press Enter when positioned...")
    
    bobber_pos = mouse.get_position()
    normal_color = vision.get_pixel_color(*bobber_pos)
    
    print(f"Bobber position: {bobber_pos}")
    print(f"Normal bobber color: RGB{normal_color}")
    
    # Define the fish bite color (typically red/orange)
    bite_color = (255, 100, 0)  # Orange
    tolerance = 30
    
    print(f"\\nWaiting for fish bite (color change to {bite_color})...")
    print("The system will use enhanced mouse input to set the hook.")
    print("Press Ctrl+C to stop")
    
    try:
        fish_count = 0
        while True:
            print(f"\\n--- Attempt {fish_count + 1} ---")
            print("Monitoring bobber...")
            
            # Wait for fish bite using pixel waiting
            bite_detected = vision.wait_for_pixel_color(
                *bobber_pos, bite_color,
                tolerance=tolerance,
                timeout=30.0,
                check_interval=0.05
            )
            
            if bite_detected:
                print("🎣 FISH BITE! Setting hook...")
                
                # Use enhanced mouse input to click (set hook)
                # Try multiple methods for maximum reliability
                success = (
                    mouse.click(*bobber_pos, method='winapi') or
                    mouse.click(*bobber_pos, method='game') or  
                    mouse.click(*bobber_pos, method='pyautogui')
                )
                
                if success:
                    print("✅ Hook set successfully!")
                    fish_count += 1
                else:
                    print("❌ Failed to set hook - trying all methods")
                    # Emergency fallback - try direct API
                    mouse.game_mouse.click_direct_api(*bobber_pos)
                
                # Wait for the action to complete
                time.sleep(3.0)
                
            else:
                print("⏰ No bite detected in 30 seconds")
                
    except KeyboardInterrupt:
        print(f"\\n🎣 Fishing stopped. Fish caught: {fish_count}")

def diagnose_mouse_issues():
    """Diagnose mouse input issues with your game."""
    print("\\n=== Mouse Input Diagnosis ===")
    
    mouse = HybridMouseController()
    
    # Check cursor visibility
    import ctypes
    cursor_info = ctypes.wintypes.CURSORINFO()
    cursor_info.cbSize = ctypes.sizeof(cursor_info)
    
    if ctypes.windll.user32.GetCursorInfo(ctypes.byref(cursor_info)):
        visible = cursor_info.flags == 1
        print(f"Cursor visible: {'Yes' if visible else 'No'}")
        
        if not visible:
            print("⚠️  Cursor is hidden - this typically means:")
            print("   - Game is in fullscreen exclusive mode")
            print("   - Game captures mouse input directly")
            print("   - Standard PyAutoGUI clicks may not work")
            print("   - Enhanced Windows API methods should work")
    
    # Check window information
    window_info = mouse.get_window_info()
    title = window_info.get('title', '').lower()
    
    # Game detection
    game_indicators = ['unity', 'unreal', 'game', 'dx', 'opengl', 'vulkan']
    is_game = any(indicator in title for indicator in game_indicators)
    
    if is_game:
        print(f"🎮 Game detected: {window_info.get('title', 'Unknown')}")
        print("Recommended mouse methods (in order):")
        print("   1. method='winapi' - Direct Windows API")
        print("   2. method='game' - Window message injection")
        print("   3. method='auto' - Try all methods automatically")
    
    # Test button state detection
    print("\\nTesting button state detection...")
    print("Hold down mouse buttons to test detection (5 seconds)")
    
    start_time = time.time()
    while time.time() - start_time < 5.0:
        left = mouse.is_button_pressed('left')
        right = mouse.is_button_pressed('right')
        middle = mouse.is_button_pressed('middle')
        
        buttons = []
        if left: buttons.append("LEFT")
        if right: buttons.append("RIGHT") 
        if middle: buttons.append("MIDDLE")
        
        status = " + ".join(buttons) if buttons else "None"
        print(f"\\rButtons: {status}     ", end="", flush=True)
        time.sleep(0.1)
    
    print("\\n✅ Button detection test complete")

def main():
    """Main function with menu."""
    print("Enhanced Mouse Controller for Games")
    print("===================================")
    
    while True:
        print("\\nChoose an example:")
        print("1. Basic game mouse clicking")
        print("2. Fishing automation with enhanced mouse")
        print("3. Diagnose mouse input issues")
        print("4. Exit")
        
        choice = input("\\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            basic_game_mouse_example()
        elif choice == "2":
            fishing_with_enhanced_mouse()
        elif choice == "3":
            diagnose_mouse_issues()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()