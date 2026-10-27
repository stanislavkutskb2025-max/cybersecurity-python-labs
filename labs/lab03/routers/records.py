import sqlite3
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

import labs.lab03.repository as repo
from labs.lab03.schemas import (
    RecordCreate,
    RecordRead,
    RecordReplace,
)

router = APIRouter(prefix="/records", tags=["Records"])


# 1. Отримання списку записів з фільтрацією та пагінацією
@router.get("", response_model=list[RecordRead])
def get_records(
    category_id: int | None = Query(None, gt=0),
    status: Literal["new", "in_progress", "done"] | None = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return repo.get_records(
        category_id=category_id,
        status=status,
        limit=limit,
        offset=offset,
    )


# 2. Пакетне додавання записів
@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def create_records_bulk(payload: list[RecordCreate]):
    if not (1 <= len(payload) <= 100):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Кількість елементів пакета має бути від 1 до 100",
        )

    categories = {c["id"] for c in repo.get_categories()}
    for item in payload:
        if item.category_id not in categories:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категорію з id={item.category_id} не знайдено",
            )

    try:
        records_data = [item.model_dump() for item in payload]
        repo.create_records_batch(records_data)
        return {"message": f"Успішно додано {len(payload)} записів"}
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Помилка унікальності code або даних у пакеті",
        )


# 3. Отримання одного запису за ID
@router.get("/{record_id}", response_model=RecordRead)
def get_record(record_id: int):
    if record_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ID має бути додатним числом",
        )
    record = repo.get_record_by_id(record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запис не знайдено",
        )
    return record


# 4. Створення одного запису
@router.post("", status_code=status.HTTP_201_CREATED, response_model=RecordRead)
def create_record(payload: RecordCreate):
    categories = {c["id"] for c in repo.get_categories()}
    if payload.category_id not in categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вказану категорію не знайдено",
        )

    try:
        return repo.create_record(payload.model_dump())
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Запис із таким кодом вже існує",
        )


# 5. Повна заміна/оновлення запису за ID
@router.put("/{record_id}", response_model=RecordRead)
def update_record(record_id: int, payload: RecordReplace):
    if record_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ID має бути додатним числом",
        )

    categories = {c["id"] for c in repo.get_categories()}
    if payload.category_id not in categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вказану категорію не знайдено",
        )

    try:
        updated = repo.update_record(record_id, payload.model_dump())
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Запис не знайдено",
            )
        return updated
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Запис із таким кодом вже існує",
        )


# 6. Видалення запису за ID
@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(record_id: int):
    if record_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ID має бути додатним числом",
        )

    deleted = repo.delete_record(record_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запис не знайдено",
        )
