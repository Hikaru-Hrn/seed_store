from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Дом Семян API")


# --- API ТОВАРОВ ---
@app.post("/api/products/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/api/products/", response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Product).offset(skip).limit(limit).all()


# --- API ЗАКАЗОВ ---
@app.post("/api/orders/")
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    # 1. Создаем запись о заказе
    db_order = models.Order(customer_name=order.customer_name, customer_phone=order.customer_phone)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # 2. Добавляем товары в заказ и списываем их со склада
    for item in order.items:
        db_item = models.OrderItem(order_id=db_order.id, product_id=item.product_id, quantity=item.quantity)
        db.add(db_item)

        # Уменьшаем количество на складе
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product and product.stock_quantity >= item.quantity:
            product.stock_quantity -= item.quantity

    db.commit()
    return {"message": "Заказ успешно оформлен!", "order_id": db_order.id}


# --- ФРОНТЕНД ---
app.mount("/static", StaticFiles(directory="../frontend"), name="static")


@app.get("/")
def read_index():
    return FileResponse("../frontend/index.html")


@app.get("/admin")
def read_admin():
    return FileResponse("../frontend/admin.html")