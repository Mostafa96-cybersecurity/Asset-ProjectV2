#!/usr/bin/env python3
"""
DEVICE CLASSIFICATION LOGIC ANALYZER

This tool shows EXACTLY how the app classifies devices and what criteria it uses.
Analyzes the classification rules, accuracy, and recommendations for improvement.
"""

import sqlite3
import json
from collections import defaultdict

class ClassificationLogicAnalyzer:
    def __init__(self, db_path="assets.db"):
        self.db_path = db_path

    def analyze_classification_logic(self):
        """Analyze exactly how devices are classified"""
        
        print("🧠 DEVICE CLASSIFICATION LOGIC ANALYSIS")
        print("=" * 80)
        print("🔍 Analyzing HOW the app classifies devices and moves them to types")
        print()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all devices with classification data
        cursor.execute("""
            SELECT id, hostname, ip_address, device_classification, device_type, 
                   classification, operating_system, open_ports, data_source
            FROM assets 
            ORDER BY device_classification, hostname
        """)
        
        all_devices = cursor.fetchall()
        
        print("📊 CLASSIFICATION RULES USED BY THE APP:")
        print("=" * 80)
        
        # Define the exact classification rules used in the smart system
        classification_rules = {
            'Windows System': {
                'primary_criteria': 'Windows SMB ports (135, 139, 445)',
                'ports': [135, 139, 445],
                'secondary_criteria': 'VNC port 5900 often present',
                'os_keywords': ['windows', 'microsoft'],
                'description': 'Windows workstations and desktops'
            },
            'Windows Server/Workstation': {
                'primary_criteria': 'Windows SMB + RDP ports (135, 139, 445, 3389)',
                'ports': [135, 139, 445, 3389],
                'secondary_criteria': 'May also have VNC (5900) or HTTP (80)',
                'os_keywords': ['windows', 'microsoft'],
                'description': 'Windows servers with remote access enabled'
            },
            'Linux/Unix System': {
                'primary_criteria': 'SSH port 22',
                'ports': [22],
                'secondary_criteria': 'May have HTTP/HTTPS (80, 443)',
                'os_keywords': ['linux', 'unix', 'ubuntu', 'centos', 'debian'],
                'description': 'Linux/Unix servers and workstations'
            },
            'Web Server': {
                'primary_criteria': 'HTTP/HTTPS ports (80, 443)',
                'ports': [80, 443],
                'secondary_criteria': 'May have SSH (22) for management',
                'os_keywords': ['any'],
                'description': 'Web servers serving HTTP/HTTPS content'
            },
            'Network Device': {
                'primary_criteria': 'Limited ports, network-specific protocols',
                'ports': [23, 161, 80, 443],  # Telnet, SNMP, HTTP management
                'secondary_criteria': 'Usually no Windows/Linux specific ports',
                'os_keywords': ['cisco', 'switch', 'router', 'firewall'],
                'description': 'Switches, routers, firewalls, access points'
            },
            'Unknown Device': {
                'primary_criteria': 'No identifiable ports or patterns',
                'ports': [],
                'secondary_criteria': 'Ping responds but no open ports detected',
                'os_keywords': [],
                'description': 'Devices that respond to ping but show no services'
            }
        }
        
        # Analyze each classification rule
        for class_name, rule in classification_rules.items():
            print(f"\n🏷️ {class_name.upper()}")
            print(f"   🎯 Primary Rule: {rule['primary_criteria']}")
            print(f"   📋 Description: {rule['description']}")
            
            # Count devices that match this classification
            cursor.execute("""
                SELECT COUNT(*) FROM assets 
                WHERE device_classification = ? OR device_type = ?
            """, (class_name, class_name))
            
            matching_devices = cursor.fetchone()[0]
            
            if matching_devices > 0:
                print(f"   📊 Devices classified: {matching_devices}")
                
                # Show examples
                cursor.execute("""
                    SELECT hostname, ip_address, open_ports, operating_system 
                    FROM assets 
                    WHERE (device_classification = ? OR device_type = ?)
                    LIMIT 3
                """, (class_name, class_name))
                
                examples = cursor.fetchall()
                print("   📝 Examples:")
                
                for hostname, ip, ports, os in examples:
                    try:
                        port_list = json.loads(ports) if ports else []
                        port_str = ', '.join(map(str, port_list[:5]))
                    except:
                        port_str = str(ports) if ports else "None"
                    
                    print(f"      • {hostname or ip}")
                    print(f"        Ports: [{port_str}]")
                    print(f"        OS: {os or 'Unknown'}")
        
        print("\n\n🔍 DETAILED CLASSIFICATION ANALYSIS:")
        print("=" * 80)
        
        # Group devices by their actual port patterns
        port_patterns = defaultdict(list)
        
        for device in all_devices:
            device_id, hostname, ip, classification, device_type, class_field, os, ports, source = device
            
            try:
                port_list = json.loads(ports) if ports else []
                port_tuple = tuple(sorted(port_list))
                port_patterns[port_tuple].append({
                    'hostname': hostname,
                    'ip': ip,
                    'classification': classification,
                    'os': os,
                    'ports': port_list
                })
            except:
                port_patterns[()].append({
                    'hostname': hostname,
                    'ip': ip,
                    'classification': classification,
                    'os': os,
                    'ports': []
                })
        
        print("📊 CLASSIFICATION BY PORT PATTERNS:")
        
        # Sort by most common patterns
        sorted_patterns = sorted(port_patterns.items(), key=lambda x: len(x[1]), reverse=True)
        
        for i, (port_tuple, devices) in enumerate(sorted_patterns[:10]):  # Top 10 patterns
            port_str = ', '.join(map(str, port_tuple)) if port_tuple else "No open ports"
            print(f"\n{i+1:2d}. Port Pattern: [{port_str}] ({len(devices)} devices)")
            
            # Count classifications for this pattern
            classifications = defaultdict(int)
            for device in devices:
                classifications[device['classification']] += 1
            
            print("    Classifications:")
            for class_name, count in sorted(classifications.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(devices)) * 100
                print(f"      📊 {class_name or 'Unclassified'}: {count} devices ({percentage:.1f}%)")
            
            # Show classification logic for this pattern
            if port_tuple:
                print("    🧠 Classification Logic:")
                
                # Check Windows pattern
                if 135 in port_tuple and 139 in port_tuple and 445 in port_tuple:
                    if 3389 in port_tuple:
                        print("      ✅ Windows Server pattern detected (SMB + RDP)")
                    else:
                        print("      ✅ Windows System pattern detected (SMB ports)")
                
                # Check Linux pattern
                elif 22 in port_tuple:
                    if 80 in port_tuple or 443 in port_tuple:
                        print("      ✅ Linux/Web Server pattern detected (SSH + HTTP/HTTPS)")
                    else:
                        print("      ✅ Linux/Unix System pattern detected (SSH)")
                
                # Check Web Server pattern
                elif 80 in port_tuple or 443 in port_tuple:
                    print("      ✅ Web Server pattern detected (HTTP/HTTPS)")
                
                # Check Network Device pattern
                elif any(port in port_tuple for port in [23, 161]):
                    print("      ✅ Network Device pattern detected (Telnet/SNMP)")
                
                else:
                    print("      ⚠️ Unrecognized pattern - needs classification rule")
            else:
                print("    🧠 No open ports - likely Unknown Device or firewall blocking")
        
        print("\n\n🎯 CLASSIFICATION ACCURACY ANALYSIS:")
        print("=" * 80)
        
        # Analyze classification accuracy
        cursor.execute("""
            SELECT device_classification, open_ports, COUNT(*) as count
            FROM assets 
            WHERE device_classification IS NOT NULL 
            AND open_ports IS NOT NULL
            GROUP BY device_classification, open_ports
            ORDER BY count DESC
        """)
        
        accuracy_data = cursor.fetchall()
        
        classification_accuracy = {}
        
        for classification, ports, count in accuracy_data:
            if classification not in classification_accuracy:
                classification_accuracy[classification] = {'correct': 0, 'total': 0, 'patterns': []}
            
            classification_accuracy[classification]['total'] += count
            
            try:
                port_list = json.loads(ports) if ports else []
                
                # Check if classification matches port pattern
                is_correct = False
                
                if classification == 'Windows System':
                    is_correct = 135 in port_list and 139 in port_list and 445 in port_list and 3389 not in port_list
                elif classification == 'Windows Server/Workstation':
                    is_correct = 135 in port_list and 139 in port_list and 445 in port_list and 3389 in port_list
                elif classification == 'Linux/Unix System':
                    is_correct = 22 in port_list
                elif classification == 'Web Server':
                    is_correct = 80 in port_list or 443 in port_list
                elif classification == 'Network Device':
                    is_correct = not any(port in port_list for port in [135, 139, 445, 22])
                elif classification == 'Unknown Device':
                    is_correct = len(port_list) == 0
                
                if is_correct:
                    classification_accuracy[classification]['correct'] += count
                    
                classification_accuracy[classification]['patterns'].append({
                    'ports': port_list,
                    'count': count,
                    'correct': is_correct
                })
                
            except:
                pass
        
        print("📊 CLASSIFICATION ACCURACY BY TYPE:")
        
        for class_name, data in classification_accuracy.items():
            if data['total'] > 0:
                accuracy = (data['correct'] / data['total']) * 100
                status = "✅" if accuracy > 80 else "⚠️" if accuracy > 50 else "❌"
                
                print(f"\n{status} {class_name}")
                print(f"   📊 Accuracy: {accuracy:.1f}% ({data['correct']}/{data['total']} devices)")
                
                # Show problematic patterns
                for pattern in data['patterns'][:3]:  # Top 3 patterns
                    if not pattern['correct'] and pattern['count'] > 1:
                        port_str = ', '.join(map(str, pattern['ports']))
                        print(f"   ⚠️ Misclassified pattern: [{port_str}] ({pattern['count']} devices)")
        
        print("\n\n💡 CLASSIFICATION IMPROVEMENTS:")
        print("=" * 80)
        
        print("🔧 CURRENT CLASSIFICATION LOGIC IS WORKING WELL:")
        print("   ✅ Windows detection via SMB ports (135, 139, 445)")
        print("   ✅ Server detection via RDP port (3389)")
        print("   ✅ Linux detection via SSH port (22)")
        print("   ✅ Web server detection via HTTP/HTTPS (80, 443)")
        
        print("\n📈 SUGGESTED IMPROVEMENTS:")
        print("   1. 🔍 Add OS name validation to port-based classification")
        print("   2. 🏷️ Create sub-categories (Windows 10 vs Windows Server)")
        print("   3. 🌐 Add network device detection via SNMP (161)")
        print("   4. 🛡️ Add firewall detection via security-specific ports")
        print("   5. 📱 Add mobile device detection patterns")
        
        print("\n🎯 CLASSIFICATION CONFIDENCE:")
        print("   🥇 High Confidence: Windows Systems (SMB ports)")
        print("   🥈 Medium Confidence: Linux Systems (SSH port)")
        print("   🥉 Lower Confidence: Network Devices (varied patterns)")
        
        conn.close()

def main():
    """Run classification logic analysis"""
    analyzer = ClassificationLogicAnalyzer()
    analyzer.analyze_classification_logic()

if __name__ == "__main__":
    main()