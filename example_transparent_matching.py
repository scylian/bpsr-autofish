"""
Example demonstrating transparent template matching.
Shows the difference between regular and transparency-aware template matching.
"""

import os
from src.automation.transparent_vision import TransparentVisionController
from src.automation.vision import VisionController

def compare_matching_methods():
    """Compare regular vs transparent template matching."""
    print("=== Template Matching Comparison ===")
    print("This compares regular vs transparent template matching\n")
    
    # Initialize both controllers
    regular_vision = VisionController(match_threshold=0.8)
    transparent_vision = TransparentVisionController(match_threshold=0.8)
    
    # Get template file
    template_path = input("Enter path to template image (PNG with transparency preferred): ")
    
    if not os.path.exists(template_path):
        print(f"❌ Template file not found: {template_path}")
        return
    
    print(f"✅ Using template: {template_path}")
    
    # Get transparency information
    transparency_info = transparent_vision.get_transparency_info(template_path)
    print(f"\n🔍 Template Analysis:")
    print(f"  Has transparency: {transparency_info.get('has_transparency', False)}")
    print(f"  OpenCV supports masks: {transparency_info.get('opencv_supports_masks', False)}")
    
    if transparency_info.get('has_transparency'):
        print(f"  Opaque pixels: {transparency_info.get('opaque_pixels', 0)}")
        print(f"  Transparent pixels: {transparency_info.get('transparent_pixels', 0)}")
        print(f"  Opacity ratio: {transparency_info.get('opacity_ratio', 0):.2%}")
        
        # Offer to save the mask
        save_mask = input("\nSave transparency mask as image? (y/n): ").lower() == 'y'
        if save_mask:
            mask_path = template_path.replace('.png', '_mask.png')
            if transparent_vision.save_template_mask(template_path, mask_path):
                print(f"✅ Mask saved to: {mask_path}")
    
    print(f"\n🔄 Starting comparison...")
    
    # Test regular matching
    print("\n1️⃣ Regular Template Matching (ignores transparency):")
    regular_match = regular_vision.find_on_screen(template_path)
    
    if regular_match:
        print(f"  ✅ Match found!")
        print(f"  Position: {regular_match['position']}")
        print(f"  Center: {regular_match['center']}")
        print(f"  Confidence: {regular_match['confidence']:.3f}")
    else:
        print(f"  ❌ No match found")
    
    # Test transparent matching
    print("\n2️⃣ Transparent Template Matching (respects transparency):")
    transparent_match = transparent_vision.find_on_screen(template_path, use_transparency=True)
    
    if transparent_match:
        print(f"  ✅ Match found!")
        print(f"  Position: {transparent_match['position']}")
        print(f"  Center: {transparent_match['center']}")
        print(f"  Confidence: {transparent_match['confidence']:.3f}")
        print(f"  Used transparency: {transparent_match.get('has_transparency', False)}")
    else:
        print(f"  ❌ No match found")
    
    # Compare results
    if regular_match and transparent_match:
        pos_diff = abs(regular_match['position'][0] - transparent_match['position'][0]) + \
                   abs(regular_match['position'][1] - transparent_match['position'][1])
        conf_diff = abs(regular_match['confidence'] - transparent_match['confidence'])
        
        print(f"\n📊 Comparison Results:")
        print(f"  Position difference: {pos_diff} pixels")
        print(f"  Confidence difference: {conf_diff:.3f}")
        
        if pos_diff == 0 and conf_diff < 0.01:
            print("  🟰 Results are nearly identical")
        elif transparent_match['confidence'] > regular_match['confidence']:
            print("  🟢 Transparent matching performed better")
        else:
            print("  🟡 Regular matching performed better")
    
    # Test finding all matches
    print(f"\n3️⃣ Finding all matches with transparency:")
    all_matches = transparent_vision.find_all_on_screen(template_path, use_transparency=True)
    print(f"  Found {len(all_matches)} total matches")
    
    for i, match in enumerate(all_matches[:5]):  # Show first 5
        print(f"  Match {i+1}: pos={match['position']}, conf={match['confidence']:.3f}")

