"""
Example demonstrating persistent pixel watchers for continuous monitoring.
This shows how to set up event-driven pixel monitoring that can trigger multiple times.
"""

import time
from src.automation.pixel_watcher import EnhancedVisionController
from src.automation import HybridMouseController, HybridKeyboardController

def fishing_automation_with_persistent_watchers():
    """Advanced fishing automation using persistent pixel watchers."""
    print("=== Fishing Automation with Persistent Watchers ===")
    print("This uses persistent pixel watchers that can trigger multiple times")
    
    # Initialize controllers
    vision = EnhancedVisionController()
    mouse = HybridMouseController()
    keyboard = HybridKeyboardController()
    
    # Statistics tracking
    fish_bites = 0
    false_positives = 0
    
    def on_fish_bite(event_data):
        """Called every time a fish bite is detected."""
        nonlocal fish_bites
        fish_bites += 1
        
        print(f"\\n🎣 FISH BITE #{fish_bites} DETECTED!")
        print(f"  Position: {event_data['position']}")
        print(f"  Color: RGB{event_data['current_color']}")
        print(f"  Trigger count: {event_data['trigger_count']}")
        print(f"  Timestamp: {event_data['timestamp']:.2f}")
        
        # Set the hook using enhanced input
        hook_success = (
            keyboard.press_key('space', method='winapi') or
            mouse.click(*event_data['position'], method='winapi') or
            keyboard.press_key('space', method='auto')
        )
        
        if hook_success:
            print("✅ Hook set successfully!")
        else:
            print("❌ Failed to set hook")
    
    def on_bobber_change(event_data):
        """Called when bobber color changes (any significant change)."""
        print(f"🔄 Bobber color changed: RGB{event_data['previous_color']} → RGB{event_data['current_color']}")
        print(f"  Change magnitude: {event_data['color_difference']}")
    
    def global_event_logger(event_data):
        """Logs all watcher events for debugging."""
        print(f"[{event_data['watcher_name']}] Event: {event_data['event_type'].value}")
    
    # Setup
    print("\\n📍 Bobber Setup:")
    print("1. Cast your fishing line manually")
    print("2. Position mouse over the bobber")
    input("Press Enter when ready...")
    
    bobber_pos = mouse.get_position()
    normal_color = vision.get_pixel_color(*bobber_pos)
    
    print(f"✓ Bobber position: {bobber_pos}")
    print(f"✓ Normal color: RGB{normal_color}")
    
    # Configuration
    bite_color = (255, 100, 0)  # Orange for fish bites
    tolerance = 30
    
    print(f"\\n⚙️ Watcher Configuration:")
    print(f"  Bite color: RGB{bite_color}")
    print(f"  Tolerance: {tolerance}")
    
    if input("\\nStart persistent fishing watchers? (y/n): ").lower() != 'y':
        return
    
    print("\\n🔄 Setting up persistent watchers...")
    
    # Create persistent watchers
    vision.watch_pixel_color(
        name="fish_bite_detector",
        x=bobber_pos[0], 
        y=bobber_pos[1],
        target_color=bite_color,
        callback=on_fish_bite,
        tolerance=tolerance,
        check_interval=0.05,  # Check 20 times per second
        cooldown=2.0,  # Minimum 2 seconds between fish bites
        trigger_once=False,  # Keep triggering
        auto_start=True
    )
    
    # Optional: Also watch for any bobber color changes
    vision.watch_pixel_change(
        name="bobber_monitor", 
        x=bobber_pos[0],
        y=bobber_pos[1],
        callback=on_bobber_change,
        min_change=20,
        check_interval=0.1,
        cooldown=0.5,  # Don't spam change events
        trigger_once=False,
        auto_start=True
    )
    
    # Add global event logger
    vision.add_global_watcher_callback(global_event_logger)
    
    print("✅ Persistent watchers started!")
    print("\\n🤖 Fishing automation is now running...")
    print("  - Watchers will continuously monitor the bobber")
    print("  - Fish bites will trigger automatically")
    print("  - Press Ctrl+C to stop")
    
    try:
        # Keep the main thread alive while watchers run
        start_time = time.time()
        last_status_time = start_time
        
        while True:
            current_time = time.time()
            
            # Show status every 30 seconds
            if current_time - last_status_time >= 30.0:
                elapsed = current_time - start_time
                print(f"\\n📊 Status Update (Running {elapsed:.0f}s):")
                print(f"  Fish bites detected: {fish_bites}")
                
                # Show watcher status
                status = vision.get_watcher_status()
                for name, info in status.items():
                    print(f"  {name}: {info['trigger_count']} triggers, {'running' if info['running'] else 'stopped'}")
                
                last_status_time = current_time
            
            time.sleep(1.0)  # Check status every second
            
    except KeyboardInterrupt:
        print("\\n\\n🛑 Stopping fishing automation...")
        
    finally:
        # Stop all watchers
        vision.stop_all_watchers()
        
        # Final statistics
        elapsed = time.time() - start_time
        print(f"\\n📈 Final Statistics:")
        print(f"  Runtime: {elapsed:.1f} seconds")
        print(f"  Fish bites detected: {fish_bites}")
        print(f"  Bites per minute: {(fish_bites / elapsed * 60):.1f}")
        
        print("\\n✅ All watchers stopped")

