# Version Management

TruLedgr uses **semantic versioning** (SemVer) across all platforms with a centralized version management system.

## Semantic Versioning Format

All versions follow the format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Incompatible API changes
- **MINOR**: Add functionality in a backward-compatible manner
- **PATCH**: Backward-compatible bug fixes

Example: `0.1.0`, `1.2.3`, `2.0.0`

## Single Source of Truth

The canonical version is stored in the `VERSION` file at the repository root. All platform-specific version configurations are derived from this file.

```
TruLedgr/
├── VERSION                          # 0.1.0 (canonical source)
├── version.py                       # Version management script
├── pyproject.toml                   # Python: version = "0.1.0"
├── api/main.py                      # FastAPI: version="0.1.0"
├── mkdocs.yml                       # Docs: project_version = "0.1.0"
├── android/app/build.gradle.kts     # Android: versionName = "0.1.0", versionCode = 100
└── apple/TruLedgr.xcodeproj/        # iOS: MARKETING_VERSION = 0.1.0, BUILD = 100
```

## Version Code Calculation

For platforms that require numeric version codes (Android versionCode, iOS build number), we use this formula:

```
VERSION_CODE = MAJOR * 10000 + MINOR * 100 + PATCH
```

Examples:
- `0.1.0` → `100`
- `1.2.3` → `10203`
- `2.0.0` → `20000`

This ensures:
- Versions are strictly incrementing (required by app stores)
- Human-readable semantic versions are preserved
- No version conflicts across releases

## Using the Version Script

The `version.py` script manages versions across all platforms:

### View Current Version

```bash
python version.py
```

Output:
```
📌 Current version: 0.1.0
   Android versionCode: 100
   iOS build number: 100
```

### Bump Version

```bash
# Bump patch: 0.1.0 -> 0.1.1
python version.py bump patch

# Bump minor: 0.1.0 -> 0.2.0
python version.py bump minor

# Bump major: 0.1.0 -> 1.0.0
python version.py bump major
```

This will:

1. Update the `VERSION` file
2. Sync to `pyproject.toml`
3. Sync to FastAPI `api/main.py`
4. Sync to Android `build.gradle.kts` (versionName + versionCode)
5. Sync to iOS `project.pbxproj` (MARKETING_VERSION + CURRENT_PROJECT_VERSION)
6. Sync to MkDocs `mkdocs.yml` (displayed in footer)

### Set Specific Version

```bash
python version.py set 1.2.3
```

### Sync Without Changing Version

If you manually edit the `VERSION` file, sync it to all platforms:

```bash
python version.py sync
```

## Platform-Specific Details

### Python/FastAPI Backend (`pyproject.toml`)

```toml
[tool.poetry]
version = "0.1.0"
```

Access in code:
```python
from version import __version__
print(__version__)  # "0.1.0"
```

### Android (`android/app/build.gradle.kts`)

```kotlin
android {
    defaultConfig {
        versionCode = 100        // Numeric, auto-incrementing
        versionName = "0.1.0"    // Semantic version string
    }
}
```

- **versionCode**: Required by Google Play, must increment with each release
- **versionName**: User-visible version in app info

### iOS/macOS (`apple/TruLedgr.xcodeproj/project.pbxproj`)

```
MARKETING_VERSION = 0.1.0;        // User-visible (CFBundleShortVersionString)
CURRENT_PROJECT_VERSION = 100;    // Build number (CFBundleVersion)
```

- **MARKETING_VERSION**: Displayed in App Store and Settings
- **CURRENT_PROJECT_VERSION**: Build number, must increment for App Store submissions

## Git Workflow

When releasing a new version:

1. **Update version:**
   ```bash
   python version.py bump minor  # or patch, major
   ```

2. **Commit version change:**
   ```bash
   git add VERSION pyproject.toml android/app/build.gradle.kts apple/TruLedgr.xcodeproj/project.pbxproj
   git commit -m "chore: bump version to 0.2.0"
   ```

3. **Tag the release:**
   ```bash
   git tag -a v0.2.0 -m "Release version 0.2.0"
   git push origin staging --tags
   ```

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.1.0   | 2025-10-09 | Initial release with Bonjour apps and API health checks |

## CI/CD Integration

The version script can be integrated into CI/CD pipelines:

```bash
# In GitHub Actions, GitLab CI, etc.
- name: Bump patch version
  run: python version.py bump patch

- name: Build with new version
  run: |
    VERSION=$(cat VERSION)
    echo "Building version $VERSION"
```

## Best Practices

1. **Always use the script**: Don't manually edit version numbers in platform files
2. **Commit VERSION file**: The `VERSION` file should be tracked in git
3. **Atomic commits**: Include all platform version files in the same commit
4. **Tag releases**: Use git tags that match the version (e.g., `v0.1.0`)
5. **Update changelog**: Document changes for each version
6. **Follow SemVer**: Be consistent about what constitutes major/minor/patch changes

## Troubleshooting

### Version out of sync

If platform versions get out of sync:

```bash
python version.py sync
```

### Script not found

Make sure you're in the repository root:

```bash
cd /path/to/TruLedgr
python version.py
```

### Permission denied

Make the script executable:

```bash
chmod +x version.py
./version.py
```

### Invalid version format

Version must be `MAJOR.MINOR.PATCH` with integers only:

```bash
# ✅ Valid
python version.py set 1.2.3

# ❌ Invalid
python version.py set 1.2.3-beta
python version.py set v1.2.3
```

For pre-release versions (alpha, beta, rc), use git tags instead of the VERSION file.
