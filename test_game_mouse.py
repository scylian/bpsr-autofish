"""
Test script to diagnose mouse input issues with games.
This helps identify the best input method for your specific game.
"""

import time
import sys
import logging
from src.automation.game_mouse import HybridMouseController, GameMouseController
from src.automation.mouse import MouseController

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mouse_methods():
    """Test different mouse input methods."""
    print("=== Game Mouse Input Diagnostics ===")
    print("This will test different methods of mouse input for games.\n")
    
    # Initialize controllers
    hybrid_mouse = HybridMouseController()
    game_mouse = GameMouseController()
    pyautogui_mouse = MouseController()
    
    # Get current window info
    window_info = hybrid_mouse.get_window_info()
    print("Current Window Information:")
    print(f"  Title: {window_info.get('title', 'Unknown')}")
    print(f"  Class: {window_info.get('class_name', 'Unknown')}")
    print(f"  Handle: {window_info.get('hwnd', 'Unknown')}")
    print(f"  Size: {window_info.get('width', 0)}x{window_info.get('height', 0)}")
    
    # Check if it's likely a game
    title = window_info.get('title', '').lower()
    class_name = window_info.get('class_name', '').lower()
    
    is_likely_game = any(keyword in title or keyword in class_name for keyword in [
        'game', 'unity', 'unreal', 'dx', 'opengl', 'vulkan', 'fullscreen'
    ])
    
    if is_likely_game:
        print("⚠️  This appears to be a game window - standard input may not work!")
    
    print(f"\nMouse position: {hybrid_mouse.get_position()}")
    
    # Interactive testing
    while True:
        print(f"\n🎯 Mouse Input Test Menu:")
        print("1. Test PyAutoGUI click (standard method)")
        print("2. Test Windows API direct click")
        print("3. Test Windows message click")
        print("4. Test hybrid click (tries multiple methods)")
        print("5. Test mouse button state detection")
        print("6. Position mouse and test clicking there")
        print("7. Test different click speeds")
        print("8. Show cursor visibility status")
        print("9. Exit")
        
        choice = input(f"\nChoose test (1-9): ").strip()
        
        if choice == "9":
            break
        
        try:
            if choice == "1":
                test_pyautogui_click(pyautogui_mouse)
            elif choice == "2":
                test_winapi_click(game_mouse)
            elif choice == "3":
                test_message_click(game_mouse)
            elif choice == "4":
                test_hybrid_click(hybrid_mouse)
            elif choice == "5":
                test_button_states(hybrid_mouse)
            elif choice == "6":
                test_position_and_click(hybrid_mouse)
            elif choice == "7":
                test_click_speeds(hybrid_mouse)
            elif choice == "8":
                test_cursor_visibility(hybrid_mouse)
            else:
                print("❌ Invalid choice")
                
        except KeyboardInterrupt:
            print("\\n⚠️ Test interrupted")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_pyautogui_click(mouse):
    """Test standard PyAutoGUI clicking."""
    print("\\n=== PyAutoGUI Click Test ===")
    x, y = mouse.get_position()
    print(f"Current position: ({x}, {y})")
    
    input("Position your mouse where you want to test click, then press Enter...")
    
    test_x, test_y = mouse.get_position()
    print(f"Testing click at ({test_x}, {test_y})")
    
    success = mouse.click(test_x, test_y)
    print(f"PyAutoGUI click {'succeeded' if success else 'failed'}")

def test_winapi_click(mouse):
    """Test Windows API direct clicking."""
    print("\\n=== Windows API Direct Click Test ===")
    x, y = mouse.get_position()
    print(f"Current position: ({x}, {y})")
    
    input("Position your mouse where you want to test click, then press Enter...")
    
    test_x, test_y = mouse.get_position()
    print(f"Testing direct API click at ({test_x}, {test_y})")
    
    success = mouse.click_direct_api(test_x, test_y)
    print(f"Direct API click {'succeeded' if success else 'failed'}")

def test_message_click(mouse):
    """Test Windows message clicking."""
    print("\\n=== Windows Message Click Test ===")
    x, y = mouse.get_position()
    print(f"Current position: ({x}, {y})")
    
    hwnd = mouse.get_foreground_window()
    if not hwnd:
        print("❌ No foreground window found")
        return
    
    input("Position your mouse where you want to test click, then press Enter...")
    
    test_x, test_y = mouse.get_position()
    print(f"Testing message click at ({test_x}, {test_y})")
    
    success = mouse.click_window_message(hwnd, test_x, test_y)
    print(f"Message click {'succeeded' if success else 'failed'}")

