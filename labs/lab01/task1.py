import os
import random
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

# варіант 2

passwords = [
    "Hello123!",
    "simple",
    "CompL3x@Pass",
    "password",
    "Str0ng#2023",
    "weak",
    "MySecur3!",
    "12345",
    "Advanced@1",
    "basic",
]

criteria = {
    "min_length": 10,
    "require_digits": True,
    "require_upper": True,
    "require_special": True,
}

forbidden_passwords = {"password", "simple", "weak", "basic", "12345", "hello"}


def get_password_category(pwd):
    min_length = criteria["min_length"]

    has_digit = any(c.isdigit() for c in pwd) if criteria["require_digits"] else True
    has_upper = any(c.isupper() for c in pwd) if criteria["require_upper"] else True
    has_special = (
        any(c in "!@#$%^&*()_+-=" for c in pwd) if criteria["require_special"] else True
    )
    has_lower = any(c.islower() for c in pwd)

    all_criteria = len(pwd) >= min_length and has_digit and has_upper and has_special

    if pwd in forbidden_passwords or len(pwd) < min_length:
        return "Заборонений"

    elif has_digit or has_upper or has_special or has_lower:
        return "Слабкий"
    elif len(pwd) >= min_length and (has_digit or has_upper or has_special):
        return "Середній"
    elif all_criteria and len(pwd) < min_length + 4:
        return "Сильний"
    elif all_criteria and len(pwd) >= min_length + 4 and passwords.count(pwd) == 1:
        return "Дуже сильний"


if __name__ == "__main__":
    for _ in range(3):
        random_index = random.randint(0, len(passwords) - 1)
        chosen_password = passwords[random_index]
        passwords.append(chosen_password)

    forbidden_list = []
    weak_list = []
    moderate_list = []
    strong_list = []
    very_strong_list = []

    results = []
    for pwd in passwords:
        category = get_password_category(pwd)
        results.append((pwd, category))

        if category == "Заборонений":
            forbidden_list.append(pwd)
        elif category == "Слабкий":
            weak_list.append(pwd)
        elif category == "Середній":
            moderate_list.append(pwd)
        elif category == "Сильний":
            strong_list.append(pwd)
        elif category == "Дуже сильний":
            very_strong_list.append(pwd)

    print(
        f"Студент: {STUDENT_NAME} | Група: {GROUP_NAME} | Варіант: {VARIANT_NUMBER}\n"
    )
    print(f"{'Пароль':<20} | {'Категорія надійності':<20}")
    print("-" * 43)
    for pwd, cat in results:
        print(f"{pwd:<20} | {cat:<20}")
