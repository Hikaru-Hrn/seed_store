from pydantic import BaseModel
from typing import List, Optional

class ProductBase(BaseModel):
    title: str
    description: str
    price: float
    stock_quantity: int
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    class Config:
        from_attributes = True

# --- НОВЫЕ СХЕМЫ ДЛЯ ЗАКАЗОВ ---
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    items: List[OrderItemCreate]