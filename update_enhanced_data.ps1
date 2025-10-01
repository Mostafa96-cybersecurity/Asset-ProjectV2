# Enhanced Asset Data Updater
# Updates database with proper field mapping

Write-Host "🔧 DATABASE UPDATE UTILITY" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan
Write-Host ""

# Check if assets.db exists
if (-not (Test-Path "assets.db")) {
    Write-Host "❌ Database file not found!" -ForegroundColor Red
    exit 1
}

Write-Host "📊 Current database status:" -ForegroundColor Yellow

# Create a temporary Python script to update the database
$pythonScript = @"
import sqlite3
from datetime import datetime

# Enhanced data from our test
enhanced_data = {
    'ip_address': '10.0.21.47',
    'hostname': 'LT-3541-0012',
    'working_user': 'SQUARE\\mahmoud.hamed',
    'manufacturer': 'Dell Inc.',
    'model': 'Precision 3541',
    'os_name': 'Microsoft Windows 10 Pro',
    'memory_gb': 16,
    'cpu_cores': 8,
    'serial_number': '3ZX1Y43',
    'device_type': 'Workstation',
    'classification': 'Workstation',
    'data_source': 'Enhanced WMI Collection',
    'processor_name': 'Intel(R) Core(TM) i7-9850H CPU @ 2.60GHz',
    'workgroup': 'WORKGROUP',
    'bios_version': 'Dell Inc. 1.19.0',
    'chassis_type': 'Portable',
    'domain': 'SQUARE',
    'operating_system': 'Microsoft Windows 10 Pro',
    'system_manufacturer': 'Dell Inc.',
    'system_model': 'Precision 3541',
    'status': 'Active',
    'department': 'IT Department'
}

try:
    conn = sqlite3.connect('assets.db')
    cursor = conn.cursor()
    
    # Check current data
    cursor.execute('SELECT COUNT(*) FROM assets')
    total = cursor.fetchone()[0]
    print(f'📊 Total assets in database: {total}')
    
    # Check if our test device exists
    cursor.execute('SELECT hostname, working_user FROM assets WHERE ip_address = ?', ('10.0.21.47',))
    current = cursor.fetchone()
    
    if current:
        print(f'📋 Current data for 10.0.21.47:')
        print(f'   Hostname: {current[0]}')
        print(f'   User: {current[1]}')
    else:
        print('⚠️ Device 10.0.21.47 not found in database')
    
    # Update with enhanced data
    cursor.execute('''
        UPDATE assets 
        SET hostname = ?, working_user = ?, manufacturer = ?, model = ?,
            os_name = ?, memory_gb = ?, cpu_cores = ?, serial_number = ?,
            device_type = ?, classification = ?, data_source = ?,
            processor_name = ?, workgroup = ?, bios_version = ?,
            chassis_type = ?, domain = ?, operating_system = ?,
            system_manufacturer = ?, system_model = ?, status = ?,
            department = ?, last_updated = ?
        WHERE ip_address = ?
    ''', (
        enhanced_data['hostname'], enhanced_data['working_user'],
        enhanced_data['manufacturer'], enhanced_data['model'],
        enhanced_data['os_name'], enhanced_data['memory_gb'],
        enhanced_data['cpu_cores'], enhanced_data['serial_number'],
        enhanced_data['device_type'], enhanced_data['classification'],
        enhanced_data['data_source'], enhanced_data['processor_name'],
        enhanced_data['workgroup'], enhanced_data['bios_version'],
        enhanced_data['chassis_type'], enhanced_data['domain'],
        enhanced_data['operating_system'], enhanced_data['system_manufacturer'],
        enhanced_data['system_model'], enhanced_data['status'],
        enhanced_data['department'], datetime.now().isoformat(),
        enhanced_data['ip_address']
    ))
    
    if cursor.rowcount > 0:
        print(f'✅ Updated {cursor.rowcount} device(s)')
    else:
        print('⚠️ No devices were updated')
    
    conn.commit()
    
    # Verify the update
    cursor.execute('''
        SELECT hostname, working_user, manufacturer, model, os_name, memory_gb
        FROM assets WHERE ip_address = ?
    ''', ('10.0.21.47',))
    
    result = cursor.fetchone()
    if result:
        print('✅ Verification successful:')
        print(f'   Hostname: {result[0]}')
        print(f'   User: {result[1]}')
        print(f'   Manufacturer: {result[2]}')
        print(f'   Model: {result[3]}')
        print(f'   OS: {result[4]}')
        print(f'   Memory: {result[5]} GB')
    
    conn.close()
    print('🎉 Database update completed!')
    
except Exception as e:
    print(f'❌ Error: {e}')
"@

# Save the Python script to a temporary file
$pythonScript | Out-File -FilePath "temp_update.py" -Encoding UTF8

Write-Host "🔄 Updating database with enhanced data..." -ForegroundColor Green

# Try to run Python script
try {
    python temp_update.py
} catch {
    Write-Host "❌ Failed to run Python script" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}

# Clean up
if (Test-Path "temp_update.py") {
    Remove-Item "temp_update.py"
}

Write-Host ""
Write-Host "✅ Update process completed!" -ForegroundColor Green
Write-Host "💡 Check the web interface: http://127.0.0.1:8080" -ForegroundColor Cyan
Write-Host ""