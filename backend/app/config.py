"""Application configuration using Pydantic BaseSettings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    database_url: str

    # JWT Configuration
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"

    # API Configuration
    api_v1_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000

    # Environment
    environment: str = "development"

    # CORS Configuration
    cors_origins: str = "http://localhost:3000"

    # Database Connection Pooling (Neon PostgreSQL)
    db_pool_size: int = 10
    db_max_overflow: int = 20

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


# Create settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings