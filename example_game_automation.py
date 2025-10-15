"""
Comprehensive example using both enhanced mouse and keyboard controllers
for game automation where standard PyAutoGUI doesn't work.
"""

from src.automation import HybridMouseController, HybridKeyboardController, VisionController
import time

def fishing_automation_enhanced():
    """Complete fishing automation using enhanced input methods."""
    print("=== Enhanced Fishing Automation ===")
    print("Using Windows API input methods for maximum game compatibility")
    
    # Initialize enhanced controllers
    mouse = HybridMouseController()
    keyboard = HybridKeyboardController()
    vision = VisionController()
    
    print("\\n🎣 Setup Instructions:")
    print("1. Position your character at a fishing spot")
    print("2. Have your fishing rod ready")
    print("3. Position this script and the game so you can see both")
    
    input("\\nPress Enter when ready...")
    
    # Get fishing bobber position
    print("\\n📍 Bobber Position Setup:")
    print("Cast your line manually, then position your mouse over the bobber")
    input("Press Enter when mouse is over the bobber...")
    
    bobber_pos = mouse.get_position()
    normal_color = vision.get_pixel_color(*bobber_pos)
    
    print(f"✓ Bobber position: {bobber_pos}")
    print(f"✓ Normal bobber color: RGB{normal_color}")
    
    # Configuration
    bite_color = (255, 100, 0)  # Orange/red for fish bite
    tolerance = 30
    cast_key = '1'  # Key to cast fishing line
    hook_key = 'space'  # Key to set hook
    
    print(f"\\n⚙️ Configuration:")
    print(f"  Cast key: {cast_key}")
    print(f"  Hook key: {hook_key}")
    print(f"  Bite color: RGB{bite_color}")
    print(f"  Tolerance: {tolerance}")
    
    if input("\\nStart automated fishing? (y/n): ").lower().strip() != 'y':
        return
    
    print("\\n🤖 Starting enhanced fishing automation...")
    print("Using Windows API input - should work even if cursor is hidden!")
    print("Press Ctrl+C to stop")
    
    fish_caught = 0
    attempts = 0
    
    try:
        while True:
            attempts += 1
            print(f"\\n--- Attempt #{attempts} ---")
            
            # Cast the line using enhanced keyboard
            print("🎣 Casting line...")
            success = (
                keyboard.press_key(cast_key, method='winapi') or
                keyboard.press_key(cast_key, method='auto')
            )
            
            if not success:
                print("❌ Failed to cast - trying all keyboard methods")
                keyboard.press_key(cast_key, method='game')
            
            # Wait for cast animation
            time.sleep(2.0)
            
            # Wait for fish bite
            print("🔍 Monitoring for fish bite...")
            bite_detected = vision.wait_for_pixel_color(
                *bobber_pos, bite_color,
                tolerance=tolerance,
                timeout=25.0,
                check_interval=0.05
            )
            
            if bite_detected:
                print("🎣 FISH BITE DETECTED!")
                
                # Set hook using enhanced input methods
                print("⚡ Setting hook with enhanced input...")
                
                # Try multiple input methods for reliability
                hook_set = False
                
                # Method 1: Enhanced keyboard (Windows API)
                if keyboard.press_key(hook_key, method='winapi'):
                    hook_set = True
                    print("✅ Hook set via Windows API keyboard")
                
                # Method 2: Enhanced mouse click as backup
                elif mouse.click(*bobber_pos, method='winapi'):
                    hook_set = True  
                    print("✅ Hook set via Windows API mouse click")
                
                # Method 3: Hybrid methods (tries everything)
                elif (keyboard.press_key(hook_key, method='auto') or 
                      mouse.click(*bobber_pos, method='auto')):
                    hook_set = True
                    print("✅ Hook set via hybrid methods")
                
                if hook_set:
                    fish_caught += 1
                    print(f"🐟 Fish #{fish_caught} caught!")
                else:
                    print("❌ Failed to set hook with all methods")
                
                # Wait for catch sequence to complete
                print("⏳ Waiting for catch to complete...")
                time.sleep(3.0)
                
            else:
                print("⏰ No bite detected - recasting")
            
            # Brief pause before next attempt
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print(f"\\n\\n🛑 Fishing automation stopped!")
        print(f"📊 Results:")
        print(f"  Attempts: {attempts}")
        print(f"  Fish caught: {fish_caught}")
        print(f"  Success rate: {(fish_caught/attempts*100):.1f}%" if attempts > 0 else "N/A")

def movement_automation_demo():
    """Demonstrate character movement automation with enhanced input."""
    print("\\n=== Movement Automation Demo ===")
    print("This will demonstrate WASD movement using enhanced keyboard input")
    
    keyboard = HybridKeyboardController()
    
    print("\\n🎮 Make sure your game character can move with WASD keys")
    print("The character should be in a safe area for movement testing")
    
    if input("Ready to test movement? (y/n): ").lower().strip() != 'y':
        return
    
    movements = [
        ("Forward", 'w', 2.0),
        ("Left", 'a', 1.5), 
        ("Backward", 's', 2.0),
        ("Right", 'd', 1.5),
        ("Jump", 'space', 0.5),
    ]
    
    print("\\n🏃 Testing movement commands...")
    
    for direction, key, duration in movements:
        print(f"Moving {direction} ({key}) for {duration}s...")
        
        # Use enhanced keyboard input
        success = keyboard.hold_key(key, duration, method='auto')
        
        if success:
            print(f"✅ {direction} movement successful")
        else:
            print(f"❌ {direction} movement failed - trying alternative methods")
            # Try direct API methods
            if keyboard.key_down(key, method='winapi'):
                time.sleep(duration)
                keyboard.key_up(key, method='winapi')
                print(f"✅ {direction} movement via Windows API")
        
        time.sleep(0.5)  # Brief pause between movements
    
    print("\\n✓ Movement test completed!")

def combat_automation_demo():
    """Demonstrate combat automation with enhanced input."""
    print("\\n=== Combat Automation Demo ===")
    print("This will demonstrate combat key sequences using enhanced input")
    
    keyboard = HybridKeyboardController()
    mouse = HybridMouseController()
    
    print("\\n⚔️ Combat Key Testing:")
    print("Make sure you're in a safe area or training dummy")
    
    if input("Ready to test combat keys? (y/n): ").lower().strip() != 'y':
        return
    
    combat_actions = [
        ("Basic Attack", 'space', 1),
        ("Skill 1", '1', 1),
        ("Skill 2", '2', 1), 
        ("Skill 3", '3', 1),
        ("Block/Defend", 'shift', 1),
        ("Dodge/Roll", 'ctrl', 1),
    ]
    
    print("\\n🗡️ Testing combat actions...")
    
    for action, key, presses in combat_actions:
        print(f"Executing {action} ({key})...")
        
        # Use enhanced keyboard with multiple fallback methods
        success = (
            keyboard.press_key(key, presses, method='winapi') or
            keyboard.press_key(key, presses, method='scancode') or
            keyboard.press_key(key, presses, method='auto')
        )
        
        if success:
            print(f"✅ {action} executed successfully")
        else:
            print(f"❌ {action} failed with all methods")
        
        time.sleep(0.8)  # Cooldown between actions
    
    # Test click-based combat
    print("\\n🖱️ Testing enhanced mouse combat...")
    print("Position mouse over a target and press Enter...")
    input()
    
    target_pos = mouse.get_position()
    print(f"Target position: {target_pos}")
    
    # Rapid clicking test
    print("Performing rapid attacks...")
    for i in range(5):
        success = (
            mouse.click(*target_pos, method='winapi') or
            mouse.click(*target_pos, method='game') or  
            mouse.click(*target_pos, method='auto')
        )
        
        if success:
            print(f"✅ Attack {i+1} successful")
        else:
            print(f"❌ Attack {i+1} failed")
        
        time.sleep(0.3)
    
    print("\\n✓ Combat test completed!")

