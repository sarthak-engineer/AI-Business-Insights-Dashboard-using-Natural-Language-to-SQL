#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Enhanced Smart Insights Engine
Validates that new insight generation works with small, medium, and large datasets
"""

import sys
import os
import pandas as pd

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Import the insight functions
from app import generate_insight, generate_python_summary

print("=" * 70)
print("ENHANCED SMART INSIGHTS ENGINE - TEST SUITE")
print("=" * 70)

# Test 1: Empty Dataset
print("\n\n📊 TEST 1: Empty Dataset")
print("-" * 70)
empty_data = []
result = generate_insight(empty_data)
print(f"Input: {empty_data}")
print(f"Output: {result}")
assert "No data available" in result, "❌ Failed: Should handle empty data gracefully"
print("✅ PASS")

# Test 2: Single Data Point
print("\n\n📊 TEST 2: Single Data Point (Edge Case)")
print("-" * 70)
single_data = [{"category": "Electronics", "value": 5000}]
result = generate_insight(single_data)
print(f"Input: {single_data}")
print(f"Output:\n{result}\n")
assert "Single data point" in result, "❌ Failed: Should handle single point"
print("✅ PASS")

# Test 3: Small Dataset (2-3 records)
print("\n\n📊 TEST 3: Small Dataset (2-3 Records)")
print("-" * 70)
small_data = [
    {"category": "Electronics", "value": 15000},
    {"category": "Clothing", "value": 3000},
    {"category": "Home", "value": 2000}
]
result = generate_insight(small_data)
print(f"Input: {small_data}")
print(f"Output:\n{result}\n")
assert len(result) > 50, "❌ Failed: Should generate meaningful insights"
assert "Limited data" not in result.split('\n')[0], "❌ Failed: Shouldn't show 'Not enough data' in first line"
print("✅ PASS")

# Test 4: Medium Dataset (5-10 records)
print("\n\n📊 TEST 4: Medium Dataset (5-10 Records)")
print("-" * 70)
medium_data = [
    {"category": "Electronics", "value": 15000},
    {"category": "Clothing", "value": 8000},
    {"category": "Home", "value": 5000},
    {"category": "Books", "value": 3000},
    {"category": "Sports", "value": 2000}
]
result = generate_insight(medium_data)
print(f"Input: {medium_data}")
print(f"Output:\n{result}\n")
assert "Electronics" in result, "❌ Failed: Should identify top performer"
assert len(result) > 100, "❌ Failed: Should generate meaningful, detailed insights"
print("✅ PASS")

# Test 5: Large Dataset
print("\n\n📊 TEST 5: Large Dataset (20+ Records)")
print("-" * 70)
large_data = [
    {"category": f"Category_{i}", "value": 10000 - (i * 100)} 
    for i in range(20)
]
result = generate_insight(large_data)
print(f"Input: {len(large_data)} records")
print(f"Output:\n{result}\n")
assert "Category_0" in result or "High" in result, "❌ Failed: Should analyze large dataset"
print("✅ PASS")

# Test 6: Balanced Distribution
print("\n\n📊 TEST 6: Balanced Distribution (Equal Values)")
print("-" * 70)
balanced_data = [
    {"category": "A", "value": 1000},
    {"category": "B", "value": 1000},
    {"category": "C", "value": 1000},
    {"category": "D", "value": 1000}
]
result = generate_insight(balanced_data)
print(f"Input: {balanced_data}")
print(f"Output:\n{result}\n")
assert "distributed" in result.lower() or "balanced" in result.lower(), "❌ Failed: Should detect balanced dist"
print("✅ PASS")

# Test 7: Heavy Skew (One dominant)
print("\n\n📊 TEST 7: Heavy Skew (One Dominant Category)")
print("-" * 70)
skewed_data = [
    {"category": "Electronics", "value": 50000},
    {"category": "Clothing", "value": 2000},
    {"category": "Home", "value": 1500}
]
result = generate_insight(skewed_data)
print(f"Input: {skewed_data}")
print(f"Output:\n{result}\n")
assert "dominates" in result.lower() or "dominant" in result.lower(), "❌ Failed: Should detect dominance"
assert "50" in result or "Electronics" in result, "❌ Failed: Should mention top category"
print("✅ PASS")

# Test 8: DataFrame Test
print("\n\n📊 TEST 8: DataFrame Input (generate_python_summary)")
print("-" * 70)
df = pd.DataFrame({
    'category': ['Electronics', 'Clothing', 'Home'],
    'sales': [20000, 8000, 5000]
})
result = generate_python_summary(df)
print(f"Input DataFrame:\n{df}\n")
print(f"Output:\n{result}\n")
assert "Electronics" in result, "❌ Failed: Should generate insights from DataFrame"
print("✅ PASS")

# Test 9: Underperformance Detection
print("\n\n📊 TEST 9: Underperformance Detection")
print("-" * 70)
underperf_data = [
    {"category": "Premium", "value": 10000},
    {"category": "Mid", "value": 5000},
    {"category": "Budget", "value": 500}
]
result = generate_insight(underperf_data)
print(f"Input: {underperf_data}")
print(f"Output:\n{result}\n")
assert "underperform" in result.lower() or "below" in result.lower(), "❌ Failed: Should detect underperformance"
print("✅ PASS")

# Test 10: Multiple Insights (Should return 2-3 insights)
print("\n\n📊 TEST 10: Multiple Insights (2-3 Lines)")
print("-" * 70)
multi_data = [
    {"category": "A", "value": 30000},
    {"category": "B", "value": 10000},
    {"category": "C", "value": 5000},
    {"category": "D", "value": 1000},
    {"category": "E", "value": 500}
]
result = generate_insight(multi_data)
lines = result.split('\n')
print(f"Input: {multi_data}")
print(f"Output ({len(lines)} lines):\n{result}\n")
assert len(lines) >= 2, f"❌ Failed: Should return multiple insights (got {len(lines)} lines)"
print("✅ PASS")

print("\n\n" + "=" * 70)
print("✅ ALL TESTS PASSED! Enhanced Insights Engine is working correctly")
print("=" * 70)
print("\nSummary of Improvements:")
print("  ✅ No 'Not enough data' fallback for small datasets")
print("  ✅ Multi-insight generation (2-3 insights per query)")
print("  ✅ Dominance detection")
print("  ✅ Underperformance detection")
print("  ✅ Distribution analysis")
print("  ✅ Confidence levels for small datasets")
print("  ✅ Edge case handling (empty, single point)")
print("  ✅ Meaningful messaging with emojis")
