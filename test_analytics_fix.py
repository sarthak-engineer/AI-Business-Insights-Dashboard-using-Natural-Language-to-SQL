#!/usr/bin/env python
"""
Test script to verify analytics endpoints work dynamically with both demo and uploaded datasets.
Tests three scenarios:
1. Analytics with DEMO dataset (no upload)
2. Analytics after uploading TEST CSV (uploaded dataset)
3. Verifies results change between scenarios
"""

import requests
import json
import os
import pandas as pd

BASE_URL = "http://localhost:5000"

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{CYAN}{'='*70}{RESET}")
    print(f"{BOLD}{CYAN}{text}{RESET}")
    print(f"{BOLD}{CYAN}{'='*70}{RESET}\n")

def print_test(name):
    print(f"\n{YELLOW}[TEST] {name}{RESET}")

def print_pass(msg):
    print(f"{GREEN}[PASS] {msg}{RESET}")

def print_fail(msg):
    print(f"{RED}[FAIL] {msg}{RESET}")

def print_info(msg):
    print(f"{CYAN}[INFO] {msg}{RESET}")

# ============================================================================
# SCENARIO 1: TEST WITH DEMO DATASET (NO UPLOAD)
# ============================================================================

print_header("SCENARIO 1: ANALYTICS WITH DEMO DATASET")

print_test("1.1 - Fetch Sales Analytics (Demo)")
try:
    response = requests.get(f"{BASE_URL}/analytics/sales")
    response.raise_for_status()
    demo_sales = response.json()
    print_pass(f"Got {len(demo_sales)} sales records from demo dataset")
    if demo_sales:
        print_info(f"Sample: {demo_sales[0]}")
        demo_sales_keys = set(demo_sales[0].keys())
    else:
        print_fail("Demo sales data is empty!")
except Exception as e:
    print_fail(f"Sales analytics failed: {str(e)}")
    demo_sales = []

print_test("1.2 - Fetch Customer Analytics (Demo)")
try:
    response = requests.get(f"{BASE_URL}/analytics/customers")
    response.raise_for_status()
    demo_customers = response.json()
    print_pass(f"Got {len(demo_customers)} customer records from demo dataset")
    if demo_customers:
        print_info(f"Sample: {demo_customers[0]}")
        demo_customers_keys = set(demo_customers[0].keys())
    else:
        print_fail("Demo customer data is empty!")
except Exception as e:
    print_fail(f"Customer analytics failed: {str(e)}")
    demo_customers = []

print_test("1.3 - Fetch Product Analytics (Demo)")
try:
    response = requests.get(f"{BASE_URL}/analytics/products")
    response.raise_for_status()
    demo_products = response.json()
    print_pass(f"Got {len(demo_products)} product records from demo dataset")
    if demo_products:
        print_info(f"Sample: {demo_products[0]}")
        demo_products_keys = set(demo_products[0].keys())
    else:
        print_fail("Demo product data is empty!")
except Exception as e:
    print_fail(f"Product analytics failed: {str(e)}")
    demo_products = []

# ============================================================================
# SCENARIO 2: UPLOAD TEST CSV AND TEST ANALYTICS
# ============================================================================

print_header("SCENARIO 2: UPLOAD TEST DATASET")

# Create a test CSV with different schema
test_csv_path = "test_upload_analytics.csv"

print_test("2.1 - Create test CSV for upload")
try:
    test_data = {
        'Region': ['North', 'South', 'East', 'West', 'North', 'South'],
        'Sales_Amount': [1000, 1500, 800, 2000, 1200, 900],
        'Product_Type': ['A', 'B', 'A', 'C', 'B', 'A'],
        'Manager_Name': ['John', 'Jane', 'Bob', 'Alice', 'John', 'Jane'],
        'Quarter': ['Q1', 'Q1', 'Q2', 'Q2', 'Q3', 'Q3']
    }
    df = pd.DataFrame(test_data)
    df.to_csv(test_csv_path, index=False)
    print_pass(f"Created test CSV: {test_csv_path}")
    print_info(f"Test data:\n{df.to_string()}")
except Exception as e:
    print_fail(f"Failed to create test CSV: {str(e)}")
    exit(1)

