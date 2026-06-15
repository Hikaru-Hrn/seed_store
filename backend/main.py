from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db

# Создаем таблицы в БД, если их нет
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Дом Семян API")

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в API Дом Семян!"}

# Эндпоинт для добавления нового товара
@app.post("/products/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Эндпоинт для получения списка всех товаров
@app.get("/products/", response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products