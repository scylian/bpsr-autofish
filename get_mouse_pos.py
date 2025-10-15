from src.automation import MouseController, VisionController

mouse = MouseController(fail_safe=True, pause_duration=0.5)
vision = VisionController(match_threshold=0.5)
current_pos = mouse.get_position()
rgb = vision.get_pixel_color(*current_pos)
print(f"Current mouse position: {current_pos}")
print(f"Pixel color at mouse position: {rgb}")