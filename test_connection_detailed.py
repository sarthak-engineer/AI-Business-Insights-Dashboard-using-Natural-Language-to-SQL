#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detailed Diagnostics: Frontend -> Backend Connection
"""

import requests
import json
import time
from urllib.parse import urljoin

print("=" * 80)
print("DETAILED CONNECTION DIAGNOSTICS")
print("=" * 80)

# Test Configuration
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 5000
BACKEND_BASE = f"http://{BACKEND_HOST}:{BACKEND_PORT}"
FRONTEND_URL = "http://localhost:5175"

print(f"\nBackend: {BACKEND_BASE}")
print(f"Frontend: {FRONTEND_URL}")

# Test 1: Direct Backend Connection
print("\n" + "=" * 80)
print("TEST 1: Direct Backend Connectivity")
print("=" * 80)
try:
    response = requests.post(
        f"{BACKEND_BASE}/query",
        json={"query": "total revenue by category"},
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print(f"✅ Backend is accessible")
    print(f"   Status: {response.status_code}")
    print(f"   Response size: {len(response.text)} bytes")
except requests.exceptions.ConnectionError as e:
    print(f"❌ UNABLE TO CONNECT: {e}")
    print("   Backend is NOT running or not accessible")
except requests.exceptions.Timeout:
    print(f"❌ REQUEST TIMEOUT: Backend took too long to respond")
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")

# Test 2: CORS Headers Simulation (Frontend Request)
print("\n" + "=" * 80)
print("TEST 2: CORS Headers Check (Simulating Browser Request)")
print("=" * 80)
try:
    headers = {
        "Content-Type": "application/json",
        "Origin": FRONTEND_URL,
        "Referer": f"{FRONTEND_URL}/",
    }
    
    response = requests.post(
        f"{BACKEND_BASE}/query",
        json={"query": "total revenue by category"},
        headers=headers,
        timeout=5
    )
    
    print(f"✅ Request successful")
    print(f"   Status: {response.status_code}")
    print(f"   CORS Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
    print(f"   Response type: {response.headers.get('Content-Type', 'unknown')}")
    
    # Check if it's JSON
    try:
        data = response.json()
        print(f"   Response is valid JSON")
        print(f"   Keys: {list(data.keys())[:5]} (showing first 5)")
    except:
        print(f"   ⚠️ Response is NOT valid JSON")
        print(f"   First 100 chars: {response.text[:100]}")
        
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")

# Test 3: OPTIONS Request (CORS Preflight)
print("\n" + "=" * 80)
print("TEST 3: CORS Preflight (OPTIONS) Request")
print("=" * 80)
try:
    headers = {
        "Origin": FRONTEND_URL,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    }
    
    response = requests.options(
        f"{BACKEND_BASE}/query",
        headers=headers,
        timeout=5
    )
    
    print(f"✅ OPTIONS request successful")
    print(f"   Status: {response.status_code}")
    print(f"   Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
    print(f"   Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'NOT SET')}")
    print(f"   Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'NOT SET')}")
    
    if response.status_code >= 400:
        print(f"   ⚠️ OPTIONS returned error status (may still work in browser)")
        
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")

# Test 4: Invalid Query (Like Frontend Error Case)
print("\n" + "=" * 80)
print("TEST 4: Error Response Structure (Invalid Query)")
print("=" * 80)
try:
    response = requests.post(
        f"{BACKEND_BASE}/query",
        json={"query": "xyz"},
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Response keys: {list(data.keys())}")
    print(f"   Message: {data.get('message', 'N/A')[:100]}")
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")

# Test 5: localhost vs 127.0.0.1
print("\n" + "=" * 80)
print("TEST 5: localhost vs 127.0.0.1 (Frontend Uses localhost)")
print("=" * 80)
try:
    # Frontend uses localhost, so let's test that
    response = requests.post(
        "http://localhost:5000/query",
        json={"query": "total revenue"},
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print(f"✅ localhost:5000 is accessible")
    print(f"   Status: {response.status_code}")
except requests.exceptions.ConnectionRefusedError:
    print(f"❌ localhost:5000 CONNECTION REFUSED")
    print(f"   This is likely the issue!")
except Exception as e:
    print(f"⚠️ {type(e).__name__}: {e}")

# Test 6: Network Interface Check
print("\n" + "=" * 80)
print("TEST 6: Network Configuration")
print("=" * 80)
import socket
try:
    localhost_ip = socket.gethostbyname('localhost')
    print(f"✅ localhost resolves to: {localhost_ip}")
except:
    print(f"❌ Cannot resolve localhost")

try:
    hostname = socket.gethostname()
    hostname_ip = socket.gethostbyname(hostname)
    print(f"✅ Hostname '{hostname}' resolves to: {hostname_ip}")
except:
    print(f"❌ Cannot resolve hostname")

# Test 7: Frontend would see this error
print("\n" + "=" * 80)
print("TEST 7: What Frontend Error Handling Would Show")
print("=" * 80)
try:
    response = requests.post(
        "http://localhost:5000/query",
        json={"query": "test", "filters": {"category": "all", "gender": "all"}},
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    
    # Frontend error handling logic
    if response.status_code == 200:
        msg = response.json().get('message', 'Success')
    else:
        msg = response.json().get('error') or response.json().get('message') or 'Backend connection failed.'
    
    print(f"✅ Frontend would receive: {msg[:80]}...")
    
except requests.exceptions.ConnectionError:
    print(f"❌ Frontend would display: 'Backend connection failed.'")
    print(f"   (Because axios catches ConnectionError with generic message)")
except requests.exceptions.Timeout:
    print(f"❌ Frontend would display: 'Backend connection failed.'")
    print(f"   (Because axios timeout results in generic error)")
except Exception as e:
    print(f"❌ Frontend would display: 'Backend connection failed.'")
    print(f"   (Actual error: {type(e).__name__})")

print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)
print("""
If backend is accessible but frontend still shows "Backend connection failed":

1. **Clear Browser Cache & Reload**
   - Ctrl+Shift+Delete (open cache settings)
   - Select "Cached images and files"
   - Click "Clear now"
   - Reload the page

2. **Check Browser Console**
   - F12 to open Developer Tools
   - Switch to Console tab
   - Look for CORS errors or network errors
   - Note the exact error message

3. **Verify Frontend URL**
   - Make sure you're visiting http://localhost:5175 (not 5173)
   - Or whatever port npm shows when it starts

4. **Check Network Tab**
   - F12 → Network tab
   - Try making a query
   - Look for failed POST requests
   - Click on the failed request to see details

5. **Environment Variables**
   - Make sure frontend and backend can see each other
   - Check that no proxy is interfering
   - Verify firewall isn't blocking port 5000
""")
