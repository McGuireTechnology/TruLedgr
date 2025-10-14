from .settings import Settings


class ProductionSettings(Settings):
    """Production-specific settings."""
    
    debug: bool = False
    database_echo: bool = False
    
    # Strict security for production
    access_token_expire_minutes: int = 15  # 15 minutes
    
    # Production hosts
    allowed_hosts: list[str] = ["api.truledgr.app"]
    
    model_config = {
        "env_file": ".env.production",
        "env_file_encoding": "utf-8"
    }


class DevelopmentSettings(Settings):
    """Development-specific settings."""
    
    debug: bool = True
    database_echo: bool = True
    
    # Relaxed security for development
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    
    # Development database (if different)
    database_url: str = "postgresql://truledgr:password@localhost:5432/truledgr_dev"
    
    model_config = {
        "env_file": ".env.development",
        "env_file_encoding": "utf-8"
    }