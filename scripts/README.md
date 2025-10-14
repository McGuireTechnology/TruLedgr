# TruLedgr Scripts

Utility scripts for managing the TruLedgr project.

## version.py

Centralized version management script that maintains version numbers across all platforms.

### Features

- **Single Source of Truth**: All version numbers come from the `VERSION` file at repository root
- **Multi-Platform Support**: Automatically syncs versions to:
  - Python (`pyproject.toml`)
  - FastAPI (`api/main.py`)
  - Android (`android/app/build.gradle.kts`)
  - iOS (`apple/TruLedgr.xcodeproj/project.pbxproj`)
  - Documentation (`mkdocs.yml`)
- **Semantic Versioning**: Follows `MAJOR.MINOR.PATCH` format
- **Version Codes**: Automatically calculates platform-specific version codes
  - Formula: `MAJOR * 10000 + MINOR * 100 + PATCH`
  - Example: `0.1.0` → `100`, `1.2.3` → `10203`

### Usage

The script is executable and can be run directly or via Python:

```bash
# View current version
./scripts/version.py
# or: python scripts/version.py

# Bump patch version (0.1.0 -> 0.1.1)
./scripts/version.py bump patch

# Bump minor version (0.1.0 -> 0.2.0)
./scripts/version.py bump minor

# Bump major version (0.1.0 -> 1.0.0)
./scripts/version.py bump major

# Set specific version
./scripts/version.py set 1.2.3

# Sync current version to all platforms (useful after manual VERSION file edit)
./scripts/version.py sync
```

### Version File Locations

The script updates the following files:

| Platform | File | Format |
|----------|------|--------|
| **Source** | `VERSION` | `0.1.0` |
| **Python** | `pyproject.toml` | `version = "0.1.0"` |
| **FastAPI** | `api/main.py` | `version="0.1.0"` |
| **Android** | `android/app/build.gradle.kts` | `versionCode = 100`<br>`versionName = "0.1.0"` |
| **iOS** | `apple/TruLedgr.xcodeproj/project.pbxproj` | `MARKETING_VERSION = 0.1.0;`<br>`CURRENT_PROJECT_VERSION = 100;` |
| **Docs** | `mkdocs.yml` | `default: 0.1.0`<br>`project_version: "0.1.0"` |

### Workflow

When releasing a new version:

1. Bump the version: `./scripts/version.py bump patch`
2. Review the changes: `git diff`
3. Commit the version bump: `git commit -am "chore: bump version to X.Y.Z"`
4. Tag the release: `git tag vX.Y.Z`
5. Push: `git push origin main --tags`

### Examples

```bash
# Development cycle: patch releases
$ ./scripts/version.py bump patch
🔼 Bumping patch: 0.1.0 -> 0.1.1
📦 Syncing version 0.1.1 to all platforms...
✅ Updated pyproject.toml: 0.1.1
✅ Updated FastAPI: 0.1.1
✅ Updated Android: 0.1.1 (versionCode: 101)
✅ Updated iOS: 0.1.1 (build: 101)
✅ Updated mkdocs.yml: 0.1.1
✨ Version sync complete!

# New feature: minor release
$ ./scripts/version.py bump minor
🔼 Bumping minor: 0.1.1 -> 0.2.0
📦 Syncing version 0.2.0 to all platforms...
...

# Breaking change: major release
$ ./scripts/version.py bump major
🔼 Bumping major: 0.2.0 -> 1.0.0
📦 Syncing version 1.0.0 to all platforms...
...

# Set specific version (useful for hotfixes)
$ ./scripts/version.py set 0.1.2
🎯 Setting version: 0.1.1 -> 0.1.2
...
```

### Error Handling

- Missing files are skipped with warnings (useful when platforms don't exist yet)
- Invalid version formats are rejected
- All changes are atomic (either all files update or none do)

### Notes

- Always run from repository root: `./scripts/version.py` or `python scripts/version.py`
- The script is standalone and does not require Poetry or dependencies
- Changes are made in-place, so review with `git diff` and commit after verifying
- Script automatically skips platforms that don't exist yet with warnings
