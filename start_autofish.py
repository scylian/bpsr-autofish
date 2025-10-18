import threading
import time
from src.automation import VisionController, EnhancedVisionController, TransparentVisionController, HybridMouseController, HybridKeyboardController

vision = EnhancedVisionController(match_threshold=0.8)
escape_vision = TransparentVisionController(match_threshold=0.8)
mouse = HybridMouseController()
keyboard = HybridKeyboardController()
bite_color = (255, 75, 1)
catch_color = (255, 241, 157)
move_color = (249, 188, 23)
pole_color = (220, 108, 27)
escape_color = (2, 17, 83)
level_up = False
sleep_cancel_event = threading.Event()

def recovery_check():
    print("No bite detected in 60 seconds, assuming stuck - restarting...")
    check_rod()

def continue_fishing():
    print("AAAAGAIN!")
    print("🤖 Autofish is running! Press Ctrl+C to stop")
    print("✓ Waiting for that fat fuck to snag...")
    mouse.click(955, 568, method="winapi")

    recovery_timer = threading.Timer(60.0, recovery_check) # 60 second failsafe
    recovery_timer.start()

    global current_recovery_timer
    current_recovery_timer = recovery_timer

def buy_pole():
    print("Broke your dick, getting a new one...")
    time.sleep(2)
    keyboard.key_down('alt', method="auto")
    mouse.click(1669, 1015, method="pyautogui")
    keyboard.key_up('alt', method="auto")
    time.sleep(1)
    mouse.click(1729, 607, method="pyautogui")
    time.sleep(2)
    check_rod()

def check_rod():
    pole_broken = vision.wait_for_pixel_color(1692, 989, pole_color, tolerance=10, timeout=1, check_interval=0.1)
    if pole_broken:
        buy_pole()
    else:
        print("Your long, hard rod is fine")
        continue_fishing()

def on_fish_bite(event_data):
    global level_up, sleep_cancel_event, current_recovery_timer
    
    if current_recovery_timer:
        current_recovery_timer.cancel()
    
    print("🎉 SUCCESS! Hooked that bitch!")
    mouse.mouse_down(955, 568, button="left")
    level_up = True

    # Interruptible sleep for 120 seconds
    sleep_cancel_event.clear() # Reset the event
    if not sleep_cancel_event.wait(30): # Returns False if timeout, True if set
        # Sleep completed normally (not interrupted)
        if level_up:
            mouse.mouse_up(button="left")
            time.sleep(4)
            mouse.click(1584, 964, method="pyautogui")
            time.sleep(2)
            check_rod()

def on_fish_caught(event_data):
    global level_up, sleep_cancel_event, current_recovery_timer

    if current_recovery_timer:
        current_recovery_timer.cancel()

    print("🐟 CAUGHT THAT MOTHAFUCKA!")
    print(f"Fish caught: {event_data['trigger_count']}")
    level_up = False
    sleep_cancel_event.set() # Cancel the sleep in on_fish_bite
    mouse.mouse_up(button="left")
    time.sleep(4)
    mouse.click(1584, 964, method="pyautogui")
    time.sleep(2)
    check_rod()

def on_fish_escape(event_data):
    global level_up, sleep_cancel_event
    print("❌ BITCH RAN!")
    print(f"Fish escaped: {event_data['trigger_count']}")
    level_up = False
    sleep_cancel_event.set() # Cancel the sleep in on_fish_bite
    mouse.mouse_up(button="left")
    time.sleep(4)
    mouse.click(1584, 964, method="pyautogui")
    time.sleep(2)
    check_rod()

def on_move_left(event_data):
    print("Moving left...")
    keyboard.key_down('a', method="auto")
    time.sleep(2)
    keyboard.key_up('a', method="auto")

def on_move_right(event_data):
    print("Moving right...")
    keyboard.key_down('d', method="auto")
    time.sleep(2)
    keyboard.key_up('d', method="auto")

# Watch for fish bites
vision.watch_pixel_color(
    name="bite_detector",
    x=955, y=568,
    target_color=bite_color,
    callback=on_fish_bite,
    tolerance=3,
    check_interval=0.1,
    cooldown=10.0,
    trigger_once=False,
    auto_start=False
)

# Watch for fish caught
vision.watch_pixel_color(
    name="catch_detector",
    x=1084, y=698,
    target_color=catch_color,
    callback=on_fish_caught,
    tolerance=3,
    check_interval=0.1,
    cooldown=10.0,
    trigger_once=False,
    auto_start=False
)

# Watch for fish escaped
escape_vision.watch_template_found(
    name="escape_detector",
    template_path="templates/escaped.png",
    callback=on_fish_escape,
    threshold=0.8,
    use_transparency=True,
    region={'top': 611, 'left': 756, 'width': 937, 'height': 152},
    check_interval=0.1,
    cooldown=30.0,
    trigger_once=False,
    auto_start=True
)

# Watch for moving left
vision.watch_pixel_color(
    name="move_left_detector",
    x=774, y=543,
    target_color=move_color,
    callback=on_move_left,
    tolerance=3,
    check_interval=0.1,
    cooldown=0.2,
    trigger_once=False,
    auto_start=False
)

# Watch for moving right
vision.watch_pixel_color(
    name="move_right_detector",
    x=1142, y=541,
    target_color=move_color,
    callback=on_move_right,
    tolerance=3,
    check_interval=0.1,
    cooldown=0.2,
    trigger_once=False,
    auto_start=False
)

vision.start_all_watchers()

# Prompt user to prepare for autofishing
print("Please place your cursor over the game window, DO NOT CLICK INTO THE GAME!")
print("Press Enter when ready...")
input()

# Click into game
cur_pos = mouse.get_position()
mouse.click(cur_pos[0], cur_pos[1], method="pyautogui")

# Cast fishing line and wait for fish to snag
# mouse.click(cur_pos[0], cur_pos[1], method="winapi")

# Keep the script running so watchers can work
print("🤖 Autofish is running! Press Ctrl+C to stop")
print("Clicked into game window, starting autofishing...")
print("✓ Waiting for that fat fuck to snag...")
print("...")
check_rod()
try:
    while True:
        time.sleep(1.0)  # Keep main thread alive
except KeyboardInterrupt:
    print("\n🛑 Stopping autofish...")
    vision.stop_all_watchers()
    print("✅ Stopped")

# success = vision.wait_for_pixel_color(955, 568, target_color, tolerance=3, timeout=300, check_interval=0.1)

# if success:
#     print("🎉 SUCCESS! Hooked that bitch!")
#     mouse.mouse_down(955, 568, button="left") # start reeling in fish
#     success_color = (255, 241, 157)
#     move_left = vision.wait_for_pixel
#     success = vision.wait_for_pixel_color(1084, 698, success_color, tolerance=3, timeout=180, check_interval=0.1)
#     while !success:

#     if success:
#         print("🐟 CAUGHT THAT MOTHAFUCKA!")
#         mouse.mouse_up(button="left")
# else:
#     print("⏰ Timeout reached - pixel did not reach target color")