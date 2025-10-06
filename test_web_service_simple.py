"""Simple test for web service connectivity issues"""
import requests
import os

def test_web_service_connection():
    """Test direct connection to web service"""
    print("Testing web service connection...")
    
    try:
        response = requests.get("http://localhost:8080", timeout=10)
        print(f"Response code: {response.status_code}")
        print(f"Content length: {len(response.content)}")
        if response.content:
            print("Service is responding with content")
            return True
        else:
            print("Service is responding but with empty content")
            return False
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

def check_fixed_dashboard():
    """Check if fixed_dashboard.py exists"""
    if os.path.exists('fixed_dashboard.py'):
        print("fixed_dashboard.py found")
        return True
    else:
        print("fixed_dashboard.py not found")
        return False

if __name__ == "__main__":
    print("Simple Web Service Test")
    print("=" * 30)
    
    check_fixed_dashboard()
    test_web_service_connection()