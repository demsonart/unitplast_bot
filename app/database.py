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

        # Drop old orders table if it exists (for migration)
        # This allows us to create the new schema
        try:
            cursor.execute("DROP TABLE IF EXISTS orders")
        except:
            pass

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

        # Таблица для заказов (расширенная)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                calculation_id INTEGER,
                email_id INTEGER UNIQUE,
                client_name TEXT,
                client_email TEXT,
                client_phone TEXT,
                company TEXT,
                material_type TEXT,
                product_name TEXT,
                quantity INTEGER DEFAULT 1,
                total_price REAL,
                status TEXT DEFAULT 'new',
                progress INTEGER DEFAULT 0,
                products TEXT,
                delivery_type TEXT DEFAULT 'courier',
                deadline TEXT,
                estimated_ready_date TEXT,
                actual_ready_date TEXT,
                comments TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
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

    # ════════════════════════════════════════════════════════════════════════
    # NEW ORDER MANAGEMENT API
    # ════════════════════════════════════════════════════════════════════════

    def create_order_from_calculation(self, calculation_id, calculation_data, client_info):
        """Create order from calculator result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO orders
                (calculation_id, client_name, client_email, client_phone, company,
                 material_type, product_name, quantity, total_price, status,
                 progress, delivery_type, estimated_ready_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                calculation_id,
                client_info.get('name', 'Unknown'),
                client_info.get('email', ''),
                client_info.get('phone', ''),
                client_info.get('company', ''),
                calculation_data.get('material_type', 'plastic'),
                calculation_data.get('product_name', 'Product'),
                calculation_data.get('quantity', 1),
                calculation_data.get('total', 0),
                'new',
                0,
                client_info.get('delivery_type', 'courier'),
                calculation_data.get('ready_date', None),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_order_by_id(self, order_id):
        """Get order with all details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def get_orders_by_status(self, status, limit=50):
        """Get orders filtered by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM orders
            WHERE status = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (status, limit))
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

    def get_all_orders(self, limit=100):
        """Get all orders with pagination"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM orders
            ORDER BY updated_at DESC
            LIMIT ?
        """, (limit,))
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

    def update_order_status(self, order_id, status, progress=None, notes=None):
        """Update order status and progress"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            updates = [f"status = ?", f"updated_at = ?"]
            params = [status, datetime.now().isoformat()]

            if progress is not None:
                updates.append("progress = ?")
                params.append(progress)

            if notes is not None:
                updates.append("notes = ?")
                params.append(notes)

            query = f"UPDATE orders SET {', '.join(updates)} WHERE id = ?"
            params.append(order_id)

            cursor.execute(query, params)
            conn.commit()
            return True
        finally:
            conn.close()

    def update_order(self, order_id, **kwargs):
        """Update any order fields"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            allowed_fields = ['status', 'progress', 'notes', 'client_name', 'client_email',
                            'client_phone', 'company', 'delivery_type', 'deadline',
                            'estimated_ready_date', 'actual_ready_date', 'total_price', 'comments']

            updates = []
            params = []

            for key, value in kwargs.items():
                if key in allowed_fields:
                    updates.append(f"{key} = ?")
                    params.append(value)

            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now().isoformat())
                params.append(order_id)

                query = f"UPDATE orders SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                conn.commit()
                return True
            return False
        finally:
            conn.close()

    def get_order_statistics(self):
        """Get orders statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN status = 'ready' THEN 1 ELSE 0 END) as ready,
                SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled,
                SUM(total_price) as total_revenue
            FROM orders
        """)

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                "total": result[0] or 0,
                "new": result[1] or 0,
                "in_progress": result[2] or 0,
                "ready": result[3] or 0,
                "delivered": result[4] or 0,
                "cancelled": result[5] or 0,
                "total_revenue": result[6] or 0
            }
        return {}
