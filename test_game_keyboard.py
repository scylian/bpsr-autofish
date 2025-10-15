"""
Test script to diagnose keyboard input issues with games.
This helps identify the best input method for your specific game.
"""

import time
import sys
import logging
from src.automation.game_keyboard import HybridKeyboardController, GameKeyboardController
from src.automation.keyboard import KeyboardController

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_keyboard_methods():
    """Test different keyboard input methods."""
    print("=== Game Keyboard Input Diagnostics ===")
    print("This will test different methods of keyboard input for games.\\n")
    
    # Initialize controllers
    hybrid_keyboard = HybridKeyboardController()
    game_keyboard = GameKeyboardController()
    pyautogui_keyboard = KeyboardController()
    
    print("Available keys:", ', '.join(hybrid_keyboard.get_available_keys()[:20]), "...")
    
    # Interactive testing
    while True:
        print(f"\\n🎯 Keyboard Input Test Menu:")
        print("1. Test PyAutoGUI key press (standard method)")
        print("2. Test Windows API key press")
        print("3. Test Scan code key press")
        print("4. Test Window message key press")
        print("5. Test Hybrid key press (tries multiple methods)")
        print("6. Test key combinations (Ctrl+C, Alt+Tab, etc.)")
        print("7. Test text typing")
        print("8. Test key state detection")
        print("9. Test key holding")
        print("10. Show available keys")
        print("11. Exit")
        
        choice = input(f"\\nChoose test (1-11): ").strip()
        
        if choice == "11":
            break
        
        try:
            if choice == "1":
                test_pyautogui_keys(pyautogui_keyboard)
            elif choice == "2":
                test_winapi_keys(game_keyboard)
            elif choice == "3":
                test_scancode_keys(game_keyboard)
            elif choice == "4":
                test_message_keys(game_keyboard)
            elif choice == "5":
                test_hybrid_keys(hybrid_keyboard)
            elif choice == "6":
                test_key_combinations(hybrid_keyboard)
            elif choice == "7":
                test_text_typing(hybrid_keyboard)
            elif choice == "8":
                test_key_states(hybrid_keyboard)
            elif choice == "9":
                test_key_holding(hybrid_keyboard)
            elif choice == "10":
                show_available_keys(hybrid_keyboard)
            else:
                print("❌ Invalid choice")
                
        except KeyboardInterrupt:
            print("\\n⚠️ Test interrupted")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_pyautogui_keys(keyboard):
    """Test standard PyAutoGUI key pressing."""
    print("\\n=== PyAutoGUI Key Test ===")
    
    key = input("Enter key to test (e.g., 'space', 'a', 'enter'): ").strip().lower()
    if not key:
        print("❌ No key entered")
        return
    
    print(f"Testing PyAutoGUI key press: {key}")
    print("Watch your active application for the key press...")
    
    success = keyboard.press_key(key)
    print(f"PyAutoGUI key press {'succeeded' if success else 'failed'}")

def test_winapi_keys(keyboard):
    """Test Windows API key pressing."""
    print("\\n=== Windows API Key Test ===")
    
    key = input("Enter key to test: ").strip().lower()
    if not key:
        print("❌ No key entered")
        return
    
    print(f"Testing Windows API key press: {key}")
    print("Watch your active application for the key press...")
    
    success = keyboard.press_key_api(key)
    print(f"Windows API key press {'succeeded' if success else 'failed'}")

def test_scancode_keys(keyboard):
    """Test scan code key pressing."""
    print("\\n=== Scan Code Key Test ===")
    
    key = input("Enter key to test: ").strip().lower()
    if not key:
        print("❌ No key entered")
        return
    
    print(f"Testing scan code key press: {key}")
    print("Watch your active application for the key press...")
    
    success = keyboard.press_key_scancode(key)
    print(f"Scan code key press {'succeeded' if success else 'failed'}")

def test_message_keys(keyboard):
    """Test window message key pressing."""
    print("\\n=== Window Message Key Test ===")
    
    hwnd = keyboard.get_foreground_window()
    if not hwnd:
        print("❌ No foreground window found")
        return
    
    key = input("Enter key to test: ").strip().lower()
    if not key:
        print("❌ No key entered")
        return
    
    print(f"Testing window message key press: {key}")
    print("Watch your active application for the key press...")
    
    success = keyboard.send_window_message(hwnd, key)
    print(f"Window message key press {'succeeded' if success else 'failed'}")

def test_hybrid_keys(keyboard):
    """Test hybrid key pressing that tries multiple methods."""
    print("\\n=== Hybrid Key Test ===")
    
    key = input("Enter key to test: ").strip().lower()
    if not key:
        print("❌ No key entered")
        return
    
    print(f"Testing hybrid key press: {key}")
    print("This will try multiple methods automatically...")
    
    success = keyboard.press_key(key, method='auto')
    print(f"Hybrid key press {'succeeded' if success else 'failed'}")

def test_key_combinations(keyboard):
    """Test key combinations like Ctrl+C, Alt+Tab, etc."""
    print("\\n=== Key Combination Test ===")
    
    print("Common combinations:")
    print("1. Ctrl+C (copy)")
    print("2. Ctrl+V (paste)")
    print("3. Alt+Tab (switch window)")
    print("4. Win+R (run dialog)")
    print("5. Custom combination")
    
    choice = input("Choose combination (1-5): ").strip()
    
    combinations = {
        '1': ['ctrl', 'c'],
        '2': ['ctrl', 'v'],
        '3': ['alt', 'tab'],
        '4': ['win', 'r'],
    }
    
    if choice in combinations:
        keys = combinations[choice]
    elif choice == '5':
        keys_input = input("Enter keys separated by spaces (e.g., 'ctrl alt delete'): ")
        keys = [k.strip().lower() for k in keys_input.split()]
        if not keys:
            print("❌ No keys entered")
            return
    else:
        print("❌ Invalid choice")
        return
    
    print(f"Testing key combination: {'+'.join(keys)}")
    
    # Test with different methods
    methods = ['auto', 'winapi', 'pyautogui']
    for method in methods:
        print(f"Trying {method} method...")
        success = keyboard.key_combination(keys, method=method)
        print(f"  {method}: {'Success' if success else 'Failed'}")
        time.sleep(0.5)
        if success:
            break

