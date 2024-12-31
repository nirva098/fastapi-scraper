import os
import re
import base64
from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from models import Product
from utils import retry_request


class Scraper:
    def __init__(self, base_url: str, page_limit: int, image_dir: str):
        self.base_url = base_url
        self.page_limit = page_limit
        self.image_dir = image_dir

    def scrape(self) -> List[Product]:
        products = []

        # Create image directory if it doesn't exist
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)

        for page in range(1, self.page_limit + 1):
            url = f"{self.base_url}/shop/page/{page}"
            response = retry_request(url)

            if response is None:
                break  # Stop if retries fail

            soup = BeautifulSoup(response.text, "html.parser")
            product_elements = soup.select("li.product")

            for item in product_elements:
                product = self.extract_product_info(item)
                if product:
                    products.append(product)

        return products

    def extract_product_info(self, item) -> Product:
        title_element = item.select_one(".woo-loop-product__title a")
        img_element = item.select_one("img")
        price_element = item.select_one(".price ins .woocommerce-Price-amount")

        title = title_element.text.strip() if title_element else "Unknown"
        price = float(price_element.text.strip().replace(
            "₹", "").replace(",", "")) if price_element else None

        # Extract image URL and save the image
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
        # Handling for base64 and regular URLs
        image_path = ""
        if img_url.startswith('data:'):
            image_path = self.handle_data_url(img_url, title)
        else:
            image_path = self.handle_external_url(img_url, title)

        return image_path

    def handle_data_url(self, img_url: str, title: str) -> str:
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
                self.image_dir, f"{sanitized_title}.{file_extension}")

            with open(image_filename, "wb") as img_file:
                img_file.write(image_data)

            image_path = image_filename
            return image_path
        except Exception as e:
            print(f"Failed to save image for {title}: {e}")
