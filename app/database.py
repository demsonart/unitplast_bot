import sqlite3
from datetime import datetime
from pathlib import Path
from .config import DATABASE_PATH

class Database:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Таблица для отслеживания обработанных писем
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_emails (
                id INTEGER PRIMARY KEY,
                message_id TEXT UNIQUE NOT NULL,
                subject TEXT,
                from_email TEXT,
                received_at TEXT,
                processed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_order BOOLEAN DEFAULT 0,
                order_data TEXT
            )
        """)

        # Таблица для заказов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                email_id INTEGER UNIQUE,
                client_name TEXT,
                client_email TEXT,
                client_phone TEXT,
                products TEXT,
                delivery_type TEXT,
                deadline TEXT,
                comments TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                pdf_path TEXT,
                telegram_message_id INTEGER,
                FOREIGN KEY(email_id) REFERENCES processed_emails(id)
            )
        """)

        # Таблица для коммерческих предложений
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commercial_offers (
                id INTEGER PRIMARY KEY,
                order_id INTEGER,
                client_name TEXT,
                pdf_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                sent_to_admin BOOLEAN DEFAULT 0,
                admin_approved BOOLEAN DEFAULT 0,
                FOREIGN KEY(order_id) REFERENCES orders(id)
            )
        """)

        conn.commit()
        conn.close()

    def add_processed_email(self, message_id, subject, from_email, is_order=False, order_data=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO processed_emails
                (message_id, subject, from_email, received_at, is_order, order_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (message_id, subject, from_email, datetime.now().isoformat(), is_order, order_data))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def is_email_processed(self, message_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM processed_emails WHERE message_id = ?", (message_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def add_order(self, email_id, client_name, client_email, client_phone, products,
                  delivery_type, deadline, comments, pdf_path):
        # Note: pdf_path is a legacy name, contains PNG image path
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO orders
                (email_id, client_name, client_email, client_phone, products,
                 delivery_type, deadline, comments, pdf_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (email_id, client_name, client_email, client_phone, products,
                  delivery_type, deadline, comments, pdf_path))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def add_commercial_offer(self, order_id, client_name, pdf_path):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO commercial_offers (order_id, client_name, pdf_path)
                VALUES (?, ?, ?)
            """, (order_id, client_name, pdf_path))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_order(self, order_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def get_recent_orders(self, limit=10):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM orders
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        results = cursor.fetchall()
        conn.close()
        return results
