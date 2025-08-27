"""
Application settings and configuration management.

Moved from fastapi_security_sample.config to provide centralized
configuration with better organization.
"""

import os
from functools import lru_cache
from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    SANDBOX = "sandbox"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class LogFormat(str, Enum):
    """Log format options."""
    TEXT = "text"
    JSON = "json"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=[".env", ".env.local"],  # Base config + local overrides only
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_parse_none_str="None",
        env_nested_delimiter="__"
    )
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    app_name: str = "FastAPI Security Sample"
    app_version: str = "2.0.0"
    debug: bool = False
    environment: Environment = Environment.DEVELOPMENT
    
    # =============================================================================
    # SECURITY SETTINGS
    # =============================================================================
    secret_key: str = Field(default="dev-secret-key-change-this", min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Password Reset
    password_reset_token_expire_minutes: int = 15
    password_reset_url_base: str = "http://localhost:8000/reset-password"
    password_reset_max_tokens_per_user: int = 3
    password_reset_token_rotation: bool = True
    password_reset_cleanup_interval_minutes: int = 60
    
    # TOTP
    totp_issuer_name: str = "FastAPI Auth App"
    
    # =============================================================================
    # OAUTH2 SOCIAL LOGIN SETTINGS
    # =============================================================================
    oauth2_enabled: bool = False
    oauth2_session_secret: str = Field(default="oauth-session-secret-change-this", min_length=32)
    oauth2_base_url: str = "http://localhost:8000"
    
    # Google OAuth2
    google_oauth2_enabled: bool = False
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = "/auth/oauth2/google/callback"
    
    # Microsoft OAuth2
    microsoft_oauth2_enabled: bool = False
    microsoft_client_id: Optional[str] = None
    microsoft_client_secret: Optional[str] = None
    microsoft_tenant_id: str = "common"
    microsoft_redirect_uri: str = "/auth/oauth2/microsoft/callback"
    
    # Apple OAuth2
    apple_oauth2_enabled: bool = False
    apple_client_id: Optional[str] = None
    apple_team_id: Optional[str] = None
    apple_key_id: Optional[str] = None
    apple_private_key: Optional[str] = None
    apple_redirect_uri: str = "/auth/oauth2/apple/callback"
    
    # =============================================================================
    # DATABASE SETTINGS
    # =============================================================================
    database_url: str = Field(default="sqlite+aiosqlite:///./test.db")
    test_database_url: str = "sqlite+aiosqlite:///:memory:"
    
    # Database Pool Settings
    db_pool_size: int = 20
    db_max_overflow: int = 0
    db_pool_recycle: int = 300
    db_echo: bool = False
    
    # =============================================================================
    # REDIS SETTINGS
    # =============================================================================
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = False
    
    # =============================================================================
    # SECURITY & RATE LIMITING
    # =============================================================================
    max_login_attempts: int = 5
    account_lockout_duration_minutes: int = 30
    
    rate_limit_requests: int = 100
    rate_limit_window_minutes: int = 15
    
    # Session Management
    max_sessions_per_user: int = 5
    session_timeout_hours: int = 24
    enable_session_analytics: bool = True
    session_cleanup_interval_hours: int = 6
    session_retention_days: int = 30
    
    # =============================================================================
    # EMAIL SETTINGS
    # =============================================================================
    email_enabled: bool = False
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_tls: bool = True
    email_from: str = "noreply@example.com"
    email_from_name: str = "FastAPI Auth"
    
    # =============================================================================
    # LOGGING SETTINGS
    # =============================================================================
    log_level: str = "INFO"
    log_format: LogFormat = LogFormat.TEXT
    log_file: Optional[str] = None
    log_rotation: str = "1 day"
    log_retention: str = "30 days"
    
    # =============================================================================
    # CORS SETTINGS
    # =============================================================================
    cors_origins: Union[str, List[str]] = [
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:5174"
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: Union[str, List[str]] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: Union[str, List[str]] = ["*"]
    
    # =============================================================================
    # CACHE CONFIGURATION
    # =============================================================================
    cache_enabled: bool = True
    cache_max_size: int = 1000
    cache_default_ttl: int = 300
    
    # =============================================================================
    # MONITORING & OBSERVABILITY SETTINGS
    # =============================================================================
    metrics_enabled: bool = Field(default=True, description="Enable Prometheus metrics collection")
    metrics_endpoint: str = Field(default="/metrics", description="Metrics endpoint path")
    
    tracing_enabled: bool = Field(default=True, description="Enable OpenTelemetry tracing")
    tracing_service_name: str = Field(default="fastapi-security-sample", description="Service name for tracing")
    tracing_sample_rate: float = Field(default=0.1, description="Tracing sample rate (0.0-1.0)")
    
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    sentry_traces_sample_rate: float = Field(default=0.1, description="Sentry traces sample rate")
    sentry_profiles_sample_rate: float = Field(default=0.1, description="Sentry profiles sample rate")
    sentry_log_level: str = Field(default="INFO", description="Sentry logging level")
    sentry_event_level: str = Field(default="ERROR", description="Sentry event level")
    
    health_check_enabled: bool = Field(default=True, description="Enable health check endpoints")
    health_check_timeout: int = Field(default=30, description="Health check timeout in seconds")
    
    slow_query_threshold: float = Field(default=1.0, description="Slow query threshold in seconds")
    slow_request_threshold: float = Field(default=2.0, description="Slow request threshold in seconds")
    
    # Background Tasks
    cleanup_interval_minutes: int = 5
    background_tasks_enabled: bool = True
    
    # =============================================================================
    # SERVER SETTINGS
    # =============================================================================
    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    
    ssl_keyfile: Optional[str] = None
    ssl_certfile: Optional[str] = None
    forwarded_allow_ips: str = "127.0.0.1"
    proxy_headers: bool = False
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v, info):
        """Validate that secret key is secure enough."""
        if v == "your-secret-key-change-this-in-production" or "change-this" in v.lower():
            if info.data.get("environment") == Environment.PRODUCTION:
                raise ValueError("Secret key must be changed from default value in production!")
        return v
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            if v.strip() == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        else:
            return [str(v)]
    
    @field_validator("cors_allow_methods", mode="before")
    @classmethod
    def parse_cors_methods(cls, v) -> List[str]:
        """Parse CORS methods from string or list."""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",") if method.strip()]
        elif isinstance(v, list):
            return v
        else:
            return [str(v)]
    
    @field_validator("cors_allow_headers", mode="before")
    @classmethod
    def parse_cors_headers(cls, v) -> List[str]:
        """Parse CORS headers from string or list."""
        if isinstance(v, str):
            if v.strip() == "*":
                return ["*"]
            return [header.strip() for header in v.split(",") if header.strip()]
        elif isinstance(v, list):
            return v
        else:
            return [str(v)]
    
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v.startswith(("sqlite+aiosqlite://", "postgresql+asyncpg://", "mysql+aiomysql://")):
            raise ValueError("Database URL must use an async driver (aiosqlite, asyncpg, aiomysql)")
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_test(self) -> bool:
        """Check if running in test mode."""
        return self.environment == Environment.TEST
    
    @property
    def database_url_for_env(self) -> str:
        """Get the appropriate database URL for the current environment."""
        if self.is_test:
            return self.test_database_url
        return self.database_url
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if isinstance(self.cors_origins, str):
            return self.parse_cors_origins(self.cors_origins)
        return self.cors_origins
    
    @property
    def cors_allow_methods_list(self) -> List[str]:
        """Get CORS methods as a list."""
        if isinstance(self.cors_allow_methods, str):
            return self.parse_cors_methods(self.cors_allow_methods)
        return self.cors_allow_methods
    
    @property 
    def cors_allow_headers_list(self) -> List[str]:
        """Get CORS headers as a list."""
        if isinstance(self.cors_allow_headers, str):
            return self.parse_cors_headers(self.cors_allow_headers)
        return self.cors_allow_headers


