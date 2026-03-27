#!/usr/bin/env python3
# Quick CORS test

import requests

print("Testing CORS Headers...")
print("-" * 60)

try:
    response = requests.post(
        'http://localhost:5000/query',
        json={'query': 'total revenue'},
        headers={
            'Origin': 'http://localhost:5175',
            'Content-Type': 'application/json'
        },
        timeout=5
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"CORS Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', '❌ NOT SET')}")
    print(f"CORS Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', '❌ NOT SET')}")
    print(f"CORS Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', '❌ NOT SET')}")
    
    if response.headers.get('Access-Control-Allow-Origin'):
        print("\n✅ CORS headers ARE being sent!")
    else:
        print("\n❌ CORS headers are NOT being sent!")
        
except Exception as e:
    print(f"Error: {e}")