def advanced_input_combinations():
    """Test advanced input combinations that games commonly use."""
    print("\\n=== Advanced Input Combinations ===")
    
    keyboard = HybridKeyboardController()
    mouse = HybridMouseController()
    
    combinations = [
        {
            'name': 'Ctrl+Click (Special attack)',
            'keys': ['ctrl'],
            'click': True,
            'description': 'Hold Ctrl and click for special attack'
        },
        {
            'name': 'Shift+WASD (Run movement)', 
            'keys': ['shift', 'w'],
            'duration': 2.0,
            'description': 'Hold Shift+W to run forward'
        },
        {
            'name': 'Alt+1-4 (Quick spells)',
            'keys': ['alt', '1'],
            'description': 'Alt+number for quick spell casting'
        },
        {
            'name': 'Ctrl+Space (Special jump)',
            'keys': ['ctrl', 'space'],
            'description': 'Ctrl+Space for power jump or special ability'
        }
    ]
    
    print("\\n🔥 Testing advanced key combinations...")
    
    for combo in combinations:
        print(f"\\n{combo['name']}: {combo['description']}")
        
        if input("Test this combination? (y/n): ").lower().strip() == 'y':
            if combo.get('click'):
                # Hold keys and click
                print("Position mouse for click, then press Enter...")
                input()
                click_pos = mouse.get_position()
                
                # Hold keys down
                for key in combo['keys']:
                    keyboard.key_down(key, method='winapi')
                
                time.sleep(0.1)
                
                # Click while holding
                mouse.click(*click_pos, method='winapi')
                
                # Release keys
                for key in reversed(combo['keys']):
                    keyboard.key_up(key, method='winapi')
                
                print("✅ Combination executed")
                
            elif combo.get('duration'):
                # Hold key combination for duration
                print(f"Holding combination for {combo['duration']}s...")
                
                # Press all keys down
                for key in combo['keys']:
                    keyboard.key_down(key, method='winapi')
                
                time.sleep(combo['duration'])
                
                # Release all keys
                for key in reversed(combo['keys']):
                    keyboard.key_up(key, method='winapi')
                
                print("✅ Combination held and released")
                
            else:
                # Simple key combination
                success = keyboard.key_combination(combo['keys'], method='winapi')
                print(f"{'✅' if success else '❌'} Combination {'executed' if success else 'failed'}")
            
            time.sleep(1.0)

def input_diagnostics():
    """Run comprehensive input diagnostics."""
    print("\\n=== Input Diagnostics ===")
    
    mouse = HybridMouseController()
    keyboard = HybridKeyboardController()
    
    # Window information
    window_info = mouse.get_window_info()
    print(f"Current Window: {window_info.get('title', 'Unknown')}")
    print(f"Window Class: {window_info.get('class_name', 'Unknown')}")
    print(f"Window Size: {window_info.get('width', 0)}x{window_info.get('height', 0)}")
    
    # Cursor status
    import ctypes
    cursor_info = ctypes.wintypes.CURSORINFO()
    cursor_info.cbSize = ctypes.sizeof(cursor_info)
    
    if ctypes.windll.user32.GetCursorInfo(ctypes.byref(cursor_info)):
        cursor_visible = cursor_info.flags == 1
        print(f"Cursor Visible: {'Yes' if cursor_visible else 'No'}")
        
        if not cursor_visible:
            print("⚠️ Cursor hidden - enhanced input methods recommended")
    
    # Test basic input
    print("\\n🧪 Quick Input Test:")
    print("Testing basic key press...")
    
    success = keyboard.press_key('f1', method='auto')
    print(f"F1 key: {'✅ Success' if success else '❌ Failed'}")
    
    print("Testing mouse position detection...")
    pos = mouse.get_position()
    print(f"Mouse position: {pos} ✅")
    
    # Recommendations
    title = window_info.get('title', '').lower()
    if any(keyword in title for keyword in ['unity', 'unreal', 'game']):
        print("\\n💡 Game Detected - Recommendations:")
        print("  - Use method='winapi' for direct API input")
        print("  - Use method='auto' for automatic fallback")
        print("  - Enhanced controllers should work better than PyAutoGUI")

def main():
    """Main menu for game automation examples."""
    print("Enhanced Game Automation Examples")
    print("=================================")
    print("Using Windows API for games where PyAutoGUI doesn't work")
    
    while True:
        print("\\nChoose an example:")
        print("1. Enhanced Fishing Automation")
        print("2. Movement Automation Demo") 
        print("3. Combat Automation Demo")
        print("4. Advanced Input Combinations")
        print("5. Input Diagnostics")
        print("6. Exit")
        
        choice = input("\\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            fishing_automation_enhanced()
        elif choice == "2":
            movement_automation_demo()
        elif choice == "3":
            combat_automation_demo()
        elif choice == "4":
            advanced_input_combinations()
        elif choice == "5":
            input_diagnostics()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()