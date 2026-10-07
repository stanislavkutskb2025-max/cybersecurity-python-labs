import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse

from labs.lab02.task1 import (
    SESSION_TIMEOUT_SEC,
    Admin,
    AuditLog,
    UserAccount,
)
from labs.lab02.task2 import generate_baseline, check_integrity, setup_logging

def run_demo():
    print("=== ПОЧАТОК ДЕМОНСТРАЦІЇ ===")

    audit_log = AuditLog()

    user = Admin(username="admin_user", email="admin@lab.com")
    user.set_password("SecretPassword123")

    account = UserAccount(user=user, audit_log=audit_log)

    print("\n--- 1. Спроба невдалого входу ---")
    login_fail = account.login("admin_user", "WrongPassword", ip="192.168.1.10")
    print(f"Результат входу з невірним паролем: {login_fail}")
    print(f"Стан авторизації (is_authenticated): {account.is_authenticated()}")

    print("\n--- 2. Спроба успішного входу ---")
    login_success = account.login("admin_user", "SecretPassword123", ip="192.168.1.10")
    print(f"Результат входу з правильним паролем: {login_success}")
    print(f"Стан авторизації (is_authenticated): {account.is_authenticated()}")

    print("\n--- 3. Перевірка прав адміністратора ---")
    current_user = account["user"]
    print(f"Роль користувача: {current_user.role}")

    current_user.grant_permission("READ_SENSITIVE_DATA")
    print(
        f"Має право READ_SENSITIVE_DATA: {current_user.has_permission('READ_SENSITIVE_DATA')}"
    )

    print("\n--- 4. Зміна Email із валідацією ---")
    print(f"Поточний email: {account['user'].email}")

    try:
        account["user"].email = "invalid-email-format"
    except ValueError as e:
        print(f"Перехоплено очікувану помилку валідації: {e}")

    account["user"].email = "new_admin@lab.com"
    print(f"Оновлений email: {account['user'].email}")

    print("\n--- 5. Перевірка таймауту сеансу ---")
    print(f"Активний до виходу за таймаут: {account.is_authenticated()}")

    if account.session:
        account.session.last_activity = datetime.now(timezone.utc) - timedelta(
            seconds=SESSION_TIMEOUT_SEC + 10
        )

    print(
        f"Активний після спливу таймауту (> {SESSION_TIMEOUT_SEC} сек): {account.is_authenticated()}"
    )

    print("\n--- 6. Вихід із системи (Logout) ---")
    account.login("admin_user", "SecretPassword123", ip="192.168.1.10")
    print(f"Авторизований перед logout: {account.is_authenticated()}")

    account.logout()
    print(f"Авторизований після logout: {account.is_authenticated()}")

    print("\n--- 7. Журнал аудиту (AuditLog) ---")
    account["audit_log"].show_all()

    print("\n=== ДЕМОНСТРАЦІЮ ЗАВЕРШЕНО ===")

def main():
    parser = argparse.ArgumentParser(description="File Integrity Monitor (FIM)")

    subparsers = parser.add_subparsers(dest="command",  help="Режим роботи")

    subparsers.add_parser("demo", help="Запустити демонстрацію Task 1")

    gen_parser = subparsers.add_parser("generate", help="Згенерувати еталонний baseline.json")
    gen_parser.add_argument("--dir", type=Path, default=Path("labs/lab02/data/monitored"), help="Шлях до монітореної папки")
    gen_parser.add_argument("--baseline", type=Path, default=Path("labs/lab02/data/baseline.json"), help="Шлях до baseline.json")

    check_parser = subparsers.add_parser("check", help="Перевірити цілісність файлів")
    check_parser.add_argument("--dir", type=Path, default=Path("labs/lab02/data/monitored"), help="Шлях до монітореної папки")
    check_parser.add_argument("--baseline", type=Path, default=Path("labs/lab02/data/baseline.json"), help="Шлях до baseline.json")
    check_parser.add_argument("--log-file", type=Path, default=Path("fim.log"), help="Шлях до файла логів")

    args = parser.parse_args()


    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        run_demo()

    elif args.command == "generate":
        generate_baseline(args.dir, args.baseline)
        print(f"Базовий стан успішно збережено у {args.baseline}!")

    elif args.command == "check":
        setup_logging(args.log_file)
        check_integrity(args.dir, args.baseline)

    else:


        print("Для запуску демонстрації виконайте: python -m labs.lab02.main demo")
        print("Для генерації еталонного baseline.json виконайте: python -m labs.lab02.main generate")
        print("Для перевірки цілісності файлів виконайте: python -m labs.lab02.main check")


if __name__ == "__main__":
    main()






