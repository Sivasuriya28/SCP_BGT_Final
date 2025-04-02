import json
import sqlite3

DB_NAME = "/tmp/budget_tracker.db"  # Lambda has access only to /tmp directory

def lambda_handler(event, context):
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Fetch all expenses
        cursor.execute("SELECT * FROM expenses")
        expenses = cursor.fetchall()
        conn.close()

        # Format response
        expense_list = [
            {
                "transaction_id": expense[0],
                "category": expense[1],
                "amount": expense[2],
                "description": expense[3],
                "date": expense[4]
            }
            for expense in expenses
        ]

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(expense_list)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }