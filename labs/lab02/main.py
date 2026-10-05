import sys
from datetime import datetime, timedelta, timezone


from labs.lab02.task1 import (
    SESSION_TIMEOUT_SEC,
    Admin,
    AuditLog,
    UserAccount,
)


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


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        run_demo()
    else:
        print("Для запуску демонстрації виконайте: python -m labs.lab02.main demo")
