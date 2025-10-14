#!/usr/bin/env python3
"""
TruLedgr Version Management

This module provides a single source of truth for version numbers
across all subprojects. The version is read from the VERSION file
at the repository root.

Usage:
    python scripts/version.py                    # Show current version
    python scripts/version.py bump patch         # Bump patch: 0.1.0 -> 0.1.1
    python scripts/version.py bump minor         # Bump minor: 0.1.0 -> 0.2.0
    python scripts/version.py bump major         # Bump major: 0.1.0 -> 1.0.0
    python scripts/version.py set 1.2.3          # Set specific version
    python scripts/version.py sync               # Sync version to all platforms
"""

import re
import sys
from pathlib import Path
from typing import Tuple

# Root directory of the project (parent of scripts directory)
ROOT_DIR = Path(__file__).parent.parent
VERSION_FILE = ROOT_DIR / "VERSION"

# Platform-specific version files
PYPROJECT_TOML = ROOT_DIR / "pyproject.toml"
ANDROID_BUILD_GRADLE = ROOT_DIR / "android" / "app" / "build.gradle.kts"
IOS_PROJECT_FILE = ROOT_DIR / "apple" / "TruLedgr.xcodeproj" / "project.pbxproj"
MKDOCS_YML = ROOT_DIR / "mkdocs.yml"
FASTAPI_MAIN = ROOT_DIR / "api" / "main.py"

# Read version from VERSION file
__version__ = VERSION_FILE.read_text().strip()

# Version components
MAJOR, MINOR, PATCH = __version__.split(".")

# Android version code (incremental integer for Google Play)
# Formula: MAJOR * 10000 + MINOR * 100 + PATCH
VERSION_CODE = int(MAJOR) * 10000 + int(MINOR) * 100 + int(PATCH)

# iOS build number (CURRENT_PROJECT_VERSION)
BUILD_NUMBER = VERSION_CODE


def read_version() -> str:
    """Read version from VERSION file."""
    if not VERSION_FILE.exists():
        raise FileNotFoundError(f"VERSION file not found at {VERSION_FILE}")
    return VERSION_FILE.read_text().strip()


def write_version(version: str) -> None:
    """Write version to VERSION file."""
    VERSION_FILE.write_text(version + "\n")


