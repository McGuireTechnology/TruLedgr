from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Optional
import os
from enum import Enum

class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    STAGING = "staging"
    SANDBOX = "sandbox"

class Settings(BaseSettings):
    # General
    environment: EnvironmentType = Field(EnvironmentType.DEVELOPMENT, env="ENVIRONMENT")

    # FastAPI
    fastapi_name: str = Field("TruLedgr", env="FASTAPI_NAME")
    fastapi_debug: Optional[bool] = Field(None, env="FASTAPI_DEBUG")
   
    # Uvicorn
    uvicorn_host: str = Field("0.0.0.0", env="UVICORN_HOST")
    uvicorn_port: int = Field(8000, env="UVICORN_PORT")
    uvicorn_reload: Optional[bool] = Field(None, env="UVICORN_RELOAD")
    
    # CORS Middleware
    cors_allowed_origins: List[str] = Field(default_factory=list, env="CORS_ALLOWED_ORIGINS")
    cors_allow_credentials: bool = Field(True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default_factory=lambda: ["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default_factory=lambda: ["*"], env="CORS_ALLOW_HEADERS")
    
    # SQL Alchemy
    sqlalchemy_db_url: str = Field(None, env="SQLALCHEMY_DB_URL")

    # Sentry
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    sentry_default_pii: bool = Field(True, env="SENTRY_DEFAULT_PII")
    sentry_environment: str = Field("unknown", env="SENTRY_ENVIRONMENT")
    sentry_traces_sample_rate: float = Field(1.0, env="SENTRY_TRACES_SAMPLE_RATE")
    sentry_profile_session_sample_rate: float = Field(1.0, env="SENTRY_PROFILE_SESSION_SAMPLE_RATE")
    sentry_profile_lifecycle: str = Field("trace", env="SENTRY_PROFILE_LIFECYCLE")

    # Private routes
    include_private_routes: Optional[bool] = Field(None, env="INCLUDE_PRIVATE_ROUTES")

    # Security
    security_access_token_expire_minutes: int = Field(..., env="SECURITY_ACCESS_TOKEN_EXPIRE_MINUTES")
    security_secret_key: str = Field(..., env="SECURITY_SECRET_KEY")

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")

    @field_validator("environment", mode="before")
    @classmethod
    def validate_environment(cls, v):
        if isinstance(v, str):
            v = v.lower()
        try:
            return EnvironmentType(v)
        except ValueError:
            raise ValueError(f"Invalid environment: {v}. Must be one of: {[e.value for e in EnvironmentType]}")

    def __init__(self, **values):
        super().__init__(**values)
        # fastapi_debug: on by default in development, off otherwise unless explicitly set
        if self.fastapi_debug is None:
            self.fastapi_debug = self.environment == EnvironmentType.DEVELOPMENT
        if self.uvicorn_reload is None:
            self.uvicorn_reload = self.fastapi_debug
        if self.include_private_routes is None:
            self.include_private_routes = self.environment == EnvironmentType.DEVELOPMENT

settings = Settings()