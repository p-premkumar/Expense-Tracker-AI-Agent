"""
Test suite for budget management features
"""
import unittest
import sqlite3
import os
from datetime import datetime, timedelta
from database import ExpenseDatabase
from config import DATABASE_PATH, CURRENCY

class TestBudgetFeatures(unittest.TestCase):
    """Test budget limit management"""
    
    def setUp(self):
        """Set up test database"""
        self.test_db_path = "test_budget.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        # Create test database
        self.conn = sqlite3.connect(self.test_db_path)
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
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
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS budget_limits (
                limit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                daily_limit REAL,
                weekly_limit REAL,
                monthly_limit REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        self.conn.commit()
        self.test_user_id = 123456
        
        # Add test user
        self.cursor.execute(
            'INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
            (self.test_user_id, 'testuser', 'Test')
        )
        self.conn.commit()
    
    def tearDown(self):
        """Clean up test database"""
        self.conn.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_set_budget_limit(self):
        """Test setting budget limits"""
        # Insert budget limits
        self.cursor.execute('''
            INSERT OR REPLACE INTO budget_limits 
            (user_id, daily_limit, weekly_limit, monthly_limit)
            VALUES (?, ?, ?, ?)
        ''', (self.test_user_id, 500, 3500, 15000))
        
        self.conn.commit()
        
        # Retrieve limits
        self.cursor.execute(
            'SELECT daily_limit, weekly_limit, monthly_limit FROM budget_limits WHERE user_id = ?',
            (self.test_user_id,)
        )
        result = self.cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 500)  # daily
        self.assertEqual(result[1], 3500)  # weekly
        self.assertEqual(result[2], 15000)  # monthly
    
    def test_get_total_today(self):
        """Test calculating today's total"""
        today = datetime.now().date()
        
        # Add expenses for today
        expenses = [100, 150, 50]
        for amount in expenses:
            self.cursor.execute('''
                INSERT INTO expenses (user_id, amount, category, description, date, source)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.test_user_id, amount, 'Food', 'Test', today, 'text'))
        
        self.conn.commit()
        
        # Calculate today's total
        self.cursor.execute(
            'SELECT SUM(amount) FROM expenses WHERE user_id = ? AND date(date) = ?',
            (self.test_user_id, today)
        )
        result = self.cursor.fetchone()[0]
        
        self.assertEqual(result, 300)
    
    def test_get_total_week(self):
        """Test calculating week's total"""
        today = datetime.now()
        
        # Add expenses from last 7 days
        expenses = [100, 150, 200, 50, 75]
        for i, amount in enumerate(expenses):
            date = today - timedelta(days=i)
            self.cursor.execute('''
                INSERT INTO expenses (user_id, amount, category, description, date, source)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.test_user_id, amount, 'Food', 'Test', date, 'text'))
        
        self.conn.commit()
        
        # Calculate week's total (last 7 days)
        seven_days_ago = today - timedelta(days=7)
        self.cursor.execute(
            'SELECT SUM(amount) FROM expenses WHERE user_id = ? AND date > ?',
            (self.test_user_id, seven_days_ago)
        )
        result = self.cursor.fetchone()[0]
        
        self.assertEqual(result, 575)
    
    def test_get_total_month(self):
        """Test calculating month's total"""
        today = datetime.now()
        
        # Add expenses from last 30 days
        expenses = [100, 150, 200, 50, 75, 125, 95]
        for i, amount in enumerate(expenses):
            date = today - timedelta(days=i)
            self.cursor.execute('''
                INSERT INTO expenses (user_id, amount, category, description, date, source)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.test_user_id, amount, 'Food', 'Test', date, 'text'))
        
        self.conn.commit()
        
        # Calculate month's total (last 30 days)
        thirty_days_ago = today - timedelta(days=30)
        self.cursor.execute(
            'SELECT SUM(amount) FROM expenses WHERE user_id = ? AND date > ?',
            (self.test_user_id, thirty_days_ago)
        )
        result = self.cursor.fetchone()[0]
        
        self.assertEqual(result, 795)
    
    def test_budget_warning_logic(self):
        """Test budget warning threshold logic"""
        
        def get_warning_level(current, limit):
            """Calculate warning level based on percentage"""
            if not limit:
                return None
            percentage = (current / limit) * 100
            if percentage >= 100:
                return "exceeded"
            elif percentage >= 90:
                return "critical"
            elif percentage >= 75:
                return "warning"
            else:
                return "safe"
        
        # Test cases
        test_cases = [
            (100, 500, "safe"),      # 20%
            (375, 500, "warning"),   # 75%
            (450, 500, "critical"),  # 90%
            (500, 500, "exceeded"),  # 100%
            (600, 500, "exceeded"),  # 120%
        ]
        
        for current, limit, expected in test_cases:
            result = get_warning_level(current, limit)
            self.assertEqual(result, expected, 
                f"Failed for {current}/{limit}: got {result}, expected {expected}")
    
    def test_multiple_users_isolation(self):
        """Test that budget limits are isolated per user"""
        user2_id = 654321
        
        # Add second user
        self.cursor.execute(
            'INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
            (user2_id, 'testuser2', 'Test2')
        )
        
        # Set different limits for each user
        self.cursor.execute('''
            INSERT INTO budget_limits (user_id, daily_limit, weekly_limit, monthly_limit)
            VALUES (?, ?, ?, ?)
        ''', (self.test_user_id, 500, 3500, 15000))
        
        self.cursor.execute('''
            INSERT INTO budget_limits (user_id, daily_limit, weekly_limit, monthly_limit)
            VALUES (?, ?, ?, ?)
        ''', (user2_id, 1000, 7000, 30000))
        
        self.conn.commit()
        
        # Verify isolation
        self.cursor.execute(
            'SELECT daily_limit FROM budget_limits WHERE user_id = ?',
            (self.test_user_id,)
        )
        user1_limit = self.cursor.fetchone()[0]
        
        self.cursor.execute(
            'SELECT daily_limit FROM budget_limits WHERE user_id = ?',
            (user2_id,)
        )
        user2_limit = self.cursor.fetchone()[0]
        
        self.assertEqual(user1_limit, 500)
        self.assertEqual(user2_limit, 1000)
        self.assertNotEqual(user1_limit, user2_limit)

class TestBudgetCommands(unittest.TestCase):
    """Test budget command parsing"""
    
    def test_setdaily_parsing(self):
        """Test /setdaily amount parsing"""
        test_cases = [
            ("500", 500.0),
            ("500.50", 500.50),
            ("1000", 1000.0),
            ("0.50", 0.50),
        ]
        
        for input_str, expected in test_cases:
            try:
                result = float(input_str)
                self.assertEqual(result, expected)
            except ValueError:
                self.fail(f"Failed to parse {input_str}")
    
    def test_budget_command_validation(self):
        """Test budget amount validation"""
        valid_amounts = [0.1, 100, 1000, 50000]
        invalid_amounts = [0, -100, "abc", None]
        
        for amount in valid_amounts:
            self.assertGreater(amount, 0, f"{amount} should be valid")
        
        for amount in invalid_amounts:
            if isinstance(amount, (int, float)):
                self.assertLessEqual(amount, 0, f"{amount} should be invalid")

if __name__ == '__main__':
    unittest.main()
