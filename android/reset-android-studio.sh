#!/bin/bash
# Reset Android Studio project files
# Run this if Android Studio won't detect the project properly

echo "�� Cleaning Android Studio project files..."

cd "$(dirname "$0")"

# Remove IDE-specific directories
rm -rf .idea
rm -rf .gradle
rm -rf build
rm -rf app/build

echo "✅ Cleaned successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Close Android Studio if it's open"
echo "2. Reopen the android/ folder in Android Studio"
echo "3. Wait for Gradle sync and indexing to complete"
echo "4. The 'app' run configuration should appear automatically"
