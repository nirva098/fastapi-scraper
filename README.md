# Web Scraper Project

## Overview
This is a web scraping project built using Python, FastAPI, and Redis. It scrapes product data from a sample website (https://dentalstall.com), including product titles, prices, and images. The scraped data is saved in a JSON file, and notifications about the scraping session are sent to a specified recipient. Additionally, a caching mechanism is implemented using Redis to prevent unnecessary updates to unchanged product prices.

## Features
- **Scraping**: Extracts product titles, prices, and images.
- **Data Storage**: Saves scraped data in a `products.json` file (which can be easily swapped out for a database like MongoDB in the future).
- **Caching**: Uses Redis to cache scraping results and ensure that product price updates are only saved when the price has changed.
- **Notifications**: Notifies users about scraping status via console messages. It can be extended to support more sophisticated notification strategies (Slack, Email, etc.).

---

## Requirements

### Set up the environment

1. **Install Python dependencies**:
   ```pip install -r requirements.txt```

2. **Run Redis in Docker: This project uses Redis for caching and managing scraping results. To run Redis locally via Docker:**

  ```docker run -d -p 6379:6379 redis```

3. **Run the FastAPI app: Start the FastAPI application using uvicorn:**
  ```uvicorn main:app --reload```

---

## Brief Overview of Key Features

### Authentication
The application uses a simple static token-based authentication system. The token is checked before scraping operations begin. A more advanced authentication method (e.g., OAuth2) & authorization middleware can be implemented for improved security.

### Notification
The notification system currently prints a simple message to the console about the scraping status. You can extend it to other notification methods (e.g., Slack, Email) by implementing the `Notification` interface.

### Database
Currently, the scraped data is stored in a `products.json` file. In the future, this can be swapped out for a database like MongoDB for better scalability and querying capabilities.

### Caching
Redis is used for caching product prices to prevent unnecessary database updates. If the price of a product hasn’t changed, the data won’t be updated in the database. This optimizes performance and reduces redundant writes.


## What's not done?
**Proxy Support**: No proxy functionality has been implemented yet. For scaling the scraping process, using a proxy rotation service would be helpful to prevent IP blocking.





