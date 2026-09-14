import csv
import functools
import hashlib
import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import VARIANT_NUMBER


class ValidationError(Exception):
    pass


min_lenght = 10
# sha3_224

users_to_register = (
    ("alex_admin", "SecurePass2026!"),
    ("john_doe", "short"),
    ("kate_m", "MyPassword123"),
    ("empty_user", ""),
    ("mike_brown", "SuperSecret999"),
    ("anna_smith", "12345"),
    ("dev_guy", "PythonDeveloper#1"),
    ("test_guest", "guest_pass_2026"),
    ("no_pass_user", None),
    ("olga_k", "StrongPass_88"),
)

PERSONAL_SALT = str(VARIANT_NUMBER).zfill(5)


def generate_hash(password: str, salt: str = PERSONAL_SALT) -> str:
    if not password or not salt:
        raise ValueError("Пароль та сіль не можуть бути порожніми!")
    if len(password) < min_lenght:
        raise ValidationError(
            f"Пароль занадто короткий (мінімум {min_lenght} символів)"
        )

    data = (password + salt).encode("utf-8")
    result = hashlib.sha3_224(data).hexdigest()

    return result


# 3
def create_user(username: str, password: str) -> tuple:
    hashed = generate_hash(password)
    return (username, hashed)


def create_users(users_list: tuple, file_path: str = "data/users.csv"):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            for username, password in users_list:
                try:
                    userdata = create_user(username, password)
                    writer.writerow(userdata)
                except (ValidationError, ValueError) as e:
                    print(f"Не вдалося зареєструвати {username}: {e}")

    except (OSError, FileNotFoundError, PermissionError) as e:
        print(f"[Помилка створення/запису файлу {file_path}]: {e}")
        raise


# 4
def read_users_db(file_path: str = "data/users.csv") -> list:
    users_db = []
    if not os.path.exists(file_path):
        print("База даних порожня або файл не знайдено.")
        return users_db

    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    users_db.append((row[0], row[1]))
    except (OSError, FileNotFoundError, PermissionError) as e:
        print(f"[Помилка читання файлу {file_path}]: {e}")
        raise

    return users_db


def print_users_table(users_db: list):
    if not users_db:
        print("Немає даних для відображення.")
        return


    print(f"{'Логін':<20} | {'Хеш пароля':<56}")
    print("-" * 80)


    for username, hash_value in users_db:
        print(f"{username:<20} | {hash_value:<56}")


# 6 Декоратор
def log_event(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user = kwargs.get("username") or (args[0] if args else "unknown")

        status = "failure"
        res = False

        try:
            res = func(*args, **kwargs)
            if res is True:
                status = "success"
        except Exception:
            status = "failure"
            raise
        finally:
            log_entry = {
                "event": func.__name__,
                "user": user,
                "result": status,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "args": list(args),
                "kwargs": kwargs,
            }

            log_file = "data/log.json"
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            logs = []
            if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
                with open(log_file, "r", encoding="utf-8") as f:
                    try:
                        logs = json.load(f)
                    except json.JSONDecodeError:
                        logs = []

            logs.append(log_entry)

            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=4, ensure_ascii=False)

        return res

    return wrapper


# 5
@log_event
def login(username: str, password: str) -> bool:
    if not username or not password:
        raise ValueError("Логін та пароль не можуть бути порожніми!")

    users_db = read_users_db()

    for db_user, db_hash in users_db:
        if db_user == username:
            try:
                input_hash = generate_hash(password)

                return input_hash == db_hash
            except ValidationError:
                return False
    return False



# 8.
def main():
    try:
        print("=== 1. Створення бази даних ===")
        create_users(users_to_register)

        print("\n=== 2. Читання та вивід бази ===")
        users_db = read_users_db()
        print_users_table(users_db)

        print("\n=== 3. Тест авторизації ===")
        print("alex_admin (вірно):", login("alex_admin", "SecurePass2026!"))
        print("kate_m (невірно):", login("kate_m", "WrongPass123"))


        print("\n=== 4. Тест винятку (порожні дані) ===")
        login("", "")

    except ValidationError as e:
        print(f"[ValidationError]: {e}")
    except ValueError as e:
        print(f"[ValueError]: {e}")
    except FileNotFoundError as e:
        print(f"[FileNotFoundError]: {e}")
    except PermissionError as e:
        print(f"[PermissionError]: {e}")
    except OSError as e:
        print(f"[IOError]: {e}")


if __name__ == "__main__":
    main()
