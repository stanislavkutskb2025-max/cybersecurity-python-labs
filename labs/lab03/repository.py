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







