"""
Example demonstrating persistent template watching with transparency support.
Shows how to set up event-driven template monitoring that can trigger multiple times.
"""

import time
import os
from src.automation.transparent_vision import TransparentVisionController, TemplateWatcherEvent
from src.automation import HybridMouseController, HybridKeyboardController

def fishing_automation_with_template_watchers():
    """Advanced fishing automation using persistent template watchers."""
    print("=== Fishing Automation with Template Watchers ===")
    print("Using persistent template watchers with transparency support")
    
    # Initialize controllers
    vision = TransparentVisionController(match_threshold=0.85)
    mouse = HybridMouseController()
    keyboard = HybridKeyboardController()
    
    # Statistics tracking
    bite_count = 0
    catch_count = 0
    
    def on_bite_indicator_found(event_data):
        """Called when fish bite indicator appears."""
        nonlocal bite_count
        bite_count += 1
        
        print(f"\\n🎣 FISH BITE #{bite_count} DETECTED!")
        print(f"  Template: {os.path.basename(event_data['template_path'])}")
        print(f"  Position: {event_data['match']['position']}")
        print(f"  Confidence: {event_data['match']['confidence']:.3f}")
        print(f"  Timestamp: {time.strftime('%H:%M:%S', time.localtime(event_data['timestamp']))}")
        
        try:
            # Click to set hook using enhanced input
            center = event_data['match']['center']
            success = (
                mouse.click(*center, method='winapi') or
                keyboard.press_key('space', method='winapi') or
                mouse.click(*center, method='auto')
            )
            
            if success:
                print("✅ Hook set successfully!")
            else:
                print("❌ Failed to set hook")
                
        except Exception as e:
            print(f"❌ Error setting hook: {e}")
    
    def on_catch_success_found(event_data):
        """Called when fish caught indicator appears."""
        nonlocal catch_count
        catch_count += 1
        
        print(f"\\n🐟 FISH CAUGHT #{catch_count}!")
        print(f"  Template: {os.path.basename(event_data['template_path'])}")
        print(f"  Position: {event_data['match']['position']}")
        print(f"  Confidence: {event_data['match']['confidence']:.3f}")
        
        # Could release mouse button or perform other catch actions
        try:
            mouse.mouse_up(button='left')
            print("✅ Released fishing reel")
        except Exception as e:
            print(f"⚠️ Error releasing reel: {e}")
    
    def on_ui_element_lost(event_data):
        """Called when a UI element disappears."""
        template_name = os.path.basename(event_data['template_path'])
        print(f"🔄 UI Element lost: {template_name}")
    
    def global_template_logger(event_data):
        """Log all template watcher events."""
        event_type = event_data['event_type'].value
        template_name = os.path.basename(event_data['template_path'])
        watcher_name = event_data['watcher_name']
        print(f"[{watcher_name}] {event_type}: {template_name}")
    
    # Example template paths (user would provide actual templates)
    templates = {
        'bite_indicator': 'templates/fish_bite.png',
        'catch_success': 'templates/fish_caught.png',
        'fishing_rod': 'templates/fishing_rod.png'
    }
    
    print("\\n📂 Template Setup:")
    available_templates = {}
    
    for name, path in templates.items():
        if os.path.exists(path):
            available_templates[name] = path
            print(f"  ✅ {name}: {path}")
            
            # Show transparency info
            info = vision.get_transparency_info(path)
            if info.get('has_transparency'):
                print(f"    🔍 Transparency: {info.get('transparency_ratio', 0):.1%}")
        else:
            print(f"  ❌ {name}: {path} (not found)")
    
    if not available_templates:
        print("\\n❌ No template files found. Please provide template images.")
        print("Example paths:")
        for name, path in templates.items():
            print(f"  {name}: {path}")
        return
    
    if input("\\nStart template-based fishing automation? (y/n): ").lower() != 'y':
        return
    
    print("\\n🔄 Setting up template watchers...")
    
    # Set up watchers for available templates
    try:
        if 'bite_indicator' in available_templates:
            vision.watch_template_found(
                name="bite_detector",
                template_path=available_templates['bite_indicator'],
                callback=on_bite_indicator_found,
                threshold=0.8,
                use_transparency=True,
                check_interval=0.1,  # Check 10 times per second
                cooldown=2.0,        # Minimum 2 seconds between bites
                trigger_once=False,  # Keep triggering
                auto_start=True
            )
            print("  ✅ Bite detector configured")
        
        if 'catch_success' in available_templates:
            vision.watch_template_found(
                name="catch_detector",
                template_path=available_templates['catch_success'],
                callback=on_catch_success_found,
                threshold=0.8,
                use_transparency=True,
                check_interval=0.2,  # Check 5 times per second
                cooldown=3.0,        # Minimum 3 seconds between catches
                trigger_once=False,
                auto_start=True
            )
            print("  ✅ Catch detector configured")
        
        if 'fishing_rod' in available_templates:
            # Watch for fishing rod to disappear (might indicate need to re-equip)
            vision.watch_template_lost(
                name="rod_monitor",
                template_path=available_templates['fishing_rod'],
                callback=on_ui_element_lost,
                threshold=0.9,
                use_transparency=True,
                check_interval=1.0,  # Check once per second
                cooldown=5.0,        # Don't spam rod alerts
                trigger_once=False,
                auto_start=True
            )
            print("  ✅ Fishing rod monitor configured")
        
        # Add global event logger
        vision.add_global_template_callback(global_template_logger)
        
        print("\\n✅ All template watchers started!")
        
    except Exception as e:
        print(f"❌ Failed to set up template watchers: {e}")
        return
    
    # Main monitoring loop
    print("\\n🤖 Template-based fishing automation is running!")
    print("  - Monitoring for fishing templates with transparency support")
    print("  - Templates will trigger events when found/lost/moved")
    print("  - Press Ctrl+C to stop")
    
    start_time = time.time()
    last_status_time = start_time
    
    try:
        while True:
            current_time = time.time()
            
            # Show status every 30 seconds
            if current_time - last_status_time >= 30.0:
                elapsed = current_time - start_time
                print(f"\\n📊 Status Update (Running {elapsed:.0f}s):")
                print(f"  Fish bites detected: {bite_count}")
                print(f"  Fish caught: {catch_count}")
                
                # Show watcher status
                status = vision.get_template_watcher_status()
                for name, info in status.items():
                    triggers = info.get('trigger_count', 0)
                    present = info.get('template_present', False)
                    running = '🟢 Running' if info.get('running', False) else '🔴 Stopped'
                    template_status = '👁️ Visible' if present else '👻 Hidden'
                    print(f"  {running} {name}: {triggers} triggers ({template_status})")
                
                last_status_time = current_time
            
            time.sleep(1.0)  # Check status every second
            
    except KeyboardInterrupt:
        print("\\n\\n🛑 Stopping template automation...")
        
    finally:
        # Stop all watchers
        vision.stop_all_template_watchers()
        
        # Final statistics
        elapsed = time.time() - start_time
        print(f"\\n📈 Session Summary:")
        print(f"  Runtime: {elapsed:.1f} seconds")
        print(f"  Fish bites detected: {bite_count}")
        print(f"  Fish caught: {catch_count}")
        
        if bite_count > 0:
            success_rate = (catch_count / bite_count) * 100
            print(f"  Success rate: {success_rate:.1f}%")
        
        if elapsed > 0:
            bites_per_minute = (bite_count / elapsed) * 60
            print(f"  Bites per minute: {bites_per_minute:.1f}")
        
        print("\\n✅ All template watchers stopped")

