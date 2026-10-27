# Лабораторна робота №3 (Варіант 2)
## Сервіс перевірки мережевих сервісів

Цей проєкт є навчальним REST API вебсервісом на базі **FastAPI** та **SQLite** для обліку, моніторингу та аналізу результатів діагностики доступності й безпеки мережевої інфраструктури.

---

### 📌 Опис предметної області
* **Предметна область:** Перевірки мережевих сервісів (`mail`, `vpn`, `dns`).
* **Одиниця вимірювання (`value`):** Час відгуку / затримка мережевого з'єднання у мілісекундах (**мс**).
* **Поріг небезпеки (Threshold):** **`6.0`** (значення `value >= 6.0` свідчать про критичну затримку чи високу ймовірність вразливості сервісу).

---

### 🚀 Кроки для запуску проєкту з нуля

#### 1. Клонування репозиторію та перехід у папку проєкту
```bash
git clone <URL_ВАШОГО_РЕПОЗИТОРІЮ>
cd cybersecurity-python-labs
```

#### 2. Створення та активація віртуального середовища Python
* **Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```


#### 3. Встановлення залежностей проєкту
```bash
pip install -r requirements.txt
```

#### 4. Початкове заповнення бази даних (Seed)
Запустіть скрипт для створення таблиць у SQLite та їх початкового заповнення 3 категоріями й 8 записами з файлу `labs/lab03/data/seed.json`:
```bash
python -m labs.lab03.seed
```

#### 5. Запуск вебсервера розробки (API)
```bash
uvicorn labs.lab03.main:app --reload --host 127.0.0.1 --port 8000
```

Після запуску відкрийте браузер за адресами:
* 👉 **Swagger UI (Інтерактивна документація):** http://127.0.0.1:8000/docs
* 👉 **OpenAPI Schema (JSON):** http://127.0.0.1:8000/openapi.json

---

### 🧪 Приклади основних запитів (cURL)

#### 1. Перевірка статусу системи (Ping)
```bash
curl -i -X GET "[http://127.0.0.1:8000/ping](http://127.0.0.1:8000/ping)"
```
*Очікувано:* `200 OK`, `{"status": "ok"}`

#### 2. Отримання інформації про студента
```bash
curl -i -X GET "[http://127.0.0.1:8000/student](http://127.0.0.1:8000/student)"
```

#### 3. Отримання списку всіх категорій
```bash
curl -i -X GET "[http://127.0.0.1:8000/categories](http://127.0.0.1:8000/categories)"
```

#### 4. Отримання записів з фільтрацією та пагінацією
```bash
curl -i -X GET "[http://127.0.0.1:8000/records?category_id=1&status=new&limit=5&offset=0](http://127.0.0.1:8000/records?category_id=1&status=new&limit=5&offset=0)"
```

#### 5. Створення нового запису
```bash
curl -i -X POST "[http://127.0.0.1:8000/records](http://127.0.0.1:8000/records)" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "V02-TEST",
    "title": "Перевірка поштового сервера",
    "category_id": 1,
    "value": 7.5,
    "status": "new"
  }'
```
*Очікувано:* `201 Created` із згенерованим `id` та `category_name: "mail"`.

#### 6. Повне оновлення запису (PUT)
```bash
curl -i -X PUT "[http://127.0.0.1:8000/records/1](http://127.0.0.1:8000/records/1)" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "V02-01",
    "title": "Оновлена перевірка сервісу 01",
    "category_id": 1,
    "value": 4.5,
    "status": "in_progress"
  }'
```

#### 7. Видалення запису за ідентифікатором
```bash
curl -i -X DELETE "[http://127.0.0.1:8000/records/1](http://127.0.0.1:8000/records/1)"
```
*Очікувано:* `204 No Content`.

#### 8. Пакетне додавання записів (Bulk Insert)
```bash
curl -i -X POST "[http://127.0.0.1:8000/records/bulk](http://127.0.0.1:8000/records/bulk)" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "code": "V02-BULK1",
      "title": "Перша пакетна перевірка",
      "category_id": 2,
      "value": 3.2,
      "status": "new"
    },
    {
      "code": "V02-BULK2",
      "title": "Друга пакетна перевірка",
      "category_id": 3,
      "value": 5.8,
      "status": "new"
    }
  ]'
```

---

### 🛠 Перевірка якості коду (Formatting & Linting)

Для перевірки форматування та відповідності стандартам PEP 8 використовується інструмент **Ruff**:

* **Перевірка стилю та помилок:**
  ```bash
  ruff check labs/lab03
  ```
* **Автоматичне форматування:**
  ```bash
  ruff format labs/lab03
  ```