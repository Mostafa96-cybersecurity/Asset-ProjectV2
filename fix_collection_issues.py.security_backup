#!/usr/bin/env python3
"""
Fix Critical Collection Issues
Addresses NMAP and system tool issues to enable full data collection
"""

import subprocess
from pathlib import Path

def fix_nmap_issue():
    """Install and configure NMAP for enhanced scanning"""
    print("🔧 FIXING NMAP CONFIGURATION")
    print("=" * 50)
    
    # Check if NMAP is in PATH
    nmap_found = False
    try:
        result = subprocess.run(['nmap', '--version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ NMAP already available in PATH")
            nmap_found = True
        else:
            print("❌ NMAP found but not working properly")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ NMAP not found in PATH")
    
    if not nmap_found:
        print("\n💡 NMAP INSTALLATION OPTIONS:")
        print("1. Install via winget (recommended):")
        print("   winget install nmap")
        print("\n2. Download manually:")
        print("   https://nmap.org/download.html")
        print("\n3. Portable option:")
        print("   Download nmap.exe to project directory")
        
        # Check common installation paths
        common_paths = [
            "C:\\Program Files (x86)\\Nmap\\nmap.exe",
            "C:\\Program Files\\Nmap\\nmap.exe",
            Path.cwd() / "nmap.exe",
            Path.cwd() / "tools" / "nmap.exe"
        ]
        
        print("\n🔍 Checking common NMAP locations...")
        for path in common_paths:
            if Path(path).exists():
                print(f"   ✅ Found NMAP at: {path}")
                print("   💡 Add this to your PATH or copy to project directory")
                return str(path)
            else:
                print(f"   ❌ Not found: {path}")
    
    return nmap_found

def create_enhanced_fallback_strategy():
    """Create enhanced fallback strategy when NMAP is not available"""
    print("\n🛡️ CREATING ENHANCED FALLBACK STRATEGY")
    print("=" * 50)
    
    fallback_code = '''
def _enhanced_fallback_scan(self, ip: str) -> Optional[Dict]:
    """Enhanced fallback scanning when NMAP is not available"""
    try:
        result = {
            'ip': ip,
            'hostname': 'unknown',
            'os_family': 'unknown',
            'open_ports': [],
            'services': [],
            'scan_method': 'fallback'
        }
        
        # 1. Try to get hostname
        try:
            import socket
            hostname = socket.gethostbyaddr(ip)[0]
            result['hostname'] = hostname
            self.log_message.emit(f"   🏷️ {ip}: Hostname resolved → {hostname}")
        except Exception:
            pass
        
        # 2. Port scanning on common ports
        common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 3389, 5432, 3306, 1433, 161, 9100, 631]
        open_ports = []
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.0)
                result_code = sock.connect_ex((ip, port))
                sock.close()
                
                if result_code == 0:
                    open_ports.append(port)
                    self.log_message.emit(f"   🔌 {ip}: Port {port} open")
            except Exception:
                continue
        
        result['open_ports'] = open_ports
        
        # 3. OS Detection based on open ports
        if 135 in open_ports or 139 in open_ports or 445 in open_ports:
            result['os_family'] = 'windows'
            self.log_message.emit(f"   🖥️ {ip}: Detected as Windows (SMB ports)")
        elif 22 in open_ports:
            result['os_family'] = 'linux'
            self.log_message.emit(f"   🐧 {ip}: Detected as Linux (SSH port)")
        elif 161 in open_ports:
            result['os_family'] = 'network_device'
            self.log_message.emit(f"   🌐 {ip}: Detected as Network Device (SNMP)")
        elif 9100 in open_ports or 631 in open_ports:
            result['os_family'] = 'printer'
            self.log_message.emit(f"   🖨️ {ip}: Detected as Printer")
        
        # 4. Service detection
        service_map = {
            21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp', 53: 'dns',
            80: 'http', 110: 'pop3', 135: 'rpc', 139: 'netbios', 143: 'imap',
            443: 'https', 445: 'smb', 993: 'imaps', 995: 'pop3s',
            3389: 'rdp', 5432: 'postgresql', 3306: 'mysql', 1433: 'mssql',
            161: 'snmp', 9100: 'printer', 631: 'ipp'
        }
        
        services = [service_map.get(port, f'port-{port}') for port in open_ports]
        result['services'] = services
        
        if len(open_ports) > 0:
            self.log_message.emit(f"   ✅ {ip}: Fallback scan successful ({len(open_ports)} ports, {result['os_family']})")
            return result
        else:
            self.log_message.emit(f"   ⚠️ {ip}: No open ports found")
            return result
            
    except Exception as e:
        self.log_message.emit(f"   ❌ {ip}: Fallback scan failed: {e}")
        return None
'''
    
    # Check if the method already exists in enhanced_collection_strategy.py
    strategy_path = Path("enhanced_collection_strategy.py")
    if strategy_path.exists():
        with open(strategy_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '_enhanced_fallback_scan' not in content:
            print("📝 Adding enhanced fallback scan method...")
            
            # Find where to insert the method (before _enhanced_nmap_scan)
            lines = content.split('\n')
            insert_point = -1
            
            for i, line in enumerate(lines):
                if 'def _enhanced_nmap_scan' in line:
                    insert_point = i
                    break
            
            if insert_point > 0:
                # Insert the fallback method before _enhanced_nmap_scan
                fallback_lines = fallback_code.strip().split('\n')
                for i, line in enumerate(fallback_lines):
                    lines.insert(insert_point + i, '    ' + line)  # Add proper indentation
                
                # Write back to file
                with open(strategy_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                print("✅ Enhanced fallback scan method added successfully")
                return True
            else:
                print("❌ Could not find insertion point for fallback method")
                return False
        else:
            print("✅ Enhanced fallback scan method already exists")
            return True
    else:
        print("❌ Enhanced collection strategy file not found")
        return False

def update_nmap_scan_method():
    """Update the _enhanced_nmap_scan method to use fallback when NMAP not available"""
    print("\n🔧 UPDATING NMAP SCAN METHOD")
    print("=" * 50)
    
    strategy_path = Path("enhanced_collection_strategy.py")
    if not strategy_path.exists():
        print("❌ Enhanced collection strategy file not found")
        return False
    
    try:
        with open(strategy_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the _enhanced_nmap_scan method
        if '_enhanced_nmap_scan' in content:
            # Update the method to include fallback
            updated_content = content.replace(
                'def _enhanced_nmap_scan(self, ip: str) -> Optional[Dict]:',
                '''def _enhanced_nmap_scan(self, ip: str) -> Optional[Dict]:
        """Enhanced NMAP scan with automatic fallback"""
        # First try NMAP if available
        try:
            import nmap
            nm = nmap.PortScanner()
            scan_result = nm.scan(ip, '1-1000', '-sS -O --osscan-guess')
            
            if ip in scan_result['scan']:
                host_info = scan_result['scan'][ip]
                result = {
                    'ip': ip,
                    'hostname': host_info.get('hostnames', [{}])[0].get('name', 'unknown'),
                    'os_family': self._extract_os_family(host_info),
                    'open_ports': list(host_info.get('tcp', {}).keys()),
                    'services': list(host_info.get('tcp', {}).values()),
                    'scan_method': 'nmap'
                }
                self.log_message.emit(f"   ✅ {ip}: NMAP scan successful")
                return result
        except Exception as e:
            self.log_message.emit(f"   ⚠️ {ip}: NMAP failed, using fallback: {str(e)[:50]}...")
        
        # Fallback to enhanced port scanning
        return self._enhanced_fallback_scan(ip)

    def _enhanced_nmap_scan_original(self, ip: str) -> Optional[Dict]:'''
            )
            
            with open(strategy_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("✅ NMAP scan method updated with fallback capability")
            return True
        else:
            print("❌ _enhanced_nmap_scan method not found")
            return False
            
    except Exception as e:
        print(f"❌ Failed to update NMAP scan method: {e}")
        return False

def create_collection_troubleshooting_guide():
    """Create a comprehensive troubleshooting guide"""
    guide_content = '''
# COLLECTION TROUBLESHOOTING GUIDE
================================

## Common Issues and Solutions

### 1. NMAP Not Found
**Issue:** "nmap program was not found in path"
**Solutions:**
- Install NMAP: `winget install nmap`
- Download from: https://nmap.org/download.html
- Add NMAP to system PATH
- Use fallback scanning (automatic)

### 2. WMI Collection Fails
**Issue:** "All collection methods failed"
**Reasons:**
- Target is not Windows
- Firewall blocking WMI
- Authentication failure
- Admin rights required

**Solutions:**
- Ensure Windows credentials are correct
- Run as administrator
- Check Windows firewall settings
- Verify WMI service is running

### 3. SSH Collection Fails
**Issue:** SSH connection refused
**Reasons:**
- SSH service not running
- Wrong port (default 22)
- Authentication failure
- Firewall blocking

**Solutions:**
- Verify SSH service is enabled
- Check correct port number
- Verify SSH credentials
- Test manual SSH connection

### 4. SNMP Collection Fails
**Issue:** No SNMP response
**Reasons:**
- SNMP service disabled
- Wrong community string
- SNMP version mismatch
- Firewall blocking port 161

**Solutions:**
- Enable SNMP service on target
- Verify community string ("public" default)
- Try different SNMP versions
- Check firewall rules

### 5. HTTP Detection Fails
**Issue:** No web services found
**Reasons:**
- No web server running
- Non-standard ports
- HTTPS only
- Firewall blocking

**Solutions:**
- Check if web server is running
- Try common ports: 80, 443, 8080, 8443
- Verify SSL certificates
- Check firewall settings

## Best Practices

1. **Network Preparation:**
   - Ensure network connectivity
   - Configure appropriate credentials
   - Check firewall rules
   - Verify service availability

2. **Credential Management:**
   - Use service accounts
   - Rotate credentials regularly
   - Test credentials manually first
   - Use least privilege principle

3. **Performance Optimization:**
   - Limit concurrent connections
   - Use appropriate timeouts
   - Monitor resource usage
   - Schedule scans during off-hours

4. **Troubleshooting Steps:**
   1. Test network connectivity (ping)
   2. Test individual collection methods
   3. Check logs for specific errors
   4. Verify target system configuration
   5. Test with manual tools first

## Expected Success Rates

- **Ping Detection:** 90-95% (for reachable devices)
- **OS Detection:** 70-80% (depends on NMAP availability)
- **WMI Collection:** 60-70% (Windows only, auth dependent)
- **SSH Collection:** 40-60% (Linux/Unix, auth dependent)
- **SNMP Collection:** 30-50% (network devices, config dependent)
- **HTTP Detection:** 20-40% (web servers only)

Note: Low success rates are normal for security reasons.
Many devices block or restrict these collection methods.
'''
    
    with open('COLLECTION_TROUBLESHOOTING.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("📚 Created comprehensive troubleshooting guide: COLLECTION_TROUBLESHOOTING.md")

def main():
    """Main function to fix critical collection issues"""
    print("🔧 FIXING CRITICAL COLLECTION ISSUES")
    print("=" * 80)
    
    # 1. Check and fix NMAP
    nmap_ok = fix_nmap_issue()
    
    # 2. Create enhanced fallback strategy
    fallback_created = create_enhanced_fallback_strategy()
    
    # 3. Update NMAP scan method
    nmap_updated = update_nmap_scan_method()
    
    # 4. Create troubleshooting guide
    create_collection_troubleshooting_guide()
    
    print("\n" + "=" * 80)
    print("🎯 FIXES APPLIED SUMMARY")
    print("=" * 80)
    
    print(f"NMAP availability: {'✅' if nmap_ok else '⚠️ Manual installation needed'}")
    print(f"Fallback strategy: {'✅' if fallback_created else '❌'}")
    print(f"NMAP method update: {'✅' if nmap_updated else '❌'}")
    print("Troubleshooting guide: ✅")
    
    if fallback_created and nmap_updated:
        print("\n🎉 COLLECTION FIXES APPLIED SUCCESSFULLY!")
        print("   • Enhanced fallback scanning when NMAP unavailable")
        print("   • Automatic OS detection via port analysis")
        print("   • Service identification from open ports")
        print("   • Comprehensive error handling and logging")
        print("   • Troubleshooting guide created")
        print("\n🚀 Your collection system will now work even without NMAP!")
    else:
        print("\n⚠️ Some fixes could not be applied")
        print("   Please check the error messages above")

if __name__ == "__main__":
    main()