def test_text_typing(keyboard):
    """Test text typing."""
    print("\\n=== Text Typing Test ===")
    
    print("⚠️ Make sure your cursor is in a text field!")
    text = input("Enter text to type: ")
    if not text:
        print("❌ No text entered")
        return
    
    print(f"Typing text: '{text}'")
    
    # Test with different methods
    methods = ['auto', 'winapi', 'pyautogui']
    for method in methods:
        print(f"Trying {method} method...")
        success = keyboard.type_text(text, method=method)
        print(f"  {method}: {'Success' if success else 'Failed'}")
        time.sleep(1.0)
        if success:
            break

def test_key_states(keyboard):
    """Test key state detection."""
    print("\\n=== Key State Detection Test ===")
    print("Hold down different keys and watch the status...")
    print("Press Ctrl+C to stop")
    
    test_keys = ['a', 'w', 's', 'd', 'space', 'ctrl', 'shift', 'alt']
    
    try:
        while True:
            pressed_keys = []
            for key in test_keys:
                if keyboard.is_key_pressed(key):
                    pressed_keys.append(key.upper())
            
            status = " + ".join(pressed_keys) if pressed_keys else "None"
            print(f"\\rKeys pressed: {status}     ", end="", flush=True)
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\\n✓ Key state test finished")

def test_key_holding(keyboard):
    """Test key holding functionality."""
    print("\\n=== Key Holding Test ===")
    
    key = input("Enter key to hold (e.g., 'w', 'space'): ").strip().lower()
    if not key:
        print("❌ No key entered")
        return
    
    try:
        duration = float(input("Enter hold duration in seconds (default 2): ") or "2")
    except ValueError:
        duration = 2.0
    
    print(f"Holding key '{key}' for {duration} seconds...")
    print("Watch your active application - the key should be held down")
    
    # Test with different methods
    methods = ['auto', 'winapi']
    for method in methods:
        print(f"Testing {method} method...")
        
        # Hold key down
        if keyboard.key_down(key, method=method):
            print(f"Key '{key}' pressed down")
            time.sleep(duration)
            
            # Release key
            if keyboard.key_up(key, method=method):
                print(f"Key '{key}' released")
                print(f"{method} method: Success")
                break
            else:
                print(f"{method} method: Failed to release")
        else:
            print(f"{method} method: Failed to press down")
        
        time.sleep(0.5)

def show_available_keys(keyboard):
    """Show available keys."""
    print("\\n=== Available Keys ===")
    
    keys = keyboard.get_available_keys()
    
    # Group keys by category
    categories = {
        'Letters': [k for k in keys if len(k) == 1 and k.isalpha()],
        'Numbers': [k for k in keys if len(k) == 1 and k.isdigit()],
        'Function Keys': [k for k in keys if k.startswith('f') and k[1:].isdigit()],
        'Arrow Keys': [k for k in keys if k in ['up', 'down', 'left', 'right']],
        'Modifier Keys': [k for k in keys if k in ['ctrl', 'shift', 'alt', 'win', 'cmd']],
        'Special Keys': [k for k in keys if k in ['space', 'enter', 'tab', 'escape', 'backspace', 'delete']],
    }
    
    for category, category_keys in categories.items():
        if category_keys:
            print(f"{category}: {', '.join(sorted(category_keys))}")
    
    print(f"\\nTotal keys available: {len(keys)}")

def run_gaming_scenarios():
    """Run common gaming scenarios."""
    print("\\n=== Gaming Scenarios Test ===")
    
    keyboard = HybridKeyboardController()
    
    scenarios = [
        ("WASD Movement", ['w', 'a', 's', 'd']),
        ("Jump (Space)", ['space']),
        ("Interact (E)", ['e']),
        ("Inventory (I)", ['i']),
        ("Menu (Escape)", ['escape']),
        ("Chat (Enter)", ['enter']),
        ("Quick Save (F5)", ['f5']),
        ("Screenshot (F12)", ['f12']),
    ]
    
    print("Common gaming keys test:")
    for name, keys in scenarios:
        print(f"\\nTesting {name}...")
        for key in keys:
            success = keyboard.press_key(key, method='auto')
            print(f"  {key}: {'✓' if success else '✗'}")
        time.sleep(0.5)

def main():
    """Main function."""
    print("This script will help diagnose keyboard input issues with games.")
    print("Make sure your game or target application is active and in the foreground.")
    
    while True:
        print("\\nChoose test suite:")
        print("1. Full diagnostic tests")
        print("2. Gaming scenarios only")
        print("3. Exit")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            test_keyboard_methods()
        elif choice == "2":
            run_gaming_scenarios()
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice")
    
    print("\\n📝 Summary:")
    print("If PyAutoGUI doesn't work but Windows API does:")
    print("  - Use HybridKeyboardController with method='winapi' or 'auto'")
    print("  - Your game likely captures keyboard input exclusively")
    print("\\nIf scan codes work better than virtual keys:")
    print("  - Use method='scancode' for hardware-independent input")
    print("\\nIf window messages work:")
    print("  - The game accepts direct window messages")
    print("  - This can work even when the game doesn't have focus")

if __name__ == "__main__":
    main()