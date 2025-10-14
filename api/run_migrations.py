#!/usr/bin/env python3
"""
Simple migration runner script for DigitalOcean App Platform.

This script can be called directly in PRE_DEPLOY jobs to run Alembic migrations.
It ensures proper error handling and logging for deployment environments.
"""
import sys
import os
from pathlib import Path

# Ensure we're in the API directory
api_dir = Path(__file__).parent
os.chdir(api_dir)

try:
    print("🚀 Starting database migrations...")
    print(f"📍 Working directory: {os.getcwd()}")
    
    # Import alembic after changing directory
    from alembic.config import Config
    from alembic import command
    
    # Create alembic config
    alembic_cfg = Config("alembic.ini")
    
    # Run migrations
    print("🔄 Running alembic upgrade head...")
    command.upgrade(alembic_cfg, "head")
    
    print("✅ Migrations completed successfully!")
    sys.exit(0)
    
except ImportError as e:
    print(f"❌ Error: Required package not found: {e}")
    print("Make sure alembic and all dependencies are installed.")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
