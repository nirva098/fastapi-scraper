import json
from abc import ABC, abstractmethod
from typing import List
from models import Product


class Storage(ABC):
    @abstractmethod
    def save(self, products: List[Product]):
        pass


class JSONStorage(Storage):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def save(self, products: List[Product]):
        try:
            with open(self.file_path, "w") as json_file:
                json.dump([product.dict()
                          for product in products], json_file, indent=4)
            print("Product data saved to products.json")
        except Exception as e:
            print(f"Failed to save product data: {e}")
