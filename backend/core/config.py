from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017/"
    secret_key: str = "your-super-secret-key-change-in-production!"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

settings = Settings(_env_file=".env")

