import uuid
import logging
import sqlite3
from decimal import Decimal
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DB_NAME = "budget_tracker.db"

def get_db_connection():
    db_path = settings.DATABASES['default']['NAME']
    return sqlite3.connect(db_path)

def initialize_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Updated Expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                transaction_id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                converted_amount REAL,
                converted_currency TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                budget_id TEXT PRIMARY KEY,
                category TEXT UNIQUE NOT NULL,
                allocated_amount REAL NOT NULL
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"!! Error: {e}")
        logger.error(f"Database initialization failed: {e}")

initialize_db()

class Expense:
    def __init__(self, category, amount, description, date, 
                 converted_amount=None, converted_currency=None, currency=None, transaction_id=None):
        self.transaction_id = transaction_id or str(uuid.uuid4())
        self.category = category
        self.amount = Decimal(str(amount))
        self.description = description or ""
        self.date = str(date)
        self.converted_amount = Decimal(str(converted_amount)) if converted_amount else None
        self.converted_currency = converted_currency
        self.currency = currency or 'EUR'  # Default fallback

    def save(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO expenses (
                    transaction_id, category, amount, description, date, 
                    converted_amount, converted_currency, currency
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(transaction_id) DO UPDATE SET
                    category=excluded.category,
                    amount=excluded.amount,
                    description=excluded.description,
                    date=excluded.date,
                    converted_amount=excluded.converted_amount,
                    converted_currency=excluded.converted_currency,
                    currency=excluded.currency
            ''', (
                self.transaction_id,
                self.category,
                float(self.amount),
                self.description,
                self.date,
                float(self.converted_amount) if self.converted_amount else None,
                self.converted_currency,
                self.currency
            ))

            conn.commit()
            conn.close()
            print("Saving expense:", self.__dict__)
            logger.info(f"Successfully saved expense: {vars(self)}")
        except sqlite3.Error as e:
            logger.error(f"Error saving expense: {e}")
            

    @staticmethod
    def get_all():
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses")
            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    "transaction_id": row[0],
                    "category": row[1],
                    "amount": Decimal(str(row[2])),
                    "description": row[3],
                    "date": row[4],
                    "converted_amount": Decimal(str(row[5])) if row[5] is not None else None,
                    "converted_currency": row[6],
                    "currency": row[7],
                } for row in rows
            ]
        except sqlite3.Error as e:
            logger.error(f"Error fetching expenses: {e}")
            return []

    @staticmethod
    def get_total_spent_by_category(category):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(
                    CASE 
                        WHEN converted_amount IS NOT NULL THEN converted_amount 
                        ELSE amount 
                    END
                ) 
                FROM expenses 
                WHERE category = ?
            """, (category,))
            total_spent = cursor.fetchone()[0] or 0
            conn.close()
            return Decimal(str(total_spent))
        except sqlite3.Error as e:
            logger.error(f"Error calculating total expenses: {e}")
            return Decimal("0.00")
    
    @staticmethod
    def delete(transaction_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE transaction_id = ?", (transaction_id,))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"Error deleting expense: {e}")

class Budget:
    def __init__(self, category, allocated_amount, budget_id=None):
        self.budget_id = budget_id or str(uuid.uuid4())
        self.category = category
        self.allocated_amount = Decimal(str(allocated_amount))

    def save(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO budgets (budget_id, category, allocated_amount)
                VALUES (?, ?, ?)
            ''', (self.budget_id, self.category, float(self.allocated_amount)))
            conn.commit()
            conn.close()
            logger.info(f"Successfully saved budget: {vars(self)}")
        except sqlite3.Error as e:
            logger.error(f"Error saving budget: {e}")

    @staticmethod
    def get_all():
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM budgets")
            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    "budget_id": row[0],
                    "category": row[1],
                    "allocated_amount": Decimal(str(row[2]))
                } for row in rows
            ]
        except sqlite3.Error as e:
            logger.error(f"Error fetching budgets: {e}")
            return []

    @staticmethod
    def get_budget_status(category):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT allocated_amount FROM budgets WHERE category = ?", (category,))
            budget_info = cursor.fetchone()
            conn.close()

            if budget_info:
                allocated = Decimal(str(budget_info[0]))
                spent = Expense.get_total_spent_by_category(category)
                return {
                    "category": category,
                    "allocated_amount": allocated,
                    "spent_amount": spent,
                    "remaining_amount": allocated - spent,
                    "status": "Over Budget" if spent > allocated else "Within Budget"
                }
            return None
        except sqlite3.Error as e:
            logger.error(f"Error fetching budget status: {e}")
            return None
