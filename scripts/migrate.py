#!/usr/bin/env python3
"""
TruLedgr Migration Management Script

This script provides easy commands for managing database migrations with Alembic.
It handles the complexity of async database operations and provides user-friendly
commands for common migration tasks.
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_alembic_command(command: list[str]) -> bool:
    """Run an Alembic command and return success status."""
    try:
        # Ensure we're in the project directory
        os.chdir(project_root)
        
        # Run the alembic command with our virtual environment Python
        venv_python = project_root / ".venv" / "bin" / "python"
        if not venv_python.exists():
            venv_python = "python"  # Fallback to system Python
        
        full_command = [str(venv_python), "-m", "alembic"] + command
        
        logger.info(f"Running: {' '.join(full_command)}")
        result = subprocess.run(full_command, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"Failed to run Alembic command: {e}")
        return False


def create_migration(message: str, autogenerate: bool = True) -> bool:
    """Create a new migration."""
    logger.info(f"Creating migration: {message}")
    
    command = ["revision"]
    if autogenerate:
        command.append("--autogenerate")
    command.extend(["-m", message])
    
    return run_alembic_command(command)


def upgrade_database(target: str = "head") -> bool:
    """Upgrade database to target revision."""
    logger.info(f"Upgrading database to: {target}")
    return run_alembic_command(["upgrade", target])


def downgrade_database(target: str) -> bool:
    """Downgrade database to target revision."""
    logger.info(f"Downgrading database to: {target}")
    return run_alembic_command(["downgrade", target])


def show_current_revision() -> bool:
    """Show current database revision."""
    logger.info("Current database revision:")
    return run_alembic_command(["current"])


def show_migration_history() -> bool:
    """Show migration history."""
    logger.info("Migration history:")
    return run_alembic_command(["history", "--verbose"])


def stamp_database(revision: str = "head") -> bool:
    """Stamp database as being at a specific revision without running migrations."""
    logger.info(f"Stamping database as: {revision}")
    return run_alembic_command(["stamp", revision])


def check_migrations() -> bool:
    """Check for pending migrations."""
    logger.info("Checking for pending migrations...")
    
    # Get current revision
    current_result = subprocess.run(
        [sys.executable, "-m", "alembic", "current"],
        capture_output=True, text=True, cwd=project_root
    )
    
    # Get head revision
    head_result = subprocess.run(
        [sys.executable, "-m", "alembic", "heads"],
        capture_output=True, text=True, cwd=project_root
    )
    
    if current_result.returncode == 0 and head_result.returncode == 0:
        current = current_result.stdout.strip()
        head = head_result.stdout.strip()
        
        if current and head:
            current_rev = current.split()[0] if current.split() else ""
            head_rev = head.split()[0] if head.split() else ""
            
            if current_rev == head_rev:
                logger.info("✅ Database is up to date")
                return True
            else:
                logger.warning(f"⚠️ Database needs migration: {current_rev} -> {head_rev}")
                return False
        else:
            logger.warning("⚠️ Could not determine migration status")
            return False
    else:
        logger.error("❌ Failed to check migration status")
        return False


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="TruLedgr Migration Management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create migration
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("message", help="Migration description")
    create_parser.add_argument("--no-auto", action="store_true", help="Don't auto-generate migration")
    
    # Upgrade database
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database")
    upgrade_parser.add_argument("target", nargs="?", default="head", help="Target revision (default: head)")
    
    # Downgrade database
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database")
    downgrade_parser.add_argument("target", help="Target revision")
    
    # Current revision
    subparsers.add_parser("current", help="Show current database revision")
    
    # Migration history
    subparsers.add_parser("history", help="Show migration history")
    
    # Stamp database
    stamp_parser = subparsers.add_parser("stamp", help="Stamp database as specific revision")
    stamp_parser.add_argument("revision", nargs="?", default="head", help="Revision to stamp (default: head)")
    
    # Check migrations
    subparsers.add_parser("check", help="Check for pending migrations")
    
    # Setup (initial migration)
    subparsers.add_parser("setup", help="Set up initial migration (for new databases)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    success = False
    
    if args.command == "create":
        success = create_migration(args.message, autogenerate=not args.no_auto)
    elif args.command == "upgrade":
        success = upgrade_database(args.target)
    elif args.command == "downgrade":
        success = downgrade_database(args.target)
    elif args.command == "current":
        success = show_current_revision()
    elif args.command == "history":
        success = show_migration_history()
    elif args.command == "stamp":
        success = stamp_database(args.revision)
    elif args.command == "check":
        success = check_migrations()
    elif args.command == "setup":
        logger.info("Setting up initial migration system...")
        logger.info("This will mark the current database as the baseline.")
        
        confirm = input("Are you sure you want to stamp the database as 'head'? (yes/no): ")
        if confirm.lower() in ['yes', 'y']:
            success = stamp_database("head")
            if success:
                logger.info("✅ Database stamped as current. Future migrations will be applied incrementally.")
        else:
            logger.info("Setup cancelled.")
            success = False
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
