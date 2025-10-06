#!/usr/bin/env python3
import requests
import json

try:
    response = requests.get('http://127.0.0.1:5000/api/assets', timeout=5)
    data = response.json()
    
    print(f'API Response Status: {response.status_code}')
    print(f'Total assets returned: {len(data.get("assets", []))}')
    
    if data.get('assets'):
        asset = data['assets'][0]
        print(f'\nFIRST ASSET KEYS ({len(asset.keys())} keys):')
        for i, key in enumerate(asset.keys()):
            value = asset[key]
            if value and len(str(value)) > 40:
                value_display = str(value)[:37] + '...'
            else:
                value_display = value
            print(f'{i:2d}. {key:30s} = {value_display}')
        
        # Check for uptime_formatted specifically
        if 'uptime_formatted' in asset:
            print(f'\nuptime_formatted found: {asset["uptime_formatted"]}')
        else:
            print(f'\nuptime_formatted NOT found in API response')
            
        # Check for common uptime-related fields
        uptime_fields = [k for k in asset.keys() if 'uptime' in k.lower()]
        if uptime_fields:
            print(f'Uptime-related fields found: {uptime_fields}')
        else:
            print(f'No uptime-related fields found')
    else:
        print('No assets in response')
        print(f'Response data: {data}')
        
except Exception as e:
    print(f'Error calling API: {e}')