"""
Step-by-step tutorial for setting up Computer Vision templates.

This script helps you:
1. Capture template images from your screen
2. Test template matching accuracy
3. Create color detection profiles
4. Set up automation workflows
"""

import os
import time
import cv2
import numpy as np
from src.automation import VisionController, MouseController, KeyboardController

class CVSetupHelper:
    """Helper class for setting up computer vision templates and testing."""
    
    def __init__(self):
        self.vision = VisionController(match_threshold=0.8)
        self.mouse = MouseController(fail_safe=True)
        self.keyboard = KeyboardController()
        
        # Create directories
        os.makedirs("templates", exist_ok=True)
        os.makedirs("test_screenshots", exist_ok=True)
        os.makedirs("debug", exist_ok=True)
        
    def capture_template_interactive(self):
        """Interactive template capture tool."""
        print("=== Interactive Template Capture ===")
        print("This tool helps you capture template images for automation.")
        print("\nInstructions:")
        print("1. Navigate to the UI element you want to capture")
        print("2. Press Enter here to take a screenshot")
        print("3. Use mouse to select the area you want as template")
        print("4. Template will be saved automatically")
        
        template_name = input("\nEnter template name (e.g., 'start_button'): ").strip()
        if not template_name:
            template_name = "template_" + str(int(time.time()))
        
        print(f"\n📸 Ready to capture template: {template_name}")
        print("Make sure the UI element is visible on screen.")
        input("Press Enter to take screenshot...")
        
        # Capture full screen
        screenshot_path = f"test_screenshots/capture_{template_name}.png"
        success = self.vision.screen_capture.save_screenshot(screenshot_path)
        
        if success:
            print(f"✓ Screenshot saved: {screenshot_path}")
            print(f"\n📋 Next steps:")
            print(f"1. Open {screenshot_path} in an image editor")
            print(f"2. Crop the UI element you want to detect")
            print(f"3. Save the cropped image as 'templates/{template_name}.png'")
            print(f"4. Use vision.find_on_screen('templates/{template_name}.png') in your code")
        else:
            print("❌ Failed to capture screenshot")
    
    def test_template_matching(self):
        """Test existing templates and show results."""
        print("=== Template Matching Test ===")
        
        # Find all template files
        template_files = []
        if os.path.exists("templates"):
            template_files = [f for f in os.listdir("templates") if f.endswith(('.png', '.jpg', '.jpeg'))]
        
        if not template_files:
            print("❌ No template files found in templates/ directory")
            print("Use the template capture tool first to create templates.")
            return
        
        print(f"Found {len(template_files)} template(s):")
        for i, template in enumerate(template_files, 1):
            print(f"  {i}. {template}")
        
        print("\nTesting all templates against current screen...")
        
        # Test each template
        results = []
        for template_file in template_files:
            template_path = f"templates/{template_file}"
            print(f"\n🔍 Testing {template_file}...")
            
            match = self.vision.find_on_screen(template_path)
            if match:
                confidence = match['confidence']
                center = match['center']
                print(f"  ✅ Found at {center} with confidence {confidence:.3f}")
                results.append((template_file, match, True))
                
                # Save debug image showing the match
                self._save_debug_match_image(template_path, match)
            else:
                print(f"  ❌ Not found (confidence below threshold)")
                results.append((template_file, None, False))
        
        # Summary
        found_count = sum(1 for _, _, found in results if found)
        print(f"\n📊 Results Summary:")
        print(f"  Templates tested: {len(template_files)}")
        print(f"  Found on screen: {found_count}")
        print(f"  Not found: {len(template_files) - found_count}")
        
        if found_count > 0:
            print(f"\n💡 Check debug/ directory for match visualization images")
    
    def analyze_screen_colors(self):
        """Analyze current screen for prominent colors."""
        print("=== Screen Color Analysis ===")
        print("This tool analyzes your screen to find prominent colors for detection.")
        
        input("Press Enter to analyze current screen...")
        
        # Capture screen
        screen = self.vision.screen_capture.capture_screen()
        if screen.size == 0:
            print("❌ Failed to capture screen")
            return
        
        print(f"✓ Captured screen: {screen.shape}")
        
        # Convert to HSV for analysis
        hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
        
        # Analyze color distribution
        print("\n🎨 Analyzing colors...")
        
        # Sample colors from different screen regions
        h, w = screen.shape[:2]
        sample_points = [
            (w//4, h//4),    # Top-left quadrant
            (3*w//4, h//4),  # Top-right quadrant  
            (w//4, 3*h//4),  # Bottom-left quadrant
            (3*w//4, 3*h//4),# Bottom-right quadrant
            (w//2, h//2),    # Center
        ]
        
        print("\nColor samples from different screen regions:")
        for i, (x, y) in enumerate(sample_points, 1):
            # Get color at this point
            bgr_color = screen[y, x]
            hsv_color = hsv[y, x]
            rgb_color = (int(bgr_color[2]), int(bgr_color[1]), int(bgr_color[0]))  # BGR to RGB
            
            print(f"  Region {i} at ({x:4d}, {y:4d}): RGB{rgb_color} HSV{tuple(hsv_color)}")
        
        # Find dominant colors
        print("\n🔍 Finding dominant colors...")
        self._analyze_dominant_colors(screen)
    
    def create_color_detection_profile(self):
        """Create a color detection profile for a specific color."""
        print("=== Color Detection Profile Creator ===")
        print("This tool helps you create color detection profiles.")
        
        print("\nOptions:")
        print("1. Click on screen to sample a color")
        print("2. Enter RGB values manually")
        
        choice = input("Choose option (1 or 2): ").strip()
        
        if choice == "1":
            print("\nClick on the color you want to detect...")
            print("Position your mouse over the target color and press Enter")
            input("Press Enter when mouse is positioned...")
            
            # Get mouse position and sample color
            mouse_pos = self.mouse.get_position()
            rgb_color = self.vision.get_pixel_color(*mouse_pos)
            print(f"✓ Sampled color at {mouse_pos}: RGB{rgb_color}")
            
        elif choice == "2":
            try:
                r = int(input("Enter Red value (0-255): "))
                g = int(input("Enter Green value (0-255): "))
                b = int(input("Enter Blue value (0-255): "))
                rgb_color = (r, g, b)
                print(f"✓ Using RGB{rgb_color}")
            except ValueError:
                print("❌ Invalid input. Using default red color.")
                rgb_color = (255, 0, 0)
        else:
            print("❌ Invalid choice. Using default red color.")
            rgb_color = (255, 0, 0)
        
        # Create color range
        tolerance = int(input("Enter tolerance (10-50, default 20): ") or "20")
        
        from src.automation.vision import rgb_to_hsv_range
        color_range = rgb_to_hsv_range(*rgb_color, tolerance=tolerance)
        
        print(f"\n✅ Color detection profile created:")
        print(f"  Target RGB: {rgb_color}")
        print(f"  Tolerance: {tolerance}")
        print(f"  HSV Range: {color_range}")
        
        # Test the color detection
        print(f"\n🧪 Testing color detection...")
        screen = self.vision.screen_capture.capture_screen()
        if screen.size > 0:
            regions = self.vision.color_detector.find_color_regions(screen, color_range)
            print(f"  Found {len(regions)} regions with this color")
            
            for i, region in enumerate(regions[:5]):  # Show first 5 regions
                center = region['center']
                area = region['area']
                print(f"    Region {i+1}: Center {center}, Area {area}")
        
        # Save the profile code
        profile_name = input("\nEnter profile name (e.g., 'health_bar_red'): ").strip()
        if profile_name:
            code = f"""
# Color detection profile: {profile_name}
{profile_name}_color = rgb_to_hsv_range({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]}, tolerance={tolerance})

# Usage:
regions = vision.color_detector.find_color_regions(screen, {profile_name}_color)
for region in regions:
    center = region['center']
    area = region['area']
    if area > 100:  # Filter small regions
        print(f"Found {profile_name} at {{center}}")
"""
            
            with open(f"debug/{profile_name}_profile.py", "w") as f:
                f.write(code)
            
            print(f"✅ Profile saved to debug/{profile_name}_profile.py")
    
    def setup_fishing_automation_templates(self):
        """Guided setup for fishing game automation."""
        print("=== Fishing Game Automation Setup ===")
        print("This wizard helps set up templates for fishing game automation.")
        
        templates_needed = [
            ("fishing_rod_icon", "The fishing rod icon in inventory or hotbar"),
            ("cast_button", "The button or area to click to cast"),
            ("fishing_spot", "A fishing spot or water area to click"),
            ("fish_bite_indicator", "Visual indicator when fish bites (optional)"),
            ("catch_dialog", "Dialog or UI when fish is caught"),
            ("inventory_full", "Indicator when inventory is full")
        ]
        
        print(f"\nFor fishing automation, you'll need these templates:")
        for name, description in templates_needed:
            print(f"  📁 {name}.png - {description}")
        
        print(f"\nRecommended workflow:")
        print(f"1. Start your fishing game")
        print(f"2. For each template needed:")
        print(f"   a) Navigate to show the UI element")
        print(f"   b) Use the template capture tool")
        print(f"   c) Crop and save the template image")
        print(f"3. Test templates with the template matching test")
        print(f"4. Set up color detection for dynamic elements (fish bite indicators)")
        
        if input("\nStart template capture wizard? (y/n): ").lower().strip() == 'y':
            for name, description in templates_needed:
                print(f"\n📸 Capturing template: {name}")
                print(f"Description: {description}")
                
                if input("Capture this template? (y/n/skip): ").lower().strip() == 'y':
                    # Set template name and capture
                    old_capture = self.capture_template_interactive
                    # Override the input to use our template name
                    self.template_name_override = name
                    print(f"Navigate to show: {description}")
                    input("Press Enter when ready to capture...")
                    
                    screenshot_path = f"test_screenshots/capture_{name}.png"
                    success = self.vision.screen_capture.save_screenshot(screenshot_path)
                    
                    if success:
                        print(f"✅ Captured {screenshot_path}")
                        print(f"Now crop this image to just the {description} and save as templates/{name}.png")
                    else:
                        print(f"❌ Failed to capture {name}")
        
        print(f"\n✅ Fishing automation setup guide completed!")
        print(f"Next: Test your templates and create your automation script!")
    
    def _save_debug_match_image(self, template_path, match):
        """Save debug image showing template match location."""
        try:
            # Load template
            template = cv2.imread(template_path)
            if template is None:
                return
            
            # Capture current screen
            screen = self.vision.screen_capture.capture_screen()
            if screen.size == 0:
                return
            
            # Draw rectangle around match
            pos = match['position']
            size = match['size']
            top_left = pos
            bottom_right = (pos[0] + size[0], pos[1] + size[1])
            center = match['center']
            
            # Draw match rectangle in green
            cv2.rectangle(screen, top_left, bottom_right, (0, 255, 0), 2)
            
            # Draw center point
            cv2.circle(screen, center, 5, (0, 255, 0), -1)
            
            # Add confidence text
            confidence_text = f"Confidence: {match['confidence']:.3f}"
            cv2.putText(screen, confidence_text, (pos[0], pos[1]-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Save debug image
            template_name = os.path.basename(template_path).split('.')[0]
            debug_path = f"debug/match_{template_name}.png"
            cv2.imwrite(debug_path, screen)
            
        except Exception as e:
            print(f"Warning: Could not save debug image: {e}")
    
    def _analyze_dominant_colors(self, screen):
        """Analyze dominant colors in the screen."""
        try:
            # Resize for faster processing
            small_screen = cv2.resize(screen, (200, 150))
            
            # Convert to RGB for k-means
            rgb_screen = cv2.cvtColor(small_screen, cv2.COLOR_BGR2RGB)
            data = rgb_screen.reshape((-1, 3))
            data = np.float32(data)
            
            # K-means clustering to find dominant colors
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            k = 5  # Find top 5 colors
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert centers back to int
            centers = np.uint8(centers)
            
            print(f"\n🎨 Top {k} dominant colors on screen:")
            for i, color in enumerate(centers, 1):
                rgb_color = tuple(color)
                print(f"  Color {i}: RGB{rgb_color}")
                
                # Show how to use this color for detection
                print(f"    Use: rgb_to_hsv_range({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]}, tolerance=20)")
                
        except Exception as e:
            print(f"Color analysis failed: {e}")

def main():
    """Main setup wizard."""
    print("=== Computer Vision Setup Tutorial ===")
    print("This wizard helps you set up computer vision for game automation.")
    
    helper = CVSetupHelper()
    
    while True:
        print(f"\n🛠️  CV Setup Options:")
        print(f"1. 📸 Capture template image")
        print(f"2. 🧪 Test existing templates")  
        print(f"3. 🎨 Analyze screen colors")
        print(f"4. 🌈 Create color detection profile")
        print(f"5. 🎣 Fishing game setup wizard")
        print(f"6. ❌ Exit")
        
        choice = input(f"\nChoose option (1-6): ").strip()
        
        try:
            if choice == "1":
                helper.capture_template_interactive()
            elif choice == "2":
                helper.test_template_matching()
            elif choice == "3":
                helper.analyze_screen_colors()
            elif choice == "4":
                helper.create_color_detection_profile()
            elif choice == "5":
                helper.setup_fishing_automation_templates()
            elif choice == "6":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Interrupted by user.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again.")
    
    print(f"\n📚 Resources created:")
    print(f"  📁 templates/ - Your template images")
    print(f"  📁 test_screenshots/ - Captured screenshots")
    print(f"  📁 debug/ - Debug images and profiles")

if __name__ == "__main__":
    main()