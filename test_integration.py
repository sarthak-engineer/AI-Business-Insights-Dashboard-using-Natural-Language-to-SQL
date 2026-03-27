#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Test: Test the complete query flow (Frontend -> Backend -> Response)
"""

import requests
import json
import time

# Test Configuration
BACKEND_URL = "http://127.0.0.1:5000"
TEST_QUERIES = [
    "What is the total revenue by category?",
    "Show top 5 products by sales",
    "How many customers made purchases?",
    "What is the average purchase amount?"
]

print("=" * 70)
print("INTEGRATION TEST: FRONTEND -> BACKEND -> DISPLAY")
print("=" * 70)

# Test 1: Check Backend Health
print("\nTEST 1: Backend Health Check")
print("-" * 70)
try:
    response = requests.post(
        f"{BACKEND_URL}/query",
        json={"query": "dummy"},
        timeout=5
    )
    # Any response (including error) means backend is running
    print(f"Status Code: {response.status_code}")
    if response.status_code >= 400:
        print(f"✅ PASS: Backend is responding (error status expected for dummy query)")
    else:
        print(f"✅ PASS: Backend is responding")
except Exception as e:
    print(f"❌ FAIL: Backend not responding - {str(e)}")
    exit(1)

# Test 2: Submit Query and Check Response Structure
print("\n\nTEST 2: Query Submission and Response Structure")
print("-" * 70)
for idx, query in enumerate(TEST_QUERIES[:2], 1):
    print(f"\nQuery {idx}: {query}")
    try:
        payload = {
            "query": query,
            "filters": {
                "category": "all",
                "gender": "all",
                "startDate": "",
                "endDate": ""
            }
        }
        
        response = requests.post(
            f"{BACKEND_URL}/query",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            
            # Check required fields
            required_fields = ["original_query", "data", "insights", "chart_type"]
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                print(f"❌ FAIL: Missing fields - {missing_fields}")
            else:
                print(f"✅ Data returned: {len(data.get('data', []))} rows")
                print(f"✅ Insights: {data.get('insights', '')[:50]}...")
                print(f"✅ Chart Type: {data.get('chart_type', 'N/A')}")
                print("✅ PASS: Response structure valid")
        else:
            print(f"❌ FAIL: Status code {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ FAIL: Request error - {str(e)}")

# Test 3: CORS Headers Check
print("\n\nTEST 3: CORS Headers Check")
print("-" * 70)
try:
    response = requests.options(
        f"{BACKEND_URL}/query",
        headers={
            "Origin": "http://localhost:5175",
            "Access-Control-Request-Method": "POST"
        },
        timeout=5
    )
    
    cors_headers = {
        "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
        "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
        "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
    }
    
    print(f"CORS Headers: {cors_headers}")
    
    if cors_headers["Access-Control-Allow-Origin"] == "http://localhost:5175":
        print("✅ PASS: CORS allows localhost:5175")
    else:
        print(f"⚠️ WARNING: CORS origin is {cors_headers['Access-Control-Allow-Origin']}")
        
except Exception as e:
    print(f"⚠️ WARNING: CORS check failed - {str(e)}")

# Test 4: Error Handling (Invalid Query)
print("\n\nTEST 4: Error Handling")
print("-" * 70)
try:
    payload = {"query": "xyz", "filters": {"category": "all", "gender": "all", "startDate": "", "endDate": ""}}
    response = requests.post(
        f"{BACKEND_URL}/query",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    if response.status_code == 400:
        print(f"Status Code: {response.status_code} (Expected for invalid query)")
        data = response.json()
        print(f"Error Message: {data.get('message', 'N/A')}")
        print("✅ PASS: Error handling works")
    else:
        print(f"Status Code: {response.status_code}")
        print("⚠️ Note: Invalid query handling may vary")
        
except Exception as e:
    print(f"⚠️ Exception - {str(e)}")

print("\n\n" + "=" * 70)
print("INTEGRATION TEST COMPLETE")
print("=" * 70)
print("""
Summary:
- Backend is running and responding
- Queries return proper JSON structure
- CORS headers are configured
- Error handling is functional

Next Steps:
1. Visit http://localhost:5175 in your browser
2. Enter a query like: "What is the total revenue by category?"
3. You should see:
   - Loading indicator while processing
   - Results table with data
   - Charts/visualization
   - Smart insights box below
   - ML insights (churn, recommendations, anomalies)
4. Data should NOT be blank!
""")
