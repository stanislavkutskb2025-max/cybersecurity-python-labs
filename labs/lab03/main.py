import sqlite3
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

import labs.lab03.repository as repo

class CategoryCreate(BaseModel):
    name: str

class RecordCreate(BaseModel):
    code: str
    title: str
    category_id: int
    value: float
    status: str



@app.get("/categories")
def get_categories():
    return repo.get_categories()

