from pydantic import BaseModel

class ProductBase(BaseModel):
    title: str
    description: str
    price: float
    stock_quantity: int
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    class Config:
        from_attributes = True