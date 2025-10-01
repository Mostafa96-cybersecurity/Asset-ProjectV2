import sys
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def quick_test():
    """Quick test of the fixed collector"""
    print("🧪 QUICK TEST OF FIXED COLLECTOR")
    print("=" * 50)
    
    try:
        from ultra_fast_collector import _port_based_os_detection, _collect_windows_standalone
        
        # Test 1: Port-based OS detection
        print("🔍 Testing port-based OS detection for 10.0.21.47...")
        result = _port_based_os_detection("10.0.21.47")
        print(f"   OS Family: {result.get('os_family', 'Unknown')}")
        print(f"   Device Type: {result.get('device_type', 'Unknown')}")
        print(f"   Confidence: {result.get('confidence', '0')}%")
        
        # Test 2: Check if it detects Windows
        if result.get('os_family') == 'Windows':
            print("✅ Windows detected! This should work with WMI")
            
            # Test 3: Quick WMI test with dummy credentials (should fail but not timeout)
            print("\n🔧 Testing WMI connection (should fail auth but not timeout)...")
            wmi_result = _collect_windows_standalone("10.0.21.47", "test", "test")
            
            if wmi_result:
                status = wmi_result.get('wmi_collection_status', 'Unknown')
                print(f"   WMI Status: {status}")
                
                if 'CoInitialize' in str(status):
                    print("❌ COM error still present")
                else:
                    print("✅ COM error fixed! (now getting proper auth errors)")
            else:
                print("⚠️ No WMI result returned")
        else:
            print(f"⚠️ Detected as {result.get('os_family', 'Unknown')}, not Windows")
        
        print("\n🎯 RECOMMENDATION:")
        print("   1. Close Desktop APP completely")
        print("   2. Restart Desktop APP")  
        print("   3. Try collection again with real credentials")
        print("   4. Should now complete without timeout")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test()