def ui_monitoring_demo():
    """Demonstrate monitoring multiple UI elements simultaneously."""
    print("\\n=== UI Monitoring Demo ===")
    print("Monitor multiple game UI elements with template watchers")
    
    vision = TransparentVisionController(match_threshold=0.8)
    
    def on_health_low(event_data):
        print(f"🔴 Low health indicator found! Position: {event_data['match']['center']}")
    
    def on_mana_low(event_data):
        print(f"🔵 Low mana indicator found! Position: {event_data['match']['center']}")
    
    def on_enemy_appeared(event_data):
        print(f"⚔️ Enemy appeared! Position: {event_data['match']['center']}")
    
    def on_enemy_disappeared(event_data):
        print(f"✅ Enemy defeated/gone! Template: {os.path.basename(event_data['template_path'])}")
    
    # Example UI templates
    ui_templates = {
        'health_low': 'templates/health_low.png',
        'mana_low': 'templates/mana_low.png',
        'enemy_nameplate': 'templates/enemy.png',
        'quest_complete': 'templates/quest_done.png'
    }
    
    print("\\nSetting up UI watchers...")
    watchers_created = 0
    
    for name, path in ui_templates.items():
        if os.path.exists(path):
            if name == 'health_low':
                vision.watch_template_found(f"{name}_detector", path, on_health_low, 
                                          cooldown=5.0, check_interval=0.5)
            elif name == 'mana_low':
                vision.watch_template_found(f"{name}_detector", path, on_mana_low,
                                          cooldown=5.0, check_interval=0.5)
            elif name == 'enemy_nameplate':
                # Watch for both appearance and disappearance
                vision.watch_template_found(f"{name}_appear", path, on_enemy_appeared,
                                          cooldown=1.0, check_interval=0.2)
                vision.watch_template_lost(f"{name}_disappear", path, on_enemy_disappeared,
                                         cooldown=2.0, check_interval=0.3)
            
            watchers_created += 1
            print(f"  ✅ {name}: {path}")
        else:
            print(f"  ❌ {name}: {path} (not found)")
    
    if watchers_created == 0:
        print("\\n❌ No UI templates found. Create some template images first.")
        return
    
    print(f"\\n🔍 Monitoring {watchers_created} UI elements...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(5.0)
            
            # Show status
            status = vision.get_template_watcher_status()
            print("\\n📊 UI Watcher Status:")
            for name, info in status.items():
                triggers = info.get('trigger_count', 0)
                present = '👁️' if info.get('template_present', False) else '👻'
                print(f"  {present} {name}: {triggers} triggers")
                
    except KeyboardInterrupt:
        vision.stop_all_template_watchers()
        print("\\n✅ UI monitoring stopped")

def template_movement_tracking():
    """Demonstrate tracking template movement."""
    print("\\n=== Template Movement Tracking ===")
    print("Track when templates move around the screen")
    
    vision = TransparentVisionController(match_threshold=0.8)
    
    def on_template_moved(event_data):
        """Called when a template moves."""
        match = event_data['match']
        previous = event_data['previous_match']
        distance = event_data['movement_distance']
        
        print(f"📍 Template moved {distance:.1f} pixels!")
        print(f"  From: {previous['center']} → To: {match['center']}")
        print(f"  Template: {os.path.basename(event_data['template_path'])}")
        print(f"  Confidence: {match['confidence']:.3f}")
    
    # Ask user for template
    template_path = input("Enter path to template for movement tracking: ")
    
    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        return
    
    # Set up movement watcher
    vision.watch_template_moved(
        name="movement_tracker",
        template_path=template_path,
        callback=on_template_moved,
        threshold=0.8,
        use_transparency=True,
        check_interval=0.2,        # Check 5 times per second
        movement_threshold=15,     # Trigger on 15+ pixel movement
        cooldown=0.5              # Max 2 triggers per second
    )
    
    print(f"\\n🎯 Tracking movement of: {os.path.basename(template_path)}")
    print("Move the template around on screen to see tracking in action")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(2.0)
            
            status = vision.get_template_watcher_status("movement_tracker")
            if status:
                triggers = status.get('trigger_count', 0)
                present = status.get('template_present', False)
                print(f"\\r📊 Movements detected: {triggers} | Present: {'Yes' if present else 'No'}     ", end="", flush=True)
                
    except KeyboardInterrupt:
        vision.stop_all_template_watchers()
        print("\\n\\n✅ Movement tracking stopped")

def main():
    """Main menu for template watcher examples."""
    print("Persistent Template Watcher Examples")
    print("====================================")
    print("Event-driven template monitoring with transparency support")
    
    while True:
        print("\\nChoose an example:")
        print("1. Fishing Automation with Template Watchers")
        print("2. UI Monitoring Demo")
        print("3. Template Movement Tracking")
        print("4. Exit")
        
        choice = input("\\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            fishing_automation_with_template_watchers()
        elif choice == "2":
            ui_monitoring_demo()
        elif choice == "3":
            template_movement_tracking()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()