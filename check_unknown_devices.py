#!/usr/bin/env python3
"""
Check Unknown Devices Status
Analysis of current device classification and unknown devices
"""

import sqlite3
from collections import Counter

def check_unknown_devices():
    # Connect to database
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Get all devices and their types
    cursor.execute('SELECT hostname, device_type, last_seen FROM assets ORDER BY last_seen DESC LIMIT 100')
    devices = cursor.fetchall()
    
    # Count device types
    device_types = [device[1] for device in devices]
    type_counts = Counter(device_types)
    
    print('=== RECENT DEVICE CLASSIFICATION STATUS ===')
    print(f'Total Recent Devices: {len(devices)}')
    print()
    print('Device Type Distribution:')
    for device_type, count in type_counts.most_common():
        percentage = (count / len(devices)) * 100 if devices else 0
        print(f'  {device_type}: {count} devices ({percentage:.1f}%)')
    
    print()
    print('=== UNKNOWN DEVICES ANALYSIS ===')
    unknown_devices = [device for device in devices if device[1] in ['Unknown', 'Unknown Device', None, '']]
    print(f'Unknown devices found: {len(unknown_devices)}')
    
    if unknown_devices:
        print()
        print('Unknown devices list:')
        for hostname, device_type, last_seen in unknown_devices[:15]:
            device_type_display = device_type if device_type else "None"
            print(f'  • {hostname} - Type: {device_type_display} - Last seen: {last_seen}')
        if len(unknown_devices) > 15:
            print(f'  ... and {len(unknown_devices) - 15} more')
    
    # Classification success rate
    classified_devices = [device for device in devices if device[1] not in ['Unknown', 'Unknown Device', None, '']]
    success_rate = (len(classified_devices) / len(devices)) * 100 if devices else 0
    
    print()
    print('=== CLASSIFICATION PERFORMANCE ===')
    print(f'Successfully Classified: {len(classified_devices)}/{len(devices)} devices')
    print(f'Classification Success Rate: {success_rate:.1f}%')
    print(f'Unknown/Unclassified: {len(unknown_devices)} devices ({100-success_rate:.1f}%)')
    
    # Check for pattern in unknown devices
    print()
    print('=== UNKNOWN DEVICES PATTERNS ===')
    unknown_hostnames = [device[0] for device in unknown_devices]
    
    # Check for common patterns
    patterns = {
        'IP addresses': sum(1 for h in unknown_hostnames if h.replace('.', '').isdigit()),
        'Short names': sum(1 for h in unknown_hostnames if len(h) < 8),
        'No domain': sum(1 for h in unknown_hostnames if '.' not in h),
        'Special chars': sum(1 for h in unknown_hostnames if any(c in h for c in '-_'))
    }
    
    for pattern, count in patterns.items():
        if count > 0:
            percentage = (count / len(unknown_hostnames)) * 100 if unknown_hostnames else 0
            print(f'  {pattern}: {count} devices ({percentage:.1f}%)')
    
    conn.close()

if __name__ == "__main__":
    check_unknown_devices()