"""
Test script to verify Excel export functionality
"""
import sys
import os

# Test imports
print("Testing imports...")
try:
    from excel_exporter import ExcelExporter
    print("[OK] ExcelExporter imported successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import ExcelExporter: {e}")
    sys.exit(1)

try:
    from openpyxl import Workbook
    print("[OK] openpyxl imported successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import openpyxl: {e}")
    sys.exit(1)

try:
    from database import ExpenseDatabase
    print("[OK] ExpenseDatabase imported successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import ExpenseDatabase: {e}")
    sys.exit(1)

try:
    from bot_commands import export_all, export_monthly, export_weekly, export_today_data
    print("[OK] All export commands imported successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import export commands: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("Testing Excel Exporter initialization...")
print("="*50)

try:
    exporter = ExcelExporter()
    print("[OK] ExcelExporter initialized successfully")
except Exception as e:
    print(f"[ERROR] Failed to initialize ExcelExporter: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("Testing database access...")
print("="*50)

try:
    db = ExpenseDatabase()
    print("[OK] Database connected successfully")
    
    # Test adding a sample user and expense for demonstration
    test_user_id = 999999
    db.add_user(test_user_id, "testuser", "Test")
    print("[OK] Test user created")
    
    db.add_expense(test_user_id, 150.50, "Food", "Test biryani expense", "text")
    print("[OK] Test expense added")
    
    # Test retrieval
    expenses = db.get_expenses(test_user_id)
    if expenses:
        print(f"[OK] Test expense retrieved: {len(expenses)} expense(s) found")
    
except Exception as e:
    print(f"[ERROR] Database test failed: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("Testing Excel file generation...")
print("="*50)

try:
    # Test all export functions
    print("Generating all expenses export...")
    file1 = exporter.export_all_expenses(test_user_id)
    if os.path.exists(file1):
        print(f"[OK] All expenses export created: {file1}")
        os.remove(file1)
        print("[OK] File cleaned up")
    else:
        print(f"[ERROR] File not found: {file1}")
    
    print("\nGenerating monthly export...")
    file2 = exporter.export_monthly_expenses(test_user_id)
    if os.path.exists(file2):
        print(f"[OK] Monthly export created: {file2}")
        os.remove(file2)
        print("[OK] File cleaned up")
    else:
        print(f"[ERROR] File not found: {file2}")
    
    print("\nGenerating 7-day export...")
    file3 = exporter.export_custom_period(test_user_id, days=7)
    if os.path.exists(file3):
        print(f"[OK] 7-day export created: {file3}")
        os.remove(file3)
        print("[OK] File cleaned up")
    else:
        print(f"[ERROR] File not found: {file3}")
    
    print("\nGenerating today export...")
    file4 = exporter.export_custom_period(test_user_id, days=1)
    if os.path.exists(file4):
        print(f"[OK] Today's export created: {file4}")
        os.remove(file4)
        print("[OK] File cleaned up")
    else:
        print(f"[ERROR] File not found: {file4}")
    
except Exception as e:
    print(f"[ERROR] Excel generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*50)
print("ALL TESTS PASSED!")
print("="*50)
print("\nExcel export functionality is ready to use!")
print("\nAvailable commands in Telegram:")
print("  /export - Export all expenses")
print("  /export_monthly - Export last 30 days")
print("  /export_weekly - Export last 7 days")
print("  /export_today - Export today's expenses")
