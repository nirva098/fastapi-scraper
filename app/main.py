from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from typing import List

app = FastAPI()


class Product(BaseModel):
    title: str


@app.get("/scrape", response_model=List[Product])
def scrape(page_limit: int):
    products = []

    for page in range(1, page_limit + 1):
        url = f"https://dentalstall.com/shop/page/{page}"
        response = requests.get(url)

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        product_elements = soup.select("li.product")

        for item in product_elements:
            title_element = item.select_one(".woo-loop-product__title a")
            if title_element:
                products.append(Product(title=title_element.text.strip()))

    return products
