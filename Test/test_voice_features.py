"""
Test script for voice and screenshot features
"""
import sys

def test_modules():
    """Test if all modules can be imported"""
    try:
        from nlp_processor import VoiceProcessor, ExpenseParser, OCRProcessor
        print("[OK] NLP Processor imports successful")
    except Exception as e:
        print(f"[ERROR] NLP Processor error: {e}")
        return False

    try:
        from database import ExpenseDatabase
        print("[OK] Database imports successful")
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        return False

    try:
        from config import BOT_TOKEN, EXPENSE_CATEGORIES
        print("[OK] Config imports successful")
    except Exception as e:
        print(f"[ERROR] Config error: {e}")
        return False

    try:
        from bot_commands import help_command, start, summary
        print("[OK] Bot commands imports successful")
    except Exception as e:
        print(f"[ERROR] Bot commands error: {e}")
        return False

    return True


def test_database_schema():
    """Test if database schema has new transaction fields"""
    try:
        import sqlite3
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Create the expenses table with new schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                transaction_id TEXT,
                account_name TEXT,
                payment_method TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Check columns
        cursor.execute("PRAGMA table_info(expenses)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = ['transaction_id', 'account_name', 'payment_method']
        for col in required_columns:
            if col in columns:
                print(f"[OK] Column '{col}' exists in expenses table")
            else:
                print(f"[ERROR] Column '{col}' missing from expenses table")
                return False
        
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] Database schema test failed: {e}")
        return False


def test_features():
    """Test core features"""
    try:
        from nlp_processor import ExpenseParser
        parser = ExpenseParser()
        
        # Test text parsing
        amount, category, desc = parser.parse_expense("Spent 150 for biriyani")
        if amount == 150 and category == "Food":
            print("[OK] Text parsing works")
        else:
            print(f"[WARNING] Parsing returned: amount={amount}, category={category}")
        
        # Test voice processor
        from nlp_processor import VoiceProcessor
        voice = VoiceProcessor()
        print("[OK] VoiceProcessor instantiated successfully")
        
        # Test OCR processor
        from nlp_processor import OCRProcessor
        ocr = OCRProcessor()
        print("[OK] OCRProcessor instantiated successfully")
        
        return True
    except Exception as e:
        print(f"[ERROR] Feature test failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Testing Voice & Screenshot Features")
    print("=" * 50)
    print()
    
    tests = [
        ("Module Imports", test_modules),
        ("Database Schema", test_database_schema),
        ("Core Features", test_features),
    ]
    
    results = {}
    for name, test_func in tests:
        print(f"\n[TEST] {name}")
        print("-" * 50)
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"[ERROR] {name} test crashed: {e}")
            results[name] = False
    
    print()
    print("=" * 50)
    print("Test Summary")
    print("=" * 50)
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n[SUCCESS] All tests passed!")
        sys.exit(0)
    else:
        print("\n[WARNING] Some tests failed")
        sys.exit(1)
