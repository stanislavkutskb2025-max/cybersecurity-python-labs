from fastapi import APIRouter
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

router = APIRouter(tags=["System"])


@router.get("/ping")
def ping():
    return {"status": "ok"}


@router.get("/student")
def student():
    return {
        "student_name": STUDENT_NAME,
        "group_name": GROUP_NAME,
        "variant_number": VARIANT_NUMBER,
    }
