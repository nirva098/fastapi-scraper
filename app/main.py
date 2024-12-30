import os
import re
import base64
from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urljoin

app = FastAPI()


class Product(BaseModel):
    title: str
    price: float
    img_path: str


@app.get("/scrape", response_model=List[Product])
def scrape(page_limit: int):
    products = []
    image_dir = "images"
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    for page in range(1, page_limit + 1):
        url = f"https://dentalstall.com/shop/page/{page}"
        response = requests.get(url)

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        product_elements = soup.select("li.product")

        for item in product_elements:
            title_element = item.select_one(".woo-loop-product__title a")
            img_element = item.select_one("img")
            price_element = item.select_one(
                ".price ins .woocommerce-Price-amount")

            title = title_element.text.strip() if title_element else "Unknown"
            print("Title 45 ", title)
            if price_element:
                price = float(price_element.text.strip().replace(
                    "₹", "").replace(",", ""))
            else:
                continue

            # Extract image URL
            image_path = ""
            if img_element and "src" in img_element.attrs:
                img_url = urljoin(url, img_element["src"])
                # print("Image url", img_url)
                if img_url.startswith('data:'):
                    try:
                        base64_data = img_url.split(',')[1]
                        image_data = base64.b64decode(
                            base64_data)
                        if "svg+xml" in img_url:
                            file_extension = "svg"
                        elif "png" in img_url:
                            file_extension = "png"
                        else:
                            file_extension = "jpg"

                        sanitized_title = re.sub(r'[\\/*?:"<>|]', "", title)
                        image_filename = os.path.join(
                            image_dir, f"{sanitized_title}.{file_extension}")

                        with open(image_filename, "wb") as img_file:
                            img_file.write(image_data)

                        image_path = image_filename
                    except Exception as e:
                        print(f"Failed to save image for {title}: {e}")

                else:
                    sanitized_title = re.sub(r'[\\/*?:"<>|]', "", title)
                    image_filename = os.path.join(
                        image_dir, f"{sanitized_title}.jpg")
                    try:
                        img_data = requests.get(img_url).content
                        with open(image_filename, "wb") as img_file:
                            img_file.write(img_data)
                        image_path = image_filename
                    except Exception as e:
                        print(f"Failed to save image for {title}: {e}")

            if title:
                products.append(
                    Product(title=title, price=price, img_path=image_path))

    return products
