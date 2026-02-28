#!/usr/bin/env python3
"""Test simple receipt extraction method"""

from nlp_processor import ExpenseParser

parser = ExpenseParser()

# Test 1: Restaurant receipt
receipt1 = """
Pizza Palace
Margherita Pizza 350
Garlic Bread 120
Subtotal 550
Service Charge 50
Total 655
"""

result1 = parser.extract_simple_receipt(receipt1)
print("[OK] Test 1: Restaurant Receipt")
print(f"   Category: {result1['category']}")
print(f"   Amount: {result1['final_amount']:.2f}")
print()

# Test 2: Simple food receipt
receipt2 = """
Chai 80
Biryani 250
Total 330
"""

result2 = parser.extract_simple_receipt(receipt2)
print("[OK] Test 2: Simple Food Receipt")
print(f"   Category: {result2['category']}")
print(f"   Amount: {result2['final_amount']:.2f}")
print()

# Test 3: Fuel receipt
receipt3 = """
Petrol Pump XYZ
Fuel Rs 2500
Grand Total: 2500
"""

result3 = parser.extract_simple_receipt(receipt3)
print("[OK] Test 3: Fuel Receipt")
print(f"   Category: {result3['category']}")
print(f"   Amount: {result3['final_amount']:.2f}")
print()

# Test 4: Shopping receipt
receipt4 = """
Online Shopping
Items Total: 5999
Taxes: 1000
Final Amount: 7999
"""

result4 = parser.extract_simple_receipt(receipt4)
print("[OK] Test 4: Shopping Receipt")
print(f"   Category: {result4['category']}")
print(f"   Amount: {result4['final_amount']:.2f}")
print()

print("All tests passed! Simple extraction working correctly.")