def multi_pixel_monitoring_demo():
    """Demonstrate monitoring multiple pixels simultaneously."""
    print("\\n=== Multi-Pixel Monitoring Demo ===")
    
    vision = EnhancedVisionController()
    mouse = HybridMouseController()
    
    def health_bar_callback(event_data):
        print(f"🔴 Health bar alert! Color: RGB{event_data['current_color']}")
    
    def mana_bar_callback(event_data):
        print(f"🔵 Mana bar alert! Color: RGB{event_data['current_color']}")
    
    def enemy_detected_callback(event_data):
        print(f"⚠️ Enemy detected! Color: RGB{event_data['current_color']}")
    
    print("Set up monitoring points:")
    
    # Health bar monitoring
    print("\\n1. Position mouse over health bar...")
    input("Press Enter...")
    health_pos = mouse.get_position()
    
    vision.watch_pixel_color(
        name="health_monitor",
        x=health_pos[0], y=health_pos[1],
        target_color=(255, 0, 0),  # Red for low health
        callback=health_bar_callback,
        tolerance=50,
        check_interval=0.2,
        cooldown=5.0  # Don't spam health alerts
    )
    
    # Mana bar monitoring
    print("\\n2. Position mouse over mana bar...")
    input("Press Enter...")
    mana_pos = mouse.get_position()
    
    vision.watch_pixel_color(
        name="mana_monitor",
        x=mana_pos[0], y=mana_pos[1],
        target_color=(0, 0, 255),  # Blue for low mana
        callback=mana_bar_callback,
        tolerance=50,
        check_interval=0.2,
        cooldown=5.0
    )
    
    # Enemy detection (red nameplate)
    print("\\n3. Position mouse where enemy nameplates appear...")
    input("Press Enter...")
    enemy_pos = mouse.get_position()
    
    vision.watch_pixel_color(
        name="enemy_detector",
        x=enemy_pos[0], y=enemy_pos[1],
        target_color=(255, 100, 100),  # Light red for enemy
        callback=enemy_detected_callback,
        tolerance=30,
        check_interval=0.1,
        cooldown=1.0
    )
    
    print("\\n🔍 Monitoring 3 pixels simultaneously...")
    print("All watchers are running in parallel!")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(5.0)
            
            # Show current status
            status = vision.get_watcher_status()
            print("\\n📊 Watcher Status:")
            for name, info in status.items():
                triggers = info['trigger_count']
                running = "🟢" if info['running'] else "🔴"
                print(f"  {running} {name}: {triggers} triggers")
                
    except KeyboardInterrupt:
        vision.stop_all_watchers()
        print("\\n✅ All watchers stopped")

