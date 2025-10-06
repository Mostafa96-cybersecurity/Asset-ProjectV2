#!/usr/bin/env python3
"""
🚀 COMPREHENSIVE ASSET MANAGEMENT PORTAL LAUNCHER
===============================================
Launches both the secure web service and enhanced dashboard
"""

import ipaddress  # For IP validation
import os
import sys
import subprocess
import time
import requests
from pathlib import Path

class ComprehensivePortalLauncher:
    def __init__(self):
        self.services = {
            'secure_web_service': {
                'file': 'secure_web_service.py',
                'port': 5556,
                'name': 'Secure Web Service',
                'process': None,
                'status': 'stopped'
            },
            'enhanced_dashboard': {
                'file': 'fixed_dashboard.py', 
                'port': 5556,
                'name': 'Enhanced Dashboard',
                'process': None,
                'status': 'stopped'
            }
        }
        
        self.python_path = self.get_python_path()
    
    def get_python_path(self):
        """Get the correct Python executable path"""
        venv_python = Path('.venv/Scripts/python.exe')
        if venv_python.exists():
            return str(venv_python.absolute())
        return 'python'
    
    def start_service(self, service_name):
        """Start a specific service"""
        if service_name not in self.services:
            print(f"❌ Unknown service: {service_name}")
            return False
        
        service = self.services[service_name]
        
        if service['status'] == 'running':
            print(f"✅ {service['name']} is already running")
            return True
        
        try:
            print(f"🚀 Starting {service['name']}...")
            
            # Start the service in background
            process = subprocess.Popen(
                [self.python_path, service['file']],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            service['process'] = process
            service['status'] = 'starting'
            
            # Wait a moment and check if service is responding
            time.sleep(3)
            
            if self.check_service_health(service_name):
                service['status'] = 'running'
                print(f"✅ {service['name']} started successfully on port {service['port']}")
                return True
            else:
                print(f"❌ {service['name']} failed to start properly")
                service['status'] = 'error'
                return False
                
        except Exception as e:
            print(f"❌ Error starting {service['name']}: {e}")
            service['status'] = 'error'
            return False
    
    def check_service_health(self, service_name):
        """Check if a service is responding"""
        service = self.services[service_name]
        max_attempts = 10
        
        for attempt in range(max_attempts):
            try:
                if service_name == 'secure_web_service':
                    response = requests.get(f'http://127.0.0.1:{service["port"]}/api/status', timeout=2)
                else:
                    response = requests.get(f'http://127.0.0.1:{service["port"]}/', timeout=2)
                
                if response.status_code in [200, 401, 403]:  # 401/403 are OK for secured services
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
        
        return False
    
    def stop_service(self, service_name):
        """Stop a specific service"""
        if service_name not in self.services:
            print(f"❌ Unknown service: {service_name}")
            return False
        
        service = self.services[service_name]
        
        if service['process']:
            try:
                service['process'].terminate()
                service['process'].wait(timeout=5)
                service['status'] = 'stopped'
                print(f"🛑 {service['name']} stopped")
                return True
            except subprocess.TimeoutExpired:
                service['process'].kill()
                service['status'] = 'stopped'
                print(f"🔥 {service['name']} force killed")
                return True
            except Exception as e:
                print(f"❌ Error stopping {service['name']}: {e}")
                return False
        else:
            print(f"ℹ️ {service['name']} is not running")
            return True
    
    def start_all_services(self):
        """Start all services"""
        print("🌟 COMPREHENSIVE ASSET MANAGEMENT PORTAL")
        print("=" * 50)
        
        success_count = 0
        
        for service_name in self.services:
            if self.start_service(service_name):
                success_count += 1
            time.sleep(2)  # Stagger startup
        
        print("\n" + "=" * 50)
        print("📊 SERVICE STATUS SUMMARY")
        print("=" * 50)
        
        for service_name, service in self.services.items():
            status_icon = "✅" if service['status'] == 'running' else "❌"
            print(f"{status_icon} {service['name']:<25} - Port {service['port']} - {service['status'].upper()}")
        
        if success_count == len(self.services):
            print("\n🎉 ALL SERVICES STARTED SUCCESSFULLY!")
            print("\n🌐 ACCESS URLS:")
            print("📝 Secure Web Service (Login):     http://localhost:5556")
            print("📊 Enhanced Dashboard Portal:     http://localhost:8081/dashboard") 
            print("\n💡 LOGIN CREDENTIALS:")
            print("   Admin: admin / admin123")
            print("   User:  user / user123")
            print("\n🔧 FEATURES AVAILABLE:")
            print("   ✅ Enhanced Access Control & Security")
            print("   ✅ Role-Based User Management")
            print("   ✅ Advanced Asset Dashboard")
            print("   ✅ Device Classification & Filtering")
            print("   ✅ Real-time Status Monitoring")
            print("   ✅ Comprehensive Asset Details")
            print("\n⌨️ Press Ctrl+C to stop all services")
            
        else:
            print(f"\n⚠️ {success_count}/{len(self.services)} services started successfully")
        
        return success_count == len(self.services)
    
    def stop_all_services(self):
        """Stop all services"""
        print("\n🛑 Stopping all services...")
        
        for service_name in self.services:
            self.stop_service(service_name)
        
        print("✅ All services stopped")
    
    def get_status(self):
        """Get status of all services"""
        print("📊 SERVICE STATUS:")
        print("-" * 40)
        
        for service_name, service in self.services.items():
            # Try to check if service is actually responding
            if service['status'] == 'running':
                if self.check_service_health(service_name):
                    status = "🟢 RUNNING"
                else:
                    status = "🔴 NOT RESPONDING"
                    service['status'] = 'error'
            else:
                status = f"🔴 {service['status'].upper()}"
            
            print(f"{service['name']:<25} - {status}")
    
    def interactive_menu(self):
        """Interactive menu for service management"""
        while True:
            print("\n" + "=" * 50)
            print("🎛️ ASSET MANAGEMENT PORTAL CONTROL")
            print("=" * 50)
            print("1. Start All Services")
            print("2. Stop All Services") 
            print("3. Check Status")
            print("4. Start Secure Web Service Only")
            print("5. Start Enhanced Dashboard Only")
            print("6. Open Web Interfaces")
            print("0. Exit")
            print("-" * 50)
            
            choice = input("Select option (0-6): ").strip()
            
            if choice == '1':
                self.start_all_services()
            elif choice == '2':
                self.stop_all_services()
            elif choice == '3':
                self.get_status()
            elif choice == '4':
                self.start_service('secure_web_service')
            elif choice == '5':
                self.start_service('enhanced_dashboard')
            elif choice == '6':
                self.open_web_interfaces()
            elif choice == '0':
                self.stop_all_services()
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    def open_web_interfaces(self):
        """Open web interfaces in browser"""
        import webbrowser
        
        print("🌐 Opening web interfaces...")
        
        if self.services['secure_web_service']['status'] == 'running':
            webbrowser.open('http://localhost:5556')
            print("📝 Opened Secure Web Service")
        
        if self.services['enhanced_dashboard']['status'] == 'running':
            webbrowser.open('http://localhost:8081/dashboard')
            print("📊 Opened Enhanced Dashboard")
        
        if all(s['status'] != 'running' for s in self.services.values()):
            print("⚠️ No services are currently running")

def main():
    """Main function"""
    launcher = ComprehensivePortalLauncher()
    
    try:
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == 'start':
                launcher.start_all_services()
                
                # Keep running and monitoring
                try:
                    while True:
                        time.sleep(10)
                        # Check if services are still running
                        for service_name, service in launcher.services.items():
                            if service['status'] == 'running' and service['process']:
                                if service['process'].poll() is not None:
                                    print(f"⚠️ {service['name']} has stopped unexpectedly")
                                    service['status'] = 'stopped'
                except KeyboardInterrupt:
                    print("\n⏹️ Shutdown requested...")
                    launcher.stop_all_services()
            
            elif command == 'stop':
                launcher.stop_all_services()
            
            elif command == 'status':
                launcher.get_status()
            
            elif command == 'menu':
                launcher.interactive_menu()
            
            else:
                print(f"❌ Unknown command: {command}")
                print("Available commands: start, stop, status, menu")
        
        else:
            # Default: start all services
            launcher.start_all_services()
            
            # Keep running
            try:
                while True:
                    time.sleep(10)
            except KeyboardInterrupt:
                print("\n⏹️ Shutdown requested...")
                launcher.stop_all_services()
    
    except Exception as e:
        print(f"❌ Launcher error: {e}")
        launcher.stop_all_services()

# NOTE: Auto-startup disabled - use launch_original_desktop.py or GUI buttons
# if __name__ == '__main__':
#     main()