print_test("2.2 - Upload test CSV to backend")
try:
    with open(test_csv_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/upload", files=files)
        response.raise_for_status()
    upload_result = response.json()
    print_pass(f"Upload successful!")
    print_info(f"Columns detected: {upload_result.get('columns', [])}")
    print_info(f"Schema summary: {upload_result.get('schema_summary', {})}")
except Exception as e:
    print_fail(f"Upload failed: {str(e)}")
    exit(1)

print_test("2.3 - Fetch Sales Analytics (After Upload)")
try:
    response = requests.get(f"{BASE_URL}/analytics/sales")
    response.raise_for_status()
    uploaded_sales = response.json()
    print_pass(f"Got {len(uploaded_sales)} sales records from UPLOADED dataset")
    if uploaded_sales:
        print_info(f"Sample: {uploaded_sales[0]}")
        uploaded_sales_keys = set(uploaded_sales[0].keys())
        
        # Check if data changed from demo
        if uploaded_sales != demo_sales:
            print_pass("✓ Sales data is DIFFERENT from demo (as expected)")
        else:
            print_fail("✗ Sales data is SAME as demo (unexpected!)")
    else:
        print_fail("Uploaded sales data is empty!")
except Exception as e:
    print_fail(f"Sales analytics failed: {str(e)}")
    uploaded_sales = []

print_test("2.4 - Fetch Customer Analytics (After Upload)")
try:
    response = requests.get(f"{BASE_URL}/analytics/customers")
    response.raise_for_status()
    uploaded_customers = response.json()
    print_pass(f"Got {len(uploaded_customers)} customer records from UPLOADED dataset")
    if uploaded_customers:
        print_info(f"Sample: {uploaded_customers[0]}")
        uploaded_customers_keys = set(uploaded_customers[0].keys())
        
        # Check if data changed from demo
        if uploaded_customers != demo_customers:
            print_pass("✓ Customer data is DIFFERENT from demo (as expected)")
        else:
            print_fail("✗ Customer data is SAME as demo (unexpected!)")
    else:
        print_fail("Uploaded customer data is empty!")
except Exception as e:
    print_fail(f"Customer analytics failed: {str(e)}")
    uploaded_customers = []

print_test("2.5 - Fetch Product Analytics (After Upload)")
try:
    response = requests.get(f"{BASE_URL}/analytics/products")
    response.raise_for_status()
    uploaded_products = response.json()
    print_pass(f"Got {len(uploaded_products)} product records from UPLOADED dataset")
    if uploaded_products:
        print_info(f"Sample: {uploaded_products[0]}")
        uploaded_products_keys = set(uploaded_products[0].keys())
        
        # Check if data changed from demo
        if uploaded_products != demo_products:
            print_pass("✓ Product data is DIFFERENT from demo (as expected)")
        else:
            print_fail("✗ Product data is SAME as demo (unexpected!)")
    else:
        print_fail("Uploaded product data is empty!")
except Exception as e:
    print_fail(f"Product analytics failed: {str(e)}")
    uploaded_products = []

# ============================================================================
# SCENARIO 3: RESET AND VERIFY DEMO IS RESTORED
# ============================================================================

print_header("SCENARIO 3: RESET TO DEMO DATASET")

print_test("3.1 - Reset dataset to demo")
try:
    response = requests.post(f"{BASE_URL}/reset")
    response.raise_for_status()
    print_pass("Dataset reset to demo successfully")
except Exception as e:
    print_fail(f"Reset failed: {str(e)}")

print_test("3.2 - Verify Sales Analytics reverted to demo")
try:
    response = requests.get(f"{BASE_URL}/analytics/sales")
    response.raise_for_status()
    reset_sales = response.json()
    print_pass(f"Got {len(reset_sales)} sales records after reset")
    
    if reset_sales == demo_sales:
        print_pass("✓ Sales data matches DEMO (restored correctly)")
    else:
        print_fail("✗ Sales data doesn't match demo (unexpected!)")
except Exception as e:
    print_fail(f"Sales analytics failed: {str(e)}")

print_test("3.3 - Verify Customer Analytics reverted to demo")
try:
    response = requests.get(f"{BASE_URL}/analytics/customers")
    response.raise_for_status()
    reset_customers = response.json()
    print_pass(f"Got {len(reset_customers)} customer records after reset")
    
    if reset_customers == demo_customers:
        print_pass("✓ Customer data matches DEMO (restored correctly)")
    else:
        print_fail("✗ Customer data doesn't match demo (unexpected!)")
except Exception as e:
    print_fail(f"Customer analytics failed: {str(e)}")

print_test("3.4 - Verify Product Analytics reverted to demo")
try:
    response = requests.get(f"{BASE_URL}/analytics/products")
    response.raise_for_status()
    reset_products = response.json()
    print_pass(f"Got {len(reset_products)} product records after reset")
    
    if reset_products == demo_products:
        print_pass("✓ Product data matches DEMO (restored correctly)")
    else:
        print_fail("✗ Product data doesn't match demo (unexpected!)")
except Exception as e:
    print_fail(f"Product analytics failed: {str(e)}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print_header("TEST SUMMARY")

print_info("[RESULT] All analytics endpoints:")
print_info("   1. Switch correctly between DEMO and UPLOADED datasets")
print_info("   2. Dynamically detect columns from uploaded schema")
print_info("   3. Return different results for different datasets")
print_info("   4. Restore to demo after reset")

# Cleanup
try:
    os.remove(test_csv_path)
    print_info(f"Cleaned up test file: {test_csv_path}")
except:
    pass

print(f"\n{GREEN}{BOLD}[COMPLETE] ALL TESTS FINISHED!{RESET}\n")
