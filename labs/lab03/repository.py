from labs.lab03.database import get_connection
from contextlib import closing
import sqlite3


#Створення категорії, отримання списку категорій і видалення порожньої категорії.
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
            return {"id": category_id, "name": name}

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

# Додавання запису й отримання запису за id
def create_record(record_data : dict):
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute( """
                            INSERT INTO RECORDS (code, title, category_id,value, status) VALUES 
                            (:code, :title, :category_id, :value, :status)
                            """,
                            record_data)

            record_id = cursor.lastrowid
            return get_record_by_id(record_id)


def get_record_by_id(record_id: int):
    with closing(get_connection()) as conn:
        query = """
                    SELECT r.id, r.code, r.title, r.category_id, c.name AS category_name, r.value, r.status
                    FROM records r
                    JOIN categories c ON r.category_id = c.id
                    WHERE r.id = ?
                    """
        cursor = conn.execute(query, (record_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return {"id": row[0],
                "code": row[1],
                "title": row[2],
                "category_id": row[3],
                "category_name": row[4],
                "value": row[5],
                "status": row[6]}

#Отримання списку записів із фільтрами та поділом на сторінки.
def get_records(
    category_id: int | None = None,
    status: str | None = None,
    limit: int = 10,
    offset: int = 0, ) -> list[dict]:
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        query = """
                SELECT r.id, r.code, r.title, r.category_id, c.name AS category_name, r.value, r.status
                FROM records r
                JOIN categories c ON r.category_id = c.id
                """
        conditions = []
        parameters = []

        if category_id is not None:
            conditions.append("r.category_id = ?")
            parameters.append(category_id)

        if status is not None:
            conditions.append("r.status = ?")
            parameters.append(status)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY r.id ASC LIMIT ? OFFSET ?"
        parameters.extend([limit, offset])
        cursor.execute(query, tuple(parameters))
        rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "code": row[1],
                "title": row[2],
                "category_id": row[3],
                "category_name": row[4],
                "value": row[5],
                "status": row[6],
            }
            for row in rows
        ]

#Повного оновлення змінюваних полів запису; id має залишатися незмінним.
def update_record(record_id : int, record_data : dict) -> dict | None:
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.cursor()
            parameters = dict(record_data)
            parameters["id"] = record_id
            cursor.execute("""  UPDATE records
                                SET code = :code,
                                    title = :title,
                                    category_id = :category_id,
                                    value = :value,
                                    status = :status
                                WHERE id = :id
                                """,parameters,)
            if cursor.rowcount == 0:
                return None
            return get_record_by_id(record_id)

#Видалення запису
def delete_record(record_id : int) -> bool:
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))

            if cursor.rowcount > 0:
                return True
            return False

#Пакетного додавання записів у межах однієї транзакції
def create_records_batch(records_data: list[dict]) -> bool:
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.cursor()
            cursor.executemany("""
                            INSERT INTO records (code, title, category_id, value, status)
                            VALUES (:code, :title, :category_id, :value, :status)
                            """, records_data,)
            return cursor.rowcount == len(records_data)














