#!/usr/bin/env python3
"""
End-to-end API test for the input validation improvements.
Tests the /query endpoint with various inputs.
"""

import requests
import json
import time

# Configuration
API_URL = "http://localhost:5000"
QUERY_ENDPOINT = f"{API_URL}/query"

def test_api():
    """Test the /query endpoint with various inputs."""
    
    test_cases = [
        {
            "name": "Valid Query - Total Sales",
            "query": "total sales",
            "expect_error": False,
            "description": "Should return SQL and data"
        },
        {
            "name": "Valid Query - Top Products",
            "query": "top 5 products by revenue",
            "expect_error": False,
            "description": "Should return SQL and data"
        },
        {
            "name": "Garbage Input",
            "query": "yh566th6yt5h",
            "expect_error": True,
            "description": "Should reject with helpful suggestions"
        },
        {
            "name": "Unclear Query",
            "query": "sales??",
            "expect_error": True,
            "description": "Should reject with helpful suggestions"
        },
        {
            "name": "Too Short",
            "query": "a",
            "expect_error": True,
            "description": "Should reject as too short"
        },
        {
            "name": "Valid - Customer Count",
            "query": "how many customers",
            "expect_error": False,
            "description": "Should generate count query"
        }
    ]
    
    print("\n" + "="*70)
    print("  API ENDPOINT VALIDATION TESTS")
    print("="*70 + "\n")
    
    for test in test_cases:
        print(f"Test: {test['name']}")
        print(f"Query: '{test['query']}'")
        print(f"Expected: {'Error with suggestions' if test['expect_error'] else 'Success with data'}")
        print(f"Details: {test['description']}\n")
        
        try:
            payload = {"query": test["query"]}
            response = requests.post(QUERY_ENDPOINT, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Response Status: {response.status_code}")
                print(f"  Response Keys: {list(data.keys())}")
                
                if test["expect_error"]:
                    print(f"  ⚠ Expected error but got success - might be valid query")
                else:
                    # Check that helpful data is returned
                    if 'data' in data and len(data.get('data', [])) > 0:
                        print(f"  Data rows: {len(data['data'])}")
                    if 'sql' in data:
                        print(f"  SQL generated: {len(data['sql'])} chars")
                        
            elif response.status_code == 400:
                data = response.json()
                print(f"✓ Response Status: {response.status_code} (Error)")
                message = data.get('message', '')
                
                # Check if helpful suggestions are in the message
                if "Try:" in message or "•" in message:
                    print(f"  ✓ Helpful suggestions provided")
                    # Show first suggestion
                    lines = message.split('\n')
                    if len(lines) > 1:
                        print(f"    Example: {lines[1]}")
                else:
                    print(f"  Message: {message[:80]}...")
                
                if not test["expect_error"]:
                    print(f"  ⚠ Expected success but got error")
                    
            else:
                print(f"✗ Unexpected status: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print(f"✗ ERROR: Cannot connect to API at {API_URL}")
            print(f"  Make sure the Flask backend is running on port 5000")
            break
        except Exception as e:
            print(f"✗ ERROR: {str(e)}")
        
        print("-" * 70 + "\n")
        time.sleep(0.5)  # Small delay between requests

if __name__ == "__main__":
    print("Starting API validation tests...")
    print(f"API endpoint: {QUERY_ENDPOINT}")
    print("Note: Make sure the Flask backend is running before running this test\n")
    
    try:
        # Check if API is running
        response = requests.get(f"{API_URL}/health", timeout=2)
        print(f"✓ API is running\n")
    except:
        print(f"⚠ API doesn't appear to be running at {API_URL}")
        print(f"  To start the backend, run: python backend/app.py\n")
    
    test_api()
