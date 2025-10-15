from src.automation import MouseController

mouse = MouseController(fail_safe=True, pause_duration=0.5)

mouse.click(1174, 348)
mouse.click(1173, 892)
mouse.click(1685, 341)
mouse.click(1685, 892)