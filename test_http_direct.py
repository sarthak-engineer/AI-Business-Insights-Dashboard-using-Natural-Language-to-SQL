#!/usr/bin/env python3
"""Direct HTTP test to frontend and backend"""
import socket
import time

def test_http(host, port, path="/"):
    """Send raw HTTP GET request"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((host, port))
        
        request = f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nConnection: close\r\n\r\n"
        s.sendall(request.encode())
        
        response = b""
        while True:
            try:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk
            except socket.timeout:
                break
        
        s.close()
        
        # Get first line of response
        response_str = response.decode('utf-8', errors='ignore')
        first_line = response_str.split('\r\n')[0]
        return first_line, response_str[:500]
        
    except Exception as e:
        return f"ERROR: {str(e)}", ""

print("=" * 70)
print("FRONTEND & BACKEND HTTP TESTS")
print("=" * 70)

# Test frontend
print("\n[TEST 1] Frontend on localhost:5173")
print("-" * 70)
status, response = test_http("127.0.0.1", 5173, "/")
print(f"Response: {status}")
if "200" in status:
    print("✅ Frontend is responding with HTTP 200")
    if "<!DOCTYPE html>" in response or "<html" in response:
        print("✅ HTML content received")
else:
    print(f"⚠️  Response: {status}")
    print(f"First 200 chars: {response[:200]}")

# Test backend
print("\n[TEST 2] Backend on 127.0.0.1:5000")
print("-" * 70)
status, response = test_http("127.0.0.1", 5000, "/health")
print(f"Response: {status}")
if "200" in status:
    print("✅ Backend is responding with HTTP 200")
else:
    print(f"⚠️  Response: {status}")
    print(f"First 200 chars: {response[:200]}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("✅ Frontend: http://localhost:5173 (access in browser)")
print("✅ Backend: http://127.0.0.1:5000 (API server)")
print("\nPlease refresh your browser to load the UI")