def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse semantic version string into (major, minor, patch)."""
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version)
    if not match:
        raise ValueError(f"Invalid semantic version: {version}")
    return tuple(map(int, match.groups()))


def format_version(major: int, minor: int, patch: int) -> str:
    """Format version tuple as semantic version string."""
    return f"{major}.{minor}.{patch}"


def version_to_code(major: int, minor: int, patch: int) -> int:
    """
    Convert semantic version to version code.
    Formula: MAJOR * 10000 + MINOR * 100 + PATCH
    Examples: 0.1.0 = 100, 1.2.3 = 10203, 2.0.0 = 20000
    """
    return major * 10000 + minor * 100 + patch


def bump_version(current: str, part: str) -> str:
    """Bump version by major, minor, or patch."""
    major, minor, patch = parse_version(current)
    
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump part: {part}. Use major, minor, or patch")
    
    return format_version(major, minor, patch)


def sync_pyproject_toml(version: str) -> None:
    """Update version in pyproject.toml."""
    if not PYPROJECT_TOML.exists():
        print(f"⚠️  Skipping pyproject.toml (not found)")
        return
    
    content = PYPROJECT_TOML.read_text()
    new_content = re.sub(
        r'^version = "[^"]+"',
        f'version = "{version}"',
        content,
        flags=re.MULTILINE
    )
    
    if new_content != content:
        PYPROJECT_TOML.write_text(new_content)
        print(f"✅ Updated pyproject.toml: {version}")
    else:
        print(f"⚠️  pyproject.toml already at {version}")


def sync_android_gradle(version: str) -> None:
    """Update version in Android build.gradle.kts."""
    if not ANDROID_BUILD_GRADLE.exists():
        print(f"⚠️  Skipping Android (build.gradle.kts not found)")
        return
    
    major, minor, patch = parse_version(version)
    version_code = version_to_code(major, minor, patch)
    
    content = ANDROID_BUILD_GRADLE.read_text()
    
    # Update versionCode
    new_content = re.sub(
        r'versionCode = \d+',
        f'versionCode = {version_code}',
        content
    )
    
    # Update versionName
    new_content = re.sub(
        r'versionName = "[^"]+"',
        f'versionName = "{version}"',
        new_content
    )
    
    if new_content != content:
        ANDROID_BUILD_GRADLE.write_text(new_content)
        print(f"✅ Updated Android: {version} (versionCode: {version_code})")
    else:
        print(f"⚠️  Android already at {version}")


def sync_ios_project(version: str) -> None:
    """Update version in iOS project.pbxproj."""
    if not IOS_PROJECT_FILE.exists():
        print(f"⚠️  Skipping iOS (project.pbxproj not found)")
        return
    
    major, minor, patch = parse_version(version)
    # iOS build number: simple incrementing integer (use version_code for consistency)
    build_number = version_to_code(major, minor, patch)
    
    content = IOS_PROJECT_FILE.read_text()
    
    # Update MARKETING_VERSION (user-visible version: 0.1.0)
    new_content = re.sub(
        r'MARKETING_VERSION = [^;]+;',
        f'MARKETING_VERSION = {version};',
        content
    )
    
    # Update CURRENT_PROJECT_VERSION (build number: integer)
    new_content = re.sub(
        r'CURRENT_PROJECT_VERSION = \d+;',
        f'CURRENT_PROJECT_VERSION = {build_number};',
        new_content
    )
    
    if new_content != content:
        IOS_PROJECT_FILE.write_text(new_content)
        print(f"✅ Updated iOS: {version} (build: {build_number})")
    else:
        print(f"⚠️  iOS already at {version}")


def sync_mkdocs_yml(version: str) -> None:
    """Update version in mkdocs.yml."""
    if not MKDOCS_YML.exists():
        print("⚠️  Skipping mkdocs.yml (not found)")
        return
    
    content = MKDOCS_YML.read_text()
    
    # Update version.default (looks like "default: 0.1.0")
    new_content = re.sub(
        r'(default:\s+)[\d.]+',
        f'\\g<1>{version}',
        content
    )
    
    # Update project_version (looks like 'project_version: "0.1.0"')
    new_content = re.sub(
        r'(project_version:\s*")[^"]+(")',
        f'\\g<1>{version}\\g<2>',
        new_content
    )
    
    if new_content != content:
        MKDOCS_YML.write_text(new_content)
        print(f"✅ Updated mkdocs.yml: {version}")
    else:
        print(f"⚠️  mkdocs.yml already at {version}")


def sync_fastapi_main(version: str) -> None:
    """Update version in FastAPI main.py."""
    if not FASTAPI_MAIN.exists():
        print("⚠️  Skipping FastAPI main.py (not found)")
        return
    
    content = FASTAPI_MAIN.read_text()
    
    # Update FastAPI app version
    new_content = re.sub(
        r'version="[^"]+"',
        f'version="{version}"',
        content
    )
    
    if new_content != content:
        FASTAPI_MAIN.write_text(new_content)
        print(f"✅ Updated FastAPI: {version}")
    else:
        print(f"⚠️  FastAPI already at {version}")


def sync_all_platforms(version: str) -> None:
    """Sync version to all platform-specific files."""
    print(f"📦 Syncing version {version} to all platforms...\n")
    sync_pyproject_toml(version)
    sync_fastapi_main(version)
    sync_android_gradle(version)
    sync_ios_project(version)
    sync_mkdocs_yml(version)
    print(f"\n✨ Version sync complete!")


def main():
    """Main entry point."""
    if len(sys.argv) == 1:
        # Just show current version
        version = read_version()
        major, minor, patch = parse_version(version)
        version_code = version_to_code(major, minor, patch)
        print(f"📌 Current version: {version}")
        print(f"   Android versionCode: {version_code}")
        print(f"   iOS build number: {version_code}")
        return
    
    command = sys.argv[1]
    
    if command == "bump":
        if len(sys.argv) != 3:
            print("Usage: python version.py bump [major|minor|patch]")
            sys.exit(1)
        
        part = sys.argv[2]
        current = read_version()
        new_version = bump_version(current, part)
        
        print(f"🔼 Bumping {part}: {current} -> {new_version}")
        write_version(new_version)
        sync_all_platforms(new_version)
    
    elif command == "set":
        if len(sys.argv) != 3:
            print("Usage: python version.py set X.Y.Z")
            sys.exit(1)
        
        new_version = sys.argv[2]
        # Validate version format
        parse_version(new_version)
        
        current = read_version()
        print(f"🎯 Setting version: {current} -> {new_version}")
        write_version(new_version)
        sync_all_platforms(new_version)
    
    elif command == "sync":
        version = read_version()
        sync_all_platforms(version)
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
