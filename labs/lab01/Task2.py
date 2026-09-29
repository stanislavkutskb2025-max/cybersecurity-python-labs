import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

users = {
    "sysadmin02": {
        "role": "system_admin",
        "clearance": 4,
        "department": "Infrastructure",
        "active": True,
    },
    "analyst234": {
        "role": "security_analyst",
        "clearance": 3,
        "department": "SOC",
        "active": True,
    },
    "developer567": {
        "role": "developer",
        "clearance": 2,
        "department": "Development",
        "active": True,
    },
    "intern890": {"role": "intern", "clearance": 1, "department": "HR", "active": True},
    "external123": {
        "role": "external",
        "clearance": 1,
        "department": "Vendor",
        "active": False,
    },
}

resources = [
    ("prod_database", 4),
    ("dev_environment", 2),
    ("documentation", 1),
    ("source_code", 3),
    ("server_configs", 4),
    ("test_data", 2),
    ("compliance_docs", 3),
    ("system_logs", 4),
    ("project_files", 2),
    ("public_wiki", 1),
]

security_levels = ("Open", "Internal", "Restricted", "Top Secret")

blocked_users = {"external123", "old_account", "test_user"}


def check_access(username, resource, users_dict, blocked_users):
    res_name, res_level = resource

    if username in blocked_users:
        return "DENY (User is blocked)"

    if username not in users_dict:
        return "DENY (User not found)"

    user_data = users_dict[username]

    if not user_data["active"]:
        return "DENY (Account inactive)"

    if user_data["clearance"] >= res_level:
        return "ALLOW"
    else:
        return "DENY (Insufficient clearance)"


def main():
    print(
        f"Студент: {STUDENT_NAME} | Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}\n"
    )

    print("=== 1. Список ресурсів та їх рівні доступу ===")
    print(f"{'Ресурс':<20} | {'Рівень безпеки':<20}")
    print("-" * 43)
    for res, level_num in resources:
        level_word = security_levels[level_num - 1]
        print(f"{res:<20} | {level_word:<20}")

    print("\n=== 2. Перевірка матриці доступу ===")
    all_users_to_test = list(users.keys()) + ["old_account", "unknown_user"]

    print(
        f"{'Користувач':<15} | {'Ресурс':<18} | {'Рівень ресурсу':<15} | {'Результат':<30}"
    )
    print("-" * 85)

    for username in all_users_to_test:
        for res_name, res_level in resources:
            level_label = security_levels[res_level - 1]
            result = check_access(
                username, (res_name, res_level), users, blocked_users
            )
            print(
                f"{username:<15} | {res_name:<18} | {level_label:<15} | {result:<30}"
            )



if __name__ == "__main__":
    main()