class DevelopmentSettings(Settings):
    """Development environment settings."""
    
    model_config = SettingsConfigDict(
        env_file=[".env", ".env.dev", ".env.local"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    debug: bool = True
    environment: Environment = Environment.DEVELOPMENT
    db_echo: bool = False
    log_level: str = "DEBUG"
    cors_origins: Union[str, List[str]] = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:8080",
        "http://localhost:5173",
        "http://localhost:5174"
    ]
    cache_enabled: bool = False
    email_enabled: bool = False


class SandboxSettings(Settings):
    """Sandbox environment settings for testing and demos."""
    
    model_config = SettingsConfigDict(
        env_file=[".env", ".env.sandbox", ".env.local"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    debug: bool = False
    environment: Environment = Environment.SANDBOX
    log_level: str = "INFO"


class StagingSettings(Settings):
    """Staging environment settings."""
    
    model_config = SettingsConfigDict(
        env_file=[".env", ".env.stage", ".env.local"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    debug: bool = False
    environment: Environment = Environment.STAGING
    log_level: str = "INFO"


class ProductionSettings(Settings):
    """Production environment settings."""
    
    model_config = SettingsConfigDict(
        env_file=[".env", ".env.prod", ".env.local"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    debug: bool = False
    environment: Environment = Environment.PRODUCTION
    log_level: str = "WARNING"
    cors_origins: Union[str, List[str]] = []


class TestSettings(Settings):
    """Test environment settings."""
    
    model_config = SettingsConfigDict(
        env_file=[".env", ".env.test", ".env.local"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    debug: bool = False
    environment: Environment = Environment.TEST
    database_url: str = "sqlite+aiosqlite:///:memory:"
    log_level: str = "WARNING"
    email_enabled: bool = False
    background_tasks_enabled: bool = False
    cache_enabled: bool = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance with proper loading order: .env -> .env.local -> .env.{environment} -> .env.local."""
    # Step 1: Load base .env and .env.local to determine environment
    try:
        from dotenv import dotenv_values
        
        # Load in order: .env, then .env.local
        base_values = dotenv_values(".env")
        local_values = dotenv_values(".env.local")
        
        # Merge with local taking priority
        combined_values = {**base_values, **local_values}
        env = combined_values.get("ENVIRONMENT", "development")
        
    except ImportError:
        # Fallback without python-dotenv
        env = os.getenv("ENVIRONMENT")
        if env is None:
            try:
                with open(".env", "r") as f:
                    for line in f:
                        if line.strip().startswith("ENVIRONMENT="):
                            env = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break
                    else:
                        env = "development"
            except FileNotFoundError:
                env = "development"
    
    env = (env or "development").lower()
    
    # Step 2: Return the appropriate settings class
    # Each class will load: .env -> .env.{environment} -> .env.local (final priority)
    if env == "production":
        return ProductionSettings()
    elif env == "staging":
        return StagingSettings()
    elif env == "sandbox":
        return SandboxSettings()
    elif env == "test":
        return TestSettings()
    else:
        return DevelopmentSettings()


# Global settings instance
settings = get_settings()


def reload_settings():
    """Reload settings from environment (clears cache)."""
    get_settings.cache_clear()
    global settings
    settings = get_settings()


def get_settings_dependency() -> Settings:
    """FastAPI dependency for injecting settings."""
    return settings


def is_development() -> bool:
    """Check if running in development mode."""
    return settings.is_development


def is_production() -> bool:
    """Check if running in production mode."""
    return settings.is_production


def is_test() -> bool:
    """Check if running in test mode."""
    return settings.is_test
