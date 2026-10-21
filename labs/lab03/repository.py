from labs.lab03.database import get_connection
from contextlib import closing
import sqlite3

def get_categories():
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY id ASC")
        rows = cursor.fetchall()
        return [{"id": row[0], "name": row[1]} for row in rows]

def create_category(name : str):
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            category_id = cursor.lastrowid
            return [{"id": category_id, "name": name}]

def delete_category(category_id : int):
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM records WHERE category_id = ?", (category_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                raise sqlite3.IntegrityError("Категорія містить записи")

            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            return cursor.rowcount > 0

def create_record(record_data : dict):
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute( """
                            INSERT INTO RECORDS (code, title, category_id,value, status) VALUES 
                            (:code, :title, :category_id, :value, :status)
                            """,
                            (record_data,))

            record_id = cursor.lastrowid
            return [{"id": record_id, "code": record_id, "title": record_data["title"],}]









