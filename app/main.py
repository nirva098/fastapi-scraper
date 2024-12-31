from fastapi import FastAPI, Depends, HTTPException, Request, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from scraper import Scraper
from storage import JSONStorage
from auth import TokenAuth
from models import Product
from utils import retry_request
from notifications import ConsoleNotification

app = FastAPI()

security = HTTPBearer()
auth = TokenAuth("dummy-secret-token")


def get_scraper(page_limit: int = Query(..., ge=1)) -> Scraper:
    base_url = "https://dentalstall.com"
    image_dir = "images"
    return Scraper(base_url, page_limit, image_dir)


def authenticate(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """ Dependency to validate token authentication """
    token = credentials.credentials
    if not auth.validate_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/scrape", response_model=List[Product])
def scrape(
    scraper: Scraper = Depends(get_scraper),
    token: HTTPAuthorizationCredentials = Depends(authenticate)
):
    # Initialize Notification
    notifier = ConsoleNotification()

    # Perform scraping
    products = scraper.scrape()

    # Save products to JSON storage
    storage = JSONStorage("products.json")
    storage.save(products)

    # Send notification about the scraping process
    num_products = len(products)
    notifier.send_message(
        f"Scraping completed. {num_products} products were scraped and stored.")

    return products
