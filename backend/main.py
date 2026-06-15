from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import shutil
import os

import models
import schemas
from database import engine, get_db
from typing import List, Optional

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Дом Семян API")

# Папка для загрузки фото
os.makedirs("../frontend/uploads", exist_ok=True)

from pydantic import BaseModel


class LoginData(BaseModel):
    password: str


# 1. АВТОРИЗАЦИЯ АДМИНА
@app.post("/api/admin/login")
def login(data: LoginData):
    if data.password == "admin123":  # Пароль для входа
        return {"token": "valid_token"}
    raise HTTPException(status_code=401, detail="Неверный пароль")


# 2. ЗАГРУЗКА ФОТО
@app.post("/api/upload/")
def upload_image(file: UploadFile = File(...)):
    file_location = f"../frontend/uploads/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"image_url": f"/static/uploads/{file.filename}"}


# 3. CRUD ТОВАРОВ (Создание, Чтение, Обновление, Удаление)
@app.post("/api/products/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


# Эндпоинт для получения списка товаров
@app.get("/api/products/", response_model=List[schemas.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Product)
    if search:
        query = query.filter(models.Product.title.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

# Эндпоинт для получения общего количества товаров (для пагинации)
@app.get("/api/products/count")
def count_products(search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Product)
    if search:
        # ilike обеспечивает поиск без учета регистра букв
        query = query.filter(models.Product.title.ilike(f"%{search}%"))
    return {"total": query.count()}


@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Товар не найден")


@app.put("/api/products/{product_id}")
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    for key, value in product.model_dump().items():
        setattr(db_product, key, value)
    db.commit()
    return db_product


# --- ЗАКАЗЫ ---
@app.post("/api/orders/")
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    db_order = models.Order(customer_name=order.customer_name, customer_phone=order.customer_phone)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item in order.items:
        db_item = models.OrderItem(order_id=db_order.id, product_id=item.product_id, quantity=item.quantity)
        db.add(db_item)
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