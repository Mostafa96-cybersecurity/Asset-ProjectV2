#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Service Management System
Advanced Web Service Controller with ACL, Security, and Monitoring
=================================================================
Complete web service management with professional features
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import psutil

class WebServiceManager:
    """Comprehensive Web Service Management System"""
    
    def __init__(self):
        self.config_file = "web_service_config.json"
        self.log_file = "web_service.log"
        self.acl_file = "web_service_acl.json"
        self.service_process = None
        self.service_pid = None
        self.startup_time = None
        self.logger = self._setup_logging()
        
        # Default configuration
        self.default_config = {
            "service": {
                "host": "127.0.0.1",
                "port": 5000,
                "debug": False,
                "auto_start": False,
                "max_connections": 100,
                "timeout": 30,
                "ssl_enabled": False,
                "ssl_cert": "",
                "ssl_key": ""
            },
            "security": {
                "auth_required": True,
                "session_timeout": 3600,
                "max_login_attempts": 5,
                "lockout_duration": 300,
                "rate_limiting": True,
                "max_requests_per_minute": 60
            },
            "monitoring": {
                "log_level": "INFO",
                "log_rotation": True,
                "max_log_size": 10485760,  # 10MB
                "keep_logs": 30,
                "performance_monitoring": True,
                "health_check_interval": 60
            }
        }
        
        self.load_config()
        self.load_acl()
        
    def _setup_logging(self):
        """Setup comprehensive logging system"""
        logger = logging.getLogger('WebServiceManager')
        logger.setLevel(logging.INFO)
        
        # Create file handler
        fh = logging.FileHandler(self.log_file, encoding='utf-8')
        fh.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        
        logger.addHandler(fh)
        return logger
        
    def load_config(self):
        """Load web service configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    
                # Merge with defaults for missing keys
                for section, settings in self.default_config.items():
                    if section not in self.config:
                        self.config[section] = settings
                    else:
                        for key, value in settings.items():
                            if key not in self.config[section]:
                                self.config[section][key] = value
            else:
                self.config = self.default_config.copy()
                self.save_config()
                
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            self.config = self.default_config.copy()
            
    def save_config(self):
        """Save web service configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            self.logger.info("Configuration saved successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            return False
            
    def load_acl(self):
        """Load Access Control List"""
        try:
            if os.path.exists(self.acl_file):
                with open(self.acl_file, 'r', encoding='utf-8') as f:
                    self.acl = json.load(f)
            else:
                self.acl = {
                    "users": {
                        "admin": {
                            "password_hash": "admin123",  # Should be hashed in production
                            "role": "administrator",
                            "permissions": ["read", "write", "admin"],
                            "allowed_ips": ["*"],
                            "created": datetime.now().isoformat(),
                            "last_login": None,
                            "failed_attempts": 0,
                            "locked_until": None
                        }
                    },
                    "ip_restrictions": {
                        "enabled": False,
                        "allowed_ips": ["127.0.0.1", "::1"],
                        "blocked_ips": [],
                        "whitelist_mode": True
                    },
                    "rate_limiting": {
                        "enabled": True,
                        "requests_per_minute": 60,
                        "burst_limit": 100
                    }
                }
                self.save_acl()
        except Exception as e:
            self.logger.error(f"Failed to load ACL: {e}")
            
    def save_acl(self):
        """Save Access Control List"""
        try:
            with open(self.acl_file, 'w', encoding='utf-8') as f:
                json.dump(self.acl, f, indent=4, ensure_ascii=False)
            self.logger.info("ACL saved successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save ACL: {e}")
            return False
            
    def start_service(self) -> Dict[str, Any]:
        """Start the web service"""
        try:
            if self.is_service_running():
                return {
                    "success": False,
                    "message": "Service is already running",
                    "pid": self.service_pid
                }
                
            # Find the web service script
            service_script = self._find_service_script()
            if not service_script:
                return {
                    "success": False,
                    "message": "Web service script not found"
                }
                
            # Start the service
            python_exe = sys.executable
            cmd = [python_exe, service_script]
            
            # Add environment variables
            env = os.environ.copy()
            env['WEB_SERVICE_CONFIG'] = self.config_file
            env['WEB_SERVICE_HOST'] = self.config['service']['host']
            env['WEB_SERVICE_PORT'] = str(self.config['service']['port'])
            
            self.service_process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            self.service_pid = self.service_process.pid
            self.startup_time = datetime.now()
            
            # Wait a moment to check if service started successfully
            time.sleep(2)
            
            if self.service_process.poll() is None:
                self.logger.info(f"Web service started successfully with PID {self.service_pid}")
                return {
                    "success": True,
                    "message": "Service started successfully",
                    "pid": self.service_pid,
                    "host": self.config['service']['host'],
                    "port": self.config['service']['port']
                }
            else:
                stdout, stderr = self.service_process.communicate()
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                self.logger.error(f"Service failed to start: {error_msg}")
                return {
                    "success": False,
                    "message": f"Service failed to start: {error_msg}"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to start service: {e}")
            return {
                "success": False,
                "message": f"Failed to start service: {str(e)}"
            }
            
    def stop_service(self) -> Dict[str, Any]:
        """Stop the web service"""
        try:
            if not self.is_service_running():
                return {
                    "success": False,
                    "message": "Service is not running"
                }
                
            # Try graceful shutdown first
            if self.service_process:
                self.service_process.terminate()
                
                # Wait for graceful shutdown
                for _ in range(10):
                    if self.service_process.poll() is not None:
                        break
                    time.sleep(0.5)
                    
                # Force kill if still running
                if self.service_process.poll() is None:
                    self.service_process.kill()
                    
            # Also try to kill by PID if we have it
            if self.service_pid:
                try:
                    if psutil.pid_exists(self.service_pid):
                        proc = psutil.Process(self.service_pid)
                        proc.terminate()
                        proc.wait(timeout=5)
                except:
                    pass
                    
            self.service_process = None
            self.service_pid = None
            self.startup_time = None
            
            self.logger.info("Web service stopped successfully")
            return {
                "success": True,
                "message": "Service stopped successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to stop service: {e}")
            return {
                "success": False,
                "message": f"Failed to stop service: {str(e)}"
            }
            
    def restart_service(self) -> Dict[str, Any]:
        """Restart the web service"""
        try:
            self.logger.info("Restarting web service...")
            
            # Stop service
            stop_result = self.stop_service()
            if not stop_result.get("success", False) and "not running" not in stop_result.get("message", ""):
                return stop_result
                
            # Wait a moment
            time.sleep(1)
            
            # Start service
            start_result = self.start_service()
            
            if start_result.get("success", False):
                self.logger.info("Web service restarted successfully")
                return {
                    "success": True,
                    "message": "Service restarted successfully",
                    "pid": start_result.get("pid"),
                    "host": start_result.get("host"),
                    "port": start_result.get("port")
                }
            else:
                return start_result
                
        except Exception as e:
            self.logger.error(f"Failed to restart service: {e}")
            return {
                "success": False,
                "message": f"Failed to restart service: {str(e)}"
            }
            
    def is_service_running(self) -> bool:
        """Check if the web service is running"""
        try:
            # Check process object
            if self.service_process and self.service_process.poll() is None:
                return True
                
            # Check by PID
            if self.service_pid and psutil.pid_exists(self.service_pid):
                try:
                    proc = psutil.Process(self.service_pid)
                    if proc.is_running():
                        return True
                except:
                    pass
                    
            # Check by port
            for conn in psutil.net_connections():
                if (conn.laddr.port == self.config['service']['port'] and 
                    conn.status == psutil.CONN_LISTEN):
                    return True
                    
            return False
            
        except Exception:
            return False
            
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        try:
            is_running = self.is_service_running()
            
            status = {
                "running": is_running,
                "pid": self.service_pid if is_running else None,
                "host": self.config['service']['host'],
                "port": self.config['service']['port'],
                "startup_time": self.startup_time.isoformat() if self.startup_time else None,
                "uptime": None,
                "memory_usage": None,
                "cpu_usage": None,
                "connections": 0,
                "total_requests": 0,
                "last_activity": None
            }
            
            if is_running and self.service_pid:
                try:
                    proc = psutil.Process(self.service_pid)
                    status["memory_usage"] = proc.memory_info().rss / 1024 / 1024  # MB
                    status["cpu_usage"] = proc.cpu_percent()
                    
                    if self.startup_time:
                        uptime = datetime.now() - self.startup_time
                        status["uptime"] = str(uptime).split('.')[0]  # Remove microseconds
                        
                except Exception:
                    pass
                    
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get service status: {e}")
            return {"running": False, "error": str(e)}
            
    def clear_cache(self) -> Dict[str, Any]:
        """Clear service cache"""
        try:
            # Clear session cache
            session_files = []
            cache_dirs = ['__pycache__', '.cache', 'cache']
            
            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir):
                    import shutil
                    shutil.rmtree(cache_dir)
                    session_files.append(cache_dir)
                    
            # Clear Python cache files
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if file.endswith('.pyc') or file.endswith('.pyo'):
                        try:
                            os.remove(os.path.join(root, file))
                            session_files.append(file)
                        except:
                            pass
                            
            self.logger.info(f"Cache cleared: {len(session_files)} items removed")
            
            return {
                "success": True,
                "message": "Cache cleared successfully",
                "items_removed": len(session_files)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
            return {
                "success": False,
                "message": f"Failed to clear cache: {str(e)}"
            }
            
    def clear_sessions(self) -> Dict[str, Any]:
        """Clear active sessions"""
        try:
            # Reset failed login attempts
            for user in self.acl.get("users", {}).values():
                user["failed_attempts"] = 0
                user["locked_until"] = None
                
            self.save_acl()
            
            self.logger.info("All sessions cleared")
            
            return {
                "success": True,
                "message": "All sessions cleared successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to clear sessions: {e}")
            return {
                "success": False,
                "message": f"Failed to clear sessions: {str(e)}"
            }
            
    def clear_connections(self) -> Dict[str, Any]:
        """Clear/reset connections"""
        try:
            cleared_count = 0
            
            # Find and close connections to our service port
            for conn in psutil.net_connections():
                if conn.laddr.port == self.config['service']['port']:
                    try:
                        if conn.pid:
                            proc = psutil.Process(conn.pid)
                            if proc.pid != self.service_pid:  # Don't kill the service itself
                                proc.terminate()
                                cleared_count += 1
                    except:
                        pass
                        
            self.logger.info(f"Cleared {cleared_count} connections")
            
            return {
                "success": True,
                "message": f"Cleared {cleared_count} connections"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to clear connections: {e}")
            return {
                "success": False,
                "message": f"Failed to clear connections: {str(e)}"
            }
            
    def get_logs(self, lines: int = 100) -> List[str]:
        """Get recent log entries"""
        try:
            if not os.path.exists(self.log_file):
                return ["No log file found"]
                
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                
            return [line.strip() for line in all_lines[-lines:]]
            
        except Exception as e:
            return [f"Error reading logs: {str(e)}"]
            
    def clear_logs(self) -> Dict[str, Any]:
        """Clear log files"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write(f"{datetime.now().isoformat()} - WebServiceManager - INFO - Log file cleared\n")
                    
            self.logger.info("Log file cleared")
            
            return {
                "success": True,
                "message": "Log file cleared successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to clear logs: {str(e)}"
            }
            
    def add_user(self, username: str, password: str, role: str = "user", 
                 permissions: List[str] = None, allowed_ips: List[str] = None) -> Dict[str, Any]:
        """Add a new user to ACL"""
        try:
            if username in self.acl.get("users", {}):
                return {
                    "success": False,
                    "message": f"User '{username}' already exists"
                }
                
            if permissions is None:
                permissions = ["read"] if role == "user" else ["read", "write", "admin"]
                
            if allowed_ips is None:
                allowed_ips = ["*"]
                
            self.acl.setdefault("users", {})[username] = {
                "password_hash": password,  # Should be hashed in production
                "role": role,
                "permissions": permissions,
                "allowed_ips": allowed_ips,
                "created": datetime.now().isoformat(),
                "last_login": None,
                "failed_attempts": 0,
                "locked_until": None
            }
            
            self.save_acl()
            self.logger.info(f"User '{username}' added successfully")
            
            return {
                "success": True,
                "message": f"User '{username}' added successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to add user: {e}")
            return {
                "success": False,
                "message": f"Failed to add user: {str(e)}"
            }
            
    def remove_user(self, username: str) -> Dict[str, Any]:
        """Remove a user from ACL"""
        try:
            if username not in self.acl.get("users", {}):
                return {
                    "success": False,
                    "message": f"User '{username}' not found"
                }
                
            del self.acl["users"][username]
            self.save_acl()
            self.logger.info(f"User '{username}' removed successfully")
            
            return {
                "success": True,
                "message": f"User '{username}' removed successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to remove user: {e}")
            return {
                "success": False,
                "message": f"Failed to remove user: {str(e)}"
            }
            
    def update_ip_restrictions(self, allowed_ips: List[str], blocked_ips: List[str] = None) -> Dict[str, Any]:
        """Update IP restrictions"""
        try:
            if blocked_ips is None:
                blocked_ips = []
                
            self.acl["ip_restrictions"] = {
                "enabled": True,
                "allowed_ips": allowed_ips,
                "blocked_ips": blocked_ips,
                "whitelist_mode": True
            }
            
            self.save_acl()
            self.logger.info("IP restrictions updated")
            
            return {
                "success": True,
                "message": "IP restrictions updated successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update IP restrictions: {e}")
            return {
                "success": False,
                "message": f"Failed to update IP restrictions: {str(e)}"
            }
            
    def _find_service_script(self) -> Optional[str]:
        """Find the web service script"""
        possible_paths = [
            "WebService/app.py",
            "webservice/app.py",
            "web_service/app.py",
            "app.py",
            "server.py",
            "web_server.py"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        return None
        
    def export_config(self, file_path: str) -> Dict[str, Any]:
        """Export configuration to file"""
        try:
            export_data = {
                "config": self.config,
                "acl": self.acl,
                "exported_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False)
                
            return {
                "success": True,
                "message": f"Configuration exported to {file_path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to export configuration: {str(e)}"
            }
            
    def import_config(self, file_path: str) -> Dict[str, Any]:
        """Import configuration from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
                
            if "config" in import_data:
                self.config = import_data["config"]
                self.save_config()
                
            if "acl" in import_data:
                self.acl = import_data["acl"]
                self.save_acl()
                
            return {
                "success": True,
                "message": f"Configuration imported from {file_path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to import configuration: {str(e)}"
            }
    
    # Convenience methods for better API compatibility
    def save_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Save configuration (convenience method)"""
        try:
            self.config.update(config)
            result = self.save_config()
            return {"success": True, "message": "Configuration saved successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def load_configuration(self) -> Dict[str, Any]:
        """Load configuration (convenience method)"""
        return self.config
    
    def add_allowed_ip(self, ip: str) -> Dict[str, Any]:
        """Add IP to allowed list"""
        try:
            if "allowed_ips" not in self.acl["security"]:
                self.acl["security"]["allowed_ips"] = []
            
            if ip not in self.acl["security"]["allowed_ips"]:
                self.acl["security"]["allowed_ips"].append(ip)
                self.save_acl()
                return {"success": True, "message": f"IP {ip} added to allowed list"}
            else:
                return {"success": False, "error": f"IP {ip} already in allowed list"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def remove_allowed_ip(self, ip: str) -> Dict[str, Any]:
        """Remove IP from allowed list"""
        try:
            if "allowed_ips" in self.acl["security"] and ip in self.acl["security"]["allowed_ips"]:
                self.acl["security"]["allowed_ips"].remove(ip)
                self.save_acl()
                return {"success": True, "message": f"IP {ip} removed from allowed list"}
            else:
                return {"success": False, "error": f"IP {ip} not found in allowed list"}
        except Exception as e:
            return {"success": False, "error": str(e)}