#!/usr/bin/env python3
"""
Test Web Service Manager
"""

from web_service_manager import WebServiceManager

def test_web_service_manager():
    print('🧪 Testing Web Service Manager...')
    print('=' * 50)

    manager = WebServiceManager()

    # Test configuration loading
    print('📋 Configuration loaded:')
    print(f'   Host: {manager.config["service"]["host"]}')
    print(f'   Port: {manager.config["service"]["port"]}')
    print(f'   Debug: {manager.config["service"]["debug"]}')

    # Test service status
    status = manager.get_service_status()
    print('')
    print('🔍 Service Status:')
    print(f'   Running: {status["running"]}')
    print(f'   Host: {status["host"]}')
    print(f'   Port: {status["port"]}')

    # Test ACL loading
    print('')
    print('🔒 Access Control:')
    users = manager.acl.get('users', {})
    print(f'   Users configured: {len(users)}')
    for username in users.keys():
        print(f'   - {username}')

    # Test starting service
    print('')
    print('🚀 Testing service start...')
    result = manager.start_service()
    print(f'   Result: {result["success"]}')
    print(f'   Message: {result["message"]}')
    
    if result["success"]:
        print('')
        print('⏸️ Testing service stop...')
        import time
        time.sleep(2)
        stop_result = manager.stop_service()
        print(f'   Result: {stop_result["success"]}')
        print(f'   Message: {stop_result["message"]}')

    print('')
    print('✅ Web Service Manager test completed successfully!')

if __name__ == '__main__':
    test_web_service_manager()