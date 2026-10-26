import sqlite3
from fastapi import APIRouter, HTTPException, status
import labs.lab03.repository as repo
from labs.lab03.schemas import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryRead])
def get_categories():
    return repo.get_categories()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CategoryRead)
def create_category(payload: CategoryCreate):
    try:
        return repo.create_category(payload.name)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Категорія з такою назвою вже існує",
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int):
    try:
        deleted = repo.delete_category(category_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категорію не знайдено",
            )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Неможливо видалити категорію, що містить записи",
        )
