import requests
import time
from typing import Optional


def retry_request(url: str, retries: int = 3, delay: int = 5) -> Optional[requests.Response]:
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response
            print(f"Failed request, status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error occurred: {e}")
        attempt += 1
        time.sleep(delay)
    return None


def parsing_util(content: str, selector: str, parser_type: str):
    # does some parsing
    # create the list of dictionaries from the HTML content
    dummy = [{}]
    return dummy
