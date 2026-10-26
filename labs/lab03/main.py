from contextlib import asynccontextmanager
from fastapi import FastAPI

from labs.lab03.database import initialize_database
from labs.lab03.routers import categories, records, system


# ініціалізація БД через lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Створюємо відсутні таблиці під час запуску застосунку
    initialize_database()
    yield


# створення застосунку з назвою та описом предметної області
app = FastAPI(
    title="Сервіс перевірки мережевих сервісів",
    description=(
        "Лабораторна робота №3 (Варіант 2). "
        "Предметна область: перевірки мережевих сервісів (mail, vpn, dns). "
        "Одиниця вимірювання value: час відгуку / затримка у мілісекундах (мс)."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# підключення маршрутів із модулів routers
app.include_router(system.router)
app.include_router(categories.router)
app.include_router(records.router)
