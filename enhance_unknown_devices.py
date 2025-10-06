#!/usr/bin/env python3
"""
Enhanced Unknown Device Classifier
Improved classification strategies for remaining unknown devices
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_ultimate_performance_collector import EnhancedUltimatePerformanceCollector
import sqlite3
import json
from collections import Counter

class UnknownDeviceEnhancer:
    """Enhanced classifier specifically for unknown devices"""
    
    def __init__(self):
        self.enhanced_patterns = {
            # More comprehensive server patterns
            'server_indicators': [
                'server', 'srv', 'svc', 'service', 'prod', 'production', 
                'app', 'application', 'db', 'database', 'sql', 'web', 'www',
                'mail', 'exchange', 'file', 'share', 'backup', 'storage',
                'dc-', 'ad-', 'dns', 'dhcp', 'proxy', 'cache', 'redis',
                'dev-', 'test-', 'staging', 'demo'
            ],
            
            # More comprehensive workstation patterns  
            'workstation_indicators': [
                'workstation', 'ws-', 'wks', 'pc-', 'computer', 'desktop',
                'user', 'emp', 'employee', 'admin', 'mgmt', 'finance',
                'hr', 'it-', 'support', 'help', 'desk', 'office',
                'work', 'dev', 'developer', 'eng', 'engineer'
            ],
            
            # More comprehensive laptop patterns
            'laptop_indicators': [
                'laptop', 'lt-', 'nb-', 'notebook', 'mobile', 'portable',
                'book', 'air', 'pro', 'ultra', 'slim', 'flex', 'yoga',
                'surface', 'think', 'latitude', 'precision', 'elitebook',
                'user-', 'personal', 'mobile'
            ],
            
            # Test device patterns
            'test_indicators': [
                'test', 'testing', 'temp', 'temporary', 'demo', 'sample',
                'trial', 'prototype', 'dev', 'development', 'staging',
                'lab', 'laboratory', 'bench', 'sandbox', 'pc-'
            ]
        }
        
        self.port_based_classification = {
            # Server ports (indicate server functionality)
            'server_ports': [80, 443, 25, 110, 143, 993, 995, 21, 22, 23, 53, 389, 636, 1433, 1521, 3306, 5432],
            
            # Workstation ports (indicate client/workstation functionality)  
            'workstation_ports': [135, 139, 445, 1024, 1025, 1026, 1027, 5357],
            
            # Management ports
            'management_ports': [161, 162, 623, 664, 5985, 5986]
        }

    def classify_unknown_device(self, hostname: str, open_ports: list, os_info: str = "") -> tuple:
        """
        Enhanced classification for unknown devices
        Returns: (device_type, confidence_score, reasoning)
        """
        hostname_lower = hostname.lower()
        reasoning = []
        scores = {
            'Server': 0,
            'Workstation': 0, 
            'Laptop': 0,
            'Test Device': 0,
            'Network Device': 0
        }
        
        # 1. Hostname pattern analysis (40% weight)
        for category, patterns in self.enhanced_patterns.items():
            for pattern in patterns:
                if pattern in hostname_lower:
                    category_name = category.split('_')[0].title()
                    if category_name == 'Test':
                        category_name = 'Test Device'
                    
                    scores[category_name] = scores.get(category_name, 0) + 25
                    reasoning.append(f"Hostname contains '{pattern}' ({category_name} indicator)")
        
        # 2. Port analysis (35% weight)
        if open_ports:
            server_port_matches = len([p for p in open_ports if p in self.port_based_classification['server_ports']])
            workstation_port_matches = len([p for p in open_ports if p in self.port_based_classification['workstation_ports']])
            management_port_matches = len([p for p in open_ports if p in self.port_based_classification['management_ports']])
            
            if server_port_matches > 0:
                scores['Server'] += server_port_matches * 15
                reasoning.append(f"Has {server_port_matches} server ports open")
                
            if workstation_port_matches > 0:
                scores['Workstation'] += workstation_port_matches * 10
                reasoning.append(f"Has {workstation_port_matches} workstation ports open")
                
            if management_port_matches > 0:
                scores['Network Device'] += management_port_matches * 20
                reasoning.append(f"Has {management_port_matches} management ports open")
        
        # 3. OS information analysis (25% weight)
        if os_info:
            os_lower = os_info.lower()
            if 'server' in os_lower:
                scores['Server'] += 30
                reasoning.append("OS indicates server edition")
            elif 'windows' in os_lower:
                scores['Workstation'] += 20
                reasoning.append("Windows OS detected (likely workstation)")
            elif 'linux' in os_lower:
                if any(p in open_ports for p in [80, 443, 22, 25]):
                    scores['Server'] += 25
                    reasoning.append("Linux with server services")
                else:
                    scores['Workstation'] += 15
                    reasoning.append("Linux workstation")
        
        # Determine best classification
        if scores:
            best_type, best_score = max(scores.items(), key=lambda x: x[1])
            confidence = min(best_score / 100.0, 1.0)  # Normalize to 0-1
            
            if confidence >= 0.3:  # Lower threshold for unknown devices
                return best_type, confidence, reasoning
        
        return "Unknown", 0.0, ["No clear classification patterns found"]

def enhance_unknown_devices():
    """Process and enhance classification of unknown devices"""
    print("=== ENHANCED UNKNOWN DEVICE CLASSIFICATION ===")
    
    # Connect to database
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Get unknown devices with their data
    cursor.execute('''
        SELECT hostname, ip_address, open_ports, operating_system, device_type, id 
        FROM assets 
        WHERE device_type IN ('Unknown', 'Unknown Device') OR device_type IS NULL
        ORDER BY last_seen DESC
    ''')
    
    unknown_devices = cursor.fetchall()
    print(f"Found {len(unknown_devices)} unknown devices to analyze")
    print()
    
    enhancer = UnknownDeviceEnhancer()
    classifications = []
    
    for hostname, ip, ports_json, os_info, current_type, device_id in unknown_devices:
        # Parse open ports
        try:
            open_ports = json.loads(ports_json) if ports_json else []
        except:
            open_ports = []
        
        # Get enhanced classification
        new_type, confidence, reasoning = enhancer.classify_unknown_device(
            hostname, open_ports, os_info or ""
        )
        
        classifications.append({
            'id': device_id,
            'hostname': hostname,
            'ip': ip,
            'current_type': current_type,
            'new_type': new_type,
            'confidence': confidence,
            'reasoning': reasoning,
            'open_ports': open_ports
        })
        
        print(f"📍 {hostname} ({ip})")
        print(f"   Current: {current_type or 'None'}")
        print(f"   Enhanced: {new_type} (confidence: {confidence:.2f})")
        print(f"   Ports: {open_ports}")
        print(f"   Reasoning: {', '.join(reasoning[:2])}")
        print()
    
    # Show summary
    reclassified = [c for c in classifications if c['confidence'] >= 0.3]
    print(f"=== ENHANCEMENT SUMMARY ===")
    print(f"Total unknown devices: {len(classifications)}")
    print(f"Successfully reclassified: {len(reclassified)}")
    print(f"Improvement rate: {len(reclassified)/len(classifications)*100:.1f}%")
    print()
    
    # Show reclassification breakdown
    new_types = Counter([c['new_type'] for c in reclassified])
    print("New classifications:")
    for device_type, count in new_types.most_common():
        print(f"  {device_type}: {count} devices")
    
    # Ask user if they want to apply the changes
    print()
    apply_changes = input("Apply these enhanced classifications to the database? (y/N): ").lower().strip()
    
    if apply_changes == 'y':
        print("\nApplying enhanced classifications...")
        updates_made = 0
        
        for classification in reclassified:
            cursor.execute('''
                UPDATE assets 
                SET device_type = ?, 
                    confidence_score = ?,
                    notes = ?
                WHERE id = ?
            ''', (
                classification['new_type'],
                classification['confidence'],
                f"Enhanced classification: {', '.join(classification['reasoning'][:2])}",
                classification['id']
            ))
            updates_made += 1
        
        conn.commit()
        print(f"✅ Updated {updates_made} device classifications")
        
        # Show final statistics
        cursor.execute('SELECT device_type, COUNT(*) FROM assets GROUP BY device_type ORDER BY COUNT(*) DESC')
        final_stats = cursor.fetchall()
        
        print("\n=== FINAL DEVICE TYPE DISTRIBUTION ===")
        total_devices = sum(count for _, count in final_stats)
        for device_type, count in final_stats:
            percentage = (count / total_devices) * 100
            print(f"  {device_type}: {count} devices ({percentage:.1f}%)")
    else:
        print("No changes applied to database.")
    
    conn.close()

if __name__ == "__main__":
    enhance_unknown_devices()