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


for res, level_num in resources:
    level_word = security_levels[level_num - 1]
    print(f"{res:<20} | {level_word:<20}")


def check_access(username, resource, users_dict, blocked_users):
    res_name, res_level = resource
    if username not in users_dict:
        return "DENY (User not found)"

    if username in blocked_users:
        return "DENY (User is blocked)"

    user_data = users_dict[username]

    if user_data["active"] == False:
        return "DENY (Account inactive)"

    if user_data["clearance"] >= res_level:
        return "ALLOW"
    else:
        return "DENY (Insufficient clearance)"


all_users_to_test = list(users.keys()) + ["blocked_user_example", "unknown_user"]

print(
    f"{'Користувач':<15} | {'Ресурс':<18} | {'Рівень ресурсу':<15} | {'Результат':<30}"
)
print("-" * 85)

for username in all_users_to_test:
    for res_name, res_level in resources:
        level_label = security_levels[res_level - 1]

        result = check_access(username, (res_name, res_level), users, blocked_users)

        print(f"{username:<15} | {res_name:<18} | {level_label:<15} | {result:<30}")
