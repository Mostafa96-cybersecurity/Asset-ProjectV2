#!/usr/bin/env python3
"""
Device Classification Analysis
Check current device types and classification strategy
"""

import sqlite3
import json

def analyze_device_classification():
    # Connect to database
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Get all unique device types
    cursor.execute('SELECT DISTINCT device_type FROM assets WHERE device_type IS NOT NULL ORDER BY device_type')
    device_types = [row[0] for row in cursor.fetchall()]
    
    print('=== ALL DEVICE TYPES IN DATABASE ===')
    for i, device_type in enumerate(device_types, 1):
        print(f'{i:2d}. {device_type}')
    
    print(f'\nTotal unique device types: {len(device_types)}')
    
    # Get devices with OS information
    cursor.execute('''
        SELECT hostname, device_type, operating_system, os_name, nmap_os_family, 
               nmap_device_type, os_fingerprint, open_ports 
        FROM assets 
        WHERE device_type IS NOT NULL 
        ORDER BY last_seen DESC 
        LIMIT 20
    ''')
    
    devices = cursor.fetchall()
    
    print('\n=== RECENT DEVICES WITH OS/NMAP INFO ===')
    for hostname, dtype, os_sys, os_name, nmap_os, nmap_dtype, os_fp, ports in devices:
        print(f'\n📍 {hostname}')
        print(f'   Device Type: {dtype}')
        print(f'   Operating System: {os_sys or "None"}')
        print(f'   OS Name: {os_name or "None"}')
        print(f'   NMAP OS Family: {nmap_os or "None"}')
        print(f'   NMAP Device Type: {nmap_dtype or "None"}')
        print(f'   OS Fingerprint: {os_fp or "None"}')
        if ports:
            try:
                port_list = json.loads(ports)
                print(f'   Open Ports: {port_list[:10]}')  # Show first 10 ports
            except:
                print(f'   Open Ports: {ports[:50]}...')
    
    # Check NMAP-based classification patterns
    print('\n=== NMAP OS FAMILY ANALYSIS ===')
    cursor.execute('SELECT nmap_os_family, COUNT(*) FROM assets WHERE nmap_os_family IS NOT NULL GROUP BY nmap_os_family ORDER BY COUNT(*) DESC')
    nmap_os_families = cursor.fetchall()
    
    for os_family, count in nmap_os_families:
        print(f'   {os_family}: {count} devices')
    
    print('\n=== NMAP DEVICE TYPE ANALYSIS ===')
    cursor.execute('SELECT nmap_device_type, COUNT(*) FROM assets WHERE nmap_device_type IS NOT NULL GROUP BY nmap_device_type ORDER BY COUNT(*) DESC')
    nmap_device_types = cursor.fetchall()
    
    for dev_type, count in nmap_device_types:
        print(f'   {dev_type}: {count} devices')
    
    # Check classification correlation
    print('\n=== DEVICE TYPE vs NMAP CORRELATION ===')
    cursor.execute('''
        SELECT device_type, nmap_os_family, nmap_device_type, COUNT(*) 
        FROM assets 
        WHERE device_type IS NOT NULL 
        GROUP BY device_type, nmap_os_family, nmap_device_type 
        ORDER BY COUNT(*) DESC 
        LIMIT 15
    ''')
    
    correlations = cursor.fetchall()
    for dev_type, nmap_os, nmap_dtype, count in correlations:
        print(f'   {dev_type} ← NMAP OS: {nmap_os or "None"}, NMAP Type: {nmap_dtype or "None"} ({count} devices)')
    
    conn.close()

if __name__ == "__main__":
    analyze_device_classification()