def test_hybrid_click(mouse):
    """Test hybrid clicking that tries multiple methods."""
    print("\\n=== Hybrid Click Test ===")
    x, y = mouse.get_position()
    print(f"Current position: ({x}, {y})")
    
    input("Position your mouse where you want to test click, then press Enter...")
    
    test_x, test_y = mouse.get_position()
    print(f"Testing hybrid click at ({test_x}, {test_y})")
    
    success = mouse.click(test_x, test_y, method='auto')
    print(f"Hybrid click {'succeeded' if success else 'failed'}")

def test_button_states(mouse):
    """Test mouse button state detection."""
    print("\\n=== Button State Detection Test ===")
    print("Hold down different mouse buttons and watch the status...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            left = mouse.is_button_pressed('left')
            right = mouse.is_button_pressed('right')
            middle = mouse.is_button_pressed('middle')
            
            status = []
            if left:
                status.append("LEFT")
            if right:
                status.append("RIGHT") 
            if middle:
                status.append("MIDDLE")
            
            status_str = " + ".join(status) if status else "None"
            print(f"\\rButtons pressed: {status_str}    ", end="", flush=True)
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\\n✓ Button state test finished")

def test_position_and_click(mouse):
    """Test positioning mouse and clicking there."""
    print("\\n=== Position and Click Test ===")
    
    try:
        target_x = int(input("Enter X coordinate: "))
        target_y = int(input("Enter Y coordinate: "))
    except ValueError:
        print("❌ Invalid coordinates")
        return
    
    print(f"Moving to ({target_x}, {target_y})...")
    mouse.move_to(target_x, target_y, duration=1.0)
    
    time.sleep(0.5)
    print("Clicking...")
    success = mouse.click(target_x, target_y, method='auto')
    print(f"Click {'succeeded' if success else 'failed'}")

def test_click_speeds(mouse):
    """Test different click speeds and patterns."""
    print("\\n=== Click Speed Test ===")
    x, y = mouse.get_position()
    
    input("Position mouse for rapid clicking test, then press Enter...")
    test_x, test_y = mouse.get_position()
    
    print("Testing different click patterns...")
    
    # Single click
    print("1. Single click")
    mouse.click(test_x, test_y, method='winapi')
    time.sleep(1.0)
    
    # Double click
    print("2. Double click")
    mouse.click(test_x, test_y, clicks=2, method='winapi')
    time.sleep(1.0)
    
    # Rapid clicks
    print("3. Rapid clicking (5 clicks)")
    for i in range(5):
        mouse.game_mouse.click_direct_api(test_x, test_y)
        time.sleep(0.1)
    
    print("✓ Click speed test completed")

def test_cursor_visibility(mouse):
    """Test cursor visibility and provide information."""
    print("\\n=== Cursor Visibility Test ===")
    
    import ctypes
    
    # Check cursor visibility
    cursor_info = ctypes.wintypes.CURSORINFO()
    cursor_info.cbSize = ctypes.sizeof(cursor_info)
    
    if ctypes.windll.user32.GetCursorInfo(ctypes.byref(cursor_info)):
        visible = cursor_info.flags == 1
        print(f"Cursor visible: {'Yes' if visible else 'No'}")
        print(f"Cursor position: ({cursor_info.ptScreenPos.x}, {cursor_info.ptScreenPos.y})")
    else:
        print("❌ Could not get cursor information")
    
    # Check if cursor is confined
    rect = ctypes.wintypes.RECT()
    if ctypes.windll.user32.GetClipCursor(ctypes.byref(rect)):
        if rect.left == 0 and rect.top == 0 and rect.right == 0 and rect.bottom == 0:
            print("Cursor clipping: None")
        else:
            print(f"Cursor clipped to: ({rect.left}, {rect.top}) - ({rect.right}, {rect.bottom})")
    
    # Show recommendations
    window_info = mouse.get_window_info()
    title = window_info.get('title', '').lower()
    
    print("\\n💡 Recommendations:")
    if not visible:
        print("  - Cursor is hidden - this is common in games")
        print("  - Try Windows API methods (options 2-4)")
        print("  - Window messages may work better")
    
    if 'unity' in title or 'unreal' in title:
        print("  - Unity/Unreal game detected")
        print("  - Try direct Windows API input")
    
    if 'fullscreen' in title or rect.right - rect.left == mouse.game_mouse.screen_width:
        print("  - Fullscreen application detected")
        print("  - Direct API or message injection recommended")

def main():
    """Main function."""
    print("This script will help diagnose mouse input issues with games.")
    print("Make sure your game is active and in the foreground.")
    input("Press Enter to continue...")
    
    test_mouse_methods()
    
    print("\\n📝 Summary:")
    print("If PyAutoGUI doesn't work but Windows API does:")
    print("  - Use HybridMouseController with method='winapi' or 'game'")
    print("  - Your game likely captures mouse input exclusively")
    print("\\nIf none of the methods work:")
    print("  - The game may have anti-automation protection")
    print("  - Try running as administrator")
    print("  - Check if the game blocks all input injection")

if __name__ == "__main__":
    main()