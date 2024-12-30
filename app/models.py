# models.py
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class Product(BaseModel):
    product_title: str
    product_price: float
    path_to_image: Optional[str]
    last_updated: datetime = datetime.now()


class ScrapingConfig(BaseModel):
    url: HttpUrl
    page_limit: Optional[int] = None
    proxy: Optional[str] = None
    selectors: dict
