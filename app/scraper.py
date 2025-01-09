import os
import re
import base64
from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from models import Product
from utils import retry_request, parsing_util
import redis
from config import settings
from datetime import datetime


class Scraper:
    def __init__(self, base_url: str, page_limit: int, image_dir: str):
        self.base_url = base_url
        self.page_limit = page_limit
        self.image_dir = image_dir
        self.redis_client = redis.StrictRedis.from_url(
            settings.REDIS_URL, decode_responses=True)

    def scrape(self) -> List[Product]:
        products = []
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)

        for page in range(1, self.page_limit + 1):
            url = f"{self.base_url}/shop/page/{page}"
            response = retry_request(url)

            if response is None:
                break  # Stop if retries fail

            current_time = datetime.now()
            current_day = datetime.isoweekday(current_time)

            product_elements = []
            parsed_products = []

            if current_day > 5:
                # weekend
                parsed_products = parsing_util(
                    response.text, "li.product", "html.parser")

            else:
                # weekday
                soup = BeautifulSoup(response.text, "html.parser")
                product_elements = soup.select("li.product")
                for item in product_elements:
                    product = self.extract_product_info(item)
                    parsed_products.append(product)

            for product in parsed_products:
                if product and self.is_new_or_updated(product):
                    products.append(product)
                    self.cache_product(product)

        return products

    def extract_product_info(self, item) -> Product:
        title_element = item.select_one(".woo-loop-product__title a")
        img_element = item.select_one("img")
        price_element = item.select_one(".price ins .woocommerce-Price-amount")

        title = title_element.text if title_element else "Unknown"
        print(f"Title ", title)
        price = float(price_element.text.strip().replace(
            "₹", "").replace(",", "")) if price_element else None

        image_path = self.save_image(img_element, title)

        if title and price and image_path:
            return Product(title=title, price=price, img_path=image_path)
        return None

    def save_image(self, img_element, title: str) -> str:
        if img_element and "src" in img_element.attrs:
            img_url = urljoin(self.base_url, img_element["src"])
            image_path = self.download_image(img_url, title)
            return image_path
        return ""

    def download_image(self, img_url: str, title: str) -> str:
        image_path = ""
        if img_url.startswith('data:'):
            image_path = self.handle_data_url(img_url, title)
        else:
            image_path = self.handle_external_url(img_url, title)

        return image_path

    def handle_data_url(self, img_url: str, title: str) -> str:
        try:
            base64_data = img_url.split(',')[1]
            image_data = base64.b64decode(base64_data)
            file_extension = self.get_file_extension(img_url)

            sanitized_title = re.sub(r'[\\/*?:"<>|]', "", title)
            image_filename = os.path.join(
                self.image_dir, f"{sanitized_title}.{file_extension}")

            with open(image_filename, "wb") as img_file:
                img_file.write(image_data)

            return image_filename
        except Exception as e:
            print(f"Failed to save image for {title}: {e}")
            return ""

    def handle_external_url(self, img_url: str, title: str) -> str:
        try:
            sanitized_title = re.sub(r'[\\/*?:"<>|]', "", title)
            file_extension = os.path.splitext(img_url)[1][1:]
            image_filename = os.path.join(
                self.image_dir, f"{sanitized_title}.{file_extension}")

            img_data = retry_request(img_url).content
            with open(image_filename, "wb") as img_file:
                img_file.write(img_data)

            return image_filename
        except Exception as e:
            print(f"Failed to download image for {title}: {e}")
            return ""

    def get_file_extension(self, img_url: str) -> str:
        if "svg+xml" in img_url:
            return "svg"
        elif "png" in img_url:
            return "png"
        return "jpg"

    def is_new_or_updated(self, product: Product) -> bool:
        """Checks if the product is new or its price has changed."""
        cached_product = self.redis_client.get(product.title)

        if cached_product:
            cached_price = float(cached_product)
            if cached_price != product.price:
                print(f"Product {product}, cached price {cached_price}")
        return True

    def cache_product(self, product: Product):
        """Caches the product data in Redis."""
        try:
            self.redis_client.set(product.title, product.price)
        except Exception as e:
            print(f"Failed to cache product {product.title}: {e}")