def advanced_fishing_with_state_machine():
    """Advanced fishing with state machine logic using persistent watchers."""
    print("\\n=== Advanced Fishing with State Machine ===")
    
    vision = EnhancedVisionController()
    mouse = HybridMouseController()
    keyboard = HybridKeyboardController()
    
    # Fishing state machine
    class FishingState:
        IDLE = "idle"
        CASTING = "casting"
        WAITING = "waiting"
        BITE_DETECTED = "bite_detected"
        REELING = "reeling"
    
    current_state = FishingState.IDLE
    stats = {"casts": 0, "bites": 0, "catches": 0}
    
    def change_state(new_state, reason=""):
        nonlocal current_state
        print(f"🔄 State: {current_state} → {new_state} ({reason})")
        current_state = new_state
    
    def on_bobber_bite(event_data):
        """Handle fish bite detection."""
        if current_state == FishingState.WAITING:
            stats["bites"] += 1
            change_state(FishingState.BITE_DETECTED, "fish bite")
            
            # Set hook
            keyboard.press_key('space', method='winapi')
            print("🎣 Hook set!")
            
            # Start reeling phase
            time.sleep(0.5)
            change_state(FishingState.REELING, "starting reel")
    
    def on_bobber_normal(event_data):
        """Handle bobber returning to normal (catch completed)."""
        if current_state == FishingState.REELING:
            stats["catches"] += 1
            change_state(FishingState.IDLE, "catch completed")
            print(f"✅ Fish caught! Total: {stats['catches']}")
            
            # Wait a bit before next cast
            time.sleep(2.0)
            cast_line()
    
    def cast_line():
        """Cast the fishing line."""
        if current_state == FishingState.IDLE:
            change_state(FishingState.CASTING, "casting line")
            
            # Cast
            keyboard.press_key('1', method='winapi')
            stats["casts"] += 1
            print(f"🎣 Cast #{stats['casts']}")
            
            # Wait for cast animation
            time.sleep(2.0)
            change_state(FishingState.WAITING, "waiting for bite")
    
    # Setup
    print("Setup bobber monitoring position...")
    input("Position mouse over bobber area and press Enter...")
    
    bobber_pos = mouse.get_position()
    normal_color = vision.get_pixel_color(*bobber_pos)
    bite_color = (255, 100, 0)
    
    # Set up watchers for different states
    vision.watch_pixel_color(
        name="bite_detector",
        x=bobber_pos[0], y=bobber_pos[1],
        target_color=bite_color,
        callback=on_bobber_bite,
        tolerance=30,
        check_interval=0.05,
        cooldown=1.0
    )
    
    vision.watch_pixel_color(
        name="normal_detector", 
        x=bobber_pos[0], y=bobber_pos[1],
        target_color=normal_color,
        callback=on_bobber_normal,
        tolerance=20,
        check_interval=0.1,
        cooldown=2.0
    )
    
    print("\\n🤖 Advanced fishing automation started!")
    print("State machine will handle the complete fishing cycle")
    print("Press Ctrl+C to stop")
    
    try:
        # Start the fishing cycle
        cast_line()
        
        # Monitor and show status
        while True:
            time.sleep(5.0)
            print(f"\\n📊 State: {current_state} | Casts: {stats['casts']} | Bites: {stats['bites']} | Catches: {stats['catches']}")
            
    except KeyboardInterrupt:
        vision.stop_all_watchers()
        
        # Final stats
        print(f"\\n📈 Final Results:")
        print(f"  Casts: {stats['casts']}")
        print(f"  Bites: {stats['bites']}")
        print(f"  Catches: {stats['catches']}")
        if stats['bites'] > 0:
            print(f"  Success rate: {(stats['catches']/stats['bites']*100):.1f}%")

def main():
    """Main menu for persistent watcher examples."""
    print("Persistent Pixel Watcher Examples")
    print("=================================")
    print("Event-driven pixel monitoring that triggers multiple times")
    
    while True:
        print("\\nChoose an example:")
        print("1. Fishing Automation with Persistent Watchers")
        print("2. Multi-Pixel Monitoring Demo")
        print("3. Advanced Fishing with State Machine")
        print("4. Exit")
        
        choice = input("\\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            fishing_automation_with_persistent_watchers()
        elif choice == "2":
            multi_pixel_monitoring_demo()
        elif choice == "3":
            advanced_fishing_with_state_machine()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()