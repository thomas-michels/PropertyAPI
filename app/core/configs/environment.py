"""
Module to load all Environment variables
"""

from pydantic_settings import BaseSettings


class Environment(BaseSettings):
    """
    Environment, add the variable and its type here matching the .env file
    """

    # APPLICATION
    APPLICATION_HOST: str = "localhost"
    APPLICATION_PORT: int = 8000
    IS_LOCALSTACK: bool = False

    # DATABASE
    DATABASE_URL: str = "localhost:5432"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "user"
    DATABASE_PASSWORD: str = "password"
    DATABASE_NAME: str = "test"
    ENVIRONMENT: str = "test"
    DATABASE_MIN_CONNECTIONS: int = 1
    DATABASE_MAX_CONNECTIONS: int = 1

    # S3
    BUCKET_BASE_URL: str = "localhost"
    BUCKET_ACCESS_KEY_ID: str = "test"
    BUCKET_SECRET_KEY: str = "test"
    BUCKET_NAME: str = "test"
    BUCKET_ACL: str = "test"
    BUCKET_URL_EXPIRES_IN_SECONDS: int = 0

    class Config:
        """Load config file"""

        env_file = ".env"
        extra='ignore'
