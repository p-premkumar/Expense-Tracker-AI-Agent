"""
Test multi-item receipt parsing feature
Tests parsing receipts with multiple items, each with separate amount and category
"""

from nlp_processor import ExpenseParser

def test_multi_item_receipt():
    parser = ExpenseParser()
    
    print("=" * 70)
    print("MULTI-ITEM RECEIPT PARSING TEST SUITE")
    print("=" * 70)
    
    # Test 1: Simple line-by-line format
    print("\n[TEST 1] Simple line-by-line format")
    print("-" * 70)
    test1 = """Biryani - 250
Coffee - 100
Pizza - 200"""
    
    result1 = parser.parse_multiple_expenses(test1)
    print(f"Input:\n{test1}\n")
    print(f"Expected: 3 items (Biryani, Coffee, Pizza)")
    print(f"Result: {len(result1)} items")
    for i, (amount, category, desc) in enumerate(result1, 1):
        print(f"  Item {i}: {desc:20} | {amount:8.2f} | {category}")
    assert len(result1) == 3, f"Expected 3 items, got {len(result1)}"
    assert result1[0][0] == 250.0
    assert result1[1][0] == 100.0
    assert result1[2][0] == 200.0
    print("PASSED\n")
    
    # Test 2: Explicit fields with separators
    print("[TEST 2] Explicit fields with separators (--- format)")
    print("-" * 70)
    test2 = """Item: Biryani
Amount: 250
Category: Food
---
Item: Coffee
Amount: 100
Category: Hot Drinks
---
Item: Pizza
Amount: 200
Category: Food"""
    
    result2 = parser.parse_multiple_expenses(test2)
    print(f"Input: (Explicit field format with --- separators)\n")
    print(f"Expected: 3 items with explicit categories")
    print(f"Result: {len(result2)} items")
    for i, (amount, category, desc) in enumerate(result2, 1):
        print(f"  Item {i}: {desc:20} | {amount:8.2f} | {category}")
    assert len(result2) == 3, f"Expected 3 items, got {len(result2)}"
    assert result2[0][1] == "Food", f"Expected 'Food', got '{result2[0][1]}'"
    assert result2[1][1] == "Hot Drinks", f"Expected 'Hot Drinks', got '{result2[1][1]}'"
    print("PASSED\n")
    
    # Test 3: Currency symbols
    print("[TEST 3] Items with currency symbols")
    print("-" * 70)
    test3 = """Biryani - Rs 250 - Food
Coffee - Rs 100 - Drinks
Pizza - Rs 200 - Food"""
    
    result3 = parser.parse_multiple_expenses(test3)
    print(f"Input:\n{test3}\n")
    print(f"Expected: 3 items with amounts extracted from Rs values")
    print(f"Result: {len(result3)} items")
    for i, (amount, category, desc) in enumerate(result3, 1):
        print(f"  Item {i}: {desc:30} | {amount:8.2f} | {category}")
    assert len(result3) == 3, f"Expected 3 items, got {len(result3)}"
    print("PASSED\n")
    
    # Test 4: Blank lines as separators (realistic OCR output)
    print("[TEST 4] Blank lines as separators (OCR receipt format)")
    print("-" * 70)
    test4 = """Biryani
250

Coffee
100

Pizza
200"""
    
    result4 = parser.parse_multiple_expenses(test4)
    print(f"Input: (Biryani, Coffee, Pizza separated by blank lines)\n")
    print(f"Expected: 3 items")
    print(f"Result: {len(result4)} items")
    for i, (amount, category, desc) in enumerate(result4, 1):
        print(f"  Item {i}: {desc:20} | {amount:8.2f} | {category}")
    assert len(result4) == 3, f"Expected 3 items, got {len(result4)}"
    print("PASSED\n")
    
    # Test 5: Single item (should still work)
    print("[TEST 5] Single item receipt (backward compatibility)")
    print("-" * 70)
    test5 = "Spent 350 for Biryani"
    
    result5 = parser.parse_multiple_expenses(test5)
    print(f"Input: {test5}\n")
    print(f"Expected: 1 item")
    print(f"Result: {len(result5)} items")
    for i, (amount, category, desc) in enumerate(result5, 1):
        print(f"  Item {i}: {desc:20} | {amount:8.2f} | {category}")
    assert len(result5) == 1, f"Expected 1 item, got {len(result5)}"
    print("PASSED\n")
    
    # Test 6: Realistic restaurant receipt
    print("[TEST 6] Realistic restaurant receipt (multi-item breakdown)")
    print("-" * 70)
    test6 = """Biryani - 250
Raita - 50
Chai - 30
Dessert - 70"""
    
    result6 = parser.parse_multiple_expenses(test6)
    print(f"Input:\n{test6}\n")
    print(f"Expected: 4 items from restaurant bill")
    print(f"Result: {len(result6)} items")
    for i, (amount, category, desc) in enumerate(result6, 1):
        print(f"  Item {i}: {desc:20} | {amount:8.2f} | {category}")
    assert len(result6) == 4, f"Expected 4 items, got {len(result6)}"
    print("PASSED\n")
    
    print("=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70)
    print("\nSummary:")
    print("[OK] Line-by-line format parsing")
    print("[OK] Explicit field extraction with separators")
    print("[OK] Currency symbol handling")
    print("[OK] Blank line separation handling")
    print("[OK] Single item backward compatibility")
    print("[OK] Realistic restaurant bill parsing")

if __name__ == "__main__":
    test_multi_item_receipt()

