"""
Database initialization and management
"""
import sqlite3
from datetime import datetime
from config import DATABASE_PATH, EXPENSE_CATEGORIES

class ExpenseDatabase:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_db()
    
    def init_db(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Expenses table
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
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL UNIQUE,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, username, first_name):
        """Add or update user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (user_id, username, first_name))
        
        conn.commit()
        conn.close()
    
    def add_expense(self, user_id, amount, category, description, source="text", transaction_id=None, account_name=None, payment_method=None):
        """Add a new expense"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO expenses (user_id, amount, category, description, source, transaction_id, account_name, payment_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, amount, category, description, source, transaction_id, account_name, payment_method))
        
        conn.commit()
        conn.close()
    
    def get_expenses(self, user_id, days=None):
        """Get expenses for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if days:
            query = '''
                SELECT id, amount, category, description, date
                FROM expenses
                WHERE user_id = ? AND date >= datetime('now', '-' || ? || ' days')
                ORDER BY date DESC
            '''
            cursor.execute(query, (user_id, days))
        else:
            query = '''
                SELECT id, amount, category, description, date
                FROM expenses
                WHERE user_id = ?
                ORDER BY date DESC
            '''
            cursor.execute(query, (user_id,))
        
        expenses = cursor.fetchall()
        conn.close()
        return expenses
    
    def get_summary(self, user_id, days=30):
        """Get expense summary by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM expenses
            WHERE user_id = ? AND date >= datetime('now', '-' || ? || ' days')
            GROUP BY category
            ORDER BY total DESC
        '''
        cursor.execute(query, (user_id, days))
        summary = cursor.fetchall()
        conn.close()
        return summary
    
    def delete_expense(self, expense_id, user_id):
        """Delete an expense"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM expenses WHERE id = ? AND user_id = ?', (expense_id, user_id))
        conn.commit()
        conn.close()
    
    def get_total_today(self, user_id):
        """Get total expenses for today"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT SUM(amount) as total
            FROM expenses
            WHERE user_id = ? AND date >= datetime('now', 'start of day')
        '''
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result[0] else 0
