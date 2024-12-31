from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    AUTH_TOKEN: str = "dummy-secret-token"
    REDIS_URL: str = "redis://localhost:6379"
    RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
