import time
import signal
import sys
from src.automation.transparent_vision import TransparentVisionController, TemplateWatcherEvent
from src.automation import HybridMouseController, KeyboardController

# Global variables for cleanup
vision = None
mouse = None
keyboard = None
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    global running, vision
    print("\n🛑 Shutting down autofish...")
    running = False
    if vision:
        try:
            vision.stop_all_template_watchers()
            print("✅ All watchers stopped")
        except Exception as e:
            print(f"Warning: Error stopping watchers: {e}")
    sys.exit(0)

# Set up signal handler for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)

def on_fish_bite(event_data):
    """Called when fish bite template is detected."""
    print(f"🎉 FISH BITE DETECTED! (Bite #{event_data['trigger_count']})")
    print(f"  Template: {event_data['template_path']}")
    print(f"  Position: {event_data['match']['position']}")
    print(f"  Confidence: {event_data['match']['confidence']:.3f}")
    print(f"  Timestamp: {time.strftime('%H:%M:%S', time.localtime(event_data['timestamp']))}")
    
    try:
        # Use the match position to click
        center = event_data['match']['center']
        success = mouse.click(*center, method="winapi")
        if success:
            print("✅ Hook set successfully!")
        else:
            print("❌ Failed to set hook")
    except Exception as e:
        print(f"❌ Error setting hook: {e}")

def on_fish_caught(event_data):
    """Called when fish caught template is detected."""
    print(f"🐟 FISH CAUGHT! (Catch #{event_data['trigger_count']})")
    print(f"  Template: {event_data['template_path']}")
    print(f"  Confidence: {event_data['match']['confidence']:.3f}")
    
    try:
        # Release mouse button or perform catch actions
        mouse.mouse_up(button="left")
        print("✅ Released reel")
    except Exception as e:
        print(f"❌ Error releasing reel: {e}")

def main():
    """Main autofish function with template watchers."""
    global vision, mouse, keyboard, running
    
    # Initialize controllers with transparency support
    print("🎣 Initializing Enhanced Autofish System...")
    vision = TransparentVisionController(match_threshold=0.8)
    mouse = HybridMouseController()
    keyboard = KeyboardController(pause_duration=0.3)
    
    # Example template paths (user should provide actual templates)
    templates = {
        'fish_bite': 'templates/fish_bite.png',
        'fish_caught': 'templates/fish_caught.png'
    }
    
    print(f"\n📂 Template Setup:")
    available_templates = {}
    
    for name, path in templates.items():
        try:
            # Check if template exists and get transparency info
            info = vision.get_transparency_info(path)
            if 'error' not in info:
                available_templates[name] = path
                print(f"  ✅ {name}: {path}")
                if info.get('has_transparency'):
                    print(f"    🔍 Transparency: {info.get('transparency_ratio', 0):.1%}")
            else:
                print(f"  ❌ {name}: {path} (not found)")
        except Exception as e:
            print(f"  ❌ {name}: {path} (error: {e})")
    
    if not available_templates:
        print("\n❌ No template files found. Please provide template images.")
        print("Create these files with screenshots of your game:")
        for name, path in templates.items():
            print(f"  {name}: {path}")
        return
    
    # Prompt user to prepare for autofishing
    print("\nPlease place your cursor over the game window, DO NOT CLICK INTO THE GAME!")
    print("Press Enter when ready...")
    input()
    
    # Click into game
    cur_pos = mouse.get_position()
    print("🖱️ Clicking into game window...")
    success = (
        mouse.click(cur_pos[0], cur_pos[1], method="winapi") or
        mouse.click(cur_pos[0], cur_pos[1], method="pyautogui")
    )
    
    if success:
        print("✅ Successfully clicked into game")
    else:
        print("⚠️ Click may have failed - continuing anyway")
    
    time.sleep(1.0)
    
    # Set up template watchers
    print("\n🔄 Setting up template watchers...")
    
    try:
        if 'fish_bite' in available_templates:
            vision.watch_template_found(
                name="bite_detector",
                template_path=available_templates['fish_bite'],
                callback=on_fish_bite,
                threshold=0.8,
                use_transparency=True,
                check_interval=0.1,  # Check 10 times per second
                cooldown=2.0,        # Minimum 2 seconds between bites
                trigger_once=False,  # Keep triggering
                auto_start=True      # Start immediately
            )
            print("  ✅ Fish bite detector configured")
        
        if 'fish_caught' in available_templates:
            vision.watch_template_found(
                name="catch_detector",
                template_path=available_templates['fish_caught'],
                callback=on_fish_caught,
                threshold=0.8,
                use_transparency=True,
                check_interval=0.2,  # Check 5 times per second
                cooldown=3.0,        # Minimum 3 seconds between catches
                trigger_once=False,
                auto_start=True
            )
            print("  ✅ Fish catch detector configured")
        
        print("✅ Template watchers configured and started!")
        
    except Exception as e:
        print(f"❌ Failed to set up template watchers: {e}")
        return
    
    # Main monitoring loop
    print("\n🤖 Enhanced Autofish is now running!")
    print("  - Using template watchers with transparency support")
    print("  - Templates will trigger automatically when detected")
    print("  - Press Ctrl+C to stop")
    
    start_time = time.time()
    last_status_time = start_time
    
    try:
        while running:
            current_time = time.time()
            
            # Show status every 30 seconds
            if current_time - last_status_time >= 30.0:
                elapsed = current_time - start_time
                print(f"\n📊 Status Update (Running {elapsed:.0f}s):")
                
                # Get watcher status
                try:
                    status = vision.get_template_watcher_status()
                    for name, info in status.items():
                        triggers = info.get('trigger_count', 0)
                        present = info.get('template_present', False)
                        running_status = '🟢 Running' if info.get('running', False) else '🔴 Stopped'
                        template_status = '👁️ Visible' if present else '👻 Hidden'
                        print(f"  {running_status} {name}: {triggers} triggers ({template_status})")
                except Exception as e:
                    print(f"  Status check failed: {e}")
                
                last_status_time = current_time
            
            # Sleep briefly to prevent high CPU usage
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        # This will be handled by the signal handler
        pass
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        if vision:
            try:
                vision.stop_all_template_watchers()
                print("✅ All watchers stopped")
            except Exception as e:
                print(f"⚠️ Error stopping watchers: {e}")
        
        # Final statistics
        elapsed = time.time() - start_time
        print(f"\n📈 Session Summary:")
        print(f"  Runtime: {elapsed:.1f} seconds")
        
        try:
            status = vision.get_template_watcher_status()
            for name, info in status.items():
                triggers = info.get('trigger_count', 0)
                print(f"  {name}: {triggers} triggers")
        except Exception as e:
            print(f"  Could not get final statistics: {e}")
        
        print("👋 Enhanced autofish session ended")

if __name__ == "__main__":
    main()