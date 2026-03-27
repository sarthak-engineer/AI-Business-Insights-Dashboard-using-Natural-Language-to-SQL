#!/usr/bin/env python3
# Debug test with detailed output

import requests
import json

print("Testing CORS with detailed output...")
print("=" * 60)

# Make a request with Origin header
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
print(f"\nAll Response Headers:")
for header, value in response.headers.items():
    print(f"  {header}: {value}")

print(f"\nCORS-specific headers:")
print(f"  Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', '❌ NOT SET')}")
print(f"  Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', '❌ NOT SET')}")
print(f"  Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', '❌ NOT SET')}")

# Also test OPTIONS request
print("\n" + "=" * 60)
print("Testing OPTIONS request (CORS preflight)...")
print("=" * 60)

options_response = requests.options(
    'http://localhost:5000/query',
    headers={
        'Origin': 'http://localhost:5175',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
    },
    timeout=5
)

print(f"Status Code: {options_response.status_code}")
print(f"\nOPTIONS Response Headers:")
for header, value in options_response.headers.items():
    print(f"  {header}: {value}")
