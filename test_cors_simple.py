#!/usr/bin/env python3
# Simple CORS header test - no Unicode

import requests

print("Testing CORS Headers...")
print("-" * 60)

response = requests.post(
    'http://localhost:5000/query',
    json={'query': 'total revenue'},
    headers={
        'Origin': 'http://localhost:5175',
        'Content-Type': 'application/json'
    },
    timeout=5
)

print("Status Code:", response.status_code)
print("CORS Allow-Origin:", response.headers.get('Access-Control-Allow-Origin', 'NOT SET'))
print("CORS Allow-Methods:", response.headers.get('Access-Control-Allow-Methods', 'NOT SET'))

if response.headers.get('Access-Control-Allow-Origin'):
    print("\nSUCCESS: CORS headers are now being set!")
else:
    print("\nFAIL: CORS headers are still not set")
