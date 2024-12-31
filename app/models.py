from pydantic import BaseModel


class Product(BaseModel):
    title: str
    price: float
    img_path: str
