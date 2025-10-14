from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "TruLedgr API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OAuth Configuration
    oauth_google_client_id: str = ""
    oauth_google_client_secret: str = ""
    oauth_microsoft_client_id: str = ""
    oauth_microsoft_client_secret: str = ""
    oauth_apple_client_id: str = ""
    oauth_apple_client_secret: str = ""
    oauth_apple_team_id: str = ""
    oauth_apple_key_id: str = ""
    oauth_redirect_uri: str = "http://localhost:8000/auth/oauth/callback"
    
    # Database
    database_url: str
    database_echo: bool = False
    
    # API Settings
    allowed_hosts: str = "*"
    
    # Import/Integration Settings
    max_import_file_size: int = 10 * 1024 * 1024  # 10MB
    supported_import_formats: list[str] = ["csv", "ofx", "qfx", "json"]
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    model_config = {
        "env_file": "api/.env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()