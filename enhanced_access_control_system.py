#!/usr/bin/env python3
"""
🔒 ENHANCED ACCESS CONTROL SYSTEM
=================================
Comprehensive access control for web services with authentication,
IP filtering, and centralized policy management.
"""

import json
import hashlib
import ipaddress
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple, Any
from pathlib import Path
import threading
import time
import sqlite3
from functools import wraps

# Import comprehensive logging
try:
    from comprehensive_logging_system import log_web_service, start_job, complete_job
except ImportError:
    def log_web_service(level, message, **kwargs):
        print(f"[ACCESS_CONTROL] {level}: {message}")
    def start_job(job_id, feature, description):
        print(f"Starting job: {description}")
    def complete_job(job_id, success, message=""):
        print(f"Job completed: {success}")

class AccessControlManager:
    """Comprehensive access control manager for web services"""
    
    def __init__(self):
        self.config_file = Path("access_control_enhanced.json")
        self.access_log_file = Path("logs/access_control.log")
        self.session_file = Path("logs/active_sessions.json")
        
        # Create directories
        self.access_log_file.parent.mkdir(exist_ok=True)
        
        # Access control settings
        self.settings = {
            'authentication_enabled': True,
            'ip_filtering_enabled': True,
            'rate_limiting_enabled': True,
            'session_timeout_minutes': 60,
            'max_login_attempts': 5,
            'lockout_duration_minutes': 30,
            'require_https': False,
            'log_all_requests': True
        }
        
        # Network access rules
        self.allowed_networks = [
            '127.0.0.0/8',    # Localhost
            '192.168.0.0/16', # Private Class C
            '10.0.0.0/8',     # Private Class A
            '172.16.0.0/12'   # Private Class B
        ]
        
        self.blocked_ips = set()
        self.allowed_ips = {'127.0.0.1', '::1'}  # Always allow localhost
        
        # Authentication
        self.users = {
            'admin': {
                'password_hash': self._hash_password('admin123'),
                'role': 'admin',
                'permissions': ['read', 'write', 'admin'],
                'created': datetime.now().isoformat(),
                'last_login': None
            },
            'user': {
                'password_hash': self._hash_password('user123'),
                'role': 'user',
                'permissions': ['read'],
                'created': datetime.now().isoformat(),
                'last_login': None
            }
        }
        
        # Session management
        self.active_sessions = {}
        self.failed_attempts = {}
        self.rate_limits = {}
        
        # Load configuration
        self.load_config()
        
        # Start cleanup thread
        self.start_cleanup_thread()
        
        log_web_service('INFO', '🔒 Enhanced Access Control Manager initialized')
        
    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = "asset_management_salt"
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
        
    def load_config(self):
        """Load access control configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    
                self.settings.update(data.get('settings', {}))
                self.allowed_networks = data.get('allowed_networks', self.allowed_networks)
                self.blocked_ips = set(data.get('blocked_ips', []))
                self.allowed_ips.update(data.get('allowed_ips', []))
                self.users.update(data.get('users', {}))
                
                log_web_service('INFO', 'Access control configuration loaded')
            else:
                self.save_config()
                log_web_service('INFO', 'Created default access control configuration')
                
        except Exception as e:
            log_web_service('ERROR', f'Failed to load access control config: {e}')
            
    def save_config(self):
        """Save access control configuration"""
        try:
            data = {
                'settings': self.settings,
                'allowed_networks': self.allowed_networks,
                'blocked_ips': list(self.blocked_ips),
                'allowed_ips': list(self.allowed_ips),
                'users': self.users,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            log_web_service('DEBUG', 'Access control configuration saved')
            
        except Exception as e:
            log_web_service('ERROR', f'Failed to save access control config: {e}')
            
    def check_ip_access(self, client_ip: str) -> Tuple[bool, str]:
        """Check if IP address has access"""
        try:
            # Always allow localhost
            if client_ip in ['127.0.0.1', '::1', 'localhost']:
                return True, "Localhost access allowed"
                
            # Check if IP is explicitly blocked
            if client_ip in self.blocked_ips:
                return False, "IP explicitly blocked"
                
            # Check if IP is explicitly allowed
            if client_ip in self.allowed_ips:
                return True, "IP explicitly allowed"
                
            # Check if IP filtering is disabled
            if not self.settings.get('ip_filtering_enabled', True):
                return True, "IP filtering disabled"
                
            # Check against allowed networks
            try:
                client_addr = ipaddress.ip_address(client_ip)
                
                for network_str in self.allowed_networks:
                    network = ipaddress.ip_network(network_str, strict=False)
                    if client_addr in network:
                        return True, f"IP in allowed network: {network_str}"
                        
                return False, "IP not in any allowed network"
                
            except ValueError:
                return False, "Invalid IP address format"
                
        except Exception as e:
            log_web_service('ERROR', f'Error checking IP access: {e}')
            return False, f"Access check error: {e}"
            
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str, Dict]:
        """Authenticate user credentials"""
        try:
            # Check if authentication is enabled
            if not self.settings.get('authentication_enabled', True):
                return True, "Authentication disabled", {'username': username, 'role': 'guest'}
                
            # Check failed attempts
            if self._is_locked_out(username):
                return False, "Account temporarily locked due to failed attempts", {}
                
            # Validate credentials
            if username not in self.users:
                self._log_failed_attempt(username)
                return False, "Invalid username", {}
                
            user_data = self.users[username]
            password_hash = self._hash_password(password)
            
            if password_hash != user_data['password_hash']:
                self._log_failed_attempt(username)
                return False, "Invalid password", {}
                
            # Reset failed attempts on successful login
            if username in self.failed_attempts:
                del self.failed_attempts[username]
                
            # Update last login
            user_data['last_login'] = datetime.now().isoformat()
            self.save_config()
            
            return True, "Authentication successful", {
                'username': username,
                'role': user_data['role'],
                'permissions': user_data['permissions']
            }
            
        except Exception as e:
            log_web_service('ERROR', f'Authentication error: {e}')
            return False, f"Authentication error: {e}", {}
            
    def create_session(self, user_info: Dict, client_ip: str) -> str:
        """Create authenticated session"""
        try:
            session_id = hashlib.sha256(f"{user_info['username']}{client_ip}{time.time()}".encode()).hexdigest()
            
            session_data = {
                'user_info': user_info,
                'client_ip': client_ip,
                'created': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat(),
                'expires': (datetime.now() + timedelta(minutes=self.settings['session_timeout_minutes'])).isoformat()
            }
            
            self.active_sessions[session_id] = session_data
            self._save_sessions()
            
            log_web_service('INFO', f'Session created for {user_info["username"]} from {client_ip}')
            return session_id
            
        except Exception as e:
            log_web_service('ERROR', f'Error creating session: {e}')
            return ""
            
    def validate_session(self, session_id: str, client_ip: str) -> Tuple[bool, Dict]:
        """Validate session and return user info"""
        try:
            if session_id not in self.active_sessions:
                return False, {}
                
            session_data = self.active_sessions[session_id]
            
            # Check if session expired
            expires = datetime.fromisoformat(session_data['expires'])
            if datetime.now() > expires:
                del self.active_sessions[session_id]
                self._save_sessions()
                return False, {}
                
            # Check if IP matches
            if session_data['client_ip'] != client_ip:
                log_web_service('WARNING', f'Session IP mismatch: expected {session_data["client_ip"]}, got {client_ip}')
                return False, {}
                
            # Update last activity and extend session
            session_data['last_activity'] = datetime.now().isoformat()
            session_data['expires'] = (datetime.now() + timedelta(minutes=self.settings['session_timeout_minutes'])).isoformat()
            
            return True, session_data['user_info']
            
        except Exception as e:
            log_web_service('ERROR', f'Error validating session: {e}')
            return False, {}
            
    def revoke_session(self, session_id: str):
        """Revoke a session"""
        try:
            if session_id in self.active_sessions:
                user_info = self.active_sessions[session_id]['user_info']
                del self.active_sessions[session_id]
                self._save_sessions()
                log_web_service('INFO', f'Session revoked for {user_info["username"]}')
                
        except Exception as e:
            log_web_service('ERROR', f'Error revoking session: {e}')
            
    def check_rate_limit(self, client_ip: str, endpoint: str) -> Tuple[bool, str]:
        """Check rate limiting for client IP and endpoint"""
        try:
            if not self.settings.get('rate_limiting_enabled', True):
                return True, "Rate limiting disabled"
                
            current_time = time.time()
            rate_key = f"{client_ip}:{endpoint}"
            
            if rate_key not in self.rate_limits:
                self.rate_limits[rate_key] = {'count': 1, 'window_start': current_time}
                return True, "Within rate limit"
                
            rate_data = self.rate_limits[rate_key]
            
            # Reset window if more than 1 minute has passed
            if current_time - rate_data['window_start'] > 60:
                rate_data['count'] = 1
                rate_data['window_start'] = current_time
                return True, "Rate limit window reset"
                
            # Check if limit exceeded (60 requests per minute)
            if rate_data['count'] >= 60:
                return False, "Rate limit exceeded (60 requests/minute)"
                
            rate_data['count'] += 1
            return True, "Within rate limit"
            
        except Exception as e:
            log_web_service('ERROR', f'Error checking rate limit: {e}')
            return True, "Rate limit check error - allowing"
            
    def log_access_attempt(self, client_ip: str, endpoint: str, method: str, 
                          user_agent: str, result: str, user_info: Dict = None):
        """Log access attempt"""
        try:
            timestamp = datetime.now().isoformat()
            
            log_entry = {
                'timestamp': timestamp,
                'client_ip': client_ip,
                'endpoint': endpoint,
                'method': method,
                'user_agent': user_agent[:100] if user_agent else 'Unknown',
                'result': result,
                'username': user_info.get('username') if user_info else 'Anonymous'
            }
            
            # Log to file
            if self.settings.get('log_all_requests', True):
                with open(self.access_log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry) + '\\n')
                    
            # Log to system
            log_web_service('INFO', f'ACCESS: {client_ip} -> {method} {endpoint} | {result}')
            
        except Exception as e:
            log_web_service('ERROR', f'Error logging access: {e}')
            
    def add_user(self, username: str, password: str, role: str = 'user') -> bool:
        """Add new user"""
        try:
            if username in self.users:
                return False
                
            permissions = ['read']
            if role == 'admin':
                permissions = ['read', 'write', 'admin']
            elif role == 'editor':
                permissions = ['read', 'write']
                
            self.users[username] = {
                'password_hash': self._hash_password(password),
                'role': role,
                'permissions': permissions,
                'created': datetime.now().isoformat(),
                'last_login': None
            }
            
            self.save_config()
            log_web_service('INFO', f'User added: {username} with role {role}')
            return True
            
        except Exception as e:
            log_web_service('ERROR', f'Error adding user: {e}')
            return False
            
    def remove_user(self, username: str) -> bool:
        """Remove user"""
        try:
            if username not in self.users:
                return False
                
            del self.users[username]
            self.save_config()
            log_web_service('INFO', f'User removed: {username}')
            return True
            
        except Exception as e:
            log_web_service('ERROR', f'Error removing user: {e}')
            return False
            
    def change_password(self, username: str, new_password: str) -> bool:
        """Change user password"""
        try:
            if username not in self.users:
                return False
                
            self.users[username]['password_hash'] = self._hash_password(new_password)
            self.save_config()
            log_web_service('INFO', f'Password changed for user: {username}')
            return True
            
        except Exception as e:
            log_web_service('ERROR', f'Error changing password: {e}')
            return False
            
    def add_allowed_ip(self, ip_address: str) -> bool:
        """Add IP to allowed list"""
        try:
            # Validate IP
            ipaddress.ip_address(ip_address)
            self.allowed_ips.add(ip_address)
            self.save_config()
            log_web_service('INFO', f'Added allowed IP: {ip_address}')
            return True
            
        except Exception as e:
            log_web_service('ERROR', f'Error adding allowed IP: {e}')
            return False
            
    def remove_allowed_ip(self, ip_address: str) -> bool:
        """Remove IP from allowed list"""
        try:
            if ip_address in self.allowed_ips:
                self.allowed_ips.remove(ip_address)
                self.save_config()
                log_web_service('INFO', f'Removed allowed IP: {ip_address}')
                return True
            return False
            
        except Exception as e:
            log_web_service('ERROR', f'Error removing allowed IP: {e}')
            return False
            
    def add_blocked_ip(self, ip_address: str) -> bool:
        """Add IP to blocked list"""
        try:
            # Validate IP
            ipaddress.ip_address(ip_address)
            self.blocked_ips.add(ip_address)
            self.save_config()
            log_web_service('INFO', f'Added blocked IP: {ip_address}')
            return True
            
        except Exception as e:
            log_web_service('ERROR', f'Error adding blocked IP: {e}')
            return False
            
    def remove_blocked_ip(self, ip_address: str) -> bool:
        """Remove IP from blocked list"""
        try:
            if ip_address in self.blocked_ips:
                self.blocked_ips.remove(ip_address)
                self.save_config()
                log_web_service('INFO', f'Removed blocked IP: {ip_address}')
                return True
            return False
            
        except Exception as e:
            log_web_service('ERROR', f'Error removing blocked IP: {e}')
            return False
            
    def get_access_stats(self) -> Dict[str, Any]:
        """Get access control statistics"""
        try:
            return {
                'settings': self.settings,
                'active_sessions': len(self.active_sessions),
                'allowed_ips_count': len(self.allowed_ips),
                'blocked_ips_count': len(self.blocked_ips),
                'allowed_networks_count': len(self.allowed_networks),
                'users_count': len(self.users),
                'failed_attempts_count': len(self.failed_attempts),
                'rate_limits_active': len(self.rate_limits)
            }
            
        except Exception as e:
            log_web_service('ERROR', f'Error getting access stats: {e}')
            return {}
            
    def _is_locked_out(self, username: str) -> bool:
        """Check if user is locked out due to failed attempts"""
        if username not in self.failed_attempts:
            return False
            
        attempts_data = self.failed_attempts[username]
        
        # Check if lockout period has expired
        lockout_end = datetime.fromisoformat(attempts_data['lockout_until'])
        if datetime.now() > lockout_end:
            del self.failed_attempts[username]
            return False
            
        return attempts_data['count'] >= self.settings['max_login_attempts']
        
    def _log_failed_attempt(self, username: str):
        """Log failed login attempt"""
        current_time = datetime.now()
        
        if username not in self.failed_attempts:
            self.failed_attempts[username] = {
                'count': 1,
                'first_attempt': current_time.isoformat(),
                'lockout_until': (current_time + timedelta(minutes=self.settings['lockout_duration_minutes'])).isoformat()
            }
        else:
            self.failed_attempts[username]['count'] += 1
            
        log_web_service('WARNING', f'Failed login attempt for user: {username}')
        
    def _save_sessions(self):
        """Save active sessions to file"""
        try:
            with open(self.session_file, 'w') as f:
                json.dump(self.active_sessions, f, indent=2)
        except Exception as e:
            log_web_service('ERROR', f'Error saving sessions: {e}')
            
    def _load_sessions(self):
        """Load active sessions from file"""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    self.active_sessions = json.load(f)
        except Exception as e:
            log_web_service('ERROR', f'Error loading sessions: {e}')
            
    def start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_loop():
            while True:
                try:
                    # Clean expired sessions
                    current_time = datetime.now()
                    expired_sessions = []
                    
                    for session_id, session_data in self.active_sessions.items():
                        expires = datetime.fromisoformat(session_data['expires'])
                        if current_time > expires:
                            expired_sessions.append(session_id)
                            
                    for session_id in expired_sessions:
                        del self.active_sessions[session_id]
                        
                    if expired_sessions:
                        self._save_sessions()
                        log_web_service('DEBUG', f'Cleaned {len(expired_sessions)} expired sessions')
                        
                    # Clean old rate limit entries
                    current_timestamp = time.time()
                    old_entries = []
                    
                    for rate_key, rate_data in self.rate_limits.items():
                        if current_timestamp - rate_data['window_start'] > 300:  # 5 minutes
                            old_entries.append(rate_key)
                            
                    for rate_key in old_entries:
                        del self.rate_limits[rate_key]
                        
                    # Sleep for 5 minutes
                    time.sleep(300)
                    
                except Exception as e:
                    log_web_service('ERROR', f'Cleanup thread error: {e}')
                    time.sleep(60)
                    
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
        log_web_service('INFO', 'Access control cleanup thread started')

# Global instance
access_control_manager = AccessControlManager()

# Convenience functions
def check_ip_access(client_ip: str):
    """Check IP access"""
    return access_control_manager.check_ip_access(client_ip)

def authenticate_user(username: str, password: str):
    """Authenticate user"""
    return access_control_manager.authenticate_user(username, password)

def create_session(user_info: Dict, client_ip: str):
    """Create session"""
    return access_control_manager.create_session(user_info, client_ip)

def validate_session(session_id: str, client_ip: str):
    """Validate session"""
    return access_control_manager.validate_session(session_id, client_ip)

def check_rate_limit(client_ip: str, endpoint: str):
    """Check rate limit"""
    return access_control_manager.check_rate_limit(client_ip, endpoint)

def log_access_attempt(client_ip: str, endpoint: str, method: str, user_agent: str, result: str, user_info: Dict = None):
    """Log access attempt"""
    return access_control_manager.log_access_attempt(client_ip, endpoint, method, user_agent, result, user_info)

if __name__ == "__main__":
    # Test the access control system
    print("[TESTING] Enhanced Access Control System...")
    
    acm = AccessControlManager()
    
    # Test IP access
    ip_allowed, reason = acm.check_ip_access('127.0.0.1')
    print(f"IP 127.0.0.1 access: {ip_allowed} - {reason}")
    
    # Test authentication
    auth_success, message, user_info = acm.authenticate_user('admin', 'admin123')
    print(f"Admin login: {auth_success} - {message}")
    
    if auth_success:
        session_id = acm.create_session(user_info, '127.0.0.1')
        print(f"Session created: {session_id[:16]}...")
        
        valid, session_user = acm.validate_session(session_id, '127.0.0.1')
        print(f"Session valid: {valid} - User: {session_user.get('username')}")
    
    # Test rate limiting
    rate_ok, rate_reason = acm.check_rate_limit('127.0.0.1', '/api/test')
    print(f"Rate limit check: {rate_ok} - {rate_reason}")
    
    # Show stats
    stats = acm.get_access_stats()
    print(f"\\nAccess Control Stats: {stats}")
    
    print("\\n[SUCCESS] Enhanced Access Control System Ready!")