import re
from pydantic import BaseModel, field_validator
from typing import List, Optional

class ProductBase(BaseModel):
    title: str
    description: str
    price: float
    stock_quantity: int
    category_id: Optional[int] = None
    image_url: Optional[str] = None # Фото

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    class Config:
        from_attributes = True

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    items: List[OrderItemCreate]

    # ВАЛИДАЦИЯ ТЕЛЕФОНА (Пункт 2)
    @field_validator('customer_phone')
    @classmethod
    def validate_ru_phone(cls, v):
        pattern = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
        if not re.match(pattern, v):
            raise ValueError('Некорректный номер телефона РФ')
        return v