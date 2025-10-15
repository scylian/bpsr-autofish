import time
import signal
import sys
from src.automation import EnhancedVisionController, HybridMouseController, KeyboardController

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
            vision.stop_all_watchers()
            print("✅ All watchers stopped")
        except Exception as e:
            print(f"Warning: Error stopping watchers: {e}")
    sys.exit(0)

# Set up signal handler for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)

def on_fish_bite(event_data):
    """Called when fish bite is detected."""
    print(f"🎉 SUCCESS! Hooked that fish! (Bite #{event_data['trigger_count']})")
    print(f"  Color detected: RGB{event_data['current_color']}")
    print(f"  Timestamp: {time.strftime('%H:%M:%S', time.localtime(event_data['timestamp']))}")
    
    try:
        # Hold down left mouse button to start reeling
        mouse.mouse_down(955, 568, button="left")
        print("🎣 Started reeling...")
    except Exception as e:
        print(f"❌ Failed to start reeling: {e}")

def on_fish_caught(event_data):
    """Called when fish is successfully caught."""
    print(f"🐟 CAUGHT THAT FISH! (Catch #{event_data['trigger_count']})")
    print(f"  Color detected: RGB{event_data['current_color']}")
    
    try:
        # Release mouse button
        mouse.mouse_up(button="left")
        print("✅ Released reel - fish caught!")
    except Exception as e:
        print(f"❌ Failed to release reel: {e}")

def main():
    """Main autofish function."""
    global vision, mouse, keyboard, running
    
    # Initialize controllers
    print("🎣 Initializing Autofish System...")
    vision = EnhancedVisionController(match_threshold=0.8)
    mouse = HybridMouseController()
    keyboard = KeyboardController(pause_duration=0.3)
    
    # Configuration
    bite_position = (955, 568)
    catch_position = (1084, 698)
    bite_color = (255, 75, 1)
    catch_color = (255, 241, 157)
    tolerance = 3
    
    print(f"⚙️ Configuration:")
    print(f"  Bite position: {bite_position}")
    print(f"  Catch position: {catch_position}")
    print(f"  Bite color: RGB{bite_color}")
    print(f"  Catch color: RGB{catch_color}")
    print(f"  Tolerance: {tolerance}")
    
    # Setup phase
    print("\n📍 Setup Instructions:")
    print("1. Make sure your fishing game is visible")
    print("2. Position your cursor over the game window")
    print("3. DO NOT CLICK INTO THE GAME YET!")
    print("\nPress Enter when ready...")
    input()
    
    # Click into game to activate it
    print("🖱️ Clicking into game window...")
    cur_pos = mouse.get_position()
    
    # Try multiple click methods for game compatibility
    click_success = (
        mouse.click(cur_pos[0], cur_pos[1], method="winapi") or
        mouse.click(cur_pos[0], cur_pos[1], method="pyautogui") or
        mouse.click(cur_pos[0], cur_pos[1], method="auto")
    )
    
    if click_success:
        print("✅ Successfully clicked into game")
    else:
        print("⚠️ Click may have failed - continuing anyway")
    
    time.sleep(1.0)  # Let game register the click
    
    # Get current pixel colors for reference
    current_bite_color = vision.get_pixel_color(*bite_position)
    current_catch_color = vision.get_pixel_color(*catch_position)
    
    print(f"\n🔍 Current pixel colors:")
    print(f"  Bite position RGB{current_bite_color}")
    print(f"  Catch position RGB{current_catch_color}")
    
    # Set up persistent watchers
    print("\n🔄 Setting up pixel watchers...")
    
    try:
        # Watch for fish bites
        vision.watch_pixel_color(
            name="bite_detector",
            x=bite_position[0], y=bite_position[1],
            target_color=bite_color,
            callback=on_fish_bite,
            tolerance=tolerance,
            check_interval=0.05,  # Check 20 times per second
            cooldown=3.0,         # Minimum 3 seconds between bites
            trigger_once=False,   # Keep triggering for multiple fish
            auto_start=True       # Start immediately
        )
        
        # Watch for successful catches
        vision.watch_pixel_color(
            name="catch_detector",
            x=catch_position[0], y=catch_position[1],
            target_color=catch_color,
            callback=on_fish_caught,
            tolerance=tolerance,
            check_interval=0.1,   # Check 10 times per second
            cooldown=5.0,         # Minimum 5 seconds between catches
            trigger_once=False,   # Keep triggering for multiple catches
            auto_start=True       # Start immediately
        )
        
        print("✅ Pixel watchers configured and started!")
        
    except Exception as e:
        print(f"❌ Failed to set up watchers: {e}")
        return
    
    # Main monitoring loop
    print("\n🤖 Autofish is now running!")
    print("  - Monitoring for fish bites and catches")
    print("  - Press Ctrl+C to stop")
    print("  - Status updates every 30 seconds")
    
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
                    status = vision.get_watcher_status()
                    for name, info in status.items():
                        triggers = info.get('trigger_count', 0)
                        running_status = '🟢 Running' if info.get('running', False) else '🔴 Stopped'
                        print(f"  {running_status} {name}: {triggers} triggers")
                except Exception as e:
                    print(f"  Status check failed: {e}")
                
                last_status_time = current_time
            
            # Sleep briefly to prevent high CPU usage
            time.sleep(0.5)
            
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
                vision.stop_all_watchers()
                print("✅ All watchers stopped")
            except Exception as e:
                print(f"⚠️ Error stopping watchers: {e}")
        
        # Final statistics
        elapsed = time.time() - start_time
        print(f"\n📈 Session Summary:")
        print(f"  Runtime: {elapsed:.1f} seconds")
        
        try:
            status = vision.get_watcher_status()
            total_bites = status.get('bite_detector', {}).get('trigger_count', 0)
            total_catches = status.get('catch_detector', {}).get('trigger_count', 0)
            
            print(f"  Fish bites: {total_bites}")
            print(f"  Fish caught: {total_catches}")
            
            if total_bites > 0:
                success_rate = (total_catches / total_bites) * 100
                print(f"  Success rate: {success_rate:.1f}%")
            
            if elapsed > 0:
                bites_per_minute = (total_bites / elapsed) * 60
                print(f"  Bites per minute: {bites_per_minute:.1f}")
                
        except Exception as e:
            print(f"  Could not calculate statistics: {e}")
        
        print("👋 Autofish session ended")

if __name__ == "__main__":
    main()