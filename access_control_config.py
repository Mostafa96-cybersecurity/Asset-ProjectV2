#!/usr/bin/env python3
"""
🔧 ACCESS CONTROL CONFIGURATION MANAGER
======================================
Tool to configure and test access control policies
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Import enhanced access control
try:
    from enhanced_access_control_system import access_control_manager
    ACCESS_CONTROL_AVAILABLE = True
except ImportError:
    ACCESS_CONTROL_AVAILABLE = False

def configure_access_control():
    """Interactive configuration of access control"""
    print("🔒 Access Control Configuration Manager")
    print("=" * 50)
    
    if not ACCESS_CONTROL_AVAILABLE:
        print("❌ Enhanced Access Control System is not available")
        print("Please ensure 'enhanced_access_control_system.py' is present")
        return False
    
    try:
        print("\\n📋 Current Configuration:")
        stats = access_control_manager.get_access_stats()
        
        print(f"Authentication: {'✅ Enabled' if stats['settings']['authentication_enabled'] else '❌ Disabled'}")
        print(f"IP Filtering: {'✅ Enabled' if stats['settings']['ip_filtering_enabled'] else '❌ Disabled'}")
        print(f"Rate Limiting: {'✅ Enabled' if stats['settings']['rate_limiting_enabled'] else '❌ Disabled'}")
        print(f"Active Sessions: {stats['active_sessions']}")
        print(f"Allowed IPs: {stats['allowed_ips_count']}")
        print(f"Blocked IPs: {stats['blocked_ips_count']}")
        print(f"Users: {stats['users_count']}")
        
        while True:
            print("\\n🔧 Configuration Options:")
            print("1. Enable/Disable Authentication")
            print("2. Enable/Disable IP Filtering")  
            print("3. Enable/Disable Rate Limiting")
            print("4. Add Allowed IP")
            print("5. Remove Allowed IP")
            print("6. Add Blocked IP")
            print("7. Remove Blocked IP")
            print("8. Add User")
            print("9. Remove User")
            print("10. Change User Password")
            print("11. Test IP Access")
            print("12. Test User Authentication")
            print("13. Show Access Logs")
            print("0. Exit")
            
            choice = input("\\nSelect option (0-13): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                toggle_authentication()
            elif choice == "2":
                toggle_ip_filtering()
            elif choice == "3":
                toggle_rate_limiting()
            elif choice == "4":
                add_allowed_ip()
            elif choice == "5":
                remove_allowed_ip()
            elif choice == "6":
                add_blocked_ip()
            elif choice == "7":
                remove_blocked_ip()
            elif choice == "8":
                add_user()
            elif choice == "9":
                remove_user()
            elif choice == "10":
                change_password()
            elif choice == "11":
                test_ip_access()
            elif choice == "12":
                test_authentication()
            elif choice == "13":
                show_access_logs()
            else:
                print("❌ Invalid option")
        
        print("\\n✅ Configuration completed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

def toggle_authentication():
    """Toggle authentication setting"""
    try:
        current = access_control_manager.settings['authentication_enabled']
        new_value = not current
        access_control_manager.settings['authentication_enabled'] = new_value
        access_control_manager.save_config()
        
        status = "enabled" if new_value else "disabled"
        print(f"✅ Authentication {status}")
        
    except Exception as e:
        print(f"❌ Failed to toggle authentication: {e}")

def toggle_ip_filtering():
    """Toggle IP filtering setting"""
    try:
        current = access_control_manager.settings['ip_filtering_enabled']
        new_value = not current
        access_control_manager.settings['ip_filtering_enabled'] = new_value
        access_control_manager.save_config()
        
        status = "enabled" if new_value else "disabled"
        print(f"✅ IP filtering {status}")
        
    except Exception as e:
        print(f"❌ Failed to toggle IP filtering: {e}")

def toggle_rate_limiting():
    """Toggle rate limiting setting"""
    try:
        current = access_control_manager.settings['rate_limiting_enabled']
        new_value = not current
        access_control_manager.settings['rate_limiting_enabled'] = new_value
        access_control_manager.save_config()
        
        status = "enabled" if new_value else "disabled"
        print(f"✅ Rate limiting {status}")
        
    except Exception as e:
        print(f"❌ Failed to toggle rate limiting: {e}")

def add_allowed_ip():
    """Add IP to allowed list"""
    try:
        ip = input("Enter IP address to allow: ").strip()
        if access_control_manager.add_allowed_ip(ip):
            print(f"✅ Added {ip} to allowed IPs")
        else:
            print(f"❌ Failed to add {ip} (invalid IP format)")
            
    except Exception as e:
        print(f"❌ Failed to add allowed IP: {e}")

def remove_allowed_ip():
    """Remove IP from allowed list"""
    try:
        # Show current allowed IPs
        print("Current allowed IPs:")
        for i, ip in enumerate(access_control_manager.allowed_ips, 1):
            print(f"{i}. {ip}")
        
        ip = input("Enter IP address to remove: ").strip()
        if access_control_manager.remove_allowed_ip(ip):
            print(f"✅ Removed {ip} from allowed IPs")
        else:
            print(f"❌ IP {ip} not found in allowed list")
            
    except Exception as e:
        print(f"❌ Failed to remove allowed IP: {e}")

def add_blocked_ip():
    """Add IP to blocked list"""
    try:
        ip = input("Enter IP address to block: ").strip()
        if access_control_manager.add_blocked_ip(ip):
            print(f"✅ Added {ip} to blocked IPs")
        else:
            print(f"❌ Failed to add {ip} (invalid IP format)")
            
    except Exception as e:
        print(f"❌ Failed to add blocked IP: {e}")

def remove_blocked_ip():
    """Remove IP from blocked list"""
    try:
        # Show current blocked IPs
        print("Current blocked IPs:")
        for i, ip in enumerate(access_control_manager.blocked_ips, 1):
            print(f"{i}. {ip}")
        
        ip = input("Enter IP address to unblock: ").strip()
        if access_control_manager.remove_blocked_ip(ip):
            print(f"✅ Removed {ip} from blocked IPs")
        else:
            print(f"❌ IP {ip} not found in blocked list")
            
    except Exception as e:
        print(f"❌ Failed to remove blocked IP: {e}")

def add_user():
    """Add new user"""
    try:
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        
        print("Select role:")
        print("1. User (read-only)")
        print("2. Editor (read/write)")
        print("3. Admin (full access)")
        
        role_choice = input("Select role (1-3): ").strip()
        role_map = {'1': 'user', '2': 'editor', '3': 'admin'}
        role = role_map.get(role_choice, 'user')
        
        if access_control_manager.add_user(username, password, role):
            print(f"✅ Added user {username} with role {role}")
        else:
            print(f"❌ Failed to add user (username may already exist)")
            
    except Exception as e:
        print(f"❌ Failed to add user: {e}")

def remove_user():
    """Remove user"""
    try:
        # Show current users
        print("Current users:")
        for i, username in enumerate(access_control_manager.users.keys(), 1):
            role = access_control_manager.users[username]['role']
            print(f"{i}. {username} ({role})")
        
        username = input("Enter username to remove: ").strip()
        if access_control_manager.remove_user(username):
            print(f"✅ Removed user {username}")
        else:
            print(f"❌ User {username} not found")
            
    except Exception as e:
        print(f"❌ Failed to remove user: {e}")

def change_password():
    """Change user password"""
    try:
        # Show current users
        print("Users:")
        for username in access_control_manager.users.keys():
            print(f"- {username}")
        
        username = input("Enter username: ").strip()
        password = input("Enter new password: ").strip()
        
        if access_control_manager.change_password(username, password):
            print(f"✅ Changed password for user {username}")
        else:
            print(f"❌ User {username} not found")
            
    except Exception as e:
        print(f"❌ Failed to change password: {e}")

def test_ip_access():
    """Test IP access"""
    try:
        ip = input("Enter IP address to test: ").strip()
        allowed, reason = access_control_manager.check_ip_access(ip)
        
        status = "✅ ALLOWED" if allowed else "❌ BLOCKED"
        print(f"{status}: {ip} - {reason}")
        
    except Exception as e:
        print(f"❌ Failed to test IP access: {e}")

def test_authentication():
    """Test user authentication"""
    try:
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        
        success, message, user_info = access_control_manager.authenticate_user(username, password)
        
        if success:
            print(f"✅ AUTHENTICATION SUCCESS: {message}")
            print(f"User Info: {user_info}")
        else:
            print(f"❌ AUTHENTICATION FAILED: {message}")
            
    except Exception as e:
        print(f"❌ Failed to test authentication: {e}")

def show_access_logs():
    """Show recent access logs"""
    try:
        log_file = Path("logs/access_control.log")
        
        if not log_file.exists():
            print("📝 No access logs found")
            return
        
        print("📝 Recent Access Logs (last 20 entries):")
        print("-" * 80)
        
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines[-20:]:
            try:
                log_entry = json.loads(line.strip())
                timestamp = log_entry['timestamp']
                ip = log_entry['client_ip']
                endpoint = log_entry['endpoint']
                result = log_entry['result']
                username = log_entry.get('username', 'Anonymous')
                
                print(f"{timestamp} | {ip} | {username} | {endpoint} | {result}")
                
            except:
                continue
                
    except Exception as e:
        print(f"❌ Failed to show access logs: {e}")

def quick_setup():
    """Quick setup with reasonable defaults"""
    print("🚀 Quick Setup - Enhanced Access Control")
    print("=" * 50)
    
    if not ACCESS_CONTROL_AVAILABLE:
        print("❌ Enhanced Access Control System is not available")
        return False
    
    try:
        # Enable all security features
        access_control_manager.settings.update({
            'authentication_enabled': True,
            'ip_filtering_enabled': True,
            'rate_limiting_enabled': True,
            'session_timeout_minutes': 60,
            'max_login_attempts': 5,
            'lockout_duration_minutes': 30,
            'log_all_requests': True
        })
        
        # Add current machine IP to allowed list
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            access_control_manager.add_allowed_ip(local_ip)
            print(f"✅ Added local IP {local_ip} to allowed list")
        except:
            pass
        
        # Save configuration
        access_control_manager.save_config()
        
        print("✅ Quick setup completed!")
        print("\\n📋 Security Features Enabled:")
        print("- 🔐 Authentication required")
        print("- 🛡️ IP filtering active")
        print("- ⏱️ Rate limiting enabled")
        print("- 📝 Full request logging")
        
        print("\\n👤 Default Users:")
        print("- Username: admin, Password: admin123 (Admin)")
        print("- Username: user, Password: user123 (Read-only)")
        
        print("\\n🌐 Web Service URL: http://localhost:8080")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick setup failed: {e}")
        return False

def main():
    """Main function"""
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "--quick":
        return 0 if quick_setup() else 1
    else:
        return 0 if configure_access_control() else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())