def test_custom_masks():
    """Test custom shape masks for template matching."""
    print("\n=== Custom Shape Masks ===")
    print("Testing different mask shapes for template matching\n")
    
    vision = TransparentVisionController(match_threshold=0.8)
    
    template_path = input("Enter path to template image: ")
    
    if not os.path.exists(template_path):
        print(f"❌ Template file not found: {template_path}")
        return
    
    # Test different mask shapes
    mask_shapes = ["circle", "ellipse", "rounded_rect"]
    
    for shape in mask_shapes:
        print(f"\n🔍 Testing {shape} mask:")
        
        match = vision.find_with_custom_mask(
            template_path=template_path,
            mask_shape=shape,
            threshold=0.7  # Lower threshold for custom masks
        )
        
        if match:
            print(f"  ✅ Match found with {shape} mask")
            print(f"  Position: {match['position']}")
            print(f"  Confidence: {match['confidence']:.3f}")
        else:
            print(f"  ❌ No match found with {shape} mask")

def transparency_info_demo():
    """Demo showing detailed transparency information."""
    print("\n=== Transparency Information Demo ===")
    print("Get detailed information about template transparency\n")
    
    vision = TransparentVisionController()
    
    # Get multiple template files
    templates = []
    while True:
        template_path = input("Enter template path (or 'done' to finish): ")
        if template_path.lower() == 'done':
            break
        if os.path.exists(template_path):
            templates.append(template_path)
        else:
            print(f"❌ File not found: {template_path}")
    
    if not templates:
        print("❌ No valid templates provided")
        return
    
    # Analyze each template
    print(f"\n📊 Analyzing {len(templates)} templates:\n")
    
    for template_path in templates:
        filename = os.path.basename(template_path)
        print(f"🖼️ {filename}:")
        
        info = vision.get_transparency_info(template_path)
        
        if 'error' in info:
            print(f"  ❌ Error: {info['error']}")
            continue
        
        print(f"  Has transparency: {'Yes' if info['has_transparency'] else 'No'}")
        
        if info['has_transparency']:
            print(f"  Total pixels: {info['total_pixels']:,}")
            print(f"  Opaque pixels: {info['opaque_pixels']:,}")
            print(f"  Transparent pixels: {info['transparent_pixels']:,}")
            print(f"  Opacity: {info['opacity_ratio']:.1%}")
            print(f"  Transparency: {info['transparency_ratio']:.1%}")
        
        print(f"  OpenCV mask support: {'Yes' if info['opencv_supports_masks'] else 'No'}")
        print()

def practical_fishing_example():
    """Practical example using transparent templates for fishing."""
    print("\n=== Practical Fishing Example ===")
    print("Using transparent templates to find fishing UI elements\n")
    
    vision = TransparentVisionController(match_threshold=0.85)
    
    # Example fishing UI elements (user would provide these)
    ui_elements = {
        "Fish Bite Indicator": "templates/fish_bite.png",
        "Fishing Rod Icon": "templates/fishing_rod.png", 
        "Catch Success": "templates/fish_caught.png"
    }
    
    print("🎣 Fishing UI Detection:")
    print("(Note: You need to provide actual template images)")
    
    for element_name, template_path in ui_elements.items():
        print(f"\n🔍 Looking for {element_name}...")
        
        if not os.path.exists(template_path):
            print(f"  📁 Template not found: {template_path}")
            continue
        
        # Check if template has transparency
        info = vision.get_transparency_info(template_path)
        has_transparency = info.get('has_transparency', False)
        
        print(f"  Template transparency: {'Yes' if has_transparency else 'No'}")
        
        # Find the element on screen
        match = vision.find_on_screen(template_path, use_transparency=has_transparency)
        
        if match:
            print(f"  ✅ Found at position {match['position']}")
            print(f"  Confidence: {match['confidence']:.3f}")
            print(f"  Center point: {match['center']}")
            
            # For fishing, you might click on the center
            print(f"  → Would click at: {match['center']}")
        else:
            print(f"  ❌ Not found on screen")
    
    print(f"\n💡 Benefits of transparency support:")
    print(f"  • Ignores background in template images")
    print(f"  • More accurate matching of UI elements")
    print(f"  • Better performance with irregular shapes")
    print(f"  • Reduces false positives from background")

def main():
    """Main menu for transparency examples."""
    print("Transparent Template Matching Examples")
    print("=====================================")
    print("Demonstrates handling PNG templates with alpha channels")
    
    while True:
        print(f"\nChoose an example:")
        print("1. Compare Regular vs Transparent Matching")
        print("2. Test Custom Shape Masks")
        print("3. Transparency Information Demo")
        print("4. Practical Fishing Example")
        print("5. Exit")
        
        choice = input(f"\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            compare_matching_methods()
        elif choice == "2":
            test_custom_masks()
        elif choice == "3":
            transparency_info_demo()
        elif choice == "4":
            practical_fishing_example()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()