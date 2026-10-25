import json
import logging
import sqlite3
from contextlib import closing
from pathlib import Path

from labs.lab03.database import get_connection, initialize_database

BASE_DIR = Path(__file__).resolve().parent
SEED_PATH = BASE_DIR / "data" / "seed.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_database() -> None:

    initialize_database()
    if not SEED_PATH.exists():
        logger.error(f"Файл початкових даних не знайдено за шляхом: {SEED_PATH}")
        return

    # Зчитуємо JSON-файл
    try:
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Помилка зчитування JSON-файлу: {e}")
        return

    categories = data.get("categories", [])
    records = data.get("records", [])

    if not isinstance(categories, list) or not isinstance(records, list):
        logger.error(
            "Формат seed.json некоректний: 'categories' та 'records' мають бути списками."
        )
        return

    with closing(get_connection()) as connection:
        cursor = connection.cursor()

        # Перевірка непорожньої бази (якщо є записи/категорії — завершуємо без змін)
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] > 0:
            logger.info("База даних вже містить дані. Початкове заповнення пропущено.")
            return

        try:
            with connection:
                connection.executemany(
                    "INSERT INTO categories (id, name) VALUES (:id, :name)",
                    categories,
                )
                connection.executemany(
                    """
                    INSERT INTO records (code, title, category_id, value, status)
                    VALUES (:code, :title, :category_id, :value, :status)
                    """,
                    records,
                )
            logger.info("Початкове заповнення бази даних успішно завершено.")

        except sqlite3.IntegrityError as e:
            logger.error(f"Помилка цілісності даних (IntegrityError): {e}")
            print(
                "Помилка: Початкові дані некоректні або порушують обмеження бази даних."
            )
        except sqlite3.Error as e:
            logger.error(f"Помилка бази даних під час заповнення: {e}")


if __name__ == "__main__":
    seed_database()
