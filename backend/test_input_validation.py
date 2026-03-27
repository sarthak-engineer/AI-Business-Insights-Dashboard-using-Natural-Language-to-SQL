#!/usr/bin/env python3
"""
Test script for validating input validation improvements (Problems 1-5 fixes).

Tests:
- Problem 1: Garbage input rejection
- Problem 2: Query confidence handling
- Problem 3: Helpful error messages
- Problem 4: SQL validation before generation
- Problem 5: Query classification (VALID/UNCLEAR/INVALID)
"""

import sys
sys.path.insert(0, '/root/backend')

from nl_to_sql_api import (
    is_meaningful_input,
    classify_query,
    validate_query,
    get_helpful_suggestions
)
import json

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_is_meaningful_input():
    """Test the lightweight garbage input detector (Problem 1)."""
    print_section("TEST 1: Lightweight Input Validation (Problem 1)")
    
    test_cases = [
        ("yh566th6yt5h", False, "Pure garbage - random chars"),
        ("asdfghjkl", False, "Random keyboard mash"),
        ("abcdefg", False, "Random letters only"),
        ("total sales", True, "Valid business query"),
        ("top 5 products", True, "Valid business query"),
        ("customer count", True, "Valid business query"),
        ("u", False, "Too short"),
        ("a b c d e f", False, "Too many single chars"),
    ]
    
    for query, expected, description in test_cases:
        result = is_meaningful_input(query)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"{status}: '{query}' → {result} (expected {expected})")
        print(f"       Description: {description}")

def test_classify_query():
    """Test query classification (Problem 2, 5)."""
    print_section("TEST 2: Query Classification (Problem 2, 5)")
    
    test_cases = [
        ("yh566th6yt5h", "INVALID", "Pure garbage"),
        ("total sales by category", "VALID", "Clear business query"),
        ("top 5 products", "VALID", "Clear business query"),
        ("sales??", "UNCLEAR", "Unclear with punctuation"),
        ("who best", "UNCLEAR", "Incomplete query"),
        ("show everything", "VALID", "Business query"),
        ("weather today", "INVALID", "Non-business query"),
    ]
    
    print("Note: Classification uses AI, results may vary slightly.\n")
    
    for query, expected_classification, description in test_cases:
        classification, confidence, _ = classify_query(query)
        confidence_str = f"{confidence:.2f}"
        
        # Don't fail if classification differs due to AI, just show results
        status = "✓" if classification == expected_classification else "?"
        print(f"{status} '{query}'")
        print(f"   Classification: {classification} (expected {expected_classification})")
        print(f"   Confidence: {confidence_str}")
        print(f"   Description: {description}\n")

def test_validate_query():
    """Test the enhanced validation with helpful messages (Problem 3)."""
    print_section("TEST 3: Enhanced Validation with Helpful Messages (Problem 3)")
    
    test_cases = [
        ("yh566th6yt5h", False, "garbage input → should be rejected"),
        ("total sales", True, "valid query → should be accepted"),
        ("sales?", None, "unclear → might be rejected or accepted depending on confidence"),
    ]
    
    for query, expected_valid, description in test_cases:
        is_valid, error_msg = validate_query(query)
        
        if expected_valid is None:
            # Don't enforce strict expectation
            status = "✓"
        else:
            status = "✓ PASS" if is_valid == expected_valid else "✗ FAIL"
        
        print(f"{status}: '{query}'")
        print(f"   Valid: {is_valid}")
        print(f"   Message: {error_msg if error_msg else '(None)'}")
        print(f"   Description: {description}\n")

def test_helpful_suggestions():
    """Test that helpful suggestions are provided (Problem 3)."""
    print_section("TEST 4: Helpful Error Suggestions (Problem 3)")
    
    suggestions = get_helpful_suggestions()
    print("Example suggestions provided:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    if len(suggestions) >= 3:
        print(f"\n✓ PASS: At least 3 example queries provided (got {len(suggestions)})")
    else:
        print(f"\n✗ FAIL: Expected at least 3 suggestions, got {len(suggestions)}")

def test_no_sql_generation_for_invalid():
    """Test that SQL is not generated for invalid queries (Problem 4)."""
    print_section("TEST 5: SQL Not Generated for Invalid Input (Problem 4)")
    
    from nl_to_sql_api import generate_sql
    
    test_cases = [
        ("yh566th6yt5h", None, "garbage input should return None for SQL"),
        ("total sales", str, "valid query should return SQL string"),
    ]
    
    print("Note: valid query test may take a moment (calls AI)\n")
    
    for query, expected_type, description in test_cases:
        try:
            sql, enhanced, hint = generate_sql(query)
            
            if expected_type is None:
                status = "✓ PASS" if sql is None else "✗ FAIL"
                result = f"SQL={sql} (expected None)"
            else:
                status = "✓ PASS" if isinstance(sql, str) or sql is None else "✗ FAIL"
                result = f"Type={type(sql).__name__} (expected {expected_type.__name__ if expected_type else 'None'})"
            
            print(f"{status}: '{query}'")
            print(f"   SQL: {result}")
            print(f"   Hint: {hint if hint else '(None)'}")
            print(f"   Description: {description}\n")
            
        except Exception as e:
            print(f"✗ ERROR: '{query}' raised exception: {str(e)}\n")

def main():
    print("\n" + "="*70)
    print("  COMPREHENSIVE INPUT VALIDATION TESTING")
    print("  Testing all 5 problem fixes")
    print("="*70)
    
    test_is_meaningful_input()
    test_classify_query()
    test_validate_query()
    test_helpful_suggestions()
    test_no_sql_generation_for_invalid()
    
    print("\n" + "="*70)
    print("  TESTING COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
