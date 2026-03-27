#!/usr/bin/env python3
# Test to see if decorator is being called

import requests

response = requests.post(
    'http://localhost:5000/query',
    json={'query': 'revenue'},
    headers={'Origin': 'http://localhost:5175'},
    timeout=5
)

print("Test Header (X-Test-Header):", response.headers.get('X-Test-Header', 'NOT FOUND'))
print("CORS Applied (X-CORS-Applied):", response.headers.get('X-CORS-Applied', 'NOT FOUND'))
print("Access-Control-Allow-Origin:", response.headers.get('Access-Control-Allow-Origin', 'NOT SET'))
