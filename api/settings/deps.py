"""
Settings dependency injection functions for FastAPI.

This module provides reusable dependency functions for:
- Application settings injection
- Environment-specific configuration
"""

import importlib.util
import os
import sys

# Import from the settings.py file directly
settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.py')
spec = importlib.util.spec_from_file_location("settings_module", settings_path)
settings_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(settings_module)

Settings = settings_module.Settings
get_settings_dependency = settings_module.get_settings_dependency


def get_settings() -> Settings:
    """
    Settings dependency for FastAPI dependency injection.
    
    Returns:
        Settings: Application settings instance
    """
    return get_settings_dependency()
