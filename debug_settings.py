#!/usr/bin/env python3
"""Debug script to check which settings are being loaded."""

import os
from api.settings import get_settings

# Simulate production environment
os.environ["ENVIRONMENT"] = "production"

settings = get_settings()

print(f"Environment: {settings.environment}")
print(f"Settings class: {type(settings).__name__}")
print(f"Database SSL verify: {settings.database_ssl_verify}")
print(f"Database URL: {settings.database_url}")
print(f"Database URL for env: {settings.database_url_for_env}")

# Test if it's production
print(f"Is production: {settings.is_production}")
