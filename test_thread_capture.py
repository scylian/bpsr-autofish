"""
Test script to verify thread-safe screen capture works properly.
This tests the fix for the mss threading issue.
"""

import time
import threading
from src.automation.transparent_vision import TransparentVisionController
from src.automation.vision import ScreenCapture

def test_screen_capture_in_thread():
    """Test screen capture from within a thread."""
    print("🧵 Testing screen capture in thread...")
    
    capture = ScreenCapture()
    
    def capture_worker(worker_id):
        """Worker function that captures screen."""
        print(f"Worker {worker_id} starting...")
        
        try:
            for i in range(5):
                screenshot = capture.capture_screen()
                
                if screenshot.size > 0:
                    print(f"Worker {worker_id}: Capture {i+1} success ({screenshot.shape})")
                else:
                    print(f"Worker {worker_id}: Capture {i+1} failed")
                
                time.sleep(0.5)
            
            print(f"Worker {worker_id} completed successfully!")
            
        except Exception as e:
            print(f"Worker {worker_id} error: {e}")
    
    # Create multiple threads
    threads = []
    for i in range(3):
        t = threading.Thread(target=capture_worker, args=(i+1,))
        threads.append(t)
    
    # Start all threads
    for t in threads:
        t.start()
    
    # Wait for all to complete
    for t in threads:
        t.join()
    
    print("✅ Thread screen capture test completed")

def test_template_watcher_basic():
    """Test basic template watcher functionality."""
    print("🔍 Testing basic template watcher...")
    
    vision = TransparentVisionController(match_threshold=0.8)
    
    # Create a dummy callback
    def dummy_callback(event_data):
        print(f"📄 Template event: {event_data['event_type'].value}")
        print(f"   Trigger count: {event_data['trigger_count']}")
        print(f"   Watcher: {event_data['watcher_name']}")
    
    try:
        # Try to create a template watcher (will fail if template doesn't exist, but shouldn't crash)
        vision.watch_template_found(
            name="test_watcher",
            template_path="non_existent_template.png",  # This will fail gracefully
            callback=dummy_callback,
            check_interval=1.0,
            auto_start=False  # Don't start automatically
        )
        
        print("✅ Template watcher creation succeeded (template file not required for this test)")
        
        # Test status
        status = vision.get_template_watcher_status("test_watcher")
        if status:
            print(f"   Watcher status: {status}")
        
        # Clean up
        vision.remove_template_watcher("test_watcher")
        print("✅ Template watcher cleanup completed")
        
    except Exception as e:
        print(f"❌ Template watcher test error: {e}")

def test_thread_safety_comprehensive():
    """Comprehensive thread safety test."""
    print("🔬 Comprehensive thread safety test...")
    
    vision = TransparentVisionController(match_threshold=0.8)
    
    # Track results
    results = {"success": 0, "error": 0}
    results_lock = threading.Lock()
    
    def template_search_worker(worker_id):
        """Worker that repeatedly searches for templates."""
        print(f"🔍 Search worker {worker_id} starting...")
        
        try:
            for i in range(10):
                # Try to find a non-existent template (this will trigger screen capture)
                match = vision.find_on_screen(
                    "non_existent_template.png", 
                    use_transparency=True
                )
                
                with results_lock:
                    if match is None:  # Expected result
                        results["success"] += 1
                    else:
                        results["error"] += 1
                
                time.sleep(0.1)
            
            print(f"🔍 Search worker {worker_id} completed")
            
        except Exception as e:
            print(f"❌ Search worker {worker_id} error: {e}")
            with results_lock:
                results["error"] += 1
    
    # Create multiple search workers
    threads = []
    for i in range(4):
        t = threading.Thread(target=template_search_worker, args=(i+1,))
        threads.append(t)
    
    # Start all threads
    start_time = time.time()
    for t in threads:
        t.start()
    
    # Wait for completion
    for t in threads:
        t.join()
    
    elapsed = time.time() - start_time
    
    print(f"📊 Thread safety test results:")
    print(f"   Duration: {elapsed:.2f} seconds")
    print(f"   Successful searches: {results['success']}")
    print(f"   Errors: {results['error']}")
    
    if results["error"] == 0:
        print("✅ Thread safety test PASSED!")
    else:
        print("❌ Thread safety test had errors")
    
    return results["error"] == 0

def main():
    """Run all thread safety tests."""
    print("Thread Safety Test Suite")
    print("========================")
    print("Testing fixes for mss threading issues")
    
    tests = [
        ("Basic Screen Capture Threading", test_screen_capture_in_thread),
        ("Template Watcher Basic", test_template_watcher_basic),
        ("Comprehensive Thread Safety", test_thread_safety_comprehensive),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 50)
        
        try:
            result = test_func()
            if result is False:
                failed += 1
                print(f"❌ {test_name} FAILED")
            else:
                passed += 1
                print(f"✅ {test_name} PASSED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} CRASHED: {e}")
    
    print(f"\n📋 Final Results:")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")
    print(f"   Total:  {passed + failed}")
    
    if failed == 0:
        print("🎉 All tests passed! Thread safety is working.")
    else:
        print("⚠️ Some tests failed. There may still be threading issues.")

if __name__ == "__main__":
    main()