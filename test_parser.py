"""
Example usage and testing script for the Expense Tracker
This demonstrates how the NLP parser works without needing Telegram
"""

from nlp_processor import ExpenseParser
from database import ExpenseDatabase
from config import CURRENCY

def test_expense_parser():
    """Test the NLP expense parser with various inputs"""
    
    parser = ExpenseParser()
    
    print("=" * 60)
    print("Testing Expense Parser")
    print("=" * 60)
    print()
    
    test_cases = [
        "Spent 150 for biriyani",
        "150 on transport",
        "Coffee - 100",
        "Movie tickets 250",
        "Electricity bill 1500",
        "Bought shoes 2000",
        "Flight ticket 5000",
        "Lunch 350",
        "Gas - 1200",
        "Shopping 5000",
        "Medical checkup 500",
        "Book purchase 450",
    ]
    
    print("Testing various expense messages:\n")
    
    for text in test_cases:
        amount, category, description = parser.parse_expense(text)
        
        if amount:
            status = "OK"
            print(f"{status} Input: \"{text}\"")
            print(f"   Amount: Rs {amount:.2f}")
            print(f"   Category: {category}")
            print()
        else:
            status = "FAIL"
            print(f"{status} Could not parse: \"{text}\"")
            print()

def test_database_operations():
    """Test database operations"""
    
    print("\n" + "=" * 60)
    print("Testing Database Operations")
    print("=" * 60)
    print()
    
    db = ExpenseDatabase()
    test_user_id = 123456789
    
    # Add sample user
    print("Step 1: Adding sample user...")
    db.add_user(test_user_id, "test_user", "Test")
    print("User added\n")
    
    # Add sample expenses
    print("Step 2: Adding sample expenses...")
    
    sample_expenses = [
        (500, "Food", "Breakfast at cafe"),
        (200, "Transport", "Uber ride"),
        (1000, "Food", "Lunch with friends"),
        (300, "Entertainment", "Movie tickets"),
        (150, "Utilities", "Internet bill"),
    ]
    
    for amount, category, description in sample_expenses:
        db.add_expense(test_user_id, amount, category, description)
        print(f"Added Rs {amount:.2f} - {category}")
    
    print()
    
    # Get expenses
    print("Step 3: Retrieving expenses...")
    expenses = db.get_expenses(test_user_id, days=30)
    print(f"Found {len(expenses)} expenses\n")
    
    for exp_id, amount, category, description, date in expenses:
        print(f"   - {category}: Rs {amount:.2f}")
    
    print()
    
    # Get summary
    print("Step 4: Getting summary by category...")
    summary = db.get_summary(test_user_id, days=30)
    
    total = 0
    for category, amount, count in summary:
        print(f"   - {category}: Rs {amount:.2f} ({count} items)")
        total += amount
    
    print(f"\n   Total: Rs {total:.2f}")
    
    print()
    
    # Get today's total
    print("Step 5: Today's total...")
    today_total = db.get_total_today(test_user_id)
    print(f"Today's spending: Rs {today_total:.2f}")
    
    print()

def show_category_examples():
    """Show examples of what the bot recognizes for each category"""
    
    from config import EXPENSE_PATTERNS
    
    print("\n" + "=" * 60)
    print("Category Examples")
    print("=" * 60)
    print()
    
    for category, keywords in EXPENSE_PATTERNS.items():
        print(f"{category.upper()}")
        print(f"   Keywords: {', '.join(keywords)}")
        print()

def main():
    """Run all tests"""
    
    print("\n")
    print("=" * 60)
    print("Expense Tracker AI - Testing Suite".center(60))
    print("=" * 60)
    
    # Run tests
    test_expense_parser()
    show_category_examples()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
    
    print("\nNext steps:")
    print("1. Review the test output above")
    print("2. Start the bot: python main.py")
    print("3. Test in Telegram: just send messages to the bot")
    print("\n")

if __name__ == "__main__":
    main()
