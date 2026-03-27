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
print("\n\nTEST 1: Empty Dataset")
print("-" * 70)
empty_data = []
result = generate_insight(empty_data)
print(f"Input: {empty_data}")
print(f"Output: {result}")
assert "No data available" in result, "FAILED: Should handle empty data gracefully"
print("PASS")

# Test 2: Single Data Point
print("\n\nTEST 2: Single Data Point (Edge Case)")
print("-" * 70)
single_data = [{"category": "Electronics", "value": 5000}]
result = generate_insight(single_data)
print(f"Input: {single_data}")
print(f"Output:\n{result}\n")
assert "Single data point" in result, "FAILED: Should handle single point"
print("PASS")

# Test 3: Small Dataset (2-3 records)
print("\n\nTEST 3: Small Dataset (2-3 Records)")
print("-" * 70)
small_data = [
    {"category": "Electronics", "value": 15000},
    {"category": "Clothing", "value": 3000},
    {"category": "Home", "value": 2000}
]
result = generate_insight(small_data)
print(f"Input: {small_data}")
print(f"Output:\n{result}\n")
assert len(result) > 50, "FAILED: Should generate meaningful insights"
assert "Not enough data" not in result.split('\n')[0], "FAILED: Shouldn't show 'Not enough data'"
print("PASS")

# Test 4: Medium Dataset (5-10 records)
print("\n\nTEST 4: Medium Dataset (5-10 Records)")
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
assert "Electronics" in result, "FAILED: Should identify top performer"
assert len(result) > 100, "FAILED: Should generate meaningful insights"
print("PASS")

# Test 5: Large Dataset
print("\n\nTEST 5: Large Dataset (20+ Records)")
print("-" * 70)
large_data = [
    {"category": f"Category_{i}", "value": 10000 - (i * 100)} 
    for i in range(20)
]
result = generate_insight(large_data)
print(f"Input: {len(large_data)} records")
print(f"Output:\n{result}\n")
assert "Distribution" in result or "distributed" in result.lower(), "FAILED: Should analyze large dataset"
print("PASS")

# Test 6: Balanced Distribution
print("\n\nTEST 6: Balanced Distribution (Equal Values)")
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
assert "distributed" in result.lower() or "balanced" in result.lower(), "FAILED: Should detect balanced distribution"
print("PASS")

# Test 7: Heavy Skew (One dominant)
print("\n\nTEST 7: Heavy Skew (One Dominant Category)")
print("-" * 70)
skewed_data = [
    {"category": "Electronics", "value": 50000},
    {"category": "Clothing", "value": 2000},
    {"category": "Home", "value": 1500}
]
result = generate_insight(skewed_data)
print(f"Input: {skewed_data}")
print(f"Output:\n{result}\n")
assert "dominates" in result.lower() or "dominant" in result.lower(), "FAILED: Should detect dominance"
assert "50" in result or "Electronics" in result, "FAILED: Should mention top category"
print("PASS")

# Test 8: DataFrame Test
print("\n\nTEST 8: DataFrame Input (generate_python_summary)")
print("-" * 70)
df = pd.DataFrame({
    'category': ['Electronics', 'Clothing', 'Home'],
    'sales': [20000, 8000, 5000]
})
result = generate_python_summary(df)
print(f"Input DataFrame:\n{df}\n")
print(f"Output:\n{result}\n")
assert "Electronics" in result, "FAILED: Should generate insights from DataFrame"
print("PASS")

# Test 9: Underperformance Detection
print("\n\nTEST 9: Underperformance Detection")
print("-" * 70)
underperf_data = [
    {"category": "Premium", "value": 10000},
    {"category": "Mid", "value": 5000},
    {"category": "Budget", "value": 500}
]
result = generate_insight(underperf_data)
print(f"Input: {underperf_data}")
print(f"Output:\n{result}\n")
assert "underperform" in result.lower() or "below" in result.lower(), "FAILED: Should detect underperformance"
print("PASS")

# Test 10: Multiple Insights (Should return 2-3 insights)
print("\n\nTEST 10: Multiple Insights (2-3 Lines)")
print("-" * 70)
multi_data = [
    {"category": "A", "value": 30000},
    {"category": "B", "value": 10000},
    {"category": "C", "value": 8000},
    {"category": "D", "value": 5000}
]
result = generate_insight(multi_data)
print(f"Input: {multi_data}")
print(f"Output:\n{result}\n")
lines = [line.strip() for line in result.split('\n') if line.strip()]
assert len(lines) >= 2, f"FAILED: Should generate 2+ insights, got {len(lines)}"
print("PASS")

print("\n\n" + "=" * 70)
print("ALL TESTS PASSED!")
print("=" * 70)
print("\nSummary:")
print("- Empty datasets handled gracefully")
print("- Single points treated as edge cases with explanations")
print("- Small datasets generate meaningful insights")
print("- Medium/Large datasets produce detailed analysis")
print("- Distribution patterns detected (balanced vs skewed)")
print("- Dominance and underperformance identified")
print("- DataFrame input supported")
print("- Multiple insights generated consistently")
print("\nConclusion: Enhanced Insights Engine successfully replaces generic")
print("'Not enough data' messages with intelligent, context-aware analysis.")
